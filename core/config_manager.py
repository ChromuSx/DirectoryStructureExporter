import json

class ConfigManager:
    def __init__(self, filter_manager, settings=None):
        self.filter_manager = filter_manager
        self.settings = settings  # Aggiungiamo l'oggetto settings
        self.filter_presets = {}  # Nome -> configurazione
        self.load_presets()

    
    def save_filter_preset(self, preset_name):
        """Salva la configurazione attuale dei filtri come preset"""
        self.filter_presets[preset_name] = {
            # Filtri esistenti
            'excluded_dirs': set(self.filter_manager.excluded_dirs),
            'excluded_dirs_regex': set(self.filter_manager.excluded_dirs_regex),
            'included_file_extensions': set(self.filter_manager.included_file_extensions),
            'included_file_regex': set(self.filter_manager.included_file_regex),
            
            # Nuovi filtri
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
        # Converti date e valori speciali
        max_file_size = self.filter_manager.max_file_size
        if max_file_size == float('inf'):
            max_file_size = "inf"
        
        config = {
            # Configurazioni esistenti
            "excluded_dirs": list(self.filter_manager.excluded_dirs),
            "excluded_dirs_regex": list(self.filter_manager.excluded_dirs_regex),
            "included_file_extensions": list(self.filter_manager.included_file_extensions),
            "included_file_regex": list(self.filter_manager.included_file_regex),
            
            # Nuove configurazioni
            "min_file_size": self.filter_manager.min_file_size,
            "max_file_size": max_file_size,
            "min_creation_date": self.filter_manager.min_creation_date,
            "max_creation_date": self.filter_manager.max_creation_date,
            "min_modification_date": self.filter_manager.min_modification_date,
            "max_modification_date": self.filter_manager.max_modification_date,
            
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
            
            # Carica le configurazioni di base
            self.filter_manager.excluded_dirs = set(config.get("excluded_dirs", []))
            self.filter_manager.excluded_dirs_regex = set(config.get("excluded_dirs_regex", []))
            self.filter_manager.included_file_extensions = set(config.get("included_file_extensions", []))
            self.filter_manager.included_file_regex = set(config.get("included_file_regex", []))
            
            # Carica i filtri avanzati
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
                    "excluded_dirs": set(preset_data.get("excluded_dirs", [])),
                    "excluded_dirs_regex": set(preset_data.get("excluded_dirs_regex", [])),
                    "included_file_extensions": set(preset_data.get("included_file_extensions", [])),
                    "included_file_regex": set(preset_data.get("included_file_regex", [])),
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
        
    # In ConfigManager
    def save_presets(self, presets_file=None):
        """Salva i preset in un file JSON"""
        if presets_file is None and self.settings:
            # Usa un file predefinito nella directory dell'applicazione
            presets_file = self.settings.value("presets_path", "presets.json")
        elif presets_file is None:
            presets_file = "presets.json"
        presets_data = {}
        for name, preset in self.filter_presets.items():
            presets_data[name] = {
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
            # Usa un file predefinito nella directory dell'applicazione
            presets_file = self.settings.value("presets_path", "presets.json")
        elif presets_file is None:
            presets_file = "presets.json"

        try:
            with open(presets_file, 'r', encoding='utf-8') as f:
                presets_data = json.load(f)
            
            for name, preset_data in presets_data.items():
                max_size = preset_data.get("max_file_size", "inf")
                preset = {
                    "excluded_dirs": set(preset_data.get("excluded_dirs", [])),
                    "excluded_dirs_regex": set(preset_data.get("excluded_dirs_regex", [])),
                    "included_file_extensions": set(preset_data.get("included_file_extensions", [])),
                    "included_file_regex": set(preset_data.get("included_file_regex", [])),
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
            # Se il file non esiste o c'è un errore, inizializziamo con preset vuoti
            self.filter_presets = {}
            return False