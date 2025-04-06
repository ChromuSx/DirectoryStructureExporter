from pathlib import Path
import json
import xml.dom.minidom as minidom
import xml.etree.ElementTree as ET

class DirectoryExporter:
    def __init__(self, filter_manager):
        self.filter_manager = filter_manager
    
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
        if self.filter_manager.is_excluded_dir(root_path.name):
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
                elif include_files and self.filter_manager.is_included_file(entry):
                    file_handle.write(f"{new_prefix}{entry.name}\n")
        except PermissionError:
            # Ignora directory a cui non abbiamo accesso
            pass
    
    def _build_structure_dict(self, path, depth=0, max_depth=None, include_files=True):
        """Costruisce un dizionario con la struttura della directory per l'esportazione JSON"""
        if self.filter_manager.is_excluded_dir(path.name):
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
                elif include_files and self.filter_manager.is_included_file(entry):
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
        if self.filter_manager.is_excluded_dir(path.name):
            return
        
        # Verifichiamo se abbiamo raggiunto la profondità massima
        if max_depth is not None and depth > max_depth:
            return
        
        try:
            for entry in sorted(path.iterdir(), key=lambda e: (not e.is_dir(), e.name)):
                if entry.is_dir():
                    if not self.filter_manager.is_excluded_dir(entry.name):
                        dir_elem = ET.SubElement(parent_elem, "directory", name=entry.name)
                        self._build_structure_xml(entry, dir_elem, depth + 1, max_depth, include_files)
                elif include_files and self.filter_manager.is_included_file(entry):
                    ET.SubElement(parent_elem, "file", name=entry.name, extension=entry.suffix)
        except PermissionError:
            # Ignora directory a cui non abbiamo accesso
            pass
    
    def _build_structure_html(self, path, indent=0, depth=0, max_depth=None, include_files=True):
        """Costruisce il codice HTML per la struttura della directory"""
        if self.filter_manager.is_excluded_dir(path.name):
            return ""
        
        # Verifichiamo se abbiamo raggiunto la profondità massima
        if max_depth is not None and depth > max_depth:
            return ""
        
        indent_str = " " * indent
        result = f"{indent_str}<li><span class=\"directory\">{path.name}/</span>\n{indent_str}    <ul>\n"
        
        try:
            for entry in sorted(path.iterdir(), key=lambda e: (not e.is_dir(), e.name)):
                if entry.is_dir():
                    if not self.filter_manager.is_excluded_dir(entry.name):
                        result += self._build_structure_html(entry, indent + 8, 
                                                           depth + 1, max_depth, include_files)
                elif include_files and self.filter_manager.is_included_file(entry):
                    result += f"{indent_str}        <li><span class=\"file\">{entry.name}</span></li>\n"
        except PermissionError:
            # Ignora directory a cui non abbiamo accesso
            pass
            
        result += f"{indent_str}    </ul>\n{indent_str}</li>\n"
        return result
    
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
        if self.filter_manager.is_excluded_dir(root_path.name):
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
                elif include_files and self.filter_manager.is_included_file(entry):
                    lines.append(f"{new_prefix}{entry.name}")
        except PermissionError:
            # Ignora directory a cui non abbiamo accesso
            pass