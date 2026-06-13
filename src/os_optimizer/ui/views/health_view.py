from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QPushButton
)

from os_optimizer.core.interfaces import IHealthChecker


class HealthWorker(QThread):
    done = Signal(list)

    def __init__(self, checker: IHealthChecker):
        super().__init__()
        self._checker = checker

    def run(self):
        self.done.emit(self._checker.get_issues())


_SEVERITY_COLORS = {
    "error": "#f38ba8",
    "warning": "#f9e2af",
    "info": "#89b4fa",
}


class HealthView(QWidget):
    summary_ready = Signal(int)

    def __init__(self, checker: IHealthChecker, parent=None):
        super().__init__(parent)
        self._checker = checker
        self._worker = None
        self._issues = []
        self._setup_ui()
        self._fetch()

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setSpacing(16)

        title = QLabel("System Health")
        title.setObjectName("section-title")
        sub = QLabel("Permission issues and configuration problems")
        sub.setObjectName("section-sub")
        root.addWidget(title)
        root.addWidget(sub)

        toolbar = QHBoxLayout()
        self._status_label = QLabel("Scanning…")
        self._status_label.setObjectName("metric-label")

        self._refresh_btn = QPushButton("Rescan")
        self._refresh_btn.setObjectName("primary-btn")
        self._refresh_btn.clicked.connect(self._fetch)

        toolbar.addWidget(self._status_label)
        toolbar.addStretch()
        toolbar.addWidget(self._refresh_btn)
        root.addLayout(toolbar)

        self._table = QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels(["Severity", "Path", "Issue", "Fix"])
        header = self._table.horizontalHeader()
        header.setSectionResizeMode(0, header.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, header.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, header.ResizeMode.Stretch)
        header.setSectionResizeMode(3, header.ResizeMode.ResizeToContents)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._table.setWordWrap(False)
        root.addWidget(self._table)

    def _fetch(self):
        if self._worker and self._worker.isRunning():
            return
        self._refresh_btn.setEnabled(False)
        self._status_label.setText("Scanning…")
        self._table.setRowCount(0)

        self._worker = HealthWorker(self._checker)
        self._worker.done.connect(self._on_fetch_done)
        self._worker.start()

    def _on_fetch_done(self, issues):
        self._issues = issues
        self._refresh_btn.setEnabled(True)
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

        errors = sum(1 for iss in issues if iss.severity == "error")
        warnings = sum(1 for iss in issues if iss.severity == "warning")

        if not issues:
            self._status_label.setText("No issues found — system looks healthy.")
        else:
            parts = []
            if errors:
                parts.append(f"{errors} error{'s' if errors != 1 else ''}")
            if warnings:
                parts.append(f"{warnings} warning{'s' if warnings != 1 else ''}")
            self._status_label.setText(", ".join(parts) + " detected")

        self.summary_ready.emit(len(issues))
