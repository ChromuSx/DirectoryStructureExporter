import os
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt

class ResourceManager:
    """Gestisce il caricamento delle risorse dell'applicazione"""
    
    _instance = None
    _logo_icon = None
    _logo_pixmap = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.logo_paths = [
                "assets/logo.png",
                "assets/logo.ico",
                "logo.png",
                "assets/logo_small.png",
                "assets/icon.png"
            ]
            self.initialized = True
    
    def get_logo_icon(self):
        """Restituisce l'icona del logo come QIcon"""
        if self._logo_icon is None:
            self._logo_icon = self._load_logo_icon()
        return self._logo_icon
    
    def get_logo_pixmap(self, size=None):
        """Restituisce il logo come QPixmap, opzionalmente ridimensionato"""
        if self._logo_pixmap is None:
            self._logo_pixmap = self._load_logo_pixmap()
        
        if size and not self._logo_pixmap.isNull():
            return self._logo_pixmap.scaled(
                size[0], size[1],
                aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,
                transformMode=Qt.TransformationMode.SmoothTransformation
            )
        
        return self._logo_pixmap
    
    def _load_logo_icon(self):
        """Carica l'icona del logo"""
        for path in self.logo_paths:
            if os.path.exists(path):
                try:
                    icon = QIcon(path)
                    if not icon.isNull():
                        return icon
                except Exception as e:
                    print(f"Errore caricamento icona {path}: {e}")
                    continue
        
        # Fallback: crea un'icona vuota
        return QIcon()
    
    def _load_logo_pixmap(self):
        """Carica il logo come pixmap"""
        for path in self.logo_paths:
            if os.path.exists(path):
                try:
                    pixmap = QPixmap(path)
                    if not pixmap.isNull():
                        return pixmap
                except Exception as e:
                    print(f"Errore caricamento pixmap {path}: {e}")
                    continue
        
        # Fallback: pixmap vuoto
        return QPixmap()
    
    def has_logo(self):
        """Verifica se è presente un logo valido"""
        return not self.get_logo_icon().isNull()

# Istanza globale per facilità d'uso
resource_manager = ResourceManager()