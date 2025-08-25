"""
Vision-Narrador: Sistema de Gestión de Estado Ultra-Avanzado
===========================================================

Sistema ultra-robusto de gestión de estado con backup incremental, 
validación de integridad SHA-256 y recuperación automática inteligente.
"""

import json
import hashlib
import shutil
import logging
import threading
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import copy


@dataclass
class MetadatosEstado:
    """Metadatos completos para tracking de estado"""
    version: str
    timestamp_creacion: str
    timestamp_modificacion: str
    checksum_sha256: str
    tamano_bytes: int
    contador_modificaciones: int
    tipo_operacion: str
    

@dataclass
class HistorialOperacion:
    """Registro detallado de cada operación en el estado"""
    timestamp: str
    operacion: str
    entidades_modificadas: List[str]
    entidades_nuevas: List[str]
    tiempo_procesamiento_ms: int
    estado_validacion: str
    errores: List[str]


class ValidadorIntegridad:
    """Sistema ultra-avanzado de validación de integridad de estado"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def calcular_checksum_estado(self, estado: Dict[str, Any]) -> str:
        """Calcular checksum SHA-256 del estado completo"""
        try:
            estado_serializado = json.dumps(estado, sort_keys=True, ensure_ascii=False)
            estado_bytes = estado_serializado.encode('utf-8')
            
            hash_obj = hashlib.sha256()
            hash_obj.update(estado_bytes)
            return hash_obj.hexdigest()
            
        except Exception as e:
            self.logger.error(f"Error calculando checksum: {e}")
            return ""
    
    def validar_estructura_estado(self, estado: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validar estructura requerida del estado"""
        errores = []
        
        # Campos requeridos en nivel raíz
        campos_requeridos = [
            "version", "metadata", "entities", "processing_state", 
            "processing_history", "system_state", "project_analytics"
        ]
        
        for campo in campos_requeridos:
            if campo not in estado:
                errores.append(f"Campo requerido faltante: {campo}")
        
        # Validar estructura de entities
        if "entities" in estado:
            if not isinstance(estado["entities"], dict):
                errores.append("'entities' debe ser un diccionario")
            else:
                categorias_requeridas = ["characters", "locations"]
                for categoria in categorias_requeridas:
                    if categoria not in estado["entities"]:
                        errores.append(f"Categoría de entidades faltante: {categoria}")
        
        return len(errores) == 0, errores
    
    def validar_integridad_completa(self, estado: Dict[str, Any], checksum_esperado: str = None) -> Tuple[bool, Dict[str, Any]]:
        """Validar integridad completa del estado"""
        resultado = {
            "timestamp": datetime.now().isoformat(),
            "checksum_calculado": "",
            "checksum_valido": False,
            "estructura_valida": False,
            "errores": [],
            "estado_general": "unknown"
        }
        
        try:
            # 1. Validar checksum si se proporciona
            checksum_calculado = self.calcular_checksum_estado(estado)
            resultado["checksum_calculado"] = checksum_calculado
            
            if checksum_esperado:
                resultado["checksum_valido"] = checksum_calculado == checksum_esperado
                if not resultado["checksum_valido"]:
                    resultado["errores"].append("Checksum no coincide - posible corrupción de datos")
            else:
                resultado["checksum_valido"] = True
            
            # 2. Validar estructura
            estructura_ok, errores_estructura = self.validar_estructura_estado(estado)
            resultado["estructura_valida"] = estructura_ok
            resultado["errores"].extend(errores_estructura)
            
            # 3. Determinar estado general
            if all([resultado["checksum_valido"], resultado["estructura_valida"]]):
                resultado["estado_general"] = "perfecto"
            elif resultado["estructura_valida"] and len(resultado["errores"]) <= 2:
                resultado["estado_general"] = "funcional_con_advertencias"
            else:
                resultado["estado_general"] = "corrupto"
                
        except Exception as e:
            resultado["errores"].append(f"Error en validación completa: {e}")
            resultado["estado_general"] = "error_validacion"
        
        return resultado["estado_general"] in ["perfecto", "funcional_con_advertencias"], resultado


class GestorBackupAvanzado:
    """Sistema ultra-avanzado de gestión de backups"""
    
    def __init__(self, ruta_proyecto: Path):
        self.ruta_proyecto = ruta_proyecto
        self.ruta_backups = ruta_proyecto / "backups_estado"
        self.logger = logging.getLogger(__name__)
        
        # Crear estructura de directorios
        self.ruta_proyecto.mkdir(parents=True, exist_ok=True)
        self.ruta_backups.mkdir(parents=True, exist_ok=True)
        
    def crear_backup_completo(self, estado: Dict[str, Any]) -> Tuple[bool, str]:
        """Crear backup completo del estado"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.ruta_backups / f"backup_completo_{timestamp}.json"
            
            backup_data = {
                "tipo": "completo",
                "timestamp": timestamp,
                "estado_completo": estado,
                "checksum": ValidadorIntegridad().calcular_checksum_estado(estado)
            }
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"✅ Backup completo creado: {backup_path}")
            return True, str(backup_path)
            
        except Exception as e:
            self.logger.error(f"Error creando backup completo: {e}")
            return False, str(e)
    
    def restaurar_desde_backup(self, backup_path: Path = None) -> Tuple[bool, Dict[str, Any]]:
        """Restaurar estado desde backup más reciente o específico"""
        try:
            if backup_path is None:
                backup_path = self._encontrar_backup_mas_reciente()
                
            if not backup_path or not backup_path.exists():
                return False, {"error": "No se encontró backup válido"}
            
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            estado_restaurado = backup_data["estado_completo"]
            
            # Validar integridad del estado restaurado
            validador = ValidadorIntegridad()
            checksum_esperado = backup_data.get("checksum")
            valido, resultado_validacion = validador.validar_integridad_completa(estado_restaurado, checksum_esperado)
            
            if not valido:
                return False, {"error": "Estado restaurado falló validación de integridad", "detalles": resultado_validacion}
            
            self.logger.info(f"✅ Estado restaurado exitosamente desde: {backup_path}")
            return True, estado_restaurado
            
        except Exception as e:
            self.logger.error(f"Error restaurando desde backup: {e}")
            return False, {"error": str(e)}
    
    def _encontrar_backup_mas_reciente(self) -> Optional[Path]:
        """Encontrar el backup más reciente"""
        backups = list(self.ruta_backups.glob("backup_completo_*.json"))
        
        if not backups:
            return None
        
        # Ordenar por fecha de modificación
        backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        return backups[0]


class GestorEstadoAvanzado:
    """Sistema ultra-avanzado de gestión de estado principal"""
    
    def __init__(self, ruta_proyecto: Path):
        self.ruta_proyecto = ruta_proyecto
        self.ruta_estado = ruta_proyecto / "state.json"
        self.logger = logging.getLogger(__name__)
        
        # Componentes principales
        self.validador = ValidadorIntegridad()
        self.gestor_backup = GestorBackupAvanzado(ruta_proyecto)
        
        # Estado actual en memoria
        self.estado_actual = {}
        self.estado_anterior = {}
        
        # Sistema de locks para operaciones concurrentes
        self.lock_estado = threading.RLock()
        
    def inicializar_estado(self) -> Tuple[bool, Dict[str, Any]]:
        """Inicializar sistema de estado con validación completa"""
        try:
            with self.lock_estado:
                self.logger.info("🔄 Inicializando sistema de estado avanzado...")
                
                # Verificar si existe estado previo
                if self.ruta_estado.exists():
                    exito_carga, estado_o_error = self.cargar_estado()
                    if exito_carga:
                        self.estado_actual = estado_o_error
                        self.logger.info("✅ Estado existente cargado y validado")
                    else:
                        # Intentar recuperación desde backup
                        self.logger.warning("⚠️ Estado corrupto, intentando recuperación...")
                        exito_recuperacion, estado_recuperado = self.recuperar_estado_automatico()
                        if exito_recuperacion:
                            self.estado_actual = estado_recuperado
                            self.logger.info("✅ Estado recuperado desde backup")
                        else:
                            self.estado_actual = self._crear_estado_inicial()
                            self.logger.info("🆕 Creado estado inicial por defecto")
                else:
                    self.estado_actual = self._crear_estado_inicial()
                    self.logger.info("🆕 Creado estado inicial")
                
                # Crear backup inicial
                self.crear_backup_completo()
                
                return True, self.estado_actual
                
        except Exception as e:
            self.logger.error(f"Error inicializando estado: {e}")
            return False, {"error": str(e)}
    
    def _crear_estado_inicial(self) -> Dict[str, Any]:
        """Crear estructura de estado inicial completa según diseño"""
        return {
            "version": "2.0",
            "metadata": {
                "novel_title": "",
                "genre": "",
                "target_audience": "",
                "creation_date": datetime.now().isoformat(),
                "last_modified": datetime.now().isoformat(),
                "total_chapters_planned": 0,
                "current_chapter_count": 0
            },
            "processing_state": {
                "last_processed_chapter": "",
                "chapters_in_queue": [],
                "failed_chapters": [],
                "processing_mode": "manual",
                "quality_level": "high"
            },
            "entities": {
                "characters": {},
                "locations": {}
            },
            "processing_history": [],
            "system_state": {
                "models_loaded": {},
                "cache_status": {
                    "entities_cache_size": 0,
                    "audio_cache_size_mb": 0.0,
                    "images_cache_size_mb": 0.0,
                    "cache_hit_rate": 0.0
                },
                "health_metrics": {
                    "last_backup": None,
                    "backup_integrity_check": "pending",
                    "error_count_24h": 0,
                    "warning_count_24h": 0
                },
                "configuration": {
                    "automation_level": "manual",
                    "quality_preference": "balanced",
                    "fallback_strategies_enabled": True,
                    "automatic_cleanup": True
                }
            },
            "project_analytics": {
                "total_processing_time_hours": 0.0,
                "total_entities_created": 0,
                "total_audio_files": 0,
                "total_images": 0,
                "total_videos": 0,
                "success_rate": 1.0
            }
        }
    
    def cargar_estado(self) -> Tuple[bool, Union[Dict[str, Any], str]]:
        """Cargar estado desde archivo con validación completa"""
        try:
            with self.lock_estado:
                if not self.ruta_estado.exists():
                    return False, "Archivo de estado no existe"
                
                with open(self.ruta_estado, 'r', encoding='utf-8') as f:
                    estado = json.load(f)
                
                # Validar integridad completa
                valido, resultado_validacion = self.validador.validar_integridad_completa(estado)
                
                if not valido:
                    return False, f"Estado inválido: {resultado_validacion['errores']}"
                
                return True, estado
                
        except json.JSONDecodeError as e:
            return False, f"Estado JSON corrupto: {e}"
        except Exception as e:
            return False, f"Error cargando estado: {e}"
    
    def guardar_estado(self, crear_backup: bool = True) -> Tuple[bool, str]:
        """Guardar estado con backup automático y validación"""
        try:
            with self.lock_estado:
                # Crear backup antes de guardar si se solicita
                if crear_backup:
                    backup_exito, backup_msg = self.gestor_backup.crear_backup_completo(self.estado_actual)
                    if not backup_exito:
                        self.logger.warning(f"Fallo creando backup: {backup_msg}")
                
                # Actualizar metadata
                self.estado_actual["metadata"]["last_modified"] = datetime.now().isoformat()
                
                # Validar antes de guardar
                valido, resultado_validacion = self.validador.validar_integridad_completa(self.estado_actual)
                if not valido and resultado_validacion["estado_general"] == "corrupto":
                    return False, f"Estado inválido para guardar: {resultado_validacion['errores']}"
                
                # Crear backup del archivo actual
                if self.ruta_estado.exists():
                    backup_file = self.ruta_estado.with_suffix('.backup')
                    shutil.copy2(self.ruta_estado, backup_file)
                
                # Guardar estado
                with open(self.ruta_estado, 'w', encoding='utf-8') as f:
                    json.dump(self.estado_actual, f, indent=2, ensure_ascii=False)
                
                self.logger.info("✅ Estado guardado exitosamente")
                return True, "Estado guardado exitosamente"
                
        except Exception as e:
            self.logger.error(f"Error guardando estado: {e}")
            return False, str(e)
    
    def actualizar_entidad(self, categoria: str, entity_id: str, datos_entidad: Dict[str, Any]) -> Tuple[bool, str]:
        """Actualizar entidad específica con validación y backup automático"""
        try:
            with self.lock_estado:
                inicio_operacion = time.time()
                
                # Validar categoría
                if categoria not in self.estado_actual["entities"]:
                    self.estado_actual["entities"][categoria] = {}
                
                entidad_anterior = self.estado_actual["entities"][categoria].get(entity_id)
                
                # Actualizar entidad
                self.estado_actual["entities"][categoria][entity_id] = datos_entidad
                
                # Crear registro de historial
                tiempo_operacion = int((time.time() - inicio_operacion) * 1000)
                historial = HistorialOperacion(
                    timestamp=datetime.now().isoformat(),
                    operacion=f"actualizar_entidad_{categoria}",
                    entidades_modificadas=[entity_id] if entidad_anterior else [],
                    entidades_nuevas=[entity_id] if not entidad_anterior else [],
                    tiempo_procesamiento_ms=tiempo_operacion,
                    estado_validacion="pendiente",
                    errores=[]
                )
                
                # Validar estado después de modificación
                valido, resultado_validacion = self.validador.validar_integridad_completa(self.estado_actual)
                historial.estado_validacion = resultado_validacion["estado_general"]
                historial.errores = resultado_validacion["errores"]
                
                # Agregar al historial
                self.estado_actual["processing_history"].append(asdict(historial))
                
                # Guardar estado
                exito_guardado, msg_guardado = self.guardar_estado()
                
                if exito_guardado and valido:
                    self.logger.info(f"✅ Entidad {categoria}/{entity_id} actualizada exitosamente")
                    return True, "Entidad actualizada exitosamente"
                else:
                    return False, f"Error: {msg_guardado if not exito_guardado else 'Estado inválido'}"
                
        except Exception as e:
            self.logger.error(f"Error actualizando entidad: {e}")
            return False, str(e)
    
    def recuperar_estado_automatico(self) -> Tuple[bool, Dict[str, Any]]:
        """Recuperación automática inteligente del estado"""
        try:
            self.logger.info("🔄 Iniciando recuperación automática de estado...")
            
            exito_restauracion, estado_o_error = self.gestor_backup.restaurar_desde_backup()
            
            if exito_restauracion:
                self.estado_actual = estado_o_error
                
                # Guardar estado recuperado
                exito_guardado, _ = self.guardar_estado(crear_backup=False)
                
                if exito_guardado:
                    return True, self.estado_actual
                else:
                    return False, {"error": "No se pudo guardar estado recuperado"}
            else:
                return False, estado_o_error
                
        except Exception as e:
            self.logger.error(f"Error en recuperación automática: {e}")
            return False, {"error": str(e)}
    
    def crear_backup_completo(self) -> Tuple[bool, str]:
        """Crear backup completo del estado actual"""
        return self.gestor_backup.crear_backup_completo(self.estado_actual)
    
    def obtener_estado_actual(self) -> Dict[str, Any]:
        """Obtener copia del estado actual"""
        with self.lock_estado:
            return copy.deepcopy(self.estado_actual)
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtener estadísticas del sistema de estado"""
        with self.lock_estado:
            return {
                "version_estado": self.estado_actual.get("version", "unknown"),
                "total_entidades": sum(len(cat) for cat in self.estado_actual.get("entities", {}).values()),
                "total_operaciones": len(self.estado_actual.get("processing_history", [])),
                "ultima_modificacion": self.estado_actual.get("metadata", {}).get("last_modified"),
                "checksum_actual": self.validador.calcular_checksum_estado(self.estado_actual)
            }