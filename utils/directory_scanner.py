from PyQt6.QtCore import QThread, pyqtSignal
from pathlib import Path
import time
import os

class DirectoryScannerThread(QThread):
    # Segnali per comunicare con l'interfaccia
    progress_updated = pyqtSignal(int)  # Aggiornamento percentuale
    status_updated = pyqtSignal(str)    # Messaggio di stato
    directory_scanned = pyqtSignal(object, object)  # Cartella scansionata e lista degli elementi
    scan_completed = pyqtSignal()       # Scansione completata
    scan_canceled = pyqtSignal()        # Scansione annullata
    scan_error = pyqtSignal(str)        # Errore durante la scansione
    
    def __init__(self, root_dir, filter_manager, include_files=True, apply_filters=True, max_depth=None):
        super().__init__()
        self.root_dir = Path(root_dir)
        self.filter_manager = filter_manager
        self.include_files = include_files
        self.apply_filters = apply_filters
        self.max_depth = max_depth
        self.canceled = False
        
        self.total_items = 0
        self.scanned_items = 0
    
    def run(self):
        """Esegue la scansione della directory"""
        try:
            # Prima scansione per contare gli elementi
            self.status_updated.emit("Conteggio elementi...")
            self.count_items(self.root_dir)
            
            if self.canceled:
                self.scan_canceled.emit()
                return
            
            # Scansione principale
            self.status_updated.emit("Scansione in corso...")
            self.scanned_items = 0
            self.scan_directory(self.root_dir, 0)
            
            if not self.canceled:
                self.progress_updated.emit(100)
                self.status_updated.emit("Scansione completata")
                self.scan_completed.emit()
            else:
                self.scan_canceled.emit()
        
        except Exception as e:
            self.scan_error.emit(str(e))
    
    def count_items(self, path, depth=0):
        """Conta in modo approssimativo quanti elementi ci sono da scansionare"""
        if self.canceled:
            return
        
        if self.max_depth is not None and depth > self.max_depth:
            return
            
        try:
            # Incrementiamo per la directory corrente
            self.total_items += 1
            
            # Scansioniamo i figli
            for entry in path.iterdir():
                if self.canceled:
                    return
                    
                if entry.is_dir():
                    if not (self.apply_filters and self.filter_manager.is_excluded_dir(entry.name)):
                        self.count_items(entry, depth + 1)
                elif self.include_files:
                    if not (self.apply_filters and not self.filter_manager.is_included_file(entry)):
                        self.total_items += 1
        except (PermissionError, OSError):
            pass
    
    def scan_directory(self, path, depth=0):
        """Esegue la scansione effettiva e invia i risultati"""
        if self.canceled:
            return
            
        if self.max_depth is not None and depth > self.max_depth:
            return
            
        try:
            # Incrementiamo il contatore e aggiorniamo il progresso
            self.scanned_items += 1
            progress = int(min(100, (self.scanned_items / max(1, self.total_items)) * 100))
            self.progress_updated.emit(progress)
            
            # Otteniamo la lista degli elementi
            entries = []
            
            for entry in sorted(path.iterdir(), key=lambda e: (not e.is_dir(), e.name.lower())):
                if self.canceled:
                    return
                    
                if entry.is_dir():
                    if not (self.apply_filters and self.filter_manager.is_excluded_dir(entry.name)):
                        entries.append((entry, True))  # True indica che è una directory
                        self.scan_directory(entry, depth + 1)
                elif self.include_files:
                    if not (self.apply_filters and not self.filter_manager.is_included_file(entry)):
                        entries.append((entry, False))  # False indica che è un file
                        self.scanned_items += 1
                        
                        # Aggiorniamo il progresso
                        if self.scanned_items % 10 == 0:  # Aggiorna ogni 10 elementi per evitare troppi aggiornamenti
                            progress = int(min(100, (self.scanned_items / max(1, self.total_items)) * 100))
                            self.progress_updated.emit(progress)
            
            # Emettiamo il segnale con i risultati
            self.directory_scanned.emit(path, entries)
            
        except (PermissionError, OSError) as e:
            self.directory_scanned.emit(path, [])
    
    def cancel(self):
        """Annulla la scansione"""
        self.canceled = True