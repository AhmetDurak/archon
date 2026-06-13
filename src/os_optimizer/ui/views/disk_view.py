from PySide6.QtCore import Qt, QThread, Signal, QRectF
from PySide6.QtGui import QPainter, QColor, QPen, QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar,
    QTableWidget, QTableWidgetItem, QPushButton, QFrame, QComboBox,
    QSizePolicy
)

from os_optimizer.core.interfaces import IDiskAnalyzer, DiskPartition
from os_optimizer.ui import strings


class _SizeItem(QTableWidgetItem):
    """Table item that sorts by raw byte value instead of display string."""
    def __init__(self, display: str, raw_bytes: int):
        super().__init__(display)
        self._raw = raw_bytes

    def __lt__(self, other: "QTableWidgetItem") -> bool:
        if isinstance(other, _SizeItem):
            return self._raw < other._raw
        return super().__lt__(other)


def _fmt_bytes(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"


# Catppuccin Mocha palette for chart slices
_SLICE_COLORS = ["#89b4fa", "#a6e3a1", "#fab387", "#cba6f7", "#f38ba8", "#f9e2af", "#94e2d5"]


class DonutChart(QWidget):
    """
    Draws a donut chart where each slice represents one partition by total size.
    Slice fill opacity reflects usage (brighter = more used).
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._partitions: list[DiskPartition] = []
        self.setMinimumSize(160, 160)
        self.setMaximumSize(200, 200)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def set_partitions(self, partitions: list[DiskPartition]):
        self._partitions = partitions
        self.update()

    def paintEvent(self, event):
        if not self._partitions:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        margin = 12
        size = min(w, h) - margin * 2
        x = (w - size) / 2
        y = (h - size) / 2
        outer = QRectF(x, y, size, size)

        hole = size * 0.52
        inner = QRectF(x + (size - hole) / 2, y + (size - hole) / 2, hole, hole)

        total = sum(p.total for p in self._partitions) or 1
        angle = 90 * 16  # start at 12 o'clock

        for i, part in enumerate(self._partitions):
            span = max(int(part.total / total * 360 * 16), 1)
            color = QColor(_SLICE_COLORS[i % len(_SLICE_COLORS)])
            # Dim the color based on free space (more used → more vivid)
            color.setAlphaF(0.4 + 0.6 * (part.percent / 100))
            painter.setBrush(color)
            painter.setPen(QPen(QColor("#1e1e2e"), 2))
            painter.drawPie(outer, angle, -span)
            angle -= span

        # Donut hole
        painter.setBrush(QColor("#181825"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(inner)

        # Center text: largest partition %
        main = max(self._partitions, key=lambda p: p.total)
        painter.setPen(QColor("#cdd6f4"))
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(inner.toRect(), Qt.AlignmentFlag.AlignCenter, f"{main.percent:.0f}%")


class DirScanWorker(QThread):
    done = Signal(list)

    def __init__(self, analyzer: IDiskAnalyzer, path: str):
        super().__init__()
        self._analyzer = analyzer
        self._path = path

    def run(self):
        self.done.emit(self._analyzer.get_large_dirs(self._path))


class DiskView(QWidget):
    def __init__(self, analyzer: IDiskAnalyzer, parent=None):
        super().__init__(parent)
        self._analyzer = analyzer
        self._worker = None
        self._setup_ui()
        self._load_partitions()

    def _setup_ui(self):
        s = strings.get()
        root = QVBoxLayout(self)
        root.setSpacing(16)

        title = QLabel(s.disk_title)
        title.setObjectName("section-title")
        sub = QLabel(s.disk_subtitle)
        sub.setObjectName("section-sub")
        root.addWidget(title)
        root.addWidget(sub)

        # Partition card: donut on left, bars on right
        self._parts_card = QFrame()
        self._parts_card.setObjectName("card")
        card_layout = QHBoxLayout(self._parts_card)
        card_layout.setSpacing(20)

        self._donut = DonutChart()
        card_layout.addWidget(self._donut)

        self._parts_bars = QWidget()
        self._parts_layout = QVBoxLayout(self._parts_bars)
        self._parts_layout.setSpacing(10)
        self._parts_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.addWidget(self._parts_bars, 1)

        root.addWidget(self._parts_card)

        # Directory scanner
        dir_header = QHBoxLayout()
        dir_label = QLabel(s.disk_largest_in)
        dir_label.setObjectName("metric-label")
        self._path_combo = QComboBox()
        self._path_combo.addItems(["/", "/home", "/var", "/usr", "/tmp"])

        self._scan_btn = QPushButton(s.disk_scan_btn)
        self._scan_btn.setObjectName("primary-btn")
        self._scan_btn.setFixedWidth(80)
        self._scan_btn.clicked.connect(self._scan_dirs)

        dir_header.addWidget(dir_label)
        dir_header.addWidget(self._path_combo)
        dir_header.addWidget(self._scan_btn)
        dir_header.addStretch()
        root.addLayout(dir_header)

        self._dirs_table = QTableWidget(0, 2)
        self._dirs_table.setHorizontalHeaderLabels([s.disk_col_path, s.disk_col_size])
        dh = self._dirs_table.horizontalHeader()
        dh.setSectionResizeMode(0, dh.ResizeMode.Interactive)
        dh.setSectionResizeMode(1, dh.ResizeMode.Interactive)
        dh.setStretchLastSection(False)
        dh.setDefaultSectionSize(200)
        self._dirs_table.setColumnWidth(0, 480)
        self._dirs_table.setColumnWidth(1, 120)
        self._dirs_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._dirs_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._dirs_table.setAlternatingRowColors(True)
        self._dirs_table.setSortingEnabled(True)
        self._dirs_table.doubleClicked.connect(self._on_dir_double_clicked)
        root.addWidget(self._dirs_table)

        hint = QLabel(s.disk_dblclick_hint)
        hint.setObjectName("metric-label")
        root.addWidget(hint)

    def _load_partitions(self):
        while self._parts_layout.count():
            item = self._parts_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        partitions = self._analyzer.get_partitions()
        self._donut.set_partitions(partitions)

        for part in partitions:
            row = QHBoxLayout()
            lbl = QLabel(f"{part.mountpoint}")
            lbl.setMinimumWidth(80)
            lbl.setMaximumWidth(120)

            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(int(part.percent))
            bar.setFixedHeight(8)
            bar.setProperty("critical", part.percent >= 90)
            bar.setProperty("warning", 75 <= part.percent < 90)

            pct_lbl = QLabel(f"{part.percent:.0f}%  {_fmt_bytes(part.free)} free")
            pct_lbl.setObjectName("metric-label")
            pct_lbl.setMinimumWidth(140)

            row.addWidget(lbl)
            row.addWidget(bar, 1)
            row.addWidget(pct_lbl)
            self._parts_layout.addLayout(row)

        self._parts_layout.addStretch()

    def _scan_dirs(self):
        if self._worker and self._worker.isRunning():
            return
        self._scan_btn.setEnabled(False)
        self._dirs_table.setRowCount(0)
        path = self._path_combo.currentText()
        self._worker = DirScanWorker(self._analyzer, path)
        self._worker.done.connect(self._on_scan_done)
        self._worker.start()

    def _on_scan_done(self, dirs):
        self._scan_btn.setEnabled(True)
        self._dirs_table.setSortingEnabled(False)
        self._dirs_table.setRowCount(len(dirs))
        for i, d in enumerate(dirs):
            self._dirs_table.setItem(i, 0, QTableWidgetItem(d.path))
            size_item = _SizeItem(_fmt_bytes(d.size), d.size)
            size_item.setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
            self._dirs_table.setItem(i, 1, size_item)
        self._dirs_table.setSortingEnabled(True)

    def _on_dir_double_clicked(self, index):
        path_item = self._dirs_table.item(index.row(), 0)
        if not path_item:
            return
        path = path_item.text()
        # Add to combo if not already there, select it, and scan
        if self._path_combo.findText(path) == -1:
            self._path_combo.addItem(path)
        self._path_combo.setCurrentText(path)
        self._scan_dirs()
