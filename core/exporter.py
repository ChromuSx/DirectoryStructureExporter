from pathlib import Path
import json
import xml.dom.minidom as minidom
import xml.etree.ElementTree as ET

class DirectoryExporter:
    def __init__(self, filter_manager):
        self.filter_manager = filter_manager
        
        # Stili di indentazione disponibili
        self.indent_styles = {
            'spaces': {
                'name': 'Spazi',
                'dir_prefix': '',
                'file_prefix': '',
                'indent_char': '    '  # 4 spazi
            },
            'dashes': {
                'name': 'Trattini',
                'dir_prefix': '- ',
                'file_prefix': '- ',
                'indent_char': '  '  # 2 spazi + trattino
            },
            'tree': {
                'name': 'Albero',
                'dir_prefix': '',
                'file_prefix': '',
                'indent_char': ''  # Gestito dinamicamente
            },
            'bullets': {
                'name': 'Bullets',
                'dir_prefix': '• ',
                'file_prefix': '• ',
                'indent_char': '  '
            },
            'icons': {
                'name': 'Icone',
                'dir_prefix': '📁 ',
                'file_prefix': '📄 ',
                'indent_char': '  '
            },
            'arrows': {
                'name': 'Frecce',
                'dir_prefix': '▶ ',
                'file_prefix': '→ ',
                'indent_char': '  '
            }
        }
    
    def get_available_indent_styles(self):
        """Restituisce la lista degli stili di indentazione disponibili"""
        return {key: style['name'] for key, style in self.indent_styles.items()}
    
    def export_structure(self, root_dir, output_file_path, include_files=True, max_depth=None, indent_style='spaces'):
        """Esporta la struttura di directory nel file specificato in formato testo"""
        try:
            with open(output_file_path, 'w', encoding='utf-8') as output_file:
                if indent_style == 'tree':
                    self._print_structure_tree(root_dir, output_file, depth=0, 
                                             max_depth=max_depth, include_files=include_files, is_last=True)
                else:
                    self._print_structure_styled(root_dir, output_file, prefix='', depth=0, 
                                               max_depth=max_depth, include_files=include_files, indent_style=indent_style)
            return True, f"La struttura è stata esportata in '{output_file_path}'."
        except Exception as e:
            return False, f"Errore durante l'esportazione: {e}"
    
    def _print_structure_styled(self, root_dir, file_handle, prefix='', depth=0, max_depth=None, include_files=True, indent_style='spaces'):
        """Stampa la struttura con stile personalizzato"""
        root_path = Path(root_dir)
        if self.filter_manager.is_excluded_dir(root_path.name):
            return
        
        if max_depth is not None and depth > max_depth:
            return
        
        style = self.indent_styles.get(indent_style, self.indent_styles['spaces'])
        
        # Stampa la directory corrente
        dir_line = f"{prefix}{style['dir_prefix']}{root_path.name}/\n"
        file_handle.write(dir_line)
        
        # Calcola il nuovo prefisso
        if indent_style == 'spaces':
            new_prefix = prefix + style['indent_char']
        else:
            new_prefix = prefix + style['indent_char']
        
        try:
            entries = sorted(root_path.iterdir(), key=lambda e: (not e.is_dir(), e.name))
            
            for entry in entries:
                if entry.is_dir():
                    self._print_structure_styled(entry, file_handle, new_prefix, 
                                               depth + 1, max_depth, include_files, indent_style)
                elif include_files and self.filter_manager.is_included_file(entry):
                    file_line = f"{new_prefix}{style['file_prefix']}{entry.name}\n"
                    file_handle.write(file_line)
        except PermissionError:
            pass
    
    def _print_structure_tree(self, root_dir, file_handle, depth=0, max_depth=None, include_files=True, is_last=True, prefix=''):
        """Stampa la struttura in stile albero con caratteri ASCII"""
        root_path = Path(root_dir)
        if self.filter_manager.is_excluded_dir(root_path.name):
            return
        
        if max_depth is not None and depth > max_depth:
            return
        
        # Caratteri per l'albero
        if depth == 0:
            current_prefix = ''
            dir_line = f"{root_path.name}/\n"
        else:
            tree_char = '└── ' if is_last else '├── '
            current_prefix = prefix + tree_char
            dir_line = f"{current_prefix}{root_path.name}/\n"
        
        file_handle.write(dir_line)
        
        try:
            entries = sorted(root_path.iterdir(), key=lambda e: (not e.is_dir(), e.name))
            
            # Separa directory e file
            dirs = [e for e in entries if e.is_dir() and not self.filter_manager.is_excluded_dir(e.name)]
            files = [e for e in entries if e.is_file() and include_files and self.filter_manager.is_included_file(e)]
            
            all_items = dirs + files
            
            for i, entry in enumerate(all_items):
                is_last_item = (i == len(all_items) - 1)
                
                if depth == 0:
                    new_prefix = ''
                else:
                    new_prefix = prefix + ('    ' if is_last else '│   ')
                
                if entry.is_dir():
                    self._print_structure_tree(entry, file_handle, depth + 1, max_depth, 
                                             include_files, is_last_item, new_prefix)
                else:
                    tree_char = '└── ' if is_last_item else '├── '
                    if depth == 0:
                        file_line = f"{tree_char}{entry.name}\n"
                    else:
                        file_line = f"{new_prefix}{tree_char}{entry.name}\n"
                    file_handle.write(file_line)
        except PermissionError:
            pass
    
    def export_structure_html(self, root_dir, output_file_path, include_files=True, max_depth=None, indent_style='spaces'):
        """Esporta la struttura di directory in formato HTML"""
        root_path = Path(root_dir)
        
        # CSS aggiornato per supportare i diversi stili
        css_styles = self._get_html_css_for_style(indent_style)
        
        html = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Struttura Directory: {root_path.name}</title>
            <style>
                {css_styles}
            </style>
        </head>
        <body>
            <h1>Struttura Directory: {root_path.name}</h1>
            <div class="tree-container">
        """
        
        if indent_style == 'tree':
            html += self._build_structure_html_tree(root_path, depth=0, max_depth=max_depth, include_files=include_files)
        else:
            html += self._build_structure_html_styled(root_path, depth=0, max_depth=max_depth, include_files=include_files, indent_style=indent_style)
        
        html += """    </div>
        </body>
        </html>"""
        
        try:
            with open(output_file_path, 'w', encoding='utf-8') as f:
                f.write(html)
            return True, f"La struttura è stata esportata in formato HTML in '{output_file_path}'."
        except Exception as e:
            return False, f"Errore durante l'esportazione HTML: {e}"
    
    def _get_html_css_for_style(self, indent_style):
        """Restituisce il CSS appropriato per lo stile selezionato"""
        base_css = """
                body { font-family: 'Courier New', monospace; margin: 20px; line-height: 1.4; }
                .tree-container { background: #f8f9fa; padding: 20px; border-radius: 8px; }
                .directory { color: #0066cc; font-weight: bold; }
                .file { color: #333; }
                .tree-line { margin: 2px 0; }
        """
        
        if indent_style == 'tree':
            return base_css + """
                .tree-line { font-family: 'Courier New', monospace; white-space: pre; }
            """
        else:
            return base_css
    
    def _build_structure_html_styled(self, path, depth=0, max_depth=None, include_files=True, indent_style='spaces'):
        """Costruisce il codice HTML per la struttura con stile personalizzato"""
        if self.filter_manager.is_excluded_dir(path.name):
            return ""
        
        if max_depth is not None and depth > max_depth:
            return ""
        
        style = self.indent_styles.get(indent_style, self.indent_styles['spaces'])
        indent = style['indent_char'] * depth
        
        result = f'<div class="tree-line"><span class="directory">{indent}{style["dir_prefix"]}{path.name}/</span></div>\n'
        
        try:
            entries = sorted(path.iterdir(), key=lambda e: (not e.is_dir(), e.name))
            
            for entry in entries:
                if entry.is_dir():
                    if not self.filter_manager.is_excluded_dir(entry.name):
                        result += self._build_structure_html_styled(entry, depth + 1, max_depth, include_files, indent_style)
                elif include_files and self.filter_manager.is_included_file(entry):
                    file_indent = style['indent_char'] * (depth + 1)
                    result += f'<div class="tree-line"><span class="file">{file_indent}{style["file_prefix"]}{entry.name}</span></div>\n'
        except PermissionError:
            pass
            
        return result
    
    def _build_structure_html_tree(self, path, depth=0, max_depth=None, include_files=True, is_last=True, prefix=''):
        """Costruisce il codice HTML per la struttura in stile albero"""
        if self.filter_manager.is_excluded_dir(path.name):
            return ""
        
        if max_depth is not None and depth > max_depth:
            return ""
        
        if depth == 0:
            result = f'<div class="tree-line"><span class="directory">{path.name}/</span></div>\n'
            current_prefix = ''
        else:
            tree_char = '└── ' if is_last else '├── '
            result = f'<div class="tree-line"><span class="directory">{prefix}{tree_char}{path.name}/</span></div>\n'
            current_prefix = prefix + ('    ' if is_last else '│   ')
        
        try:
            entries = sorted(path.iterdir(), key=lambda e: (not e.is_dir(), e.name))
            dirs = [e for e in entries if e.is_dir() and not self.filter_manager.is_excluded_dir(e.name)]
            files = [e for e in entries if e.is_file() and include_files and self.filter_manager.is_included_file(e)]
            
            all_items = dirs + files
            
            for i, entry in enumerate(all_items):
                is_last_item = (i == len(all_items) - 1)
                
                if entry.is_dir():
                    result += self._build_structure_html_tree(entry, depth + 1, max_depth, include_files, is_last_item, current_prefix)
                else:
                    tree_char = '└── ' if is_last_item else '├── '
                    if depth == 0:
                        result += f'<div class="tree-line"><span class="file">{tree_char}{entry.name}</span></div>\n'
                    else:
                        result += f'<div class="tree-line"><span class="file">{current_prefix}{tree_char}{entry.name}</span></div>\n'
        except PermissionError:
            pass
            
        return result
    
    # Metodi esistenti per JSON e XML rimangono invariati
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
            rough_string = ET.tostring(root_elem, 'utf-8')
            reparsed = minidom.parseString(rough_string)
            pretty_xml = reparsed.toprettyxml(indent="  ")
            
            with open(output_file_path, 'w', encoding='utf-8') as f:
                f.write(pretty_xml)
                
            return True, f"La struttura è stata esportata in formato XML in '{output_file_path}'."
        except Exception as e:
            return False, f"Errore durante l'esportazione XML: {e}"
    
    # ----- METODI DI SUPPORTO ESISTENTI -----
    
    def _build_structure_dict(self, path, depth=0, max_depth=None, include_files=True):
        """Costruisce un dizionario con la struttura della directory per l'esportazione JSON"""
        if self.filter_manager.is_excluded_dir(path.name):
            return None
        
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
            pass
    
    def generate_preview(self, root_dir, max_items=100, include_files=True, max_depth=None, indent_style='spaces'):
        """Genera un'anteprima della struttura senza salvarla su file"""
        lines = []
        if indent_style == 'tree':
            self._generate_preview_tree(root_dir, lines, max_items, depth=0, max_depth=max_depth, include_files=include_files)
        else:
            self._generate_preview_styled(root_dir, lines, max_items, prefix='', depth=0, max_depth=max_depth, include_files=include_files, indent_style=indent_style)
        return lines[:max_items]
    
    def _generate_preview_styled(self, root_dir, lines, max_items, prefix='', depth=0, max_depth=None, include_files=True, indent_style='spaces'):
        """Funzione ricorsiva per generare l'anteprima con stile personalizzato"""
        if len(lines) >= max_items:
            return
            
        root_path = Path(root_dir)
        if self.filter_manager.is_excluded_dir(root_path.name):
            return

        if max_depth is not None and depth > max_depth:
            return
        
        style = self.indent_styles.get(indent_style, self.indent_styles['spaces'])
        lines.append(f"{prefix}{style['dir_prefix']}{root_path.name}/")
        new_prefix = prefix + style['indent_char']
        
        try:
            for entry in sorted(root_path.iterdir(), key=lambda e: (not e.is_dir(), e.name)):
                if len(lines) >= max_items:
                    return
                    
                if entry.is_dir():
                    self._generate_preview_styled(entry, lines, max_items, new_prefix, 
                                                depth + 1, max_depth, include_files, indent_style)
                elif include_files and self.filter_manager.is_included_file(entry):
                    lines.append(f"{new_prefix}{style['file_prefix']}{entry.name}")
        except PermissionError:
            pass
    
    def _generate_preview_tree(self, root_dir, lines, max_items, depth=0, max_depth=None, include_files=True, is_last=True, prefix=''):
        """Funzione ricorsiva per generare l'anteprima in stile albero"""
        if len(lines) >= max_items:
            return
            
        root_path = Path(root_dir)
        if self.filter_manager.is_excluded_dir(root_path.name):
            return

        if max_depth is not None and depth > max_depth:
            return
        
        if depth == 0:
            lines.append(f"{root_path.name}/")
            current_prefix = ''
        else:
            tree_char = '└── ' if is_last else '├── '
            lines.append(f"{prefix}{tree_char}{root_path.name}/")
            current_prefix = prefix + ('    ' if is_last else '│   ')
        
        try:
            entries = sorted(root_path.iterdir(), key=lambda e: (not e.is_dir(), e.name))
            dirs = [e for e in entries if e.is_dir() and not self.filter_manager.is_excluded_dir(e.name)]
            files = [e for e in entries if e.is_file() and include_files and self.filter_manager.is_included_file(e)]
            
            all_items = dirs + files
            
            for i, entry in enumerate(all_items):
                if len(lines) >= max_items:
                    return
                    
                is_last_item = (i == len(all_items) - 1)
                
                if entry.is_dir():
                    self._generate_preview_tree(entry, lines, max_items, depth + 1, max_depth, 
                                              include_files, is_last_item, current_prefix)
                else:
                    tree_char = '└── ' if is_last_item else '├── '
                    if depth == 0:
                        lines.append(f"{tree_char}{entry.name}")
                    else:
                        lines.append(f"{current_prefix}{tree_char}{entry.name}")
        except PermissionError:
            pass