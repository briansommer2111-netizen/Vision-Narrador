"""
Vision-Narrador: Workspace Manager Ultra-Avanzado
=================================================

Sistema ultra-robusto de gestión de espacio de trabajo con capacidades de:
- Recuperación automática inteligente
- Detección proactiva de problemas
- Monitor de integridad continuo
- Cuarentena automática de archivos problemáticos
- Reparación automática en segundo plano
- Validación exhaustiva de dependencias
- Sistema de alertas predictivas
"""

import os
import json
import logging
import hashlib
import threading
import time
import shutil
import psutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue
from enum import Enum

# Import our ultra-robust systems
from configuracion_ultra_robusta import ConfiguracionUltraRobusta
from gestor_estado_avanzado import GestorEstadoAvanzado


class EstadoArchivo(Enum):
    """Estados posibles de un archivo en el workspace"""
    SALUDABLE = "healthy"
    CORRUPTO = "corrupted"
    CUARENTENA = "quarantined"
    EN_REPARACION = "repairing"
    PENDIENTE_VALIDACION = "pending_validation"
    DESCONOCIDO = "unknown"


class TipoProblema(Enum):
    """Tipos de problemas detectables"""
    ARCHIVO_CORRUPTO = "file_corruption"
    DEPENDENCIA_FALTANTE = "missing_dependency"
    ESPACIO_DISCO_BAJO = "low_disk_space"
    MEMORIA_INSUFICIENTE = "insufficient_memory"
    PERMISOS_INSUFICIENTES = "insufficient_permissions"
    ESTRUCTURA_DIRECTORIO_INVALIDA = "invalid_directory_structure"
    ESTADO_INCONSISTENTE = "inconsistent_state"
    MODELO_NO_DISPONIBLE = "model_unavailable"


@dataclass
class ProblemaDetectado:
    """Información sobre un problema detectado"""
    tipo: TipoProblema
    descripcion: str
    archivo_afectado: Optional[Path]
    severidad: str  # "critico", "alto", "medio", "bajo"
    timestamp: datetime
    resuelto: bool = False
    accion_correctiva: Optional[str] = None
    intentos_reparacion: int = 0


@dataclass
class ArchiveInfo:
    """Información extendida sobre archivos en el workspace"""
    path: Path
    size: int
    hash_sha256: str
    last_modified: datetime
    estado: EstadoArchivo
    last_validation: Optional[datetime]
    corruption_checks: int
    repair_attempts: int
    metadata: Dict[str, Any]


@dataclass
class MetricasRendimiento:
    """Métricas de rendimiento del workspace"""
    tiempo_ultima_validacion: float
    archivos_validados: int
    problemas_detectados: int
    problemas_resueltos: int
    uso_cpu_promedio: float
    uso_memoria_promedio: float
    espacio_disco_disponible: float
    tasa_exito_reparaciones: float


class MonitorIntegridad:
    """Monitor continuo de integridad del workspace"""
    
    def __init__(self, workspace_manager):
        self.workspace_manager = workspace_manager
        self.logger = logging.getLogger(__name__)
        self.running = False
        self.monitor_thread = None
        self.problemas_queue = queue.Queue()
        
        # Configuración del monitor
        self.intervalo_chequeo = 30  # segundos
        self.intervalo_validacion_profunda = 300  # 5 minutos
        
    def iniciar_monitoreo(self):
        """Iniciar monitoreo continuo en background"""
        if not self.running:
            self.running = True
            self.monitor_thread = threading.Thread(target=self._bucle_monitoreo, daemon=True)
            self.monitor_thread.start()
            self.logger.info("🔍 Monitor de integridad iniciado")
    
    def detener_monitoreo(self):
        """Detener monitoreo continuo"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("⏹️ Monitor de integridad detenido")
    
    def _bucle_monitoreo(self):
        """Bucle principal de monitoreo"""
        ultimo_chequeo_profundo = time.time()
        
        while self.running:
            try:
                # Chequeo básico de salud del sistema
                self._chequeo_salud_sistema()
                
                # Validación profunda periódica
                if time.time() - ultimo_chequeo_profundo > self.intervalo_validacion_profunda:
                    self._validacion_profunda()
                    ultimo_chequeo_profundo = time.time()
                
                # Procesar problemas detectados
                self._procesar_problemas_pendientes()
                
                time.sleep(self.intervalo_chequeo)
                
            except Exception as e:
                self.logger.error(f"Error en monitor de integridad: {e}")
                time.sleep(self.intervalo_chequeo)
    
    def _chequeo_salud_sistema(self):
        """Chequeo básico de salud del sistema"""
        try:
            # Verificar espacio en disco
            disk_usage = shutil.disk_usage(self.workspace_manager.ruta_proyecto)
            espacio_libre_gb = disk_usage.free / (1024**3)
            
            if espacio_libre_gb < 1.0:  # Menos de 1GB
                problema = ProblemaDetectado(
                    tipo=TipoProblema.ESPACIO_DISCO_BAJO,
                    descripcion=f"Espacio en disco bajo: {espacio_libre_gb:.1f} GB disponibles",
                    archivo_afectado=None,
                    severidad="critico",
                    timestamp=datetime.now()
                )
                self.problemas_queue.put(problema)
            
            # Verificar memoria disponible
            memoria = psutil.virtual_memory()
            if memoria.percent > 90:
                problema = ProblemaDetectado(
                    tipo=TipoProblema.MEMORIA_INSUFICIENTE,
                    descripcion=f"Uso de memoria alto: {memoria.percent:.1f}%",
                    archivo_afectado=None,
                    severidad="alto",
                    timestamp=datetime.now()
                )
                self.problemas_queue.put(problema)
                
        except Exception as e:
            self.logger.error(f"Error en chequeo de salud: {e}")
    
    def _validacion_profunda(self):
        """Validación profunda de todos los archivos"""
        try:
            self.logger.info("🔍 Iniciando validación profunda del workspace")
            
            # Validar estructura de directorios
            self.workspace_manager._validar_estructura_directorios()
            
            # Validar integridad de archivos críticos
            archivos_criticos = [
                self.workspace_manager.ruta_proyecto / "state.json",
                self.workspace_manager.ruta_proyecto / "configuracion_adaptativa.json"
            ]
            
            for archivo in archivos_criticos:
                if archivo.exists():
                    if not self._validar_integridad_archivo(archivo):
                        problema = ProblemaDetectado(
                            tipo=TipoProblema.ARCHIVO_CORRUPTO,
                            descripcion=f"Archivo crítico corrupto: {archivo.name}",
                            archivo_afectado=archivo,
                            severidad="critico",
                            timestamp=datetime.now()
                        )
                        self.problemas_queue.put(problema)
            
            self.logger.info("✅ Validación profunda completada")
            
        except Exception as e:
            self.logger.error(f"Error en validación profunda: {e}")
    
    def _validar_integridad_archivo(self, archivo: Path) -> bool:
        """Validar integridad de un archivo específico"""
        try:
            if not archivo.exists():
                return False
            
            # Para archivos JSON, validar que se pueden parsear
            if archivo.suffix == '.json':
                with open(archivo, 'r', encoding='utf-8') as f:
                    json.load(f)
            
            # Verificar que el archivo no esté vacío
            if archivo.stat().st_size == 0:
                return False
            
            return True
            
        except (json.JSONDecodeError, PermissionError, OSError):
            return False
    
    def _procesar_problemas_pendientes(self):
        """Procesar problemas en la queue"""
        while not self.problemas_queue.empty():
            try:
                problema = self.problemas_queue.get_nowait()
                self.workspace_manager._manejar_problema(problema)
            except queue.Empty:
                break
            except Exception as e:
                self.logger.error(f"Error procesando problema: {e}")


class SistemaReparacionAutomatica:
    """Sistema de reparación automática de problemas"""
    
    def __init__(self, workspace_manager):
        self.workspace_manager = workspace_manager
        self.logger = logging.getLogger(__name__)
        
    def reparar_problema(self, problema: ProblemaDetectado) -> bool:
        """Reparar un problema específico automáticamente"""
        try:
            if problema.tipo == TipoProblema.ARCHIVO_CORRUPTO:
                return self._reparar_archivo_corrupto(problema)
            elif problema.tipo == TipoProblema.ESTRUCTURA_DIRECTORIO_INVALIDA:
                return self._reparar_estructura_directorios()
            elif problema.tipo == TipoProblema.ESTADO_INCONSISTENTE:
                return self._reparar_estado_inconsistente()
            elif problema.tipo == TipoProblema.ESPACIO_DISCO_BAJO:
                return self._limpiar_archivos_temporales()
            else:
                self.logger.warning(f"Tipo de problema no reparable automáticamente: {problema.tipo}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error reparando problema {problema.tipo}: {e}")
            return False
    
    def _reparar_archivo_corrupto(self, problema: ProblemaDetectado) -> bool:
        """Reparar archivo corrupto desde backup"""
        try:
            if not problema.archivo_afectado:
                return False
            
            archivo = problema.archivo_afectado
            
            # Mover archivo corrupto a cuarentena
            cuarentena_dir = self.workspace_manager.ruta_proyecto / "cuarentena"
            cuarentena_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archivo_cuarentena = cuarentena_dir / f"{archivo.name}_{timestamp}.corrupted"
            
            if archivo.exists():
                shutil.move(str(archivo), str(archivo_cuarentena))
                self.logger.info(f"📁 Archivo movido a cuarentena: {archivo_cuarentena}")
            
            # Intentar restaurar desde backup
            if archivo.name == "state.json":
                return self._restaurar_estado_desde_backup()
            else:
                # Para otros archivos, intentar crear versión mínima funcional
                return self._crear_archivo_minimo(archivo)
                
        except Exception as e:
            self.logger.error(f"Error reparando archivo corrupto: {e}")
            return False
    
    def _restaurar_estado_desde_backup(self) -> bool:
        """Restaurar state.json desde backup"""
        try:
            gestor_estado = self.workspace_manager.gestor_estado
            exito, estado_restaurado = gestor_estado.recuperar_estado_automatico()
            
            if exito:
                self.logger.info("✅ Estado restaurado desde backup")
                return True
            else:
                # Crear estado inicial si no hay backup
                estado_inicial = gestor_estado._crear_estado_inicial()
                gestor_estado.estado_actual = estado_inicial
                exito_guardado, _ = gestor_estado.guardar_estado(crear_backup=False)
                
                if exito_guardado:
                    self.logger.info("🆕 Estado inicial recreado")
                    return True
                    
        except Exception as e:
            self.logger.error(f"Error restaurando estado: {e}")
        
        return False
    
    def _reparar_estructura_directorios(self) -> bool:
        """Reparar estructura de directorios faltante"""
        try:
            directorios_requeridos = [
                "chapters", "assets", "assets/characters", "assets/locations",
                "assets/objects", "assets/scenes", "audio", "videos", 
                "output", "temp", "logs", "backups", "cuarentena"
            ]
            
            for directorio in directorios_requeridos:
                dir_path = self.workspace_manager.ruta_proyecto / directorio
                dir_path.mkdir(parents=True, exist_ok=True)
            
            self.logger.info("✅ Estructura de directorios reparada")
            return True
            
        except Exception as e:
            self.logger.error(f"Error reparando estructura: {e}")
            return False
    
    def _limpiar_archivos_temporales(self) -> bool:
        """Limpiar archivos temporales para liberar espacio"""
        try:
            temp_dirs = [
                self.workspace_manager.ruta_proyecto / "temp",
                self.workspace_manager.ruta_proyecto / "logs"
            ]
            
            espacio_liberado = 0
            
            for temp_dir in temp_dirs:
                if temp_dir.exists():
                    for archivo in temp_dir.rglob("*"):
                        if archivo.is_file():
                            # Eliminar archivos más antiguos de 7 días
                            edad = datetime.now() - datetime.fromtimestamp(archivo.stat().st_mtime)
                            if edad > timedelta(days=7):
                                tamano = archivo.stat().st_size
                                archivo.unlink()
                                espacio_liberado += tamano
            
            espacio_liberado_mb = espacio_liberado / (1024*1024)
            self.logger.info(f"🧹 Limpieza completada: {espacio_liberado_mb:.1f} MB liberados")
            return True
            
        except Exception as e:
            self.logger.error(f"Error en limpieza: {e}")
            return False


class WorkspaceManagerAvanzado:
    """Workspace Manager ultra-avanzado con todas las capacidades robustas"""
    
    def __init__(self, ruta_proyecto: str = "./vision_narrador_proyecto"):
        self.ruta_proyecto = Path(ruta_proyecto)
        self.logger = self._configurar_logging()
        
        # Inicializar componentes ultra-robustos
        self.configuracion = ConfiguracionUltraRobusta(str(self.ruta_proyecto))
        self.gestor_estado = GestorEstadoAvanzado(self.ruta_proyecto)
        
        # Sistemas de monitoreo y reparación
        self.monitor_integridad = MonitorIntegridad(self)
        self.sistema_reparacion = SistemaReparacionAutomatica(self)
        
        # Estado del workspace
        self.archivos_trackeados: Dict[str, ArchiveInfo] = {}
        self.problemas_detectados: List[ProblemaDetectado] = []
        self.metricas: MetricasRendimiento = MetricasRendimiento(0, 0, 0, 0, 0, 0, 0, 0)
        
        # Sistema de locks
        self.lock_workspace = threading.RLock()
        
        # Inicializar
        self._inicializar_workspace()
    
    def _configurar_logging(self) -> logging.Logger:
        """Configurar logging específico para WorkspaceManager"""
        logger = logging.getLogger(f"WorkspaceManagerAvanzado_{id(self)}")
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        
        return logger
    
    def _inicializar_workspace(self):
        """Inicializar workspace con validación completa"""
        try:
            with self.lock_workspace:
                self.logger.info("🚀 Inicializando Workspace Manager Avanzado...")
                
                # 1. Inicializar configuración ultra-robusta
                config_exito, config_resultado = self.configuracion.inicializar_sistema_completo()
                if not config_exito:
                    raise Exception(f"Fallo en configuración: {config_resultado}")
                
                # 2. Inicializar sistema de estado
                estado_exito, estado_inicial = self.gestor_estado.inicializar_estado()
                if not estado_exito:
                    raise Exception(f"Fallo en sistema de estado: {estado_inicial}")
                
                # 3. Validar y reparar estructura de directorios
                self._validar_estructura_directorios()
                
                # 4. Escanear y validar archivos existentes
                self._escanear_workspace()
                
                # 5. Iniciar monitoreo de integridad
                self.monitor_integridad.iniciar_monitoreo()
                
                self.logger.info("✅ Workspace Manager Avanzado inicializado correctamente")
                
        except Exception as e:
            self.logger.error(f"Error inicializando workspace: {e}")
            raise
    
    def _validar_estructura_directorios(self):
        """Validar y crear estructura de directorios requerida"""
        try:
            directorios_requeridos = [
                "chapters", "assets", "assets/characters", "assets/locations",
                "assets/objects", "assets/scenes", "audio", "videos", 
                "output", "temp", "logs", "backups_estado", "cuarentena"
            ]
            
            directorios_faltantes = []
            
            for directorio in directorios_requeridos:
                dir_path = self.ruta_proyecto / directorio
                if not dir_path.exists():
                    directorios_faltantes.append(directorio)
                    dir_path.mkdir(parents=True, exist_ok=True)
            
            if directorios_faltantes:
                self.logger.info(f"📁 Directorios creados: {', '.join(directorios_faltantes)}")
            else:
                self.logger.info("✅ Estructura de directorios validada")
                
        except Exception as e:
            self.logger.error(f"Error validando estructura: {e}")
            problema = ProblemaDetectado(
                tipo=TipoProblema.ESTRUCTURA_DIRECTORIO_INVALIDA,
                descripcion=f"Error en estructura de directorios: {e}",
                archivo_afectado=None,
                severidad="alto",
                timestamp=datetime.now()
            )
            self._manejar_problema(problema)
    
    def _escanear_workspace(self):
        """Escanear y catalogar todos los archivos del workspace"""
        try:
            self.logger.info("🔍 Escaneando workspace...")
            
            archivos_encontrados = 0
            
            # Escanear directorios importantes
            directorios_importantes = ["chapters", "assets", "audio", "videos", "output"]
            
            for directorio in directorios_importantes:
                dir_path = self.ruta_proyecto / directorio
                if dir_path.exists():
                    for archivo in dir_path.rglob("*"):
                        if archivo.is_file():
                            self._agregar_archivo_tracking(archivo)
                            archivos_encontrados += 1
            
            # Archivos críticos en raíz
            archivos_criticos = ["state.json", "configuracion_adaptativa.json"]
            for archivo_nombre in archivos_criticos:
                archivo_path = self.ruta_proyecto / archivo_nombre
                if archivo_path.exists():
                    self._agregar_archivo_tracking(archivo_path)
                    archivos_encontrados += 1
            
            self.logger.info(f"✅ Escaneo completado: {archivos_encontrados} archivos encontrados")
            
        except Exception as e:
            self.logger.error(f"Error escaneando workspace: {e}")
    
    def _agregar_archivo_tracking(self, archivo: Path):
        """Agregar archivo al sistema de tracking"""
        try:
            archivo_key = str(archivo.relative_to(self.ruta_proyecto))
            
            # Calcular hash del archivo
            hash_sha256 = self._calcular_hash_archivo(archivo)
            
            archivo_info = ArchiveInfo(
                path=archivo,
                size=archivo.stat().st_size,
                hash_sha256=hash_sha256,
                last_modified=datetime.fromtimestamp(archivo.stat().st_mtime),
                estado=EstadoArchivo.PENDIENTE_VALIDACION,
                last_validation=None,
                corruption_checks=0,
                repair_attempts=0,
                metadata={}
            )
            
            self.archivos_trackeados[archivo_key] = archivo_info
            
        except Exception as e:
            self.logger.error(f"Error agregando archivo a tracking: {e}")
    
    def _calcular_hash_archivo(self, archivo: Path) -> str:
        """Calcular hash SHA-256 de un archivo"""
        try:
            hash_obj = hashlib.sha256()
            with open(archivo, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()
        except Exception:
            return ""
    
    def detectar_capitulos_nuevos(self) -> List[Dict[str, Any]]:
        """Detectar capítulos nuevos o modificados con validación robusta"""
        try:
            with self.lock_workspace:
                capitulos_para_procesar = []
                chapters_dir = self.ruta_proyecto / "chapters"
                
                if not chapters_dir.exists():
                    self.logger.warning("📁 Directorio de capítulos no existe")
                    return []
                
                # Obtener estado actual
                estado_actual = self.gestor_estado.obtener_estado_actual()
                capitulos_procesados = estado_actual.get("processing_state", {}).get("processed_chapters", {})
                
                # Escanear archivos de capítulos
                for archivo in chapters_dir.glob("*.txt"):
                    try:
                        # Validar integridad del archivo
                        if not self._validar_archivo_capitulo(archivo):
                            self.logger.warning(f"⚠️ Archivo de capítulo inválido: {archivo.name}")
                            continue
                        
                        # Calcular hash para detectar cambios
                        hash_actual = self._calcular_hash_archivo(archivo)
                        hash_anterior = capitulos_procesados.get(archivo.name, {}).get("hash", "")
                        
                        # Determinar si necesita procesamiento
                        if hash_actual != hash_anterior:
                            capitulo_info = {
                                "filename": archivo.name,
                                "path": str(archivo),
                                "size": archivo.stat().st_size,
                                "hash": hash_actual,
                                "last_modified": datetime.fromtimestamp(archivo.stat().st_mtime).isoformat(),
                                "status": "nuevo" if not hash_anterior else "modificado"
                            }
                            capitulos_para_procesar.append(capitulo_info)
                    
                    except Exception as e:
                        self.logger.error(f"Error procesando capítulo {archivo.name}: {e}")
                
                self.logger.info(f"📚 Capítulos detectados para procesamiento: {len(capitulos_para_procesar)}")
                return capitulos_para_procesar
                
        except Exception as e:
            self.logger.error(f"Error detectando capítulos: {e}")
            return []
    
    def _validar_archivo_capitulo(self, archivo: Path) -> bool:
        """Validar que un archivo de capítulo es válido"""
        try:
            # Verificar que el archivo existe y no está vacío
            if not archivo.exists() or archivo.stat().st_size == 0:
                return False
            
            # Verificar que se puede leer
            with open(archivo, 'r', encoding='utf-8') as f:
                contenido = f.read()
            
            # Verificar contenido mínimo
            if len(contenido.strip()) < 100:  # Al menos 100 caracteres
                return False
            
            return True
            
        except Exception:
            return False
    
    def _manejar_problema(self, problema: ProblemaDetectado):
        """Manejar un problema detectado"""
        try:
            self.problemas_detectados.append(problema)
            
            self.logger.warning(f"⚠️ Problema detectado: {problema.tipo.value} - {problema.descripcion}")
            
            # Intentar reparación automática según severidad
            if problema.severidad in ["critico", "alto"] and problema.intentos_reparacion < 3:
                self.logger.info(f"🔧 Intentando reparación automática...")
                
                exito_reparacion = self.sistema_reparacion.reparar_problema(problema)
                problema.intentos_reparacion += 1
                
                if exito_reparacion:
                    problema.resuelto = True
                    problema.accion_correctiva = "Reparación automática exitosa"
                    self.logger.info(f"✅ Problema reparado automáticamente: {problema.tipo.value}")
                else:
                    self.logger.error(f"❌ Fallo en reparación automática: {problema.tipo.value}")
            
        except Exception as e:
            self.logger.error(f"Error manejando problema: {e}")
    
    def obtener_estadisticas_workspace(self) -> Dict[str, Any]:
        """Obtener estadísticas completas del workspace"""
        try:
            with self.lock_workspace:
                # Calcular métricas actuales
                total_archivos = len(self.archivos_trackeados)
                archivos_saludables = sum(1 for info in self.archivos_trackeados.values() 
                                        if info.estado == EstadoArchivo.SALUDABLE)
                problemas_activos = sum(1 for problema in self.problemas_detectados if not problema.resuelto)
                
                # Información del sistema
                memoria = psutil.virtual_memory()
                disco = shutil.disk_usage(self.ruta_proyecto)
                
                estadisticas = {
                    "timestamp": datetime.now().isoformat(),
                    "archivos": {
                        "total": total_archivos,
                        "saludables": archivos_saludables,
                        "en_seguimiento": len(self.archivos_trackeados)
                    },
                    "problemas": {
                        "detectados": len(self.problemas_detectados),
                        "activos": problemas_activos,
                        "resueltos": len(self.problemas_detectados) - problemas_activos
                    },
                    "sistema": {
                        "uso_memoria_percent": memoria.percent,
                        "memoria_disponible_gb": memoria.available / (1024**3),
                        "espacio_disco_disponible_gb": disco.free / (1024**3),
                        "espacio_disco_total_gb": disco.total / (1024**3)
                    },
                    "workspace": {
                        "ruta_proyecto": str(self.ruta_proyecto),
                        "monitor_activo": self.monitor_integridad.running,
                        "configuracion_version": self.configuracion.configuraciones_ambiente.get("version_configuracion", "unknown")
                    }
                }
                
                return estadisticas
                
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas: {e}")
            return {"error": str(e)}
    
    def cerrar_workspace(self):
        """Cerrar workspace de manera segura"""
        try:
            with self.lock_workspace:
                self.logger.info("🔄 Cerrando Workspace Manager...")
                
                # Detener monitor de integridad
                self.monitor_integridad.detener_monitoreo()
                
                # Guardar estado final
                self.gestor_estado.guardar_estado()
                
                # Crear backup final
                self.gestor_estado.crear_backup_completo()
                
                self.logger.info("✅ Workspace cerrado correctamente")
                
        except Exception as e:
            self.logger.error(f"Error cerrando workspace: {e}")


# Instancia global para compatibilidad
WORKSPACE_MANAGER_AVANZADO = None

def obtener_workspace_manager() -> WorkspaceManagerAvanzado:
    """Obtener instancia singleton del workspace manager"""
    global WORKSPACE_MANAGER_AVANZADO
    if WORKSPACE_MANAGER_AVANZADO is None:
        WORKSPACE_MANAGER_AVANZADO = WorkspaceManagerAvanzado()
    return WORKSPACE_MANAGER_AVANZADO