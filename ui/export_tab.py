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

from utils.translation_manager import tr

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
        self.dir_group = QGroupBox(tr("Selezione Directory"))
        dir_layout = QHBoxLayout()
        
        self.dir_path = QLineEdit()
        self.browse_dir_btn = QPushButton(tr("Sfoglia..."))
        self.browse_dir_btn.clicked.connect(self.browse_directory)
        
        self.drop_hint = QLabel(tr("Trascina qui una cartella"))
        self.drop_hint.setStyleSheet("color: gray; font-style: italic;")
        
        self.dir_label = QLabel(tr("Directory:"))
        
        dir_layout.addWidget(self.dir_label)
        dir_layout.addWidget(self.dir_path, 1)
        dir_layout.addWidget(self.browse_dir_btn)
        dir_layout.addWidget(self.drop_hint)
        self.dir_group.setLayout(dir_layout)
        
        # Gruppo per il file di output
        self.output_group = QGroupBox(tr("File di Output"))
        output_layout = QHBoxLayout()
        
        self.output_path = QLineEdit()
        self.browse_output_btn = QPushButton(tr("Sfoglia..."))
        self.browse_output_btn.clicked.connect(self.browse_output)
        
        self.file_label = QLabel(tr("File:"))
        
        output_layout.addWidget(self.file_label)
        output_layout.addWidget(self.output_path, 1)
        output_layout.addWidget(self.browse_output_btn)
        self.output_group.setLayout(output_layout)
        
        # Riga per formato e stile indentazione
        format_style_layout = QHBoxLayout()
        
        # Selezione formato
        self.format_label = QLabel(tr("Formato:"))
        format_style_layout.addWidget(self.format_label)
        self.format_combo = QComboBox()
        self.format_combo.addItems(["TXT", "HTML", "JSON", "XML"])
        format_style_layout.addWidget(self.format_combo)
        
        format_style_layout.addSpacing(20)
        
        # Selezione stile indentazione
        self.indent_style_label = QLabel(tr("Stile indentazione:"))
        format_style_layout.addWidget(self.indent_style_label)
        self.indent_style_combo = QComboBox()
        self.populate_indent_styles()
        format_style_layout.addWidget(self.indent_style_combo)
        
        format_style_layout.addStretch(1)
        
        # Opzioni di esportazione
        self.options_group = QGroupBox(tr("Opzioni di esportazione"))
        options_layout = QVBoxLayout()
        
        self.include_files_check = QCheckBox(tr("Includi file"))
        self.include_files_check.stateChanged.connect(self.reload_tree_structure)
        self.include_files_check.stateChanged.connect(self.sync_tree_with_export_options)
        self.include_files_check.setChecked(True)
        options_layout.addWidget(self.include_files_check)
        
        # Opzione per la profondità massima
        depth_layout = QHBoxLayout()
        self.depth_label = QLabel(tr("Profondità massima:"))
        depth_layout.addWidget(self.depth_label)
        self.depth_spin = QSpinBox()
        self.depth_spin.valueChanged.connect(self.reload_tree_structure)
        self.depth_spin.setMinimum(0)
        self.depth_spin.setMaximum(999)
        self.depth_spin.setValue(0)
        self.depth_spin.setSpecialValueText(tr("Illimitata"))
        depth_layout.addWidget(self.depth_spin)
        options_layout.addLayout(depth_layout)
        
        self.options_group.setLayout(options_layout)
        
        # Pulsanti di azione
        action_layout = QHBoxLayout()
        self.export_btn = QPushButton(tr("Esporta"))
        self.export_btn.clicked.connect(self.export_structure)
        self.preview_btn = QPushButton(tr("Anteprima"))
        self.preview_btn.clicked.connect(self.show_preview)
        action_layout.addWidget(self.export_btn)
        action_layout.addWidget(self.preview_btn)

        # Area vista struttura
        self.tree_group = QGroupBox(tr("Struttura Directory"))
        tree_layout = QVBoxLayout()
        
        # Controlli per la vista ad albero
        tree_controls = QHBoxLayout()
        
        self.show_files_check = QCheckBox(tr("Mostra file"))
        self.show_files_check.setChecked(True)
        self.show_files_check.stateChanged.connect(self.reload_tree_structure)
        
        self.apply_filters_check = QCheckBox(tr("Applica filtri"))
        self.apply_filters_check.setChecked(True)
        self.apply_filters_check.stateChanged.connect(self.reload_tree_structure)
        
        # Barra di ricerca
        self.search_label = QLabel(tr("Cerca:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(tr("Cerca file o cartelle..."))
        self.search_input.textChanged.connect(self.filter_tree_items)
        
        tree_controls.addWidget(self.show_files_check)
        tree_controls.addWidget(self.apply_filters_check)
        tree_controls.addStretch(1)
        tree_controls.addWidget(self.search_label)
        tree_controls.addWidget(self.search_input)
        
        # Widget albero
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels([tr("Nome"), tr("Tipo"), tr("Percorso")])
        self.tree_widget.setColumnWidth(0, 300)
        self.tree_widget.setAlternatingRowColors(True)
        self.tree_widget.itemExpanded.connect(self.on_item_expanded)
        
        tree_layout.addLayout(tree_controls)
        tree_layout.addWidget(self.tree_widget)
        self.tree_group.setLayout(tree_layout)
        
        # Aggiungi tutto al layout principale
        layout.addWidget(self.dir_group)
        layout.addWidget(self.output_group)
        layout.addLayout(format_style_layout)
        layout.addWidget(self.options_group)
        layout.addLayout(action_layout)
        layout.addWidget(self.tree_group, 1)
    
    def populate_indent_styles(self):
        """Popola il combo box con gli stili di indentazione disponibili"""
        styles = self.exporter.get_available_indent_styles()
        self.indent_style_combo.clear()
        
        for key, name in styles.items():
            self.indent_style_combo.addItem(name, key)
    
    def show_preview(self):
        """Mostra un'anteprima della struttura con lo stile selezionato"""
        directory = self.dir_path.text()
        if not directory:
            QMessageBox.warning(self, tr("Errore"), tr("Seleziona prima una directory."))
            return
        
        include_files = self.include_files_check.isChecked()
        max_depth = None if self.depth_spin.value() == 0 else self.depth_spin.value()
        indent_style = self.indent_style_combo.currentData()
        
        # Genera anteprima
        preview_lines = self.exporter.generate_preview(
            directory, max_items=50, include_files=include_files, 
            max_depth=max_depth, indent_style=indent_style
        )
        
        if preview_lines:
            preview_text = "\n".join(preview_lines)
            if len(preview_lines) >= 50:
                preview_text += "\n\n... (anteprima limitata a 50 elementi)"
            
            # Crea finestra di dialogo per l'anteprima
            from PyQt6.QtWidgets import QDialog, QTextEdit, QVBoxLayout as QVBoxLayoutDialog
            
            dialog = QDialog(self)
            dialog.setWindowTitle(tr("Anteprima struttura"))
            dialog.resize(600, 400)
            
            layout = QVBoxLayoutDialog()
            text_edit = QTextEdit()
            text_edit.setPlainText(preview_text)
            text_edit.setFont(self.font())  # Usa font monospace
            text_edit.setReadOnly(True)
            
            layout.addWidget(text_edit)
            dialog.setLayout(layout)
            dialog.exec()
        else:
            QMessageBox.information(self, tr("Anteprima"), tr("Nessun elemento da visualizzare con i filtri attuali."))
    
    def retranslate_ui(self):
        """Aggiorna tutte le traduzioni dell'interfaccia"""
        # Aggiorna i titoli dei gruppi
        self.dir_group.setTitle(tr("Selezione Directory"))
        self.output_group.setTitle(tr("File di Output"))
        self.options_group.setTitle(tr("Opzioni di esportazione"))
        self.tree_group.setTitle(tr("Struttura Directory"))
        
        # Aggiorna le etichette
        self.dir_label.setText(tr("Directory:"))
        self.file_label.setText(tr("File:"))
        self.format_label.setText(tr("Formato:"))
        self.indent_style_label.setText(tr("Stile indentazione:"))
        self.depth_label.setText(tr("Profondità massima:"))
        self.search_label.setText(tr("Cerca:"))
        
        # Aggiorna i pulsanti
        self.browse_dir_btn.setText(tr("Sfoglia..."))
        self.browse_output_btn.setText(tr("Sfoglia..."))
        self.export_btn.setText(tr("Esporta"))
        self.preview_btn.setText(tr("Anteprima"))
        
        # Aggiorna i checkbox
        self.include_files_check.setText(tr("Includi file"))
        self.show_files_check.setText(tr("Mostra file"))
        self.apply_filters_check.setText(tr("Applica filtri"))
        
        # Aggiorna placeholder e altri testi
        self.drop_hint.setText(tr("Trascina qui una cartella"))
        self.search_input.setPlaceholderText(tr("Cerca file o cartelle..."))
        self.depth_spin.setSpecialValueText(tr("Illimitata"))
        
        # Aggiorna header dell'albero
        self.tree_widget.setHeaderLabels([tr("Nome"), tr("Tipo"), tr("Percorso")])
        
        # Ricarica gli stili di indentazione tradotti
        current_style = self.indent_style_combo.currentData()
        self.populate_indent_styles()
        # Ripristina la selezione
        for i in range(self.indent_style_combo.count()):
            if self.indent_style_combo.itemData(i) == current_style:
                self.indent_style_combo.setCurrentIndex(i)
                break
    
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
        
        if item.text(1) == tr("Directory") or item.text(1) == "Directory":
            expand_action = context_menu.addAction(tr("Espandi tutto"))
            collapse_action = context_menu.addAction(tr("Comprimi tutto"))
            context_menu.addSeparator()
            open_action = context_menu.addAction(tr("Apri in Esplora risorse"))
            
        elif item.text(1) == tr("File") or item.text(1) == "File":
            open_action = context_menu.addAction(tr("Apri file"))
            open_dir_action = context_menu.addAction(tr("Apri cartella contenitore"))
        
        context_menu.addSeparator()
        copy_path_action = context_menu.addAction(tr("Copia percorso"))
        
        action = context_menu.exec(self.tree_widget.viewport().mapToGlobal(position))
        
        if action:
            path = Path(item.text(2))
            
            if 'expand_action' in locals() and action == expand_action:
                item.setExpanded(True)
                self.expand_all_children(item)
            elif 'collapse_action' in locals() and action == collapse_action:
                self.collapse_all_children(item)
            elif action == open_action:
                if path.is_dir():
                    QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))
                else:
                    QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))
            elif 'open_dir_action' in locals() and action == open_dir_action:
                QDesktopServices.openUrl(QUrl.fromLocalFile(str(path.parent)))
            elif action == copy_path_action:
                QApplication.clipboard().setText(str(path))
                self.window().statusBar.showMessage(tr("Percorso copiato:") + f" {path}", 3000)
    
    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, tr("Seleziona Directory"))
        if directory:
            self.dir_path.setText(directory)
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
            self, tr("Salva File"), "", f"File {selected_format} (*{extension})"
        )
        
        if file_path:
            if not file_path.lower().endswith(extension.lower()):
                file_path += extension
            self.output_path.setText(file_path)
    
    def export_structure(self):
        directory = self.dir_path.text()
        output_file = self.output_path.text()
        
        if not directory or not output_file:
            QMessageBox.warning(self, tr("Errore"), tr("Seleziona directory e file di output."))
            return
        
        include_files = self.include_files_check.isChecked()
        max_depth = None if self.depth_spin.value() == 0 else self.depth_spin.value()
        indent_style = self.indent_style_combo.currentData()
        
        selected_format = self.format_combo.currentText()
        output_path = Path(output_file)
        
        if selected_format == "TXT" and output_path.suffix.lower() != ".txt":
            output_file = str(output_path.with_suffix(".txt"))
        elif selected_format == "HTML" and output_path.suffix.lower() != ".html":
            output_file = str(output_path.with_suffix(".html"))
        elif selected_format == "JSON" and output_path.suffix.lower() != ".json":
            output_file = str(output_path.with_suffix(".json"))
        elif selected_format == "XML" and output_path.suffix.lower() != ".xml":
            output_file = str(output_path.with_suffix(".xml"))
        
        try:
            if selected_format == "TXT":
                success, message = self.exporter.export_structure(
                    directory, output_file, include_files, max_depth, indent_style
                )
            elif selected_format == "HTML":
                success, message = self.exporter.export_structure_html(
                    directory, output_file, include_files, max_depth, indent_style
                )
            elif selected_format == "JSON":
                success, message = self.exporter.export_structure_json(
                    directory, output_file, include_files, max_depth
                )
            elif selected_format == "XML":
                success, message = self.exporter.export_structure_xml(
                    directory, output_file, include_files, max_depth
                )
            
            self.output_path.setText(output_file)
            
            if success:
                QMessageBox.information(self, tr("Esportazione completata"), message)
                self.window().statusBar.showMessage(message, 5000)
            else:
                QMessageBox.warning(self, tr("Errore durante l'esportazione"), message)
                
        except Exception as e:
            error_message = tr("Errore durante l'esportazione:") + f" {e}"
            QMessageBox.critical(self, tr("Errore"), error_message)
    
    def load_tree_structure(self):
        """Carica la struttura delle directory nell'albero usando lazy loading"""
        directory = self.dir_path.text()
        if not directory:
            QMessageBox.warning(self, tr("Errore"), tr("Seleziona prima una directory."))
            return

        self.tree_widget.clear()
        
        root_path = Path(directory)
        self.root_item = QTreeWidgetItem(self.tree_widget)
        self.root_item.setText(0, root_path.name)
        self.root_item.setText(1, tr("Directory"))
        self.root_item.setText(2, str(root_path))
        
        self.root_item.setIcon(0, self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon))
        
        font = self.root_item.font(0)
        font.setBold(True)
        self.root_item.setFont(0, font)
        
        self.populate_tree_item(self.root_item, root_path, 0)
        self.root_item.setExpanded(True)
        
        main_window = self.window()
        if main_window and hasattr(main_window, 'statusBar'):
            main_window.statusBar.showMessage(tr("Struttura caricata:") + f" {directory}")
    
    def populate_tree_item(self, parent_item, path, current_depth=0):
        """Popola un elemento dell'albero con i suoi figli diretti"""
        while parent_item.childCount() > 0:
            parent_item.removeChild(parent_item.child(0))
        
        max_depth = None if self.depth_spin.value() == 0 else self.depth_spin.value()
        if max_depth is not None and current_depth >= max_depth:
            return
        
        apply_filters = self.apply_filters_check.isChecked()
        
        try:
            entries = sorted(path.iterdir(), key=lambda e: (not e.is_dir(), e.name.lower()))
            
            for entry in entries:
                if apply_filters and entry.is_dir() and self.filter_manager.is_excluded_dir(entry.name):
                    continue
                    
                if entry.is_file():
                    if not self.show_files_check.isChecked():
                        continue
                    if apply_filters and not self.filter_manager.is_included_file(entry):
                        continue
                
                item = QTreeWidgetItem(parent_item)
                item.setText(0, entry.name)
                item.setText(2, str(entry))
                
                if entry.is_dir():
                    item.setText(1, tr("Directory"))
                    item.setIcon(0, self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon))
                    
                    if self.directory_has_content(entry, apply_filters):
                        temp_item = QTreeWidgetItem(item)
                        temp_item.setText(0, "...")
                        temp_item.setText(1, tr("Caricamento"))
                        temp_item.setForeground(0, QColor(128, 128, 128))
                else:
                    item.setText(1, tr("File"))
                    item.setIcon(0, self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon))
    
        except PermissionError:
            error_item = QTreeWidgetItem(parent_item)
            error_item.setText(0, tr("Accesso negato"))
            error_item.setText(1, tr("Errore"))
            error_item.setForeground(0, QColor(255, 0, 0))
    
    def directory_has_content(self, directory_path, apply_filters):
        """Verifica se una directory ha contenuti visibili"""
        try:
            for entry in directory_path.iterdir():
                if entry.is_dir():
                    if not (apply_filters and self.filter_manager.is_excluded_dir(entry.name)):
                        return True
                elif self.show_files_check.isChecked():
                    if not (apply_filters and not self.filter_manager.is_included_file(entry)):
                        return True
        except (PermissionError, OSError):
            pass
        return False
    
    def on_item_expanded(self, item):
        """Gestisce l'espansione di un elemento"""
        if (item.childCount() == 1 and 
            item.child(0).text(0) == "..." and 
            item.child(0).text(1) == tr("Caricamento")):
            
            path = Path(item.text(2))
            
            current_depth = 0
            parent = item.parent()
            while parent:
                current_depth += 1
                parent = parent.parent()
            
            self.populate_tree_item(item, path, current_depth)
    
    def reload_tree_structure(self):
        """Ricarica la struttura dell'albero applicando i filtri correnti"""
        if hasattr(self, 'tree_widget') and self.tree_widget.topLevelItemCount() > 0:
            self.load_tree_structure()
    
    def filter_tree_items(self):
        """Filtra gli elementi dell'albero in base al testo di ricerca"""
        search_text = self.search_input.text().lower()
        
        def set_item_visible(item, visible):
            item.setHidden(not visible)
        
        def search_in_item(item):
            if not search_text:
                set_item_visible(item, True)
                for i in range(item.childCount()):
                    search_in_item(item.child(i))
                return True
            
            if search_text in item.text(0).lower():
                set_item_visible(item, True)
                parent = item.parent()
                while parent:
                    set_item_visible(parent, True)
                    parent = parent.parent()
                
                for i in range(item.childCount()):
                    set_item_visible(item.child(i), True)
                
                return True
            
            match_in_children = False
            for i in range(item.childCount()):
                if search_in_item(item.child(i)):
                    match_in_children = True
            
            set_item_visible(item, match_in_children)
            return match_in_children
        
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
        if hasattr(self, 'show_files_check'):
            self.show_files_check.setChecked(self.include_files_check.isChecked())
            self.reload_tree_structure()
    
    def save_settings(self):
        """Salva le impostazioni della scheda"""
        self.settings.setValue("dir_path", self.dir_path.text())
        self.settings.setValue("output_path", self.output_path.text())
        self.settings.setValue("format", self.format_combo.currentText())
        self.settings.setValue("include_files", self.include_files_check.isChecked())
        self.settings.setValue("max_depth", self.depth_spin.value())
        self.settings.setValue("indent_style", self.indent_style_combo.currentData())
    
    def load_settings(self):
        """Carica le impostazioni della scheda"""
        self.dir_path.setText(self.settings.value("dir_path", ""))
        self.output_path.setText(self.settings.value("output_path", ""))
        
        format_text = self.settings.value("format", "TXT")
        index = self.format_combo.findText(format_text)
        if index >= 0:
            self.format_combo.setCurrentIndex(index)
            
        self.include_files_check.setChecked(self.settings.value("include_files", True, type=bool))
        self.depth_spin.setValue(self.settings.value("max_depth", 0, type=int))
        
        # Carica lo stile di indentazione
        saved_style = self.settings.value("indent_style", "spaces")
        for i in range(self.indent_style_combo.count()):
            if self.indent_style_combo.itemData(i) == saved_style:
                self.indent_style_combo.setCurrentIndex(i)
                break
        
        directory_path = self.dir_path.text()
        if directory_path:
            self.load_tree_structure()
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Gestisce l'evento di inizio trascinamento"""
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                if Path(path).is_dir():
                    self.setStyleSheet("QGroupBox[title=\"" + tr("Selezione Directory") + "\"] { border: 2px dashed #0066cc; background-color: #e6f0ff; }")
                    event.acceptProposedAction()
                    return
        event.ignore()
    
    def dragLeaveEvent(self, event):
        """Gestisce l'uscita del cursore durante il trascinamento"""
        self.setStyleSheet("")
        event.accept()

    def dragMoveEvent(self, event):
        """Gestisce l'evento di movimento durante il trascinamento"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        """Gestisce l'evento di rilascio"""
        self.setStyleSheet("")
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                if Path(path).is_dir():
                    self.dir_path.setText(path)
                    self.load_tree_structure()
                    self.tree_widget.setFocus()
                    event.acceptProposedAction()
                    self.window().statusBar.showMessage(tr("Directory caricata:") + f" {path}", 3000)
                    return
        event.ignore()