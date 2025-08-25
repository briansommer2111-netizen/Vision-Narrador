"""
Vision-Narrador: Configuración del Sistema
==========================================

Este archivo define todas las configuraciones principales del pipeline
para garantizar un funcionamiento robusto y consistente.

IMPORTANTE: Ahora integrado con ConfiguracionUltraRobusta para máxima estabilidad.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
import json
import logging

# Importar nuevo sistema ultra-robusto
try:
    from configuracion_ultra_robusta import ConfiguracionUltraRobusta, DEFAULT_CONFIG_ULTRA_ROBUSTA
    ULTRA_ROBUST_AVAILABLE = True
except ImportError:
    ULTRA_ROBUST_AVAILABLE = False
    logging.warning("Sistema ultra-robusto no disponible, usando configuración básica")


@dataclass
class ProjectPaths:
    """Estructura de directorios del proyecto"""
    root: Path
    chapters: Path
    assets: Path
    characters: Path
    locations: Path
    objects: Path
    scenes: Path
    audio: Path
    videos: Path
    output: Path
    state_file: Path
    
    @classmethod
    def create_from_root(cls, root_path: str) -> 'ProjectPaths':
        """Crear estructura de paths desde directorio raíz"""
        root = Path(root_path)
        
        return cls(
            root=root,
            chapters=root / "chapters",
            assets=root / "assets",
            characters=root / "assets" / "characters",
            locations=root / "assets" / "locations", 
            objects=root / "assets" / "objects",
            scenes=root / "assets" / "scenes",
            audio=root / "audio",
            videos=root / "videos",
            output=root / "output",
            state_file=root / "state.json"
        )
    
    def create_directories(self) -> None:
        """Crear todos los directorios necesarios"""
        directories = [
            self.chapters, self.assets, self.characters,
            self.locations, self.objects, self.scenes,
            self.audio, self.videos, self.output
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)


@dataclass
class ModelConfig:
    """Configuración de modelos de IA"""
    # Modelo de lenguaje para NER y chat
    nlp_model: str = "es_core_news_lg"
    llm_model: str = "microsoft/DialoGPT-small"
    
    # Síntesis de voz
    tts_model: str = "tts_models/es/css10/vits"
    default_voice_speed: float = 1.0
    
    # Generación de imágenes
    sd_model: str = "runwayml/stable-diffusion-v1-5"
    image_width: int = 512
    image_height: int = 768
    inference_steps: int = 20
    guidance_scale: float = 7.5
    
    # Estilo por defecto
    style_prompt: str = "webtoon, anime, flat illustration, digital art, clean lines"
    negative_prompt: str = "blurry, low quality, distorted, ugly, bad anatomy"


@dataclass
class VideoConfig:
    """Configuración de video"""
    resolution: tuple = (1080, 1920)  # Formato vertical para webtoon
    fps: int = 24
    duration_per_scene: float = 3.0  # segundos por escena por defecto
    audio_sample_rate: int = 22050
    
    # Códecs y calidad
    video_codec: str = "libx264"
    audio_codec: str = "aac"
    bitrate: str = "2000k"


class VisionNarradorConfig:
    """Configuración principal del sistema"""
    
    def __init__(self, project_root: str = "./novela"):
        self.paths = ProjectPaths.create_from_root(project_root)
        self.models = ModelConfig()
        self.video = VideoConfig()
        
        # Nivel de automatización
        self.automation_level = "manual"  # manual, assisted, automatic
        
        # Configuración de logging
        self.log_level = "INFO"
        self.enable_debug = False
        
        # Límites de recursos
        self.max_memory_usage = 16  # GB
        self.cpu_threads = os.cpu_count() or 4
        
    def initialize_project(self) -> None:
        """Inicializar estructura del proyecto"""
        try:
            self.paths.create_directories()
            
            # Crear archivo de estado inicial si no existe
            if not self.paths.state_file.exists():
                self._create_initial_state()
                
            print(f"✅ Proyecto inicializado en: {self.paths.root}")
            
        except Exception as e:
            raise RuntimeError(f"Error inicializando proyecto: {e}")
    
    def _create_initial_state(self) -> None:
        """Crear archivo de estado inicial"""
        initial_state = {
            "novel_title": "",
            "last_processed_chapter": "",
            "entities": {
                "characters": {},
                "locations": {},
                "objects": {},
                "events": {}
            },
            "project_settings": {
                "style_prompt": self.models.style_prompt,
                "default_voice_model": self.models.tts_model,
                "video_resolution": f"{self.video.resolution[0]}x{self.video.resolution[1]}",
                "automation_level": self.automation_level
            },
            "processing_history": [],
            "version": "1.0"
        }
        
        with open(self.paths.state_file, 'w', encoding='utf-8') as f:
            json.dump(initial_state, f, indent=2, ensure_ascii=False)
    
    def load_state(self) -> Dict[str, Any]:
        """Cargar estado del proyecto"""
        try:
            if not self.paths.state_file.exists():
                self._create_initial_state()
            
            with open(self.paths.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            raise RuntimeError(f"Error cargando estado: {e}")
    
    def save_state(self, state: Dict[str, Any]) -> None:
        """Guardar estado del proyecto"""
        try:
            # Crear backup del estado anterior
            if self.paths.state_file.exists():
                backup_file = self.paths.root / "state_backup.json"
                self.paths.state_file.rename(backup_file)
            
            with open(self.paths.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            raise RuntimeError(f"Error guardando estado: {e}")
    
    def validate_setup(self) -> bool:
        """Validar que el sistema esté correctamente configurado"""
        checks = []
        
        # Verificar directorios
        checks.append(("Directorios", self.paths.root.exists()))
        
        # Verificar dependencias críticas
        try:
            import torch
            checks.append(("PyTorch", True))
        except ImportError:
            checks.append(("PyTorch", False))
        
        try:
            import transformers
            checks.append(("Transformers", True))
        except ImportError:
            checks.append(("Transformers", False))
            
        try:
            import TTS
            checks.append(("TTS", True))
        except ImportError:
            checks.append(("TTS", False))
        
        # Mostrar resultados
        all_good = True
        for check_name, result in checks:
            status = "✅" if result else "❌"
            print(f"{status} {check_name}")
            if not result:
                all_good = False
        
        return all_good


# Configuración global por defecto
DEFAULT_CONFIG = VisionNarradorConfig()


class VisionNarradorConfigIntegrado:
    """Configuración integrada con sistema ultra-robusto para máxima estabilidad"""
    
    def __init__(self, project_root: str = "./vision_narrador_proyecto", usar_ultra_robusto: bool = True):
        self.project_root = project_root
        self.usar_ultra_robusto = usar_ultra_robusto and ULTRA_ROBUST_AVAILABLE
        
        # Configuración básica (compatibilidad hacia atrás)
        self.config_basica = VisionNarradorConfig(project_root)
        
        # Configuración ultra-robusta si está disponible
        self.config_ultra = None
        if self.usar_ultra_robusto:
            self.config_ultra = ConfiguracionUltraRobusta(project_root)
            
        self.logger = logging.getLogger(__name__)
    
    def inicializar_proyecto_robusto(self) -> tuple[bool, dict[str, Any]]:
        """Inicializar proyecto con validación ultra-robusta o básica"""
        if self.usar_ultra_robusto and self.config_ultra:
            self.logger.info("🚀 Inicializando con sistema ultra-robusto...")
            return self.config_ultra.inicializar_sistema_completo()
        else:
            self.logger.info("🚀 Inicializando con configuración básica...")
            try:
                self.config_basica.initialize_project()
                return True, {"tipo": "basico", "mensaje": "Proyecto inicializado con configuración básica"}
            except Exception as e:
                return False, {"error": str(e)}
    
    def validar_sistema(self) -> tuple[bool, dict[str, Any]]:
        """Validar sistema con validación ultra-robusta o básica"""
        if self.usar_ultra_robusto and self.config_ultra:
            return self.config_ultra.validar_dependencias_criticas()
        else:
            exito = self.config_basica.validate_setup()
            return exito, {"tipo": "validacion_basica", "exito": exito}
    
    def crear_backup(self) -> tuple[bool, str]:
        """Crear backup con sistema ultra-robusto o método básico"""
        if self.usar_ultra_robusto and self.config_ultra:
            return self.config_ultra.gestor_backups.crear_backup_automatico()
        else:
            # Backup básico
            try:
                import shutil
                from datetime import datetime
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = Path(self.project_root) / "backups" / f"backup_basico_{timestamp}"
                backup_path.mkdir(parents=True, exist_ok=True)
                
                # Copiar archivos importantes
                state_file = Path(self.project_root) / "state.json"
                if state_file.exists():
                    shutil.copy2(state_file, backup_path / "state.json")
                
                return True, f"Backup básico creado: {backup_path}"
            except Exception as e:
                return False, f"Error creando backup básico: {e}"
    
    def obtener_configuracion_hardware(self) -> dict[str, Any]:
        """Obtener información del hardware del sistema"""
        if self.usar_ultra_robusto and self.config_ultra:
            from dataclasses import asdict
            return asdict(self.config_ultra.config_hardware)
        else:
            # Información básica del hardware
            try:
                import psutil
                memoria = psutil.virtual_memory()
                return {
                    "cpu_cores": os.cpu_count() or 4,
                    "memoria_total_gb": memoria.total / (1024**3),
                    "memoria_disponible_gb": memoria.available / (1024**3),
                    "tipo": "informacion_basica"
                }
            except:
                return {"tipo": "informacion_no_disponible"}


# Configuración integrada por defecto (usa sistema ultra-robusto si está disponible)
CONFIG_INTEGRADO = VisionNarradorConfigIntegrado()

# Para compatibilidad hacia atrás
if ULTRA_ROBUST_AVAILABLE:
    # Usar configuración ultra-robusta como predeterminada
    DEFAULT_CONFIG_ULTRA = DEFAULT_CONFIG_ULTRA_ROBUSTA
else:
    # Fallback a configuración básica
    DEFAULT_CONFIG_ULTRA = DEFAULT_CONFIG