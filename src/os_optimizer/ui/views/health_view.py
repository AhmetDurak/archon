from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QPushButton
)

from os_optimizer.core.interfaces import IHealthChecker
from os_optimizer.sudo_session import SudoSession
from os_optimizer.ui import strings


class HealthWorker(QThread):
    done = Signal(list)

    def __init__(self, checker: IHealthChecker):
        super().__init__()
        self._checker = checker

    def run(self):
        self.done.emit(self._checker.get_issues())


_SEVERITY_COLORS = {
    "error":   "#f38ba8",
    "warning": "#f9e2af",
    "info":    "#89b4fa",
}


class HealthView(QWidget):
    summary_ready = Signal(int)

    def __init__(self, checker: IHealthChecker, sudo_session: SudoSession, parent=None):
        super().__init__(parent)
        self._checker = checker
        self._sudo = sudo_session
        self._worker = None
        self._setup_ui()
        self._fetch()

    def _setup_ui(self):
        s = strings.get()
        root = QVBoxLayout(self)
        root.setSpacing(16)

        title = QLabel(s.health_title)
        title.setObjectName("section-title")
        sub = QLabel(s.health_subtitle)
        sub.setObjectName("section-sub")
        root.addWidget(title)
        root.addWidget(sub)

        toolbar = QHBoxLayout()
        self._status_label = QLabel(s.health_scanning)
        self._status_label.setObjectName("metric-label")

        self._refresh_btn = QPushButton(s.health_rescan_btn)
        self._refresh_btn.setObjectName("primary-btn")
        self._refresh_btn.clicked.connect(self._fetch)

        toolbar.addWidget(self._status_label)
        toolbar.addStretch()
        toolbar.addWidget(self._refresh_btn)
        root.addLayout(toolbar)

        self._table = QTableWidget(0, 5)
        self._table.setHorizontalHeaderLabels([
            s.health_col_severity,
            s.health_col_path,
            s.health_col_issue,
            s.health_col_fix,
            s.health_col_action,
        ])
        header = self._table.horizontalHeader()
        header.setSectionResizeMode(0, header.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, header.ResizeMode.Interactive)
        header.setSectionResizeMode(2, header.ResizeMode.Stretch)
        header.setSectionResizeMode(3, header.ResizeMode.Interactive)
        header.setSectionResizeMode(4, header.ResizeMode.ResizeToContents)
        header.setStretchLastSection(False)
        self._table.setColumnWidth(1, 180)
        self._table.setColumnWidth(3, 240)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._table.setSortingEnabled(True)
        self._table.setWordWrap(False)
        self._table.verticalHeader().setDefaultSectionSize(36)
        root.addWidget(self._table)

    def _fetch(self):
        if self._worker and self._worker.isRunning():
            return
        s = strings.get()
        self._refresh_btn.setEnabled(False)
        self._status_label.setText(s.health_scanning)
        self._table.setRowCount(0)

        self._worker = HealthWorker(self._checker)
        self._worker.done.connect(self._on_fetch_done)
        self._worker.start()

    def _on_fetch_done(self, issues):
        s = strings.get()
        self._refresh_btn.setEnabled(True)
        self._table.setSortingEnabled(False)
        self._table.setRowCount(len(issues))

        for i, issue in enumerate(issues):
            color = _SEVERITY_COLORS.get(issue.severity, "#cdd6f4")

            sev_item = QTableWidgetItem(issue.severity.upper())
            sev_item.setForeground(QColor(color))
            self._table.setItem(i, 0, sev_item)
            self._table.setItem(i, 1, QTableWidgetItem(issue.path))
            self._table.setItem(i, 2, QTableWidgetItem(issue.message))

            fix_item = QTableWidgetItem(issue.fix or "—")
            fix_item.setForeground(QColor("#6c7086"))
            self._table.setItem(i, 3, fix_item)

            if issue.fix:
                btn = QPushButton(s.health_fix_btn)
                btn.setObjectName("table-btn")
                btn.clicked.connect(lambda _, cmd=issue.fix: self._open_fix_dialog(cmd))
                self._table.setCellWidget(i, 4, btn)

        self._table.setSortingEnabled(True)

        errors = sum(1 for iss in issues if iss.severity == "error")
        warnings = sum(1 for iss in issues if iss.severity == "warning")

        if not issues:
            self._status_label.setText(s.health_no_issues)
        else:
            self._status_label.setText(s.health_n_detected.format(
                errors=errors, es="s" if errors != 1 else "",
                warnings=warnings, ws="s" if warnings != 1 else "",
            ))

        self.summary_ready.emit(len(issues))

    def refresh(self):
        self._fetch()

    def _open_fix_dialog(self, command: str):
        from os_optimizer.ui.fix_dialog import FixDialog
        btn = self.sender()
        row = next(
            (r for r in range(self._table.rowCount()) if self._table.cellWidget(r, 4) is btn),
            -1,
        )
        dlg = FixDialog(command, self._sudo, self)
        if dlg.exec():
            if row != -1:
                self._table.removeRow(row)
            self.summary_ready.emit(self._table.rowCount())
            self._fetch()
