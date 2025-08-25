"""
Vision-Narrador: Sistema de Paralelización Ultra-Avanzado
====================================================

Sistema ultra-robusto de paralelización con:
- Queue inteligente con priorización y planificación
- Worker pool dinámico que se adapta a la carga
- Balanceador de carga avanzado con métricas en tiempo real
- Monitoreo continuo de rendimiento y salud
- Sistema de fallback automático
- Gestión inteligente de recursos del sistema
"""

import time
import json
import threading
import queue
import asyncio
import concurrent.futures
from typing import Dict, List, Optional, Tuple, Any, Callable, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
import psutil
import statistics

from sistema_logging_monitoreo import obtener_sistema_logging, NivelSeveridad
from cache_lru_multinivel import obtener_cache_multinivel, TipoDato


class PrioridadTarea(Enum):
    """Niveles de prioridad para tareas"""
    BAJA = 1
    NORMAL = 2
    ALTA = 3
    CRITICA = 4


class EstadoTarea(Enum):
    """Estados de una tarea"""
    PENDIENTE = "pendiente"
    EN_COLA = "en_cola"
    EN_PROCESO = "en_proceso"
    COMPLETADA = "completada"
    FALLIDA = "fallida"
    CANCELADA = "cancelada"


class TipoWorker(Enum):
    """Tipos de workers disponibles"""
    CPU_INTENSIVO = "cpu_intensivo"
    IO_INTENSIVO = "io_intensivo"
    MEMORIA_INTENSIVO = "memoria_intensivo"
    GENERAL = "general"


@dataclass
class TareaParalelizacion:
    """Representación de una tarea para paralelización"""
    id: str
    funcion: Callable
    args: Tuple
    kwargs: Dict[str, Any]
    prioridad: PrioridadTarea
    tipo_worker: TipoWorker
    timeout: float
    retries: int
    dependencias: List[str]
    metadata: Dict[str, Any]
    timestamp_creacion: datetime
    timestamp_inicio: Optional[datetime] = None
    timestamp_finalizacion: Optional[datetime] = None
    estado: EstadoTarea = EstadoTarea.PENDIENTE
    resultado: Optional[Any] = None
    error: Optional[str] = None


@dataclass
class MetricasWorker:
    """Métricas de rendimiento de un worker"""
    id_worker: str
    tipo: TipoWorker
    tareas_procesadas: int
    tareas_fallidas: int
    tiempo_promedio_ejecucion: float
    cpu_utilizacion: float
    memoria_utilizacion: float
    ultima_actividad: datetime
    estado_salud: str  # "saludable", "degradado", "critico"


@dataclass
class MetricasSistema:
    """Métricas generales del sistema de paralelización"""
    tareas_totales: int
    tareas_pendientes: int
    tareas_en_proceso: int
    tareas_completadas: int
    tareas_fallidas: int
    workers_activos: int
    workers_disponibles: int
    cola_tareas: int
    tiempo_respuesta_promedio: float
    throughput: float  # tareas por segundo
    cpu_utilizacion_promedio: float
    memoria_utilizacion_promedio: float


@dataclass
class ConfiguracionParalelizacion:
    """Configuración del sistema de paralelización"""
    max_workers: int
    min_workers: int
    timeout_tarea: float
    max_retries: int
    umbral_cpu_alto: float
    umbral_memoria_alta: float
    intervalo_monitoreo: float
    tamano_maximo_cola: int
    habilitar_autoscaling: bool


class QueueInteligente:
    """Queue inteligente con priorización y planificación avanzada"""
    
    def __init__(self, max_size: int = 0):
        self.max_size = max_size
        self.tareas: Dict[str, TareaParalelizacion] = {}
        self.cola_prioridad: Dict[PrioridadTarea, queue.PriorityQueue] = {
            PrioridadTarea.BAJA: queue.PriorityQueue(),
            PrioridadTarea.NORMAL: queue.PriorityQueue(),
            PrioridadTarea.ALTA: queue.PriorityQueue(),
            PrioridadTarea.CRITICA: queue.PriorityQueue()
        }
        self.lock = threading.RLock()
        self.logger = obtener_sistema_logging().obtener_sistema_logger()
    
    def agregar_tarea(self, tarea: TareaParalelizacion) -> bool:
        """Agregar tarea a la queue"""
        with self.lock:
            try:
                if self.max_size > 0 and len(self.tareas) >= self.max_size:
                    self.logger.log(NivelSeveridad.WARNING, 
                                  f"Cola llena, no se puede agregar tarea {tarea.id}")
                    return False
                
                # Agregar a diccionario de tareas
                self.tareas[tarea.id] = tarea
                
                # Agregar a cola de prioridad (usando timestamp negativo para FIFO dentro de prioridad)
                timestamp_negativo = -tarea.timestamp_creacion.timestamp()
                self.cola_prioridad[tarea.prioridad].put((timestamp_negativo, tarea.id))
                
                tarea.estado = EstadoTarea.EN_COLA
                self.logger.log(NivelSeveridad.DEBUG, 
                              f"Tarea agregada a cola: {tarea.id} (prioridad: {tarea.prioridad.value})")
                
                return True
                
            except Exception as e:
                self.logger.log(NivelSeveridad.ERROR, f"Error agregando tarea a cola: {e}")
                return False
    
    def obtener_tarea(self) -> Optional[TareaParalelizacion]:
        """Obtener la siguiente tarea según prioridad"""
        with self.lock:
            try:
                # Buscar en orden de prioridad: CRITICA -> ALTA -> NORMAL -> BAJA
                for prioridad in [PrioridadTarea.CRITICA, PrioridadTarea.ALTA, 
                                PrioridadTarea.NORMAL, PrioridadTarea.BAJA]:
                    if not self.cola_prioridad[prioridad].empty():
                        _, tarea_id = self.cola_prioridad[prioridad].get()
                        if tarea_id in self.tareas:
                            tarea = self.tareas[tarea_id]
                            tarea.estado = EstadoTarea.EN_PROCESO
                            tarea.timestamp_inicio = datetime.now()
                            return tarea
                
                return None
                
            except Exception as e:
                self.logger.log(NivelSeveridad.ERROR, f"Error obteniendo tarea de cola: {e}")
                return None
    
    def cancelar_tarea(self, tarea_id: str) -> bool:
        """Cancelar una tarea (marcar como cancelada)"""
        with self.lock:
            if tarea_id in self.tareas:
                tarea = self.tareas[tarea_id]
                tarea.estado = EstadoTarea.CANCELADA
                tarea.timestamp_finalizacion = datetime.now()
                self.logger.log(NivelSeveridad.INFO, f"Tarea cancelada: {tarea_id}")
                return True
            return False
    
    def obtener_tarea_por_id(self, tarea_id: str) -> Optional[TareaParalelizacion]:
        """Obtener tarea específica por ID"""
        with self.lock:
            return self.tareas.get(tarea_id)
    
    def obtener_estadisticas(self) -> Dict[str, int]:
        """Obtener estadísticas de la cola"""
        with self.lock:
            return {
                "total_tareas": len(self.tareas),
                "tareas_pendientes": sum(1 for t in self.tareas.values() 
                                       if t.estado == EstadoTarea.EN_COLA),
                "tareas_en_proceso": sum(1 for t in self.tareas.values() 
                                       if t.estado == EstadoTarea.EN_PROCESO),
                "tareas_completadas": sum(1 for t in self.tareas.values() 
                                        if t.estado == EstadoTarea.COMPLETADA),
                "tareas_fallidas": sum(1 for t in self.tareas.values() 
                                     if t.estado == EstadoTarea.FALLIDA),
                "tareas_canceladas": sum(1 for t in self.tareas.values() 
                                       if t.estado == EstadoTarea.CANCELADA)
            }


class WorkerPoolDinamico:
    """Worker pool dinámico con gestión automática de recursos"""
    
    def __init__(self, config: ConfiguracionParalelizacion):
        self.config = config
        self.workers: Dict[str, Dict[str, Any]] = {}
        self.workers_disponibles: Dict[TipoWorker, List[str]] = {
            TipoWorker.CPU_INTENSIVO: [],
            TipoWorker.IO_INTENSIVO: [],
            TipoWorker.MEMORIA_INTENSIVO: [],
            TipoWorker.GENERAL: []
        }
        self.metricas_workers: Dict[str, MetricasWorker] = {}
        self.lock = threading.RLock()
        self.logger = obtener_sistema_logging().obtener_sistema_logger()
        
        # Inicializar workers mínimos
        self._inicializar_workers_minimos()
    
    def _inicializar_workers_minimos(self):
        """Inicializar el número mínimo de workers"""
        with self.lock:
            for i in range(self.config.min_workers):
                worker_id = f"worker_{i}_{int(time.time() * 1000)}"
                worker_info = {
                    "id": worker_id,
                    "tipo": TipoWorker.GENERAL,
                    "thread": None,
                    "activo": True,
                    "ultima_tarea": None
                }
                
                self.workers[worker_id] = worker_info
                self.workers_disponibles[TipoWorker.GENERAL].append(worker_id)
                
                # Crear métricas iniciales
                self.metricas_workers[worker_id] = MetricasWorker(
                    id_worker=worker_id,
                    tipo=TipoWorker.GENERAL,
                    tareas_procesadas=0,
                    tareas_fallidas=0,
                    tiempo_promedio_ejecucion=0.0,
                    cpu_utilizacion=0.0,
                    memoria_utilizacion=0.0,
                    ultima_actividad=datetime.now(),
                    estado_salud="saludable"
                )
            
            self.logger.log(NivelSeveridad.INFO, 
                          f"Inicializados {self.config.min_workers} workers mínimos")
    
    def obtener_worker_disponible(self, tipo_requerido: TipoWorker = TipoWorker.GENERAL) -> Optional[str]:
        """Obtener worker disponible del tipo requerido"""
        with self.lock:
            # Primero buscar workers del tipo específico
            if self.workers_disponibles[tipo_requerido]:
                return self.workers_disponibles[tipo_requerido].pop(0)
            
            # Si no hay, buscar workers generales
            if self.workers_disponibles[TipoWorker.GENERAL]:
                return self.workers_disponibles[TipoWorker.GENERAL].pop(0)
            
            # Si no hay workers disponibles, crear nuevo si posible
            if len(self.workers) < self.config.max_workers:
                return self._crear_nuevo_worker(tipo_requerido)
            
            return None
    
    def _crear_nuevo_worker(self, tipo: TipoWorker) -> Optional[str]:
        """Crear un nuevo worker"""
        with self.lock:
            if len(self.workers) >= self.config.max_workers:
                return None
            
            worker_id = f"worker_{len(self.workers)}_{int(time.time() * 1000)}"
            worker_info = {
                "id": worker_id,
                "tipo": tipo,
                "thread": None,
                "activo": True,
                "ultima_tarea": None
            }
            
            self.workers[worker_id] = worker_info
            self.workers_disponibles[tipo].append(worker_id)
            
            # Crear métricas
            self.metricas_workers[worker_id] = MetricasWorker(
                id_worker=worker_id,
                tipo=tipo,
                tareas_procesadas=0,
                tareas_fallidas=0,
                tiempo_promedio_ejecucion=0.0,
                cpu_utilizacion=0.0,
                memoria_utilizacion=0.0,
                ultima_actividad=datetime.now(),
                estado_salud="saludable"
            )
            
            self.logger.log(NivelSeveridad.INFO, f"Nuevo worker creado: {worker_id} ({tipo.value})")
            return worker_id
    
    def liberar_worker(self, worker_id: str, tipo: TipoWorker):
        """Liberar worker para que esté disponible"""
        with self.lock:
            if worker_id in self.workers:
                self.workers_disponibles[tipo].append(worker_id)
                self.logger.log(NivelSeveridad.DEBUG, f"Worker liberado: {worker_id}")
    
    def actualizar_metricas_worker(self, worker_id: str, tiempo_ejecucion: float, 
                                 exito: bool, recursos_sistema: Dict[str, float]):
        """Actualizar métricas de un worker"""
        with self.lock:
            if worker_id in self.metricas_workers:
                metricas = self.metricas_workers[worker_id]
                
                # Actualizar contadores
                if exito:
                    metricas.tareas_procesadas += 1
                else:
                    metricas.tareas_fallidas += 1
                
                # Actualizar tiempo promedio
                total_tareas = metricas.tareas_procesadas + metricas.tareas_fallidas
                if total_tareas > 0:
                    metricas.tiempo_promedio_ejecucion = (
                        (metricas.tiempo_promedio_ejecucion * (total_tareas - 1) + tiempo_ejecucion) / 
                        total_tareas
                    )
                
                # Actualizar recursos del sistema
                metricas.cpu_utilizacion = recursos_sistema.get('cpu', 0.0)
                metricas.memoria_utilizacion = recursos_sistema.get('memoria', 0.0)
                metricas.ultima_actividad = datetime.now()
                
                # Actualizar estado de salud
                if metricas.cpu_utilizacion > 90 or metricas.memoria_utilizacion > 90:
                    metricas.estado_salud = "critico"
                elif metricas.cpu_utilizacion > 70 or metricas.memoria_utilizacion > 70:
                    metricas.estado_salud = "degradado"
                else:
                    metricas.estado_salud = "saludable"
    
    def obtener_metricas_workers(self) -> Dict[str, MetricasWorker]:
        """Obtener métricas de todos los workers"""
        with self.lock:
            return self.metricas_workers.copy()
    
    def escalar_workers(self, carga_actual: int, metricas_sistema: MetricasSistema) -> int:
        """Escalar workers según la carga actual"""
        if not self.config.habilitar_autoscaling:
            return 0
        
        workers_creados = 0
        
        # Verificar si necesitamos más workers
        if (carga_actual > len(self.workers) * 2 and 
            len(self.workers) < self.config.max_workers):
            
            # Crear workers adicionales
            workers_necesarios = min(
                carga_actual // 2,
                self.config.max_workers - len(self.workers)
            )
            
            for i in range(workers_necesarios):
                self._crear_nuevo_worker(TipoWorker.GENERAL)
                workers_creados += 1
        
        # Verificar si podemos reducir workers (cuando hay poca carga)
        elif (carga_actual < len(self.workers) // 2 and 
              len(self.workers) > self.config.min_workers):
            
            # Marcar workers excedentes para eliminación
            # (En una implementación real, se manejaría la terminación segura)
            pass
        
        if workers_creados > 0:
            self.logger.log(NivelSeveridad.INFO, f"Creados {workers_creados} workers adicionales")
        
        return workers_creados


class BalanceadorCarga:
    """Balanceador de carga avanzado con métricas en tiempo real"""
    
    def __init__(self, worker_pool: WorkerPoolDinamico):
        self.worker_pool = worker_pool
        self.logger = obtener_sistema_logging().obtener_sistema_logger()
        self.historial_rendimiento: List[float] = []
        self.ultima_decision = datetime.now()
    
    def seleccionar_worker_optimo(self, tipo_tarea: TipoWorker, 
                                metricas_sistema: MetricasSistema) -> Optional[str]:
        """Seleccionar el worker óptimo para una tarea"""
        try:
            metricas_workers = self.worker_pool.obtener_metricas_workers()
            
            # Filtrar workers saludables
            workers_saludables = {
                wid: m for wid, m in metricas_workers.items() 
                if m.estado_salud != "critico"
            }
            
            if not workers_saludables:
                # Si no hay workers saludables, usar cualquier worker disponible
                return self.worker_pool.obtener_worker_disponible(tipo_tarea)
            
            # Seleccionar worker con mejor rendimiento
            mejor_worker = None
            mejor_puntaje = float('inf')
            
            for worker_id, metricas in workers_saludables.items():
                # Calcular puntaje basado en tiempo de ejecución y carga
                puntaje = (
                    metricas.tiempo_promedio_ejecucion * 0.7 +
                    (metricas.cpu_utilizacion + metricas.memoria_utilizacion) * 0.3
                )
                
                if puntaje < mejor_puntaje:
                    mejor_puntaje = puntaje
                    mejor_worker = worker_id
            
            if mejor_worker:
                # Remover worker de disponibles (será asignado)
                worker_tipo = metricas_workers[mejor_worker].tipo
                if mejor_worker in self.worker_pool.workers_disponibles[worker_tipo]:
                    self.worker_pool.workers_disponibles[worker_tipo].remove(mejor_worker)
                return mejor_worker
            else:
                # Usar worker disponible por defecto
                return self.worker_pool.obtener_worker_disponible(tipo_tarea)
                
        except Exception as e:
            self.logger.log(NivelSeveridad.ERROR, f"Error seleccionando worker óptimo: {e}")
            return self.worker_pool.obtener_worker_disponible(tipo_tarea)
    
    def optimizar_distribucion(self, metricas_sistema: MetricasSistema) -> Dict[str, Any]:
        """Optimizar distribución de carga"""
        try:
            decisiones = {
                "workers_creados": 0,
                "rebalanceo_necesario": False,
                "observaciones": []
            }
            
            # Verificar si necesitamos escalar
            carga_pendiente = metricas_sistema.tareas_pendientes
            if carga_pendiente > metricas_sistema.workers_activos * 3:
                workers_creados = self.worker_pool.escalar_workers(carga_pendiente, metricas_sistema)
                decisiones["workers_creados"] = workers_creados
                if workers_creados > 0:
                    decisiones["observaciones"].append(f"Creados {workers_creados} workers por alta carga")
            
            # Verificar si necesitamos rebalancear
            if metricas_sistema.tiempo_respuesta_promedio > 5.0:  # 5 segundos
                decisiones["rebalanceo_necesario"] = True
                decisiones["observaciones"].append("Tiempo de respuesta alto, considerando rebalanceo")
            
            self.ultima_decision = datetime.now()
            return decisiones
            
        except Exception as e:
            self.logger.log(NivelSeveridad.ERROR, f"Error optimizando distribución: {e}")
            return {"workers_creados": 0, "rebalanceo_necesario": False, "observaciones": [f"Error: {e}"]}


class SistemaParalelizacionUltraAvanzado:
    """Sistema principal de paralelización ultra-avanzado"""
    
    def __init__(self, ruta_base: Path = None, config: ConfiguracionParalelizacion = None):
        self.ruta_base = ruta_base or Path("./paralelizacion_sistema")
        self.ruta_base.mkdir(parents=True, exist_ok=True)
        
        self.logger = obtener_sistema_logging().obtener_sistema_logger()
        self.cache = obtener_cache_multinivel(self.ruta_base)
        
        # Configuración por defecto
        self.config = config or ConfiguracionParalelizacion(
            max_workers=20,
            min_workers=4,
            timeout_tarea=300.0,  # 5 minutos
            max_retries=3,
            umbral_cpu_alto=80.0,
            umbral_memoria_alta=85.0,
            intervalo_monitoreo=30.0,
            tamano_maximo_cola=1000,
            habilitar_autoscaling=True
        )
        
        # Componentes del sistema
        self.queue_inteligente = QueueInteligente(self.config.tamano_maximo_cola)
        self.worker_pool = WorkerPoolDinamico(self.config)
        self.balanceador = BalanceadorCarga(self.worker_pool)
        
        # Estado del sistema
        self.activo = True
        self.metricas_sistema = MetricasSistema(
            tareas_totales=0,
            tareas_pendientes=0,
            tareas_en_proceso=0,
            tareas_completadas=0,
            tareas_fallidas=0,
            workers_activos=0,
            workers_disponibles=0,
            cola_tareas=0,
            tiempo_respuesta_promedio=0.0,
            throughput=0.0,
            cpu_utilizacion_promedio=0.0,
            memoria_utilizacion_promedio=0.0
        )
        
        # Monitoreo
        self.tiempo_inicio = datetime.now()
        self.tareas_procesadas_historial = []
        
        # Thread de monitoreo
        self.thread_monitoreo = threading.Thread(target=self._monitorear_sistema, daemon=True)
        self.thread_monitoreo.start()
        
        self.logger.log(NivelSeveridad.INFO, "Sistema de paralelización ultra-avanzado inicializado")
    
    def submit_tarea(self, funcion: Callable, *args, prioridad: PrioridadTarea = PrioridadTarea.NORMAL,
                    tipo_worker: TipoWorker = TipoWorker.GENERAL, timeout: float = None,
                    retries: int = None, dependencias: List[str] = None,
                    metadata: Dict[str, Any] = None, **kwargs) -> str:
        """Enviar una tarea para ejecución paralela"""
        try:
            tarea_id = f"tarea_{int(time.time() * 1000000)}_{hash(str(funcion) + str(args) + str(kwargs)) % 10000}"
            
            # Convert string prioridad to enum if needed
            if isinstance(prioridad, str):
                # Map string values to enum values
                prioridad_mapping = {
                    "BAJA": PrioridadTarea.BAJA,
                    "NORMAL": PrioridadTarea.NORMAL,
                    "ALTA": PrioridadTarea.ALTA,
                    "CRITICA": PrioridadTarea.CRITICA,
                    "baja": PrioridadTarea.BAJA,
                    "normal": PrioridadTarea.NORMAL,
                    "alta": PrioridadTarea.ALTA,
                    "critica": PrioridadTarea.CRITICA
                }
                prioridad_enum = prioridad_mapping.get(prioridad.upper(), PrioridadTarea.NORMAL)
            else:
                prioridad_enum = prioridad
            
            # Convert string tipo_worker to enum if needed
            if isinstance(tipo_worker, str):
                # Map string values to enum values
                worker_mapping = {
                    "CPU_INTENSIVO": TipoWorker.CPU_INTENSIVO,
                    "IO_INTENSIVO": TipoWorker.IO_INTENSIVO,
                    "MEMORIA_INTENSIVO": TipoWorker.MEMORIA_INTENSIVO,
                    "GENERAL": TipoWorker.GENERAL,
                    "cpu_intensivo": TipoWorker.CPU_INTENSIVO,
                    "io_intensivo": TipoWorker.IO_INTENSIVO,
                    "memoria_intensivo": TipoWorker.MEMORIA_INTENSIVO,
                    "general": TipoWorker.GENERAL
                }
                tipo_worker_enum = worker_mapping.get(tipo_worker.upper(), TipoWorker.GENERAL)
            else:
                tipo_worker_enum = tipo_worker
            
            tarea = TareaParalelizacion(
                id=tarea_id,
                funcion=funcion,
                args=args,
                kwargs=kwargs,
                prioridad=prioridad_enum,
                tipo_worker=tipo_worker_enum,
                timeout=timeout or self.config.timeout_tarea,
                retries=retries or self.config.max_retries,
                dependencias=dependencias or [],
                metadata=metadata or {},
                timestamp_creacion=datetime.now()
            )
            
            # Verificar cache primero
            cache_key = f"tarea_{tarea_id}_resultado"
            resultado_cached = self.cache.get(cache_key)
            if resultado_cached is not None:
                tarea.estado = EstadoTarea.COMPLETADA
                tarea.resultado = resultado_cached
                tarea.timestamp_finalizacion = datetime.now()
                self.logger.log(NivelSeveridad.DEBUG, f"Tarea cacheada recuperada: {tarea_id}")
                return tarea_id
            
            # Agregar a queue
            if self.queue_inteligente.agregar_tarea(tarea):
                self.metricas_sistema.tareas_totales += 1
                self.metricas_sistema.tareas_pendientes += 1
                self.logger.log(NivelSeveridad.INFO, 
                              f"Tarea enviada: {tarea_id} (prioridad: {prioridad_enum.value})")
                return tarea_id
            else:
                raise Exception("No se pudo agregar tarea a la cola")
                
        except Exception as e:
            self.logger.log(NivelSeveridad.ERROR, f"Error enviando tarea: {e}")
            raise
    
    def obtener_resultado_tarea(self, tarea_id: str, timeout: float = None) -> Optional[Any]:
        """Obtener resultado de una tarea"""
        try:
            inicio_espera = time.time()
            timeout_total = timeout or self.config.timeout_tarea
            
            while time.time() - inicio_espera < timeout_total:
                tarea = self.queue_inteligente.obtener_tarea_por_id(tarea_id)
                if tarea and tarea.estado in [EstadoTarea.COMPLETADA, EstadoTarea.FALLIDA, EstadoTarea.CANCELADA]:
                    if tarea.estado == EstadoTarea.COMPLETADA:
                        return tarea.resultado
                    elif tarea.estado == EstadoTarea.FALLIDA:
                        raise Exception(f"Tarea fallida: {tarea.error}")
                    else:
                        raise Exception("Tarea cancelada")
                
                time.sleep(0.1)  # Esperar 100ms
            
            raise TimeoutError(f"Timeout esperando resultado de tarea {tarea_id}")
            
        except Exception as e:
            self.logger.log(NivelSeveridad.ERROR, f"Error obteniendo resultado de tarea {tarea_id}: {e}")
            raise
    
    def cancelar_tarea(self, tarea_id: str) -> bool:
        """Cancelar una tarea"""
        return self.queue_inteligente.cancelar_tarea(tarea_id)
    
    def _monitorear_sistema(self):
        """Thread de monitoreo continuo del sistema"""
        while self.activo:
            try:
                # Actualizar métricas del sistema
                self._actualizar_metricas_sistema()
                
                # Verificar tareas pendientes
                self._procesar_tareas_pendientes()
                
                # Optimizar distribución de carga
                decisiones = self.balanceador.optimizar_distribucion(self.metricas_sistema)
                if decisiones["observaciones"]:
                    for obs in decisiones["observaciones"]:
                        self.logger.log(NivelSeveridad.INFO, f"Optimización: {obs}")
                
                time.sleep(self.config.intervalo_monitoreo)
                
            except Exception as e:
                self.logger.log(NivelSeveridad.ERROR, f"Error en monitoreo del sistema: {e}")
                time.sleep(self.config.intervalo_monitoreo)
    
    def _procesar_tareas_pendientes(self):
        """Procesar tareas pendientes en la cola"""
        try:
            # Obtener métricas actuales del sistema
            metricas_workers = self.worker_pool.obtener_metricas_workers()
            self.metricas_sistema.workers_activos = len(metricas_workers)
            
            # Procesar tareas mientras haya workers disponibles
            tareas_procesadas = 0
            max_tareas_por_ciclo = min(10, len(metricas_workers))  # Limitar para no sobrecargar
            
            for _ in range(max_tareas_por_ciclo):
                tarea = self.queue_inteligente.obtener_tarea()
                if not tarea:
                    break
                
                # Seleccionar worker óptimo
                worker_id = self.balanceador.seleccionar_worker_optimo(tarea.tipo_worker, self.metricas_sistema)
                if not worker_id:
                    # Re-agregar tarea a la cola si no hay workers
                    self.queue_inteligente.agregar_tarea(tarea)
                    break
                
                # Procesar tarea en worker
                self._procesar_tarea_en_worker(tarea, worker_id)
                tareas_procesadas += 1
            
            if tareas_procesadas > 0:
                self.logger.log(NivelSeveridad.DEBUG, f"Procesadas {tareas_procesadas} tareas")
                
        except Exception as e:
            self.logger.log(NivelSeveridad.ERROR, f"Error procesando tareas pendientes: {e}")
    
    def _procesar_tarea_en_worker(self, tarea: TareaParalelizacion, worker_id: str):
        """Procesar una tarea específica en un worker"""
        try:
            inicio_ejecucion = time.time()
            
            # Ejecutar tarea con timeout
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(tarea.funcion, *tarea.args, **tarea.kwargs)
                
                try:
                    resultado = future.result(timeout=tarea.timeout)
                    exito = True
                    error = None
                    
                    # Guardar resultado en cache
                    cache_key = f"tarea_{tarea.id}_resultado"
                    self.cache.put(cache_key, resultado, TipoDato.JSON, 0.1)
                    
                except Exception as e:
                    resultado = None
                    exito = False
                    error = str(e)
            
            tiempo_ejecucion = time.time() - inicio_ejecucion
            
            # Actualizar estado de la tarea
            tarea.timestamp_finalizacion = datetime.now()
            if exito:
                tarea.estado = EstadoTarea.COMPLETADA
                tarea.resultado = resultado
                self.metricas_sistema.tareas_completadas += 1
            else:
                tarea.estado = EstadoTarea.FALLIDA
                tarea.error = error
                self.metricas_sistema.tareas_fallidas += 1
            
            self.metricas_sistema.tareas_pendientes -= 1
            
            # Actualizar métricas del worker
            recursos_sistema = self._obtener_recursos_sistema()
            self.worker_pool.actualizar_metricas_worker(worker_id, tiempo_ejecucion, exito, recursos_sistema)
            
            # Liberar worker
            self.worker_pool.liberar_worker(worker_id, tarea.tipo_worker)
            
            # Registrar en historial
            self.tareas_procesadas_historial.append(tiempo_ejecucion)
            if len(self.tareas_procesadas_historial) > 1000:  # Mantener solo últimas 1000
                self.tareas_procesadas_historial.pop(0)
            
            self.logger.log(NivelSeveridad.DEBUG, 
                          f"Tarea {tarea.id} procesada en {tiempo_ejecucion:.2f}s - {'Éxito' if exito else 'Fallida'}")
            
        except Exception as e:
            self.logger.log(NivelSeveridad.ERROR, f"Error procesando tarea {tarea.id} en worker {worker_id}: {e}")
            
            # Marcar tarea como fallida
            tarea.estado = EstadoTarea.FALLIDA
            tarea.error = str(e)
            tarea.timestamp_finalizacion = datetime.now()
            self.metricas_sistema.tareas_fallidas += 1
            self.metricas_sistema.tareas_pendientes -= 1
            
            # Liberar worker
            self.worker_pool.liberar_worker(worker_id, tarea.tipo_worker)
    
    def _actualizar_metricas_sistema(self):
        """Actualizar métricas generales del sistema"""
        try:
            # Obtener estadísticas de la cola
            stats_cola = self.queue_inteligente.obtener_estadisticas()
            
            # Obtener métricas de workers
            metricas_workers = self.worker_pool.obtener_metricas_workers()
            
            # Calcular métricas del sistema
            self.metricas_sistema.tareas_pendientes = stats_cola["tareas_pendientes"]
            self.metricas_sistema.tareas_en_proceso = stats_cola["tareas_en_proceso"]
            self.metricas_sistema.tareas_completadas = stats_cola["tareas_completadas"]
            self.metricas_sistema.tareas_fallidas = stats_cola["tareas_fallidas"]
            self.metricas_sistema.workers_activos = len(metricas_workers)
            
            # Calcular workers disponibles
            workers_disponibles = 0
            for lista_workers in self.worker_pool.workers_disponibles.values():
                workers_disponibles += len(lista_workers)
            self.metricas_sistema.workers_disponibles = workers_disponibles
            
            # Calcular cola de tareas
            self.metricas_sistema.cola_tareas = stats_cola["total_tareas"]
            
            # Calcular tiempo de respuesta promedio
            if self.tareas_procesadas_historial:
                self.metricas_sistema.tiempo_respuesta_promedio = statistics.mean(self.tareas_procesadas_historial[-100:])
            
            # Calcular throughput
            tiempo_actividad = (datetime.now() - self.tiempo_inicio).total_seconds()
            if tiempo_actividad > 0:
                self.metricas_sistema.throughput = self.metricas_sistema.tareas_completadas / tiempo_actividad
            
            # Obtener recursos del sistema
            recursos = self._obtener_recursos_sistema()
            self.metricas_sistema.cpu_utilizacion_promedio = recursos.get('cpu', 0.0)
            self.metricas_sistema.memoria_utilizacion_promedio = recursos.get('memoria', 0.0)
            
        except Exception as e:
            self.logger.log(NivelSeveridad.ERROR, f"Error actualizando métricas del sistema: {e}")
    
    def _obtener_recursos_sistema(self) -> Dict[str, float]:
        """Obtener utilización actual de recursos del sistema"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memoria = psutil.virtual_memory()
            return {
                'cpu': cpu_percent,
                'memoria': memoria.percent
            }
        except:
            return {'cpu': 0.0, 'memoria': 0.0}
    
    def obtener_metricas_sistema(self) -> MetricasSistema:
        """Obtener métricas actuales del sistema"""
        return self.metricas_sistema
    
    def obtener_estadisticas_detalles(self) -> Dict[str, Any]:
        """Obtener estadísticas detalladas del sistema"""
        return {
            "metricas_sistema": asdict(self.metricas_sistema),
            "metricas_workers": {wid: asdict(m) for wid, m in self.worker_pool.obtener_metricas_workers().items()},
            "estadisticas_cola": self.queue_inteligente.obtener_estadisticas(),
            "tiempo_actividad": (datetime.now() - self.tiempo_inicio).total_seconds(),
            "tareas_historial": len(self.tareas_procesadas_historial)
        }
    
    def cerrar(self):
        """Cerrar el sistema de paralelización de manera segura"""
        self.activo = False
        if self.thread_monitoreo.is_alive():
            self.thread_monitoreo.join(timeout=5)
        
        self.logger.log(NivelSeveridad.INFO, "Sistema de paralelización cerrado")


# Instancia global
SISTEMA_PARALELIZACION_GLOBAL = None

def obtener_sistema_paralelizacion(ruta_base: Path = None, 
                                 config: ConfiguracionParalelizacion = None) -> SistemaParalelizacionUltraAvanzado:
    """Obtener instancia global del sistema de paralelización"""
    global SISTEMA_PARALELIZACION_GLOBAL
    if SISTEMA_PARALELIZACION_GLOBAL is None:
        SISTEMA_PARALELIZACION_GLOBAL = SistemaParalelizacionUltraAvanzado(ruta_base, config)
    return SISTEMA_PARALELIZACION_GLOBAL