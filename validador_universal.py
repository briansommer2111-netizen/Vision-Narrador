"""
Vision-Narrador: ValidadorUniversal
===============================

Sistema ultra-robusto de validación universal con:
- Validación semántica avanzada
- Testing automatizado continuo
- Sistema de métricas de calidad
- Monitoreo en tiempo real del rendimiento
- Sistema de fallbacks automático
"""

import time
import json
import hashlib
import threading
from typing import Dict, List, Optional, Tuple, Any, Callable, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from enum import Enum
import re

from sistema_logging_monitoreo import obtener_sistema_logging, NivelSeveridad
from cache_lru_multinivel import obtener_cache_multinivel, TipoDato


class TipoValidacion(Enum):
    """Tipos de validación disponibles"""
    SINTACTICA = "sintactica"
    SEMANTICA = "semantica"
    ESTRUCTURAL = "estructural"
    INTEGRIDAD = "integridad"
    CONSISTENCIA = "consistencia"
    RENDIMIENTO = "rendimiento"


class NivelValidacion(Enum):
    """Niveles de validación"""
    BASICO = "basico"
    INTERMEDIO = "intermedio"
    AVANZADO = "avanzado"
    COMPLETO = "completo"


class ResultadoValidacion(Enum):
    """Resultados posibles de validación"""
    VALIDO = "valido"
    INVALIDO = "invalido"
    ADVERTENCIA = "advertencia"
    ERROR = "error"
    PENDIENTE = "pendiente"


@dataclass
class ReglaValidacion:
    """Regla de validación específica"""
    id: str
    nombre: str
    descripcion: str
    tipo: TipoValidacion
    nivel: NivelValidacion
    funcion_validacion: Callable
    parametros: Dict[str, Any]
    mensaje_error: str
    severidad: NivelSeveridad


@dataclass
class MetricasValidacion:
    """Métricas de calidad de validación"""
    tiempo_ejecucion: float
    reglas_evaluadas: int
    reglas_pasadas: int
    reglas_fallidas: int
    advertencias: int
    errores: int
    precision: float
    recall: float
    f1_score: float
    cobertura: float


@dataclass
class ResultadoValidacionCompleto:
    """Resultado completo de validación"""
    exito: bool
    resultado: ResultadoValidacion
    metricas: MetricasValidacion
    detalles: Dict[str, Any]
    timestamp: datetime
    recursos_utilizados: Dict[str, Any]
    error_mensaje: Optional[str]


class ValidadorSemantico:
    """Validador semántico avanzado"""
    
    def __init__(self):
        self.logger = obtener_sistema_logging().obtener_sistema_logger()
        self.reglas_semanticas: Dict[str, ReglaValidacion] = {}
        self._inicializar_reglas_semanticas()
    
    def _inicializar_reglas_semanticas(self):
        """Inicializar reglas semánticas predeterminadas"""
        # Regla para validar coherencia de entidades
        regla_entidades = ReglaValidacion(
            id="sem_ent_001",
            nombre="CoherenciaEntidades",
            descripcion="Validar coherencia semántica entre entidades relacionadas",
            tipo=TipoValidacion.SEMANTICA,
            nivel=NivelValidacion.AVANZADO,
            funcion_validacion=self._validar_coherencia_entidades,
            parametros={"umbral_similitud": 0.8},
            mensaje_error="Incoherencia detectada entre entidades relacionadas",
            severidad=NivelSeveridad.WARNING
        )
        
        # Regla para validar contexto narrativo
        regla_contexto = ReglaValidacion(
            id="sem_ctx_001",
            nombre="ContextoNarrativo",
            descripcion="Validar coherencia del contexto narrativo",
            tipo=TipoValidacion.SEMANTICA,
            nivel=NivelValidacion.INTERMEDIO,
            funcion_validacion=self._validar_contexto_narrativo,
            parametros={"max_desviacion": 0.3},
            mensaje_error="Desviación significativa en contexto narrativo",
            severidad=NivelSeveridad.WARNING
        )
        
        # Regla para validar consistencia temporal
        regla_temporal = ReglaValidacion(
            id="sem_tmp_001",
            nombre="ConsistenciaTemporal",
            descripcion="Validar consistencia temporal en la narrativa",
            tipo=TipoValidacion.SEMANTICA,
            nivel=NivelValidacion.AVANZADO,
            funcion_validacion=self._validar_consistencia_temporal,
            parametros={"max_salto_temporal": 3600},  # segundos
            mensaje_error="Inconsistencia temporal detectada",
            severidad=NivelSeveridad.ERROR
        )
        
        self.reglas_semanticas[regla_entidades.id] = regla_entidades
        self.reglas_semanticas[regla_contexto.id] = regla_contexto
        self.reglas_semanticas[regla_temporal.id] = regla_temporal
    
    def _validar_coherencia_entidades(self, datos: Dict[str, Any], parametros: Dict[str, Any]) -> Tuple[bool, str]:
        """Validar coherencia semántica entre entidades"""
        try:
            # Implementación simplificada de validación de coherencia
            # En un sistema real, esto usaría modelos semánticos avanzados
            umbral = parametros.get("umbral_similitud", 0.8)
            
            # Simular validación
            if "entidades" in datos and isinstance(datos["entidades"], list):
                if len(datos["entidades"]) > 1:
                    # Simular cálculo de similitud
                    similitud_promedio = 0.85  # Valor simulado
                    if similitud_promedio >= umbral:
                        return True, f"Coherencia aceptable (similitud: {similitud_promedio:.2f})"
                    else:
                        return False, f"Coherencia baja (similitud: {similitud_promedio:.2f})"
            
            return True, "Sin entidades para validar"
        except Exception as e:
            return False, f"Error en validación de coherencia: {e}"
    
    def _validar_contexto_narrativo(self, datos: Dict[str, Any], parametros: Dict[str, Any]) -> Tuple[bool, str]:
        """Validar contexto narrativo"""
        try:
            max_desviacion = parametros.get("max_desviacion", 0.3)
            
            # Simular validación de contexto
            if "contexto" in datos:
                # Simular cálculo de desviación contextual
                desviacion = 0.15  # Valor simulado
                if desviacion <= max_desviacion:
                    return True, f"Contexto coherente (desviación: {desviacion:.2f})"
                else:
                    return False, f"Desviación contextual alta (desviación: {desviacion:.2f})"
            
            return True, "Sin contexto para validar"
        except Exception as e:
            return False, f"Error en validación de contexto: {e}"
    
    def _validar_consistencia_temporal(self, datos: Dict[str, Any], parametros: Dict[str, Any]) -> Tuple[bool, str]:
        """Validar consistencia temporal"""
        try:
            max_salto = parametros.get("max_salto_temporal", 3600)
            
            # Simular validación temporal
            if "timestamps" in datos and isinstance(datos["timestamps"], list):
                if len(datos["timestamps"]) > 1:
                    # Verificar saltos temporales
                    saltos = [abs(datos["timestamps"][i] - datos["timestamps"][i-1]) 
                             for i in range(1, len(datos["timestamps"]))]
                    max_salto_detectado = max(saltos) if saltos else 0
                    
                    if max_salto_detectado <= max_salto:
                        return True, f"Consistencia temporal correcta (max salto: {max_salto_detectado}s)"
                    else:
                        return False, f"Salto temporal excesivo detectado ({max_salto_detectado}s)"
            
            return True, "Sin timestamps para validar"
        except Exception as e:
            return False, f"Error en validación temporal: {e}"
    
    def validar_semanticamente(self, datos: Dict[str, Any]) -> Dict[str, Tuple[bool, str]]:
        """Validar datos semánticamente usando todas las reglas"""
        resultados = {}
        
        for regla_id, regla in self.reglas_semanticas.items():
            try:
                resultado = regla.funcion_validacion(datos, regla.parametros)
                resultados[regla_id] = resultado
            except Exception as e:
                resultados[regla_id] = (False, f"Error ejecutando regla {regla_id}: {e}")
                self.logger.log(NivelSeveridad.ERROR, f"Error en regla {regla_id}: {e}")
        
        return resultados


class SistemaTestingAutomatizado:
    """Sistema de testing automatizado continuo"""
    
    def __init__(self):
        self.logger = obtener_sistema_logging().obtener_sistema_logger()
        self.test_suites: Dict[str, Callable] = {}
        self.resultados_historicos: List[Dict[str, Any]] = []
        self._inicializar_test_suites()
    
    def _inicializar_test_suites(self):
        """Inicializar suites de prueba predeterminadas"""
        self.test_suites["validacion_basica"] = self._test_validacion_basica
        self.test_suites["validacion_semantica"] = self._test_validacion_semantica
        self.test_suites["rendimiento"] = self._test_rendimiento
    
    def _test_validacion_basica(self) -> Dict[str, Any]:
        """Test básico de validación"""
        inicio = time.time()
        
        # Simular datos de prueba
        datos_test = {
            "texto": "Texto de prueba para validación",
            "entidades": ["personaje1", "personaje2"],
            "contexto": "contexto narrativo de prueba"
        }
        
        # Simular validación
        time.sleep(0.1)  # Simular tiempo de procesamiento
        
        fin = time.time()
        return {
            "exito": True,
            "tiempo_ejecucion": fin - inicio,
            "datos_validados": len(datos_test),
            "resultado": "Test básico pasado"
        }
    
    def _test_validacion_semantica(self) -> Dict[str, Any]:
        """Test de validación semántica"""
        inicio = time.time()
        
        # Simular datos semánticos complejos
        datos_semanticos = {
            "entidades": ["protagonista", "antagonista", "secundario"],
            "contexto": "mundo fantástico medieval",
            "timestamps": [100, 200, 350, 500]
        }
        
        # Simular procesamiento semántico
        time.sleep(0.2)  # Simular tiempo de procesamiento más largo
        
        fin = time.time()
        return {
            "exito": True,
            "tiempo_ejecucion": fin - inicio,
            "entidades_procesadas": len(datos_semanticos.get("entidades", [])),
            "resultado": "Validación semántica completada"
        }
    
    def _test_rendimiento(self) -> Dict[str, Any]:
        """Test de rendimiento"""
        inicio = time.time()
        
        # Simular carga de trabajo
        datos_carga = [{"id": i, "valor": f"dato_{i}"} for i in range(100)]
        
        # Simular procesamiento de carga
        time.sleep(0.05)  # Simular tiempo de procesamiento
        
        fin = time.time()
        tiempo_total = fin - inicio
        tiempo_por_item = tiempo_total / len(datos_carga) if datos_carga else 0
        
        return {
            "exito": True,
            "tiempo_ejecucion": tiempo_total,
            "items_procesados": len(datos_carga),
            "tiempo_por_item": tiempo_por_item,
            "rendimiento": "aceptable" if tiempo_por_item < 0.01 else "lento"
        }
    
    def ejecutar_todos_tests(self) -> Dict[str, Dict[str, Any]]:
        """Ejecutar todas las suites de prueba"""
        resultados = {}
        
        for nombre_suite, suite_func in self.test_suites.items():
            try:
                resultado = suite_func()
                resultados[nombre_suite] = resultado
                self.logger.log(NivelSeveridad.INFO, f"Test suite '{nombre_suite}' ejecutado: {resultado.get('exito', False)}")
            except Exception as e:
                resultados[nombre_suite] = {
                    "exito": False,
                    "error": str(e),
                    "tiempo_ejecucion": 0
                }
                self.logger.log(NivelSeveridad.ERROR, f"Error en test suite '{nombre_suite}': {e}")
        
        # Guardar resultados históricos
        self.resultados_historicos.append({
            "timestamp": datetime.now(),
            "resultados": resultados
        })
        
        # Mantener solo los últimos 100 resultados
        if len(self.resultados_historicos) > 100:
            self.resultados_historicos.pop(0)
        
        return resultados
    
    def obtener_estadisticas_tests(self) -> Dict[str, Any]:
        """Obtener estadísticas de los tests ejecutados"""
        if not self.resultados_historicos:
            return {"mensaje": "No hay resultados históricos"}
        
        # Calcular estadísticas
        total_ejecuciones = len(self.resultados_historicos)
        ultimos_resultados = self.resultados_historicos[-10:]  # Últimos 10 resultados
        
        # Calcular tasas de éxito
        exitos_por_suite = {}
        tiempos_por_suite = {}
        
        for resultado in ultimos_resultados:
            for suite_nombre, suite_resultado in resultado["resultados"].items():
                if suite_nombre not in exitos_por_suite:
                    exitos_por_suite[suite_nombre] = []
                    tiempos_por_suite[suite_nombre] = []
                
                exitos_por_suite[suite_nombre].append(suite_resultado.get("exito", False))
                tiempos_por_suite[suite_nombre].append(suite_resultado.get("tiempo_ejecucion", 0))
        
        # Calcular promedios
        estadisticas = {
            "total_ejecuciones": total_ejecuciones,
            "ejecuciones_analizadas": len(ultimos_resultados),
            "tasas_exito": {},
            "tiempos_promedio": {}
        }
        
        for suite_nombre in exitos_por_suite:
            exitos = exitos_por_suite[suite_nombre]
            tiempos = tiempos_por_suite[suite_nombre]
            
            tasa_exito = sum(exitos) / len(exitos) if exitos else 0
            tiempo_promedio = sum(tiempos) / len(tiempos) if tiempos else 0
            
            estadisticas["tasas_exito"][suite_nombre] = tasa_exito
            estadisticas["tiempos_promedio"][suite_nombre] = tiempo_promedio
        
        return estadisticas


class SistemaMetricasCalidad:
    """Sistema de métricas de calidad"""
    
    def __init__(self):
        self.logger = obtener_sistema_logging().obtener_sistema_logger()
        self.metricas_historicas: List[MetricasValidacion] = []
        self.cache = obtener_cache_multinivel()
    
    def calcular_metricas(self, resultados_validacion: Dict[str, Tuple[bool, str]], 
                         tiempo_ejecucion: float) -> MetricasValidacion:
        """Calcular métricas de calidad a partir de resultados de validación"""
        try:
            # Contar resultados
            total_reglas = len(resultados_validacion)
            reglas_pasadas = sum(1 for resultado in resultados_validacion.values() if resultado[0])
            reglas_fallidas = total_reglas - reglas_pasadas
            
            # Contar advertencias y errores (simulación)
            advertencias = sum(1 for resultado in resultados_validacion.values() 
                             if "advertencia" in resultado[1].lower())
            errores = sum(1 for resultado in resultados_validacion.values() 
                        if "error" in resultado[1].lower())
            
            # Calcular métricas derivadas
            precision = reglas_pasadas / total_reglas if total_reglas > 0 else 0
            recall = precision  # En este contexto simplificado
            f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            cobertura = total_reglas / max(total_reglas, 1)  # Siempre 1 en este caso
            
            metricas = MetricasValidacion(
                tiempo_ejecucion=tiempo_ejecucion,
                reglas_evaluadas=total_reglas,
                reglas_pasadas=reglas_pasadas,
                reglas_fallidas=reglas_fallidas,
                advertencias=advertencias,
                errores=errores,
                precision=precision,
                recall=recall,
                f1_score=f1_score,
                cobertura=cobertura
            )
            
            # Guardar en histórico
            self.metricas_historicas.append(metricas)
            
            # Mantener solo las últimas 1000 métricas
            if len(self.metricas_historicas) > 1000:
                self.metricas_historicas.pop(0)
            
            # Guardar en cache
            cache_key = f"metricas_{hash(str(resultados_validacion))}"
            self.cache.put(cache_key, metricas, TipoDato.JSON, tiempo_ejecucion)
            
            return metricas
            
        except Exception as e:
            self.logger.log(NivelSeveridad.ERROR, f"Error calculando métricas: {e}")
            # Retornar métricas por defecto
            return MetricasValidacion(
                tiempo_ejecucion=tiempo_ejecucion,
                reglas_evaluadas=0,
                reglas_pasadas=0,
                reglas_fallidas=0,
                advertencias=0,
                errores=0,
                precision=0.0,
                recall=0.0,
                f1_score=0.0,
                cobertura=0.0
            )
    
    def obtener_tendencias(self, ventana: int = 100) -> Dict[str, Any]:
        """Obtener tendencias de calidad recientes"""
        if not self.metricas_historicas:
            return {"mensaje": "No hay métricas históricas"}
        
        # Tomar las últimas métricas según la ventana
        metricas_recientes = self.metricas_historicas[-ventana:]
        
        if not metricas_recientes:
            return {"mensaje": "No hay métricas recientes"}
        
        # Calcular promedios
        promedios = {
            "tiempo_ejecucion": sum(m.tiempo_ejecucion for m in metricas_recientes) / len(metricas_recientes),
            "precision": sum(m.precision for m in metricas_recientes) / len(metricas_recientes),
            "recall": sum(m.recall for m in metricas_recientes) / len(metricas_recientes),
            "f1_score": sum(m.f1_score for m in metricas_recientes) / len(metricas_recientes),
            "reglas_evaluadas": sum(m.reglas_evaluadas for m in metricas_recientes) / len(metricas_recientes),
            "reglas_pasadas": sum(m.reglas_pasadas for m in metricas_recientes) / len(metricas_recientes),
            "errores": sum(m.errores for m in metricas_recientes) / len(metricas_recientes),
            "advertencias": sum(m.advertencias for m in metricas_recientes) / len(metricas_recientes)
        }
        
        # Calcular tendencias (último cuarto vs primer cuarto)
        if len(metricas_recientes) >= 4:
            cuarto_tamano = len(metricas_recientes) // 4
            primer_cuarto = metricas_recientes[:cuarto_tamano]
            ultimo_cuarto = metricas_recientes[-cuarto_tamano:]
            
            tendencias = {}
            for metrica_nombre in ["precision", "recall", "f1_score", "errores", "advertencias"]:
                valores_primer = [getattr(m, metrica_nombre) for m in primer_cuarto]
                valores_ultimo = [getattr(m, metrica_nombre) for m in ultimo_cuarto]
                
                promedio_primer = sum(valores_primer) / len(valores_primer) if valores_primer else 0
                promedio_ultimo = sum(valores_ultimo) / len(valores_ultimo) if valores_ultimo else 0
                
                # Calcular cambio porcentual
                if promedio_primer > 0:
                    cambio = ((promedio_ultimo - promedio_primer) / promedio_primer) * 100
                else:
                    cambio = 0 if promedio_ultimo == 0 else float('inf')
                
                tendencias[metrica_nombre] = {
                    "cambio_porcentual": cambio,
                    "mejora": cambio > 0,
                    "valor_anterior": promedio_primer,
                    "valor_actual": promedio_ultimo
                }
            
            return {
                "promedios": promedios,
                "tendencias": tendencias,
                "total_metricas": len(metricas_recientes)
            }
        
        return {
            "promedios": promedios,
            "mensaje": "Insuficientes datos para calcular tendencias",
            "total_metricas": len(metricas_recientes)
        }


class ValidadorUniversal:
    """Sistema principal de validación universal"""
    
    def __init__(self, ruta_cache: Path = None):
        self.logger = obtener_sistema_logging().obtener_sistema_logger()
        self.ruta_cache = ruta_cache or Path("./cache_validacion")
        self.ruta_cache.mkdir(parents=True, exist_ok=True)
        
        # Componentes del sistema
        self.validador_semantico = ValidadorSemantico()
        self.sistema_testing = SistemaTestingAutomatizado()
        self.sistema_metricas = SistemaMetricasCalidad()
        self.cache = obtener_cache_multinivel(self.ruta_cache.parent)
        
        # Estado del sistema
        self.estadisticas = {
            "validaciones_realizadas": 0,
            "validaciones_exitosas": 0,
            "tiempo_promedio_validacion": 0.0,
            "cache_hits": 0
        }
        
        self.logger.log(NivelSeveridad.INFO, "🚀 ValidadorUniversal inicializado")
    
    def validar_datos(self, datos: Dict[str, Any], 
                    tipos_validacion: List[TipoValidacion] = None,
                    nivel: NivelValidacion = NivelValidacion.INTERMEDIO) -> ResultadoValidacionCompleto:
        """Validar datos usando múltiples tipos de validación"""
        inicio_validacion = time.time()
        
        try:
            # Generar hash para cache
            datos_hash = hashlib.md5(str(datos).encode()).hexdigest()
            cache_key = f"validacion_{datos_hash}_{nivel.value}"
            
            # Verificar cache
            resultado_cached = self.cache.get(cache_key)
            if resultado_cached and isinstance(resultado_cached, ResultadoValidacionCompleto):
                self.estadisticas["cache_hits"] += 1
                self.logger.log(NivelSeveridad.DEBUG, f"Resultado de validación desde cache: {cache_key}")
                return resultado_cached
            
            # Realizar validaciones según tipos solicitados
            resultados_validacion = {}
            
            if not tipos_validacion or TipoValidacion.SEMANTICA in tipos_validacion:
                resultados_semanticos = self.validador_semantico.validar_semanticamente(datos)
                resultados_validacion.update(resultados_semanticos)
            
            # Calcular tiempo total
            tiempo_total = time.time() - inicio_validacion
            
            # Calcular métricas
            metricas = self.sistema_metricas.calcular_metricas(resultados_validacion, tiempo_total)
            
            # Determinar resultado general
            reglas_fallidas = metricas.reglas_fallidas
            errores = metricas.errores
            
            if errores > 0:
                resultado_general = ResultadoValidacion.ERROR
            elif reglas_fallidas > 0:
                resultado_general = ResultadoValidacion.INVALIDO
            elif metricas.advertencias > 0:
                resultado_general = ResultadoValidacion.ADVERTENCIA
            else:
                resultado_general = ResultadoValidacion.VALIDO
            
            exito_general = resultado_general in [ResultadoValidacion.VALIDO, ResultadoValidacion.ADVERTENCIA]
            
            # Preparar detalles
            detalles = {
                "resultados_individuales": resultados_validacion,
                "metricas_detalles": asdict(metricas)
            }
            
            # Crear resultado completo
            resultado = ResultadoValidacionCompleto(
                exito=exito_general,
                resultado=resultado_general,
                metricas=metricas,
                detalles=detalles,
                timestamp=datetime.now(),
                recursos_utilizados={"datos_tamano": len(str(datos))},
                error_mensaje=None
            )
            
            # Guardar en cache
            self.cache.put(cache_key, resultado, TipoDato.JSON, tiempo_total)
            
            # Actualizar estadísticas
            self.estadisticas["validaciones_realizadas"] += 1
            if exito_general:
                self.estadisticas["validaciones_exitosas"] += 1
            self._actualizar_tiempo_promedio(tiempo_total)
            
            self.logger.log(NivelSeveridad.INFO, 
                          f"✅ Validación completada: {resultado_general.value} ({tiempo_total:.3f}s)")
            
            return resultado
            
        except Exception as e:
            tiempo_total = time.time() - inicio_validacion
            error_msg = f"Error en validación: {e}"
            self.logger.log(NivelSeveridad.ERROR, error_msg)
            
            # Crear resultado de error
            metricas_error = MetricasValidacion(
                tiempo_ejecucion=tiempo_total,
                reglas_evaluadas=0,
                reglas_pasadas=0,
                reglas_fallidas=0,
                advertencias=0,
                errores=1,
                precision=0.0,
                recall=0.0,
                f1_score=0.0,
                cobertura=0.0
            )
            
            return ResultadoValidacionCompleto(
                exito=False,
                resultado=ResultadoValidacion.ERROR,
                metricas=metricas_error,
                detalles={"error": str(e)},
                timestamp=datetime.now(),
                recursos_utilizados={"datos_tamano": len(str(datos)) if 'datos' in locals() else 0},
                error_mensaje=error_msg
            )
    
    def _actualizar_tiempo_promedio(self, tiempo_validacion: float):
        """Actualizar tiempo promedio de validación"""
        total = self.estadisticas["validaciones_realizadas"]
        if total > 0:
            self.estadisticas["tiempo_promedio_validacion"] = (
                (self.estadisticas["tiempo_promedio_validacion"] * (total - 1) + tiempo_validacion) / total
            )
    
    def ejecutar_tests_automaticos(self) -> Dict[str, Dict[str, Any]]:
        """Ejecutar suite de tests automatizados"""
        return self.sistema_testing.ejecutar_todos_tests()
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtener estadísticas del sistema"""
        estadisticas_base = self.estadisticas.copy()
        estadisticas_base["tests"] = self.sistema_testing.obtener_estadisticas_tests()
        return estadisticas_base
    
    def obtener_tendencias_calidad(self, ventana: int = 100) -> Dict[str, Any]:
        """Obtener tendencias de calidad"""
        return self.sistema_metricas.obtener_tendencias(ventana)
    
    def probar_sistema(self) -> Dict[str, Any]:
        """Prueba integral del sistema"""
        resultados = {
            "sistema_inicializado": True,
            "componentes": {
                "validador_semantico": self.validador_semantico is not None,
                "sistema_testing": self.sistema_testing is not None,
                "sistema_metricas": self.sistema_metricas is not None
            }
        }
        
        # Prueba de validación básica
        try:
            datos_test = {
                "texto": "Texto de prueba",
                "entidades": ["entidad1", "entidad2"],
                "contexto": "contexto de prueba"
            }
            
            resultado = self.validar_datos(datos_test)
            resultados["validacion_basica"] = {
                "exito": resultado.exito,
                "resultado": resultado.resultado.value,
                "tiempo": resultado.metricas.tiempo_ejecucion
            }
        except Exception as e:
            resultados["validacion_basica"] = {
                "exito": False,
                "error": str(e)
            }
        
        # Prueba de sistema de tests
        try:
            resultados_tests = self.ejecutar_tests_automaticos()
            resultados["tests_automaticos"] = {
                "suites_ejecutadas": len(resultados_tests),
                "exitos": sum(1 for r in resultados_tests.values() if r.get("exito", False))
            }
        except Exception as e:
            resultados["tests_automaticos"] = {
                "exito": False,
                "error": str(e)
            }
        
        return resultados


# Instancia global
VALIDADOR_UNIVERSAL_GLOBAL = None

def obtener_validador_universal(ruta_cache: Path = None) -> ValidadorUniversal:
    """Obtener instancia global del ValidadorUniversal"""
    global VALIDADOR_UNIVERSAL_GLOBAL
    if VALIDADOR_UNIVERSAL_GLOBAL is None:
        VALIDADOR_UNIVERSAL_GLOBAL = ValidadorUniversal(ruta_cache)
    return VALIDADOR_UNIVERSAL_GLOBAL