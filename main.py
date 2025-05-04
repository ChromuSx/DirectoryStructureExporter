import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings

from core.exporter import DirectoryExporter
from core.filters import FilterManager
from core.config_manager import ConfigManager
from ui.main_window import MainWindow

def main():
    os.makedirs("core", exist_ok=True)
    os.makedirs("ui", exist_ok=True)
    os.makedirs("utils", exist_ok=True)
    
    app = QApplication(sys.argv)
    app.setApplicationName("Directory Structure Exporter")
    app.setOrganizationName("DirectoryExporter")

    settings = QSettings()
    
    filter_manager = FilterManager()
    config_manager = ConfigManager(filter_manager, settings)
    exporter = DirectoryExporter(filter_manager)
    
    window = MainWindow(exporter, filter_manager, config_manager)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()