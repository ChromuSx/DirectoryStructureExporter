from pathlib import Path
import os

def normalize_path(path):
    """Normalizza un percorso per il sistema operativo corrente"""
    return str(Path(path))

def is_subpath(parent, child):
    """Verifica se un percorso è sottodirettorio di un altro"""
    parent_path = Path(parent).resolve()
    child_path = Path(child).resolve()
    return parent_path in child_path.parents

def get_relative_path(from_path, to_path):
    """Ottiene il percorso relativo da un percorso a un altro"""
    from_path = Path(from_path).resolve()
    to_path = Path(to_path).resolve()
    return os.path.relpath(to_path, from_path)

def get_common_ancestor(path1, path2):
    """Trova il percorso comune più profondo tra due percorsi"""
    path1 = Path(path1).resolve().parts
    path2 = Path(path2).resolve().parts
    common = []
    
    for p1, p2 in zip(path1, path2):
        if p1 == p2:
            common.append(p1)
        else:
            break
    
    if not common:
        return None
    
    if os.name == 'nt':  # Windows
        return Path('\\'.join(common))
    else:  # Unix
        return Path('/'.join(common) if common[0] == '/' else common[0] + '/' + '/'.join(common[1:]))

def ensure_directory_exists(path):
    """Assicura che una directory esista, creandola se necessario"""
    directory = Path(path)
    if not directory.exists():
        directory.mkdir(parents=True)
    return directory.exists() and directory.is_dir()

def is_path_valid(path):
    """Verifica se un percorso è valido nel sistema operativo corrente"""
    try:
        Path(path)
        return True
    except (ValueError, OSError):
        return False