#!/usr/bin/env python3
"""
Script per generare e gestire i file di traduzione dell'applicazione
"""

import os
import sys
import subprocess
import json
import re
from pathlib import Path

class TranslationManager:
    """Gestisce le traduzioni dell'applicazione"""
    
    def __init__(self):
        self.app = None  # Verrà impostata successivamente
        self.translator = None
        self.current_language = 'it'  # Default italiano
        self.translations_dir = 'translations'
        self.settings = None  # Verrà impostata quando l'app sarà disponibile
        self.fallback_translations = {}
        
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
        
        # Carica la lingua salvata ora che tutto è inizializzato
        self.load_saved_language()
    
    def get_available_languages(self):
        """Restituisce il dizionario delle lingue disponibili"""
        return self.available_languages
    
    def get_current_language(self):
        """Restituisce il codice della lingua corrente"""
        return self.current_language
    
    def get_current_language_name(self):
        """Restituisce il nome della lingua corrente"""
        return self.available_languages.get(self.current_language, 'Italiano')
    
    def load_saved_language(self):
        """Carica la lingua salvata nelle impostazioni"""
        if not self.settings:
            return
            
        saved_lang = self.settings.value("language", "it")
        if saved_lang in self.available_languages:
            self.current_language = saved_lang
        self.load_translation(self.current_language)
    
    def save_language(self, language_code):
        """Salva la lingua corrente nelle impostazioni"""
        if self.settings:
            self.settings.setValue("language", language_code)
    
    def load_translation(self, language_code):
        """Carica una traduzione specifica"""
        if language_code == 'it':
            # Italiano è la lingua di default, rimuovi traduttore
            if self.translator and self.app:
                self.app.removeTranslator(self.translator)
            self.current_language = language_code
            return True
        
        translation_file = os.path.join(self.translations_dir, f"app_{language_code}.qm")
        
        if os.path.exists(translation_file) and self.app:
            # Rimuovi il traduttore precedente
            if self.translator:
                self.app.removeTranslator(self.translator)
            
            # Carica il nuovo traduttore
            self.translator = QTranslator()
            if self.translator.load(translation_file):
                self.app.installTranslator(self.translator)
                self.current_language = language_code
                return True
        
        # Se il file non esiste o l'app non è pronta, usa le traduzioni di fallback
        return self.load_fallback_translation(language_code)
    
    def load_fallback_translation(self, language_code):
        """Carica traduzioni di fallback da dizionario interno"""
        fallback_file = os.path.join(self.translations_dir, f"fallback_{language_code}.json")
        
        if not os.path.exists(fallback_file):
            self.create_fallback_translation(language_code)
        
        try:
            with open(fallback_file, 'r', encoding='utf-8') as f:
                translations = json.load(f)
            
            self.fallback_translations = translations
            self.current_language = language_code
            print(f"Traduzioni caricate per {language_code}: {len(translations)} stringhe")
            return True
            
        except Exception as e:
            # Usa traduzioni integrate come fallback
            self.fallback_translations = self.get_default_translations(language_code)
            self.current_language = language_code
            print(f"Usando traduzioni integrate per {language_code}: {len(self.fallback_translations)} stringhe")
            return True
    
    def create_fallback_translation(self, language_code):
        """Crea file di traduzione di fallback"""
        translations = self.get_default_translations(language_code)
        
        fallback_file = os.path.join(self.translations_dir, f"fallback_{language_code}.json")
        try:
            with open(fallback_file, 'w', encoding='utf-8') as f:
                json.dump(translations, f, indent=2, ensure_ascii=False)
            print(f"File di fallback creato: {fallback_file}")
            return True
        except Exception as e:
            print(f"Errore creazione fallback {language_code}: {e}")
            return False
    
    def get_default_translations(self, language_code):
        """Restituisce le traduzioni di default per una lingua"""
        # Importiamo le traduzioni dal generatore per evitare duplicazione
        # o le manteniamo qui per non dipendere dal translation_generator
        translations = {
            'en': {
                # Main Window
                'Directory Structure Exporter': 'Directory Structure Exporter',
                'Tema:': 'Theme:',
                'Lingua:': 'Language:',
                'Sistema': 'System',
                'Chiaro': 'Light',
                'Scuro': 'Dark',
                'Pronto': 'Ready',
                
                # Tab names
                'Esportazione': 'Export',
                'Filtri': 'Filters',
                'Configurazione': 'Configuration',
                
                # Export Tab
                'Directory:': 'Directory:',
                'Sfoglia...': 'Browse...',
                'Esporta': 'Export',
                'Errore': 'Error',
                'File:': 'File:',
                'Formato:': 'Format:',
                'Includi file': 'Include files',
                'Mostra file': 'Show files',
                'Cerca:': 'Search:',
                'Nome': 'Name',
                'Tipo': 'Type',
                'Percorso': 'Path',
                'Directory': 'Directory',
                'File': 'File',
            },
            'es': {
                'Directory Structure Exporter': 'Exportador de Estructura de Directorios',
                'Tema:': 'Tema:',
                'Lingua:': 'Idioma:',
                'Sistema': 'Sistema',
                'Chiaro': 'Claro',
                'Scuro': 'Oscuro',
                'Pronto': 'Listo',
                'Esportazione': 'Exportación',
                'Filtri': 'Filtros',
                'Configurazione': 'Configuración',
                'Directory:': 'Directorio:',
                'Sfoglia...': 'Examinar...',
                'Esporta': 'Exportar',
            },
            'fr': {
                'Directory Structure Exporter': 'Exportateur de Structure de Répertoires',
                'Tema:': 'Thème:',
                'Lingua:': 'Langue:',
                'Sistema': 'Système',
                'Chiaro': 'Clair',
                'Scuro': 'Sombre',
                'Pronto': 'Prêt',
                'Esportazione': 'Exportation',
                'Filtri': 'Filtres',
                'Configurazione': 'Configuration',
                'Directory:': 'Répertoire:',
                'Sfoglia...': 'Parcourir...',
                'Esporta': 'Exporter',
            },
            'de': {
                'Directory Structure Exporter': 'Verzeichnisstruktur-Exporteur',
                'Tema:': 'Thema:',
                'Lingua:': 'Sprache:',
                'Sistema': 'System',
                'Chiaro': 'Hell',
                'Scuro': 'Dunkel',
                'Pronto': 'Bereit',
                'Esportazione': 'Export',
                'Filtri': 'Filter',
                'Configurazione': 'Konfiguration',
                'Directory:': 'Verzeichnis:',
                'Sfoglia...': 'Durchsuchen...',
                'Esporta': 'Exportieren',
            }
        }
        
        return translations.get(language_code, {})
    
    def tr(self, text, context=None):
        """Traduce un testo utilizzando il sistema di traduzione corrente"""
        # Debug
        if self.current_language != 'it':
            if hasattr(self, 'fallback_translations') and self.fallback_translations:
                translated = self.fallback_translations.get(text, text)
                if translated != text:
                    # print(f"Tradotto '{text}' -> '{translated}'")  # Uncomment per debug
                    pass
                return translated
            else:
                print(f"Nessuna traduzione di fallback disponibile per {self.current_language}")
        
        return text
    
    def change_language(self, language_code):
        """Cambia la lingua dell'applicazione"""
        print(f"Tentativo di cambio lingua a: {language_code}")
        if language_code in self.available_languages:
            success = self.load_translation(language_code)
            print(f"Risultato caricamento: {success}")
            if success:
                self.save_language(language_code)
                print(f"Lingua cambiata con successo a: {language_code}")
                return True
            else:
                print(f"Errore nel caricamento di {language_code}")
                return False
        else:
            print(f"Lingua {language_code} non supportata")
            return False

# Istanza globale
translation_manager = TranslationManager()

def tr(text, context=None):
    """Funzione di traduzione globale"""
    return translation_manager.tr(text, context)