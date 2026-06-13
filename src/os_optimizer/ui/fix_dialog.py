from PySide6.QtCore import QProcess
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QFrame
)

from os_optimizer.sudo_session import SudoSession
from os_optimizer.ui import strings


class FixDialog(QDialog):
    """
    Shows the fix command, asks for confirmation, then runs it with live output.
    Commands containing 'sudo' get sudo -S injected if a password is available.
    Always runs via `bash -c` so shell expansions like $(…) work.

    Returns Accepted (dlg.exec() == True) only when the fix exited with code 0.
    Returns Rejected on cancel or non-zero exit — caller skips re-scanning.
    """

    def __init__(self, fix_command: str, sudo_session: SudoSession, parent=None, title: str | None = None):
        super().__init__(parent)
        s = strings.get()
        self.setWindowTitle(title if title is not None else s.fix_title)
        self.setMinimumWidth(560)
        self._sudo = sudo_session
        self._raw_command = fix_command
        self._process: QProcess | None = None
        self._succeeded = False
        self._setup_ui(fix_command)

    def _setup_ui(self, command: str):
        s = strings.get()
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        desc = QLabel(s.fix_description)
        desc.setObjectName("metric-label")
        layout.addWidget(desc)

        cmd_box = QTextEdit()
        cmd_box.setReadOnly(True)
        cmd_box.setPlainText(command)
        cmd_box.setFixedHeight(60)
        layout.addWidget(cmd_box)

        if "sudo" in command:
            warn = QLabel(s.fix_warn_sudo)
            warn.setObjectName("badge-warn")
            layout.addWidget(warn)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #313244;")
        layout.addWidget(sep)

        self._output = QTextEdit()
        self._output.setReadOnly(True)
        self._output.setVisible(False)
        self._output.setMinimumHeight(180)
        layout.addWidget(self._output)

        btns = QHBoxLayout()

        self._cancel_btn = QPushButton(s.fix_close_btn)
        self._cancel_btn.setObjectName("danger-btn")
        self._cancel_btn.clicked.connect(self._on_close_clicked)

        self._apply_btn = QPushButton(s.fix_apply_btn)
        self._apply_btn.setObjectName("primary-btn")
        self._apply_btn.clicked.connect(self._run)

        btns.addWidget(self._cancel_btn)
        btns.addStretch()
        btns.addWidget(self._apply_btn)
        layout.addLayout(btns)

    def _run(self):
        self._apply_btn.setEnabled(False)
        self._output.setVisible(True)
        self.adjustSize()

        cmd = self._raw_command
        if "sudo" in cmd and self._sudo.password is not None:
            cmd = cmd.replace("sudo ", "sudo -S ", 1)

        self._process = QProcess(self)
        self._process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self._process.readyReadStandardOutput.connect(self._read_output)
        self._process.finished.connect(self._on_finished)
        self._process.start("bash", ["-c", cmd])

        if "sudo -S" in cmd and self._sudo.password is not None:
            self._process.write(f"{self._sudo.password}\n".encode())

    def _read_output(self):
        data = self._process.readAllStandardOutput().data().decode(errors="replace")
        self._output.append(data.rstrip())

    def _on_finished(self, code: int, _status):
        s = strings.get()
        self._succeeded = (code == 0)

        if code == 0:
            self._output.append(s.fix_success)
            # Switch Close button to primary style — clicking it will accept the dialog
            self._cancel_btn.setObjectName("primary-btn")
            self._cancel_btn.style().unpolish(self._cancel_btn)
            self._cancel_btn.style().polish(self._cancel_btn)
        else:
            self._output.append(s.fix_failed.format(code=code))

        self._cancel_btn.setText(s.fix_close_btn)
        self._cancel_btn.setEnabled(True)

    def _on_close_clicked(self):
        if self._process and self._process.state() != QProcess.ProcessState.NotRunning:
            self._process.kill()
            self._process.waitForFinished(2000)
        # Accept only if fix succeeded — health view re-scans on True
        if self._succeeded:
            self.accept()
        else:
            self.reject()

    def closeEvent(self, event):
        if self._process and self._process.state() != QProcess.ProcessState.NotRunning:
            self._process.kill()
            self._process.waitForFinished(2000)
        super().closeEvent(event)
