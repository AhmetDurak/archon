import psutil
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QFrame
)

from os_optimizer.core.interfaces import IDiskAnalyzer, IPackageManager, IHealthChecker


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
        parent=None,
    ):
        super().__init__(parent)
        self._disk = disk
        self._packages = packages
        self._health = health
        self._setup_ui()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh_metrics)
        self._timer.start(2000)
        self._refresh_metrics()

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setSpacing(20)

        title = QLabel("Dashboard")
        title.setObjectName("section-title")
        sub = QLabel("Live system overview")
        sub.setObjectName("section-sub")
        root.addWidget(title)
        root.addWidget(sub)

        # Metric cards row
        cards_row = QHBoxLayout()
        cards_row.setSpacing(12)

        self._cpu_card = MetricCard("CPU Usage")
        self._ram_card = MetricCard("Memory")
        self._disk_card = MetricCard("Disk  /")
        cards_row.addWidget(self._cpu_card)
        cards_row.addWidget(self._ram_card)
        cards_row.addWidget(self._disk_card)
        root.addLayout(cards_row)

        # Summary row
        summary_row = QHBoxLayout()
        summary_row.setSpacing(12)
        self._pkg_card = self._summary_card("Packages", "Checking…")
        self._health_card = self._summary_card("Health Issues", "Checking…")
        summary_row.addWidget(self._pkg_card[0])
        summary_row.addWidget(self._health_card[0])
        root.addLayout(summary_row)

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
            mem.percent,
            f"{mem.percent:.0f}%",
            f"{_fmt_bytes(mem.used)} / {_fmt_bytes(mem.total)}",
        )

        partitions = self._disk.get_partitions()
        root_part = next((p for p in partitions if p.mountpoint == "/"), None)
        if root_part:
            self._disk_card.update(
                root_part.percent,
                f"{root_part.percent:.0f}%",
                f"{_fmt_bytes(root_part.used)} / {_fmt_bytes(root_part.total)}",
            )

    def refresh_summaries(self, pkg_count: int, issue_count: int):
        color_pkg = "#f9e2af" if pkg_count > 0 else "#a6e3a1"
        color_health = "#f38ba8" if issue_count > 0 else "#a6e3a1"

        val_pkg = self._pkg_card[1]
        val_pkg.setText(f"{pkg_count} updates")
        val_pkg.setStyleSheet(f"color: {color_pkg}; font-size: 22px; font-weight: bold;")

        val_health = self._health_card[1]
        val_health.setText(f"{issue_count} issues")
        val_health.setStyleSheet(f"color: {color_health}; font-size: 22px; font-weight: bold;")
