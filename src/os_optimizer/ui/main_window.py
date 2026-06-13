from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QStackedWidget, QSizePolicy
)

from os_optimizer.core.interfaces import IDiskAnalyzer, IPackageManager, IHealthChecker
from os_optimizer.ui.views.dashboard_view import DashboardView
from os_optimizer.ui.views.disk_view import DiskView
from os_optimizer.ui.views.packages_view import PackagesView
from os_optimizer.ui.views.health_view import HealthView


class MainWindow(QMainWindow):
    def __init__(
        self,
        disk: IDiskAnalyzer,
        packages: IPackageManager,
        health: IHealthChecker,
    ):
        super().__init__()
        self.setWindowTitle("OS Optimizer")
        self.setMinimumSize(960, 640)
        self.resize(1100, 700)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self._build_sidebar())

        self._stack = QStackedWidget()
        self._stack.setObjectName("content")
        layout.addWidget(self._stack, 1)

        # Create views
        self._dashboard = DashboardView(disk, packages, health)
        self._disk_view = DiskView(disk)
        self._packages_view = PackagesView(packages)
        self._health_view = HealthView(health)

        self._stack.addWidget(self._dashboard)
        self._stack.addWidget(self._disk_view)
        self._stack.addWidget(self._packages_view)
        self._stack.addWidget(self._health_view)

        # Wire summary signals back to dashboard
        self._packages_view.summary_ready.connect(
            lambda n: self._dashboard.refresh_summaries(n, self._last_health_count)
        )
        self._health_view.summary_ready.connect(
            lambda n: self._update_health_count(n)
        )
        self._last_health_count = 0

        self._nav_buttons[0].setChecked(True)

    def _update_health_count(self, n: int):
        self._last_health_count = n
        # Trigger dashboard refresh with current pkg count (unknown at this point, 0 is safe default)
        # Dashboard will get updated when packages_view also fires
        self._dashboard.refresh_summaries(0, n)

    def _build_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        title = QLabel("OS Optimizer")
        title.setObjectName("app-title")
        layout.addWidget(title)

        nav_items = [
            ("📊  Dashboard", 0),
            ("💾  Disk Usage", 1),
            ("📦  Packages", 2),
            ("🏥  Health", 3),
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

        version_label = QLabel("v0.1  ·  Arch Linux")
        version_label.setObjectName("metric-label")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setContentsMargins(0, 0, 0, 16)
        layout.addWidget(version_label)

        return sidebar

    def _navigate(self, index: int):
        self._stack.setCurrentIndex(index)
        for i, btn in enumerate(self._nav_buttons):
            btn.setChecked(i == index)
