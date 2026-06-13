from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QPushButton, QLineEdit,
)

from os_optimizer.core.interfaces import IPackageManager, InstalledApp
from os_optimizer.sudo_session import SudoSession
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


# Column indices
_C_NAME    = 0
_C_VERSION = 1
_C_SIZE    = 2
_C_DATE    = 3
_C_DESC    = 4
_C_ACTION  = 5


class AppsView(QWidget):
    package_removed = Signal()

    def __init__(self, manager: IPackageManager, sudo_session: SudoSession, parent=None):
        super().__init__(parent)
        self._manager = manager
        self._sudo = sudo_session
        self._worker: _AppsWorker | None = None
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

        self._table = QTableWidget(0, 6)
        self._table.setHorizontalHeaderLabels([
            s.apps_col_name,
            s.apps_col_version,
            s.apps_col_size,
            s.apps_col_installed,
            s.apps_col_desc,
            s.apps_col_action,
        ])
        hdr = self._table.horizontalHeader()
        hdr.setSectionResizeMode(_C_NAME,    hdr.ResizeMode.Interactive)
        hdr.setSectionResizeMode(_C_VERSION, hdr.ResizeMode.Interactive)
        hdr.setSectionResizeMode(_C_SIZE,    hdr.ResizeMode.Interactive)
        hdr.setSectionResizeMode(_C_DATE,    hdr.ResizeMode.Interactive)
        hdr.setSectionResizeMode(_C_DESC,    hdr.ResizeMode.Stretch)
        hdr.setSectionResizeMode(_C_ACTION,  hdr.ResizeMode.ResizeToContents)
        hdr.setStretchLastSection(False)
        self._table.setColumnWidth(_C_NAME,    180)
        self._table.setColumnWidth(_C_VERSION, 100)
        self._table.setColumnWidth(_C_SIZE,    110)
        self._table.setColumnWidth(_C_DATE,    100)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._table.setSortingEnabled(True)
        self._table.setWordWrap(False)
        self._table.verticalHeader().setDefaultSectionSize(32)
        self._table.sortByColumn(_C_SIZE, Qt.SortOrder.DescendingOrder)
        root.addWidget(self._table)

    def _fetch(self):
        if self._worker and self._worker.isRunning():
            return
        s = strings.get()
        self._refresh_btn.setEnabled(False)
        self._search.setEnabled(False)
        self._status.setText(s.apps_loading)
        self._table.setRowCount(0)

        self._worker = _AppsWorker(self._manager)
        self._worker.done.connect(self._on_done)
        self._worker.start()

    def _on_done(self, apps: list[InstalledApp]):
        s = strings.get()
        self._refresh_btn.setEnabled(True)
        self._search.setEnabled(True)

        total_bytes = sum(a.size_bytes for a in apps)
        self._status.setText(s.apps_n_packages.format(n=len(apps), size=_fmt_bytes(total_bytes)))

        self._table.setSortingEnabled(False)
        self._table.setRowCount(len(apps))
        for i, app in enumerate(apps):
            self._table.setItem(i, _C_NAME, QTableWidgetItem(app.name))
            self._table.setItem(i, _C_VERSION, QTableWidgetItem(app.version))

            size_item = _SizeItem(_fmt_bytes(app.size_bytes), app.size_bytes)
            size_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self._table.setItem(i, _C_SIZE, size_item)

            date_str = app.install_date.strftime("%Y-%m-%d") if app.install_date else "—"
            self._table.setItem(i, _C_DATE, QTableWidgetItem(date_str))

            desc_item = QTableWidgetItem(app.description)
            desc_item.setToolTip(app.description)   # full text on hover
            self._table.setItem(i, _C_DESC, desc_item)

            btn = QPushButton(s.apps_remove_btn)
            btn.setObjectName("danger-table-btn")
            btn.clicked.connect(
                lambda _, cmd=f"sudo pacman -Rns --noconfirm {app.name}": self._remove(cmd)
            )
            self._table.setCellWidget(i, _C_ACTION, btn)

        self._table.setSortingEnabled(True)
        self._table.sortByColumn(_C_SIZE, Qt.SortOrder.DescendingOrder)
        self._filter(self._search.text())

    def _remove(self, command: str):
        from os_optimizer.ui.fix_dialog import FixDialog
        btn = self.sender()
        row = next(
            (r for r in range(self._table.rowCount())
             if self._table.cellWidget(r, _C_ACTION) is btn),
            -1,
        )
        dlg = FixDialog(command, self._sudo, self, title=strings.get().apps_remove_title)
        if dlg.exec():
            if row != -1:
                self._table.removeRow(row)
            self._update_status()
            self._fetch()
            self.package_removed.emit()

    def _update_status(self):
        s = strings.get()
        total = sum(
            self._table.item(r, _C_SIZE)._raw
            for r in range(self._table.rowCount())
            if isinstance(self._table.item(r, _C_SIZE), _SizeItem)
        )
        self._status.setText(
            s.apps_n_packages.format(n=self._table.rowCount(), size=_fmt_bytes(total))
        )

    def _filter(self, text: str):
        query = text.strip().lower()
        for row in range(self._table.rowCount()):
            name_item = self._table.item(row, _C_NAME)
            matches = not query or (name_item and query in name_item.text().lower())
            self._table.setRowHidden(row, not matches)
