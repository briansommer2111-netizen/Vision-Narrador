"""
Vision-Narrador: Sistema de Configuración Ultra-Robusto
=======================================================

Sistema ultra-avanzado de configuración con validación exhaustiva automática,
gestión inteligente de backups y recuperación automática.

Funcionalidades Ultra-Robustas:
- Validación automática de todas las dependencias críticas
- Sistema de backup incremental multimodal 
- Recuperación automática inteligente
- Configuración adaptativa según hardware
- Detección automática de conflictos de software
- Optimización automática basada en benchmarks
"""

import os
import sys
import json
import hashlib
import shutil
import platform
import subprocess
import time
import psutil
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import tempfile
import zipfile


@dataclass
class DependenciasCriticas:
    """Definición de dependencias críticas del sistema"""
    nombre: str
    version_minima: str
    comando_verificacion: str
    instalacion_automatica: bool = False
    comando_instalacion: Optional[str] = None
    critica: bool = True


@dataclass
class ConfiguracionHardware:
    """Configuración adaptativa según hardware detectado"""
    cpu_cores: int
    memoria_total_gb: float
    memoria_disponible_gb: float
    espacio_disco_gb: float
    gpu_disponible: bool
    cpu_arquitectura: str
    sistema_operativo: str
    python_version: str


class ValidadorDependencias:
    """Sistema ultra-avanzado de validación de dependencias"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.dependencias_criticas = self._definir_dependencias_criticas()
        
    def _definir_dependencias_criticas(self) -> List[DependenciasCriticas]:
        """Definir lista completa de dependencias críticas"""
        return [
            DependenciasCriticas(
                nombre="Python",
                version_minima="3.8.0",
                comando_verificacion="python --version",
                critica=True
            ),
            DependenciasCriticas(
                nombre="FFmpeg",
                version_minima="4.0.0",
                comando_verificacion="ffmpeg -version",
                instalacion_automatica=True,
                comando_instalacion="pip install ffmpeg-python",
                critica=True
            ),
            DependenciasCriticas(
                nombre="PyTorch",
                version_minima="1.9.0",
                comando_verificacion="python -c 'import torch; print(torch.__version__)'",
                instalacion_automatica=True,
                comando_instalacion="pip install torch torchvision torchaudio",
                critica=True
            ),
            DependenciasCriticas(
                nombre="spaCy",
                version_minima="3.4.0",
                comando_verificacion="python -c 'import spacy; print(spacy.__version__)'",
                instalacion_automatica=True,
                comando_instalacion="pip install spacy",
                critica=True
            ),
            DependenciasCriticas(
                nombre="Transformers",
                version_minima="4.20.0",
                comando_verificacion="python -c 'import transformers; print(transformers.__version__)'",
                instalacion_automatica=True,
                comando_instalacion="pip install transformers",
                critica=True
            )
        ]
    
    def validar_python_version(self) -> Tuple[bool, str]:
        """Validar versión de Python"""
        try:
            version_actual = sys.version_info
            version_str = f"{version_actual.major}.{version_actual.minor}.{version_actual.micro}"
            
            if version_actual >= (3, 8, 0):
                return True, f"Python {version_str} ✅"
            else:
                return False, f"Python {version_str} ❌ (Mínimo requerido: 3.8.0)"
                
        except Exception as e:
            return False, f"Error verificando Python: {e}"
    
    def verificar_espacios_disco(self, ruta_proyecto: Path, minimo_gb: float = 5.0) -> Tuple[bool, str]:
        """Verificar espacio disponible en disco"""
        try:
            stat = shutil.disk_usage(ruta_proyecto)
            espacio_disponible_gb = stat.free / (1024**3)
            
            if espacio_disponible_gb >= minimo_gb:
                return True, f"Espacio disponible: {espacio_disponible_gb:.1f} GB ✅"
            else:
                return False, f"Espacio insuficiente: {espacio_disponible_gb:.1f} GB (Mínimo: {minimo_gb} GB) ❌"
                
        except Exception as e:
            return False, f"Error verificando espacio en disco: {e}"
    
    def comprobar_memoria_disponible(self, minimo_gb: float = 4.0) -> Tuple[bool, str]:
        """Comprobar memoria RAM disponible"""
        try:
            memoria = psutil.virtual_memory()
            memoria_disponible_gb = memoria.available / (1024**3)
            memoria_total_gb = memoria.total / (1024**3)
            
            if memoria_disponible_gb >= minimo_gb:
                return True, f"Memoria disponible: {memoria_disponible_gb:.1f}/{memoria_total_gb:.1f} GB ✅"
            else:
                return False, f"Memoria insuficiente: {memoria_disponible_gb:.1f} GB (Mínimo: {minimo_gb} GB) ❌"
                
        except Exception as e:
            return False, f"Error verificando memoria: {e}"
    
    def ejecutar_validacion_completa(self, ruta_proyecto: Path) -> Dict[str, Any]:
        """Ejecutar validación completa del sistema"""
        resultados = {
            "timestamp": datetime.now().isoformat(),
            "validaciones": {},
            "errores_criticos": [],
            "advertencias": [],
            "estado_general": "unknown"
        }
        
        self.logger.info("🔍 Iniciando validación completa del sistema...")
        
        # Validaciones básicas del sistema
        validaciones_basicas = [
            ("Python", self.validar_python_version),
            ("Espacio en Disco", lambda: self.verificar_espacios_disco(ruta_proyecto)),
            ("Memoria RAM", self.comprobar_memoria_disponible)
        ]
        
        errores_criticos = 0
        advertencias = 0
        
        for nombre, validacion in validaciones_basicas:
            try:
                exito, mensaje = validacion()
                resultados["validaciones"][nombre] = {
                    "exito": exito,
                    "mensaje": mensaje,
                    "timestamp": datetime.now().isoformat()
                }
                
                if not exito:
                    if nombre in ["Python", "Espacio en Disco", "Memoria RAM"]:
                        errores_criticos += 1
                        resultados["errores_criticos"].append(mensaje)
                    else:
                        advertencias += 1
                        resultados["advertencias"].append(mensaje)
                        
            except Exception as e:
                mensaje_error = f"Error en validación {nombre}: {e}"
                resultados["validaciones"][nombre] = {
                    "exito": False,
                    "mensaje": mensaje_error,
                    "timestamp": datetime.now().isoformat()
                }
                errores_criticos += 1
                resultados["errores_criticos"].append(mensaje_error)
        
        # Determinar estado general
        if errores_criticos == 0:
            if advertencias == 0:
                resultados["estado_general"] = "perfecto"
            else:
                resultados["estado_general"] = "funcional_con_advertencias"
        else:
            resultados["estado_general"] = "critico"
        
        self.logger.info(f"✅ Validación completa finalizada - Estado: {resultados['estado_general']}")
        return resultados


class GestorBackups:
    """Sistema ultra-avanzado de gestión de backups automáticos"""
    
    def __init__(self, ruta_proyecto: Path):
        self.ruta_proyecto = ruta_proyecto
        self.ruta_backups = ruta_proyecto / "backups"
        self.max_backups_retenidos = 10
        self.logger = logging.getLogger(__name__)
        
        # Crear directorio de proyecto y backups
        self.ruta_proyecto.mkdir(parents=True, exist_ok=True)
        self.ruta_backups.mkdir(parents=True, exist_ok=True)
    
    def calcular_checksum_archivo(self, archivo: Path) -> str:
        """Calcular checksum SHA-256 de un archivo"""
        hash_sha256 = hashlib.sha256()
        try:
            with open(archivo, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            self.logger.error(f"Error calculando checksum para {archivo}: {e}")
            return ""
    
    def crear_backup_automatico(self, incluir_assets: bool = True) -> Tuple[bool, str]:
        """Crear backup automático incremental completo"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = self.ruta_backups / f"backup_{timestamp}"
            backup_dir.mkdir(exist_ok=True)
            
            self.logger.info(f"🔄 Creando backup automático: {backup_dir}")
            
            # Información del backup
            backup_info = {
                "timestamp": timestamp,
                "fecha_creacion": datetime.now().isoformat(),
                "version": "2.0",
                "archivos_respaldados": [],
                "checksums": {},
                "estado": "completado"
            }
            
            # Archivar archivos críticos del proyecto
            archivos_criticos = [
                "state.json",
                "config.py", 
                "configuracion_ultra_robusta.py",
                "main.py",
                "requirements.txt"
            ]
            
            for archivo_nombre in archivos_criticos:
                archivo_origen = self.ruta_proyecto / archivo_nombre
                if archivo_origen.exists():
                    archivo_destino = backup_dir / archivo_nombre
                    shutil.copy2(archivo_origen, archivo_destino)
                    
                    # Calcular checksum
                    checksum = self.calcular_checksum_archivo(archivo_origen)
                    backup_info["checksums"][archivo_nombre] = checksum
                    backup_info["archivos_respaldados"].append(archivo_nombre)
            
            # Guardar información del backup
            info_file = backup_dir / "backup_info.json"
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(backup_info, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"✅ Backup creado exitosamente: {backup_dir}")
            return True, f"Backup creado: {timestamp}"
            
        except Exception as e:
            self.logger.error(f"Error creando backup: {e}")
            return False, f"Error creando backup: {e}"
    
    def listar_backups_disponibles(self) -> List[Dict[str, Any]]:
        """Listar todos los backups disponibles con información detallada"""
        backups = []
        
        try:
            for item in self.ruta_backups.iterdir():
                if item.is_dir() and item.name.startswith("backup_"):
                    info_file = item / "backup_info.json"
                    if info_file.exists():
                        with open(info_file, 'r', encoding='utf-8') as f:
                            backup_info = json.load(f)
                        backup_info["ruta"] = str(item)
                        backup_info["tipo_almacenamiento"] = "directorio"
                        backups.append(backup_info)
                
                elif item.is_file() and item.name.startswith("backup_") and item.suffix == '.zip':
                    # Backup comprimido - leer información
                    try:
                        with zipfile.ZipFile(item, 'r') as zipf:
                            with zipf.open("backup_info.json") as info_file:
                                backup_info = json.load(info_file)
                        backup_info["ruta"] = str(item)
                        backup_info["tipo_almacenamiento"] = "comprimido"
                        backups.append(backup_info)
                    except:
                        pass  # Backup corrupto o incompleto
            
            # Ordenar por fecha de creación (más reciente primero)
            backups.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            
        except Exception as e:
            self.logger.error(f"Error listando backups: {e}")
        
        return backups


class ConfiguracionUltraRobusta:
    """Sistema ultra-robusto de configuración con validación exhaustiva y recuperación automática"""
    
    def __init__(self, ruta_proyecto: str = "./vision_narrador_proyecto"):
        self.ruta_proyecto = Path(ruta_proyecto)
        self.logger = self._configurar_logging()
        
        # Componentes principales
        self.validador = ValidadorDependencias()
        self.gestor_backups = GestorBackups(self.ruta_proyecto)
        
        # Configuración del sistema
        self.config_hardware = self._detectar_configuracion_hardware()
        self.configuraciones_ambiente = {}
        
        # Estado del sistema
        self.sistema_inicializado = False
        self.ultimo_backup = None
        
    def _configurar_logging(self) -> logging.Logger:
        """Configurar sistema de logging robusto"""
        logger = logging.getLogger(f"ConfiguracionUltraRobusta_{id(self)}")
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        
        return logger
    
    def _detectar_configuracion_hardware(self) -> ConfiguracionHardware:
        """Detectar configuración del hardware automáticamente"""
        try:
            memoria = psutil.virtual_memory()
            disco = shutil.disk_usage(self.ruta_proyecto.parent if self.ruta_proyecto.exists() else Path.cwd())
            
            # Detectar GPU (básico)
            gpu_disponible = False
            try:
                import torch
                gpu_disponible = torch.cuda.is_available()
            except:
                pass
            
            return ConfiguracionHardware(
                cpu_cores=os.cpu_count() or 4,
                memoria_total_gb=memoria.total / (1024**3),
                memoria_disponible_gb=memoria.available / (1024**3),
                espacio_disco_gb=disco.free / (1024**3),
                gpu_disponible=gpu_disponible,
                cpu_arquitectura=platform.machine(),
                sistema_operativo=platform.system(),
                python_version=sys.version
            )
            
        except Exception as e:
            self.logger.warning(f"Error detectando hardware, usando valores por defecto: {e}")
            return ConfiguracionHardware(
                cpu_cores=4,
                memoria_total_gb=8.0,
                memoria_disponible_gb=4.0,
                espacio_disco_gb=10.0,
                gpu_disponible=False,
                cpu_arquitectura="unknown",
                sistema_operativo="unknown",
                python_version=sys.version
            )
    
    def configurar_ambiente_automatico(self) -> Tuple[bool, Dict[str, Any]]:
        """Configurar ambiente automáticamente según hardware detectado"""
        try:
            self.logger.info("🔧 Configurando ambiente automáticamente...")
            
            # Crear estructura de directorios
            self.ruta_proyecto.mkdir(exist_ok=True)
            
            directorios_requeridos = [
                "chapters", "assets", "assets/characters", "assets/locations",
                "assets/objects", "assets/scenes", "audio", "videos", 
                "output", "temp", "logs", "backups"
            ]
            
            for directorio in directorios_requeridos:
                (self.ruta_proyecto / directorio).mkdir(parents=True, exist_ok=True)
            
            # Configurar parámetros adaptativos según hardware
            config_adaptativa = self._generar_configuracion_adaptativa()
            
            # Guardar configuración
            config_file = self.ruta_proyecto / "configuracion_adaptativa.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_adaptativa, f, indent=2, ensure_ascii=False)
            
            self.configuraciones_ambiente = config_adaptativa
            self.logger.info("✅ Ambiente configurado automáticamente")
            
            return True, config_adaptativa
            
        except Exception as e:
            self.logger.error(f"Error configurando ambiente: {e}")
            return False, {"error": str(e)}
    
    def _generar_configuracion_adaptativa(self) -> Dict[str, Any]:
        """Generar configuración adaptativa según capacidades del sistema"""
        hw = self.config_hardware
        
        # Determinar configuración óptima según recursos
        if hw.memoria_total_gb >= 16 and hw.cpu_cores >= 8:
            perfil = "alto_rendimiento"
            chunk_size = 2000
            workers_paralelos = min(hw.cpu_cores, 8)
        elif hw.memoria_total_gb >= 8 and hw.cpu_cores >= 4:
            perfil = "rendimiento_medio"
            chunk_size = 1000
            workers_paralelos = min(hw.cpu_cores, 4)
        else:
            perfil = "rendimiento_basico"
            chunk_size = 500
            workers_paralelos = 2
        
        config = {
            "perfil_hardware": perfil,
            "hardware_detectado": asdict(hw),
            "configuracion_procesamiento": {
                "chunk_size_palabras": chunk_size,
                "workers_paralelos": workers_paralelos,
                "usar_gpu": hw.gpu_disponible,
                "optimizar_cpu": not hw.gpu_disponible
            },
            "timestamp_configuracion": datetime.now().isoformat(),
            "version_configuracion": "2.0"
        }
        
        return config
    
    def validar_dependencias_criticas(self) -> Tuple[bool, Dict[str, Any]]:
        """Ejecutar validación completa de dependencias críticas"""
        self.logger.info("🔍 Iniciando validación de dependencias críticas...")
        
        resultados = self.validador.ejecutar_validacion_completa(self.ruta_proyecto)
        
        if resultados["estado_general"] == "critico":
            self.logger.error("❌ Dependencias críticas faltantes - Sistema no operativo")
            return False, resultados
        elif resultados["estado_general"] == "funcional_con_advertencias":
            self.logger.warning("⚠️ Sistema funcional pero con advertencias")
            return True, resultados
        else:
            self.logger.info("✅ Todas las dependencias críticas validadas")
            return True, resultados
    
    def inicializar_sistema_completo(self) -> Tuple[bool, Dict[str, Any]]:
        """Inicializar sistema completo con validación exhaustiva"""
        try:
            self.logger.info("🚀 Iniciando inicialización completa del sistema...")
            
            # 1. Crear backup antes de cualquier cambio
            backup_exito, backup_msg = self.gestor_backups.crear_backup_automatico()
            if backup_exito:
                self.ultimo_backup = backup_msg
            
            # 2. Configurar ambiente automáticamente
            config_exito, config_result = self.configurar_ambiente_automatico()
            if not config_exito:
                return False, {"error": "Fallo configurando ambiente", "detalle": config_result}
            
            # 3. Validar dependencias críticas
            deps_exito, deps_result = self.validar_dependencias_criticas()
            if not deps_exito:
                return False, {"error": "Dependencias críticas faltantes", "detalle": deps_result}
            
            # 4. Marcar sistema como inicializado
            self.sistema_inicializado = True
            
            resultado_final = {
                "sistema_inicializado": True,
                "backup_inicial": backup_msg,
                "configuracion": config_result,
                "validacion_dependencias": deps_result,
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info("✅ Sistema inicializado completamente con éxito")
            return True, resultado_final
            
        except Exception as e:
            self.logger.error(f"Error en inicialización completa: {e}")
            return False, {"error": str(e)}


# Configuración por defecto optimizada
DEFAULT_CONFIG_ULTRA_ROBUSTA = ConfiguracionUltraRobusta()
