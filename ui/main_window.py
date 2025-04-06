from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                          QLabel, QPushButton, QLineEdit, QFileDialog, 
                          QTextEdit, QGroupBox, QCheckBox, QListWidget, 
                          QTabWidget, QInputDialog, QSpinBox, QComboBox,
                          QMessageBox, QDateTimeEdit, QGridLayout)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QMenu, QStyle
from PyQt6.QtGui import QColor, QDesktopServices
from PyQt6.QtCore import Qt, QSettings, QDateTime
from pathlib import Path
import re

class MainWindow(QMainWindow):
    def __init__(self, exporter):
        super().__init__()
        self.exporter = exporter
        self.settings = QSettings("DirectoryExporter", "Settings")
        self.setup_ui()
        self.setup_tree_context_menu()  # Aggiungi questa riga
        self.load_settings()
        
    def setup_ui(self):
        self.size_multiplier = 1

        # Configurazione della finestra principale
        self.setWindowTitle("Directory Structure Exporter")
        self.setMinimumSize(800, 600)
        
        # Widget centrale
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principale
        main_layout = QVBoxLayout(central_widget)
        
        # Widget con schede
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # ----- SCHEDA PRINCIPALE (ESPORTAZIONE) -----
        main_tab = QWidget()
        main_tab_layout = QVBoxLayout(main_tab)
        
        # Gruppo per la selezione della directory
        dir_group = QGroupBox("Selezione Directory")
        dir_layout = QHBoxLayout()
        
        self.dir_path = QLineEdit()
        browse_dir_btn = QPushButton("Sfoglia...")
        browse_dir_btn.clicked.connect(self.browse_directory)
        
        dir_layout.addWidget(QLabel("Directory:"))
        dir_layout.addWidget(self.dir_path, 1)
        dir_layout.addWidget(browse_dir_btn)
        dir_group.setLayout(dir_layout)
        
        # Gruppo per il file di output
        output_group = QGroupBox("File di Output")
        output_layout = QHBoxLayout()
        
        self.output_path = QLineEdit()
        browse_output_btn = QPushButton("Sfoglia...")
        browse_output_btn.clicked.connect(self.browse_output)
        
        output_layout.addWidget(QLabel("File:"))
        output_layout.addWidget(self.output_path, 1)
        output_layout.addWidget(browse_output_btn)
        output_group.setLayout(output_layout)
        
        # Selezione formato
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Formato:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["TXT", "HTML", "JSON", "XML"])
        format_layout.addWidget(self.format_combo)
        format_layout.addStretch(1)
        
        # Opzioni di esportazione
        options_group = QGroupBox("Opzioni di esportazione")
        options_layout = QVBoxLayout()
        
        # Opzione per includere/escludere file
        self.include_files_check = QCheckBox("Includi file")
        self.include_files_check.stateChanged.connect(self.reload_tree_structure)
        self.include_files_check.stateChanged.connect(self.sync_tree_with_export_options)
        self.include_files_check.setChecked(True)
        options_layout.addWidget(self.include_files_check)
        
        # Opzione per la profondità massima
        depth_layout = QHBoxLayout()
        depth_layout.addWidget(QLabel("Profondità massima:"))
        self.depth_spin = QSpinBox()
        self.depth_spin.valueChanged.connect(self.reload_tree_structure)
        self.depth_spin.setMinimum(0)
        self.depth_spin.setMaximum(999)
        self.depth_spin.setValue(0)
        self.depth_spin.setSpecialValueText("Illimitata")
        depth_layout.addWidget(self.depth_spin)
        options_layout.addLayout(depth_layout)
        
        options_group.setLayout(options_layout)
        
        # Pulsanti di azione
        action_layout = QHBoxLayout()
        export_btn = QPushButton("Esporta")
        export_btn.clicked.connect(self.export_structure)
        
        action_layout.addWidget(export_btn)
        
        # Area vista struttura (sostituiamo l'anteprima testuale con la vista ad albero)
        tree_group = QGroupBox("Struttura Directory")
        tree_layout = QVBoxLayout()
        
        # Controlli per la vista ad albero
        tree_controls = QHBoxLayout()
        
        # Checkbox per mostrare file e applicare filtri
        self.show_files_check = QCheckBox("Mostra file")
        self.show_files_check.setChecked(True)
        self.show_files_check.stateChanged.connect(self.reload_tree_structure)
        
        self.apply_filters_check = QCheckBox("Applica filtri")
        self.apply_filters_check.setChecked(True)
        self.apply_filters_check.stateChanged.connect(self.reload_tree_structure)
        
        # Barra di ricerca
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Cerca:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cerca file o cartelle...")
        self.search_input.textChanged.connect(self.filter_tree_items)
        
        # Aggiungiamo i controlli al layout
        tree_controls.addWidget(self.show_files_check)
        tree_controls.addWidget(self.apply_filters_check)
        tree_controls.addStretch(1)
        tree_controls.addWidget(QLabel("Cerca:"))
        tree_controls.addWidget(self.search_input)
        
        # Widget albero
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["Nome", "Tipo", "Percorso"])
        self.tree_widget.setColumnWidth(0, 300)
        self.tree_widget.setAlternatingRowColors(True)
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["Nome", "Tipo", "Percorso"])
        self.tree_widget.setColumnWidth(0, 300)
        self.tree_widget.setAlternatingRowColors(True)
        self.tree_widget.itemExpanded.connect(self.on_item_expanded)
        
        # Componiamo il layout della vista ad albero
        tree_layout.addLayout(tree_controls)
        tree_layout.addWidget(self.tree_widget)
        tree_group.setLayout(tree_layout)
        
        # Aggiungi tutto al layout della scheda principale
        main_tab_layout.addWidget(dir_group)
        main_tab_layout.addWidget(output_group)
        main_tab_layout.addLayout(format_layout)
        main_tab_layout.addWidget(options_group)
        main_tab_layout.addLayout(action_layout)
        main_tab_layout.addWidget(tree_group, 1)  # Diamo peso 1 per far espandere la vista
        
        # ----- SCHEDA CONFIGURAZIONE -----
        config_tab = QWidget()
        config_layout = QVBoxLayout(config_tab)
        
        # Sezione directory escluse
        excluded_dirs_group = QGroupBox("Directory escluse")
        excluded_layout = QVBoxLayout()
        self.excluded_dirs_list = QListWidget()
        
        # Popola la lista con i valori attuali
        for dir_name in self.exporter.excluded_dirs:
            self.excluded_dirs_list.addItem(dir_name)
        
        excluded_buttons_layout = QHBoxLayout()
        add_excluded_btn = QPushButton("Aggiungi")
        add_excluded_regex_btn = QPushButton("Aggiungi Regex")
        remove_excluded_btn = QPushButton("Rimuovi")
        
        add_excluded_btn.clicked.connect(self.add_excluded_dir)
        add_excluded_regex_btn.clicked.connect(self.add_excluded_dir_regex)
        remove_excluded_btn.clicked.connect(self.remove_excluded_dir)
        
        excluded_buttons_layout.addWidget(add_excluded_btn)
        excluded_buttons_layout.addWidget(add_excluded_regex_btn)
        excluded_buttons_layout.addWidget(remove_excluded_btn)
        
        excluded_layout.addWidget(self.excluded_dirs_list)
        excluded_layout.addLayout(excluded_buttons_layout)
        excluded_dirs_group.setLayout(excluded_layout)
        
        # Sezione estensioni incluse
        included_exts_group = QGroupBox("Estensioni incluse")
        included_layout = QVBoxLayout()
        self.included_exts_list = QListWidget()
        
        # Popola la lista con i valori attuali
        for ext in self.exporter.included_file_extensions:
            self.included_exts_list.addItem(ext)
        
        included_buttons_layout = QHBoxLayout()
        add_included_btn = QPushButton("Aggiungi")
        add_included_regex_btn = QPushButton("Aggiungi Regex") 
        remove_included_btn = QPushButton("Rimuovi")
        
        add_included_btn.clicked.connect(self.add_included_ext)
        add_included_regex_btn.clicked.connect(self.add_included_ext_regex)
        remove_included_btn.clicked.connect(self.remove_included_ext)
        
        included_buttons_layout.addWidget(add_included_btn)
        included_buttons_layout.addWidget(add_included_regex_btn)
        included_buttons_layout.addWidget(remove_included_btn)
        
        included_layout.addWidget(self.included_exts_list)
        included_layout.addLayout(included_buttons_layout)
        included_exts_group.setLayout(included_layout)
        
        # Pulsanti per salvare/caricare configurazione
        config_buttons_layout = QHBoxLayout()
        save_config_btn = QPushButton("Salva configurazione")
        load_config_btn = QPushButton("Carica configurazione")
        
        save_config_btn.clicked.connect(self.save_config)
        load_config_btn.clicked.connect(self.load_config)
        
        config_buttons_layout.addWidget(save_config_btn)
        config_buttons_layout.addWidget(load_config_btn)
        
        # Aggiunta al layout della scheda configurazione
        config_layout.addWidget(excluded_dirs_group)
        config_layout.addWidget(included_exts_group)
        config_layout.addLayout(config_buttons_layout)
        
        # Aggiunta delle schede
        self.tab_widget.addTab(main_tab, "Esportazione")
        self.tab_widget.addTab(config_tab, "Configurazione")
        
        # ----- BARRA DI STATO E SELETTORE DI TEMA -----
        self.statusBar = self.statusBar()
        theme_label = QLabel("Tema:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Sistema", "Chiaro", "Scuro"])
        self.theme_combo.currentIndexChanged.connect(self.change_theme)
        
        self.statusBar.addPermanentWidget(theme_label)
        self.statusBar.addPermanentWidget(self.theme_combo)

        regex_help_btn = QPushButton("?")
        regex_help_btn.setFixedSize(25, 25)
        regex_help_btn.clicked.connect(self.show_regex_help)
        excluded_buttons_layout.addWidget(regex_help_btn)

        regex_help_btn_ext = QPushButton("?")
        regex_help_btn_ext.setFixedSize(25, 25)
        regex_help_btn_ext.clicked.connect(self.show_regex_help)
        included_buttons_layout.addWidget(regex_help_btn_ext)

        # Nuova scheda per i filtri avanzati
        advanced_filters_tab = QWidget()
        advanced_filters_layout = QVBoxLayout(advanced_filters_tab)

        # Gruppo per filtri dimensione file
        size_filters_group = QGroupBox("Filtri per dimensione")
        size_layout = QGridLayout()

        # Dimensione minima
        size_layout.addWidget(QLabel("Dimensione minima:"), 0, 0)
        self.min_size_spin = QSpinBox()
        self.min_size_spin.setRange(0, 1000000000)
        self.min_size_spin.setSuffix(" bytes")
        size_layout.addWidget(self.min_size_spin, 0, 1)

        # Dimensione massima
        size_layout.addWidget(QLabel("Dimensione massima:"), 1, 0)
        self.max_size_spin = QSpinBox()
        self.max_size_spin.setRange(0, 1000000000)
        self.max_size_spin.setSpecialValueText("Illimitata")
        self.max_size_spin.setSuffix(" bytes")
        size_layout.addWidget(self.max_size_spin, 1, 1)

        # Selezione unità di misura
        size_layout.addWidget(QLabel("Unità:"), 2, 0)
        self.size_unit_combo = QComboBox()
        self.size_unit_combo.addItems(["Bytes", "KB", "MB", "GB"])
        self.size_unit_combo.currentIndexChanged.connect(self.update_size_units)
        size_layout.addWidget(self.size_unit_combo, 2, 1)

        size_filters_group.setLayout(size_layout)

        # Gruppo per filtri data
        date_filters_group = QGroupBox("Filtri per data")
        date_layout = QGridLayout()

        # Data creazione
        date_layout.addWidget(QLabel("Data creazione da:"), 0, 0)
        self.min_creation_date = QDateTimeEdit()
        self.min_creation_date.setCalendarPopup(True)
        self.min_creation_date.setDateTime(QDateTime.currentDateTime().addYears(-1))
        date_layout.addWidget(self.min_creation_date, 0, 1)

        date_layout.addWidget(QLabel("a:"), 0, 2)
        self.max_creation_date = QDateTimeEdit()
        self.max_creation_date.setCalendarPopup(True)
        self.max_creation_date.setDateTime(QDateTime.currentDateTime())
        date_layout.addWidget(self.max_creation_date, 0, 3)

        # Checkbox per abilitare il filtro data creazione
        self.enable_creation_date = QCheckBox("Abilita filtro")
        date_layout.addWidget(self.enable_creation_date, 0, 4)

        # Data modifica
        date_layout.addWidget(QLabel("Data modifica da:"), 1, 0)
        self.min_modification_date = QDateTimeEdit()
        self.min_modification_date.setCalendarPopup(True)
        self.min_modification_date.setDateTime(QDateTime.currentDateTime().addYears(-1))
        date_layout.addWidget(self.min_modification_date, 1, 1)

        date_layout.addWidget(QLabel("a:"), 1, 2)
        self.max_modification_date = QDateTimeEdit()
        self.max_modification_date.setCalendarPopup(True)
        self.max_modification_date.setDateTime(QDateTime.currentDateTime())
        date_layout.addWidget(self.max_modification_date, 1, 3)

        # Checkbox per abilitare il filtro data modifica
        self.enable_modification_date = QCheckBox("Abilita filtro")
        date_layout.addWidget(self.enable_modification_date, 1, 4)

        date_filters_group.setLayout(date_layout)

        # Gruppo per presets
        presets_group = QGroupBox("Configurazioni predefinite")
        presets_layout = QVBoxLayout()

        # Lista e gestione dei preset
        presets_list_layout = QHBoxLayout()
        self.presets_combo = QComboBox()
        load_preset_btn = QPushButton("Carica")
        load_preset_btn.clicked.connect(self.load_filter_preset)
        presets_list_layout.addWidget(self.presets_combo, 1)
        presets_list_layout.addWidget(load_preset_btn)

        # Pulsanti per la gestione dei preset
        presets_actions_layout = QHBoxLayout()
        save_preset_btn = QPushButton("Salva configurazione attuale")
        save_preset_btn.clicked.connect(self.save_filter_preset)
        delete_preset_btn = QPushButton("Elimina")
        delete_preset_btn.clicked.connect(self.delete_filter_preset)
        presets_actions_layout.addWidget(save_preset_btn)
        presets_actions_layout.addWidget(delete_preset_btn)

        presets_layout.addLayout(presets_list_layout)
        presets_layout.addLayout(presets_actions_layout)
        presets_group.setLayout(presets_layout)

        # Aggiunta dei gruppi al layout della scheda
        advanced_filters_layout.addWidget(size_filters_group)
        advanced_filters_layout.addWidget(date_filters_group)
        advanced_filters_layout.addWidget(presets_group)
        advanced_filters_layout.addStretch(1)

        # Aggiunta della scheda al widget tab
        self.tab_widget.addTab(advanced_filters_tab, "Filtri Avanzati")
        
    # ----- METODI PER LA GESTIONE DEI PERCORSI -----

    def update_size_units(self):
        """Aggiorna l'unità di misura per i filtri dimensione file"""
        unit = self.size_unit_combo.currentText()
        multiplier = 1
        
        if unit == "KB":
            multiplier = 1024
        elif unit == "MB":
            multiplier = 1024 * 1024
        elif unit == "GB":
            multiplier = 1024 * 1024 * 1024
        
        # Aggiorna i suffissi
        self.min_size_spin.setSuffix(f" {unit}")
        self.max_size_spin.setSuffix(f" {unit}")
        
        # Memorizza il moltiplicatore per la conversione
        self.size_multiplier = multiplier

    def save_filter_preset(self):
        """Salva la configurazione attuale come preset"""
        preset_name, ok = QInputDialog.getText(
            self, "Salva configurazione", "Nome della configurazione:"
        )
        
        if ok and preset_name:
            # Applica i filtri correnti all'esportatore
            self.apply_filters_to_exporter()
            
            # Salva come preset
            success, message = self.exporter.save_filter_preset(preset_name)
            
            # Aggiorna la combobox
            self.update_presets_combobox()
            
            self.statusBar.showMessage(message, 3000)

    def update_presets_combobox(self):
        """Aggiorna la lista dei preset nella combobox"""
        self.presets_combo.clear()
        preset_names = self.exporter.get_filter_preset_names()
        self.presets_combo.addItems(preset_names)

    def update_ui_from_exporter(self):
        """Aggiorna l'interfaccia con i valori attuali dell'esportatore"""
        # Filtri dimensione
        # Determina l'unità più appropriata
        max_size = self.exporter.max_file_size if self.exporter.max_file_size != float('inf') else 0
        min_size = self.exporter.min_file_size
        
        # Scegli l'unità più appropriata
        if max(min_size, max_size) > 1024*1024*1024:
            unit_index = 3  # GB
            divisor = 1024*1024*1024
        elif max(min_size, max_size) > 1024*1024:
            unit_index = 2  # MB
            divisor = 1024*1024
        elif max(min_size, max_size) > 1024:
            unit_index = 1  # KB
            divisor = 1024
        else:
            unit_index = 0  # Bytes
            divisor = 1
        
        self.size_unit_combo.setCurrentIndex(unit_index)
        self.min_size_spin.setValue(min_size // divisor)
        self.max_size_spin.setValue(max_size // divisor if max_size != float('inf') else 0)
        
        # Filtri data
        if self.exporter.min_creation_date:
            self.enable_creation_date.setChecked(True)
            dt = QDateTime()
            dt.setSecsSinceEpoch(self.exporter.min_creation_date)
            self.min_creation_date.setDateTime(dt)
            
            dt = QDateTime()
            dt.setSecsSinceEpoch(self.exporter.max_creation_date)
            self.max_creation_date.setDateTime(dt)
        else:
            self.enable_creation_date.setChecked(False)
        
        if self.exporter.min_modification_date:
            self.enable_modification_date.setChecked(True)
            dt = QDateTime()
            dt.setSecsSinceEpoch(self.exporter.min_modification_date)
            self.min_modification_date.setDateTime(dt)
            
            dt = QDateTime()
            dt.setSecsSinceEpoch(self.exporter.max_modification_date)
            self.max_modification_date.setDateTime(dt)
        else:
            self.enable_modification_date.setChecked(False)

    def load_filter_preset(self):
        """Carica un preset selezionato"""
        preset_name = self.presets_combo.currentText()
        if not preset_name:
            return
        
        success, message = self.exporter.load_filter_preset(preset_name)
        
        if success:
            # Aggiorna l'interfaccia con i valori caricati
            self.update_ui_from_exporter()
            self.statusBar.showMessage(message, 3000)
        else:
            QMessageBox.warning(self, "Errore", message)

    def delete_filter_preset(self):
        """Elimina un preset selezionato"""
        preset_name = self.presets_combo.currentText()
        if not preset_name:
            return
        
        reply = QMessageBox.question(
            self, 
            "Conferma eliminazione", 
            f"Sei sicuro di voler eliminare la configurazione '{preset_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success, message = self.exporter.delete_filter_preset(preset_name)
            if success:
                # Aggiorna la combobox
                self.update_presets_combobox()
                self.statusBar.showMessage(message, 3000)
            else:
                QMessageBox.warning(self, "Errore", message)

    def apply_filters_to_exporter(self):
        """Applica i filtri impostati all'oggetto esportatore"""
        # Filtri di dimensione
        multiplier = self.size_multiplier
        self.exporter.min_file_size = self.min_size_spin.value() * multiplier
        
        if self.max_size_spin.value() == 0:  # Valore speciale per "Illimitata"
            self.exporter.max_file_size = float('inf')
        else:
            self.exporter.max_file_size = self.max_size_spin.value() * multiplier
        
        # Filtri di data
        if self.enable_creation_date.isChecked():
            self.exporter.min_creation_date = self.min_creation_date.dateTime().toSecsSinceEpoch()
            self.exporter.max_creation_date = self.max_creation_date.dateTime().toSecsSinceEpoch()
        else:
            self.exporter.min_creation_date = None
            self.exporter.max_creation_date = None
        
        if self.enable_modification_date.isChecked():
            self.exporter.min_modification_date = self.min_modification_date.dateTime().toSecsSinceEpoch()
            self.exporter.max_modification_date = self.max_modification_date.dateTime().toSecsSinceEpoch()
        else:
            self.exporter.min_modification_date = None
            self.exporter.max_modification_date = None

    def show_regex_help(self):
        help_text = """
        <h3>Guida alle Espressioni Regolari</h3>
        <p>Esempi di pattern comuni:</p>
        <ul>
            <li><b>^temp</b> - Corrisponde a nomi che iniziano con "temp"</li>
            <li><b>backup$</b> - Corrisponde a nomi che finiscono con "backup"</li>
            <li><b>^data_\\d+$</b> - Corrisponde a nomi come "data_123", "data_45", ecc.</li>
            <li><b>.*log.*</b> - Corrisponde a qualsiasi nome che contiene "log"</li>
        </ul>
        """
        QMessageBox.information(self, "Aiuto Espressioni Regolari", help_text)

    def add_excluded_dir_regex(self):
        pattern, ok = QInputDialog.getText(
            self, 
            "Aggiungi pattern regex", 
            "Inserisci un'espressione regolare per escludere le directory:"
        )
        if ok and pattern:
            try:
                # Testiamo se è una regex valida
                re.compile(pattern)
                # Aggiungiamo alla lista visuale con indicatore [regex]
                self.excluded_dirs_list.addItem(f"[regex] {pattern}")
                # Aggiungiamo al set nell'esportatore
                self.exporter.excluded_dirs_regex.add(pattern)
            except re.error:
                QMessageBox.warning(
                    self, 
                    "Espressione non valida", 
                    "L'espressione regolare inserita non è valida."
                )

    def add_included_ext_regex(self):
        pattern, ok = QInputDialog.getText(
            self, 
            "Aggiungi pattern regex", 
            "Inserisci un'espressione regolare per includere i file:"
        )
        if ok and pattern:
            try:
                # Testiamo se è una regex valida
                re.compile(pattern)
                # Aggiungiamo alla lista visuale con indicatore [regex]
                self.included_exts_list.addItem(f"[regex] {pattern}")
                # Aggiungiamo al set nell'esportatore
                self.exporter.included_file_regex.add(pattern)
            except re.error:
                QMessageBox.warning(
                    self, 
                    "Espressione non valida", 
                    "L'espressione regolare inserita non è valida."
                )
    
    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Seleziona Directory")
        if directory:
            self.dir_path.setText(directory)
            # Carichiamo automaticamente l'albero
            self.load_tree_structure()
        
    def sync_tree_with_export_options(self):
        """Sincronizza le opzioni della vista albero con quelle di esportazione"""
        # Verifica se l'attributo show_files_check esiste
        if hasattr(self, 'show_files_check'):
            # Sincronizziamo il checkbox dei file
            self.show_files_check.setChecked(self.include_files_check.isChecked())
            
            # Aggiorniamo l'albero
            self.reload_tree_structure()
    
    def browse_output(self):
        selected_format = self.format_combo.currentText()
        extension = ".txt"
        
        if selected_format == "HTML":
            extension = ".html"
        elif selected_format == "JSON":
            extension = ".json"
        elif selected_format == "XML":
            extension = ".xml"
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Salva File", "", f"File {selected_format} (*{extension})"
        )
        
        if file_path:
            # Assicuriamoci che abbia l'estensione corretta
            if not file_path.lower().endswith(extension.lower()):
                file_path += extension
            self.output_path.setText(file_path)
    
    # ----- METODI PER LA GESTIONE DELL'ESPORTAZIONE -----
    
    def export_structure(self):

        self.apply_filters_to_exporter()

        directory = self.dir_path.text()
        output_file = self.output_path.text()
        
        if not directory or not output_file:
            QMessageBox.warning(self, "Errore", "Seleziona directory e file di output.")
            return
        
        include_files = self.include_files_check.isChecked()
        max_depth = None if self.depth_spin.value() == 0 else self.depth_spin.value()
        
        # Prepariamo il percorso di output con l'estensione corretta
        selected_format = self.format_combo.currentText()
        output_path = Path(output_file)
        
        # Assicuriamoci che il file abbia l'estensione corretta
        if selected_format == "TXT" and output_path.suffix.lower() != ".txt":
            output_file = str(output_path.with_suffix(".txt"))
        elif selected_format == "HTML" and output_path.suffix.lower() != ".html":
            output_file = str(output_path.with_suffix(".html"))
        elif selected_format == "JSON" and output_path.suffix.lower() != ".json":
            output_file = str(output_path.with_suffix(".json"))
        elif selected_format == "XML" and output_path.suffix.lower() != ".xml":
            output_file = str(output_path.with_suffix(".xml"))
        
        # Esportiamo nel formato selezionato
        try:
            if selected_format == "TXT":
                success, message = self.exporter.export_structure(
                    directory, output_file, include_files, max_depth
                )
            elif selected_format == "HTML":
                success, message = self.exporter.export_structure_html(
                    directory, output_file, include_files, max_depth
                )
            elif selected_format == "JSON":
                success, message = self.exporter.export_structure_json(
                    directory, output_file, include_files, max_depth
                )
            elif selected_format == "XML":
                success, message = self.exporter.export_structure_xml(
                    directory, output_file, include_files, max_depth
                )
            
            # Aggiorniamo il campo con il nuovo nome file se è stato modificato
            self.output_path.setText(output_file)
            
            # Mostriamo un messaggio di successo
            if success:
                QMessageBox.information(self, "Esportazione completata", message)
                # Mostriamo anche nella barra di stato
                self.statusBar.showMessage(message, 5000)  # Mostra per 5 secondi
            else:
                QMessageBox.warning(self, "Errore durante l'esportazione", message)
                
        except Exception as e:
            error_message = f"Errore durante l'esportazione: {e}"
            QMessageBox.critical(self, "Errore", error_message)
    
    # ----- METODI PER LA GESTIONE DELLA CONFIGURAZIONE -----
    
    def add_excluded_dir(self):
        dir_name, ok = QInputDialog.getText(self, "Aggiungi directory", "Nome directory:")
        if ok and dir_name:
            self.excluded_dirs_list.addItem(dir_name)
            self.exporter.excluded_dirs.add(dir_name)
    
    def remove_excluded_dir(self):
        selected_items = self.excluded_dirs_list.selectedItems()
        if selected_items:
            for item in selected_items:
                dir_name = item.text()
                self.excluded_dirs_list.takeItem(self.excluded_dirs_list.row(item))
                
                # Determiniamo se è un pattern regex o una stringa semplice
                if dir_name.startswith("[regex] "):
                    pattern = dir_name[8:]  # Rimuovi il prefisso "[regex] "
                    self.exporter.excluded_dirs_regex.remove(pattern)
                else:
                    self.exporter.excluded_dirs.remove(dir_name)
    
    def add_included_ext(self):
        ext, ok = QInputDialog.getText(self, "Aggiungi estensione", "Estensione (con punto iniziale, es. .py):")
        if ok and ext:
            if not ext.startswith('.'):
                ext = f".{ext}"
            self.included_exts_list.addItem(ext)
            self.exporter.included_file_extensions.add(ext)
    
    def remove_included_ext(self):
        selected_items = self.included_exts_list.selectedItems()
        if selected_items:
            for item in selected_items:
                ext = item.text()
                self.included_exts_list.takeItem(self.included_exts_list.row(item))
                
                # Determiniamo se è un pattern regex o una stringa semplice
                if ext.startswith("[regex] "):
                    pattern = ext[8:]  # Rimuovi il prefisso "[regex] "
                    self.exporter.included_file_regex.remove(pattern)
                else:
                    self.exporter.included_file_extensions.remove(ext)
    
    # Nel file exporter.py
    def save_config(self):
        """Salva la configurazione corrente in un file JSON"""
        config_file, _ = QFileDialog.getSaveFileName(
            self, "Salva Configurazione", "", "File JSON (*.json)"
        )
        
        if not config_file:
            return
            
        # Usa l'oggetto exporter per salvare la configurazione
        success, message = self.exporter.save_config(config_file)
        
        if success:
            self.statusBar.showMessage(message, 3000)
        else:
            QMessageBox.warning(self, "Errore", message)

    def load_config(self):
        """Carica la configurazione da un file JSON"""
        config_file, _ = QFileDialog.getOpenFileName(
            self, "Carica Configurazione", "", "File JSON (*.json)"
        )
        
        if not config_file:
            return
            
        # Usa l'oggetto exporter per caricare la configurazione
        success, message = self.exporter.load_config(config_file)
        
        if success:
            # Aggiorna le liste UI dopo aver caricato la configurazione
            self.update_config_lists()
            self.statusBar.showMessage(message, 3000)
        else:
            QMessageBox.warning(self, "Errore", message)
        
    def update_config_lists(self):
        # Aggiorniamo la lista delle directory escluse
        self.excluded_dirs_list.clear()
        for dir_name in self.exporter.excluded_dirs:
            self.excluded_dirs_list.addItem(dir_name)
        for pattern in self.exporter.excluded_dirs_regex:
            self.excluded_dirs_list.addItem(f"[regex] {pattern}")
        
        # Aggiorniamo la lista delle estensioni incluse
        self.included_exts_list.clear()
        for ext in self.exporter.included_file_extensions:
            self.included_exts_list.addItem(ext)
        for pattern in self.exporter.included_file_regex:
            self.included_exts_list.addItem(f"[regex] {pattern}")
        
        self.reload_tree_structure()
    # ----- METODI PER LA GESTIONE DEL TEMA -----
    
    def change_theme(self):
        theme = self.theme_combo.currentText()
        
        if theme == "Chiaro":
            self.set_light_theme()
        elif theme == "Scuro":
            self.set_dark_theme()
        else:  # Sistema
            self.reset_theme()
    
    def set_light_theme(self):
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
        app = QApplication.instance()
        app.setStyle("Fusion")
        app.setPalette(app.style().standardPalette())
    
    # ----- METODI PER LA GESTIONE DELLE IMPOSTAZIONI -----
    
    def closeEvent(self, event):
        """Metodo chiamato quando la finestra viene chiusa"""
        self.save_settings()
        event.accept()
    
    def save_settings(self):
        """Salva le impostazioni utente"""
        # Salva i percorsi
        self.settings.setValue("dir_path", self.dir_path.text())
        self.settings.setValue("output_path", self.output_path.text())
        
        # Salva le impostazioni di esportazione
        self.settings.setValue("format", self.format_combo.currentText())
        self.settings.setValue("include_files", self.include_files_check.isChecked())
        self.settings.setValue("max_depth", self.depth_spin.value())
        
        # Salva il tema
        self.settings.setValue("theme", self.theme_combo.currentText())
        
        # Salva la configurazione di directory escluse ed estensioni incluse
        self.settings.setValue("excluded_dirs", list(self.exporter.excluded_dirs))
        self.settings.setValue("excluded_dirs_regex", list(self.exporter.excluded_dirs_regex))
        self.settings.setValue("included_extensions", list(self.exporter.included_file_extensions))
        self.settings.setValue("included_file_regex", list(self.exporter.included_file_regex))
    
    def load_settings(self):
        """Carica le impostazioni utente"""
        # Carica i percorsi
        self.dir_path.setText(self.settings.value("dir_path", ""))
        self.output_path.setText(self.settings.value("output_path", ""))
        
        # Carica le impostazioni di esportazione
        format_text = self.settings.value("format", "TXT")
        index = self.format_combo.findText(format_text)
        if index >= 0:
            self.format_combo.setCurrentIndex(index)
            
        self.include_files_check.setChecked(self.settings.value("include_files", True, type=bool))
        self.depth_spin.setValue(self.settings.value("max_depth", 0, type=int))
        
        # Carica il tema
        theme_text = self.settings.value("theme", "Sistema")
        index = self.theme_combo.findText(theme_text)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
            self.change_theme()
            
        # Carica la configurazione di directory escluse ed estensioni incluse
        excluded_dirs = self.settings.value("excluded_dirs", None)
        if excluded_dirs:
            self.exporter.excluded_dirs = set(excluded_dirs)
            
        excluded_dirs_regex = self.settings.value("excluded_dirs_regex", None)
        if excluded_dirs_regex:
            self.exporter.excluded_dirs_regex = set(excluded_dirs_regex)
            
        included_extensions = self.settings.value("included_extensions", None)
        if included_extensions:
            self.exporter.included_file_extensions = set(included_extensions)
            
        included_file_regex = self.settings.value("included_file_regex", None)
        if included_file_regex:
            self.exporter.included_file_regex = set(included_file_regex)
            
        # Aggiorna le liste UI
        self.update_config_lists()
        
        # AGGIUNTA: Carica l'albero se è presente un percorso di directory
        directory_path = self.dir_path.text()
        if directory_path:
            self.load_tree_structure()
        
    def load_tree_structure(self):
        """Carica la struttura delle directory nell'albero"""
        directory = self.dir_path.text()
        if not directory:
            QMessageBox.warning(self, "Errore", "Seleziona prima una directory.")
            return
    
        # Resetta l'albero
        self.tree_widget.clear()
        
        # Imposta il cursore di attesa
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        
        try:
            # Crea l'elemento radice
            root_path = Path(directory)
            root_item = QTreeWidgetItem(self.tree_widget)
            root_item.setText(0, root_path.name)
            root_item.setText(1, "Directory")
            root_item.setText(2, str(root_path))
            
            # Imposta un'icona per la cartella
            root_item.setIcon(0, self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon))
            
            # Rendi il testo in grassetto
            font = root_item.font(0)
            font.setBold(True)
            root_item.setFont(0, font)
            
            # Popola il primo livello
            self.populate_tree_item(root_item, root_path)
            
            # Espandi l'elemento radice
            root_item.setExpanded(True)
            
            # Mostra la statusbar
            self.statusBar.showMessage(f"Struttura caricata: {directory}")
        
        finally:
            # Ripristina il cursore
            QApplication.restoreOverrideCursor()

    def populate_tree_item(self, parent_item, path):
        """Popola un elemento dell'albero con i suoi figli"""
        # Controlla se applicare i filtri
        apply_filters = self.apply_filters_check.isChecked()
        
        try:
            # Ordina le cartelle prima dei file
            entries = sorted(path.iterdir(), key=lambda e: (not e.is_dir(), e.name.lower()))
            
            for entry in entries:
                # Salta le directory escluse se i filtri sono attivi
                if apply_filters and entry.is_dir() and self.exporter.is_excluded_dir(entry.name):
                    continue
                    
                # Salta i file se non sono visibili o se i filtri sono attivi e l'estensione non è inclusa
                if entry.is_file():
                    if not self.show_files_check.isChecked():
                        continue
                    if apply_filters and not self.exporter.is_included_file(entry.name):
                        continue
                
                # Crea l'elemento figlio
                item = QTreeWidgetItem(parent_item)
                item.setText(0, entry.name)
                item.setText(2, str(entry))
                
                if entry.is_dir():
                    # È una directory
                    item.setText(1, "Directory")
                    item.setIcon(0, self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon))
                    
                    # Aggiungi un elemento temporaneo per mostrare l'icona di espansione
                    QTreeWidgetItem(item, ["Caricamento..."])
                else:
                    # È un file
                    item.setText(1, "File")
                    item.setIcon(0, self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon))
    
        except PermissionError:
            # In caso di errore di permessi
            error_item = QTreeWidgetItem(parent_item)
            error_item.setText(0, "Accesso negato")
            error_item.setText(1, "Errore")
            error_item.setForeground(0, QColor(255, 0, 0))

    def on_item_expanded(self, item):
        """Gestisce l'espansione di un elemento"""
        # Se l'elemento ha solo un figlio "Caricamento..." lo sostituisce con il contenuto effettivo
        if item.childCount() == 1 and item.child(0).text(0) == "Caricamento...":
            # Rimuovi l'elemento temporaneo
            item.removeChild(item.child(0))
            
            # Ottieni il percorso dall'item
            path = Path(item.text(2))
            
            # Popola l'elemento con i suoi figli
            self.populate_tree_item(item, path)

    def reload_tree_structure(self):
        """Ricarica la struttura dell'albero applicando i filtri correnti"""
        # Verifica che tree_widget esista
        if hasattr(self, 'tree_widget') and self.tree_widget.topLevelItemCount() > 0:
            # Ricarichiamo la struttura
            self.load_tree_structure()

    def filter_tree_items(self):
        """Filtra gli elementi dell'albero in base al testo di ricerca"""
        search_text = self.search_input.text().lower()
        
        def set_item_visible(item, visible):
            # PyQt non ha un metodo diretto per nascondere gli elementi dell'albero
            # quindi impostiamo un'altezza di riga pari a 0 per nasconderli
            item.setHidden(not visible)
        
        def search_in_item(item):
            # Se il testo di ricerca è vuoto, mostriamo tutto
            if not search_text:
                set_item_visible(item, True)
                for i in range(item.childCount()):
                    search_in_item(item.child(i))
                return True
            
            # Controllo se l'elemento corrente corrisponde
            if search_text in item.text(0).lower():
                # Mostra l'elemento e tutti i suoi antenati
                set_item_visible(item, True)
                parent = item.parent()
                while parent:
                    set_item_visible(parent, True)
                    parent = parent.parent()
                
                # Mostra anche tutti i figli
                for i in range(item.childCount()):
                    set_item_visible(item.child(i), True)
                
                return True
            
            # Cerca nei figli
            match_in_children = False
            for i in range(item.childCount()):
                if search_in_item(item.child(i)):
                    match_in_children = True
            
            # Se c'è una corrispondenza nei figli, mostra anche questo elemento
            set_item_visible(item, match_in_children)
            return match_in_children
        
        # Applica la ricerca a tutti gli elementi principali
        for i in range(self.tree_widget.topLevelItemCount()):
            search_in_item(self.tree_widget.topLevelItem(i))
    def setup_tree_context_menu(self):
        """Configura il menu contestuale per l'albero"""
        self.tree_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_widget.customContextMenuRequested.connect(self.show_tree_context_menu)

    def show_tree_context_menu(self, position):
        """Mostra il menu contestuale per l'elemento selezionato nell'albero"""
        item = self.tree_widget.itemAt(position)
        if not item:
            return
        
        context_menu = QMenu(self)
        
        # Azioni diverse in base al tipo di elemento
        if item.text(1) == "Directory":
            # Azioni per directory
            expand_action = context_menu.addAction("Espandi tutto")
            collapse_action = context_menu.addAction("Comprimi tutto")
            context_menu.addSeparator()
            open_action = context_menu.addAction("Apri in Esplora risorse")
            
        elif item.text(1) == "File":
            # Azioni per file
            open_action = context_menu.addAction("Apri file")
            open_dir_action = context_menu.addAction("Apri cartella contenitore")
        
        # Aggiungi azioni comuni
        context_menu.addSeparator()
        copy_path_action = context_menu.addAction("Copia percorso")
        
        # Esegui il menu e ottieni l'azione selezionata
        action = context_menu.exec(self.tree_widget.mapToGlobal(position))
        
        # Gestisci l'azione selezionata
        if action:
            path = Path(item.text(2))
            
            if action == expand_action:
                item.setExpanded(True)
                self.expand_all_children(item)
            elif action == collapse_action:
                self.collapse_all_children(item)
            elif action == open_action:
                if path.is_dir():
                    QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))
                else:
                    QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))
            elif action == open_dir_action:
                QDesktopServices.openUrl(QUrl.fromLocalFile(str(path.parent)))
            elif action == copy_path_action:
                QApplication.clipboard().setText(str(path))
                self.statusBar.showMessage(f"Percorso copiato: {path}", 3000)

    def expand_all_children(self, item):
        """Espande ricorsivamente tutti i figli di un elemento"""
        for i in range(item.childCount()):
            child = item.child(i)
            if child.childCount() > 0:
                child.setExpanded(True)
                self.expand_all_children(child)

    def collapse_all_children(self, item):
        """Comprime ricorsivamente tutti i figli di un elemento"""
        for i in range(item.childCount()):
            child = item.child(i)
            if child.childCount() > 0:
                self.collapse_all_children(child)
                child.setExpanded(False)