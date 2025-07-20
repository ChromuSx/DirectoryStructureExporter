#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script per costruire l'eseguibile del Directory Structure Exporter
"""

import os
import subprocess
import shutil
import sys

def clean_build_dirs():
    """Pulisce le cartelle di build precedenti"""
    dirs_to_clean = ['dist', 'build', '__pycache__']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"🧹 Pulendo {dir_name}/")
            shutil.rmtree(dir_name)
    
    # Pulisci anche i file .spec
    for file in os.listdir('.'):
        if file.endswith('.spec'):
            print(f"🧹 Rimuovendo {file}")
            os.remove(file)

def build_executable():
    """Costruisce l'eseguibile con PyInstaller"""
    
    print("🚀 Inizio build del Directory Structure Exporter...")
    
    # Pulisci prima
    clean_build_dirs()
    
    # Verifica che main.py esista
    if not os.path.exists('main.py'):
        print("❌ Errore: main.py non trovato!")
        return False
    
    # Comando PyInstaller base
    cmd = [
        'pyinstaller',
        '--onefile',                    # Un singolo file eseguibile
        '--windowed',                   # Nasconde la console (importante per GUI)
        '--name=DirectoryStructureExporter',     # Nome dell'eseguibile
        'main.py'
    ]
    
    # Aggiungi icona se esiste
    icon_paths = ['assets/logo.ico', 'assets/icon.ico', 'logo.ico']
    for icon_path in icon_paths:
        if os.path.exists(icon_path):
            cmd.append(f'--icon={icon_path}')
            print(f"🎨 Usando icona: {icon_path}")
            break
    
    # Aggiungi cartelle di risorse se esistono
    if os.path.exists('translations'):
        cmd.append('--add-data=translations;translations')
        print("📁 Aggiungendo cartella translations/")
    
    if os.path.exists('assets'):
        cmd.append('--add-data=assets;assets')
        print("📁 Aggiungendo cartella assets/")
    
    print(f"⚙️  Comando: {' '.join(cmd)}")
    print("⏳ Costruendo eseguibile (può richiedere alcuni minuti)...")
    
    try:
        # Esegui PyInstaller
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Verifica che l'eseguibile sia stato creato
        exe_path = 'dist/DirectoryStructureExporter.exe'
        if os.path.exists(exe_path):
            file_size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
            print(f"✅ Eseguibile creato con successo!")
            print(f"📍 Percorso: {os.path.abspath(exe_path)}")
            print(f"📏 Dimensione: {file_size:.1f} MB")
            return True
        else:
            print("❌ Errore: eseguibile non trovato in dist/")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Errore durante il build:")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Errore inaspettato: {e}")
        return False

def test_executable():
    """Testa l'eseguibile creato (opzionale)"""
    exe_path = 'dist/DirectoryStructureExporter.exe'
    
    if os.path.exists(exe_path):
        print("🧪 Vuoi testare l'eseguibile? (y/n): ", end='')
        if input().lower() == 'y':
            print("🚀 Avvio test...")
            try:
                subprocess.Popen([exe_path])
                print("✅ Test avviato - controlla che l'applicazione si apra correttamente")
            except Exception as e:
                print(f"❌ Errore nel test: {e}")

def main():
    """Funzione principale"""
    print("=" * 60)
    print("🏗️  BUILD SCRIPT - Directory Structure Exporter")
    print("=" * 60)
    
    # Verifica che PyInstaller sia installato
    try:
        subprocess.run(['pyinstaller', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ PyInstaller non trovato!")
        print("💡 Installa con: pip install pyinstaller")
        return
    
    # Costruisci
    if build_executable():
        print("\n🎉 Build completato con successo!")
        print("📦 L'eseguibile è pronto in dist/DirectoryStructureExporter.exe")
        print("💡 Puoi distribuire questo file singolo agli utenti")
        
        # Test opzionale
        test_executable()
        
        # Pulizia opzionale
        print("\n🧹 Vuoi pulire i file temporanei di build? (y/n): ", end='')
        if input().lower() == 'y':
            if os.path.exists('build'):
                shutil.rmtree('build')
            for file in os.listdir('.'):
                if file.endswith('.spec'):
                    os.remove(file)
            print("✅ File temporanei rimossi")
    else:
        print("\n💥 Build fallito!")
        print("💡 Controlla gli errori sopra e riprova")

if __name__ == "__main__":
    main()