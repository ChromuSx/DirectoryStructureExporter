import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings

from core.exporter import DirectoryExporter
from core.filters import FilterManager
from core.config_manager import ConfigManager
from ui.main_window import MainWindow
from utils.resources import resource_manager

def setup_application_icon(app):
    """Configura l'icona dell'applicazione"""
    icon = resource_manager.get_logo_icon()
    if not icon.isNull():
        app.setWindowIcon(icon)
        return True
    else:
        print("Nessuna icona trovata")
        return False

def main():
    # Crea le cartelle necessarie
    os.makedirs("core", exist_ok=True)
    os.makedirs("ui", exist_ok=True)
    os.makedirs("utils", exist_ok=True)
    os.makedirs("assets", exist_ok=True)  # AGGIUNTA: cartella per assets
    
    app = QApplication(sys.argv)
    app.setApplicationName("Directory Structure Exporter")
    app.setOrganizationName("DirectoryExporter")

    # AGGIUNTA: Configura l'icona dell'applicazione
    setup_application_icon(app)

    settings = QSettings()
    
    filter_manager = FilterManager()
    config_manager = ConfigManager(filter_manager, settings)
    exporter = DirectoryExporter(filter_manager)
    
    window = MainWindow(exporter, filter_manager, config_manager)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()