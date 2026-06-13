from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame
)

from os_optimizer.sudo_session import SudoSession, validate_password
from os_optimizer.ui import strings


class AuthDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        s = strings.get()
        self.setWindowTitle(s.auth_title)
        self.setFixedWidth(420)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowStaysOnTopHint)
        self._session: SudoSession | None = None
        self._setup_ui()

    def _setup_ui(self):
        s = strings.get()
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        icon_label = QLabel(s.auth_icon)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("font-size: 36px;")
        layout.addWidget(icon_label)

        title = QLabel(s.auth_heading)
        title.setObjectName("section-title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        desc = QLabel(s.auth_description)
        desc.setObjectName("metric-label")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #313244;")
        layout.addWidget(sep)

        self._password_input = QLineEdit()
        self._password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._password_input.setPlaceholderText(s.auth_placeholder)
        self._password_input.setStyleSheet(
            "background: #313244; border: 1px solid #45475a; border-radius: 8px;"
            "padding: 10px 12px; color: #cdd6f4; font-size: 13px;"
        )
        self._password_input.returnPressed.connect(self._authenticate)
        layout.addWidget(self._password_input)

        self._error_label = QLabel("")
        self._error_label.setObjectName("badge-error")
        self._error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._error_label.hide()
        layout.addWidget(self._error_label)

        btns = QHBoxLayout()
        skip_btn = QPushButton(s.auth_skip_btn)
        skip_btn.setObjectName("danger-btn")
        skip_btn.clicked.connect(self._skip)

        self._auth_btn = QPushButton(s.auth_confirm_btn)
        self._auth_btn.setObjectName("primary-btn")
        self._auth_btn.clicked.connect(self._authenticate)

        btns.addWidget(skip_btn)
        btns.addWidget(self._auth_btn)
        layout.addLayout(btns)

    def _authenticate(self):
        s = strings.get()
        password = self._password_input.text()
        if not password:
            self._show_error(s.auth_error_empty)
            return

        self._auth_btn.setEnabled(False)
        self._auth_btn.setText(s.auth_verifying)
        self.repaint()

        if validate_password(password):
            self._session = SudoSession(password=password)
            self.accept()
        else:
            self._show_error(s.auth_error_wrong)
            self._password_input.clear()
            self._auth_btn.setEnabled(True)
            self._auth_btn.setText(s.auth_confirm_btn)

    def _skip(self):
        self._session = SudoSession(password=None)
        self.reject()

    def _show_error(self, msg: str):
        self._error_label.setText(msg)
        self._error_label.show()

    def get_session(self) -> SudoSession:
        return self._session or SudoSession(password=None)
