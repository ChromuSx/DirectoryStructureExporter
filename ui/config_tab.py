from PyQt6.QtWidgets import (QLineEdit, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QInputDialog, QListWidget, QGroupBox, QFileDialog, QMessageBox, QComboBox)
import re

class ConfigTab(QWidget):
    def __init__(self, filter_manager, config_manager, settings):
        super().__init__()
        self.filter_manager = filter_manager
        self.config_manager = config_manager
        self.settings = settings
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Sezione directory escluse
        excluded_dirs_group = QGroupBox("Directory escluse")
        excluded_layout = QVBoxLayout()
        self.excluded_dirs_list = QListWidget()
        
        # Popola la lista con i valori attuali
        for dir_name in self.filter_manager.excluded_dirs:
            self.excluded_dirs_list.addItem(dir_name)
        for pattern in self.filter_manager.excluded_dirs_regex:
            self.excluded_dirs_list.addItem(f"[regex] {pattern}")
        
        preset_group = QGroupBox("Preset Configurazioni")
        preset_layout = QVBoxLayout()
        
        # Combo box per selezionare preset esistenti
        preset_selector_layout = QHBoxLayout()
        preset_selector_layout.addWidget(QLabel("Preset:"))
        self.preset_combo = QComboBox()
        self.preset_combo.setMinimumWidth(200)
        self.update_preset_combo()  # Popoliamo la combo con i preset esistenti
        self.preset_combo.currentIndexChanged.connect(self.on_preset_selected)
        
        preset_selector_layout.addWidget(self.preset_combo)
        preset_selector_layout.addStretch(1)
        
        # Pulsanti per gestire i preset
        preset_buttons_layout = QHBoxLayout()
        save_preset_btn = QPushButton("Salva come nuovo")
        update_preset_btn = QPushButton("Aggiorna selezionato")
        delete_preset_btn = QPushButton("Elimina selezionato")
        
        save_preset_btn.clicked.connect(self.save_new_preset)
        update_preset_btn.clicked.connect(self.update_current_preset)
        delete_preset_btn.clicked.connect(self.delete_current_preset)
        
        preset_buttons_layout.addWidget(save_preset_btn)
        preset_buttons_layout.addWidget(update_preset_btn)
        preset_buttons_layout.addWidget(delete_preset_btn)
        
        preset_layout.addLayout(preset_selector_layout)
        preset_layout.addLayout(preset_buttons_layout)
        preset_group.setLayout(preset_layout)
        
        preset_path_group = QGroupBox("Percorso File Preset")
        preset_path_layout = QHBoxLayout()

        preset_path_layout.addWidget(QLabel("File preset:"))
        self.preset_path_edit = QLineEdit()
        self.preset_path_edit.setText(self.settings.value("presets_path", "presets.json"))
        preset_path_layout.addWidget(self.preset_path_edit, 1)

        browse_preset_path_btn = QPushButton("Sfoglia...")
        browse_preset_path_btn.clicked.connect(self.browse_preset_path)
        preset_path_layout.addWidget(browse_preset_path_btn)

        apply_path_btn = QPushButton("Applica")
        apply_path_btn.clicked.connect(self.apply_preset_path)
        preset_path_layout.addWidget(apply_path_btn)

        preset_path_group.setLayout(preset_path_layout)
        layout.addWidget(preset_path_group)

        # Aggiungi il gruppo al layout principale
        layout.addWidget(preset_group)

        excluded_buttons_layout = QHBoxLayout()
        add_excluded_btn = QPushButton("Aggiungi")
        add_excluded_regex_btn = QPushButton("Aggiungi Regex")
        remove_excluded_btn = QPushButton("Rimuovi")
        regex_help_btn = QPushButton("?")
        
        add_excluded_btn.clicked.connect(self.add_excluded_dir)
        add_excluded_regex_btn.clicked.connect(self.add_excluded_dir_regex)
        remove_excluded_btn.clicked.connect(self.remove_excluded_dir)
        regex_help_btn.setFixedSize(25, 25)
        regex_help_btn.clicked.connect(self.show_regex_help)
        
        excluded_buttons_layout.addWidget(add_excluded_btn)
        excluded_buttons_layout.addWidget(add_excluded_regex_btn)
        excluded_buttons_layout.addWidget(remove_excluded_btn)
        excluded_buttons_layout.addWidget(regex_help_btn)
        
        excluded_layout.addWidget(self.excluded_dirs_list)
        excluded_layout.addLayout(excluded_buttons_layout)
        excluded_dirs_group.setLayout(excluded_layout)
        
        # Sezione estensioni incluse
        included_exts_group = QGroupBox("Estensioni incluse")
        included_layout = QVBoxLayout()
        self.included_exts_list = QListWidget()
        
        # Popola la lista con i valori attuali
        for ext in self.filter_manager.included_file_extensions:
            self.included_exts_list.addItem(ext)
        for pattern in self.filter_manager.included_file_regex:
            self.included_exts_list.addItem(f"[regex] {pattern}")
        
        included_buttons_layout = QHBoxLayout()
        add_included_btn = QPushButton("Aggiungi")
        add_included_regex_btn = QPushButton("Aggiungi Regex") 
        remove_included_btn = QPushButton("Rimuovi")
        regex_help_btn_ext = QPushButton("?")
        
        add_included_btn.clicked.connect(self.add_included_ext)
        add_included_regex_btn.clicked.connect(self.add_included_ext_regex)
        remove_included_btn.clicked.connect(self.remove_included_ext)
        regex_help_btn_ext.setFixedSize(25, 25)
        regex_help_btn_ext.clicked.connect(self.show_regex_help)
        
        included_buttons_layout.addWidget(add_included_btn)
        included_buttons_layout.addWidget(add_included_regex_btn)
        included_buttons_layout.addWidget(remove_included_btn)
        included_buttons_layout.addWidget(regex_help_btn_ext)
        
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
        
        # Aggiunta al layout principale
        layout.addWidget(excluded_dirs_group)
        layout.addWidget(included_exts_group)
        layout.addLayout(config_buttons_layout)

    def browse_preset_path(self):
        """Permette all'utente di scegliere il percorso del file dei preset"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Imposta file preset", self.preset_path_edit.text(), "File JSON (*.json)"
        )
        
        if file_path:
            self.preset_path_edit.setText(file_path)

    def apply_preset_path(self):
        """Applica il nuovo percorso dei preset"""
        new_path = self.preset_path_edit.text()
        current_path = self.settings.value("presets_path", "presets.json")
        
        if new_path != current_path:
            # Chiedi conferma
            if QMessageBox.question(
                self, 
                "Cambiare percorso preset", 
                f"Vuoi spostare i preset in '{new_path}'?\nI preset attuali verranno copiati nel nuovo percorso.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            ) == QMessageBox.StandardButton.Yes:
                # Salva i preset attuali nel nuovo percorso
                self.settings.setValue("presets_path", new_path)
                self.config_manager.save_presets(new_path)
                self.window().statusBar.showMessage(f"Percorso preset impostato: {new_path}", 3000)

    def update_preset_combo(self):
        """Aggiorna la combo box con i preset disponibili"""
        self.preset_combo.clear()
        self.preset_combo.addItem("-- Seleziona un preset --")
        preset_names = self.config_manager.get_filter_preset_names()
        for name in sorted(preset_names):
            self.preset_combo.addItem(name)

    def on_preset_selected(self, index):
        """Gestisce la selezione di un preset dalla combo"""
        if index <= 0:  # Nessun preset selezionato
            return
            
        preset_name = self.preset_combo.currentText()
        success, message = self.config_manager.load_filter_preset(preset_name)
        
        if success:
            # Aggiorna l'interfaccia utente
            self.update_config_lists()
            
            # Aggiorna anche la scheda dei filtri
            if hasattr(self.window(), 'filters_tab') and self.window().filters_tab:
                self.window().filters_tab.update_filters_ui()
                
            # Aggiorna il tree view se necessario
            if hasattr(self.window(), 'export_tab') and self.window().export_tab:
                self.window().export_tab.reload_tree_structure()
                
            self.window().statusBar.showMessage(message, 3000)
        else:
            QMessageBox.warning(self, "Errore", message)

    def save_new_preset(self):
        """Salva la configurazione corrente come nuovo preset"""
        preset_name, ok = QInputDialog.getText(
            self, "Salva Preset", "Nome del preset:"
        )
        if ok and preset_name:
            # Verifica se esiste già
            if preset_name in self.config_manager.get_filter_preset_names():
                if QMessageBox.question(
                    self, 
                    "Preset esistente", 
                    f"Il preset '{preset_name}' esiste già. Sovrascrivere?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                ) == QMessageBox.StandardButton.No:
                    return

            # Salva il preset
            success, message = self.config_manager.save_filter_preset(preset_name)
            
            if success:
                self.update_preset_combo()
                # Seleziona il preset appena creato
                index = self.preset_combo.findText(preset_name)
                if index >= 0:
                    self.preset_combo.setCurrentIndex(index)
                self.window().statusBar.showMessage(message, 3000)
            else:
                QMessageBox.warning(self, "Errore", message)

    def update_current_preset(self):
        """Aggiorna il preset selezionato con la configurazione corrente"""
        index = self.preset_combo.currentIndex()
        if index <= 0:
            QMessageBox.warning(self, "Nessun preset selezionato", "Seleziona prima un preset da aggiornare.")
            return
            
        preset_name = self.preset_combo.currentText()
        
        # Chiedi conferma
        if QMessageBox.question(
            self, 
            "Aggiorna preset", 
            f"Sei sicuro di voler aggiornare il preset '{preset_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        ) == QMessageBox.StandardButton.Yes:
            success, message = self.config_manager.save_filter_preset(preset_name)
            if success:
                self.window().statusBar.showMessage(message, 3000)
            else:
                QMessageBox.warning(self, "Errore", message)

    def delete_current_preset(self):
        """Elimina il preset selezionato"""
        index = self.preset_combo.currentIndex()
        if index <= 0:
            QMessageBox.warning(self, "Nessun preset selezionato", "Seleziona prima un preset da eliminare.")
            return
            
        preset_name = self.preset_combo.currentText()
        
        # Chiedi conferma
        if QMessageBox.question(
            self, 
            "Elimina preset", 
            f"Sei sicuro di voler eliminare il preset '{preset_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        ) == QMessageBox.StandardButton.Yes:
            success, message = self.config_manager.delete_filter_preset(preset_name)
            if success:
                self.update_preset_combo()
                self.preset_combo.setCurrentIndex(0)  # Resetta la selezione
                self.window().statusBar.showMessage(message, 3000)
            else:
                QMessageBox.warning(self, "Errore", message)
    
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
    
    def add_excluded_dir(self):
        dir_name, ok = QInputDialog.getText(self, "Aggiungi directory", "Nome directory:")
        if ok and dir_name:
            self.excluded_dirs_list.addItem(dir_name)
            self.filter_manager.add_excluded_dir(dir_name)
    
    def add_excluded_dir_regex(self):
        pattern, ok = QInputDialog.getText(
            self, 
            "Aggiungi pattern regex", 
            "Inserisci un'espressione regolare per escludere le directory:"
        )
        if ok and pattern:
            if self.filter_manager.add_excluded_dir_regex(pattern):
                # Aggiungiamo alla lista visuale con indicatore [regex]
                self.excluded_dirs_list.addItem(f"[regex] {pattern}")
            else:
                QMessageBox.warning(
                    self, 
                    "Espressione non valida", 
                    "L'espressione regolare inserita non è valida."
                )
    
    def remove_excluded_dir(self):
        selected_items = self.excluded_dirs_list.selectedItems()
        if selected_items:
            for item in selected_items:
                dir_name = item.text()
                self.excluded_dirs_list.takeItem(self.excluded_dirs_list.row(item))
                
                # Determiniamo se è un pattern regex o una stringa semplice
                if dir_name.startswith("[regex] "):
                    pattern = dir_name[8:]  # Rimuovi il prefisso "[regex] "
                    self.filter_manager.remove_excluded_dir_regex(pattern)
                else:
                    self.filter_manager.remove_excluded_dir(dir_name)
    
    def add_included_ext(self):
        ext, ok = QInputDialog.getText(self, "Aggiungi estensione", "Estensione (con punto iniziale, es. .py):")
        if ok and ext:
            if not ext.startswith('.'):
                ext = f".{ext}"
            self.included_exts_list.addItem(ext)
            self.filter_manager.add_included_ext(ext)
    
    def add_included_ext_regex(self):
        pattern, ok = QInputDialog.getText(
            self, 
            "Aggiungi pattern regex", 
            "Inserisci un'espressione regolare per includere i file:"
        )
        if ok and pattern:
            if self.filter_manager.add_included_file_regex(pattern):
                # Aggiungiamo alla lista visuale con indicatore [regex]
                self.included_exts_list.addItem(f"[regex] {pattern}")
            else:
                QMessageBox.warning(
                    self, 
                    "Espressione non valida", 
                    "L'espressione regolare inserita non è valida."
                )
    
    def remove_included_ext(self):
        selected_items = self.included_exts_list.selectedItems()
        if selected_items:
            for item in selected_items:
                ext = item.text()
                self.included_exts_list.takeItem(self.included_exts_list.row(item))
                
                # Determiniamo se è un pattern regex o una stringa semplice
                if ext.startswith("[regex] "):
                    pattern = ext[8:]  # Rimuovi il prefisso "[regex] "
                    self.filter_manager.remove_included_file_regex(pattern)
                else:
                    self.filter_manager.remove_included_ext(ext)
    
    def save_config(self):
        """Salva la configurazione corrente in un file JSON"""
        config_file, _ = QFileDialog.getSaveFileName(
            self, "Salva Configurazione", "", "File JSON (*.json)"
        )
        
        if not config_file:
            return
            
        # Usa l'oggetto config_manager per salvare la configurazione
        success, message = self.config_manager.save_config(config_file)
        
        if success:
            self.window().statusBar.showMessage(message, 3000)
        else:
            QMessageBox.warning(self, "Errore", message)
    
    def load_config(self):
        """Carica la configurazione da un file JSON"""
        config_file, _ = QFileDialog.getOpenFileName(
            self, "Carica Configurazione", "", "File JSON (*.json)"
        )
        
        if not config_file:
            return
            
        # Usa l'oggetto config_manager per caricare la configurazione
        success, message = self.config_manager.load_config(config_file)
        
        if success:
            # Aggiorna le liste UI dopo aver caricato la configurazione
            self.update_config_lists()
            
            # Aggiorna anche i controlli nella scheda filtri
            if hasattr(self.window(), 'filters_tab') and self.window().filters_tab:
                self.window().filters_tab.update_filters_ui()
                
            # Aggiorna il tree view se necessario
            if hasattr(self.window(), 'export_tab') and self.window().export_tab:
                self.window().export_tab.reload_tree_structure()
                
            # Aggiorna la combo dei preset
            self.update_preset_combo()
                
            self.window().statusBar.showMessage(message, 3000)
        else:
            QMessageBox.warning(self, "Errore", message)
    
    def update_config_lists(self):
        """Aggiorna le liste UI con i valori attuali"""
        # Aggiorniamo la lista delle directory escluse
        self.excluded_dirs_list.clear()
        for dir_name in self.filter_manager.excluded_dirs:
            self.excluded_dirs_list.addItem(dir_name)
        for pattern in self.filter_manager.excluded_dirs_regex:
            self.excluded_dirs_list.addItem(f"[regex] {pattern}")
        
        # Aggiorniamo la lista delle estensioni incluse
        self.included_exts_list.clear()
        for ext in self.filter_manager.included_file_extensions:
            self.included_exts_list.addItem(ext)
        for pattern in self.filter_manager.included_file_regex:
            self.included_exts_list.addItem(f"[regex] {pattern}")
    
    def save_settings(self):
        """Salva le impostazioni della scheda"""
        # Salva la configurazione di directory escluse ed estensioni incluse
        self.settings.setValue("excluded_dirs", list(self.filter_manager.excluded_dirs))
        self.settings.setValue("excluded_dirs_regex", list(self.filter_manager.excluded_dirs_regex))
        self.settings.setValue("included_extensions", list(self.filter_manager.included_file_extensions))
        self.settings.setValue("included_file_regex", list(self.filter_manager.included_file_regex))
        self.settings.setValue("presets_path", self.preset_path_edit.text())
    
    def load_settings(self):
        """Carica le impostazioni della scheda"""
        # Carica la configurazione di directory escluse ed estensioni incluse
        excluded_dirs = self.settings.value("excluded_dirs", None)
        if excluded_dirs:
            self.filter_manager.excluded_dirs = set(excluded_dirs)
            
        excluded_dirs_regex = self.settings.value("excluded_dirs_regex", None)
        if excluded_dirs_regex:
            self.filter_manager.excluded_dirs_regex = set(excluded_dirs_regex)
            
        included_extensions = self.settings.value("included_extensions", None)
        if included_extensions:
            self.filter_manager.included_file_extensions = set(included_extensions)
            
        included_file_regex = self.settings.value("included_file_regex", None)
        if included_file_regex:
            self.filter_manager.included_file_regex = set(included_file_regex)
            
        # Aggiorna le liste UI
        self.update_config_lists()