#!/usr/bin/env python3
"""
Vision-Narrador: Punto de Entrada Principal
===========================================

Sistema completo para convertir novelas en videos animados estilo webtoon.
Este script proporciona una interfaz de línea de comandos fácil de usar.

Uso:
    python main.py                    # Iniciar interfaz interactiva
    python main.py --process         # Procesar nuevos capítulos
    python main.py --setup           # Configurar nuevo proyecto
    python main.py --chat            # Iniciar chat IA
    python main.py --status          # Mostrar estado del proyecto
"""

import asyncio
import argparse
import sys
import logging
import traceback
from pathlib import Path

# Rich para interfaz mejorada
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from rich.prompt import Confirm

# Módulos del sistema
from config import VisionNarradorConfig, DEFAULT_CONFIG
from vision_narrador_pipeline import VisionNarradorPipeline
from ai_chat_interface import AIChat


class VisionNarradorCLI:
    """Interfaz de línea de comandos principal"""
    
    def __init__(self):
        self.console = Console()
        self.config = None
        self.pipeline = None
        
    def setup_logging(self, verbose: bool = False):
        """Configurar logging global"""
        level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('vision_narrador_main.log', encoding='utf-8')
            ]
        )
    
    def display_banner(self):
        """Mostrar banner del sistema"""
        banner = """
🎬 Vision-Narrador v1.0

Sistema de código abierto para convertir novelas 
en videos animados estilo webtoon.

✨ Funcionalidades:
• Extracción inteligente de entidades
• Generación automática de guiones
• Síntesis de voz multiidioma
• Creación de imágenes con IA
• Montaje automático de video

🚀 ¡Transforma tus historias en experiencias visuales!
        """
        
        panel = Panel.fit(
            banner,
            title="[bold cyan]Bienvenido a Vision-Narrador[/bold cyan]",
            border_style="cyan"
        )
        self.console.print(panel)
    
    def initialize_project(self, project_path: str = None) -> bool:
        """Inicializar proyecto"""
        try:
            if project_path:
                self.config = VisionNarradorConfig(project_path)
            else:
                self.config = DEFAULT_CONFIG
            
            # Validar y configurar proyecto
            if not self.config.paths.root.exists():
                if Confirm.ask(f"¿Crear nuevo proyecto en {self.config.paths.root}?"):
                    self.config.initialize_project()
                else:
                    return False
            
            # Validar configuración
            if not self.config.validate_setup():
                self.console.print("❌ [red]Error en la configuración. Revisa las dependencias.[/red]")
                return False
            
            self.console.print(f"✅ [green]Proyecto inicializado: {self.config.paths.root}[/green]")
            return True
            
        except Exception as e:
            self.console.print(f"❌ [red]Error inicializando proyecto: {e}[/red]")
            return False
    
    async def run_interactive_mode(self):
        """Ejecutar modo interactivo"""
        self.display_banner()
        
        if not self.initialize_project():
            return False
        
        # Menú principal
        while True:
            self.console.print("\n[bold]¿Qué deseas hacer?[/bold]")
            self.console.print("1. 🔄 Procesar nuevos capítulos")
            self.console.print("2. 💬 Abrir chat IA")
            self.console.print("3. 📊 Ver estado del proyecto")
            self.console.print("4. ⚙️ Configuración")
            self.console.print("5. 📚 Ayuda")
            self.console.print("6. 🚪 Salir")
            
            try:
                from rich.prompt import Prompt
                choice = Prompt.ask("Selecciona una opción", choices=['1', '2', '3', '4', '5', '6'], default='1')
                
                if choice == '1':
                    await self.process_chapters()
                elif choice == '2':
                    await self.start_ai_chat()
                elif choice == '3':
                    await self.show_status()
                elif choice == '4':
                    await self.configure_system()
                elif choice == '5':
                    self.show_help()
                elif choice == '6':
                    self.console.print("👋 [cyan]¡Hasta luego![/cyan]")
                    break
                    
            except KeyboardInterrupt:
                self.console.print("\n👋 [yellow]¡Hasta luego![/yellow]")
                break
            except Exception as e:
                self.console.print(f"❌ [red]Error: {e}[/red]")
        
        return True
    
    async def process_chapters(self):
        """Procesar capítulos nuevos"""
        try:
            self.console.print("\n🔄 [bold]Iniciando procesamiento de capítulos...[/bold]")
            
            # Inicializar pipeline
            self.pipeline = VisionNarradorPipeline(self.config)
            
            if not await self.pipeline.initialize():
                self.console.print("❌ [red]Error inicializando pipeline[/red]")
                return False
            
            # Procesar capítulos
            success = await self.pipeline.process_new_chapters()
            
            if success:
                self.console.print("✅ [green]¡Procesamiento completado exitosamente![/green]")
            else:
                self.console.print("⚠️ [yellow]Procesamiento completado con errores[/yellow]")
            
            # Limpiar recursos
            self.pipeline.cleanup()
            return success
            
        except Exception as e:
            self.console.print(f"❌ [red]Error procesando capítulos: {e}[/red]")
            logging.error(traceback.format_exc())
            return False
    
    async def start_ai_chat(self):
        """Iniciar chat con IA"""
        try:
            self.console.print("\n💬 [bold]Iniciando chat IA...[/bold]")
            
            chat = AIChat(self.config)
            await chat.start_chat_session()
            
        except Exception as e:
            self.console.print(f"❌ [red]Error en chat IA: {e}[/red]")
    
    async def show_status(self):
        """Mostrar estado del proyecto"""
        try:
            from workspace_manager_avanzado import WorkspaceManagerAvanzado
            
            workspace = WorkspaceManagerAvanzado(self.config.paths.root)
            stats = workspace.obtener_estadisticas_workspace()
            
            status_info = f"""
📁 **Proyecto:** {stats.get('workspace', {}).get('ruta_proyecto', 'Sin título')}
📊 **Archivos en seguimiento:** {stats.get('archivos', {}).get('en_seguimiento', 0)}
📚 **Problemas detectados:** {stats.get('problemas', {}).get('detectados', 0)}
🔧 **Monitor activo:** {stats.get('workspace', {}).get('monitor_activo', False)}
💾 **Ruta del proyecto:** {stats.get('workspace', {}).get('ruta_proyecto', 'N/A')}
            """
            
            status_panel = Panel.fit(
                status_info,
                title="[bold blue]Estado del Proyecto[/bold blue]",
                border_style="blue"
            )
            
            self.console.print(status_panel)
            
        except Exception as e:
            self.console.print(f"❌ [red]Error obteniendo estado: {e}[/red]")
    
    async def configure_system(self):
        """Configurar sistema"""
        self.console.print("\n⚙️ [bold]Configuración del Sistema[/bold]")
        self.console.print("Esta función está en desarrollo.")
        self.console.print("Por ahora, puedes editar el archivo config.py directamente.")
    
    def show_help(self):
        """Mostrar ayuda"""
        help_text = """
🆘 **Ayuda de Vision-Narrador**

**Flujo de trabajo típico:**
1. Coloca tus archivos .txt en la carpeta 'chapters/'
2. Ejecuta el procesamiento de capítulos
3. Revisa y valida las entidades detectadas
4. Los videos se generarán en la carpeta 'output/'

**Estructura de archivos:**
```
./novela/
├── chapters/          # Archivos .txt de capítulos
├── assets/           # Imágenes generadas
├── audio/            # Archivos de audio TTS
├── videos/           # Videos de escenas
├── output/           # Videos finales
└── state.json        # Estado del proyecto
```

**Comandos CLI:**
• `python main.py` - Modo interactivo
• `python main.py --process` - Procesar capítulos
• `python main.py --chat` - Chat IA
• `python main.py --status` - Estado del proyecto

**Soporte:**
- GitHub: Vision-Narrador
- Documentación: docs/
        """
        
        help_panel = Panel.fit(
            help_text,
            title="[bold green]Ayuda[/bold green]",
            border_style="green"
        )
        
        self.console.print(help_panel)


def create_argument_parser():
    """Crear parser de argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(
        description="Vision-Narrador: Convierte novelas en videos webtoon",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python main.py                     # Modo interactivo
  python main.py --process          # Procesar capítulos
  python main.py --chat             # Chat IA
  python main.py --project ./mi_novela  # Usar proyecto específico
        """
    )
    
    parser.add_argument(
        '--process', 
        action='store_true',
        help='Procesar nuevos capítulos automáticamente'
    )
    
    parser.add_argument(
        '--chat',
        action='store_true', 
        help='Iniciar chat IA para validación de entidades'
    )
    
    parser.add_argument(
        '--status',
        action='store_true',
        help='Mostrar estado del proyecto'
    )
    
    parser.add_argument(
        '--setup',
        action='store_true',
        help='Configurar nuevo proyecto'
    )
    
    parser.add_argument(
        '--project',
        type=str,
        help='Ruta del proyecto (default: ./novela)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Mostrar información detallada de depuración'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Vision-Narrador 1.0'
    )
    
    return parser


async def main():
    """Función principal"""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Crear instancia CLI
    cli = VisionNarradorCLI()
    cli.setup_logging(args.verbose)
    
    try:
        # Inicializar proyecto
        if not cli.initialize_project(args.project):
            return 1
        
        # Ejecutar comando específico o modo interactivo
        if args.process:
            success = await cli.process_chapters()
            return 0 if success else 1
            
        elif args.chat:
            await cli.start_ai_chat()
            return 0
            
        elif args.status:
            await cli.show_status()
            return 0
            
        elif args.setup:
            cli.console.print("🔧 [bold]Configuración de nuevo proyecto[/bold]")
            if cli.initialize_project(args.project):
                cli.console.print("✅ [green]Proyecto configurado exitosamente[/green]")
                return 0
            else:
                return 1
        else:
            # Modo interactivo por defecto
            success = await cli.run_interactive_mode()
            return 0 if success else 1
            
    except KeyboardInterrupt:
        cli.console.print("\n⏹️ [yellow]Operación cancelada por el usuario[/yellow]")
        return 130
        
    except Exception as e:
        cli.console.print(f"❌ [red]Error fatal: {e}[/red]")
        logging.error(traceback.format_exc())
        return 1


if __name__ == "__main__":
    # Verificar versión de Python
    if sys.version_info < (3, 9):
        print("❌ Error: Se requiere Python 3.9 o superior")
        sys.exit(1)
    
    # Ejecutar programa principal
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️ Programa interrumpido")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        sys.exit(1)