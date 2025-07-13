from PyQt6.QtWidgets import (QMainWindow, QTabWidget, QVBoxLayout, QHBoxLayout, 
                           QWidget, QLabel, QComboBox, QPushButton, QStatusBar, 
                           QApplication)
from PyQt6.QtCore import QSettings
from PyQt6.QtGui import QColor, QIcon, QPalette

from ui.export_tab import ExportTab
from ui.config_tab import ConfigTab
from ui.filters_tab import FiltersTab
from utils.resources import resource_manager

class MainWindow(QMainWindow):
    def __init__(self, exporter, filter_manager, config_manager):
        super().__init__()
        
        # Salva i riferimenti ai manager
        self.exporter = exporter
        self.filter_manager = filter_manager
        self.config_manager = config_manager
        
        # Carica le impostazioni
        self.settings = QSettings()
        
        # Inizializza l'interfaccia utente
        self.initUI()
        
        # Carica le impostazioni salvate
        self.load_settings()

    def create_header_with_logo(self):
        """Crea un header con logo e titolo"""
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(10, 10, 10, 5)
        
        # Logo
        logo_label = QLabel()
        pixmap = resource_manager.get_logo_pixmap((48, 48))
        if not pixmap.isNull():
            logo_label.setPixmap(pixmap)
        else:
            logo_label.setText("📁")  # Fallback emoji
            logo_label.setStyleSheet("font-size: 32px;")
        
        # Titolo dell'applicazione
        title_label = QLabel("Directory Structure Exporter")
        title_label.setStyleSheet("""
            font-size: 18px; 
            font-weight: bold; 
            color: #2563eb;
            margin-left: 10px;
        """)
        
        # Layout header
        header_layout.addWidget(logo_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch(1)
        
        return header_widget
    
    def initUI(self):
        """Inizializza l'interfaccia utente"""
        # Imposta il titolo e la dimensione della finestra
        self.setWindowTitle("Directory Structure Exporter")
        self.resize(900, 600)

        # Widget centrale
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)

        # AGGIUNTA: Header con logo
        header = self.create_header_with_logo()
        main_layout.addWidget(header)

        # Linea separatrice (opzionale)
        separator = QWidget()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #e5e7eb;")
        main_layout.addWidget(separator)
        
        try:
            # Prova diversi percorsi per il logo
            logo_paths = [
                "assets/logo.png",
                "assets/logo_small.png", 
                "logo.png",
                "assets/logo.ico"
            ]
            
            for path in logo_paths:
                try:
                    icon = QIcon(path)
                    if not icon.isNull():
                        self.setWindowIcon(icon)
                        # Imposta anche l'icona dell'applicazione
                        QApplication.instance().setWindowIcon(icon)
                        break
                except:
                    continue
        except Exception as e:
            print(f"Impossibile caricare il logo: {e}")
        
        # Crea una barra di stato
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Pronto")

        self.export_tab = ExportTab(self.exporter, self.filter_manager, self.settings)
        self.config_tab = ConfigTab(self.filter_manager, self.config_manager, self.settings)
        self.filters_tab = FiltersTab(self.filter_manager, self.settings)
        
        # Widget centrale
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # Crea una barra degli strumenti in alto
        toolbar_layout = QHBoxLayout()
        
        # Selezione del tema
        theme_label = QLabel("Tema:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Sistema", "Chiaro", "Scuro"])
        self.theme_combo.currentIndexChanged.connect(self.change_theme)
        
        toolbar_layout.addWidget(theme_label)
        toolbar_layout.addWidget(self.theme_combo)
        toolbar_layout.addStretch(1)
        
        # Aggiungi la barra degli strumenti al layout principale
        main_layout.addLayout(toolbar_layout)
        
        # Crea il widget con le schede
        self.tabs = QTabWidget()
        
        # Crea le diverse schede
        self.export_tab = ExportTab(self.exporter, self.filter_manager, self.settings)
        self.config_tab = ConfigTab(self.filter_manager, self.config_manager, self.settings)
        self.filters_tab = FiltersTab(self.filter_manager, self.settings)
        
        # Aggiungi le schede al widget
        self.tabs.addTab(self.export_tab, "Esportazione")
        self.tabs.addTab(self.filters_tab, "Filtri")
        self.tabs.addTab(self.config_tab, "Configurazione")
        
        # Aggiungi il widget delle schede al layout principale
        main_layout.addWidget(self.tabs)
        
        # Imposta il widget centrale
        self.setCentralWidget(central_widget)

        self.export_tab.config_tab = self.config_tab
        self.export_tab.filters_tab = self.filters_tab
        self.config_tab.export_tab = self.export_tab
        self.config_tab.filters_tab = self.filters_tab
        self.filters_tab.config_tab = self.config_tab
        self.filters_tab.export_tab = self.export_tab
        
    def load_settings(self):
        """Carica le impostazioni dell'interfaccia utente"""
        # Carica le impostazioni dell'interfaccia utente
        theme_text = self.settings.value("theme", "Sistema")
        index = self.theme_combo.findText(theme_text)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
            self.change_theme()
    
    def save_settings(self):
        """Salva le impostazioni utente"""
        # Salva il tema
        self.settings.setValue("theme", self.theme_combo.currentText())

        self.config_manager.save_presets()
        
        # Invoca il salvataggio delle impostazioni per ogni scheda
        self.export_tab.save_settings()
        self.config_tab.save_settings()
        self.filters_tab.save_settings()

    def change_theme(self):
        """Cambia il tema dell'applicazione"""
        theme = self.theme_combo.currentText()
        
        if theme == "Chiaro":
            self.set_light_theme()
        elif theme == "Scuro":
            self.set_dark_theme()
        else:  # Sistema
            self.reset_theme()

    def set_light_theme(self):
        """Imposta il tema chiaro"""
        app = QApplication.instance()
        app.setStyle("Fusion")
        
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(230, 230, 230))
        palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.Link, QColor(0, 0, 255))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        
        app.setPalette(palette)

    def set_dark_theme(self):
        """Imposta il tema scuro"""
        app = QApplication.instance()
        app.setStyle("Fusion")
        
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        
        app.setPalette(palette)

    def reset_theme(self):
        """Reimposta il tema di sistema"""
        app = QApplication.instance()
        app.setStyle("Fusion")
        app.setPalette(app.style().standardPalette())

    def closeEvent(self, event):
        """Metodo chiamato quando la finestra viene chiusa"""
        self.save_settings()
        event.accept()