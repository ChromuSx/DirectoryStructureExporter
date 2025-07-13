from PyQt6.QtWidgets import (QMainWindow, QTabWidget, QVBoxLayout, QHBoxLayout, 
                           QWidget, QLabel, QComboBox, QPushButton, QStatusBar, 
                           QApplication, QMessageBox)
from PyQt6.QtCore import QSettings, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QIcon, QPalette

from ui.export_tab import ExportTab
from ui.config_tab import ConfigTab
from ui.filters_tab import FiltersTab
from utils.resources import resource_manager
from utils.translation_manager import translation_manager, tr

class MainWindow(QMainWindow):
    # Segnale emesso quando cambia la lingua
    language_changed = pyqtSignal(str)
    
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
        
        # Connetti il segnale di cambio lingua
        self.language_changed.connect(self.on_language_changed)
    
    def initUI(self):
        """Inizializza l'interfaccia utente"""
        self.setWindowTitle(tr("Directory Structure Exporter"))
        self.resize(900, 600)

        # Imposta l'icona della finestra
        icon = resource_manager.get_logo_icon()
        if not icon.isNull():
            self.setWindowIcon(icon)
            QApplication.instance().setWindowIcon(icon)
        
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage(tr("Pronto"))

        # Widget centrale
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # Barra degli strumenti
        toolbar_layout = QHBoxLayout()
        
        # Selettore tema
        self.theme_label = QLabel(tr("Tema:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems([tr("Sistema"), tr("Chiaro"), tr("Scuro")])
        self.theme_combo.currentIndexChanged.connect(self.change_theme)
        
        # Selettore lingua
        self.language_label = QLabel(tr("Lingua:"))
        self.language_combo = QComboBox()
        self.populate_language_combo()
        self.language_combo.currentIndexChanged.connect(self.change_language)
        
        toolbar_layout.addWidget(self.theme_label)
        toolbar_layout.addWidget(self.theme_combo)
        toolbar_layout.addSpacing(20)
        toolbar_layout.addWidget(self.language_label)
        toolbar_layout.addWidget(self.language_combo)
        toolbar_layout.addStretch(1)
        
        main_layout.addLayout(toolbar_layout)
        
        # Schede
        self.tabs = QTabWidget()
        self.export_tab = ExportTab(self.exporter, self.filter_manager, self.settings)
        self.config_tab = ConfigTab(self.filter_manager, self.config_manager, self.settings)
        self.filters_tab = FiltersTab(self.filter_manager, self.settings)
        
        self.update_tab_titles()
        
        main_layout.addWidget(self.tabs)
        self.setCentralWidget(central_widget)
        
        # Collegamenti tra le schede
        self.export_tab.config_tab = self.config_tab
        self.export_tab.filters_tab = self.filters_tab
        self.config_tab.export_tab = self.export_tab
        self.config_tab.filters_tab = self.filters_tab
        self.filters_tab.config_tab = self.config_tab
        self.filters_tab.export_tab = self.export_tab
        
        # Connetti le schede al segnale di cambio lingua
        if hasattr(self.export_tab, 'language_changed'):
            self.language_changed.connect(self.export_tab.retranslate_ui)
        if hasattr(self.config_tab, 'language_changed'):
            self.language_changed.connect(self.config_tab.retranslate_ui)
        if hasattr(self.filters_tab, 'language_changed'):
            self.language_changed.connect(self.filters_tab.retranslate_ui)
    
    def populate_language_combo(self):
        """Popola il combo box delle lingue"""
        self.language_combo.clear()
        
        current_lang = translation_manager.get_current_language()
        current_index = 0
        
        for i, (code, name) in enumerate(translation_manager.get_available_languages().items()):
            self.language_combo.addItem(name, code)
            if code == current_lang:
                current_index = i
        
        self.language_combo.setCurrentIndex(current_index)
    
    def update_tab_titles(self):
        """Aggiorna i titoli delle schede"""
        self.tabs.clear()
        self.tabs.addTab(self.export_tab, tr("Esportazione"))
        self.tabs.addTab(self.filters_tab, tr("Filtri"))
        self.tabs.addTab(self.config_tab, tr("Configurazione"))
    
    def change_language(self):
        """Cambia la lingua dell'applicazione"""
        if self.language_combo.currentIndex() < 0:
            return
            
        language_code = self.language_combo.currentData()
        if language_code and language_code != translation_manager.get_current_language():
            success = translation_manager.change_language(language_code)
            
            if success:
                # Aggiorna l'interfaccia
                self.retranslate_ui()
                
                # Emetti il segnale di cambio lingua
                self.language_changed.emit(language_code)
                
                # Mostra messaggio di conferma
                QMessageBox.information(
                    self, 
                    tr("Lingua cambiata"), 
                    tr("La lingua è stata cambiata. Alcune modifiche potrebbero richiedere il riavvio dell'applicazione.")
                )
            else:
                QMessageBox.warning(
                    self, 
                    tr("Errore"), 
                    tr("Errore nel caricamento della lingua selezionata.")
                )
    
    def retranslate_ui(self):
        """Ricarica tutte le traduzioni dell'interfaccia"""
        # Aggiorna il titolo della finestra
        self.setWindowTitle(tr("Directory Structure Exporter"))
        
        # Aggiorna la status bar
        self.statusBar.showMessage(tr("Pronto"))
        
        # Aggiorna le etichette della toolbar
        self.theme_label.setText(tr("Tema:"))
        self.language_label.setText(tr("Lingua:"))
        
        # Aggiorna il combo del tema
        current_theme = self.theme_combo.currentIndex()
        self.theme_combo.clear()
        self.theme_combo.addItems([tr("Sistema"), tr("Chiaro"), tr("Scuro")])
        self.theme_combo.setCurrentIndex(current_theme)
        
        # Aggiorna i titoli delle schede
        self.update_tab_titles()
        
        # Ricarica il combo delle lingue per aggiornare l'etichetta
        current_lang = translation_manager.get_current_language()
        self.populate_language_combo()
        
        # Ripristina la selezione corretta
        for i in range(self.language_combo.count()):
            if self.language_combo.itemData(i) == current_lang:
                self.language_combo.setCurrentIndex(i)
                break
    
    def on_language_changed(self, language_code):
        """Gestisce il cambio di lingua"""
        # Aggiorna lo status bar
        self.statusBar.showMessage(tr("Lingua cambiata in") + f" {translation_manager.get_current_language_name()}", 3000)
        
        # Qui puoi aggiungere altri aggiornamenti necessari
        pass
        
    def load_settings(self):
        """Carica le impostazioni dell'interfaccia utente"""
        # Carica il tema
        theme_text = self.settings.value("theme", tr("Sistema"))
        theme_items = [tr("Sistema"), tr("Chiaro"), tr("Scuro")]
        
        for i, item in enumerate(theme_items):
            if item == theme_text:
                self.theme_combo.setCurrentIndex(i)
                break
        
        self.change_theme()
        
        # La lingua viene caricata automaticamente dal TranslationManager
        self.populate_language_combo()
    
    def save_settings(self):
        """Salva le impostazioni utente"""
        # Salva il tema
        self.settings.setValue("theme", self.theme_combo.currentText())

        # Salva la configurazione dei preset
        self.config_manager.save_presets()
        
        # Invoca il salvataggio delle impostazioni per ogni scheda
        self.export_tab.save_settings()
        self.config_tab.save_settings()
        self.filters_tab.save_settings()

    def change_theme(self):
        """Cambia il tema dell'applicazione"""
        theme = self.theme_combo.currentText()
        
        if theme == tr("Chiaro"):
            self.set_light_theme()
        elif theme == tr("Scuro"):
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