import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings

# Importazioni relative
from core.exporter import DirectoryExporter
from core.filters import FilterManager
from core.config_manager import ConfigManager
from ui.main_window import MainWindow

def main():
    # Crea le directory per i moduli se non esistono
    os.makedirs("core", exist_ok=True)
    os.makedirs("ui", exist_ok=True)
    os.makedirs("utils", exist_ok=True)
    
    # Inizializza l'applicazione
    app = QApplication(sys.argv)
    app.setApplicationName("Directory Structure Exporter")
    app.setOrganizationName("DirectoryExporter")

    settings = QSettings()
    
    # Crea gli oggetti core
    filter_manager = FilterManager()
    config_manager = ConfigManager(filter_manager, settings)
    exporter = DirectoryExporter(filter_manager)
    
    # Crea e mostra la finestra principale
    window = MainWindow(exporter, filter_manager, config_manager)
    window.show()
    
    # Avvia il ciclo di eventi
    sys.exit(app.exec())

if __name__ == "__main__":
    main()