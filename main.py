import sys
import os
from PyQt6.QtWidgets import QApplication
from core.exporter import DirectoryExporter
from ui.main_window import MainWindow

def main():
    # Crea le directory per i moduli se non esistono
    os.makedirs("core", exist_ok=True)
    os.makedirs("ui", exist_ok=True)
    
    # Inizializza l'applicazione
    app = QApplication(sys.argv)
    app.setApplicationName("Directory Structure Exporter")
    app.setOrganizationName("DirectoryExporter")
    
    # Crea l'oggetto esportatore
    exporter = DirectoryExporter()
    
    # Crea e mostra la finestra principale
    window = MainWindow(exporter)
    window.show()
    
    # Avvia il ciclo di eventi
    sys.exit(app.exec())

if __name__ == "__main__":
    main()