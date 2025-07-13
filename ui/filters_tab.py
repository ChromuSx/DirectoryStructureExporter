from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QLineEdit, QComboBox, QListWidget, QGroupBox, QCheckBox, 
                            QDateTimeEdit, QSpinBox, QMessageBox)
from PyQt6.QtCore import Qt, QDateTime
import datetime

class FiltersTab(QWidget):
    def __init__(self, filter_manager, settings):
        super().__init__()
        self.filter_manager = filter_manager
        self.settings = settings
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """Configura l'interfaccia utente della scheda filtri"""
        layout = QVBoxLayout(self)
        
        # Gruppo dimensione file
        size_group = QGroupBox("Filtri dimensione file")
        size_layout = QVBoxLayout()
        
        size_min_layout = QHBoxLayout()
        size_min_layout.addWidget(QLabel("Dimensione minima (bytes):"))
        self.min_size_spin = QSpinBox()
        self.min_size_spin.setRange(0, 1000000000)  # Da 0 a 1 GB
        self.min_size_spin.setValue(0)
        size_min_layout.addWidget(self.min_size_spin)
        
        size_max_layout = QHBoxLayout()
        size_max_layout.addWidget(QLabel("Dimensione massima (bytes):"))
        self.max_size_spin = QSpinBox()
        self.max_size_spin.setRange(0, 1000000000)  # Da 0 a 1 GB
        self.max_size_spin.setValue(0)
        self.max_size_spin.setSpecialValueText("Illimitato")
        size_max_layout.addWidget(self.max_size_spin)
        
        size_layout.addLayout(size_min_layout)
        size_layout.addLayout(size_max_layout)
        size_group.setLayout(size_layout)
        
        # Gruppo data di creazione
        creation_group = QGroupBox("Filtri data creazione")
        creation_layout = QVBoxLayout()
        
        creation_min_layout = QHBoxLayout()
        creation_min_layout.addWidget(QLabel("Data minima:"))
        self.min_creation_date = QDateTimeEdit()
        self.min_creation_date.setCalendarPopup(True)
        self.min_creation_date.setDateTime(QDateTime.currentDateTime().addYears(-1))
        creation_min_layout.addWidget(self.min_creation_date)
        
        creation_max_layout = QHBoxLayout()
        creation_max_layout.addWidget(QLabel("Data massima:"))
        self.max_creation_date = QDateTimeEdit()
        self.max_creation_date.setCalendarPopup(True)
        self.max_creation_date.setDateTime(QDateTime.currentDateTime())
        creation_max_layout.addWidget(self.max_creation_date)
        
        self.use_creation_date = QCheckBox("Attiva filtro per data di creazione")
        
        creation_layout.addWidget(self.use_creation_date)
        creation_layout.addLayout(creation_min_layout)
        creation_layout.addLayout(creation_max_layout)
        creation_group.setLayout(creation_layout)
        
        # Gruppo data di modifica
        modification_group = QGroupBox("Filtri data modifica")
        modification_layout = QVBoxLayout()
        
        modification_min_layout = QHBoxLayout()
        modification_min_layout.addWidget(QLabel("Data minima:"))
        self.min_modification_date = QDateTimeEdit()
        self.min_modification_date.setCalendarPopup(True)
        self.min_modification_date.setDateTime(QDateTime.currentDateTime().addYears(-1))
        modification_min_layout.addWidget(self.min_modification_date)
        
        modification_max_layout = QHBoxLayout()
        modification_max_layout.addWidget(QLabel("Data massima:"))
        self.max_modification_date = QDateTimeEdit()
        self.max_modification_date.setCalendarPopup(True)
        self.max_modification_date.setDateTime(QDateTime.currentDateTime())
        modification_max_layout.addWidget(self.max_modification_date)
        
        self.use_modification_date = QCheckBox("Attiva filtro per data di modifica")
        
        modification_layout.addWidget(self.use_modification_date)
        modification_layout.addLayout(modification_min_layout)
        modification_layout.addLayout(modification_max_layout)
        modification_group.setLayout(modification_layout)
        
        # Pulsanti di azione
        action_layout = QHBoxLayout()
        apply_btn = QPushButton("Applica filtri")
        reset_btn = QPushButton("Reimposta filtri predefiniti")
        
        apply_btn.clicked.connect(self.apply_filters)
        reset_btn.clicked.connect(self.reset_filters)
        
        action_layout.addWidget(apply_btn)
        action_layout.addWidget(reset_btn)
        
        # Aggiungi tutto al layout principale
        layout.addWidget(size_group)
        layout.addWidget(creation_group)
        layout.addWidget(modification_group)
        layout.addLayout(action_layout)
        layout.addStretch(1)  # Spazio flessibile in fondo

    def retranslate_ui(self):
        """Aggiorna tutte le traduzioni dell'interfaccia"""
        from utils.translation_manager import tr
        
        # Aggiorna i titoli dei gruppi
        for i in range(self.layout().count()):
            item = self.layout().itemAt(i)
            if item and item.widget() and hasattr(item.widget(), 'setTitle'):
                widget = item.widget()
                title = widget.title().lower()
                if 'dimensione' in title or 'size' in title:
                    widget.setTitle(tr("Filtri dimensione file"))
                elif 'creazione' in title or 'creation' in title:
                    widget.setTitle(tr("Filtri data creazione"))
                elif 'modifica' in title or 'modification' in title:
                    widget.setTitle(tr("Filtri data modifica"))
        
        # Aggiorna le etichette
        self._update_labels_in_widget(self)
        
        # Aggiorna i pulsanti
        self._update_buttons_in_widget(self)
        
        # Aggiorna i checkbox
        self._update_checkboxes_in_widget(self)
        
        # Aggiorna lo special value text dello spinbox
        if hasattr(self, 'max_size_spin'):
            self.max_size_spin.setSpecialValueText(tr("Illimitato"))

    def _update_labels_in_widget(self, widget):
        """Aggiorna ricorsivamente le etichette in un widget"""
        from utils.translation_manager import tr
        from PyQt6.QtWidgets import QLabel
        
        for child in widget.findChildren(QLabel):
            text = child.text().lower()
            if 'dimensione minima' in text or 'minimum size' in text:
                child.setText(tr("Dimensione minima (bytes):"))
            elif 'dimensione massima' in text or 'maximum size' in text:
                child.setText(tr("Dimensione massima (bytes):"))
            elif 'data minima' in text or 'minimum date' in text:
                child.setText(tr("Data minima:"))
            elif 'data massima' in text or 'maximum date' in text:
                child.setText(tr("Data massima:"))

    def _update_buttons_in_widget(self, widget):
        """Aggiorna ricorsivamente i pulsanti in un widget"""
        from utils.translation_manager import tr
        from PyQt6.QtWidgets import QPushButton
        
        for child in widget.findChildren(QPushButton):
            text = child.text().lower()
            if 'applica filtri' in text or 'apply filters' in text:
                child.setText(tr("Applica filtri"))
            elif 'reimposta' in text or 'reset' in text:
                child.setText(tr("Reimposta filtri predefiniti"))

    def _update_checkboxes_in_widget(self, widget):
        """Aggiorna ricorsivamente i checkbox in un widget"""
        from utils.translation_manager import tr
        from PyQt6.QtWidgets import QCheckBox
        
        for child in widget.findChildren(QCheckBox):
            text = child.text().lower()
            if 'creazione' in text or 'creation' in text:
                child.setText(tr("Attiva filtro per data di creazione"))
            elif 'modifica' in text or 'modification' in text:
                child.setText(tr("Attiva filtro per data di modifica"))

    def update_filters_ui(self):
        """Aggiorna l'interfaccia utente con i valori attuali dei filtri"""
        # Aggiorna i controlli di dimensione file
        self.min_size_spin.setValue(self.filter_manager.min_file_size)
        
        if self.filter_manager.max_file_size == float('inf'):
            self.max_size_spin.setValue(0)  # 0 è il valore "Illimitato"
        else:
            self.max_size_spin.setValue(int(self.filter_manager.max_file_size))
        
        # Aggiorna i controlli di data
        if self.filter_manager.min_creation_date is not None:
            self.use_creation_date.setChecked(True)
            date_time = QDateTime.fromSecsSinceEpoch(self.filter_manager.min_creation_date)
            self.min_creation_date.setDateTime(date_time)
        else:
            self.use_creation_date.setChecked(False)
        
        if self.filter_manager.max_creation_date is not None:
            date_time = QDateTime.fromSecsSinceEpoch(self.filter_manager.max_creation_date)
            self.max_creation_date.setDateTime(date_time)
        
        if self.filter_manager.min_modification_date is not None:
            self.use_modification_date.setChecked(True)
            date_time = QDateTime.fromSecsSinceEpoch(self.filter_manager.min_modification_date)
            self.min_modification_date.setDateTime(date_time)
        else:
            self.use_modification_date.setChecked(False)
        
        if self.filter_manager.max_modification_date is not None:
            date_time = QDateTime.fromSecsSinceEpoch(self.filter_manager.max_modification_date)
            self.max_modification_date.setDateTime(date_time)
    
    def apply_filters(self):
        """Applica i filtri impostati"""
        # Imposta i filtri di dimensione
        min_size = self.min_size_spin.value()
        max_size = self.max_size_spin.value()
        self.filter_manager.set_size_filters(min_size, max_size)
        
        # Imposta i filtri di data di creazione
        if self.use_creation_date.isChecked():
            min_creation = self.min_creation_date.dateTime().toSecsSinceEpoch()
            max_creation = self.max_creation_date.dateTime().toSecsSinceEpoch()
            self.filter_manager.set_creation_date_filters(min_creation, max_creation)
        else:
            self.filter_manager.set_creation_date_filters(None, None)
        
        # Imposta i filtri di data di modifica
        if self.use_modification_date.isChecked():
            min_modification = self.min_modification_date.dateTime().toSecsSinceEpoch()
            max_modification = self.max_modification_date.dateTime().toSecsSinceEpoch()
            self.filter_manager.set_modification_date_filters(min_modification, max_modification)
        else:
            self.filter_manager.set_modification_date_filters(None, None)
        
        # Aggiorna la vista principale se necessario
        # Se nella scheda di esportazione c'è già un albero caricato, potremmo volerlo aggiornare
        if hasattr(self.window(), 'export_tab') and self.window().export_tab:
            self.window().export_tab.reload_tree_structure()
        
        # Mostra un messaggio di conferma
        QMessageBox.information(self, "Filtri applicati", "I filtri sono stati applicati con successo.")
        # Aggiorna anche la statusbar
        self.window().statusBar.showMessage("Filtri applicati con successo", 3000)
    
    def reset_filters(self):
        """Reimposta i filtri ai valori predefiniti"""
        # Reimposta i filtri nel FilterManager
        self.filter_manager.reset_filters()
        
        # Aggiorna l'interfaccia
        self.min_size_spin.setValue(0)
        self.max_size_spin.setValue(0)
        self.use_creation_date.setChecked(False)
        self.use_modification_date.setChecked(False)
        
        # Aggiorna la vista principale se necessario
        if hasattr(self.window(), 'export_tab') and self.window().export_tab:
            self.window().export_tab.reload_tree_structure()
        
        # Mostra un messaggio di conferma
        QMessageBox.information(self, "Filtri reimpostati", "I filtri sono stati reimpostati ai valori predefiniti.")
        # Aggiorna anche la statusbar
        self.window().statusBar.showMessage("Filtri reimpostati", 3000)
    
    def save_settings(self):
        """Salva le impostazioni dei filtri"""
        # Salva le impostazioni di dimensione
        self.settings.setValue("filters_min_size", self.min_size_spin.value())
        self.settings.setValue("filters_max_size", self.max_size_spin.value())
        
        # Salva le impostazioni di data
        self.settings.setValue("filters_use_creation_date", self.use_creation_date.isChecked())
        self.settings.setValue("filters_min_creation_date", self.min_creation_date.dateTime())
        self.settings.setValue("filters_max_creation_date", self.max_creation_date.dateTime())
        
        self.settings.setValue("filters_use_modification_date", self.use_modification_date.isChecked())
        self.settings.setValue("filters_min_modification_date", self.min_modification_date.dateTime())
        self.settings.setValue("filters_max_modification_date", self.max_modification_date.dateTime())
    
    def load_settings(self):
        """Carica le impostazioni dei filtri"""
        # Carica le impostazioni di dimensione
        min_size = self.settings.value("filters_min_size", 0, type=int)
        max_size = self.settings.value("filters_max_size", 0, type=int)
        self.min_size_spin.setValue(min_size)
        self.max_size_spin.setValue(max_size)
        
        # Carica le impostazioni di data
        use_creation = self.settings.value("filters_use_creation_date", False, type=bool)
        self.use_creation_date.setChecked(use_creation)
        
        min_creation_date = self.settings.value("filters_min_creation_date")
        if min_creation_date:
            self.min_creation_date.setDateTime(min_creation_date)
        
        max_creation_date = self.settings.value("filters_max_creation_date")
        if max_creation_date:
            self.max_creation_date.setDateTime(max_creation_date)
        
        use_modification = self.settings.value("filters_use_modification_date", False, type=bool)
        self.use_modification_date.setChecked(use_modification)
        
        min_modification_date = self.settings.value("filters_min_modification_date")
        if min_modification_date:
            self.min_modification_date.setDateTime(min_modification_date)
        
        max_modification_date = self.settings.value("filters_max_modification_date")
        if max_modification_date:
            self.max_modification_date.setDateTime(max_modification_date)