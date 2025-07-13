import json

class ConfigManager:
    def __init__(self, filter_manager, settings=None):
        self.filter_manager = filter_manager
        self.settings = settings
        self.filter_presets = {}
        self.load_presets()

    def save_filter_preset(self, preset_name):
        """Salva la configurazione attuale dei filtri come preset"""
        self.filter_presets[preset_name] = {
            # Filtri directory
            'excluded_dirs': set(self.filter_manager.excluded_dirs),
            'excluded_dirs_regex': set(self.filter_manager.excluded_dirs_regex),
            
            # Filtri file - NUOVO
            'excluded_files': set(self.filter_manager.excluded_files),
            'excluded_files_regex': set(self.filter_manager.excluded_files_regex),
            
            # Filtri estensioni
            'included_file_extensions': set(self.filter_manager.included_file_extensions),
            'included_file_regex': set(self.filter_manager.included_file_regex),
            
            # Filtri dimensione e data
            'min_file_size': self.filter_manager.min_file_size,
            'max_file_size': self.filter_manager.max_file_size, 
            'min_creation_date': self.filter_manager.min_creation_date,
            'max_creation_date': self.filter_manager.max_creation_date,
            'min_modification_date': self.filter_manager.min_modification_date,
            'max_modification_date': self.filter_manager.max_modification_date
        }
        return True, f"Preset '{preset_name}' salvato con successo."
    
    def load_filter_preset(self, preset_name):
        """Carica una configurazione di filtri salvata"""
        if preset_name not in self.filter_presets:
            return False, f"Preset '{preset_name}' non trovato."
        
        preset = self.filter_presets[preset_name]
        
        # Carica tutti i filtri dal preset
        self.filter_manager.excluded_dirs = set(preset['excluded_dirs'])
        self.filter_manager.excluded_dirs_regex = set(preset['excluded_dirs_regex'])
        
        # File esclusi - NUOVO
        self.filter_manager.excluded_files = set(preset.get('excluded_files', set()))
        self.filter_manager.excluded_files_regex = set(preset.get('excluded_files_regex', set()))
        
        self.filter_manager.included_file_extensions = set(preset['included_file_extensions'])
        self.filter_manager.included_file_regex = set(preset['included_file_regex'])
        self.filter_manager.min_file_size = preset['min_file_size']
        self.filter_manager.max_file_size = preset['max_file_size']
        self.filter_manager.min_creation_date = preset['min_creation_date']
        self.filter_manager.max_creation_date = preset['max_creation_date']
        self.filter_manager.min_modification_date = preset['min_modification_date']
        self.filter_manager.max_modification_date = preset['max_modification_date']
        
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
    
    def save_config(self, config_file):
        """Salva la configurazione corrente in un file JSON"""
        max_file_size = self.filter_manager.max_file_size
        if max_file_size == float('inf'):
            max_file_size = "inf"
        
        config = {
            # Directory
            "excluded_dirs": list(self.filter_manager.excluded_dirs),
            "excluded_dirs_regex": list(self.filter_manager.excluded_dirs_regex),
            
            # File - NUOVO
            "excluded_files": list(self.filter_manager.excluded_files),
            "excluded_files_regex": list(self.filter_manager.excluded_files_regex),
            
            # Estensioni
            "included_file_extensions": list(self.filter_manager.included_file_extensions),
            "included_file_regex": list(self.filter_manager.included_file_regex),
            
            # Dimensione e data
            "min_file_size": self.filter_manager.min_file_size,
            "max_file_size": max_file_size,
            "min_creation_date": self.filter_manager.min_creation_date,
            "max_creation_date": self.filter_manager.max_creation_date,
            "min_modification_date": self.filter_manager.min_modification_date,
            "max_modification_date": self.filter_manager.max_modification_date,
            
            # Presets
            "filter_presets": {
                name: {
                    # Directory
                    "excluded_dirs": list(preset["excluded_dirs"]),
                    "excluded_dirs_regex": list(preset["excluded_dirs_regex"]),
                    
                    # File - NUOVO
                    "excluded_files": list(preset.get("excluded_files", set())),
                    "excluded_files_regex": list(preset.get("excluded_files_regex", set())),
                    
                    # Estensioni
                    "included_file_extensions": list(preset["included_file_extensions"]),
                    "included_file_regex": list(preset["included_file_regex"]),
                    
                    # Dimensione e data
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
            
            # Directory
            self.filter_manager.excluded_dirs = set(config.get("excluded_dirs", []))
            self.filter_manager.excluded_dirs_regex = set(config.get("excluded_dirs_regex", []))
            
            # File - NUOVO
            self.filter_manager.excluded_files = set(config.get("excluded_files", []))
            self.filter_manager.excluded_files_regex = set(config.get("excluded_files_regex", []))
            
            # Estensioni
            self.filter_manager.included_file_extensions = set(config.get("included_file_extensions", []))
            self.filter_manager.included_file_regex = set(config.get("included_file_regex", []))
            
            # Dimensione e data
            self.filter_manager.min_file_size = config.get("min_file_size", 0)
            
            max_file_size = config.get("max_file_size", "inf")
            self.filter_manager.max_file_size = float('inf') if max_file_size == "inf" else float(max_file_size)
            
            self.filter_manager.min_creation_date = config.get("min_creation_date")
            self.filter_manager.max_creation_date = config.get("max_creation_date")
            self.filter_manager.min_modification_date = config.get("min_modification_date")
            self.filter_manager.max_modification_date = config.get("max_modification_date")
            
            # Carica i preset
            presets = config.get("filter_presets", {})
            self.filter_presets = {}
            
            for name, preset_data in presets.items():
                max_size = preset_data.get("max_file_size", "inf")
                preset = {
                    # Directory
                    "excluded_dirs": set(preset_data.get("excluded_dirs", [])),
                    "excluded_dirs_regex": set(preset_data.get("excluded_dirs_regex", [])),
                    
                    # File - NUOVO (con retrocompatibilità)
                    "excluded_files": set(preset_data.get("excluded_files", [])),
                    "excluded_files_regex": set(preset_data.get("excluded_files_regex", [])),
                    
                    # Estensioni
                    "included_file_extensions": set(preset_data.get("included_file_extensions", [])),
                    "included_file_regex": set(preset_data.get("included_file_regex", [])),
                    
                    # Dimensione e data
                    "min_file_size": preset_data.get("min_file_size", 0),
                    "max_file_size": float('inf') if max_size == "inf" else float(max_size),
                    "min_creation_date": preset_data.get("min_creation_date"),
                    "max_creation_date": preset_data.get("max_creation_date"),
                    "min_modification_date": preset_data.get("min_modification_date"),
                    "max_modification_date": preset_data.get("max_modification_date")
                }
                self.filter_presets[name] = preset
            
            return True, "Configurazione caricata con successo."
        except Exception as e:
            return False, f"Errore durante il caricamento: {e}"
        
    def save_presets(self, presets_file=None):
        """Salva i preset in un file JSON"""
        if presets_file is None and self.settings:
            presets_file = self.settings.value("presets_path", "presets.json")
        elif presets_file is None:
            presets_file = "presets.json"
            
        presets_data = {}
        for name, preset in self.filter_presets.items():
            presets_data[name] = {
                # Directory
                "excluded_dirs": list(preset["excluded_dirs"]),
                "excluded_dirs_regex": list(preset["excluded_dirs_regex"]),
                
                # File - NUOVO
                "excluded_files": list(preset.get("excluded_files", set())),
                "excluded_files_regex": list(preset.get("excluded_files_regex", set())),
                
                # Estensioni
                "included_file_extensions": list(preset["included_file_extensions"]),
                "included_file_regex": list(preset["included_file_regex"]),
                
                # Dimensione e data
                "min_file_size": preset["min_file_size"],
                "max_file_size": "inf" if preset["max_file_size"] == float('inf') else preset["max_file_size"],
                "min_creation_date": preset["min_creation_date"],
                "max_creation_date": preset["max_creation_date"],
                "min_modification_date": preset["min_modification_date"],
                "max_modification_date": preset["max_modification_date"]
            }
        
        try:
            with open(presets_file, 'w', encoding='utf-8') as f:
                json.dump(presets_data, f, indent=4)
            return True
        except Exception:
            return False

    def load_presets(self, presets_file=None):
        """Carica i preset da un file JSON"""
        if presets_file is None and self.settings:
            presets_file = self.settings.value("presets_path", "presets.json")
        elif presets_file is None:
            presets_file = "presets.json"

        try:
            with open(presets_file, 'r', encoding='utf-8') as f:
                presets_data = json.load(f)
            
            for name, preset_data in presets_data.items():
                max_size = preset_data.get("max_file_size", "inf")
                preset = {
                    # Directory
                    "excluded_dirs": set(preset_data.get("excluded_dirs", [])),
                    "excluded_dirs_regex": set(preset_data.get("excluded_dirs_regex", [])),
                    
                    # File - NUOVO (con retrocompatibilità)
                    "excluded_files": set(preset_data.get("excluded_files", [])),
                    "excluded_files_regex": set(preset_data.get("excluded_files_regex", [])),
                    
                    # Estensioni
                    "included_file_extensions": set(preset_data.get("included_file_extensions", [])),
                    "included_file_regex": set(preset_data.get("included_file_regex", [])),
                    
                    # Dimensione e data
                    "min_file_size": preset_data.get("min_file_size", 0),
                    "max_file_size": float('inf') if max_size == "inf" else float(max_size),
                    "min_creation_date": preset_data.get("min_creation_date"),
                    "max_creation_date": preset_data.get("max_creation_date"),
                    "min_modification_date": preset_data.get("min_modification_date"),
                    "max_modification_date": preset_data.get("max_modification_date")
                }
                self.filter_presets[name] = preset
            
            return True
        except Exception:
            self.filter_presets = {}
            return False