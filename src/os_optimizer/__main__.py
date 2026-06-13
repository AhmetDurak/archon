import sys
from PySide6.QtWidgets import QApplication
from os_optimizer.ui.theme import CATPPUCCIN_MOCHA
from os_optimizer.ui.main_window import MainWindow
from os_optimizer import platform as platform_factory


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("OS Optimizer")
    app.setStyleSheet(CATPPUCCIN_MOCHA)

    disk = platform_factory.get_disk_analyzer()
    packages = platform_factory.get_package_manager()
    health = platform_factory.get_health_checker()

    window = MainWindow(disk, packages, health)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
