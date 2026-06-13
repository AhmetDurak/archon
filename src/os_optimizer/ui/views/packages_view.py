from PySide6.QtCore import Qt, QThread, Signal, QProcess
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QPushButton, QDialog, QTextEdit, QDialogButtonBox
)

from os_optimizer.core.interfaces import IPackageManager


class FetchWorker(QThread):
    done = Signal(list)

    def __init__(self, pkg_manager: IPackageManager):
        super().__init__()
        self._pm = pkg_manager

    def run(self):
        self.done.emit(self._pm.get_outdated_packages())


class UpdateDialog(QDialog):
    def __init__(self, command: list[str], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Applying Updates")
        self.resize(640, 400)

        layout = QVBoxLayout(self)
        self._output = QTextEdit()
        self._output.setReadOnly(True)
        layout.addWidget(self._output)

        self._close_btn = QPushButton("Close")
        self._close_btn.setObjectName("primary-btn")
        self._close_btn.setEnabled(False)
        self._close_btn.clicked.connect(self.accept)
        layout.addWidget(self._close_btn)

        self._process = QProcess(self)
        self._process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self._process.readyReadStandardOutput.connect(self._read_output)
        self._process.finished.connect(self._on_finished)
        self._process.start(command[0], command[1:])

    def _read_output(self):
        data = self._process.readAllStandardOutput().data().decode(errors="replace")
        self._output.append(data.rstrip())

    def _on_finished(self, code: int, _status):
        if code == 0:
            self._output.append("\n✓ Update completed successfully.")
        else:
            self._output.append(f"\n✗ Process exited with code {code}.")
        self._close_btn.setEnabled(True)

    def closeEvent(self, event):
        if self._process.state() != QProcess.ProcessState.NotRunning:
            self._process.kill()
            self._process.waitForFinished(2000)
        super().closeEvent(event)


class PackagesView(QWidget):
    summary_ready = Signal(int)

    def __init__(self, pkg_manager: IPackageManager, parent=None):
        super().__init__(parent)
        self._pm = pkg_manager
        self._worker = None
        self._packages = []
        self._setup_ui()
        self._fetch()

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setSpacing(16)

        title = QLabel("Packages")
        title.setObjectName("section-title")
        sub = QLabel("Available system updates via pacman")
        sub.setObjectName("section-sub")
        root.addWidget(title)
        root.addWidget(sub)

        toolbar = QHBoxLayout()
        self._status_label = QLabel("Checking for updates…")
        self._status_label.setObjectName("metric-label")

        self._refresh_btn = QPushButton("Refresh")
        self._refresh_btn.setObjectName("primary-btn")
        self._refresh_btn.clicked.connect(self._fetch)

        self._update_btn = QPushButton("Apply All Updates")
        self._update_btn.setObjectName("danger-btn")
        self._update_btn.setEnabled(False)
        self._update_btn.clicked.connect(self._run_update)

        toolbar.addWidget(self._status_label)
        toolbar.addStretch()
        toolbar.addWidget(self._refresh_btn)
        toolbar.addWidget(self._update_btn)
        root.addLayout(toolbar)

        self._table = QTableWidget(0, 3)
        self._table.setHorizontalHeaderLabels(["Package", "Current", "Available"])
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
        self._refresh_btn.setEnabled(False)
        self._update_btn.setEnabled(False)
        self._status_label.setText("Checking for updates…")
        self._table.setRowCount(0)

        self._worker = FetchWorker(self._pm)
        self._worker.done.connect(self._on_fetch_done)
        self._worker.start()

    def _on_fetch_done(self, packages):
        self._packages = packages
        self._refresh_btn.setEnabled(True)
        self._table.setRowCount(len(packages))

        for i, pkg in enumerate(packages):
            self._table.setItem(i, 0, QTableWidgetItem(pkg.name))
            self._table.setItem(i, 1, QTableWidgetItem(pkg.current))
            item = QTableWidgetItem(pkg.available)
            item.setForeground(Qt.GlobalColor.green)
            self._table.setItem(i, 2, item)

        count = len(packages)
        if count == 0:
            self._status_label.setText("System is up to date.")
        else:
            self._status_label.setText(f"{count} update{'s' if count != 1 else ''} available")
            self._update_btn.setEnabled(True)

        self.summary_ready.emit(count)

    def _run_update(self):
        dlg = UpdateDialog(self._pm.get_update_command(), self)
        dlg.exec()
        self._fetch()
