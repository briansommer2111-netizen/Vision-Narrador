#!/usr/bin/env python3
"""
Vision-Narrador: Script de Instalación y Configuración
======================================================

Script automático para instalar dependencias y configurar el entorno
de Vision-Narrador de forma sencilla y robusta.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, TaskID
from rich.panel import Panel

console = Console()

def check_python_version():
    """Verificar versión de Python"""
    version = sys.version_info
    if version.major != 3 or version.minor < 9:
        console.print(f"❌ [red]Error: Se requiere Python 3.9+, tienes {version.major}.{version.minor}[/red]")
        return False
    
    console.print(f"✅ [green]Python {version.major}.{version.minor}.{version.micro} detectado[/green]")
    return True

def install_dependencies():
    """Instalar dependencias del requirements.txt"""
    console.print("\n📦 [bold]Instalando dependencias...[/bold]")
    
    try:
        # Actualizar pip
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True, capture_output=True)
        
        # Instalar dependencias
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        
        console.print("✅ [green]Dependencias instaladas correctamente[/green]")
        return True
        
    except subprocess.CalledProcessError as e:
        console.print(f"❌ [red]Error instalando dependencias: {e}[/red]")
        return False

def setup_spacy_models():
    """Instalar modelos de spaCy"""
    console.print("\n🧠 [bold]Configurando modelos de spaCy...[/bold]")
    
    models = ["es_core_news_lg", "es_core_news_sm"]
    
    for model in models:
        try:
            console.print(f"📥 Descargando {model}...")
            subprocess.run([sys.executable, "-m", "spacy", "download", model], 
                          check=True, capture_output=True)
            console.print(f"✅ [green]{model} instalado[/green]")
            break  # Si se instala uno exitosamente, salir
        except subprocess.CalledProcessError:
            console.print(f"⚠️ [yellow]Error instalando {model}, intentando siguiente...[/yellow]")
            continue
    else:
        console.print("❌ [red]No se pudo instalar ningún modelo de spaCy[/red]")
        return False
    
    return True

def create_example_project():
    """Crear proyecto de ejemplo"""
    console.print("\n📁 [bold]Creando proyecto de ejemplo...[/bold]")
    
    try:
        from config import VisionNarradorConfig
        
        # Crear configuración para proyecto de ejemplo
        example_path = Path("./ejemplo_novela")
        config = VisionNarradorConfig(str(example_path))
        config.initialize_project()
        
        console.print(f"✅ [green]Proyecto de ejemplo creado en: {example_path}[/green]")
        return True
        
    except Exception as e:
        console.print(f"❌ [red]Error creando proyecto de ejemplo: {e}[/red]")
        return False

def run_system_tests():
    """Ejecutar pruebas del sistema"""
    console.print("\n🧪 [bold]Ejecutando pruebas del sistema...[/bold]")
    
    tests = [
        ("Importar configuración", lambda: __import__("config")),
        ("Importar workspace_manager_avanzado", lambda: __import__("workspace_manager_avanzado")),
        ("Importar multilayer_ner_avanzado", lambda: __import__("multilayer_ner_avanzado")),
        ("Importar ai_chat_interface", lambda: __import__("ai_chat_interface")),
        ("Importar tts_handler_ultraconfiable", lambda: __import__("tts_handler_ultraconfiable")),
        ("Importar pipeline principal", lambda: __import__("vision_narrador_pipeline")),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            console.print(f"✅ [green]{test_name}[/green]")
            passed += 1
        except Exception as e:
            console.print(f"❌ [red]{test_name}: {e}[/red]")
            failed += 1
    
    console.print(f"\n📊 Resultados: {passed} exitosas, {failed} fallidas")
    return failed == 0

def display_completion_message():
    """Mostrar mensaje de finalización"""
    message = """
🎉 ¡Instalación Completada!

Vision-Narrador está listo para usar.

🚀 Comandos para empezar:

# Ejecutar en modo interactivo
python main.py

# Procesar capítulos automáticamente  
python main.py --process

# Abrir chat IA
python main.py --chat

# Ver ayuda completa
python main.py --help

📚 Documentación adicional:
• README.md - Guía de inicio
• docs/ - Documentación completa
• ejemplo_novela/ - Proyecto de ejemplo

¡Disfruta creando tus videos webtoon! 🎬
    """
    
    panel = Panel.fit(
        message,
        title="[bold green]Instalación Exitosa[/bold green]",
        border_style="green"
    )
    
    console.print(panel)

def main():
    """Función principal de instalación"""
    # Banner
    banner = """
🎬 Vision-Narrador Setup

Instalador automático para el sistema de conversión
de novelas a videos webtoon.
    """
    
    console.print(Panel.fit(
        banner,
        title="[bold cyan]Bienvenido al Instalador[/bold cyan]",
        border_style="cyan"
    ))
    
    # Verificaciones y instalación
    steps = [
        ("Verificar Python", check_python_version),
        ("Instalar dependencias", install_dependencies), 
        ("Configurar modelos spaCy", setup_spacy_models),
        ("Crear proyecto ejemplo", create_example_project),
        ("Ejecutar pruebas", run_system_tests)
    ]
    
    failed_steps = []
    
    with Progress() as progress:
        task = progress.add_task("[cyan]Configurando Vision-Narrador...", total=len(steps))
        
        for step_name, step_func in steps:
            progress.update(task, description=f"[cyan]{step_name}...")
            
            if step_func():
                console.print(f"✅ [green]{step_name} completado[/green]")
            else:
                console.print(f"❌ [red]{step_name} falló[/red]")
                failed_steps.append(step_name)
            
            progress.advance(task)
    
    # Resultados
    if failed_steps:
        console.print(f"\n⚠️ [yellow]Instalación completada con errores en: {', '.join(failed_steps)}[/yellow]")
        console.print("💡 [blue]El sistema puede funcionar parcialmente. Revisa los errores arriba.[/blue]")
    else:
        display_completion_message()
    
    return len(failed_steps) == 0

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        console.print("\n⏹️ [yellow]Instalación cancelada[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"\n❌ [red]Error fatal en instalación: {e}[/red]")
        sys.exit(1)