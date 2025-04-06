import re
from pathlib import Path

class FilterManager:
    def __init__(self):
        # Filtri per directory
        self.excluded_dirs = {'.git', '.vs', 'bin', 'obj', 'Debug', 'Release', 'packages'}
        self.excluded_dirs_regex = set()
        
        # Filtri per file
        self.included_file_extensions = {'.sln', '.csproj', '.vbproj', '.cs', '.html', '.cshtml', '.css', '.js'}
        self.included_file_regex = set()
        
        # Filtri per dimensione file
        self.min_file_size = 0  # in bytes
        self.max_file_size = float('inf')  # in bytes
        
        # Filtri per data
        self.min_creation_date = None  # timestamp
        self.max_creation_date = None  # timestamp
        self.min_modification_date = None  # timestamp
        self.max_modification_date = None  # timestamp
    
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
        
        # Verifica estensione/regex
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
            
        # Verifica data di creazione
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
        
        return True
    
    def add_excluded_dir(self, dir_name):
        """Aggiunge una directory alla lista delle directory escluse"""
        self.excluded_dirs.add(dir_name)
    
    def remove_excluded_dir(self, dir_name):
        """Rimuove una directory dalla lista delle directory escluse"""
        if dir_name in self.excluded_dirs:
            self.excluded_dirs.remove(dir_name)
    
    def add_excluded_dir_regex(self, pattern):
        """Aggiunge un pattern regex alla lista delle directory escluse"""
        try:
            # Verifica se è una regex valida
            re.compile(pattern)
            self.excluded_dirs_regex.add(pattern)
            return True
        except re.error:
            return False
    
    def remove_excluded_dir_regex(self, pattern):
        """Rimuove un pattern regex dalla lista delle directory escluse"""
        if pattern in self.excluded_dirs_regex:
            self.excluded_dirs_regex.remove(pattern)
    
    def add_included_ext(self, extension):
        """Aggiunge un'estensione alla lista delle estensioni incluse"""
        if not extension.startswith('.'):
            extension = f".{extension}"
        self.included_file_extensions.add(extension)
    
    def remove_included_ext(self, extension):
        """Rimuove un'estensione dalla lista delle estensioni incluse"""
        if extension in self.included_file_extensions:
            self.included_file_extensions.remove(extension)
    
    def add_included_file_regex(self, pattern):
        """Aggiunge un pattern regex alla lista dei file inclusi"""
        try:
            # Verifica se è una regex valida
            re.compile(pattern)
            self.included_file_regex.add(pattern)
            return True
        except re.error:
            return False
    
    def remove_included_file_regex(self, pattern):
        """Rimuove un pattern regex dalla lista dei file inclusi"""
        if pattern in self.included_file_regex:
            self.included_file_regex.remove(pattern)
    
    def set_size_filters(self, min_size, max_size):
        """Imposta i filtri per la dimensione dei file"""
        self.min_file_size = min_size
        self.max_file_size = float('inf') if max_size == 0 else max_size
    
    def set_creation_date_filters(self, min_date, max_date):
        """Imposta i filtri per la data di creazione"""
        self.min_creation_date = min_date
        self.max_creation_date = max_date
    
    def set_modification_date_filters(self, min_date, max_date):
        """Imposta i filtri per la data di modifica"""
        self.min_modification_date = min_date
        self.max_modification_date = max_date
    
    def reset_filters(self):
        """Reimposta tutti i filtri ai valori predefiniti"""
        self.excluded_dirs = {'.git', '.vs', 'bin', 'obj', 'Debug', 'Release', 'packages'}
        self.excluded_dirs_regex = set()
        self.included_file_extensions = {'.sln', '.csproj', '.vbproj', '.cs', '.html', '.cshtml', '.css', '.js'}
        self.included_file_regex = set()
        self.min_file_size = 0
        self.max_file_size = float('inf')
        self.min_creation_date = None
        self.max_creation_date = None
        self.min_modification_date = None
        self.max_modification_date = None