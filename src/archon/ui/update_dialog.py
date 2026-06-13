from PySide6.QtCore import QProcess
from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QTextEdit

from archon.sudo_session import SudoSession
from archon.ui import strings


class UpdateDialog(QDialog):
    def __init__(self, command: list[str], sudo_session: SudoSession, parent=None):
        super().__init__(parent)
        s = strings.get()
        self.setWindowTitle(s.update_title)
        self.resize(680, 440)

        layout = QVBoxLayout(self)
        self._output = QTextEdit()
        self._output.setReadOnly(True)
        layout.addWidget(self._output)

        self._close_btn = QPushButton(s.update_close_btn)
        self._close_btn.setObjectName("primary-btn")
        self._close_btn.setEnabled(False)
        self._close_btn.clicked.connect(self.accept)
        layout.addWidget(self._close_btn)

        # Use sudo -S when we have a password so we can inject it via stdin
        if sudo_session.password is not None:
            cmd = [command[0], "-S"] + command[1:]
        else:
            cmd = command

        self._process = QProcess(self)
        self._process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self._process.readyReadStandardOutput.connect(self._read_output)
        self._process.finished.connect(self._on_finished)
        self._process.start(cmd[0], cmd[1:])

        if sudo_session.password is not None:
            self._process.write(f"{sudo_session.password}\n".encode())

    def _read_output(self):
        data = self._process.readAllStandardOutput().data().decode(errors="replace")
        self._output.append(data.rstrip())

    def _on_finished(self, code: int, _status):
        s = strings.get()
        if code == 0:
            self._output.append(s.update_success)
        else:
            self._output.append(s.update_failed.format(code=code))
        self._close_btn.setEnabled(True)

    def closeEvent(self, event):
        if self._process.state() != QProcess.ProcessState.NotRunning:
            self._process.kill()
            self._process.waitForFinished(2000)
        super().closeEvent(event)
