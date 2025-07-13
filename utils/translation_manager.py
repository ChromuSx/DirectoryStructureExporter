import os
import json
from PyQt6.QtCore import QTranslator, QLocale, QCoreApplication, QSettings
from PyQt6.QtWidgets import QApplication

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
            self.fallback_translations = {}  # Pulisci le traduzioni di fallback
            return True
        
        # Carica traduzioni di fallback per lingue diverse dall'italiano
        return self.load_fallback_translation(language_code)
    
    def load_fallback_translation(self, language_code):
        """Carica traduzioni di fallback da dizionario interno"""
        fallback_file = os.path.join(self.translations_dir, f"fallback_{language_code}.json")
        
        # Se il file non esiste, crealo
        if not os.path.exists(fallback_file):
            print(f"File di traduzione {fallback_file} non trovato, creazione in corso...")
            self.create_fallback_translation(language_code)
        
        try:
            with open(fallback_file, 'r', encoding='utf-8') as f:
                translations = json.load(f)
            
            # Carica le traduzioni in memoria
            self.fallback_translations = translations
            self.current_language = language_code
            
            print(f"Traduzioni caricate per {language_code}: {len(translations)} stringhe")
            return True
        except Exception as e:
            print(f"Errore nel caricamento delle traduzioni per {language_code}: {e}")
            # In caso di errore, mantieni almeno la lingua impostata
            self.current_language = language_code
            self.fallback_translations = {}
            return False
    
    def create_fallback_translation(self, language_code):
        """Crea file di traduzione di fallback"""
        translations = self.get_default_translations(language_code)
        
        fallback_file = os.path.join(self.translations_dir, f"fallback_{language_code}.json")
        try:
            with open(fallback_file, 'w', encoding='utf-8') as f:
                json.dump(translations, f, indent=2, ensure_ascii=False)
            print(f"File di traduzione creato: {fallback_file}")
        except Exception as e:
            print(f"Errore creazione fallback {language_code}: {e}")
    
    def get_default_translations(self, language_code):
        """Restituisce le traduzioni di default per una lingua"""
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
                'Lingua cambiata': 'Language changed',
                'La lingua è stata cambiata. Alcune modifiche potrebbero richiedere il riavvio dell\'applicazione.': 'Language has been changed. Some changes may require restarting the application.',
                'Errore': 'Error',
                'Errore nel caricamento della lingua selezionata.': 'Error loading selected language.',
                'Lingua cambiata in': 'Language changed to',
                
                # Tab names
                'Esportazione': 'Export',
                'Filtri': 'Filters',
                'Configurazione': 'Configuration',
                
                # Export Tab
                'Selezione Directory': 'Directory Selection',
                'Directory:': 'Directory:',
                'Sfoglia...': 'Browse...',
                'Trascina qui una cartella': 'Drag a folder here',
                'File di Output': 'Output File',
                'File:': 'File:',
                'Formato:': 'Format:',
                'Opzioni di esportazione': 'Export Options',
                'Includi file': 'Include files',
                'Profondità massima:': 'Maximum depth:',
                'Illimitata': 'Unlimited',
                'Esporta': 'Export',
                'Struttura Directory': 'Directory Structure',
                'Mostra file': 'Show files',
                'Applica filtri': 'Apply filters',
                'Cerca:': 'Search:',
                'Cerca file o cartelle...': 'Search files or folders...',
                'Nome': 'Name',
                'Tipo': 'Type',
                'Percorso': 'Path',
                'Directory': 'Directory',
                'File': 'File',
                'Caricamento': 'Loading',
                'Accesso negato': 'Access denied',
                
                # Filters
                'Filtri dimensione file': 'File Size Filters',
                'Dimensione minima (bytes):': 'Minimum size (bytes):',
                'Dimensione massima (bytes):': 'Maximum size (bytes):',
                'Illimitato': 'Unlimited',
                'Filtri data creazione': 'Creation Date Filters',
                'Data minima:': 'Minimum date:',
                'Data massima:': 'Maximum date:',
                'Attiva filtro per data di creazione': 'Enable creation date filter',
                'Filtri data modifica': 'Modification Date Filters',
                'Attiva filtro per data di modifica': 'Enable modification date filter',
                'Reimposta filtri predefiniti': 'Reset default filters',
                
                # Configuration
                'Directory escluse': 'Excluded Directories',
                'File esclusi': 'Excluded Files',
                'Estensioni incluse': 'Included Extensions',
                'Preset Configurazioni': 'Configuration Presets',
                'Preset:': 'Preset:',
                '-- Seleziona un preset --': '-- Select a preset --',
                'Salva come nuovo': 'Save as new',
                'Aggiorna selezionato': 'Update selected',
                'Elimina selezionato': 'Delete selected',
                'Percorso File Preset': 'Preset File Path',
                'File preset:': 'Preset file:',
                'Applica': 'Apply',
                'Aggiungi': 'Add',
                'Aggiungi Regex': 'Add Regex',
                'Rimuovi': 'Remove',
                'Salva configurazione': 'Save configuration',
                'Carica configurazione': 'Load configuration',
            },
            'es': {
                # Traduzioni spagnole complete
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
                'Errore': 'Error',
                'File:': 'Archivo:',
                'Formato:': 'Formato:',
                'Includi file': 'Incluir archivos',
                'Mostra file': 'Mostrar archivos',
                'Cerca:': 'Buscar:',
                'Nome': 'Nombre',
                'Tipo': 'Tipo',
                'Percorso': 'Ruta',
                'Directory': 'Directorio',
                'File': 'Archivo',
                'Applica filtri': 'Aplicar filtros',
                'Filtri dimensione file': 'Filtros de Tamaño de Archivo',
                'Directory escluse': 'Directorios Excluidos',
                'File esclusi': 'Archivos Excluidos',
                'Estensioni incluse': 'Extensiones Incluidas',
                'Aggiungi': 'Agregar',
                'Rimuovi': 'Eliminar',
            },
            'fr': {
                # Traduzioni francesi complete
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
                'Errore': 'Erreur',
                'File:': 'Fichier:',
                'Formato:': 'Format:',
                'Includi file': 'Inclure fichiers',
                'Mostra file': 'Afficher fichiers',
                'Cerca:': 'Rechercher:',
                'Nome': 'Nom',
                'Tipo': 'Type',
                'Percorso': 'Chemin',
                'Directory': 'Répertoire',
                'File': 'Fichier',
                'Applica filtri': 'Appliquer filtres',
                'Filtri dimensione file': 'Filtres de Taille de Fichier',
                'Directory escluse': 'Répertoires Exclus',
                'File esclusi': 'Fichiers Exclus',
                'Estensioni incluse': 'Extensions Incluses',
                'Aggiungi': 'Ajouter',
                'Rimuovi': 'Supprimer',
            },
            'de': {
                # Traduzioni tedesche complete
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
                'Errore': 'Fehler',
                'File:': 'Datei:',
                'Formato:': 'Format:',
                'Includi file': 'Dateien einschließen',
                'Mostra file': 'Dateien anzeigen',
                'Cerca:': 'Suchen:',
                'Nome': 'Name',
                'Tipo': 'Typ',
                'Percorso': 'Pfad',
                'Directory': 'Verzeichnis',
                'File': 'Datei',
                'Applica filtri': 'Filter anwenden',
                'Filtri dimensione file': 'Dateigrößen-Filter',
                'Directory escluse': 'Ausgeschlossene Verzeichnisse',
                'File esclusi': 'Ausgeschlossene Dateien',
                'Estensioni incluse': 'Eingeschlossene Erweiterungen',
                'Aggiungi': 'Hinzufügen',
                'Rimuovi': 'Entfernen',
            }
        }
        
        return translations.get(language_code, {})
    
    def tr(self, text, context=None):
        """Traduce un testo utilizzando il sistema di traduzione corrente"""
        # Se la lingua è italiana, restituisci il testo originale
        if self.current_language == 'it':
            return text
            
        # Se abbiamo traduzioni di fallback caricate, usale
        if hasattr(self, 'fallback_translations') and self.fallback_translations:
            translated = self.fallback_translations.get(text, None)
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

# Istanza globale
translation_manager = TranslationManager()

def tr(text, context=None):
    """Funzione di traduzione globale"""
    return translation_manager.tr(text, context)