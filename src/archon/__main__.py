import sys
from PySide6.QtWidgets import QApplication
from archon.ui.theme import CATPPUCCIN_MOCHA
from archon.ui.main_window import MainWindow
from archon.sudo_session import SudoSession, check_passwordless
from archon.ui.auth_dialog import AuthDialog
from archon import platform as platform_factory


def _acquire_sudo_session(app: QApplication) -> SudoSession:
    if check_passwordless():
        return SudoSession(password=None)

    dlg = AuthDialog()
    dlg.exec()
    return dlg.get_session()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Archon")
    app.setStyleSheet(CATPPUCCIN_MOCHA)

    sudo_session = _acquire_sudo_session(app)

    disk = platform_factory.get_disk_analyzer()
    packages = platform_factory.get_package_manager()
    health = platform_factory.get_health_checker()

    window = MainWindow(disk, packages, health, sudo_session)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
