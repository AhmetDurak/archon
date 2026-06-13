import psutil
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QFrame, QPushButton
)

from os_optimizer.core.interfaces import IDiskAnalyzer, IPackageManager, IHealthChecker
from os_optimizer.sudo_session import SudoSession
from os_optimizer.ui import strings


def _fmt_bytes(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"


class MetricCard(QFrame):
    def __init__(self, label: str, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        self._label = QLabel(label)
        self._label.setObjectName("metric-label")
        self._value = QLabel("—")
        self._value.setObjectName("metric-value")
        self._bar = QProgressBar()
        self._bar.setRange(0, 100)
        self._bar.setFixedHeight(8)
        self._sub = QLabel("")
        self._sub.setObjectName("metric-label")

        layout.addWidget(self._label)
        layout.addWidget(self._value)
        layout.addWidget(self._bar)
        layout.addWidget(self._sub)

    def update(self, percent: float, value_text: str, sub_text: str = ""):
        self._value.setText(value_text)
        self._bar.setValue(int(percent))
        self._sub.setText(sub_text)
        self._bar.setProperty("critical", percent >= 90)
        self._bar.setProperty("warning", 75 <= percent < 90)
        self._bar.style().unpolish(self._bar)
        self._bar.style().polish(self._bar)


class DashboardView(QWidget):
    def __init__(
        self,
        disk: IDiskAnalyzer,
        packages: IPackageManager,
        health: IHealthChecker,
        sudo_session: SudoSession,
        parent=None,
    ):
        super().__init__(parent)
        self._disk = disk
        self._packages = packages
        self._sudo = sudo_session
        self._setup_ui()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh_metrics)
        self._timer.start(2000)
        self._refresh_metrics()

    def _setup_ui(self):
        s = strings.get()
        root = QVBoxLayout(self)
        root.setSpacing(20)

        title = QLabel(s.dash_title)
        title.setObjectName("section-title")
        sub = QLabel(s.dash_subtitle)
        sub.setObjectName("section-sub")
        root.addWidget(title)
        root.addWidget(sub)

        cards_row = QHBoxLayout()
        cards_row.setSpacing(12)
        self._cpu_card = MetricCard(s.dash_cpu)
        self._ram_card = MetricCard(s.dash_ram)
        self._disk_card = MetricCard(s.dash_disk_root)
        cards_row.addWidget(self._cpu_card)
        cards_row.addWidget(self._ram_card)
        cards_row.addWidget(self._disk_card)
        root.addLayout(cards_row)

        summary_row = QHBoxLayout()
        summary_row.setSpacing(12)
        self._pkg_card = self._summary_card(s.dash_packages_label, s.dash_checking)
        self._health_card = self._summary_card(s.dash_health_label, s.dash_checking)
        summary_row.addWidget(self._pkg_card[0])
        summary_row.addWidget(self._health_card[0])
        root.addLayout(summary_row)

        self._update_btn = QPushButton(s.dash_update_btn)
        self._update_btn.setObjectName("primary-btn")
        self._update_btn.setFixedHeight(42)
        self._update_btn.clicked.connect(self._run_update)
        self._update_btn.hide()
        root.addWidget(self._update_btn)

        root.addStretch()

    def _summary_card(self, label: str, initial: str):
        frame = QFrame()
        frame.setObjectName("card")
        layout = QVBoxLayout(frame)
        lbl = QLabel(label)
        lbl.setObjectName("metric-label")
        val = QLabel(initial)
        val.setObjectName("metric-value")
        layout.addWidget(lbl)
        layout.addWidget(val)
        return frame, val

    def _refresh_metrics(self):
        cpu = psutil.cpu_percent(interval=None)
        self._cpu_card.update(cpu, f"{cpu:.0f}%")

        mem = psutil.virtual_memory()
        self._ram_card.update(
            mem.percent, f"{mem.percent:.0f}%",
            f"{_fmt_bytes(mem.used)} / {_fmt_bytes(mem.total)}",
        )

        partitions = self._disk.get_partitions()
        root_part = next((p for p in partitions if p.mountpoint == "/"), None)
        if root_part:
            self._disk_card.update(
                root_part.percent, f"{root_part.percent:.0f}%",
                f"{_fmt_bytes(root_part.used)} / {_fmt_bytes(root_part.total)}",
            )

    def refresh_summaries(self, pkg_count: int, issue_count: int):
        s = strings.get()
        color_pkg = "#f9e2af" if pkg_count > 0 else "#a6e3a1"
        color_health = "#f38ba8" if issue_count > 0 else "#a6e3a1"

        val_pkg = self._pkg_card[1]
        val_pkg.setText(s.dash_n_updates.format(n=pkg_count))
        val_pkg.setStyleSheet(f"color: {color_pkg}; font-size: 22px; font-weight: bold;")

        val_health = self._health_card[1]
        val_health.setText(s.dash_n_issues.format(n=issue_count))
        val_health.setStyleSheet(f"color: {color_health}; font-size: 22px; font-weight: bold;")

        self._update_btn.setVisible(pkg_count > 0)

    def _run_update(self):
        from os_optimizer.ui.update_dialog import UpdateDialog
        dlg = UpdateDialog(self._packages.get_update_command(), self._sudo, self)
        dlg.exec()
