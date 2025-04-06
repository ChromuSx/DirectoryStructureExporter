from pathlib import Path
import os
import datetime

def get_file_size(file_path):
    """Restituisce la dimensione del file in bytes"""
    try:
        return os.path.getsize(file_path)
    except (OSError, PermissionError):
        return 0

def get_file_creation_time(file_path):
    """Restituisce il timestamp di creazione del file"""
    try:
        return os.path.getctime(file_path)
    except (OSError, PermissionError):
        return 0

def get_file_modification_time(file_path):
    """Restituisce il timestamp di ultima modifica del file"""
    try:
        return os.path.getmtime(file_path)
    except (OSError, PermissionError):
        return 0

def format_file_size(size_bytes):
    """Formatta la dimensione del file in unità leggibili dall'uomo"""
    if size_bytes < 1024:
        return f"{size_bytes} bytes"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

def format_timestamp(timestamp):
    """Formatta un timestamp in una stringa di data/ora leggibile"""
    dt = datetime.datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def get_file_extension(file_path):
    """Restituisce l'estensione del file"""
    return Path(file_path).suffix.lower()

def get_filename(file_path):
    """Restituisce il nome del file senza percorso"""
    return Path(file_path).name

def is_directory_accessible(dir_path):
    """Verifica se la directory è accessibile"""
    try:
        os.listdir(dir_path)
        return True
    except (PermissionError, OSError):
        return False