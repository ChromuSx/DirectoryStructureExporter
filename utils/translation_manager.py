import os
import json
from PyQt6.QtCore import QObject, pyqtSignal, QSettings
from typing import Dict, Optional, Set

class TranslationManager(QObject):
    """Gestisce le traduzioni dell'applicazione in modo semplificato"""
    
    # Segnale emesso quando la lingua cambia
    language_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.current_language = 'it'  # Default italiano
        self.translations_dir = 'translations'
        self.current_translations: Dict[str, str] = {}
        self.settings: Optional[QSettings] = None
        
        # Lingue disponibili
        self.available_languages = {
            'it': 'Italiano',
            'en': 'English', 
            'es': 'Español',
            'fr': 'Français',
            'de': 'Deutsch'
        }
        
        # Cache per evitare ricaricamenti
        self._translation_cache: Dict[str, Dict[str, str]] = {}
        
        # Set di stringhe mancanti per debugging
        self._missing_translations: Set[str] = set()
        
        os.makedirs(self.translations_dir, exist_ok=True)
    
    def initialize(self, settings: QSettings) -> None:
        """Inizializza il manager con le impostazioni"""
        self.settings = settings
        self._create_translation_files_if_needed()
        
        # Carica lingua salvata o sistema
        saved_language = settings.value("language", None)
        if saved_language and saved_language in self.available_languages:
            self.load_language(saved_language)
        else:
            # Rileva lingua sistema o default
            from PyQt6.QtCore import QLocale
            system_lang = QLocale.system().name()[:2]
            target_lang = system_lang if system_lang in self.available_languages else 'it'
            self.load_language(target_lang)
    
    def get_available_languages(self) -> Dict[str, str]:
        return self.available_languages.copy()
    
    def get_current_language(self) -> str:
        return self.current_language
    
    def get_current_language_name(self) -> str:
        return self.available_languages.get(self.current_language, 'Italiano')
    
    def load_language(self, language_code: str) -> bool:
        """Carica una lingua specifica"""
        if language_code not in self.available_languages:
            return False
        
        old_language = self.current_language
        self.current_language = language_code
        
        if language_code == 'it':
            # Italiano è default, nessuna traduzione necessaria
            self.current_translations = {}
            self._missing_translations.clear()
        else:
            # Carica da cache o file
            if language_code in self._translation_cache:
                self.current_translations = self._translation_cache[language_code]
            else:
                success = self._load_from_file(language_code)
                if not success:
                    self.current_language = old_language
                    return False
        
        # Salva impostazione e emetti segnale
        if self.settings:
            self.settings.setValue("language", language_code)
        
        if old_language != language_code:
            self.language_changed.emit(language_code)
        
        return True
    
    def translate(self, text: str, context: Optional[str] = None) -> str:
        """Traduce un testo"""
        if self.current_language == 'it' or not text:
            return text
        
        # Cerca traduzione
        translation = self.current_translations.get(text)
        if translation:
            return translation
        
        # Traduzione mancante - log per debugging
        if text not in self._missing_translations:
            self._missing_translations.add(text)
            print(f"Traduzione mancante [{self.current_language}]: '{text}'")
        
        return text  # Fallback a italiano
    
    def _load_from_file(self, language_code: str) -> bool:
        """Carica traduzioni da file JSON"""
        json_file = os.path.join(self.translations_dir, f"{language_code}.json")
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                translations = json.load(f)
            
            if not isinstance(translations, dict):
                raise ValueError("Il file deve contenere un oggetto JSON")
            
            # Cache e imposta traduzioni correnti
            self._translation_cache[language_code] = translations
            self.current_translations = translations
            
            print(f"Caricate {len(translations)} traduzioni per {language_code}")
            return True
            
        except Exception as e:
            print(f"Errore caricamento traduzioni {language_code}: {e}")
            self.current_translations = {}
            return False
    
    def _create_translation_files_if_needed(self) -> None:
        """Crea file JSON vuoti se non esistono"""
        for lang_code in self.available_languages.keys():
            if lang_code == 'it':
                continue
                
            json_file = os.path.join(self.translations_dir, f"{lang_code}.json")
            if not os.path.exists(json_file):
                try:
                    with open(json_file, 'w', encoding='utf-8') as f:
                        json.dump({}, f, indent=2, ensure_ascii=False)
                    print(f"Creato file traduzione: {json_file}")
                except Exception as e:
                    print(f"Errore creazione {json_file}: {e}")
    
    def get_missing_translations(self) -> Set[str]:
        """Restituisce le traduzioni mancanti per debug"""
        return self._missing_translations.copy()
    
    def add_translation(self, italian_text: str, translated_text: str, 
                       language_code: Optional[str] = None) -> bool:
        """Aggiunge una traduzione (utile per tool di traduzione)"""
        target_lang = language_code or self.current_language
        
        if target_lang == 'it':
            return True  # Non serve tradurre l'italiano
            
        json_file = os.path.join(self.translations_dir, f"{target_lang}.json")
        
        try:
            # Carica esistenti
            translations = {}
            if os.path.exists(json_file):
                with open(json_file, 'r', encoding='utf-8') as f:
                    translations = json.load(f)
            
            # Aggiungi nuova
            translations[italian_text] = translated_text
            
            # Salva
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(translations, f, indent=2, ensure_ascii=False)
            
            # Aggiorna cache e traduzioni correnti se necessario
            self._translation_cache[target_lang] = translations
            if target_lang == self.current_language:
                self.current_translations = translations
                if italian_text in self._missing_translations:
                    self._missing_translations.remove(italian_text)
            
            return True
            
        except Exception as e:
            print(f"Errore aggiunta traduzione: {e}")
            return False

# Istanza globale
translation_manager = TranslationManager()

def tr(text: str, context: Optional[str] = None) -> str:
    """Funzione di traduzione globale semplificata"""
    return translation_manager.translate(text, context)