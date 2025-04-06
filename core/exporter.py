import re
from pathlib import Path
import json
import xml.dom.minidom as minidom
import xml.etree.ElementTree as ET

class DirectoryExporter:
    def __init__(self):
        # Strutture esistenti
        self.excluded_dirs = {'.git', '.vs', 'bin', 'obj', 'Debug', 'Release', 'packages'}
        self.excluded_dirs_regex = set()
        self.included_file_extensions = {'.sln', '.csproj', '.vbproj', '.cs', '.html', '.cshtml', '.css', '.js'}
        self.included_file_regex = set()
        
        # Nuovi filtri
        self.min_file_size = 0  # in bytes
        self.max_file_size = float('inf')  # in bytes
        self.min_creation_date = None  # timestamp
        self.max_creation_date = None  # timestamp
        self.min_modification_date = None  # timestamp
        self.max_modification_date = None  # timestamp
        
        # Collezione di preset salvati
        self.filter_presets = {}  # Nome -> configurazione

    def save_filter_preset(self, preset_name):
        """Salva la configurazione attuale dei filtri come preset"""
        self.filter_presets[preset_name] = {
            # Filtri esistenti
            'excluded_dirs': set(self.excluded_dirs),
            'excluded_dirs_regex': set(self.excluded_dirs_regex),
            'included_file_extensions': set(self.included_file_extensions),
            'included_file_regex': set(self.included_file_regex),
            
            # Nuovi filtri
            'min_file_size': self.min_file_size,
            'max_file_size': self.max_file_size, 
            'min_creation_date': self.min_creation_date,
            'max_creation_date': self.max_creation_date,
            'min_modification_date': self.min_modification_date,
            'max_modification_date': self.max_modification_date
        }
        return True, f"Preset '{preset_name}' salvato con successo."

    def load_filter_preset(self, preset_name):
        """Carica una configurazione di filtri salvata"""
        if preset_name not in self.filter_presets:
            return False, f"Preset '{preset_name}' non trovato."
        
        preset = self.filter_presets[preset_name]
        
        # Carica tutti i filtri dal preset
        self.excluded_dirs = set(preset['excluded_dirs'])
        self.excluded_dirs_regex = set(preset['excluded_dirs_regex'])
        self.included_file_extensions = set(preset['included_file_extensions'])
        self.included_file_regex = set(preset['included_file_regex'])
        self.min_file_size = preset['min_file_size']
        self.max_file_size = preset['max_file_size']
        self.min_creation_date = preset['min_creation_date']
        self.max_creation_date = preset['max_creation_date']
        self.min_modification_date = preset['min_modification_date']
        self.max_modification_date = preset['max_modification_date']
        
        return True, f"Preset '{preset_name}' caricato con successo."

    def delete_filter_preset(self, preset_name):
        """Elimina un preset salvato"""
        if preset_name in self.filter_presets:
            del self.filter_presets[preset_name]
            return True, f"Preset '{preset_name}' eliminato."
        return False, f"Preset '{preset_name}' non trovato."

    def get_filter_preset_names(self):
        """Restituisce i nomi di tutti i preset disponibili"""
        return list(self.filter_presets.keys())
        
    # ----- METODI PRINCIPALI DI ESPORTAZIONE -----

    # Metodi per verificare se un nome corrisponde a un pattern regex
    def is_excluded_dir(self, dir_name):
        """Verifica se la directory deve essere esclusa"""
        # Controllo esatto
        if dir_name in self.excluded_dirs:
            return True
            
        # Controllo con regex
        for pattern in self.excluded_dirs_regex:
            try:
                if re.search(pattern, dir_name):
                    return True
            except re.error:
                continue  # Ignora pattern regex non validi
                
        return False
        
    def is_included_file(self, file_path):
        """Verifica se il file deve essere incluso in base a tutti i criteri"""
        file_path = Path(file_path) if isinstance(file_path, str) else file_path
        
        # Verifica estensione/regex (codice esistente)
        extension_match = file_path.suffix in self.included_file_extensions
        regex_match = any(re.search(pattern, file_path.name) for pattern in self.included_file_regex)
        
        if not (extension_match or regex_match) and (self.included_file_extensions or self.included_file_regex):
            return False
        
        # Verifica dimensione file
        try:
            file_size = file_path.stat().st_size
            if file_size < self.min_file_size or file_size > self.max_file_size:
                return False
        except (OSError, PermissionError):
            # In caso di errori, ignoriamo questo criterio
            pass
            
        try:
            creation_time = file_path.stat().st_ctime
            if (self.min_creation_date and creation_time < self.min_creation_date) or \
            (self.max_creation_date and creation_time > self.max_creation_date):
                return False
        except (OSError, PermissionError):
            pass
        
        # Verifica data di modifica
        try:
            modification_time = file_path.stat().st_mtime
            if (self.min_modification_date and modification_time < self.min_modification_date) or \
            (self.max_modification_date and modification_time > self.max_modification_date):
                return False
        except (OSError, PermissionError):
            pass
        
        # Aggiungere qui controlli per date di creazione/modifica
        
        return True
    
    def export_structure(self, root_dir, output_file_path, include_files=True, max_depth=None):
        """Esporta la struttura di directory nel file specificato in formato testo"""
        try:
            with open(output_file_path, 'w', encoding='utf-8') as output_file:
                self._print_structure(root_dir, output_file, prefix='', depth=0, 
                                      max_depth=max_depth, include_files=include_files)
            return True, f"La struttura è stata esportata in '{output_file_path}'."
        except Exception as e:
            return False, f"Errore durante l'esportazione: {e}"
    
    def export_structure_html(self, root_dir, output_file_path, include_files=True, max_depth=None):
        """Esporta la struttura di directory in formato HTML"""
        root_path = Path(root_dir)
        
        # Creiamo la struttura HTML di base
        html = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Struttura Directory: {root_path.name}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .directory {{ color: #0066cc; font-weight: bold; }}
                .file {{ color: #333; }}
                ul {{ list-style-type: none; }}
                li {{ margin: 5px 0; }}
            </style>
        </head>
        <body>
            <h1>Struttura Directory: {root_path.name}</h1>
            <ul id="root">
        """
        
        # Aggiungiamo la struttura
        html += self._build_structure_html(root_path, indent=8, depth=0, 
                                          max_depth=max_depth, include_files=include_files)
        
        # Chiudiamo il documento HTML
        html += """    </ul>
        </body>
        </html>"""
        
        try:
            with open(output_file_path, 'w', encoding='utf-8') as f:
                f.write(html)
            return True, f"La struttura è stata esportata in formato HTML in '{output_file_path}'."
        except Exception as e:
            return False, f"Errore durante l'esportazione HTML: {e}"
    
    def export_structure_json(self, root_dir, output_file_path, include_files=True, max_depth=None):
        """Esporta la struttura di directory in formato JSON"""
        root_path = Path(root_dir)
        structure = self._build_structure_dict(root_path, depth=0, max_depth=max_depth, include_files=include_files)
        
        try:
            with open(output_file_path, 'w', encoding='utf-8') as f:
                json.dump(structure, f, indent=4)
            return True, f"La struttura è stata esportata in formato JSON in '{output_file_path}'."
        except Exception as e:
            return False, f"Errore durante l'esportazione JSON: {e}"
    
    def export_structure_xml(self, root_dir, output_file_path, include_files=True, max_depth=None):
        """Esporta la struttura di directory in formato XML"""
        root_path = Path(root_dir)
        root_elem = ET.Element("directory", name=root_path.name)
        
        self._build_structure_xml(root_path, root_elem, depth=0, max_depth=max_depth, include_files=include_files)
        
        try:
            # Formattiamo l'XML per renderlo leggibile
            rough_string = ET.tostring(root_elem, 'utf-8')
            reparsed = minidom.parseString(rough_string)
            pretty_xml = reparsed.toprettyxml(indent="  ")
            
            with open(output_file_path, 'w', encoding='utf-8') as f:
                f.write(pretty_xml)
                
            return True, f"La struttura è stata esportata in formato XML in '{output_file_path}'."
        except Exception as e:
            return False, f"Errore durante l'esportazione XML: {e}"
    
    # ----- METODI DI SUPPORTO PER LA GENERAZIONE DELLA STRUTTURA -----
    
    def _print_structure(self, root_dir, file_handle, prefix='', depth=0, max_depth=None, include_files=True):
        root_path = Path(root_dir)
        if self.is_excluded_dir(root_path.name):  # Usa il nuovo metodo
            return
        
        # Verifichiamo se abbiamo raggiunto la profondità massima
        if max_depth is not None and depth > max_depth:
            return
        
        file_handle.write(f"{prefix}{root_path.name}/\n")
        new_prefix = prefix + '    '
        
        try:
            for entry in sorted(root_path.iterdir(), key=lambda e: (not e.is_dir(), e.name)):
                if entry.is_dir():
                    self._print_structure(entry, file_handle, new_prefix, 
                                         depth + 1, max_depth, include_files)
                elif include_files and self.is_included_file(entry.name):  # Usa il nuovo metodo
                    file_handle.write(f"{new_prefix}{entry.name}\n")
        except PermissionError:
            # Ignora directory a cui non abbiamo accesso
            pass
    
    def _build_structure_dict(self, path, depth=0, max_depth=None, include_files=True):
        """Costruisce un dizionario con la struttura della directory per l'esportazione JSON"""
        if self.is_excluded_dir(path.name):  # Sostituito con il nuovo metodo
            return None
        
        # Verifichiamo se abbiamo raggiunto la profondità massima
        if max_depth is not None and depth > max_depth:
            return None
        
        result = {"name": path.name, "type": "directory", "children": []}
        
        try:
            for entry in sorted(path.iterdir(), key=lambda e: (not e.is_dir(), e.name)):
                if entry.is_dir():
                    child = self._build_structure_dict(entry, depth + 1, max_depth, include_files)
                    if child:
                        result["children"].append(child)
                elif include_files and self.is_included_file(entry.name):  # Sostituito con il nuovo metodo
                    result["children"].append({
                        "name": entry.name,
                        "type": "file",
                        "extension": entry.suffix
                    })
        except PermissionError:
            pass
            
        return result
    
    def _build_structure_xml(self, path, parent_elem, depth=0, max_depth=None, include_files=True):
        """Costruisce un elemento XML con la struttura della directory"""
        if self.is_excluded_dir(path.name):  # Usa il nuovo metodo
            return
        
        # Verifichiamo se abbiamo raggiunto la profondità massima
        if max_depth is not None and depth > max_depth:
            return
        
        try:
            for entry in sorted(path.iterdir(), key=lambda e: (not e.is_dir(), e.name)):
                if entry.is_dir():
                    if not self.is_excluded_dir(entry.name):  # Usa il nuovo metodo
                        dir_elem = ET.SubElement(parent_elem, "directory", name=entry.name)
                        self._build_structure_xml(entry, dir_elem, depth + 1, max_depth, include_files)
                elif include_files and self.is_included_file(entry.name):  # Usa il nuovo metodo
                    ET.SubElement(parent_elem, "file", name=entry.name, extension=entry.suffix)
        except PermissionError:
            # Ignora directory a cui non abbiamo accesso
            pass
    
    def _build_structure_html(self, path, indent=0, depth=0, max_depth=None, include_files=True):
        """Costruisce il codice HTML per la struttura della directory"""
        if self.is_excluded_dir(path.name):  # Usa il nuovo metodo
            return ""
        
        # Verifichiamo se abbiamo raggiunto la profondità massima
        if max_depth is not None and depth > max_depth:
            return ""
        
        indent_str = " " * indent
        result = f"{indent_str}<li><span class=\"directory\">{path.name}/</span>\n{indent_str}    <ul>\n"
        
        try:
            for entry in sorted(path.iterdir(), key=lambda e: (not e.is_dir(), e.name)):
                if entry.is_dir():
                    if not self.is_excluded_dir(entry.name):  # Usa il nuovo metodo
                        result += self._build_structure_html(entry, indent + 8, 
                                                            depth + 1, max_depth, include_files)
                elif include_files and self.is_included_file(entry.name):  # Usa il nuovo metodo
                    result += f"{indent_str}        <li><span class=\"file\">{entry.name}</span></li>\n"
        except PermissionError:
            # Ignora directory a cui non abbiamo accesso
            pass
            
        result += f"{indent_str}    </ul>\n{indent_str}</li>\n"
        return result
    
    # ----- METODI PER LA GESTIONE DELLE CONFIGURAZIONI -----
    
    def save_config(self, config_file):
        """Salva la configurazione corrente in un file JSON"""
        # Converti date e valori speciali
        max_file_size = self.max_file_size
        if max_file_size == float('inf'):
            max_file_size = "inf"
        
        config = {
            # Configurazioni esistenti
            "excluded_dirs": list(self.excluded_dirs),
            "excluded_dirs_regex": list(self.excluded_dirs_regex),
            "included_file_extensions": list(self.included_file_extensions),
            "included_file_regex": list(self.included_file_regex),
            
            # Nuove configurazioni
            "min_file_size": self.min_file_size,
            "max_file_size": max_file_size,
            "min_creation_date": self.min_creation_date,
            "max_creation_date": self.max_creation_date,
            "min_modification_date": self.min_modification_date,
            "max_modification_date": self.max_modification_date,
            
            # Presets
            "filter_presets": {
                name: {
                    # Converti i set in liste per JSON
                    "excluded_dirs": list(preset["excluded_dirs"]),
                    "excluded_dirs_regex": list(preset["excluded_dirs_regex"]),
                    "included_file_extensions": list(preset["included_file_extensions"]),
                    "included_file_regex": list(preset["included_file_regex"]),
                    
                    "min_file_size": preset["min_file_size"],
                    "max_file_size": "inf" if preset["max_file_size"] == float('inf') else preset["max_file_size"],
                    "min_creation_date": preset["min_creation_date"],
                    "max_creation_date": preset["max_creation_date"],
                    "min_modification_date": preset["min_modification_date"],
                    "max_modification_date": preset["max_modification_date"]
                } for name, preset in self.filter_presets.items()
            }
        }

        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
            return True, f"Configurazione salvata in '{config_file}'."
        except Exception as e:
            return False, f"Errore durante il salvataggio: {e}"
    
    def load_config(self, config_file):
        """Carica la configurazione da un file JSON"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.excluded_dirs = set(config.get("excluded_dirs", []))
            self.included_file_extensions = set(config.get("included_file_extensions", []))
            return True, "Configurazione caricata con successo."
        except Exception as e:
            return False, f"Errore durante il caricamento: {e}"
    
    # ----- METODI PER L'ANTEPRIMA -----
    
    def generate_preview(self, root_dir, max_items=100, include_files=True, max_depth=None):
        """Genera un'anteprima della struttura senza salvarla su file"""
        lines = []
        self._generate_preview_recursive(root_dir, lines, max_items, prefix='', 
                                        depth=0, max_depth=max_depth, include_files=include_files)
        return lines[:max_items]
    
    def _generate_preview_recursive(self, root_dir, lines, max_items, prefix='', 
                               depth=0, max_depth=None, include_files=True):
        """Funzione ricorsiva per generare l'anteprima"""
        if len(lines) >= max_items:
            return
            
        root_path = Path(root_dir)
        if self.is_excluded_dir(root_path.name):  # Usa il nuovo metodo
            return

        # Verifichiamo se abbiamo raggiunto la profondità massima
        if max_depth is not None and depth > max_depth:
            return
        
        lines.append(f"{prefix}{root_path.name}/")
        new_prefix = prefix + '    '
        
        try:
            for entry in sorted(root_path.iterdir(), key=lambda e: (not e.is_dir(), e.name)):
                if len(lines) >= max_items:
                    return
                    
                if entry.is_dir():
                    self._generate_preview_recursive(entry, lines, max_items, new_prefix, 
                                                depth + 1, max_depth, include_files)
                elif include_files and self.is_included_file(entry.name):  # Usa il nuovo metodo
                    lines.append(f"{new_prefix}{entry.name}")
        except PermissionError:
            # Ignora directory a cui non abbiamo accesso
            pass