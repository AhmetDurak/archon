from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QPushButton, QLineEdit,
)

from os_optimizer.core.interfaces import IPackageManager, InstalledApp
from os_optimizer.ui import strings


def _fmt_bytes(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"


class _SizeItem(QTableWidgetItem):
    def __init__(self, display: str, raw: int):
        super().__init__(display)
        self._raw = raw

    def __lt__(self, other: "QTableWidgetItem") -> bool:
        if isinstance(other, _SizeItem):
            return self._raw < other._raw
        return super().__lt__(other)


class _AppsWorker(QThread):
    done = Signal(list)

    def __init__(self, manager: IPackageManager):
        super().__init__()
        self._manager = manager

    def run(self):
        self.done.emit(self._manager.get_installed_packages())


class AppsView(QWidget):
    def __init__(self, manager: IPackageManager, parent=None):
        super().__init__(parent)
        self._manager = manager
        self._worker: _AppsWorker | None = None
        self._all_apps: list[InstalledApp] = []
        self._setup_ui()
        self._fetch()

    def _setup_ui(self):
        s = strings.get()
        root = QVBoxLayout(self)
        root.setSpacing(16)

        title = QLabel(s.apps_title)
        title.setObjectName("section-title")
        sub = QLabel(s.apps_subtitle)
        sub.setObjectName("section-sub")
        root.addWidget(title)
        root.addWidget(sub)

        toolbar = QHBoxLayout()

        self._status = QLabel(s.apps_loading)
        self._status.setObjectName("metric-label")

        self._search = QLineEdit()
        self._search.setPlaceholderText(s.apps_search_placeholder)
        self._search.setFixedWidth(220)
        self._search.textChanged.connect(self._filter)

        self._refresh_btn = QPushButton(s.apps_refresh_btn)
        self._refresh_btn.setObjectName("primary-btn")
        self._refresh_btn.clicked.connect(self._fetch)

        toolbar.addWidget(self._status)
        toolbar.addStretch()
        toolbar.addWidget(self._search)
        toolbar.addWidget(self._refresh_btn)
        root.addLayout(toolbar)

        self._table = QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels([
            s.apps_col_name,
            s.apps_col_version,
            s.apps_col_size,
            s.apps_col_desc,
        ])
        hdr = self._table.horizontalHeader()
        hdr.setSectionResizeMode(0, hdr.ResizeMode.Interactive)
        hdr.setSectionResizeMode(1, hdr.ResizeMode.Interactive)
        hdr.setSectionResizeMode(2, hdr.ResizeMode.Interactive)
        hdr.setSectionResizeMode(3, hdr.ResizeMode.Stretch)
        hdr.setStretchLastSection(False)
        self._table.setColumnWidth(0, 200)
        self._table.setColumnWidth(1, 120)
        self._table.setColumnWidth(2, 120)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._table.setSortingEnabled(True)
        self._table.setWordWrap(False)
        self._table.verticalHeader().setDefaultSectionSize(32)
        # default sort: size descending
        self._table.sortByColumn(2, Qt.SortOrder.DescendingOrder)
        root.addWidget(self._table)

    def _fetch(self):
        if self._worker and self._worker.isRunning():
            return
        s = strings.get()
        self._refresh_btn.setEnabled(False)
        self._search.setEnabled(False)
        self._status.setText(s.apps_loading)
        self._table.setRowCount(0)
        self._all_apps = []

        self._worker = _AppsWorker(self._manager)
        self._worker.done.connect(self._on_done)
        self._worker.start()

    def _on_done(self, apps: list[InstalledApp]):
        s = strings.get()
        self._all_apps = apps
        self._refresh_btn.setEnabled(True)
        self._search.setEnabled(True)

        total_bytes = sum(a.size_bytes for a in apps)
        self._status.setText(s.apps_n_packages.format(n=len(apps), size=_fmt_bytes(total_bytes)))

        self._table.setSortingEnabled(False)
        self._table.setRowCount(len(apps))
        for i, app in enumerate(apps):
            self._table.setItem(i, 0, QTableWidgetItem(app.name))
            self._table.setItem(i, 1, QTableWidgetItem(app.version))
            size_item = _SizeItem(_fmt_bytes(app.size_bytes), app.size_bytes)
            size_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self._table.setItem(i, 2, size_item)
            self._table.setItem(i, 3, QTableWidgetItem(app.description))
        self._table.setSortingEnabled(True)
        self._table.sortByColumn(2, Qt.SortOrder.DescendingOrder)

        self._filter(self._search.text())

    def _filter(self, text: str):
        query = text.strip().lower()
        for row in range(self._table.rowCount()):
            name_item = self._table.item(row, 0)
            matches = not query or (name_item and query in name_item.text().lower())
            self._table.setRowHidden(row, not matches)
