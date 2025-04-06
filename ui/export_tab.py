from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QLineEdit, QFileDialog, QGroupBox, QCheckBox, QSpinBox, 
                            QComboBox, QMessageBox, QTreeWidget, QTreeWidgetItem, QMenu)
from PyQt6.QtCore import Qt, QSettings, QUrl
from PyQt6.QtGui import QColor, QDesktopServices
from PyQt6.QtWidgets import QApplication, QStyle
from pathlib import Path
from PyQt6.QtCore import Qt, QSettings, QUrl, QMimeData
from PyQt6.QtGui import QColor, QDesktopServices, QDragEnterEvent, QDropEvent
from PyQt6.QtWidgets import QProgressBar
from utils.directory_scanner import DirectoryScannerThread

class ExportTab(QWidget):
    def __init__(self, exporter, filter_manager, settings):
        super().__init__()
        self.exporter = exporter
        self.filter_manager = filter_manager
        self.settings = settings
        self.setup_ui()
        self.setup_tree_context_menu()
        self.load_settings()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.setAcceptDrops(True)

        # Gruppo per la selezione della directory
        dir_group = QGroupBox("Selezione Directory")
        dir_layout = QHBoxLayout()
        
        self.dir_path = QLineEdit()
        browse_dir_btn = QPushButton("Sfoglia...")
        browse_dir_btn.clicked.connect(self.browse_directory)
        
        # Aggiungi l'etichetta per il drag & drop
        drop_hint = QLabel("Trascina qui una cartella")
        drop_hint.setStyleSheet("color: gray; font-style: italic;")
        
        dir_layout.addWidget(QLabel("Directory:"))
        dir_layout.addWidget(self.dir_path, 1)
        dir_layout.addWidget(browse_dir_btn)
        dir_layout.addWidget(drop_hint)
        dir_group.setLayout(dir_layout)
        
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

        tree_group = QGroupBox("Struttura Directory")
        tree_layout = QVBoxLayout()
        
        # Area vista struttura
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
        self.tree_widget.itemExpanded.connect(self.on_item_expanded)

        progress_layout = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setVisible(False)  # Nascosta per default
        
        self.progress_label = QLabel("In attesa...")
        self.progress_label.setVisible(False)
        
        self.cancel_scan_btn = QPushButton("Annulla")
        self.cancel_scan_btn.clicked.connect(self.cancel_scan)
        self.cancel_scan_btn.setVisible(False)
        
        progress_layout.addWidget(self.progress_label)
        progress_layout.addWidget(self.progress_bar, 1)
        progress_layout.addWidget(self.cancel_scan_btn)
        
        # Componiamo il layout della vista ad albero
        tree_layout.addLayout(tree_controls)
        tree_layout.addWidget(self.tree_widget)
        tree_layout.addLayout(progress_layout)
        tree_group.setLayout(tree_layout)
        
        
        # Aggiungi tutto al layout principale
        layout.addWidget(dir_group)
        layout.addWidget(output_group)
        layout.addLayout(format_layout)
        layout.addWidget(options_group)
        layout.addLayout(action_layout)
        layout.addWidget(tree_group, 1)  # Diamo peso 1 per far espandere la vista
    
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
        action = context_menu.exec(self.tree_widget.viewport().mapToGlobal(position))
        
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
                self.window().statusBar.showMessage(f"Percorso copiato: {path}", 3000)
    
    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Seleziona Directory")
        if directory:
            self.dir_path.setText(directory)
            # Carichiamo automaticamente l'albero
            self.load_tree_structure()
    
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
    
    def export_structure(self):
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
                self.window().statusBar.showMessage(message, 5000)  # Mostra per 5 secondi
            else:
                QMessageBox.warning(self, "Errore durante l'esportazione", message)
                
        except Exception as e:
            error_message = f"Errore durante l'esportazione: {e}"
            QMessageBox.critical(self, "Errore", error_message)
    
    def load_tree_structure(self):
        """Carica la struttura delle directory nell'albero"""
        directory = self.dir_path.text()
        if not directory:
            QMessageBox.warning(self, "Errore", "Seleziona prima una directory.")
            return

        # Resetta l'albero
        self.tree_widget.clear()
        
        # Prepara la UI per la scansione
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.progress_label.setText("Preparazione scansione...")
        self.progress_label.setVisible(True)
        self.cancel_scan_btn.setVisible(True)
        
        # Crea l'elemento radice
        root_path = Path(directory)
        self.root_item = QTreeWidgetItem(self.tree_widget)
        self.root_item.setText(0, root_path.name)
        self.root_item.setText(1, "Directory")
        self.root_item.setText(2, str(root_path))
        
        # Imposta un'icona per la cartella
        self.root_item.setIcon(0, self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon))
        
        # Rendi il testo in grassetto
        font = self.root_item.font(0)
        font.setBold(True)
        self.root_item.setFont(0, font)
        
        # Avvia il thread di scansione
        self.scanner = DirectoryScannerThread(
            root_path,
            self.filter_manager,
            self.show_files_check.isChecked(),
            self.apply_filters_check.isChecked(),
            None if self.depth_spin.value() == 0 else self.depth_spin.value()
        )
        
        # Connessione dei segnali
        self.scanner.progress_updated.connect(self.update_scan_progress)
        self.scanner.status_updated.connect(self.update_scan_status)
        self.scanner.directory_scanned.connect(self.process_scanned_directory)
        self.scanner.scan_completed.connect(self.on_scan_completed)
        self.scanner.scan_canceled.connect(self.on_scan_canceled)
        self.scanner.scan_error.connect(self.on_scan_error)
        
        # Avvio del thread
        self.scanner.start()
        
        # Espandiamo l'elemento radice
        self.root_item.setExpanded(True)
        
        # Mostriamo un messaggio nella statusbar
        main_window = self.window()
        if main_window and hasattr(main_window, 'statusBar'):
            main_window.statusBar.showMessage(f"Scansione in corso: {directory}")
    
    def update_scan_progress(self, value):
        """Aggiorna la barra di progresso"""
        self.progress_bar.setValue(value)

    def update_scan_status(self, message):
        """Aggiorna il messaggio di stato"""
        self.progress_label.setText(message)

    def process_scanned_directory(self, path, entries):
        """Processa i risultati di una directory scansionata"""
        # Troviamo l'elemento corrispondente al percorso
        parent_item = self.find_tree_item_by_path(str(path))
        
        if parent_item:
            # Se l'elemento ha un figlio "Caricamento...", lo rimuoviamo
            if parent_item.childCount() == 1 and parent_item.child(0).text(0) == "Caricamento...":
                parent_item.removeChild(parent_item.child(0))
                
            # Aggiungiamo gli elementi trovati
            for entry, is_dir in entries:
                item = QTreeWidgetItem(parent_item)
                item.setText(0, entry.name)
                item.setText(2, str(entry))
                
                if is_dir:
                    # È una directory
                    item.setText(1, "Directory")
                    item.setIcon(0, self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon))
                    
                    # Aggiungiamo un elemento temporaneo
                    QTreeWidgetItem(item, ["Caricamento..."])
                else:
                    # È un file
                    item.setText(1, "File")
                    item.setIcon(0, self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon))

    def find_tree_item_by_path(self, path_str):
        """Trova un elemento nell'albero in base al percorso"""
        # Controlla l'elemento radice
        if self.tree_widget.topLevelItemCount() > 0:
            root_item = self.tree_widget.topLevelItem(0)
            if root_item.text(2) == path_str:
                return root_item
                
            # Ricerca ricorsiva
            return self.find_tree_item_by_path_recursive(root_item, path_str)
        
        return None

    def find_tree_item_by_path_recursive(self, parent_item, path_str):
        """Ricerca ricorsiva di un elemento per percorso"""
        for i in range(parent_item.childCount()):
            child = parent_item.child(i)
            if child.text(2) == path_str:
                return child
                
            # Ricerca nei figli
            found = self.find_tree_item_by_path_recursive(child, path_str)
            if found:
                return found
        
        return None

    def on_scan_completed(self):
        """Gestisce il completamento della scansione"""
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        self.cancel_scan_btn.setVisible(False)
        
        # Mostra messaggio nella statusbar
        main_window = self.window()
        if main_window and hasattr(main_window, 'statusBar'):
            directory = self.dir_path.text()
            main_window.statusBar.showMessage(f"Struttura caricata: {directory}")

    def on_scan_canceled(self):
        """Gestisce l'annullamento della scansione"""
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        self.cancel_scan_btn.setVisible(False)
        
        # Mostra messaggio nella statusbar
        main_window = self.window()
        if main_window and hasattr(main_window, 'statusBar'):
            main_window.statusBar.showMessage("Scansione annullata")

    def on_scan_error(self, error_message):
        """Gestisce gli errori durante la scansione"""
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        self.cancel_scan_btn.setVisible(False)
        
        QMessageBox.critical(self, "Errore di scansione", f"Si è verificato un errore durante la scansione: {error_message}")
        
        main_window = self.window()
        if main_window and hasattr(main_window, 'statusBar'):
            main_window.statusBar.showMessage(f"Errore di scansione: {error_message}")

    def cancel_scan(self):
        """Annulla la scansione in corso"""
        if hasattr(self, 'scanner') and self.scanner.isRunning():
            self.scanner.cancel()
            self.progress_label.setText("Annullamento in corso...")

    def populate_tree_item(self, parent_item, path):
        """Popola un elemento dell'albero con i suoi figli"""
        # Controlla se applicare i filtri
        apply_filters = self.apply_filters_check.isChecked()
        
        try:
            # Ordina le cartelle prima dei file
            entries = sorted(path.iterdir(), key=lambda e: (not e.is_dir(), e.name.lower()))
            
            for entry in entries:
                # Salta le directory escluse se i filtri sono attivi
                if apply_filters and entry.is_dir() and self.filter_manager.is_excluded_dir(entry.name):
                    continue
                    
                # Salta i file se non sono visibili o se i filtri sono attivi e l'estensione non è inclusa
                if entry.is_file():
                    if not self.show_files_check.isChecked():
                        continue
                    if apply_filters and not self.filter_manager.is_included_file(entry):
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
            path = Path(item.text(2))
            # Il contenuto verrà caricato dal thread di scansione
            # Mostriamo solo un indicatore di caricamento
            item.child(0).setText(0, "Caricamento in corso...")
            
            # Creiamo e avviamo un thread per questa directory specifica
            scanner = DirectoryScannerThread(
                path,
                self.filter_manager,
                self.show_files_check.isChecked(),
                self.apply_filters_check.isChecked(),
                None  # Non impostiamo max_depth qui poiché stiamo caricando solo i figli diretti
            )
            
            # Connessione dei segnali
            scanner.directory_scanned.connect(self.process_scanned_directory)
            scanner.scan_error.connect(lambda msg: self.on_item_scan_error(item, msg))
            
            # Salva il riferimento per evitare che venga garbage-collected
            self.current_item_scanner = scanner
            scanner.start()

    def on_item_scan_error(self, item, error_message):
        """Gestisce gli errori durante la scansione di un item"""
        # Rimuove tutti i figli
        while item.childCount() > 0:
            item.removeChild(item.child(0))
        
        # Aggiunge un elemento di errore
        error_item = QTreeWidgetItem(item)
        error_item.setText(0, f"Errore: {error_message}")
        error_item.setText(1, "Errore")
        error_item.setForeground(0, QColor(255, 0, 0))
    
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
    
    def sync_tree_with_export_options(self):
        """Sincronizza le opzioni della vista albero con quelle di esportazione"""
        # Verifica se l'attributo show_files_check esiste
        if hasattr(self, 'show_files_check'):
            # Sincronizziamo il checkbox dei file
            self.show_files_check.setChecked(self.include_files_check.isChecked())
            
            # Aggiorniamo l'albero
            self.reload_tree_structure()
    
    def save_settings(self):
        """Salva le impostazioni della scheda"""
        # Salva i percorsi
        self.settings.setValue("dir_path", self.dir_path.text())
        self.settings.setValue("output_path", self.output_path.text())
        
        # Salva le impostazioni di esportazione
        self.settings.setValue("format", self.format_combo.currentText())
        self.settings.setValue("include_files", self.include_files_check.isChecked())
        self.settings.setValue("max_depth", self.depth_spin.value())
    
    def load_settings(self):
        """Carica le impostazioni della scheda"""
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
        
        # Carica la struttura se è presente un percorso di directory
        directory_path = self.dir_path.text()
        if directory_path:
            self.load_tree_structure()
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Gestisce l'evento di inizio trascinamento"""
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                if Path(path).is_dir():
                    # Aggiungi un effetto visivo
                    self.setStyleSheet("QGroupBox[title=\"Selezione Directory\"] { border: 2px dashed #0066cc; background-color: #e6f0ff; }")
                    event.acceptProposedAction()
                    return
        
        event.ignore()
    
    def dragLeaveEvent(self, event):
        """Gestisce l'uscita del cursore durante il trascinamento"""
        # Ripristina lo stile normale
        self.setStyleSheet("")
        event.accept()

    def dragMoveEvent(self, event):
        """Gestisce l'evento di movimento durante il trascinamento"""
        # Accetta l'azione se dragEnterEvent l'ha accettata
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        """Gestisce l'evento di rilascio"""
        self.setStyleSheet("")
        # Controlla se i dati rilasciati contengono URL
        if event.mimeData().hasUrls():
            # Prende il primo URL che è una directory
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                if Path(path).is_dir():
                    # Imposta il percorso e carica la struttura
                    self.dir_path.setText(path)
                    self.load_tree_structure()
                    # Imposta il focus sulla struttura ad albero
                    self.tree_widget.setFocus()
                    event.acceptProposedAction()
                    # Aggiorna la barra di stato
                    self.window().statusBar.showMessage(f"Directory caricata: {path}", 3000)
                    return
        
        event.ignore()