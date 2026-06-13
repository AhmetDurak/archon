from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QStackedWidget, QSizePolicy
)

_ICON_PATH = Path(__file__).parent.parent / "assets" / "icon.svg"

from os_optimizer.core.interfaces import IDiskAnalyzer, IPackageManager, IHealthChecker
from os_optimizer.sudo_session import SudoSession
from os_optimizer.ui import strings
from os_optimizer.ui.views.dashboard_view import DashboardView
from os_optimizer.ui.views.disk_view import DiskView
from os_optimizer.ui.views.packages_view import PackagesView
from os_optimizer.ui.views.health_view import HealthView
from os_optimizer.ui.views.apps_view import AppsView


class MainWindow(QMainWindow):
    def __init__(
        self,
        disk: IDiskAnalyzer,
        packages: IPackageManager,
        health: IHealthChecker,
        sudo_session: SudoSession,
    ):
        super().__init__()
        s = strings.get()
        self.setWindowTitle(s.app_name)
        self.setMinimumSize(960, 640)
        self.resize(1100, 700)

        if _ICON_PATH.exists():
            self.setWindowIcon(QIcon(str(_ICON_PATH)))

        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self._build_sidebar())

        self._stack = QStackedWidget()
        self._stack.setObjectName("content")
        layout.addWidget(self._stack, 1)

        self._dashboard = DashboardView(disk, packages, health, sudo_session)
        self._disk_view = DiskView(disk)
        self._packages_view = PackagesView(packages, sudo_session)
        self._health_view = HealthView(health, sudo_session)
        self._apps_view = AppsView(packages, sudo_session)

        self._stack.addWidget(self._dashboard)
        self._stack.addWidget(self._disk_view)
        self._stack.addWidget(self._packages_view)
        self._stack.addWidget(self._health_view)
        self._stack.addWidget(self._apps_view)

        self._pkg_count = 0
        self._health_count = 0
        self._packages_view.summary_ready.connect(self._on_pkg_count)
        self._health_view.summary_ready.connect(self._on_health_count)

        self._nav_buttons[0].setChecked(True)

    def _on_pkg_count(self, n: int):
        self._pkg_count = n
        self._dashboard.refresh_summaries(self._pkg_count, self._health_count)

    def _on_health_count(self, n: int):
        self._health_count = n
        self._dashboard.refresh_summaries(self._pkg_count, self._health_count)

    def _build_sidebar(self) -> QWidget:
        s = strings.get()
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QHBoxLayout()
        header.setContentsMargins(16, 16, 16, 12)
        header.setSpacing(10)

        if _ICON_PATH.exists():
            icon_lbl = QLabel()
            px = QPixmap(str(_ICON_PATH)).scaled(
                32, 32,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            icon_lbl.setPixmap(px)
            header.addWidget(icon_lbl)

        title = QLabel(s.app_name)
        title.setObjectName("app-title")
        title.setContentsMargins(0, 0, 0, 0)
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        nav_items = [
            (f"{s.nav_dashboard_icon}  {s.nav_dashboard}", 0),
            (f"{s.nav_disk_icon}  {s.nav_disk}", 1),
            (f"{s.nav_packages_icon}  {s.nav_packages}", 2),
            (f"{s.nav_health_icon}  {s.nav_health}", 3),
            (f"{s.nav_apps_icon}  {s.nav_apps}", 4),
        ]

        self._nav_buttons = []
        for label, index in nav_items:
            btn = QPushButton(label)
            btn.setObjectName("nav-btn")
            btn.setCheckable(True)
            btn.setAutoExclusive(True)
            btn.clicked.connect(lambda _, i=index: self._navigate(i))
            layout.addWidget(btn)
            self._nav_buttons.append(btn)

        layout.addStretch()

        version_label = QLabel(f"v0.1  ·  {s.app_platform}")
        version_label.setObjectName("metric-label")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setContentsMargins(0, 0, 0, 16)
        layout.addWidget(version_label)

        return sidebar

    def _navigate(self, index: int):
        self._stack.setCurrentIndex(index)
        for i, btn in enumerate(self._nav_buttons):
            btn.setChecked(i == index)
