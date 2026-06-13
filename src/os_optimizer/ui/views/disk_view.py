from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar,
    QTableWidget, QTableWidgetItem, QPushButton, QFrame, QComboBox
)

from os_optimizer.core.interfaces import IDiskAnalyzer


def _fmt_bytes(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"


class DirScanWorker(QThread):
    done = Signal(list)

    def __init__(self, analyzer: IDiskAnalyzer, path: str):
        super().__init__()
        self._analyzer = analyzer
        self._path = path

    def run(self):
        result = self._analyzer.get_large_dirs(self._path)
        self.done.emit(result)


class DiskView(QWidget):
    def __init__(self, analyzer: IDiskAnalyzer, parent=None):
        super().__init__(parent)
        self._analyzer = analyzer
        self._worker = None
        self._setup_ui()
        self._load()

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setSpacing(16)

        title = QLabel("Disk Usage")
        title.setObjectName("section-title")
        sub = QLabel("Partition usage and largest directories")
        sub.setObjectName("section-sub")
        root.addWidget(title)
        root.addWidget(sub)

        # Partition bars
        self._parts_frame = QFrame()
        self._parts_frame.setObjectName("card")
        self._parts_layout = QVBoxLayout(self._parts_frame)
        root.addWidget(self._parts_frame)

        # Large dirs
        dir_header = QHBoxLayout()
        dir_label = QLabel("Largest directories in:")
        dir_label.setObjectName("metric-label")
        self._path_combo = QComboBox()
        self._path_combo.addItems(["/", "/home", "/var", "/usr", "/tmp"])
        self._path_combo.currentTextChanged.connect(self._scan_dirs)

        self._scan_btn = QPushButton("Scan")
        self._scan_btn.setObjectName("primary-btn")
        self._scan_btn.setFixedWidth(80)
        self._scan_btn.clicked.connect(self._scan_dirs)

        dir_header.addWidget(dir_label)
        dir_header.addWidget(self._path_combo)
        dir_header.addWidget(self._scan_btn)
        dir_header.addStretch()
        root.addLayout(dir_header)

        self._dirs_table = QTableWidget(0, 2)
        self._dirs_table.setHorizontalHeaderLabels(["Path", "Size"])
        self._dirs_table.horizontalHeader().setStretchLastSection(False)
        self._dirs_table.horizontalHeader().setSectionResizeMode(
            0, self._dirs_table.horizontalHeader().ResizeMode.Stretch
        )
        self._dirs_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._dirs_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._dirs_table.setAlternatingRowColors(True)
        root.addWidget(self._dirs_table)

    def _load(self):
        # Clear old partition rows
        while self._parts_layout.count():
            item = self._parts_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for part in self._analyzer.get_partitions():
            row = QHBoxLayout()
            lbl = QLabel(f"{part.mountpoint} ({part.device})")
            lbl.setMinimumWidth(180)
            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(int(part.percent))
            bar.setFixedHeight(8)
            bar.setProperty("critical", part.percent >= 90)
            bar.setProperty("warning", 75 <= part.percent < 90)
            pct_lbl = QLabel(f"{part.percent:.0f}%  {_fmt_bytes(part.free)} free")
            pct_lbl.setObjectName("metric-label")
            pct_lbl.setMinimumWidth(160)
            row.addWidget(lbl)
            row.addWidget(bar, 1)
            row.addWidget(pct_lbl)
            self._parts_layout.addLayout(row)

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
        self._dirs_table.setRowCount(len(dirs))
        for i, d in enumerate(dirs):
            self._dirs_table.setItem(i, 0, QTableWidgetItem(d.path))
            size_item = QTableWidgetItem(_fmt_bytes(d.size))
            size_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self._dirs_table.setItem(i, 1, size_item)
