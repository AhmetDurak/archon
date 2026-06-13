from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QPushButton
)

from os_optimizer.core.interfaces import IPackageManager
from os_optimizer.sudo_session import SudoSession
from os_optimizer.ui import strings
from os_optimizer.ui.update_dialog import UpdateDialog


class FetchWorker(QThread):
    done = Signal(list)

    def __init__(self, pkg_manager: IPackageManager):
        super().__init__()
        self._pm = pkg_manager

    def run(self):
        self.done.emit(self._pm.get_outdated_packages())


class PackagesView(QWidget):
    summary_ready = Signal(int)

    def __init__(self, pkg_manager: IPackageManager, sudo_session: SudoSession, parent=None):
        super().__init__(parent)
        self._pm = pkg_manager
        self._sudo = sudo_session
        self._worker = None
        self._packages = []
        self._setup_ui()
        self._fetch()

    def _setup_ui(self):
        s = strings.get()
        root = QVBoxLayout(self)
        root.setSpacing(16)

        title = QLabel(s.pkg_title)
        title.setObjectName("section-title")
        sub = QLabel(s.pkg_subtitle)
        sub.setObjectName("section-sub")
        root.addWidget(title)
        root.addWidget(sub)

        toolbar = QHBoxLayout()
        self._status_label = QLabel(s.pkg_checking)
        self._status_label.setObjectName("metric-label")

        self._refresh_btn = QPushButton(s.pkg_refresh_btn)
        self._refresh_btn.setObjectName("primary-btn")
        self._refresh_btn.clicked.connect(self._fetch)

        self._update_btn = QPushButton(s.pkg_update_btn)
        self._update_btn.setObjectName("danger-btn")
        self._update_btn.setEnabled(False)
        self._update_btn.clicked.connect(self._run_update)

        toolbar.addWidget(self._status_label)
        toolbar.addStretch()
        toolbar.addWidget(self._refresh_btn)
        toolbar.addWidget(self._update_btn)
        root.addLayout(toolbar)

        self._table = QTableWidget(0, 3)
        self._table.setHorizontalHeaderLabels(
            [s.pkg_col_name, s.pkg_col_current, s.pkg_col_available]
        )
        header = self._table.horizontalHeader()
        header.setSectionResizeMode(0, header.ResizeMode.Stretch)
        header.setSectionResizeMode(1, header.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, header.ResizeMode.ResizeToContents)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setAlternatingRowColors(True)
        root.addWidget(self._table)

    def _fetch(self):
        if self._worker and self._worker.isRunning():
            return
        s = strings.get()
        self._refresh_btn.setEnabled(False)
        self._update_btn.setEnabled(False)
        self._status_label.setText(s.pkg_checking)
        self._table.setRowCount(0)

        self._worker = FetchWorker(self._pm)
        self._worker.done.connect(self._on_fetch_done)
        self._worker.start()

    def _on_fetch_done(self, packages):
        s = strings.get()
        self._packages = packages
        self._refresh_btn.setEnabled(True)
        self._table.setRowCount(len(packages))

        for i, pkg in enumerate(packages):
            self._table.setItem(i, 0, QTableWidgetItem(pkg.name))
            self._table.setItem(i, 1, QTableWidgetItem(pkg.current))
            item = QTableWidgetItem(pkg.available)
            item.setForeground(QColor("#a6e3a1"))
            self._table.setItem(i, 2, item)

        count = len(packages)
        if count == 0:
            self._status_label.setText(s.pkg_up_to_date)
        else:
            plural = "s" if count != 1 else ""
            self._status_label.setText(s.pkg_n_available.format(n=count, s=plural))
            self._update_btn.setEnabled(True)

        self.summary_ready.emit(count)

    def _run_update(self):
        dlg = UpdateDialog(self._pm.get_update_command(), self._sudo, self)
        dlg.exec()
        self._fetch()
