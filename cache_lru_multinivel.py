"""
Vision-Narrador: Sistema de Cache LRU Multinivel Ultra-Robusto
==============================================================

Sistema ultra-avanzado de cache LRU con:
- Cache multinivel (L1: Memoria, L2: Disco, L3: Comprimido)
- Persistencia inteligente con compresión automática
- Liberación predictiva de memoria
- Monitoreo continuo de rendimiento
"""

import os
import pickle
import gzip
import json
import time
import threading
import hashlib
import psutil
import statistics
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from collections import OrderedDict
from enum import Enum
import gc

from sistema_logging_monitoreo import obtener_sistema_logging, NivelSeveridad


class NivelCache(Enum):
    """Niveles de cache disponibles"""
    L1_MEMORIA = "L1_memoria"
    L2_DISCO = "L2_disco"
    L3_COMPRIMIDO = "L3_comprimido"


class TipoDato(Enum):
    """Tipos de datos para optimización"""
    TEXTO = "texto"
    IMAGEN = "imagen"
    AUDIO = "audio"
    VIDEO = "video"
    JSON = "json"
    BINARIO = "binario"
    ENTIDADES = "entidades"


@dataclass
class MetadataCache:
    """Metadatos de entrada de cache"""
    clave: str
    tamano_bytes: int
    tipo_dato: TipoDato
    timestamp_creacion: datetime
    timestamp_acceso: datetime
    frecuencia_acceso: int
    nivel_cache: NivelCache
    comprimido: bool
    checksum: str
    tiempo_computacion: float
    prioridad: int = 5


@dataclass
class EstadisticasCache:
    """Estadísticas de rendimiento del cache"""
    hits_l1: int = 0
    hits_l2: int = 0
    hits_l3: int = 0
    misses: int = 0
    evictions: int = 0
    bytes_almacenados: int = 0
    tiempo_promedio_acceso: float = 0.0
    memoria_utilizada_mb: float = 0.0
    
    @property
    def total_hits(self) -> int:
        return self.hits_l1 + self.hits_l2 + self.hits_l3
    
    @property
    def hit_rate(self) -> float:
        total = self.total_hits + self.misses
        return (self.total_hits / total) * 100 if total > 0 else 0.0


class CompresorInteligente:
    """Sistema de compresión inteligente adaptativa"""
    
    def __init__(self):
        self.logger = obtener_sistema_logging().obtener_sistema_logger()
        self.ratios_compresion = {}
    
    def comprimir(self, datos: bytes, tipo_dato: TipoDato) -> Tuple[bytes, float]:
        """Comprimir datos con algoritmo adaptativo"""
        try:
            tamano_original = len(datos)
            nivel_compresion = 6 if tipo_dato in [TipoDato.TEXTO, TipoDato.JSON] else 3
            
            datos_comprimidos = gzip.compress(datos, compresslevel=nivel_compresion)
            ratio = tamano_original / len(datos_comprimidos) if datos_comprimidos else 1.0
            
            return datos_comprimidos, ratio
            
        except Exception as e:
            self.logger.log(NivelSeveridad.ERROR, f"Error comprimiendo: {e}")
            return datos, 1.0
    
    def descomprimir(self, datos_comprimidos: bytes) -> bytes:
        """Descomprimir datos"""
        try:
            return gzip.decompress(datos_comprimidos)
        except Exception as e:
            self.logger.log(NivelSeveridad.ERROR, f"Error descomprimiendo: {e}")
            return datos_comprimidos


class CacheL1Memoria:
    """Cache L1 en memoria RAM con LRU"""
    
    def __init__(self, capacidad_mb: float = 512):
        self.capacidad_bytes = int(capacidad_mb * 1024 * 1024)
        self.datos = OrderedDict()
        self.metadatos = {}
        self.tamano_actual = 0
        self.lock = threading.RLock()
        self.logger = obtener_sistema_logging().obtener_sistema_logger()
    
    def get(self, clave: str) -> Optional[Tuple[Any, MetadataCache]]:
        """Obtener elemento del cache L1"""
        with self.lock:
            if clave in self.datos:
                valor = self.datos.pop(clave)
                self.datos[clave] = valor  # Mover al final
                
                metadata = self.metadatos[clave]
                metadata.timestamp_acceso = datetime.now()
                metadata.frecuencia_acceso += 1
                
                return valor, metadata
            return None
    
    def put(self, clave: str, valor: Any, metadata: MetadataCache):
        """Almacenar elemento en cache L1"""
        with self.lock:
            if clave in self.datos:
                self.tamano_actual -= self.metadatos[clave].tamano_bytes
                del self.datos[clave]
                del self.metadatos[clave]
            
            while (self.tamano_actual + metadata.tamano_bytes > self.capacidad_bytes and 
                   len(self.datos) > 0):
                self._evict_lru()
            
            self.datos[clave] = valor
            self.metadatos[clave] = metadata
            self.tamano_actual += metadata.tamano_bytes
    
    def _evict_lru(self) -> Optional[str]:
        """Evitar elemento menos usado"""
        if not self.datos:
            return None
        
        clave_lru = next(iter(self.datos))
        self.datos.pop(clave_lru)
        metadata = self.metadatos.pop(clave_lru)
        self.tamano_actual -= metadata.tamano_bytes
        return clave_lru
    
    def clear(self):
        """Limpiar cache L1"""
        with self.lock:
            self.datos.clear()
            self.metadatos.clear()
            self.tamano_actual = 0
    
    def get_info(self) -> Dict[str, Any]:
        """Información del cache L1"""
        with self.lock:
            return {
                "nivel": "L1_memoria",
                "elementos": len(self.datos),
                "tamano_mb": self.tamano_actual / (1024 * 1024),
                "utilizacion_percent": (self.tamano_actual / self.capacidad_bytes) * 100
            }


class CacheL2Disco:
    """Cache L2 en disco con persistencia"""
    
    def __init__(self, ruta_cache: Path, capacidad_mb: float = 2048):
        self.ruta_cache = ruta_cache
        self.capacidad_bytes = int(capacidad_mb * 1024 * 1024)
        self.ruta_cache.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.ruta_cache / "metadata.json"
        self.lock = threading.RLock()
        self.logger = obtener_sistema_logging().obtener_sistema_logger()
        self.metadatos = self._cargar_metadatos()
    
    def _cargar_metadatos(self) -> Dict[str, Dict]:
        """Cargar metadatos desde disco"""
        try:
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
    
    def _guardar_metadatos(self):
        """Guardar metadatos a disco"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadatos, f, indent=2)
        except Exception as e:
            self.logger.log(NivelSeveridad.ERROR, f"Error guardando metadatos: {e}")
    
    def get(self, clave: str) -> Optional[Tuple[Any, MetadataCache]]:
        """Obtener del cache L2"""
        with self.lock:
            if clave in self.metadatos:
                try:
                    archivo = self.ruta_cache / f"{clave}.cache"
                    if archivo.exists():
                        with open(archivo, 'rb') as f:
                            datos = pickle.load(f)
                        
                        # Crear objeto MetadataCache
                        meta_dict = self.metadatos[clave]
                        metadata = MetadataCache(
                            clave=meta_dict["clave"],
                            tamano_bytes=meta_dict["tamano_bytes"],
                            tipo_dato=TipoDato(meta_dict["tipo_dato"]),
                            timestamp_creacion=datetime.fromisoformat(meta_dict["timestamp_creacion"]),
                            timestamp_acceso=datetime.now(),
                            frecuencia_acceso=meta_dict["frecuencia_acceso"] + 1,
                            nivel_cache=NivelCache(meta_dict["nivel_cache"]),
                            comprimido=meta_dict["comprimido"],
                            checksum=meta_dict["checksum"],
                            tiempo_computacion=meta_dict["tiempo_computacion"],
                            prioridad=meta_dict.get("prioridad", 5)
                        )
                        
                        # Actualizar metadatos
                        self.metadatos[clave]["timestamp_acceso"] = metadata.timestamp_acceso.isoformat()
                        self.metadatos[clave]["frecuencia_acceso"] = metadata.frecuencia_acceso
                        self._guardar_metadatos()
                        
                        return datos, metadata
                except Exception as e:
                    self.logger.log(NivelSeveridad.ERROR, f"Error leyendo L2 {clave}: {e}")
        return None
    
    def put(self, clave: str, valor: Any, metadata: MetadataCache):
        """Almacenar en cache L2"""
        with self.lock:
            try:
                self._limpiar_espacio(metadata.tamano_bytes)
                
                archivo = self.ruta_cache / f"{clave}.cache"
                with open(archivo, 'wb') as f:
                    pickle.dump(valor, f)
                
                # Convertir metadata a dict para JSON
                metadata_dict = {
                    "clave": metadata.clave,
                    "tamano_bytes": metadata.tamano_bytes,
                    "tipo_dato": metadata.tipo_dato.value,
                    "timestamp_creacion": metadata.timestamp_creacion.isoformat(),
                    "timestamp_acceso": metadata.timestamp_acceso.isoformat(),
                    "frecuencia_acceso": metadata.frecuencia_acceso,
                    "nivel_cache": metadata.nivel_cache.value,
                    "comprimido": metadata.comprimido,
                    "checksum": metadata.checksum,
                    "tiempo_computacion": metadata.tiempo_computacion,
                    "prioridad": metadata.prioridad
                }
                
                self.metadatos[clave] = metadata_dict
                self._guardar_metadatos()
                
            except Exception as e:
                self.logger.log(NivelSeveridad.ERROR, f"Error guardando L2 {clave}: {e}")
    
    def _limpiar_espacio(self, bytes_necesarios: int):
        """Limpiar espacio necesario"""
        tamano_actual = self._calcular_tamano_actual()
        
        while tamano_actual + bytes_necesarios > self.capacidad_bytes and self.metadatos:
            # Encontrar más antiguo
            mas_antiguo = min(self.metadatos.keys(), 
                             key=lambda k: self.metadatos[k]["timestamp_acceso"])
            self._eliminar_archivo(mas_antiguo)
            tamano_actual = self._calcular_tamano_actual()
    
    def _eliminar_archivo(self, clave: str):
        """Eliminar archivo de cache"""
        try:
            archivo = self.ruta_cache / f"{clave}.cache"
            if archivo.exists():
                archivo.unlink()
            if clave in self.metadatos:
                del self.metadatos[clave]
        except Exception as e:
            self.logger.log(NivelSeveridad.ERROR, f"Error eliminando {clave}: {e}")
    
    def _calcular_tamano_actual(self) -> int:
        """Calcular tamaño actual"""
        tamano = 0
        for archivo in self.ruta_cache.glob("*.cache"):
            try:
                tamano += archivo.stat().st_size
            except:
                pass
        return tamano
    
    def get_info(self) -> Dict[str, Any]:
        """Información del cache L2"""
        tamano = self._calcular_tamano_actual()
        return {
            "nivel": "L2_disco",
            "elementos": len(self.metadatos),
            "tamano_mb": tamano / (1024 * 1024),
            "utilizacion_percent": (tamano / self.capacidad_bytes) * 100
        }


class MonitorMemoria:
    """Monitor predictivo de memoria"""
    
    def __init__(self):
        self.umbral_critico = 90.0
        self.umbral_alto = 75.0
    
    def obtener_uso_memoria(self) -> float:
        """Uso actual de memoria"""
        try:
            return psutil.virtual_memory().percent
        except:
            return 0.0
    
    def predecir_necesidad_limpieza(self) -> bool:
        """Predecir necesidad de limpieza"""
        return self.obtener_uso_memoria() >= self.umbral_alto


class CacheMultinivel:
    """Sistema principal de cache multinivel LRU ultra-robusto"""
    
    def __init__(self, ruta_base: Path, config_cache: Dict[str, Any] = None):
        self.ruta_base = ruta_base
        self.ruta_cache = ruta_base / "cache_multinivel"
        self.logger = obtener_sistema_logging().obtener_sistema_logger()
        
        self.config = config_cache or {
            "l1_capacidad_mb": 512,
            "l2_capacidad_mb": 2048,
            "habilitar_compresion": True,
            "auto_limpieza": True
        }
        
        # Componentes del sistema
        self.cache_l1 = CacheL1Memoria(self.config["l1_capacidad_mb"])
        self.cache_l2 = CacheL2Disco(self.ruta_cache, self.config["l2_capacidad_mb"])
        self.compresor = CompresorInteligente()
        self.monitor_memoria = MonitorMemoria()
        
        # Estadísticas
        self.estadisticas = EstadisticasCache()
        
        # Monitor automático
        self.activo = True
        self.thread_monitor = threading.Thread(target=self._monitor_continuo, daemon=True)
        self.thread_monitor.start()
        
        self.logger.log(NivelSeveridad.INFO, "Cache multinivel inicializado")
    
    def put(self, clave: str, valor: Any, tipo_dato: TipoDato, 
           tiempo_computacion: float = 0.0, prioridad: int = 5) -> bool:
        """Almacenar en cache multinivel"""
        try:
            datos_serializados = pickle.dumps(valor)
            tamano_original = len(datos_serializados)
            checksum = hashlib.sha256(datos_serializados).hexdigest()
            
            metadata = MetadataCache(
                clave=clave,
                tamano_bytes=tamano_original,
                tipo_dato=tipo_dato,
                timestamp_creacion=datetime.now(),
                timestamp_acceso=datetime.now(),
                frecuencia_acceso=1,
                nivel_cache=NivelCache.L1_MEMORIA,
                comprimido=False,
                checksum=checksum,
                tiempo_computacion=tiempo_computacion,
                prioridad=prioridad
            )
            
            # L1 para objetos pequeños
            if tamano_original <= self.cache_l1.capacidad_bytes * 0.1:
                self.cache_l1.put(clave, valor, metadata)
                self.estadisticas.bytes_almacenados += tamano_original
                return True
            
            # L2 con compresión opcional
            valor_a_guardar = valor
            if self.config["habilitar_compresion"]:
                datos_comprimidos, _ = self.compresor.comprimir(datos_serializados, tipo_dato)
                metadata.comprimido = True
                metadata.tamano_bytes = len(datos_comprimidos)
                valor_a_guardar = datos_comprimidos
            
            metadata.nivel_cache = NivelCache.L2_DISCO
            self.cache_l2.put(clave, valor_a_guardar, metadata)
            self.estadisticas.bytes_almacenados += metadata.tamano_bytes
            
            return True
            
        except Exception as e:
            self.logger.log(NivelSeveridad.ERROR, f"Error almacenando {clave}: {e}")
            return False
    
    def get(self, clave: str) -> Optional[Any]:
        """Obtener del cache multinivel"""
        inicio = time.time()
        
        try:
            # Buscar en L1
            resultado_l1 = self.cache_l1.get(clave)
            if resultado_l1:
                self.estadisticas.hits_l1 += 1
                self._actualizar_tiempo_promedio(time.time() - inicio)
                return resultado_l1[0]
            
            # Buscar en L2
            resultado_l2 = self.cache_l2.get(clave)
            if resultado_l2:
                valor, metadata = resultado_l2
                self.estadisticas.hits_l2 += 1
                
                # Descomprimir si es necesario
                if metadata.comprimido and isinstance(valor, bytes):
                    datos_descomprimidos = self.compresor.descomprimir(valor)
                    valor = pickle.loads(datos_descomprimidos)
                
                # Promover a L1 si es pequeño y frecuente
                if (metadata.tamano_bytes <= self.cache_l1.capacidad_bytes * 0.05 and 
                    metadata.frecuencia_acceso >= 3):
                    self.cache_l1.put(clave, valor, metadata)
                
                self._actualizar_tiempo_promedio(time.time() - inicio)
                return valor
            
            # Cache miss
            self.estadisticas.misses += 1
            return None
            
        except Exception as e:
            self.logger.log(NivelSeveridad.ERROR, f"Error obteniendo {clave}: {e}")
            self.estadisticas.misses += 1
            return None
    
    def _actualizar_tiempo_promedio(self, tiempo_acceso: float):
        """Actualizar tiempo promedio"""
        total = self.estadisticas.total_hits + self.estadisticas.misses
        if total > 0:
            self.estadisticas.tiempo_promedio_acceso = (
                (self.estadisticas.tiempo_promedio_acceso * (total - 1) + tiempo_acceso) / total
            )
    
    def _monitor_continuo(self):
        """Monitor continuo del cache"""
        while self.activo:
            try:
                if (self.config["auto_limpieza"] and 
                    self.monitor_memoria.predecir_necesidad_limpieza()):
                    self._limpieza_automatica()
                
                # Actualizar estadísticas de memoria
                proceso = psutil.Process()
                self.estadisticas.memoria_utilizada_mb = proceso.memory_info().rss / (1024 * 1024)
                
                time.sleep(30)
                
            except Exception as e:
                self.logger.log(NivelSeveridad.ERROR, f"Error en monitor: {e}")
                time.sleep(30)
    
    def _limpieza_automatica(self):
        """Limpieza automática inteligente"""
        try:
            # Limpiar 25% del L1
            elementos_a_limpiar = len(self.cache_l1.datos) // 4
            for _ in range(elementos_a_limpiar):
                if self.cache_l1.datos:
                    self.cache_l1._evict_lru()
                    self.estadisticas.evictions += 1
            
            gc.collect()
            self.logger.log(NivelSeveridad.INFO, f"Limpieza automática: {elementos_a_limpiar} elementos")
            
        except Exception as e:
            self.logger.log(NivelSeveridad.ERROR, f"Error en limpieza: {e}")
    
    def obtener_estadisticas(self) -> EstadisticasCache:
        """Estadísticas del cache"""
        return self.estadisticas
    
    def obtener_info_detallada(self) -> Dict[str, Any]:
        """Información detallada"""
        return {
            "estadisticas": asdict(self.estadisticas),
            "cache_l1": self.cache_l1.get_info(),
            "cache_l2": self.cache_l2.get_info(),
            "memoria_sistema": self.monitor_memoria.obtener_uso_memoria(),
            "configuracion": self.config
        }
    
    def limpiar_todo(self):
        """Limpiar todo el cache"""
        self.cache_l1.clear()
        
        with self.cache_l2.lock:
            for archivo in self.cache_l2.ruta_cache.glob("*.cache"):
                archivo.unlink()
            self.cache_l2.metadatos.clear()
            self.cache_l2._guardar_metadatos()
        
        self.estadisticas = EstadisticasCache()
    
    def cerrar(self):
        """Cerrar sistema de cache"""
        self.activo = False
        if self.thread_monitor.is_alive():
            self.thread_monitor.join(timeout=5)


# Instancia global
CACHE_MULTINIVEL_GLOBAL = None

def obtener_cache_multinivel(ruta_base: Path = None) -> CacheMultinivel:
    """Obtener instancia global del cache"""
    global CACHE_MULTINIVEL_GLOBAL
    if CACHE_MULTINIVEL_GLOBAL is None:
        ruta = ruta_base or Path("./cache_sistema")
        CACHE_MULTINIVEL_GLOBAL = CacheMultinivel(ruta)
    return CACHE_MULTINIVEL_GLOBAL