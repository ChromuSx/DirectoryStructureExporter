from pathlib import Path
import os
from PyQt6.QtCore import QObject, pyqtSignal, QSettings
from typing import Dict, Optional, Set

class TranslationManager(QObject):
    """Gestisce le traduzioni dell'applicazione senza file JSON"""

    language_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.current_language = 'it'  # Default italiano
        self.settings: Optional[QSettings] = None

        self.available_languages = {
            'it': 'Italiano',
            'en': 'English',
            'es': 'Español',
            'fr': 'Français',
            'de': 'Deutsch'
        }

        # Dizionari statici delle traduzioni (con le nuove aggiunte)
        self._translations = {
            'en': {
                "Directory Structure Exporter": "Directory Structure Exporter",
                "Tema:": "Theme:",
                "Lingua:": "Language:",
                "Sistema": "System",
                "Chiaro": "Light",
                "Scuro": "Dark",
                "Pronto": "Ready",
                "Lingua cambiata": "Language changed",
                "La lingua è stata cambiata. Alcune modifiche potrebbero richiedere il riavvio dell'applicazione.": "Language has been changed. Some changes may require restarting the application.",
                "Errore": "Error",
                "Errore nel caricamento della lingua selezionata.": "Error loading selected language.",
                "Lingua cambiata in": "Language changed to",
                "Esportazione": "Export",
                "Filtri": "Filters",
                "Configurazione": "Configuration",
                "Selezione Directory": "Directory Selection",
                "Directory:": "Directory:",
                "Sfoglia...": "Browse...",
                "Trascina qui una cartella": "Drag a folder here",
                "File di Output": "Output File",
                "File:": "File:",
                "Formato:": "Format:",
                "Stile indentazione:": "Indentation style:",
                "Opzioni di esportazione": "Export Options",
                "Includi file": "Include files",
                "Profondità massima:": "Maximum depth:",
                "Illimitata": "Unlimited",
                "Esporta": "Export",
                "Anteprima": "Preview",
                "Struttura Directory": "Directory Structure",
                "Mostra file": "Show files",
                "Applica filtri": "Apply filters",
                "Cerca:": "Search:",
                "Cerca file o cartelle...": "Search files or folders...",
                "Nome": "Name",
                "Tipo": "Type",
                "Percorso": "Path",
                "Directory": "Directory",
                "File": "File",
                "Caricamento": "Loading",
                "Accesso negato": "Access denied",
                "Espandi tutto": "Expand all",
                "Comprimi tutto": "Collapse all",
                "Apri in Esplora risorse": "Open in File Explorer",
                "Apri file": "Open file",
                "Apri cartella contenitore": "Open containing folder",
                "Copia percorso": "Copy path",
                "Percorso copiato:": "Path copied:",
                "Seleziona Directory": "Select Directory",
                "Salva File": "Save File",
                "Seleziona directory e file di output.": "Select directory and output file.",
                "Seleziona prima una directory.": "Select a directory first.",
                "Esportazione completata": "Export completed",
                "Errore durante l'esportazione": "Error during export",
                "Errore durante l'esportazione:": "Error during export:",
                "Struttura caricata:": "Structure loaded:",
                "Directory caricata:": "Directory loaded:",
                "Anteprima struttura": "Structure Preview",
                "Nessun elemento da visualizzare con i filtri attuali.": "No elements to display with current filters.",
                
                # Stili di indentazione
                "Spazi": "Spaces",
                "Trattini": "Dashes", 
                "Albero": "Tree",
                "Bullets": "Bullets",
                "Icone": "Icons",
                "Frecce": "Arrows",
                
                # Resto delle traduzioni esistenti...
                "Filtri dimensione file": "File Size Filters",
                "Dimensione minima (bytes):": "Minimum size (bytes):",
                "Dimensione massima (bytes):": "Maximum size (bytes):",
                "Illimitato": "Unlimited",
                "Filtri data creazione": "Creation Date Filters",
                "Data minima:": "Minimum date:",
                "Data massima:": "Maximum date:",
                "Attiva filtro per data di creazione": "Enable creation date filter",
                "Filtri data modifica": "Modification Date Filters",
                "Attiva filtro per data di modifica": "Enable modification date filter",
                "Reimposta filtri predefiniti": "Reset default filters",
                "Filtri applicati": "Filters applied",
                "I filtri sono stati applicati con successo.": "Filters have been applied successfully.",
                "Filtri reimpostati": "Filters reset",
                "I filtri sono stati reimpostati ai valori predefiniti.": "Filters have been reset to default values.",
                "Directory escluse": "Excluded Directories",
                "File esclusi": "Excluded Files",
                "Estensioni incluse": "Included Extensions",
                "Preset Configurazioni": "Configuration Presets",
                "Preset:": "Preset:",
                "-- Seleziona un preset --": "-- Select a preset --",
                "Salva come nuovo": "Save as new",
                "Aggiorna selezionato": "Update selected",
                "Elimina selezionato": "Delete selected",
                "Percorso File Preset": "Preset File Path",
                "File preset:": "Preset file:",
                "Applica": "Apply",
                "Aggiungi": "Add",
                "Aggiungi Regex": "Add Regex",
                "Rimuovi": "Remove",
                "Salva configurazione": "Save configuration",
                "Carica configurazione": "Load configuration",
                "Guida alle Espressioni Regolari": "Regular Expressions Guide",
                "Aiuto Espressioni Regolari": "Regular Expressions Help",
                "Aggiungi directory": "Add directory",
                "Nome directory:": "Directory name:",
                "Aggiungi pattern regex": "Add regex pattern",
                "Inserisci un'espressione regolare per escludere le directory:": "Enter a regular expression to exclude directories:",
                "Espressione non valida": "Invalid expression",
                "L'espressione regolare inserita non è valida.": "The entered regular expression is not valid.",
                "Aggiungi file": "Add file",
                "Nome file (es. .gitignore, thumbs.db):": "File name (e.g. .gitignore, thumbs.db):",
                "Inserisci un'espressione regolare per escludere i file:": "Enter a regular expression to exclude files:",
                "Aggiungi estensione": "Add extension",
                "Estensione (con punto iniziale, es. .py):": "Extension (with initial dot, e.g. .py):",
                "Inserisci un'espressione regolare per includere i file:": "Enter a regular expression to include files:",
                "Salva Configurazione": "Save Configuration",
                "Carica Configurazione": "Load Configuration",
                "Salva Preset": "Save Preset",
                "Preset esistente": "Existing preset",
                "Nessun preset selezionato": "No preset selected",
                "Seleziona prima un preset da aggiornare.": "Select a preset to update first.",
                "Aggiorna preset": "Update preset",
                "Seleziona prima un preset da eliminare.": "Select a preset to delete first.",
                "Elimina preset": "Delete preset",
                "Filtri applicati con successo": "Filters applied successfully",
                "Imposta file preset": "Set preset file",
                "Cambiare percorso preset": "Change preset path",
                "Vuoi spostare i preset in": "Do you want to move presets to",
                "I preset attuali verranno copiati nel nuovo percorso.": "Current presets will be copied to the new path.",
                "Percorso preset impostato:": "Preset path set:",
                "Nome del preset:": "Preset name:",
                "Il preset": "The preset",
                "esiste già. Sovrascrivere?": "already exists. Overwrite?",
                "Sei sicuro di voler aggiornare il preset": "Are you sure you want to update the preset",
                "Sei sicuro di voler eliminare il preset": "Are you sure you want to delete the preset",
                "Esempi di pattern comuni:": "Examples of common patterns:",
                "Corrisponde a nomi che iniziano con": "Matches names starting with",
                "Corrisponde a nomi che finiscono con": "Matches names ending with",
                "Corrisponde a nomi come": "Matches names like",
                "ecc.": "etc.",
                "Corrisponde a qualsiasi nome che contiene": "Matches any name containing",
                "Corrisponde a file che finiscono con": "Matches files ending with"
            },
            'de': {
                "Directory Structure Exporter": "Verzeichnisstruktur-Exporteur",
                "Tema:": "Thema:",
                "Lingua:": "Sprache:",
                "Sistema": "System",
                "Chiaro": "Hell",
                "Scuro": "Dunkel",
                "Pronto": "Bereit",
                "Lingua cambiata": "Sprache geändert",
                "La lingua è stata cambiata. Alcune modifiche potrebbero richiedere il riavvio dell'applicazione.": "Die Sprache wurde geändert. Einige Änderungen können einen Neustart der Anwendung erfordern.",
                "Errore": "Fehler",
                "Errore nel caricamento della lingua selezionata.": "Fehler beim Laden der ausgewählten Sprache.",
                "Lingua cambiata in": "Sprache geändert zu",
                "Esportazione": "Export",
                "Filtri": "Filter",
                "Configurazione": "Konfiguration",
                "Selezione Directory": "Verzeichnisauswahl",
                "Directory:": "Verzeichnis:",
                "Sfoglia...": "Durchsuchen...",
                "Trascina qui una cartella": "Ordner hierher ziehen",
                "File di Output": "Ausgabedatei",
                "File:": "Datei:",
                "Formato:": "Format:",
                "Stile indentazione:": "Einrückungsstil:",
                "Opzioni di esportazione": "Export-Optionen",
                "Includi file": "Dateien einschließen",
                "Profondità massima:": "Maximale Tiefe:",
                "Illimitata": "Unbegrenzt",
                "Esporta": "Exportieren",
                "Anteprima": "Vorschau",
                "Struttura Directory": "Verzeichnisstruktur",
                "Mostra file": "Dateien anzeigen",
                "Applica filtri": "Filter anwenden",
                "Cerca:": "Suchen:",
                "Cerca file o cartelle...": "Dateien oder Ordner suchen...",
                "Nome": "Name",
                "Tipo": "Typ",
                "Percorso": "Pfad",
                "Directory": "Verzeichnis",
                "File": "Datei",
                "Caricamento": "Laden",
                "Accesso negato": "Zugriff verweigert",
                "Espandi tutto": "Alles erweitern",
                "Comprimi tutto": "Alles einklappen",
                "Apri in Esplora risorse": "Im Datei-Explorer öffnen",
                "Apri file": "Datei öffnen",
                "Apri cartella contenitore": "Enthaltenden Ordner öffnen",
                "Copia percorso": "Pfad kopieren",
                "Percorso copiato:": "Pfad kopiert:",
                "Seleziona Directory": "Verzeichnis auswählen",
                "Salva File": "Datei speichern",
                "Seleziona directory e file di output.": "Verzeichnis und Ausgabedatei auswählen.",
                "Seleziona prima una directory.": "Zuerst ein Verzeichnis auswählen.",
                "Esportazione completata": "Export abgeschlossen",
                "Errore durante l'esportazione": "Fehler beim Export",
                "Errore durante l'esportazione:": "Fehler beim Export:",
                "Struttura caricata:": "Struktur geladen:",
                "Directory caricata:": "Verzeichnis geladen:",
                "Anteprima struttura": "Struktur-Vorschau", 
                "Nessun elemento da visualizzare con i filtri attuali.": "Keine Elemente mit den aktuellen Filtern anzuzeigen.",
                
                # Stili di indentazione
                "Spazi": "Leerzeichen",
                "Trattini": "Bindestriche",
                "Albero": "Baum",
                "Bullets": "Aufzählungszeichen",
                "Icone": "Symbole", 
                "Frecce": "Pfeile",
                
                # Altri elementi tedeschi...
                "Filtri dimensione file": "Dateigrößen-Filter",
                "Dimensione minima (bytes):": "Mindestgröße (Bytes):",
                "Dimensione massima (bytes):": "Maximalgröße (Bytes):",
                "Illimitato": "Unbegrenzt",
                "Filtri data creazione": "Erstellungsdatum-Filter",
                "Data minima:": "Mindestdatum:",
                "Data massima:": "Maximaldatum:",
                "Attiva filtro per data di creazione": "Filter für Erstellungsdatum aktivieren",
                "Filtri data modifica": "Änderungsdatum-Filter",
                "Attiva filtro per data di modifica": "Filter für Änderungsdatum aktivieren",
                "Reimposta filtri predefiniti": "Standardfilter zurücksetzen",
                "Filtri applicati": "Filter angewendet",
                "I filtri sono stati applicati con successo.": "Die Filter wurden erfolgreich angewendet.",
                "Filtri reimpostati": "Filter zurückgesetzt",
                "I filtri sono stati reimpostati ai valori predefiniti.": "Die Filter wurden auf Standardwerte zurückgesetzt.",
                "Directory escluse": "Ausgeschlossene Verzeichnisse",
                "File esclusi": "Ausgeschlossene Dateien",
                "Estensioni incluse": "Eingeschlossene Erweiterungen"
            },
            'fr': {
                "Directory Structure Exporter": "Exportateur de Structure de Répertoires",
                "Tema:": "Thème:",
                "Lingua:": "Langue:",
                "Sistema": "Système",
                "Chiaro": "Clair",
                "Scuro": "Sombre",
                "Pronto": "Prêt",
                "Lingua cambiata": "Langue changée",
                "La lingua è stata cambiata. Alcune modifiche potrebbero richiedere il riavvio dell'applicazione.": "La langue a été changée. Certains changements peuvent nécessiter le redémarrage de l'application.",
                "Errore": "Erreur",
                "Errore nel caricamento della lingua selezionata.": "Erreur lors du chargement de la langue sélectionnée.",
                "Lingua cambiata in": "Langue changée en",
                "Esportazione": "Exportation",
                "Filtri": "Filtres",
                "Configurazione": "Configuration",
                "Selezione Directory": "Sélection de Répertoire",
                "Directory:": "Répertoire:",
                "Sfoglia...": "Parcourir...",
                "Trascina qui una cartella": "Glissez un dossier ici",
                "File di Output": "Fichier de Sortie",
                "File:": "Fichier:",
                "Formato:": "Format:",
                "Stile indentazione:": "Style d'indentation:",
                "Opzioni di esportazione": "Options d'exportation",
                "Includi file": "Inclure fichiers",
                "Profondità massima:": "Profondeur maximale:",
                "Illimitata": "Illimitée",
                "Esporta": "Exporter",
                "Anteprima": "Aperçu",
                "Struttura Directory": "Structure de Répertoires",
                "Mostra file": "Afficher fichiers",
                "Applica filtri": "Appliquer filtres",
                "Cerca:": "Rechercher:",
                "Cerca file o cartelle...": "Rechercher fichiers ou dossiers...",
                "Nome": "Nom",
                "Tipo": "Type",
                "Percorso": "Chemin",
                "Directory": "Répertoire",
                "File": "Fichier",
                "Caricamento": "Chargement",
                "Accesso negato": "Accès refusé",
                "Espandi tutto": "Développer tout",
                "Comprimi tutto": "Réduire tout",
                "Apri in Esplora risorse": "Ouvrir dans l'Explorateur",
                "Apri file": "Ouvrir fichier",
                "Apri cartella contenitore": "Ouvrir dossier parent",
                "Copia percorso": "Copier chemin",
                "Percorso copiato:": "Chemin copié:",
                "Seleziona Directory": "Sélectionner Répertoire",
                "Salva File": "Enregistrer Fichier",
                "Seleziona directory e file di output.": "Sélectionnez répertoire et fichier de sortie.",
                "Seleziona prima una directory.": "Sélectionnez d'abord un répertoire.",
                "Esportazione completata": "Exportation terminée",
                "Errore durante l'esportazione": "Erreur pendant l'exportation",
                "Errore durante l'esportazione:": "Erreur pendant l'exportation:",
                "Struttura caricata:": "Structure chargée:",
                "Directory caricata:": "Répertoire chargé:",
                "Anteprima struttura": "Aperçu de la structure",
                "Nessun elemento da visualizzare con i filtri attuali.": "Aucun élément à afficher avec les filtres actuels.",
                
                # Stili di indentazione
                "Spazi": "Espaces",
                "Trattini": "Tirets",
                "Albero": "Arbre",
                "Bullets": "Puces", 
                "Icone": "Icônes",
                "Frecce": "Flèches",
                
                # Altri elementi francesi...
                "Filtri dimensione file": "Filtres de Taille de Fichier",
                "Dimensione minima (bytes):": "Taille minimale (octets):",
                "Dimensione massima (bytes):": "Taille maximale (octets):",
                "Illimitato": "Illimité",
                "Filtri data creazione": "Filtres de Date de Création",
                "Data minima:": "Date minimale:",
                "Data massima:": "Date maximale:",
                "Attiva filtro per data di creazione": "Activer filtre par date de création",
                "Filtri data modifica": "Filtres de Date de Modification",
                "Attiva filtro per data di modifica": "Activer filtre par date de modification",
                "Reimposta filtri predefiniti": "Réinitialiser filtres par défaut",
                "Filtri applicati": "Filtres appliqués",
                "I filtri sono stati applicati con successo.": "Les filtres ont été appliqués avec succès.",
                "Filtri reimpostati": "Filtres réinitialisés",
                "I filtri sono stati reimpostati ai valori predefiniti.": "Les filtres ont été réinitialisés aux valeurs par défaut.",
                "Directory escluse": "Répertoires Exclus",
                "File esclusi": "Fichiers Exclus",
                "Estensioni incluse": "Extensions Incluses"
            },
            'es': {
                "Directory Structure Exporter": "Exportador de Estructura de Directorios",
                "Tema:": "Tema:",
                "Lingua:": "Idioma:",
                "Sistema": "Sistema",
                "Chiaro": "Claro",
                "Scuro": "Oscuro",
                "Pronto": "Listo",
                "Lingua cambiata": "Idioma cambiado",
                "La lingua è stata cambiata. Alcune modifiche potrebbero richiedere il riavvio dell'applicazione.": "El idioma ha sido cambiado. Algunos cambios pueden requerir reiniciar la aplicación.",
                "Errore": "Error",
                "Errore nel caricamento della lingua selezionata.": "Error al cargar el idioma seleccionado.",
                "Lingua cambiata in": "Idioma cambiado a",
                "Esportazione": "Exportación",
                "Filtri": "Filtros",
                "Configurazione": "Configuración",
                "Selezione Directory": "Selección de Directorio",
                "Directory:": "Directorio:",
                "Sfoglia...": "Examinar...",
                "Trascina qui una cartella": "Arrastra una carpeta aquí",
                "File di Output": "Archivo de Salida",
                "File:": "Archivo:",
                "Formato:": "Formato:",
                "Stile indentazione:": "Estilo de indentación:",
                "Opzioni di esportazione": "Opciones de exportación",
                "Includi file": "Incluir archivos",
                "Profondità massima:": "Profundidad máxima:",
                "Illimitata": "Ilimitada",
                "Esporta": "Exportar",
                "Anteprima": "Vista previa",
                "Struttura Directory": "Estructura de Directorios",
                "Mostra file": "Mostrar archivos",
                "Applica filtri": "Aplicar filtros",
                "Cerca:": "Buscar:",
                "Cerca file o cartelle...": "Buscar archivos o carpetas...",
                "Nome": "Nombre",
                "Tipo": "Tipo",
                "Percorso": "Ruta",
                "Directory": "Directorio",
                "File": "Archivo",
                "Caricamento": "Cargando",
                "Accesso negato": "Acceso denegado",
                "Espandi tutto": "Expandir todo",
                "Comprimi tutto": "Contraer todo",
                "Apri in Esplora risorse": "Abrir en Explorador de archivos",
                "Apri file": "Abrir archivo",
                "Apri cartella contenitore": "Abrir carpeta contenedora",
                "Copia percorso": "Copiar ruta",
                "Percorso copiato:": "Ruta copiada:",
                "Seleziona Directory": "Seleccionar Directorio",
                "Salva File": "Guardar Archivo",
                "Seleziona directory e file di output.": "Selecciona directorio y archivo de salida.",
                "Seleziona prima una directory.": "Selecciona primero un directorio.",
                "Esportazione completata": "Exportación completada",
                "Errore durante l'esportazione": "Error durante la exportación",
                "Errore durante l'esportazione:": "Error durante la exportación:",
                "Struttura caricata:": "Estructura cargada:",
                "Directory caricata:": "Directorio cargado:",
                "Anteprima struttura": "Vista previa de estructura",
                "Nessun elemento da visualizzare con i filtri attuali.": "No hay elementos para mostrar con los filtros actuales.",
                
                # Stili di indentazione
                "Spazi": "Espacios",
                "Trattini": "Guiones",
                "Albero": "Árbol", 
                "Bullets": "Viñetas",
                "Icone": "Iconos",
                "Frecce": "Flechas",
                
                # Altri elementi spagnoli...
                "Filtri dimensione file": "Filtros de Tamaño de Archivo",
                "Dimensione minima (bytes):": "Tamaño mínimo (bytes):",
                "Dimensione massima (bytes):": "Tamaño máximo (bytes):",
                "Illimitato": "Ilimitado",
                "Filtri data creazione": "Filtros de Fecha de Creación",
                "Data minima:": "Fecha mínima:",
                "Data massima:": "Fecha máxima:",
                "Attiva filtro per data di creazione": "Activar filtro por fecha de creación",
                "Filtri data modifica": "Filtros de Fecha de Modificación",
                "Attiva filtro per data di modifica": "Activar filtro por fecha de modificación",
                "Reimposta filtri predefiniti": "Restablecer filtros predeterminados",
                "Filtri applicati": "Filtros aplicados",
                "I filtri sono stati applicati con successo.": "Los filtros se han aplicado con éxito.",
                "Filtri reimpostati": "Filtros restablecidos",
                "I filtri sono stati reimpostati ai valori predefiniti.": "Los filtros se han restablecido a los valores predeterminados.",
                "Directory escluse": "Directorios Excluidos",
                "File esclusi": "Archivos Excluidos",
                "Estensioni incluse": "Extensiones Incluidas"
            }
        }

        self.current_translations: Dict[str, str] = {}
        self._missing_translations: Set[str] = set()

    def initialize(self, settings: QSettings) -> None:
        self.settings = settings
        saved_language = settings.value("language", None)
        if saved_language and saved_language in self.available_languages:
            self.load_language(saved_language)
        else:
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
        if language_code not in self.available_languages:
            return False

        old_language = self.current_language
        self.current_language = language_code

        if language_code == 'it':
            self.current_translations = {}
            self._missing_translations.clear()
        else:
            self.current_translations = self._translations.get(language_code, {})

        if self.settings:
            self.settings.setValue("language", language_code)

        if old_language != language_code:
            self.language_changed.emit(language_code)

        return True

    def translate(self, text: str, context: Optional[str] = None) -> str:
        if self.current_language == 'it' or not text:
            return text

        translation = self.current_translations.get(text)
        if translation:
            return translation

        if text not in self._missing_translations:
            self._missing_translations.add(text)
            print(f"Traduzione mancante [{self.current_language}]: '{text}'")

        return text

    def get_missing_translations(self) -> Set[str]:
        return self._missing_translations.copy()

    def add_translation(self, italian_text: str, translated_text: str,
                       language_code: Optional[str] = None) -> bool:
        target_lang = language_code or self.current_language
        if target_lang == 'it':
            return True
        if target_lang not in self._translations:
            self._translations[target_lang] = {}
        self._translations[target_lang][italian_text] = translated_text
        if target_lang == self.current_language:
            self.current_translations = self._translations[target_lang]
            if italian_text in self._missing_translations:
                self._missing_translations.remove(italian_text)
        return True

# Istanza globale
translation_manager = TranslationManager()

def tr(text: str, context: Optional[str] = None) -> str:
    return translation_manager.translate(text, context)# Aggiunte al translation_manager.py per i nuovi elementi

# Aggiungi queste traduzioni ai dizionari esistenti:

traduzioni_aggiuntive = {
    'en': {
        "Stile indentazione:": "Indentation style:",
        "Anteprima": "Preview",
        "Anteprima struttura": "Structure Preview",
        "Nessun elemento da visualizzare con i filtri attuali.": "No elements to display with current filters.",
        "Spazi": "Spaces",
        "Trattini": "Dashes", 
        "Albero": "Tree",
        "Bullets": "Bullets",
        "Icone": "Icons",
        "Frecce": "Arrows"
    },
    'es': {
        "Stile indentazione:": "Estilo de indentación:",
        "Anteprima": "Vista previa",
        "Anteprima struttura": "Vista previa de estructura",
        "Nessun elemento da visualizzare con i filtri attuali.": "No hay elementos para mostrar con los filtros actuales.",
        "Spazi": "Espacios",
        "Trattini": "Guiones",
        "Albero": "Árbol", 
        "Bullets": "Viñetas",
        "Icone": "Iconos",
        "Frecce": "Flechas"
    },
    'fr': {
        "Stile indentazione:": "Style d'indentation:",
        "Anteprima": "Aperçu",
        "Anteprima struttura": "Aperçu de la structure",
        "Nessun elemento da visualizzare con i filtri attuali.": "Aucun élément à afficher avec les filtres actuels.",
        "Spazi": "Espaces",
        "Trattini": "Tirets",
        "Albero": "Arbre",
        "Bullets": "Puces", 
        "Icone": "Icônes",
        "Frecce": "Flèches"
    },
    'de': {
        "Stile indentazione:": "Einrückungsstil:",
        "Anteprima": "Vorschau",
        "Anteprima struttura": "Struktur-Vorschau", 
        "Nessun elemento da visualizzare con i filtri attuali.": "Keine Elemente mit den aktuellen Filtern anzuzeigen.",
        "Spazi": "Leerzeichen",
        "Trattini": "Bindestriche",
        "Albero": "Baum",
        "Bullets": "Aufzählungszeichen",
        "Icone": "Symbole", 
        "Frecce": "Pfeile"
    }
}