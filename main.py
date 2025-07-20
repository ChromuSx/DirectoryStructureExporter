import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings, QLocale

from core.exporter import DirectoryExporter
from core.filters import FilterManager
from core.config_manager import ConfigManager
from ui.main_window import MainWindow
from utils.resources import resource_manager
from utils.translation_manager import translation_manager

def setup_application_icon(app):
    """Configura l'icona dell'applicazione"""
    icon = resource_manager.get_logo_icon()
    if not icon.isNull():
        app.setWindowIcon(icon)
        return True
    else:
        print("Nessuna icona trovata")
        return False

def setup_translations(settings):
    """Configura il sistema di traduzioni"""
    # Inizializza il sistema di traduzione con QSettings, non QApplication
    translation_manager.initialize(settings)
    
    print(f"Lingua caricata: {translation_manager.get_current_language_name()}")

def main():
    
    app = QApplication(sys.argv)
    app.setApplicationName("Directory Structure Exporter")
    app.setOrganizationName("DirectoryExporter")
    app.setApplicationVersion("2.0")

    # Crea QSettings PRIMA di setup_translations
    settings = QSettings()
    
    # Configura l'icona dell'applicazione
    setup_application_icon(app)
    
    # Configura il sistema di traduzioni (ora con settings, non app)
    setup_translations(settings)
    
    filter_manager = FilterManager()
    config_manager = ConfigManager(filter_manager, settings)
    exporter = DirectoryExporter(filter_manager)
    
    window = MainWindow(exporter, filter_manager, config_manager)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()