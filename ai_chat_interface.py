"""
Vision-Narrador: Interfaz de Chat IA
====================================

Sistema de chat interactivo para validar entidades, permitir personalización
y guiar al usuario a través del proceso de adaptación de novelas.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from enum import Enum

from rich.console import Console
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown

from config import VisionNarradorConfig, DEFAULT_CONFIG
from workspace_manager_avanzado import WorkspaceManagerAvanzado
from multilayer_ner_avanzado import EntidadCandidato


class ChatMode(Enum):
    """Modos de chat disponibles"""
    ENTITY_VALIDATION = "entity_validation"
    ENTITY_EDITING = "entity_editing"
    GENERAL_HELP = "general_help"
    PROJECT_SETUP = "project_setup"


class AIChat:
    """
    Interfaz de chat IA para interacción con el usuario
    
    Características:
    - Validación interactiva de entidades
    - Edición de descripciones y atributos
    - Guía contextual para el usuario
    - Interfaz amigable con Rich
    """
    
    def __init__(self, config: VisionNarradorConfig = None):
        self.config = config or DEFAULT_CONFIG
        self.console = Console()
        self.logger = logging.getLogger('VisionNarrador.AIChat')
        
        # Estado del chat
        self.current_mode = ChatMode.GENERAL_HELP
        self.session_data = {}
        self.user_preferences = {}
        
        # Respuestas predefinidas y guías
        self.help_messages = self._load_help_messages()
        self.entity_suggestions = self._load_entity_suggestions()
    
    def _load_help_messages(self) -> Dict[str, str]:
        """Cargar mensajes de ayuda predefinidos"""
        return {
            'welcome': """¡Bienvenido a Vision-Narrador! 🎬

Este sistema te ayudará a convertir tus novelas en videos animados estilo webtoon.

Comandos disponibles:
• `procesar` - Procesar nuevos capítulos
• `entidades` - Ver/editar entidades del proyecto
• `configurar` - Configurar el proyecto
• `ayuda` - Mostrar esta ayuda
• `salir` - Salir del programa""",
            
            'entity_help': """Gestión de Entidades 👥

Las entidades son los elementos clave de tu historia:
• **Personajes**: Protagonistas, antagonistas, personajes secundarios
• **Lugares**: Ciudades, bosques, castillos, habitaciones
• **Objetos**: Armas mágicas, artefactos importantes, elementos clave
• **Eventos**: Batallas, ceremonias, festividades importantes

Puedes revisar, editar y confirmar cada entidad detectada.""",
            
            'processing_help': """Procesamiento de Capítulos 📚

El sistema procesará automáticamente:
1. Extracción de entidades del texto
2. Generación de guión estructurado
3. Síntesis de voz para diálogos
4. Creación de imágenes para escenas
5. Composición final en video

El proceso puede tomar varios minutos dependiendo de la longitud del capítulo."""
        }
    
    def _load_entity_suggestions(self) -> Dict[str, List[str]]:
        """Cargar sugerencias para diferentes tipos de entidades"""
        return {
            'character_attributes': [
                'edad', 'género', 'descripción física', 'personalidad',
                'ocupación', 'habilidades especiales', 'historia personal'
            ],
            'location_attributes': [
                'tipo de lugar', 'clima', 'descripción visual', 'importancia',
                'habitantes', 'historia del lugar', 'características especiales'
            ],
            'object_attributes': [
                'tipo de objeto', 'propiedades mágicas', 'origen', 'importancia',
                'descripción visual', 'poderes especiales', 'historia'
            ]
        }
    
    async def start_chat_session(self) -> None:
        """Iniciar sesión de chat principal"""
        try:
            self.console.print(Panel.fit(
                self.help_messages['welcome'],
                title="[bold cyan]Vision-Narrador AI Assistant[/bold cyan]",
                border_style="cyan"
            ))
            
            await self._main_chat_loop()
            
        except KeyboardInterrupt:
            self.console.print("\n👋 [yellow]¡Hasta luego![/yellow]")
        except Exception as e:
            self.logger.error(f"Error en sesión de chat: {e}")
            self.console.print(f"❌ [red]Error en el chat: {e}[/red]")
    
    async def _main_chat_loop(self) -> None:
        """Bucle principal del chat"""
        while True:
            try:
                # Mostrar prompt
                user_input = Prompt.ask(
                    "\n[bold cyan]Vision-Narrador[/bold cyan]",
                    default="ayuda"
                ).strip().lower()
                
                # Procesar comandos
                if user_input in ['salir', 'exit', 'quit']:
                    break
                elif user_input in ['ayuda', 'help']:
                    await self._show_help()
                elif user_input in ['procesar', 'process']:
                    await self._handle_processing_command()
                elif user_input in ['entidades', 'entities']:
                    await self._handle_entities_command()
                elif user_input in ['configurar', 'config']:
                    await self._handle_config_command()
                elif user_input in ['estado', 'status']:
                    await self._show_project_status()
                else:
                    await self._handle_unknown_command(user_input)
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.logger.error(f"Error procesando comando: {e}")
                self.console.print(f"❌ [red]Error: {e}[/red]")
    
    async def _show_help(self) -> None:
        """Mostrar ayuda contextual"""
        help_panel = Panel.fit(
            self.help_messages['welcome'],
            title="[bold green]Ayuda[/bold green]",
            border_style="green"
        )
        self.console.print(help_panel)
    
    async def _handle_processing_command(self) -> None:
        """Manejar comando de procesamiento"""
        self.console.print("🔄 [bold]Iniciando procesamiento de capítulos...[/bold]")
        
        # Importar y ejecutar pipeline
        try:
            from vision_narrador_pipeline import VisionNarradorPipeline
            
            pipeline = VisionNarradorPipeline(self.config)
            
            if await pipeline.initialize():
                success = await pipeline.process_new_chapters()
                
                if success:
                    self.console.print("✅ [green]Procesamiento completado exitosamente[/green]")
                else:
                    self.console.print("⚠️ [yellow]Procesamiento completado con errores[/yellow]")
                
                pipeline.cleanup()
            else:
                self.console.print("❌ [red]Error inicializando el pipeline[/red]")
                
        except Exception as e:
            self.logger.error(f"Error en procesamiento: {e}")
            self.console.print(f"❌ [red]Error: {e}[/red]")
    
    async def _handle_entities_command(self) -> None:
        """Manejar comando de entidades"""
        self.current_mode = ChatMode.ENTITY_VALIDATION
        
        try:
            from workspace_manager import WorkspaceManager
            workspace = WorkspaceManager(self.config)
            
            await self._show_entities_menu(workspace)
            
        except Exception as e:
            self.logger.error(f"Error manejando entidades: {e}")
            self.console.print(f"❌ [red]Error: {e}[/red]")
    
    async def _show_entities_menu(self, workspace) -> None:
        """Mostrar menú de gestión de entidades"""
        while True:
            entities = workspace.state.get('entities', {})
            
            # Mostrar tabla de entidades
            self._display_entities_table(entities)
            
            self.console.print("\n[bold]Opciones:[/bold]")
            self.console.print("1. Ver detalles de una entidad")
            self.console.print("2. Editar entidad")
            self.console.print("3. Agregar nueva entidad")
            self.console.print("4. Eliminar entidad")
            self.console.print("5. Volver al menú principal")
            
            choice = Prompt.ask("Selecciona una opción", choices=['1', '2', '3', '4', '5'], default='5')
            
            if choice == '5':
                break
            elif choice == '1':
                await self._view_entity_details(workspace, entities)
            elif choice == '2':
                await self._edit_entity(workspace, entities)
            elif choice == '3':
                await self._add_new_entity(workspace)
            elif choice == '4':
                await self._delete_entity(workspace, entities)
    
    def _display_entities_table(self, entities: Dict[str, Dict]) -> None:
        """Mostrar tabla de entidades"""
        table = Table(title="🎭 Entidades del Proyecto")
        
        table.add_column("Tipo", style="cyan", no_wrap=True)
        table.add_column("Nombre", style="green")
        table.add_column("Descripción", style="white")
        table.add_column("Imágenes", style="yellow", justify="center")
        
        for entity_type, type_entities in entities.items():
            for name, data in type_entities.items():
                description = data.get('description', 'Sin descripción')
                if len(description) > 50:
                    description = description[:47] + "..."
                
                image_count = len(data.get('images', []))
                
                table.add_row(
                    entity_type.title(),
                    name,
                    description,
                    str(image_count)
                )
        
        if table.row_count == 0:
            self.console.print("📭 [yellow]No hay entidades registradas aún[/yellow]")
        else:
            self.console.print(table)
    
    async def _view_entity_details(self, workspace, entities: Dict[str, Dict]) -> None:
        """Ver detalles de una entidad"""
        entity_name = Prompt.ask("Nombre de la entidad")
        
        found_entity = None
        found_type = None
        
        for entity_type, type_entities in entities.items():
            if entity_name in type_entities:
                found_entity = type_entities[entity_name]
                found_type = entity_type
                break
        
        if not found_entity:
            self.console.print(f"❌ [red]Entidad '{entity_name}' no encontrada[/red]")
            return
        
        # Mostrar detalles
        details_text = f"""**Nombre:** {entity_name}
**Tipo:** {found_type.title()}
**Descripción:** {found_entity.get('description', 'Sin descripción')}
**Fecha de creación:** {found_entity.get('creation_date', 'N/A')}
**Imágenes:** {len(found_entity.get('images', []))}
**Metadatos:** {len(found_entity.get('metadata', {}))} propiedades"""
        
        details_panel = Panel.fit(
            Markdown(details_text),
            title=f"[bold green]Detalles: {entity_name}[/bold green]",
            border_style="green"
        )
        
        self.console.print(details_panel)
    
    async def _edit_entity(self, workspace, entities: Dict[str, Dict]) -> None:
        """Editar una entidad existente"""
        entity_name = Prompt.ask("Nombre de la entidad a editar")
        
        found_entity = None
        found_type = None
        
        for entity_type, type_entities in entities.items():
            if entity_name in type_entities:
                found_entity = type_entities[entity_name]
                found_type = entity_type
                break
        
        if not found_entity:
            self.console.print(f"❌ [red]Entidad '{entity_name}' no encontrada[/red]")
            return
        
        # Opciones de edición
        self.console.print(f"\n[bold]Editando: {entity_name}[/bold]")
        self.console.print("¿Qué deseas editar?")
        self.console.print("1. Descripción")
        self.console.print("2. Tipo de entidad")
        self.console.print("3. Agregar metadatos")
        self.console.print("4. Cancelar")
        
        choice = Prompt.ask("Opción", choices=['1', '2', '3', '4'], default='4')
        
        if choice == '1':
            new_description = Prompt.ask(
                "Nueva descripción",
                default=found_entity.get('description', '')
            )
            found_entity['description'] = new_description
            workspace.save_state()
            self.console.print("✅ [green]Descripción actualizada[/green]")
            
        elif choice == '2':
            new_type = Prompt.ask(
                "Nuevo tipo",
                choices=['character', 'location', 'object', 'event'],
                default=found_type
            )
            
            if new_type != found_type:
                # Mover entidad al nuevo tipo
                del entities[found_type][entity_name]
                if new_type not in entities:
                    entities[new_type] = {}
                entities[new_type][entity_name] = found_entity
                workspace.save_state()
                self.console.print("✅ [green]Tipo de entidad actualizado[/green]")
                
        elif choice == '3':
            metadata_key = Prompt.ask("Clave del metadato")
            metadata_value = Prompt.ask("Valor del metadato")
            
            if 'metadata' not in found_entity:
                found_entity['metadata'] = {}
            
            found_entity['metadata'][metadata_key] = metadata_value
            workspace.save_state()
            self.console.print("✅ [green]Metadato agregado[/green]")
    
    async def _add_new_entity(self, workspace) -> None:
        """Agregar nueva entidad manualmente"""
        self.console.print("\n[bold]Agregar Nueva Entidad[/bold]")
        
        name = Prompt.ask("Nombre de la entidad")
        entity_type = Prompt.ask(
            "Tipo de entidad",
            choices=['character', 'location', 'object', 'event']
        )
        description = Prompt.ask("Descripción")
        
        # Crear nueva entidad
        new_entity = EntityInfo(
            name=name,
            entity_type=entity_type,
            description=description,
            creation_date=datetime.now(),
            images=[],
            metadata={'manually_added': True}
        )
        
        try:
            workspace.add_entity(new_entity)
            self.console.print("✅ [green]Entidad agregada exitosamente[/green]")
        except Exception as e:
            self.console.print(f"❌ [red]Error agregando entidad: {e}[/red]")
    
    async def _delete_entity(self, workspace, entities: Dict[str, Dict]) -> None:
        """Eliminar una entidad"""
        entity_name = Prompt.ask("Nombre de la entidad a eliminar")
        
        found_type = None
        for entity_type, type_entities in entities.items():
            if entity_name in type_entities:
                found_type = entity_type
                break
        
        if not found_type:
            self.console.print(f"❌ [red]Entidad '{entity_name}' no encontrada[/red]")
            return
        
        # Confirmar eliminación
        if Confirm.ask(f"¿Estás seguro de eliminar '{entity_name}'?"):
            del entities[found_type][entity_name]
            workspace.save_state()
            self.console.print("✅ [green]Entidad eliminada[/green]")
        else:
            self.console.print("❌ [yellow]Eliminación cancelada[/yellow]")
    
    async def _handle_config_command(self) -> None:
        """Manejar configuración del proyecto"""
        self.console.print("⚙️ [bold]Configuración del Proyecto[/bold]")
        
        # Mostrar configuración actual
        config_info = f"""**Título del proyecto:** {self.config.paths.root.name}
**Resolución de video:** {self.config.video.resolution[0]}x{self.config.video.resolution[1]}
**FPS:** {self.config.video.fps}
**Modelo TTS:** {self.config.models.tts_model}
**Estilo de imagen:** {self.config.models.style_prompt}"""
        
        config_panel = Panel.fit(
            Markdown(config_info),
            title="[bold blue]Configuración Actual[/bold blue]",
            border_style="blue"
        )
        
        self.console.print(config_panel)
        
        # Opciones de configuración
        if Confirm.ask("¿Deseas modificar alguna configuración?"):
            await self._modify_config()
    
    async def _modify_config(self) -> None:
        """Modificar configuración"""
        self.console.print("🔧 [bold]Modificar Configuración[/bold]")
        self.console.print("1. Resolución de video")
        self.console.print("2. FPS")
        self.console.print("3. Estilo de imagen")
        self.console.print("4. Cancelar")
        
        choice = Prompt.ask("¿Qué deseas modificar?", choices=['1', '2', '3', '4'], default='4')
        
        if choice == '1':
            width = IntPrompt.ask("Ancho", default=self.config.video.resolution[0])
            height = IntPrompt.ask("Alto", default=self.config.video.resolution[1])
            self.config.video.resolution = (width, height)
            self.console.print("✅ [green]Resolución actualizada[/green]")
            
        elif choice == '2':
            fps = IntPrompt.ask("FPS", default=self.config.video.fps)
            self.config.video.fps = fps
            self.console.print("✅ [green]FPS actualizado[/green]")
            
        elif choice == '3':
            style = Prompt.ask("Estilo de imagen", default=self.config.models.style_prompt)
            self.config.models.style_prompt = style
            self.console.print("✅ [green]Estilo actualizado[/green]")
    
    async def _show_project_status(self) -> None:
        """Mostrar estado del proyecto"""
        try:
            from workspace_manager import WorkspaceManager
            workspace = WorkspaceManager(self.config)
            stats = workspace.get_project_stats()
            
            status_text = f"""**📁 Proyecto:** {stats.get('novel_title', 'Sin título')}
**📊 Entidades:** {stats.get('total_entities', 0)}
**📚 Capítulos procesados:** {stats.get('processed_chapters', 0)}
**📖 Último capítulo:** {stats.get('last_processed', 'Ninguno')}
**🔧 Automatización:** {stats.get('automation_level', 'manual')}
**💾 Ruta:** {stats.get('project_path', 'N/A')}"""
            
            status_panel = Panel.fit(
                Markdown(status_text),
                title="[bold cyan]Estado del Proyecto[/bold cyan]",
                border_style="cyan"
            )
            
            self.console.print(status_panel)
            
        except Exception as e:
            self.console.print(f"❌ [red]Error obteniendo estado: {e}[/red]")
    
    async def _handle_unknown_command(self, command: str) -> None:
        """Manejar comando desconocido"""
        self.console.print(f"❓ [yellow]Comando no reconocido: '{command}'[/yellow]")
        self.console.print("💡 Escribe 'ayuda' para ver los comandos disponibles")
    
    async def validate_entities_interactive(self, candidates: List[EntidadCandidato]) -> List[EntidadCandidato]:
        """Validar entidades de forma interactiva"""
        if not candidates:
            self.console.print("ℹ️ [blue]No se detectaron entidades nuevas[/blue]")
            return []
        
        self.console.print(f"\n🔍 [bold]Se detectaron {len(candidates)} entidades potenciales[/bold]")
        self.console.print("Por favor, revisa y confirma cada una:")
        
        validated = []
        
        for i, candidate in enumerate(candidates, 1):
            self.console.print(f"\n[bold cyan]Entidad {i}/{len(candidates)}:[/bold cyan]")
            
            # Mostrar información de la entidad
            entity_info = f"""**Texto:** {candidate.texto}
**Tipo sugerido:** {candidate.tipo_sugerido}
**Confianza:** {candidate.confianza:.2f}
**Método:** {candidate.metodo_extraccion}
**Contexto:** "{candidate.contexto[:100]}..." """
            
            entity_panel = Panel.fit(
                Markdown(entity_info),
                title=f"[bold green]Candidato: {candidate.texto}[/bold green]",
                border_style="green"
            )
            
            self.console.print(entity_panel)
            
            # Opciones para el usuario
            self.console.print("\n[bold]¿Qué deseas hacer?[/bold]")
            self.console.print("1. Confirmar como está")
            self.console.print("2. Cambiar tipo")
            self.console.print("3. Editar descripción")
            self.console.print("4. Descartar")
            self.console.print("5. Confirmar todas las restantes")
            
            choice = Prompt.ask("Opción", choices=['1', '2', '3', '4', '5'], default='1')
            
            if choice == '1':
                validated.append(candidate)
            elif choice == '2':
                new_type = Prompt.ask(
                    "Nuevo tipo",
                    choices=['CHARACTER', 'LOCATION', 'OBJECT', 'EVENT'],
                    default=candidate.tipo_sugerido
                )
                candidate.tipo_sugerido = new_type
                validated.append(candidate)
            elif choice == '3':
                new_description = Prompt.ask("Nueva descripción", default=candidate.contexto[:100])
                candidate.contexto = new_description
                validated.append(candidate)
            elif choice == '4':
                self.console.print("❌ [red]Entidad descartada[/red]")
            elif choice == '5':
                validated.extend(candidates[i-1:])
                break
        
        self.console.print(f"\n✅ [green]Validación completada: {len(validated)} entidades confirmadas[/green]")
        return validated


# Función principal para testing
async def main():
    """Función principal para probar el chat"""
    chat = AIChat()
    await chat.start_chat_session()


if __name__ == "__main__":
    asyncio.run(main())