import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings, QTranslator, QLocale

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

def setup_translations(app):
    """Configura il sistema di traduzioni"""
    # Inizializza il sistema di traduzione
    translation_manager.app = app
    
    # Carica la lingua salvata o quella di sistema
    saved_language = QSettings().value("language", None)
    
    if saved_language:
        # Usa la lingua salvata
        translation_manager.load_translation(saved_language)
    else:
        # Rileva la lingua di sistema
        system_locale = QLocale.system().name()[:2]  # Prende solo il codice della lingua (es. 'en' da 'en_US')
        
        if system_locale in translation_manager.get_available_languages():
            translation_manager.load_translation(system_locale)
            # Salva la lingua rilevata
            QSettings().setValue("language", system_locale)
        else:
            # Default a italiano
            translation_manager.load_translation('it')
            QSettings().setValue("language", 'it')
    
    print(f"Lingua caricata: {translation_manager.get_current_language_name()}")

def main():
    # Crea le cartelle necessarie
    os.makedirs("core", exist_ok=True)
    os.makedirs("ui", exist_ok=True)
    os.makedirs("utils", exist_ok=True)
    os.makedirs("assets", exist_ok=True)
    os.makedirs("translations", exist_ok=True)  # Cartella per le traduzioni
    
    app = QApplication(sys.argv)
    app.setApplicationName("Directory Structure Exporter")
    app.setOrganizationName("DirectoryExporter")
    app.setApplicationVersion("2.0")

    # Configura l'icona dell'applicazione
    setup_application_icon(app)
    
    # Configura il sistema di traduzioni
    setup_translations(app)

    settings = QSettings()
    
    filter_manager = FilterManager()
    config_manager = ConfigManager(filter_manager, settings)
    exporter = DirectoryExporter(filter_manager)
    
    window = MainWindow(exporter, filter_manager, config_manager)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()