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

class TranslationGenerator:
    def __init__(self):
        self.project_root = Path.cwd()
        self.translations_dir = self.project_root / "translations"
        self.source_files = []
        self.languages = ['en', 'es', 'fr', 'de']
        
        # Crea la directory delle traduzioni se non esiste
        self.translations_dir.mkdir(exist_ok=True)
        
        # Trova tutti i file Python che contengono tr()
        self.find_source_files()
    
    def find_source_files(self):
        """Trova tutti i file Python che potrebbero contenere stringhe da tradurre"""
        python_files = []
        
        # Cerca ricorsivamente tutti i file .py
        for py_file in self.project_root.rglob("*.py"):
            # Escludi file temporanei e di test
            if not any(exclude in str(py_file) for exclude in ['__pycache__', '.git', 'test_', 'tests']):
                # Controlla se il file contiene tr( o tr("
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if 'tr(' in content or 'tr("' in content:
                            python_files.append(str(py_file.relative_to(self.project_root)))
                except:
                    pass
        
        self.source_files = python_files
        print(f"Trovati {len(self.source_files)} file con stringhe da tradurre:")
        for f in self.source_files:
            print(f"  - {f}")
    
    def create_pro_file(self):
        """Crea il file .pro per pylupdate"""
        pro_content = f"""# File di progetto per le traduzioni
SOURCES = {' '.join(self.source_files)}

TRANSLATIONS = """
        
        for lang in self.languages:
            pro_content += f"translations/app_{lang}.ts "
        
        pro_file = self.translations_dir / "translations.pro"
        with open(pro_file, 'w', encoding='utf-8') as f:
            f.write(pro_content)
        
        print(f"File .pro creato: {pro_file}")
        return pro_file
    
    def extract_strings(self):
        """Estrae le stringhe da tradurre usando pylupdate"""
        pro_file = self.create_pro_file()
        
        try:
            # Prova prima con pylupdate6
            result = subprocess.run(['pylupdate6', str(pro_file)], 
                                  capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode != 0:
                # Se pylupdate6 non funziona, prova con pylupdate5
                print("pylupdate6 non trovato, provo con pylupdate5...")
                result = subprocess.run(['pylupdate5', str(pro_file)], 
                                      capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                print("Estrazione stringhe completata con successo!")
                print(result.stdout)
            else:
                print(f"Errore durante l'estrazione: {result.stderr}")
                return False
                
        except FileNotFoundError:
            print("pylupdate non trovato. Installa PyQt6-tools o uso il metodo alternativo.")
            self.create_fallback_translations()
            return False
        
        return True
    
    def create_fallback_translations(self):
        """Crea traduzioni di fallback se pylupdate non è disponibile"""
        print("Creazione traduzioni di fallback...")
        
        # Estrai manualmente le stringhe tr() dai file
        all_strings = set()
        
        for source_file in self.source_files:
            try:
                with open(source_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Regex semplice per trovare tr("stringa") e tr('stringa')
                patterns = [
                    r'tr\("([^"]+)"\)',
                    r"tr\('([^']+)'\)"
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    all_strings.update(matches)
                    
            except Exception as e:
                print(f"Errore leggendo {source_file}: {e}")
        
        print(f"Trovate {len(all_strings)} stringhe da tradurre")
        
        # Crea i file di traduzione di fallback per ogni lingua
        for lang in self.languages:
            self.create_fallback_json(lang, all_strings)
    
    def create_fallback_json(self, language_code, strings):
        """Crea un file JSON di fallback per una lingua specifica"""
        # Usa traduzioni predefinite integrate direttamente qui
        default_translations = self.get_builtin_translations(language_code)
        
        # Crea il dizionario di traduzione
        translations = {}
        for string in strings:
            translations[string] = default_translations.get(string, string)
        
        # Salva il file JSON
        fallback_file = self.translations_dir / f"fallback_{language_code}.json"
        with open(fallback_file, 'w', encoding='utf-8') as f:
            json.dump(translations, f, indent=2, ensure_ascii=False)
        
        print(f"File di fallback creato: {fallback_file}")
    
    def get_builtin_translations(self, language_code):
        """Restituisce le traduzioni integrate per una lingua"""
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
                
                # Context Menu
                'Espandi tutto': 'Expand all',
                'Comprimi tutto': 'Collapse all',
                'Apri in Esplora risorse': 'Open in File Explorer',
                'Apri file': 'Open file',
                'Apri cartella contenitore': 'Open containing folder',
                'Copia percorso': 'Copy path',
                'Percorso copiato:': 'Path copied:',
                
                # Messages
                'Seleziona Directory': 'Select Directory',
                'Salva File': 'Save File',
                'Seleziona directory e file di output.': 'Select directory and output file.',
                'Seleziona prima una directory.': 'Select a directory first.',
                'Esportazione completata': 'Export completed',
                'Errore durante l\'esportazione': 'Error during export',
                'Errore durante l\'esportazione:': 'Error during export:',
                'Struttura caricata:': 'Structure loaded:',
                'Directory caricata:': 'Directory loaded:',
                
                # Filters Tab
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
                'Applica filtri': 'Apply filters',
                'Reimposta filtri predefiniti': 'Reset default filters',
                'Filtri applicati': 'Filters applied',
                'I filtri sono stati applicati con successo.': 'Filters have been applied successfully.',
                'Filtri reimpostati': 'Filters reset',
                'I filtri sono stati reimpostati ai valori predefiniti.': 'Filters have been reset to default values.',
            },
            'es': {
                # Traduzioni spagnole
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
                'Lingua cambiata': 'Idioma cambiado',
                'La lingua è stata cambiata. Alcune modifiche potrebbero richiedere il riavvio dell\'applicazione.': 'El idioma ha sido cambiado. Algunos cambios pueden requerir reiniciar la aplicación.',
                'Errore nel caricamento della lingua selezionata.': 'Error al cargar el idioma seleccionado.',
            },
            'fr': {
                # Traduzioni francesi
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
                'Lingua cambiata': 'Langue changée',
                'La lingua è stata cambiata. Alcune modifiche potrebbero richiedere il riavvio dell\'applicazione.': 'La langue a été changée. Certains changements peuvent nécessiter le redémarrage de l\'application.',
                'Errore nel caricamento della lingua selezionata.': 'Erreur lors du chargement de la langue sélectionnée.',
            },
            'de': {
                # Traduzioni tedesche
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
                'Lingua cambiata': 'Sprache geändert',
                'La lingua è stata cambiata. Alcune modifiche potrebbero richiedere il riavvio dell\'applicazione.': 'Die Sprache wurde geändert. Einige Änderungen können einen Neustart der Anwendung erfordern.',
                'Errore nel caricamento della lingua selezionata.': 'Fehler beim Laden der ausgewählten Sprache.',
            }
        }
        
        return translations.get(language_code, {})
    
    def compile_translations(self):
        """Compila i file .ts in .qm usando lrelease"""
        ts_files = list(self.translations_dir.glob("*.ts"))
        
        if not ts_files:
            print("Nessun file .ts trovato da compilare")
            return False
        
        for ts_file in ts_files:
            qm_file = ts_file.with_suffix('.qm')
            
            try:
                # Prova prima con lrelease6
                result = subprocess.run(['lrelease6', str(ts_file), '-qm', str(qm_file)], 
                                      capture_output=True, text=True)
                
                if result.returncode != 0:
                    # Se lrelease6 non funziona, prova con lrelease
                    result = subprocess.run(['lrelease', str(ts_file), '-qm', str(qm_file)], 
                                          capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"Compilato: {ts_file.name} -> {qm_file.name}")
                else:
                    print(f"Errore compilando {ts_file.name}: {result.stderr}")
                    
            except FileNotFoundError:
                print(f"lrelease non trovato per compilare {ts_file.name}")
        
        return True
    
    def create_language_template(self, language_code):
        """Crea un template di traduzione per una nuova lingua"""
        if language_code not in self.languages:
            self.languages.append(language_code)
        
        # Estrai le stringhe
        self.extract_strings()
        
        print(f"Template per {language_code} creato in translations/app_{language_code}.ts")
    
    def update_translations(self):
        """Aggiorna i file di traduzione esistenti con nuove stringhe"""
        print("Aggiornamento traduzioni...")
        self.extract_strings()
        print("Traduzioni aggiornate!")
    
    def build_all(self):
        """Costruisce tutto: estrazione, compilazione e fallback"""
        print("=== Generazione completa delle traduzioni ===")
        
        # 1. Estrai le stringhe
        if self.extract_strings():
            # 2. Compila i file .ts in .qm
            self.compile_translations()
        else:
            print("Usando traduzioni di fallback...")
        
        print("\n=== Processo completato ===")
        print(f"File di traduzione generati in: {self.translations_dir}")

def main():
    if len(sys.argv) < 2:
        print("""
Uso: python translation_generator.py <comando> [opzioni]

Comandi disponibili:
  extract     - Estrae le stringhe da tradurre dai file sorgente
  compile     - Compila i file .ts in .qm
  build       - Estrae e compila tutto
  update      - Aggiorna le traduzioni esistenti
  add <lang>  - Aggiunge supporto per una nuova lingua (es: add pt)
  
Esempi:
  python translation_generator.py build
  python translation_generator.py add pt
  python translation_generator.py update
        """)
        return
    
    generator = TranslationGenerator()
    command = sys.argv[1]
    
    if command == "extract":
        generator.extract_strings()
    elif command == "compile":
        generator.compile_translations()
    elif command == "build":
        generator.build_all()
    elif command == "update":
        generator.update_translations()
    elif command == "add" and len(sys.argv) > 2:
        lang_code = sys.argv[2]
        generator.create_language_template(lang_code)
    else:
        print(f"Comando non riconosciuto: {command}")

if __name__ == "__main__":
    main()