import re
from pathlib import Path

class FilterManager:
    def __init__(self):
        # Filtri per directory
        self.excluded_dirs = {'.git', '.vs', 'bin', 'obj', 'Debug', 'Release', 'packages'}
        self.excluded_dirs_regex = set()
        
        # Filtri per file - NUOVI
        self.excluded_files = {'.gitignore', 'thumbs.db', '.DS_Store', 'desktop.ini', 'package-lock.json'}
        self.excluded_files_regex = set()
        
        # Filtri per estensioni (incluse)
        self.included_file_extensions = {'.sln', '.csproj', '.vbproj', '.cs', '.html', '.cshtml', '.css', '.js'}
        self.included_file_regex = set()
        
        # Filtri per dimensione file
        self.min_file_size = 0
        self.max_file_size = float('inf')
        
        # Filtri per data
        self.min_creation_date = None
        self.max_creation_date = None
        self.min_modification_date = None
        self.max_modification_date = None
    
    def is_excluded_dir(self, dir_name):
        """Verifica se la directory deve essere esclusa"""
        if dir_name in self.excluded_dirs:
            return True
            
        for pattern in self.excluded_dirs_regex:
            try:
                if re.search(pattern, dir_name):
                    return True
            except re.error:
                continue
                
        return False
    
    def is_excluded_file(self, file_path):
        """Verifica se il file deve essere escluso"""
        file_path = Path(file_path) if isinstance(file_path, str) else file_path
        file_name = file_path.name
        
        # Controllo nomi esatti
        if file_name.lower() in {f.lower() for f in self.excluded_files}:
            return True
            
        # Controllo con regex
        for pattern in self.excluded_files_regex:
            try:
                if re.search(pattern, file_name):
                    return True
            except re.error:
                continue
                
        return False
    
    def is_included_file(self, file_path):
        """Verifica se il file deve essere incluso in base a tutti i criteri"""
        file_path = Path(file_path) if isinstance(file_path, str) else file_path
        
        # PRIMA verifica se il file è esplicitamente escluso
        if self.is_excluded_file(file_path):
            return False
        
        # Verifica estensione/regex per inclusione
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
    
    # Metodi esistenti per directory...
    def add_excluded_dir(self, dir_name):
        self.excluded_dirs.add(dir_name)
    
    def remove_excluded_dir(self, dir_name):
        if dir_name in self.excluded_dirs:
            self.excluded_dirs.remove(dir_name)
    
    def add_excluded_dir_regex(self, pattern):
        try:
            re.compile(pattern)
            self.excluded_dirs_regex.add(pattern)
            return True
        except re.error:
            return False
    
    def remove_excluded_dir_regex(self, pattern):
        if pattern in self.excluded_dirs_regex:
            self.excluded_dirs_regex.remove(pattern)
    
    # NUOVI metodi per file esclusi
    def add_excluded_file(self, file_name):
        """Aggiunge un file alla lista dei file esclusi"""
        self.excluded_files.add(file_name)
    
    def remove_excluded_file(self, file_name):
        """Rimuove un file dalla lista dei file esclusi"""
        if file_name in self.excluded_files:
            self.excluded_files.remove(file_name)
    
    def add_excluded_file_regex(self, pattern):
        """Aggiunge un pattern regex alla lista dei file esclusi"""
        try:
            re.compile(pattern)
            self.excluded_files_regex.add(pattern)
            return True
        except re.error:
            return False
    
    def remove_excluded_file_regex(self, pattern):
        """Rimuove un pattern regex dalla lista dei file esclusi"""
        if pattern in self.excluded_files_regex:
            self.excluded_files_regex.remove(pattern)
    
    # Metodi esistenti per estensioni incluse...
    def add_included_ext(self, extension):
        if not extension.startswith('.'):
            extension = f".{extension}"
        self.included_file_extensions.add(extension)
    
    def remove_included_ext(self, extension):
        if extension in self.included_file_extensions:
            self.included_file_extensions.remove(extension)
    
    def add_included_file_regex(self, pattern):
        try:
            re.compile(pattern)
            self.included_file_regex.add(pattern)
            return True
        except re.error:
            return False
    
    def remove_included_file_regex(self, pattern):
        if pattern in self.included_file_regex:
            self.included_file_regex.remove(pattern)
    
    def set_size_filters(self, min_size, max_size):
        self.min_file_size = min_size
        self.max_file_size = float('inf') if max_size == 0 else max_size
    
    def set_creation_date_filters(self, min_date, max_date):
        self.min_creation_date = min_date
        self.max_creation_date = max_date
    
    def set_modification_date_filters(self, min_date, max_date):
        self.min_modification_date = min_date
        self.max_modification_date = max_date
    
    def reset_filters(self):
        """Reimposta tutti i filtri ai valori predefiniti"""
        self.excluded_dirs = {'.git', '.vs', 'bin', 'obj', 'Debug', 'Release', 'packages'}
        self.excluded_dirs_regex = set()
        self.excluded_files = {'.gitignore', 'thumbs.db', '.DS_Store', 'desktop.ini', 'package-lock.json'}
        self.excluded_files_regex = set()
        self.included_file_extensions = {'.sln', '.csproj', '.vbproj', '.cs', '.html', '.cshtml', '.css', '.js'}
        self.included_file_regex = set()
        self.min_file_size = 0
        self.max_file_size = float('inf')
        self.min_creation_date = None
        self.max_creation_date = None
        self.min_modification_date = None
        self.max_modification_date = None