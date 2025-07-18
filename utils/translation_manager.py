import os
import json
from PyQt6.QtCore import QTranslator, QLocale, QCoreApplication, QSettings
from PyQt6.QtWidgets import QApplication

class TranslationManager:
    """Gestisce le traduzioni dell'applicazione"""
    
    def __init__(self):
        self.app = None
        self.translator = None
        self.current_language = 'it'  # Default italiano
        self.translations_dir = 'translations'
        self.settings = None
        self.current_translations = {}
        
        # Dizionario delle lingue disponibili
        self.available_languages = {
            'it': 'Italiano',
            'en': 'English',
            'es': 'Español', 
            'fr': 'Français',
            'de': 'Deutsch'
        }
        
        # Crea la directory delle traduzioni se non esiste
        os.makedirs(self.translations_dir, exist_ok=True)
    
    def initialize(self, app):
        """Inizializza il manager con l'applicazione Qt"""
        self.app = app
        self.translator = QTranslator()
        self.settings = QSettings()
        
        # Crea i file JSON vuoti se non esistono
        self._create_empty_translation_files()
    
    def get_available_languages(self):
        """Restituisce il dizionario delle lingue disponibili"""
        return self.available_languages
    
    def get_current_language(self):
        """Restituisce il codice della lingua corrente"""
        return self.current_language
    
    def get_current_language_name(self):
        """Restituisce il nome della lingua corrente"""
        return self.available_languages.get(self.current_language, 'Italiano')
    
    def save_language(self, language_code):
        """Salva la lingua corrente nelle impostazioni"""
        if self.settings:
            self.settings.setValue("language", language_code)
    
    def load_translation(self, language_code):
        """Carica una traduzione specifica dal file JSON"""
        if language_code == 'it':
            # Italiano è la lingua di default, pulisci le traduzioni
            self.current_translations = {}
            self.current_language = language_code
            return True
        
        # Carica traduzioni dal file JSON
        return self._load_translation_from_json(language_code)
    
    def _load_translation_from_json(self, language_code):
        """Carica traduzioni da file JSON"""
        json_file = os.path.join(self.translations_dir, f"{language_code}.json")
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                translations = json.load(f)
            
            # Carica le traduzioni in memoria
            self.current_translations = translations
            self.current_language = language_code
            
            print(f"Traduzioni caricate per {language_code}: {len(translations)} stringhe")
            return True
        except Exception as e:
            print(f"Errore nel caricamento delle traduzioni per {language_code}: {e}")
            # In caso di errore, mantieni almeno la lingua impostata
            self.current_language = language_code
            self.current_translations = {}
            return False
    
    def _create_empty_translation_files(self):
        """Crea file JSON vuoti per le lingue se non esistono"""
        for lang_code in self.available_languages.keys():
            if lang_code != 'it':  # Skip italiano (default)
                json_file = os.path.join(self.translations_dir, f"{lang_code}.json")
                
                # Se il file non esiste, crealo vuoto
                if not os.path.exists(json_file):
                    try:
                        with open(json_file, 'w', encoding='utf-8') as f:
                            json.dump({}, f, indent=2, ensure_ascii=False)
                        print(f"File di traduzione vuoto creato: {json_file}")
                    except Exception as e:
                        print(f"Errore creazione file {json_file}: {e}")
    
    def tr(self, text, context=None):
        """Traduce un testo utilizzando le traduzioni caricate dal JSON"""
        # Se la lingua è italiana, restituisci il testo originale
        if self.current_language == 'it':
            return text
            
        # Se abbiamo traduzioni caricate dal JSON, usale
        if self.current_translations:
            translated = self.current_translations.get(text, None)
            if translated:
                return translated
        
        # Fallback: restituisci il testo originale se non trovato
        return text
    
    def change_language(self, language_code):
        """Cambia la lingua dell'applicazione"""
        if language_code in self.available_languages:
            success = self.load_translation(language_code)
            if success:
                self.save_language(language_code)
                print(f"Lingua cambiata con successo a: {self.get_current_language_name()}")
                return True
            else:
                print(f"Errore nel cambio lingua a: {language_code}")
        return False
    
    def add_translation(self, language_code, italian_text, translated_text):
        """Aggiunge una traduzione al file JSON"""
        if language_code == 'it':
            return  # Non serve tradurre l'italiano
            
        json_file = os.path.join(self.translations_dir, f"{language_code}.json")
        
        # Carica traduzioni esistenti
        translations = {}
        if os.path.exists(json_file):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    translations = json.load(f)
            except:
                pass
        
        # Aggiungi nuova traduzione
        translations[italian_text] = translated_text
        
        # Salva file aggiornato
        try:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(translations, f, indent=2, ensure_ascii=False)
            
            # Se questa è la lingua corrente, aggiorna anche le traduzioni in memoria
            if language_code == self.current_language:
                self.current_translations[italian_text] = translated_text
                
            return True
        except Exception as e:
            print(f"Errore aggiungendo traduzione: {e}")
            return False
    
    def get_missing_translations(self, language_code, italian_texts):
        """Restituisce le traduzioni mancanti per una lingua"""
        if language_code == 'it':
            return []
            
        json_file = os.path.join(self.translations_dir, f"{language_code}.json")
        
        existing_translations = {}
        if os.path.exists(json_file):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    existing_translations = json.load(f)
            except:
                pass
        
        missing = []
        for text in italian_texts:
            if text not in existing_translations:
                missing.append(text)
        
        return missing
    
    def reload_translations(self):
        """Ricarica le traduzioni dal file JSON corrente"""
        if self.current_language != 'it':
            self._load_translation_from_json(self.current_language)

# Istanza globale
translation_manager = TranslationManager()

def tr(text, context=None):
    """Funzione di traduzione globale"""
    return translation_manager.tr(text, context)