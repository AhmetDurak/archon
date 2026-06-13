CATPPUCCIN_MOCHA = """
/* Catppuccin Mocha */

QMainWindow, QDialog, QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-family: "Segoe UI", "Noto Sans", sans-serif;
    font-size: 13px;
}

/* Sidebar */
#sidebar {
    background-color: #181825;
    border-right: 1px solid #313244;
    min-width: 200px;
    max-width: 200px;
}

#app-title {
    color: #89b4fa;
    font-size: 15px;
    font-weight: bold;
    padding: 20px 16px 12px 16px;
}

QPushButton#nav-btn {
    background-color: transparent;
    color: #a6adc8;
    border: none;
    border-radius: 8px;
    text-align: left;
    padding: 10px 16px;
    font-size: 13px;
    margin: 2px 8px;
}

QPushButton#nav-btn:hover {
    background-color: #313244;
    color: #cdd6f4;
}

QPushButton#nav-btn:checked {
    background-color: #313244;
    color: #89b4fa;
    font-weight: bold;
}

/* Content area */
#content {
    background-color: #1e1e2e;
    padding: 24px;
}

/* Cards */
#card {
    background-color: #181825;
    border: 1px solid #313244;
    border-radius: 12px;
    padding: 16px;
}

/* Section headers */
QLabel#section-title {
    color: #cdd6f4;
    font-size: 20px;
    font-weight: bold;
    margin-bottom: 4px;
}

QLabel#section-sub {
    color: #6c7086;
    font-size: 12px;
    margin-bottom: 16px;
}

/* Metric labels */
QLabel#metric-label {
    color: #a6adc8;
    font-size: 12px;
}

QLabel#metric-value {
    color: #cdd6f4;
    font-size: 22px;
    font-weight: bold;
}

/* Progress bars */
QProgressBar {
    background-color: #313244;
    border: none;
    border-radius: 4px;
    height: 8px;
    text-align: center;
    color: transparent;
}

QProgressBar::chunk {
    border-radius: 4px;
    background-color: #89b4fa;
}

QProgressBar[critical="true"]::chunk {
    background-color: #f38ba8;
}

QProgressBar[warning="true"]::chunk {
    background-color: #f9e2af;
}

/* Tables */
QTableWidget {
    background-color: #181825;
    gridline-color: #313244;
    border: 1px solid #313244;
    border-radius: 8px;
    alternate-background-color: #1e1e2e;
    selection-background-color: #313244;
    selection-color: #cdd6f4;
}

QTableWidget::item {
    padding: 6px 10px;
    border: none;
}

QHeaderView::section {
    background-color: #181825;
    color: #6c7086;
    font-size: 11px;
    font-weight: bold;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding: 8px 10px;
    border: none;
    border-bottom: 1px solid #313244;
}

/* Buttons */
QPushButton#primary-btn {
    background-color: #89b4fa;
    color: #1e1e2e;
    border: none;
    border-radius: 8px;
    padding: 9px 20px;
    font-weight: bold;
    font-size: 13px;
}

QPushButton#primary-btn:hover {
    background-color: #b4d0ff;
}

QPushButton#primary-btn:disabled {
    background-color: #45475a;
    color: #6c7086;
}

QPushButton#danger-btn {
    background-color: transparent;
    color: #f38ba8;
    border: 1px solid #f38ba8;
    border-radius: 8px;
    padding: 9px 20px;
    font-weight: bold;
}

QPushButton#danger-btn:hover {
    background-color: #f38ba820;
}

/* Status badges */
QLabel#badge-ok {
    background-color: #a6e3a120;
    color: #a6e3a1;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 11px;
}

QLabel#badge-warn {
    background-color: #f9e2af20;
    color: #f9e2af;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 11px;
}

QLabel#badge-error {
    background-color: #f38ba820;
    color: #f38ba8;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 11px;
}

/* Text output area */
QTextEdit {
    background-color: #11111b;
    color: #a6e3a1;
    font-family: "JetBrains Mono", "Fira Code", monospace;
    font-size: 12px;
    border: 1px solid #313244;
    border-radius: 8px;
    padding: 8px;
}

/* Scrollbars */
QScrollBar:vertical {
    background: #1e1e2e;
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: #45475a;
    border-radius: 4px;
    min-height: 20px;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background: #1e1e2e;
    height: 8px;
    border-radius: 4px;
}

QScrollBar::handle:horizontal {
    background: #45475a;
    border-radius: 4px;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}
"""
