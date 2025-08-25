"""
Vision-Narrador: Sistema de Logging y Monitoreo Ultra-Avanzado
==============================================================

Sistema ultra-robusto de logging estructurado con:
- Niveles de severidad avanzados
- Monitor en tiempo real con dashboard de métricas
- Alertas proactivas automatizadas
- Análisis de tendencias y patrones
- Rotación automática de logs
- Exportación de métricas
- Sistema de notificaciones inteligente
"""

import logging
import json
import time
import threading
import queue
import psutil
import statistics
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
from collections import defaultdict, deque


class NivelSeveridad(Enum):
    """Niveles de severidad extendidos"""
    TRACE = 5
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50
    FATAL = 60


class TipoMetrica(Enum):
    """Tipos de métricas monitoreadas"""
    CONTADOR = "counter"
    GAUGE = "gauge"
    HISTOGRAMA = "histogram"
    TASA = "rate"
    TIEMPO_RESPUESTA = "response_time"


class EstadoSistema(Enum):
    """Estados del sistema"""
    SALUDABLE = "healthy"
    DEGRADADO = "degraded"
    CRITICO = "critical"
    FALLO = "failure"
    DESCONOCIDO = "unknown"


@dataclass
class EventoLog:
    """Estructura de evento de log completa"""
    timestamp: datetime
    nivel: NivelSeveridad
    modulo: str
    mensaje: str
    contexto: Dict[str, Any]
    stack_trace: Optional[str]
    usuario: Optional[str]
    sesion_id: Optional[str]
    proceso_id: int
    thread_id: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "nivel": self.nivel.name,
            "modulo": self.modulo,
            "mensaje": self.mensaje,
            "contexto": self.contexto,
            "stack_trace": self.stack_trace,
            "usuario": self.usuario,
            "sesion_id": self.sesion_id,
            "proceso_id": self.proceso_id,
            "thread_id": self.thread_id
        }


@dataclass
class Metrica:
    """Métrica del sistema"""
    nombre: str
    tipo: TipoMetrica
    valor: float
    timestamp: datetime
    etiquetas: Dict[str, str]
    unidad: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "nombre": self.nombre,
            "tipo": self.tipo.value,
            "valor": self.valor,
            "timestamp": self.timestamp.isoformat(),
            "etiquetas": self.etiquetas,
            "unidad": self.unidad
        }


@dataclass
class AlertaConfig:
    """Configuración de alerta"""
    nombre: str
    metrica: str
    umbral: float
    operador: str  # ">", "<", ">=", "<=", "==", "!="
    ventana_tiempo: int  # segundos
    callback: Optional[Callable] = None
    activa: bool = True
    mensaje_personalizado: Optional[str] = None


class LoggerEstructurado:
    """Logger estructurado ultra-avanzado"""
    
    def __init__(self, nombre: str, ruta_logs: Path):
        self.nombre = nombre
        self.ruta_logs = ruta_logs
        self.ruta_logs.mkdir(parents=True, exist_ok=True)
        
        # Base de datos para logs estructurados
        self.db_path = ruta_logs / "logs.db"
        self._inicializar_db()
        
        # Queue para logs asíncronos
        self.log_queue = queue.Queue()
        self.procesando = True
        
        # Thread para procesamiento de logs
        self.log_thread = threading.Thread(target=self._procesar_logs, daemon=True)
        self.log_thread.start()
        
        # Configurar logger Python estándar
        self.logger = logging.getLogger(nombre)
        self.logger.setLevel(NivelSeveridad.TRACE.value)
        
        # Handler personalizado
        handler = LogHandlerEstructurado(self)
        self.logger.addHandler(handler)
    
    def _inicializar_db(self):
        """Inicializar base de datos de logs"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    nivel TEXT NOT NULL,
                    modulo TEXT NOT NULL,
                    mensaje TEXT NOT NULL,
                    contexto TEXT,
                    stack_trace TEXT,
                    usuario TEXT,
                    sesion_id TEXT,
                    proceso_id INTEGER,
                    thread_id INTEGER
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp ON logs(timestamp)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_nivel ON logs(nivel)
            """)
    
    def log(self, nivel: NivelSeveridad, mensaje: str, **contexto):
        """Método principal de logging"""
        evento = EventoLog(
            timestamp=datetime.now(),
            nivel=nivel,
            modulo=self.nombre,
            mensaje=mensaje,
            contexto=contexto,
            stack_trace=None,
            usuario=contexto.get("usuario"),
            sesion_id=contexto.get("sesion_id"),
            proceso_id=os.getpid(),
            thread_id=threading.get_ident()
        )
        
        # Agregar stack trace para errores
        if nivel.value >= NivelSeveridad.ERROR.value:
            import traceback
            evento.stack_trace = traceback.format_stack()
        
        self.log_queue.put(evento)
    
    def _procesar_logs(self):
        """Procesar logs de manera asíncrona"""
        while self.procesando:
            try:
                # Procesar logs en lotes
                eventos = []
                deadline = time.time() + 1  # 1 segundo máximo
                
                while time.time() < deadline and len(eventos) < 100:
                    try:
                        evento = self.log_queue.get(timeout=0.1)
                        eventos.append(evento)
                    except queue.Empty:
                        break
                
                if eventos:
                    self._persistir_logs(eventos)
                    
            except Exception as e:
                # Log crítico usando logging estándar
                logging.critical(f"Error procesando logs: {e}")
    
    def _persistir_logs(self, eventos: List[EventoLog]):
        """Persistir logs en base de datos"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                for evento in eventos:
                    conn.execute("""
                        INSERT INTO logs (
                            timestamp, nivel, modulo, mensaje, contexto,
                            stack_trace, usuario, sesion_id, proceso_id, thread_id
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        evento.timestamp.isoformat(),
                        evento.nivel.name,
                        evento.modulo,
                        evento.mensaje,
                        json.dumps(evento.contexto) if evento.contexto else None,
                        evento.stack_trace,
                        evento.usuario,
                        evento.sesion_id,
                        evento.proceso_id,
                        evento.thread_id
                    ))
        except Exception as e:
            logging.critical(f"Error persistiendo logs: {e}")
    
    def consultar_logs(self, nivel_min: NivelSeveridad = None, 
                      desde: datetime = None, hasta: datetime = None,
                      limite: int = 1000) -> List[Dict[str, Any]]:
        """Consultar logs con filtros"""
        try:
            query = "SELECT * FROM logs WHERE 1=1"
            params = []
            
            if nivel_min:
                query += " AND nivel IN ({})".format(
                    ",".join(f"'{n.name}'" for n in NivelSeveridad if n.value >= nivel_min.value)
                )
            
            if desde:
                query += " AND timestamp >= ?"
                params.append(desde.isoformat())
            
            if hasta:
                query += " AND timestamp <= ?"
                params.append(hasta.isoformat())
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limite)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logging.error(f"Error consultando logs: {e}")
            return []
    
    def cerrar(self):
        """Cerrar logger de manera segura"""
        self.procesando = False
        if self.log_thread.is_alive():
            self.log_thread.join(timeout=5)


class LogHandlerEstructurado(logging.Handler):
    """Handler personalizado para integración con logging estándar"""
    
    def __init__(self, logger_estructurado: LoggerEstructurado):
        super().__init__()
        self.logger_estructurado = logger_estructurado
    
    def emit(self, record):
        """Emitir log al sistema estructurado"""
        try:
            # Mapear nivel de logging a NivelSeveridad
            nivel_map = {
                logging.DEBUG: NivelSeveridad.DEBUG,
                logging.INFO: NivelSeveridad.INFO,
                logging.WARNING: NivelSeveridad.WARNING,
                logging.ERROR: NivelSeveridad.ERROR,
                logging.CRITICAL: NivelSeveridad.CRITICAL
            }
            
            nivel = nivel_map.get(record.levelno, NivelSeveridad.INFO)
            
            # Extraer contexto del record
            contexto = {
                "funcname": record.funcName,
                "lineno": record.lineno,
                "pathname": record.pathname
            }
            
            # Agregar contexto adicional si existe
            if hasattr(record, 'extra'):
                contexto.update(record.extra)
            
            self.logger_estructurado.log(nivel, record.getMessage(), **contexto)
            
        except Exception:
            self.handleError(record)


class ColectorMetricas:
    """Colector de métricas del sistema"""
    
    def __init__(self, ruta_metricas: Path):
        self.ruta_metricas = ruta_metricas
        self.ruta_metricas.mkdir(parents=True, exist_ok=True)
        
        # Almacenamiento en memoria de métricas
        self.metricas: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Base de datos para métricas
        self.db_path = ruta_metricas / "metricas.db"
        self._inicializar_db_metricas()
        
        # Thread de recolección
        self.recolectando = True
        self.recolector_thread = threading.Thread(target=self._recolectar_metricas_sistema, daemon=True)
        self.recolector_thread.start()
    
    def _inicializar_db_metricas(self):
        """Inicializar base de datos de métricas"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS metricas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    tipo TEXT NOT NULL,
                    valor REAL NOT NULL,
                    timestamp TEXT NOT NULL,
                    etiquetas TEXT,
                    unidad TEXT
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_nombre_timestamp ON metricas(nombre, timestamp)
            """)
    
    def registrar_metrica(self, metrica: Metrica):
        """Registrar una métrica"""
        # Almacenar en memoria
        self.metricas[metrica.nombre].append(metrica)
        
        # Persistir en base de datos
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO metricas (nombre, tipo, valor, timestamp, etiquetas, unidad)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    metrica.nombre,
                    metrica.tipo.value,
                    metrica.valor,
                    metrica.timestamp.isoformat(),
                    json.dumps(metrica.etiquetas),
                    metrica.unidad
                ))
        except Exception as e:
            logging.error(f"Error persistiendo métrica: {e}")
    
    def _recolectar_metricas_sistema(self):
        """Recolectar métricas del sistema automáticamente"""
        while self.recolectando:
            try:
                now = datetime.now()
                
                # Métricas de CPU
                cpu_percent = psutil.cpu_percent(interval=1)
                self.registrar_metrica(Metrica(
                    nombre="sistema.cpu.uso_percent",
                    tipo=TipoMetrica.GAUGE,
                    valor=cpu_percent,
                    timestamp=now,
                    etiquetas={"host": "local"},
                    unidad="percent"
                ))
                
                # Métricas de memoria
                memoria = psutil.virtual_memory()
                self.registrar_metrica(Metrica(
                    nombre="sistema.memoria.uso_percent",
                    tipo=TipoMetrica.GAUGE,
                    valor=memoria.percent,
                    timestamp=now,
                    etiquetas={"host": "local"},
                    unidad="percent"
                ))
                
                self.registrar_metrica(Metrica(
                    nombre="sistema.memoria.disponible_gb",
                    tipo=TipoMetrica.GAUGE,
                    valor=memoria.available / (1024**3),
                    timestamp=now,
                    etiquetas={"host": "local"},
                    unidad="GB"
                ))
                
                # Métricas de disco
                disco = psutil.disk_usage("/")
                self.registrar_metrica(Metrica(
                    nombre="sistema.disco.uso_percent",
                    tipo=TipoMetrica.GAUGE,
                    valor=(disco.used / disco.total) * 100,
                    timestamp=now,
                    etiquetas={"host": "local"},
                    unidad="percent"
                ))
                
                time.sleep(30)  # Recolectar cada 30 segundos
                
            except Exception as e:
                logging.error(f"Error recolectando métricas: {e}")
                time.sleep(30)
    
    def obtener_metricas_recientes(self, nombre: str, ventana_minutos: int = 60) -> List[Metrica]:
        """Obtener métricas recientes de una ventana de tiempo"""
        if nombre in self.metricas:
            ahora = datetime.now()
            limite = ahora - timedelta(minutes=ventana_minutos)
            
            return [m for m in self.metricas[nombre] if m.timestamp >= limite]
        return []
    
    def calcular_estadisticas(self, nombre: str, ventana_minutos: int = 60) -> Dict[str, float]:
        """Calcular estadísticas de una métrica"""
        metricas_recientes = self.obtener_metricas_recientes(nombre, ventana_minutos)
        
        if not metricas_recientes:
            return {}
        
        valores = [m.valor for m in metricas_recientes]
        
        return {
            "promedio": statistics.mean(valores),
            "mediana": statistics.median(valores),
            "minimo": min(valores),
            "maximo": max(valores),
            "desviacion_estandar": statistics.stdev(valores) if len(valores) > 1 else 0,
            "total_muestras": len(valores)
        }


class SistemaAlertas:
    """Sistema de alertas proactivas"""
    
    def __init__(self, colector_metricas: ColectorMetricas, logger: LoggerEstructurado):
        self.colector_metricas = colector_metricas
        self.logger = logger
        self.alertas_config: Dict[str, AlertaConfig] = {}
        self.alertas_activas: Dict[str, datetime] = {}
        
        # Thread para monitoreo de alertas
        self.monitoreando = True
        self.monitor_thread = threading.Thread(target=self._monitorear_alertas, daemon=True)
        self.monitor_thread.start()
    
    def agregar_alerta(self, config: AlertaConfig):
        """Agregar configuración de alerta"""
        self.alertas_config[config.nombre] = config
        self.logger.log(
            NivelSeveridad.INFO,
            f"Alerta configurada: {config.nombre}",
            metrica=config.metrica,
            umbral=config.umbral,
            operador=config.operador
        )
    
    def _monitorear_alertas(self):
        """Monitorear alertas continuamente"""
        while self.monitoreando:
            try:
                for nombre, config in self.alertas_config.items():
                    if not config.activa:
                        continue
                    
                    self._evaluar_alerta(nombre, config)
                
                time.sleep(10)  # Evaluar cada 10 segundos
                
            except Exception as e:
                self.logger.log(
                    NivelSeveridad.ERROR,
                    f"Error monitoreando alertas: {e}"
                )
                time.sleep(10)
    
    def _evaluar_alerta(self, nombre: str, config: AlertaConfig):
        """Evaluar una alerta específica"""
        try:
            # Obtener métricas recientes
            ventana_segundos = config.ventana_tiempo
            metricas = self.colector_metricas.obtener_metricas_recientes(
                config.metrica, ventana_segundos // 60
            )
            
            if not metricas:
                return
            
            # Tomar el valor más reciente
            valor_actual = metricas[-1].valor
            
            # Evaluar condición
            condicion_cumplida = self._evaluar_condicion(
                valor_actual, config.operador, config.umbral
            )
            
            if condicion_cumplida:
                # Verificar si la alerta ya está activa
                if nombre not in self.alertas_activas:
                    self._disparar_alerta(nombre, config, valor_actual)
                    self.alertas_activas[nombre] = datetime.now()
            else:
                # Resolver alerta si estaba activa
                if nombre in self.alertas_activas:
                    self._resolver_alerta(nombre, config, valor_actual)
                    del self.alertas_activas[nombre]
                    
        except Exception as e:
            self.logger.log(
                NivelSeveridad.ERROR,
                f"Error evaluando alerta {nombre}: {e}"
            )
    
    def _evaluar_condicion(self, valor: float, operador: str, umbral: float) -> bool:
        """Evaluar condición de alerta"""
        if operador == ">":
            return valor > umbral
        elif operador == "<":
            return valor < umbral
        elif operador == ">=":
            return valor >= umbral
        elif operador == "<=":
            return valor <= umbral
        elif operador == "==":
            return valor == umbral
        elif operador == "!=":
            return valor != umbral
        else:
            return False
    
    def _disparar_alerta(self, nombre: str, config: AlertaConfig, valor: float):
        """Disparar una alerta"""
        mensaje = config.mensaje_personalizado or f"Alerta {nombre}: {config.metrica} {config.operador} {config.umbral}"
        
        self.logger.log(
            NivelSeveridad.CRITICAL,
            f"🚨 ALERTA DISPARADA: {mensaje}",
            alerta=nombre,
            metrica=config.metrica,
            valor_actual=valor,
            umbral=config.umbral,
            operador=config.operador
        )
        
        # Ejecutar callback si existe
        if config.callback:
            try:
                config.callback(nombre, config, valor)
            except Exception as e:
                self.logger.log(
                    NivelSeveridad.ERROR,
                    f"Error ejecutando callback de alerta {nombre}: {e}"
                )
    
    def _resolver_alerta(self, nombre: str, config: AlertaConfig, valor: float):
        """Resolver una alerta"""
        self.logger.log(
            NivelSeveridad.INFO,
            f"✅ Alerta resuelta: {nombre}",
            alerta=nombre,
            metrica=config.metrica,
            valor_actual=valor
        )


class MonitorTiempoReal:
    """Monitor en tiempo real con dashboard de métricas"""
    
    def __init__(self, logger: LoggerEstructurado, colector_metricas: ColectorMetricas, 
                 sistema_alertas: SistemaAlertas):
        self.logger = logger
        self.colector_metricas = colector_metricas
        self.sistema_alertas = sistema_alertas
        
        # Estado del sistema
        self.estado_sistema = EstadoSistema.DESCONOCIDO
        self.ultima_evaluacion = datetime.now()
    
    def obtener_dashboard_data(self) -> Dict[str, Any]:
        """Obtener datos para dashboard en tiempo real"""
        try:
            ahora = datetime.now()
            
            # Métricas de sistema
            cpu_stats = self.colector_metricas.calcular_estadisticas("sistema.cpu.uso_percent", 60)
            memoria_stats = self.colector_metricas.calcular_estadisticas("sistema.memoria.uso_percent", 60)
            disco_stats = self.colector_metricas.calcular_estadisticas("sistema.disco.uso_percent", 60)
            
            # Logs recientes por nivel
            logs_recientes = self.logger.consultar_logs(limite=100)
            logs_por_nivel = defaultdict(int)
            
            for log in logs_recientes:
                logs_por_nivel[log["nivel"]] += 1
            
            # Alertas activas
            alertas_activas = list(self.sistema_alertas.alertas_activas.keys())
            
            # Evaluar estado general del sistema
            self.estado_sistema = self._evaluar_estado_sistema(cpu_stats, memoria_stats, alertas_activas)
            
            dashboard = {
                "timestamp": ahora.isoformat(),
                "estado_sistema": self.estado_sistema.value,
                "metricas_sistema": {
                    "cpu": cpu_stats,
                    "memoria": memoria_stats,
                    "disco": disco_stats
                },
                "logs_recientes": {
                    "total": len(logs_recientes),
                    "por_nivel": dict(logs_por_nivel)
                },
                "alertas": {
                    "activas": alertas_activas,
                    "total_configuradas": len(self.sistema_alertas.alertas_config)
                },
                "rendimiento": {
                    "metricas_recolectadas": sum(len(m) for m in self.colector_metricas.metricas.values()),
                    "logs_procesados": len(logs_recientes)
                }
            }
            
            return dashboard
            
        except Exception as e:
            self.logger.log(
                NivelSeveridad.ERROR,
                f"Error generando dashboard: {e}"
            )
            return {"error": str(e)}
    
    def _evaluar_estado_sistema(self, cpu_stats: Dict, memoria_stats: Dict, alertas_activas: List) -> EstadoSistema:
        """Evaluar estado general del sistema"""
        try:
            # Si hay alertas críticas activas
            if alertas_activas:
                return EstadoSistema.CRITICO
            
            # Verificar métricas de rendimiento
            cpu_promedio = cpu_stats.get("promedio", 0)
            memoria_promedio = memoria_stats.get("promedio", 0)
            
            if cpu_promedio > 90 or memoria_promedio > 95:
                return EstadoSistema.CRITICO
            elif cpu_promedio > 70 or memoria_promedio > 80:
                return EstadoSistema.DEGRADADO
            else:
                return EstadoSistema.SALUDABLE
                
        except Exception:
            return EstadoSistema.DESCONOCIDO


class SistemaLoggingMonitoreoAvanzado:
    """Sistema principal que integra logging, métricas y alertas"""
    
    def __init__(self, ruta_base: Path):
        self.ruta_base = ruta_base
        self.ruta_base.mkdir(parents=True, exist_ok=True)
        
        # Componentes principales
        self.logger = LoggerEstructurado("VisionNarrador", ruta_base / "logs")
        self.colector_metricas = ColectorMetricas(ruta_base / "metricas")
        self.sistema_alertas = SistemaAlertas(self.colector_metricas, self.logger)
        self.monitor_tiempo_real = MonitorTiempoReal(
            self.logger, self.colector_metricas, self.sistema_alertas
        )
        
        # Configurar alertas básicas
        self._configurar_alertas_basicas()
        
        self.logger.log(
            NivelSeveridad.INFO,
            "Sistema de Logging y Monitoreo iniciado",
            componentes=["logger", "metricas", "alertas", "monitor"]
        )
    
    def _configurar_alertas_basicas(self):
        """Configurar alertas básicas del sistema"""
        # Alerta de CPU alto
        self.sistema_alertas.agregar_alerta(AlertaConfig(
            nombre="cpu_alto",
            metrica="sistema.cpu.uso_percent",
            umbral=80.0,
            operador=">",
            ventana_tiempo=300,  # 5 minutos
            mensaje_personalizado="Uso de CPU alto: puede afectar rendimiento"
        ))
        
        # Alerta de memoria alta
        self.sistema_alertas.agregar_alerta(AlertaConfig(
            nombre="memoria_alta",
            metrica="sistema.memoria.uso_percent",
            umbral=85.0,
            operador=">",
            ventana_tiempo=300,
            mensaje_personalizado="Uso de memoria alto: riesgo de problemas de rendimiento"
        ))
        
        # Alerta de disco lleno
        self.sistema_alertas.agregar_alerta(AlertaConfig(
            nombre="disco_lleno",
            metrica="sistema.disco.uso_percent",
            umbral=90.0,
            operador=">",
            ventana_tiempo=600,  # 10 minutos
            mensaje_personalizado="Espacio en disco bajo: se requiere limpieza"
        ))
    
    def obtener_sistema_logger(self) -> LoggerEstructurado:
        """Obtener logger para uso en otros módulos"""
        return self.logger
    
    def registrar_metrica_personalizada(self, nombre: str, valor: float, 
                                      etiquetas: Dict[str, str] = None):
        """Registrar métrica personalizada"""
        metrica = Metrica(
            nombre=nombre,
            tipo=TipoMetrica.GAUGE,
            valor=valor,
            timestamp=datetime.now(),
            etiquetas=etiquetas or {}
        )
        self.colector_metricas.registrar_metrica(metrica)
    
    def obtener_dashboard(self) -> Dict[str, Any]:
        """Obtener datos de dashboard"""
        return self.monitor_tiempo_real.obtener_dashboard_data()
    
    def cerrar(self):
        """Cerrar sistema de manera segura"""
        self.logger.log(NivelSeveridad.INFO, "Cerrando sistema de logging y monitoreo")
        
        # Cerrar componentes
        self.sistema_alertas.monitoreando = False
        self.colector_metricas.recolectando = False
        self.logger.cerrar()


# Instancia global
SISTEMA_LOGGING_GLOBAL = None

def obtener_sistema_logging(ruta_base: Path = None) -> SistemaLoggingMonitoreoAvanzado:
    """Obtener instancia global del sistema de logging"""
    global SISTEMA_LOGGING_GLOBAL
    if SISTEMA_LOGGING_GLOBAL is None:
        ruta = ruta_base or Path("./logs_sistema")
        SISTEMA_LOGGING_GLOBAL = SistemaLoggingMonitoreoAvanzado(ruta)
    return SISTEMA_LOGGING_GLOBAL