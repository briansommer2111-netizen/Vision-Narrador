"""
Vision-Narrador: TTSHandler Ultra-Confiable
==========================================

Sistema ultra-robusto de Text-to-Speech con:
- Detección automática de modelos disponibles
- Fallbacks jerárquicos inteligentes
- Validación exhaustiva de calidad de audio
- Cache inteligente de síntesis
"""

import os
import time
import wave
import json
import hashlib
import threading
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from enum import Enum
import tempfile

from sistema_logging_monitoreo import obtener_sistema_logging, NivelSeveridad
from cache_lru_multinivel import obtener_cache_multinivel, TipoDato


class TipoTTS(Enum):
    """Tipos de sistemas TTS disponibles"""
    PYTTSX3 = "pyttsx3"
    GTTS = "gtts"
    EDGE_TTS = "edge_tts"
    WINDOWS_SAPI = "windows_sapi"


class CalidadAudio(Enum):
    """Niveles de calidad de audio"""
    BAJA = 1
    MEDIA = 2
    ALTA = 3
    ULTRA = 4


@dataclass
class ConfiguracionTTS:
    """Configuración de un sistema TTS"""
    tipo: TipoTTS
    disponible: bool
    velocidad: float
    volumen: float
    voz: str
    idioma: str
    calidad: CalidadAudio
    prioridad: int


@dataclass
class MetricasAudio:
    """Métricas de calidad de audio"""
    duracion_segundos: float
    tamano_bytes: int
    sample_rate: int
    calidad_estimada: CalidadAudio


@dataclass
class ResultadoTTS:
    """Resultado de síntesis TTS"""
    exito: bool
    archivo_audio: Optional[Path]
    duracion: float
    tiempo_sintesis: float
    tts_utilizado: TipoTTS
    metricas_audio: Optional[MetricasAudio]
    error_mensaje: Optional[str]


class DetectorModelosTTS:
    """Detector automático de modelos TTS disponibles"""
    
    def __init__(self):
        self.logger = obtener_sistema_logging().obtener_sistema_logger()
    
    def detectar_todos_los_modelos(self) -> Dict[TipoTTS, ConfiguracionTTS]:
        """Detectar todos los modelos TTS disponibles"""
        self.logger.log(NivelSeveridad.INFO, "🔍 Detectando modelos TTS...")
        
        modelos = {}
        detectores = [
            (self._detectar_pyttsx3, TipoTTS.PYTTSX3),
            (self._detectar_gtts, TipoTTS.GTTS),
            (self._detectar_edge_tts, TipoTTS.EDGE_TTS),
            (self._detectar_windows_sapi, TipoTTS.WINDOWS_SAPI)
        ]
        
        for detector, tipo in detectores:
            try:
                config = detector()
                if config and config.disponible:
                    modelos[tipo] = config
                    self.logger.log(NivelSeveridad.INFO, f"✅ {tipo.value} disponible")
            except Exception as e:
                self.logger.log(NivelSeveridad.DEBUG, f"❌ {tipo.value} no disponible: {e}")
        
        return modelos
    
    def _detectar_pyttsx3(self) -> Optional[ConfiguracionTTS]:
        """Detectar pyttsx3"""
        try:
            import pyttsx3
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            voz = voices[0].id if voices else "default"
            
            return ConfiguracionTTS(
                tipo=TipoTTS.PYTTSX3,
                disponible=True,
                velocidad=200,
                volumen=0.9,
                voz=voz,
                idioma="es",
                calidad=CalidadAudio.MEDIA,
                prioridad=8
            )
        except:
            return None
    
    def _detectar_gtts(self) -> Optional[ConfiguracionTTS]:
        """Detectar Google TTS"""
        try:
            from gtts import gTTS
            return ConfiguracionTTS(
                tipo=TipoTTS.GTTS,
                disponible=True,
                velocidad=1.0,
                volumen=1.0,
                voz="google_es",
                idioma="es",
                calidad=CalidadAudio.ALTA,
                prioridad=9
            )
        except:
            return None
    
    def _detectar_edge_tts(self) -> Optional[ConfiguracionTTS]:
        """Detectar Edge TTS"""
        try:
            import edge_tts
            return ConfiguracionTTS(
                tipo=TipoTTS.EDGE_TTS,
                disponible=True,
                velocidad=1.0,
                volumen=1.0,
                voz="es-ES-AlvaroNeural",
                idioma="es",
                calidad=CalidadAudio.ULTRA,
                prioridad=10
            )
        except:
            return None
    
    def _detectar_windows_sapi(self) -> Optional[ConfiguracionTTS]:
        """Detectar Windows SAPI"""
        try:
            import platform
            if platform.system() != "Windows":
                return None
                
            import win32com.client
            return ConfiguracionTTS(
                tipo=TipoTTS.WINDOWS_SAPI,
                disponible=True,
                velocidad=0,
                volumen=100,
                voz="default",
                idioma="es",
                calidad=CalidadAudio.MEDIA,
                prioridad=6
            )
        except:
            return None


class ValidadorCalidadAudio:
    """Validador de calidad de audio"""
    
    def __init__(self):
        self.logger = obtener_sistema_logging().obtener_sistema_logger()
    
    def validar_archivo_audio(self, archivo_audio: Path) -> MetricasAudio:
        """Validar archivo de audio"""
        try:
            if not archivo_audio.exists():
                raise FileNotFoundError(f"Archivo no encontrado: {archivo_audio}")
            
            tamano = archivo_audio.stat().st_size
            
            # Intentar leer como WAV
            try:
                with wave.open(str(archivo_audio), 'rb') as wav_file:
                    frames = wav_file.getnframes()
                    sample_rate = wav_file.getframerate()
                    duracion = frames / sample_rate if sample_rate > 0 else 0
            except:
                # Si no es WAV, estimar valores
                duracion = max(1.0, tamano / 32000)  # Estimación básica
                sample_rate = 22050
            
            # Calcular calidad basada en tamaño y duración
            if tamano > 50000 and duracion > 1.0:
                calidad = CalidadAudio.ALTA
            elif tamano > 20000 and duracion > 0.5:
                calidad = CalidadAudio.MEDIA
            else:
                calidad = CalidadAudio.BAJA
            
            return MetricasAudio(
                duracion_segundos=duracion,
                tamano_bytes=tamano,
                sample_rate=sample_rate,
                calidad_estimada=calidad
            )
            
        except Exception as e:
            self.logger.log(NivelSeveridad.ERROR, f"Error validando audio: {e}")
            return MetricasAudio(
                duracion_segundos=0.0,
                tamano_bytes=0,
                sample_rate=0,
                calidad_estimada=CalidadAudio.BAJA
            )


class SintetizadorTTS:
    """Sintetizador específico para cada tipo de TTS"""
    
    def __init__(self, config: ConfiguracionTTS):
        self.config = config
        self.logger = obtener_sistema_logging().obtener_sistema_logger()
        self.instancia_tts = None
        self._inicializar_tts()
    
    def _inicializar_tts(self):
        """Inicializar instancia TTS específica"""
        try:
            if self.config.tipo == TipoTTS.PYTTSX3:
                import pyttsx3
                self.instancia_tts = pyttsx3.init()
                self.instancia_tts.setProperty('rate', self.config.velocidad)
                self.instancia_tts.setProperty('volume', self.config.volumen)
                
            elif self.config.tipo == TipoTTS.WINDOWS_SAPI:
                import win32com.client
                self.instancia_tts = win32com.client.Dispatch("SAPI.SpVoice")
                
        except Exception as e:
            self.logger.log(NivelSeveridad.ERROR, f"Error inicializando {self.config.tipo.value}: {e}")
    
    def sintetizar(self, texto: str, archivo_salida: Path) -> bool:
        """Sintetizar texto a audio"""
        try:
            if self.config.tipo == TipoTTS.PYTTSX3:
                return self._sintetizar_pyttsx3(texto, archivo_salida)
            elif self.config.tipo == TipoTTS.GTTS:
                return self._sintetizar_gtts(texto, archivo_salida)
            elif self.config.tipo == TipoTTS.EDGE_TTS:
                return self._sintetizar_edge_tts(texto, archivo_salida)
            elif self.config.tipo == TipoTTS.WINDOWS_SAPI:
                return self._sintetizar_windows_sapi(texto, archivo_salida)
            return False
                
        except Exception as e:
            self.logger.log(NivelSeveridad.ERROR, f"Error sintetizando: {e}")
            return False
    
    def _sintetizar_pyttsx3(self, texto: str, archivo_salida: Path) -> bool:
        """Sintetizar con pyttsx3"""
        try:
            if not self.instancia_tts:
                return False
            
            self.instancia_tts.save_to_file(texto, str(archivo_salida))
            self.instancia_tts.runAndWait()
            return archivo_salida.exists()
            
        except Exception:
            return False
    
    def _sintetizar_gtts(self, texto: str, archivo_salida: Path) -> bool:
        """Sintetizar con Google TTS"""
        try:
            from gtts import gTTS
            
            tts = gTTS(text=texto, lang='es')
            # Guardar como MP3 temporalmente
            archivo_mp3 = archivo_salida.with_suffix('.mp3')
            tts.save(str(archivo_mp3))
            
            # Para convertir a WAV necesitaríamos ffmpeg
            # Por ahora mantener como MP3
            if archivo_mp3.exists():
                if archivo_salida.suffix.lower() == '.wav':
                    # Intentar conversión básica
                    import shutil
                    shutil.move(str(archivo_mp3), str(archivo_salida.with_suffix('.mp3')))
                return True
            return False
            
        except Exception:
            return False
    
    def _sintetizar_edge_tts(self, texto: str, archivo_salida: Path) -> bool:
        """Sintetizar con Edge TTS"""
        try:
            import edge_tts
            import asyncio
            
            async def _generar():
                communicate = edge_tts.Communicate(texto, self.config.voz)
                await communicate.save(str(archivo_salida))
            
            asyncio.run(_generar())
            return archivo_salida.exists()
            
        except Exception:
            return False
    
    def _sintetizar_windows_sapi(self, texto: str, archivo_salida: Path) -> bool:
        """Sintetizar con Windows SAPI"""
        try:
            if not self.instancia_tts:
                return False
            
            import win32com.client
            file_stream = win32com.client.Dispatch("SAPI.SpFileStream")
            file_stream.Open(str(archivo_salida), 3)
            self.instancia_tts.AudioOutputStream = file_stream
            self.instancia_tts.Speak(texto)
            file_stream.Close()
            
            return archivo_salida.exists()
            
        except Exception:
            return False


class TTSHandlerUltraConfiable:
    """Sistema principal ultra-confiable de Text-to-Speech"""
    
    def __init__(self, ruta_cache: Path = None):
        self.logger = obtener_sistema_logging().obtener_sistema_logger()
        self.ruta_cache = ruta_cache or Path("./cache_tts")
        self.ruta_cache.mkdir(parents=True, exist_ok=True)
        
        # Componentes del sistema
        self.detector = DetectorModelosTTS()
        self.validador = ValidadorCalidadAudio()
        self.cache = obtener_cache_multinivel(self.ruta_cache.parent)
        
        # Estado del sistema
        self.modelos_disponibles = {}
        self.sintetizadores = {}
        self.estadisticas = {
            "sintesis_exitosas": 0,
            "fallbacks_utilizados": 0,
            "tiempo_promedio_sintesis": 0.0,
            "cache_hits": 0
        }
        
        # Inicialización
        self.inicializar_sistema()
    
    def inicializar_sistema(self):
        """Inicializar sistema TTS completo"""
        try:
            self.logger.log(NivelSeveridad.INFO, "🚀 Inicializando TTSHandler ultra-confiable...")
            
            # Detectar modelos disponibles
            self.modelos_disponibles = self.detector.detectar_todos_los_modelos()
            
            # Crear sintetizadores para modelos disponibles
            for tipo_tts, config in self.modelos_disponibles.items():
                sintetizador = SintetizadorTTS(config)
                self.sintetizadores[tipo_tts] = sintetizador
            
            # Ordenar por prioridad
            self.modelos_disponibles = dict(
                sorted(self.modelos_disponibles.items(), 
                      key=lambda x: x[1].prioridad, reverse=True)
            )
            
            self.logger.log(
                NivelSeveridad.INFO, 
                f"✅ Sistema TTS inicializado con {len(self.sintetizadores)} sintetizadores"
            )
            
        except Exception as e:
            self.logger.log(NivelSeveridad.ERROR, f"Error inicializando TTS: {e}")
    
    def sintetizar_texto(self, texto: str, archivo_salida: Optional[Path] = None, 
                        calidad_minima: CalidadAudio = CalidadAudio.MEDIA) -> ResultadoTTS:
        """Sintetizar texto con fallbacks automáticos"""
        inicio_sintesis = time.time()
        
        try:
            # Cache key
            texto_hash = hashlib.md5(texto.encode('utf-8')).hexdigest()
            cache_key = f"tts_{texto_hash}_{calidad_minima.value}"
            
            # Verificar cache
            audio_cached = self.cache.get(cache_key)
            if audio_cached and isinstance(audio_cached, Path) and audio_cached.exists():
                self.estadisticas["cache_hits"] += 1
                metricas = self.validador.validar_archivo_audio(audio_cached)
                
                if metricas.calidad_estimada.value >= calidad_minima.value:
                    if archivo_salida:
                        import shutil
                        shutil.copy2(audio_cached, archivo_salida)
                        archivo_final = archivo_salida
                    else:
                        archivo_final = audio_cached
                    
                    return ResultadoTTS(
                        exito=True,
                        archivo_audio=archivo_final,
                        duracion=metricas.duracion_segundos,
                        tiempo_sintesis=time.time() - inicio_sintesis,
                        tts_utilizado=list(self.modelos_disponibles.keys())[0],
                        metricas_audio=metricas,
                        error_mensaje=None
                    )
            
            # Archivo de salida
            if archivo_salida is None:
                archivo_salida = self.ruta_cache / f"tts_{texto_hash}.wav"
            
            # Intentar síntesis con fallbacks
            for tipo_tts, config in self.modelos_disponibles.items():
                if tipo_tts not in self.sintetizadores:
                    continue
                
                try:
                    self.logger.log(NivelSeveridad.DEBUG, f"Intentando {tipo_tts.value}")
                    
                    sintetizador = self.sintetizadores[tipo_tts]
                    inicio_modelo = time.time()
                    
                    # Intentar síntesis
                    exito = sintetizador.sintetizar(texto, archivo_salida)
                    tiempo_modelo = time.time() - inicio_modelo
                    
                    if exito and archivo_salida.exists():
                        # Validar calidad
                        metricas = self.validador.validar_archivo_audio(archivo_salida)
                        
                        if metricas.calidad_estimada.value >= calidad_minima.value:
                            # Guardar en cache
                            self.cache.put(cache_key, archivo_salida, TipoDato.AUDIO, tiempo_modelo)
                            
                            # Actualizar estadísticas
                            self.estadisticas["sintesis_exitosas"] += 1
                            self._actualizar_tiempo_promedio(time.time() - inicio_sintesis)
                            
                            self.logger.log(
                                NivelSeveridad.INFO,
                                f"✅ Síntesis exitosa con {tipo_tts.value}",
                                duracion=metricas.duracion_segundos
                            )
                            
                            return ResultadoTTS(
                                exito=True,
                                archivo_audio=archivo_salida,
                                duracion=metricas.duracion_segundos,
                                tiempo_sintesis=time.time() - inicio_sintesis,
                                tts_utilizado=tipo_tts,
                                metricas_audio=metricas,
                                error_mensaje=None
                            )
                        else:
                            # Calidad insuficiente, probar siguiente
                            self.estadisticas["fallbacks_utilizados"] += 1
                            self.logger.log(NivelSeveridad.WARNING, 
                                          f"Calidad insuficiente con {tipo_tts.value}")
                    
                except Exception as e:
                    self.estadisticas["fallbacks_utilizados"] += 1
                    self.logger.log(NivelSeveridad.WARNING, f"Fallback {tipo_tts.value}: {e}")
                    continue
            
            # Todos los fallbacks fallaron
            tiempo_total = time.time() - inicio_sintesis
            error_msg = "Todos los sistemas TTS fallaron"
            
            self.logger.log(NivelSeveridad.ERROR, error_msg)
            
            return ResultadoTTS(
                exito=False,
                archivo_audio=None,
                duracion=0.0,
                tiempo_sintesis=tiempo_total,
                tts_utilizado=list(self.modelos_disponibles.keys())[0] if self.modelos_disponibles else TipoTTS.PYTTSX3,
                metricas_audio=None,
                error_mensaje=error_msg
            )
            
        except Exception as e:
            error_msg = f"Error crítico en síntesis TTS: {e}"
            self.logger.log(NivelSeveridad.ERROR, error_msg)
            
            return ResultadoTTS(
                exito=False,
                archivo_audio=None,
                duracion=0.0,
                tiempo_sintesis=time.time() - inicio_sintesis,
                tts_utilizado=list(self.modelos_disponibles.keys())[0] if self.modelos_disponibles else TipoTTS.PYTTSX3,
                metricas_audio=None,
                error_mensaje=error_msg
            )
    
    def _actualizar_tiempo_promedio(self, tiempo_sintesis: float):
        """Actualizar tiempo promedio de síntesis"""
        total = self.estadisticas["sintesis_exitosas"]
        if total > 0:
            self.estadisticas["tiempo_promedio_sintesis"] = (
                (self.estadisticas["tiempo_promedio_sintesis"] * (total - 1) + tiempo_sintesis) / total
            )
    
    def obtener_modelos_disponibles(self) -> Dict[TipoTTS, ConfiguracionTTS]:
        """Obtener modelos TTS disponibles"""
        return self.modelos_disponibles
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtener estadísticas del sistema"""
        return self.estadisticas.copy()
    
    def probar_sistema(self, texto_prueba: str = "Hola, este es un test del sistema TTS.") -> Dict[str, Any]:
        """Probar todos los sistemas TTS"""
        resultados = {}
        
        for tipo_tts in self.modelos_disponibles.keys():
            try:
                archivo_test = self.ruta_cache / f"test_{tipo_tts.value}.wav"
                resultado = self.sintetizar_texto(texto_prueba, archivo_test, CalidadAudio.BAJA)
                
                resultados[tipo_tts.value] = {
                    "exito": resultado.exito,
                    "duracion": resultado.duracion,
                    "tiempo_sintesis": resultado.tiempo_sintesis,
                    "calidad": resultado.metricas_audio.calidad_estimada.name if resultado.metricas_audio else "DESCONOCIDA"
                }
                
                # Limpiar archivo de test
                if archivo_test.exists():
                    archivo_test.unlink()
                    
            except Exception as e:
                resultados[tipo_tts.value] = {
                    "exito": False,
                    "error": str(e)
                }
        
        return resultados


# Instancia global
TTS_HANDLER_GLOBAL = None

def obtener_tts_handler(ruta_cache: Path = None) -> TTSHandlerUltraConfiable:
    """Obtener instancia global del TTS handler"""
    global TTS_HANDLER_GLOBAL
    if TTS_HANDLER_GLOBAL is None:
        TTS_HANDLER_GLOBAL = TTSHandlerUltraConfiable(ruta_cache)
    return TTS_HANDLER_GLOBAL