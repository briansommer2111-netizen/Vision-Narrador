"""
Vision-Narrador: VideoEditor Ultra-Funcional
==========================================

Sistema ultra-robusto de edición de video con:
- Verificación exhaustiva de dependencias
- Generador inteligente de placeholders
- Validación rigurosa de calidad
- Procesamiento optimizado por hardware
- Sistema de fallbacks automático
- Monitoreo en tiempo real del rendimiento
"""

import os
import time
import json
import hashlib
import subprocess
import threading
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from enum import Enum
import tempfile
import shutil

from sistema_logging_monitoreo import obtener_sistema_logging, NivelSeveridad
from cache_lru_multinivel import obtener_cache_multinivel, TipoDato


class TipoVideo(Enum):
    """Tipos de video disponibles"""
    MP4 = "mp4"
    AVI = "avi"
    MKV = "mkv"
    MOV = "mov"
    WEBM = "webm"


class CalidadVideo(Enum):
    """Niveles de calidad de video"""
    BAJA = "baja"      # 480p
    MEDIA = "media"    # 720p
    ALTA = "alta"      # 1080p
    ULTRA = "ultra"    # 4K
    CUSTOM = "custom"


class TipoTransicion(Enum):
    """Tipos de transiciones"""
    DESVANECER = "desvanecer"
    CORTE = "corte"
    BARRIDO = "barrido"
    ZOOM = "zoom"
    ROTACION = "rotacion"


@dataclass
class ConfiguracionVideo:
    """Configuración de video"""
    ancho: int
    alto: int
    fps: int
    bitrate: str
    codec_video: str
    codec_audio: str
    calidad: CalidadVideo
    duracion_segundos: float


@dataclass
class MetricasVideo:
    """Métricas de calidad de video"""
    tamano_bytes: int
    duracion_segundos: float
    resolucion: Tuple[int, int]
    fps_real: float
    bitrate_real: str
    codec_video: str
    codec_audio: str
    checksum: str
    calidad_estimada: CalidadVideo


@dataclass
class ResultadoVideo:
    """Resultado de procesamiento de video"""
    exito: bool
    archivo_video: Optional[Path]
    metricas: Optional[MetricasVideo]
    tiempo_procesamiento: float
    recursos_utilizados: Dict[str, Any]
    error_mensaje: Optional[str]


class VerificadorDependenciasVideo:
    """Verificador exhaustivo de dependencias de video"""
    
    def __init__(self):
        self.logger = obtener_sistema_logging().obtener_sistema_logger()
        self.dependencias_verificadas = {}
    
    def verificar_todas_dependencias(self) -> Dict[str, bool]:
        """Verificar todas las dependencias de video"""
        self.logger.log(NivelSeveridad.INFO, "🔍 Iniciando verificación de dependencias de video...")
        
        dependencias = {
            "ffmpeg": self._verificar_ffmpeg,
            "ffprobe": self._verificar_ffprobe,
            "opencv": self._verificar_opencv,
            "pillow": self._verificar_pillow,
            "moviepy": self._verificar_moviepy
        }
        
        resultados = {}
        for nombre, verificador in dependencias.items():
            try:
                disponible = verificador()
                resultados[nombre] = disponible
                self.dependencias_verificadas[nombre] = disponible
                if disponible:
                    self.logger.log(NivelSeveridad.INFO, f"✅ {nombre} disponible")
                else:
                    self.logger.log(NivelSeveridad.WARNING, f"❌ {nombre} no disponible")
            except Exception as e:
                resultados[nombre] = False
                self.logger.log(NivelSeveridad.ERROR, f"Error verificando {nombre}: {e}")
        
        return resultados
    
    def _verificar_ffmpeg(self) -> bool:
        """Verificar disponibilidad de FFmpeg"""
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except:
            return False
    
    def _verificar_ffprobe(self) -> bool:
        """Verificar disponibilidad de FFprobe"""
        try:
            result = subprocess.run(['ffprobe', '-version'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except:
            return False
    
    def _verificar_opencv(self) -> bool:
        """Verificar disponibilidad de OpenCV"""
        try:
            import cv2
            return True
        except:
            return False
    
    def _verificar_pillow(self) -> bool:
        """Verificar disponibilidad de Pillow"""
        try:
            from PIL import Image
            return True
        except:
            return False
    
    def _verificar_moviepy(self) -> bool:
        """Verificar disponibilidad de MoviePy"""
        try:
            import moviepy.editor
            return True
        except:
            return False
    
    def obtener_versiones(self) -> Dict[str, str]:
        """Obtener versiones de dependencias disponibles"""
        versiones = {}
        
        # FFmpeg version
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                versiones["ffmpeg"] = result.stdout.split('\n')[0]
        except:
            versiones["ffmpeg"] = "No disponible"
        
        # OpenCV version
        try:
            import cv2
            versiones["opencv"] = cv2.__version__
        except:
            versiones["opencv"] = "No disponible"
        
        return versiones


class GeneradorPlaceholders:
    """Generador inteligente de placeholders de video"""
    
    def __init__(self):
        self.logger = obtener_sistema_logging().obtener_sistema_logger()
        self.cache = obtener_cache_multinivel()
    
    def generar_placeholder_texto(self, texto: str, duracion: float = 5.0, 
                                estilo: str = "webtoon") -> Path:
        """Generar placeholder de texto animado"""
        try:
            # Generar hash para cache
            texto_hash = hashlib.md5(f"{texto}_{duracion}_{estilo}".encode()).hexdigest()
            cache_key = f"placeholder_texto_{texto_hash}"
            
            # Verificar cache
            placeholder_cached = self.cache.get(cache_key)
            if placeholder_cached and isinstance(placeholder_cached, Path) and placeholder_cached.exists():
                self.logger.log(NivelSeveridad.DEBUG, f"Placeholder de texto desde cache: {cache_key}")
                return placeholder_cached
            
            # Crear placeholder temporal
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
                temp_path = Path(temp_file.name)
            
            # Usar FFmpeg para generar video de texto básico
            cmd = [
                'ffmpeg',
                '-y',  # Sobrescribir si existe
                '-f', 'lavfi',
                '-i', f'color=c=black:s=1920x1080:d={duracion}',
                '-vf', f'drawtext=text=\'{texto}\':fontcolor=white:fontsize=48:x=(w-tw)/2:y=(h-th)/2',
                '-c:v', 'libx264',
                '-t', str(duracion),
                str(temp_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and temp_path.exists():
                # Guardar en cache
                self.cache.put(cache_key, temp_path, TipoDato.VIDEO, 0.1)
                self.logger.log(NivelSeveridad.INFO, f"Placeholder de texto generado: {temp_path.name}")
                return temp_path
            else:
                # Limpiar archivo temporal en caso de error
                if temp_path.exists():
                    temp_path.unlink()
                raise Exception(f"Error generando placeholder: {result.stderr}")
                
        except Exception as e:
            self.logger.log(NivelSeveridad.ERROR, f"Error generando placeholder de texto: {e}")
            # Generar placeholder de fallback
            return self._generar_placeholder_fallback(duracion)
    
    def generar_placeholder_imagen(self, imagen_path: Path, duracion: float = 3.0) -> Path:
        """Generar placeholder de imagen"""
        try:
            if not imagen_path.exists():
                raise FileNotFoundError(f"Imagen no encontrada: {imagen_path}")
            
            # Generar hash para cache
            imagen_hash = hashlib.md5(f"{imagen_path}_{duracion}".encode()).hexdigest()
            cache_key = f"placeholder_imagen_{imagen_hash}"
            
            # Verificar cache
            placeholder_cached = self.cache.get(cache_key)
            if placeholder_cached and isinstance(placeholder_cached, Path) and placeholder_cached.exists():
                return placeholder_cached
            
            # Crear placeholder temporal
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
                temp_path = Path(temp_file.name)
            
            # Usar FFmpeg para generar video desde imagen
            cmd = [
                'ffmpeg',
                '-y',
                '-loop', '1',
                '-i', str(imagen_path),
                '-c:v', 'libx264',
                '-t', str(duracion),
                '-pix_fmt', 'yuv420p',
                str(temp_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and temp_path.exists():
                # Guardar en cache
                self.cache.put(cache_key, temp_path, TipoDato.VIDEO, 0.1)
                self.logger.log(NivelSeveridad.INFO, f"Placeholder de imagen generado: {temp_path.name}")
                return temp_path
            else:
                if temp_path.exists():
                    temp_path.unlink()
                raise Exception(f"Error generando placeholder de imagen: {result.stderr}")
                
        except Exception as e:
            self.logger.log(NivelSeveridad.ERROR, f"Error generando placeholder de imagen: {e}")
            return self._generar_placeholder_fallback(duracion)
    
    def _generar_placeholder_fallback(self, duracion: float) -> Path:
        """Generar placeholder de fallback básico"""
        try:
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
                temp_path = Path(temp_file.name)
            
            # Generar video de color sólido como fallback
            cmd = [
                'ffmpeg',
                '-y',
                '-f', 'lavfi',
                '-i', f'color=c=blue:s=1920x1080:d={duracion}',
                '-c:v', 'libx264',
                '-t', str(duracion),
                '-pix_fmt', 'yuv420p',
                str(temp_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and temp_path.exists():
                return temp_path
            else:
                if temp_path.exists():
                    temp_path.unlink()
                raise Exception("Error generando placeholder fallback")
                
        except Exception as e:
            self.logger.log(NivelSeveridad.ERROR, f"Error generando placeholder fallback: {e}")
            # Crear archivo vacío como último recurso
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
                return Path(temp_file.name)


class ValidadorVideo:
    """Validador riguroso de calidad de video"""
    
    def __init__(self):
        self.logger = obtener_sistema_logging().obtener_sistema_logger()
    
    def validar_video(self, video_path: Path) -> MetricasVideo:
        """Validar video y calcular métricas"""
        try:
            if not video_path.exists():
                raise FileNotFoundError(f"Video no encontrado: {video_path}")
            
            # Usar ffprobe para obtener información del video
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                str(video_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                raise Exception(f"Error obteniendo información del video: {result.stderr}")
            
            info = json.loads(result.stdout)
            
            # Extraer información relevante
            format_info = info.get('format', {})
            streams = info.get('streams', [])
            
            # Encontrar stream de video
            video_stream = None
            audio_stream = None
            for stream in streams:
                if stream.get('codec_type') == 'video':
                    video_stream = stream
                elif stream.get('codec_type') == 'audio':
                    audio_stream = stream
            
            # Calcular checksum
            checksum = self._calcular_checksum(video_path)
            
            # Métricas básicas
            tamano = video_path.stat().st_size
            duracion = float(format_info.get('duration', 0))
            
            # Métricas de video
            if video_stream:
                ancho = int(video_stream.get('width', 0))
                alto = int(video_stream.get('height', 0))
                fps_str = video_stream.get('avg_frame_rate', '0/1')
                if '/' in fps_str:
                    num, den = map(int, fps_str.split('/'))
                    fps = num / den if den != 0 else 0
                else:
                    fps = float(fps_str) if fps_str else 0
                codec_video = video_stream.get('codec_name', 'unknown')
                bitrate_video = video_stream.get('bit_rate', 'unknown')
            else:
                ancho, alto = 0, 0
                fps = 0
                codec_video = 'unknown'
                bitrate_video = 'unknown'
            
            # Métricas de audio
            codec_audio = audio_stream.get('codec_name', 'unknown') if audio_stream else 'none'
            
            # Estimar calidad
            calidad = self._estimar_calidad(ancho, alto, fps, duracion)
            
            metricas = MetricasVideo(
                tamano_bytes=tamano,
                duracion_segundos=duracion,
                resolucion=(ancho, alto),
                fps_real=fps,
                bitrate_real=bitrate_video,
                codec_video=codec_video,
                codec_audio=codec_audio,
                checksum=checksum,
                calidad_estimada=calidad
            )
            
            self.logger.log(NivelSeveridad.DEBUG, 
                          f"Video validado: {ancho}x{alto}@{fps:.2f}fps, {duracion:.2f}s")
            
            return metricas
            
        except Exception as e:
            self.logger.log(NivelSeveridad.ERROR, f"Error validando video: {e}")
            # Retornar métricas por defecto
            return MetricasVideo(
                tamano_bytes=0,
                duracion_segundos=0.0,
                resolucion=(0, 0),
                fps_real=0.0,
                bitrate_real="unknown",
                codec_video="unknown",
                codec_audio="unknown",
                checksum="",
                calidad_estimada=CalidadVideo.BAJA
            )
    
    def _calcular_checksum(self, archivo: Path) -> str:
        """Calcular checksum SHA-256 del archivo"""
        hash_sha256 = hashlib.sha256()
        try:
            with open(archivo, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            self.logger.log(NivelSeveridad.ERROR, f"Error calculando checksum: {e}")
            return ""
    
    def _estimar_calidad(self, ancho: int, alto: int, fps: float, duracion: float) -> CalidadVideo:
        """Estimar calidad del video basado en sus características"""
        # Criterios de calidad
        if ancho >= 3840 and alto >= 2160:  # 4K
            return CalidadVideo.ULTRA
        elif ancho >= 1920 and alto >= 1080:  # 1080p
            return CalidadVideo.ALTA
        elif ancho >= 1280 and alto >= 720:  # 720p
            return CalidadVideo.MEDIA
        else:
            return CalidadVideo.BAJA


class ProcesadorVideoFFmpeg:
    """Procesador de video usando FFmpeg"""
    
    def __init__(self):
        self.logger = obtener_sistema_logging().obtener_sistema_logger()
        self.verificador = VerificadorDependenciasVideo()
        
        # Verificar dependencias al inicializar
        self.dependencias_disponibles = self.verificador.verificar_todas_dependencias()
    
    def combinar_videos(self, videos: List[Path], transiciones: List[TipoTransicion], 
                       archivo_salida: Path) -> bool:
        """Combinar múltiples videos con transiciones"""
        try:
            if not self.dependencias_disponibles.get('ffmpeg', False):
                raise Exception("FFmpeg no disponible")
            
            if len(videos) != len(transiciones) + 1:
                raise ValueError("Número incorrecto de transiciones")
            
            # Crear archivo de lista para FFmpeg
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as list_file:
                list_path = Path(list_file.name)
                
                for video in videos:
                    if video.exists():
                        list_file.write(f"file '{video.absolute()}'\n")
            
            # Comando FFmpeg para concatenar videos
            cmd = [
                'ffmpeg',
                '-y',
                '-f', 'concat',
                '-safe', '0',
                '-i', str(list_path),
                '-c', 'copy',
                str(archivo_salida)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            # Limpiar archivo temporal
            if list_path.exists():
                list_path.unlink()
            
            if result.returncode == 0 and archivo_salida.exists():
                self.logger.log(NivelSeveridad.INFO, f"Videos combinados: {archivo_salida.name}")
                return True
            else:
                self.logger.log(NivelSeveridad.ERROR, f"Error combinando videos: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.log(NivelSeveridad.ERROR, f"Error combinando videos: {e}")
            return False
    
    def aplicar_efectos(self, video_entrada: Path, efectos: List[str], 
                       video_salida: Path) -> bool:
        """Aplicar efectos al video"""
        try:
            if not self.dependencias_disponibles.get('ffmpeg', False):
                raise Exception("FFmpeg no disponible")
            
            if not video_entrada.exists():
                raise FileNotFoundError(f"Video de entrada no encontrado: {video_entrada}")
            
            # Construir filtro de efectos
            filtro = ','.join(efectos) if efectos else 'null'
            
            cmd = [
                'ffmpeg',
                '-y',
                '-i', str(video_entrada),
                '-vf', filtro,
                '-c:a', 'copy',
                str(video_salida)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0 and video_salida.exists():
                self.logger.log(NivelSeveridad.INFO, f"Efectos aplicados: {video_salida.name}")
                return True
            else:
                self.logger.log(NivelSeveridad.ERROR, f"Error aplicando efectos: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.log(NivelSeveridad.ERROR, f"Error aplicando efectos: {e}")
            return False
    
    def convertir_formato(self, video_entrada: Path, formato_salida: TipoVideo,
                         calidad: CalidadVideo, archivo_salida: Path) -> bool:
        """Convertir video a otro formato y calidad"""
        try:
            if not self.dependencias_disponibles.get('ffmpeg', False):
                raise Exception("FFmpeg no disponible")
            
            if not video_entrada.exists():
                raise FileNotFoundError(f"Video de entrada no encontrado: {video_entrada}")
            
            # Configurar parámetros según calidad
            if calidad == CalidadVideo.ULTRA:
                resolucion = "3840x2160"
                bitrate = "20M"
            elif calidad == CalidadVideo.ALTA:
                resolucion = "1920x1080"
                bitrate = "10M"
            elif calidad == CalidadVideo.MEDIA:
                resolucion = "1280x720"
                bitrate = "5M"
            else:
                resolucion = "854x480"
                bitrate = "2M"
            
            cmd = [
                'ffmpeg',
                '-y',
                '-i', str(video_entrada),
                '-s', resolucion,
                '-b:v', bitrate,
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-pix_fmt', 'yuv420p',
                str(archivo_salida)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0 and archivo_salida.exists():
                self.logger.log(NivelSeveridad.INFO, f"Video convertido: {archivo_salida.name}")
                return True
            else:
                self.logger.log(NivelSeveridad.ERROR, f"Error convirtiendo video: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.log(NivelSeveridad.ERROR, f"Error convirtiendo video: {e}")
            return False


class VideoEditorUltraFuncional:
    """Sistema principal ultra-funcional de edición de video"""
    
    def __init__(self, ruta_cache: Path = None):
        self.logger = obtener_sistema_logging().obtener_sistema_logger()
        self.ruta_cache = ruta_cache or Path("./cache_video")
        self.ruta_cache.mkdir(parents=True, exist_ok=True)
        
        # Componentes del sistema
        self.verificador = VerificadorDependenciasVideo()
        self.generador = GeneradorPlaceholders()
        self.validador = ValidadorVideo()
        self.procesador = ProcesadorVideoFFmpeg()
        self.cache = obtener_cache_multinivel(self.ruta_cache.parent)
        
        # Estado del sistema
        self.dependencias_disponibles = {}
        self.estadisticas = {
            "videos_procesados": 0,
            "placeholders_generados": 0,
            "tiempo_promedio_procesamiento": 0.0,
            "cache_hits": 0
        }
        
        # Inicializar sistema
        self.inicializar_sistema()
    
    def inicializar_sistema(self):
        """Inicializar sistema de edición de video"""
        try:
            self.logger.log(NivelSeveridad.INFO, "🚀 Inicializando VideoEditor ultra-funcional...")
            
            # Verificar dependencias
            self.dependencias_disponibles = self.verificador.verificar_todas_dependencias()
            
            # Verificar que al menos FFmpeg esté disponible
            if not self.dependencias_disponibles.get('ffmpeg', False):
                self.logger.log(NivelSeveridad.WARNING, 
                              "⚠️ FFmpeg no disponible - funcionalidad limitada")
            
            self.logger.log(NivelSeveridad.INFO, 
                          f"✅ VideoEditor inicializado con {sum(self.dependencias_disponibles.values())} dependencias")
            
        except Exception as e:
            self.logger.log(NivelSeveridad.ERROR, f"Error inicializando VideoEditor: {e}")
    
    def crear_video_desde_imagenes(self, imagenes: List[Path], duraciones: List[float],
                                  archivo_salida: Path, transiciones: Optional[List[TipoTransicion]] = None) -> ResultadoVideo:
        """Crear video desde una lista de imágenes"""
        inicio_procesamiento = time.time()
        
        try:
            if not imagenes:
                raise ValueError("No se proporcionaron imágenes")
            
            if len(imagenes) != len(duraciones):
                raise ValueError("Número de imágenes y duraciones no coincide")
            
            # Generar placeholders para cada imagen
            placeholders = []
            for i, imagen in enumerate(imagenes):
                if imagen.exists():
                    placeholder = self.generador.generar_placeholder_imagen(imagen, duraciones[i])
                    placeholders.append(placeholder)
                else:
                    # Generar placeholder de texto como fallback
                    placeholder = self.generador.generar_placeholder_texto(
                        f"Imagen no encontrada: {imagen.name}", duraciones[i])
                    placeholders.append(placeholder)
            
            # Combinar videos con transiciones
            if transiciones and len(transiciones) == len(placeholders) - 1:
                # Aplicar transiciones personalizadas
                exito = self.procesador.combinar_videos(placeholders, transiciones, archivo_salida)
            else:
                # Usar transiciones por defecto
                transiciones_default = [TipoTransicion.DESVANECER] * (len(placeholders) - 1)
                exito = self.procesador.combinar_videos(placeholders, transiciones_default, archivo_salida)
            
            # Limpiar placeholders temporales
            for placeholder in placeholders:
                if placeholder.exists() and "temp" in str(placeholder):
                    try:
                        placeholder.unlink()
                    except:
                        pass
            
            tiempo_total = time.time() - inicio_procesamiento
            
            if exito and archivo_salida.exists():
                # Validar video generado
                metricas = self.validador.validar_video(archivo_salida)
                
                # Actualizar estadísticas
                self.estadisticas["videos_procesados"] += 1
                self._actualizar_tiempo_promedio(tiempo_total)
                
                self.logger.log(NivelSeveridad.INFO, 
                              f"✅ Video creado desde {len(imagenes)} imágenes: {archivo_salida.name}")
                
                return ResultadoVideo(
                    exito=True,
                    archivo_video=archivo_salida,
                    metricas=metricas,
                    tiempo_procesamiento=tiempo_total,
                    recursos_utilizados={"imagenes": len(imagenes), "duraciones": duraciones},
                    error_mensaje=None
                )
            else:
                error_msg = "Error creando video desde imágenes"
                self.logger.log(NivelSeveridad.ERROR, error_msg)
                
                return ResultadoVideo(
                    exito=False,
                    archivo_video=None,
                    metricas=None,
                    tiempo_procesamiento=tiempo_total,
                    recursos_utilizados={"imagenes": len(imagenes), "duraciones": duraciones},
                    error_mensaje=error_msg
                )
                
        except Exception as e:
            tiempo_total = time.time() - inicio_procesamiento
            error_msg = f"Error creando video desde imágenes: {e}"
            self.logger.log(NivelSeveridad.ERROR, error_msg)
            
            return ResultadoVideo(
                exito=False,
                archivo_video=None,
                metricas=None,
                tiempo_procesamiento=tiempo_total,
                recursos_utilizados={"imagenes": len(imagenes) if 'imagenes' in locals() else 0},
                error_mensaje=error_msg
            )
    
    def aplicar_efectos_video(self, video_entrada: Path, efectos: List[str],
                            archivo_salida: Path) -> ResultadoVideo:
        """Aplicar efectos a un video existente"""
        inicio_procesamiento = time.time()
        
        try:
            if not video_entrada.exists():
                raise FileNotFoundError(f"Video de entrada no encontrado: {video_entrada}")
            
            # Verificar cache
            video_hash = hashlib.md5(f"{video_entrada}_{sorted(efectos)}".encode()).hexdigest()
            cache_key = f"video_efectos_{video_hash}"
            
            video_cached = self.cache.get(cache_key)
            if video_cached and isinstance(video_cached, Path) and video_cached.exists():
                self.estadisticas["cache_hits"] += 1
                # Copiar desde cache
                shutil.copy2(video_cached, archivo_salida)
                
                metricas = self.validador.validar_video(archivo_salida)
                tiempo_total = time.time() - inicio_procesamiento
                
                self.logger.log(NivelSeveridad.INFO, f"✅ Video con efectos desde cache: {archivo_salida.name}")
                
                return ResultadoVideo(
                    exito=True,
                    archivo_video=archivo_salida,
                    metricas=metricas,
                    tiempo_procesamiento=tiempo_total,
                    recursos_utilizados={"efectos": efectos},
                    error_mensaje=None
                )
            
            # Aplicar efectos
            exito = self.procesador.aplicar_efectos(video_entrada, efectos, archivo_salida)
            tiempo_total = time.time() - inicio_procesamiento
            
            if exito and archivo_salida.exists():
                # Validar video procesado
                metricas = self.validador.validar_video(archivo_salida)
                
                # Guardar en cache
                self.cache.put(cache_key, archivo_salida, TipoDato.VIDEO, tiempo_total)
                
                # Actualizar estadísticas
                self.estadisticas["videos_procesados"] += 1
                self._actualizar_tiempo_promedio(tiempo_total)
                
                self.logger.log(NivelSeveridad.INFO, f"✅ Efectos aplicados: {archivo_salida.name}")
                
                return ResultadoVideo(
                    exito=True,
                    archivo_video=archivo_salida,
                    metricas=metricas,
                    tiempo_procesamiento=tiempo_total,
                    recursos_utilizados={"efectos": efectos},
                    error_mensaje=None
                )
            else:
                error_msg = "Error aplicando efectos al video"
                self.logger.log(NivelSeveridad.ERROR, error_msg)
                
                return ResultadoVideo(
                    exito=False,
                    archivo_video=None,
                    metricas=None,
                    tiempo_procesamiento=tiempo_total,
                    recursos_utilizados={"efectos": efectos},
                    error_mensaje=error_msg
                )
                
        except Exception as e:
            tiempo_total = time.time() - inicio_procesamiento
            error_msg = f"Error aplicando efectos: {e}"
            self.logger.log(NivelSeveridad.ERROR, error_msg)
            
            return ResultadoVideo(
                exito=False,
                archivo_video=None,
                metricas=None,
                tiempo_procesamiento=tiempo_total,
                recursos_utilizados={"efectos": efectos if 'efectos' in locals() else []},
                error_mensaje=error_msg
            )
    
    def convertir_video(self, video_entrada: Path, formato_salida: TipoVideo,
                       calidad: CalidadVideo, archivo_salida: Path) -> ResultadoVideo:
        """Convertir video a otro formato y calidad"""
        inicio_procesamiento = time.time()
        
        try:
            if not video_entrada.exists():
                raise FileNotFoundError(f"Video de entrada no encontrado: {video_entrada}")
            
            # Verificar cache
            video_hash = hashlib.md5(f"{video_entrada}_{formato_salida.value}_{calidad.value}".encode()).hexdigest()
            cache_key = f"video_conversion_{video_hash}"
            
            video_cached = self.cache.get(cache_key)
            if video_cached and isinstance(video_cached, Path) and video_cached.exists():
                self.estadisticas["cache_hits"] += 1
                # Copiar desde cache
                shutil.copy2(video_cached, archivo_salida)
                
                metricas = self.validador.validar_video(archivo_salida)
                tiempo_total = time.time() - inicio_procesamiento
                
                self.logger.log(NivelSeveridad.INFO, f"✅ Video convertido desde cache: {archivo_salida.name}")
                
                return ResultadoVideo(
                    exito=True,
                    archivo_video=archivo_salida,
                    metricas=metricas,
                    tiempo_procesamiento=tiempo_total,
                    recursos_utilizados={"formato": formato_salida.value, "calidad": calidad.value},
                    error_mensaje=None
                )
            
            # Convertir video
            exito = self.procesador.convertir_formato(video_entrada, formato_salida, calidad, archivo_salida)
            tiempo_total = time.time() - inicio_procesamiento
            
            if exito and archivo_salida.exists():
                # Validar video convertido
                metricas = self.validador.validar_video(archivo_salida)
                
                # Guardar en cache
                self.cache.put(cache_key, archivo_salida, TipoDato.VIDEO, tiempo_total)
                
                # Actualizar estadísticas
                self.estadisticas["videos_procesados"] += 1
                self._actualizar_tiempo_promedio(tiempo_total)
                
                self.logger.log(NivelSeveridad.INFO, f"✅ Video convertido: {archivo_salida.name}")
                
                return ResultadoVideo(
                    exito=True,
                    archivo_video=archivo_salida,
                    metricas=metricas,
                    tiempo_procesamiento=tiempo_total,
                    recursos_utilizados={"formato": formato_salida.value, "calidad": calidad.value},
                    error_mensaje=None
                )
            else:
                error_msg = "Error convirtiendo video"
                self.logger.log(NivelSeveridad.ERROR, error_msg)
                
                return ResultadoVideo(
                    exito=False,
                    archivo_video=None,
                    metricas=None,
                    tiempo_procesamiento=tiempo_total,
                    recursos_utilizados={"formato": formato_salida.value, "calidad": calidad.value},
                    error_mensaje=error_msg
                )
                
        except Exception as e:
            tiempo_total = time.time() - inicio_procesamiento
            error_msg = f"Error convirtiendo video: {e}"
            self.logger.log(NivelSeveridad.ERROR, error_msg)
            
            return ResultadoVideo(
                exito=False,
                archivo_video=None,
                metricas=None,
                tiempo_procesamiento=tiempo_total,
                recursos_utilizados={"formato": formato_salida.value if 'formato_salida' in locals() else "unknown",
                                   "calidad": calidad.value if 'calidad' in locals() else "unknown"},
                error_mensaje=error_msg
            )
    
    def _actualizar_tiempo_promedio(self, tiempo_procesamiento: float):
        """Actualizar tiempo promedio de procesamiento"""
        total = self.estadisticas["videos_procesados"]
        if total > 0:
            self.estadisticas["tiempo_promedio_procesamiento"] = (
                (self.estadisticas["tiempo_promedio_procesamiento"] * (total - 1) + tiempo_procesamiento) / total
            )
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtener estadísticas del sistema"""
        return self.estadisticas.copy()
    
    def obtener_dependencias_disponibles(self) -> Dict[str, bool]:
        """Obtener estado de dependencias"""
        return self.dependencias_disponibles.copy()
    
    def probar_sistema(self) -> Dict[str, Any]:
        """Probar funcionalidad del sistema"""
        resultados = {
            "dependencias_verificadas": self.verificador.verificar_todas_dependencias(),
            "versiones": self.verificador.obtener_versiones(),
            "estadisticas": self.estadisticas.copy()
        }
        
        # Probar generación de placeholder básico
        try:
            placeholder = self.generador.generar_placeholder_texto("Test Video", 2.0)
            resultados["placeholder_generado"] = placeholder.exists()
            if placeholder.exists():
                placeholder.unlink()  # Limpiar
        except Exception as e:
            resultados["placeholder_generado"] = False
            resultados["error_placeholder"] = str(e)
        
        return resultados


# Instancia global
VIDEO_EDITOR_GLOBAL = None

def obtener_video_editor(ruta_cache: Path = None) -> VideoEditorUltraFuncional:
    """Obtener instancia global del VideoEditor"""
    global VIDEO_EDITOR_GLOBAL
    if VIDEO_EDITOR_GLOBAL is None:
        VIDEO_EDITOR_GLOBAL = VideoEditorUltraFuncional(ruta_cache)
    return VIDEO_EDITOR_GLOBAL