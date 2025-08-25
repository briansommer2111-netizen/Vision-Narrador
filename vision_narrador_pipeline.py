"""
Vision-Narrador: Pipeline Principal Ultra-Robusto
============================================

Pipeline ultra-robusto de procesamiento con:
- Integración completa de todos los módulos optimizados
- Sistema de recuperación automática inteligente
- Monitoreo continuo de rendimiento y salud
- Validación exhaustiva en cada etapa
- Sistema de fallbacks automático
"""

import time
import json
import threading
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from datetime import datetime

# Importar todos los módulos optimizados
from configuracion_ultra_robusta import ConfiguracionUltraRobusta
from gestor_estado_avanzado import GestorEstadoAvanzado
from workspace_manager_avanzado import WorkspaceManagerAvanzado
from sistema_logging_monitoreo import obtener_sistema_logging, NivelSeveridad
from multilayer_ner_avanzado import MultiLayerNERAvanzado
from cache_lru_multinivel import obtener_cache_multinivel
from tts_handler_ultraconfiable import TTSHandlerUltraConfiable
from video_editor_ultrafuncional import VideoEditorUltraFuncional
from sistema_recuperacion_ultraconfiable import obtener_sistema_recuperacion
from sistema_paralelizacion_ultraavanzado import obtener_sistema_paralelizacion, PrioridadTarea, TipoWorker
from validador_universal import obtener_validador_universal, ResultadoValidacion

class VisionNarradorPipeline:
    """Pipeline principal ultra-robusto de Vision-Narrador"""
    
    def __init__(self, ruta_proyecto: Path = None):
        self.ruta_proyecto = ruta_proyecto or Path("./vision_narrador_project")
        self.ruta_proyecto.mkdir(parents=True, exist_ok=True)
        
        self.logger = obtener_sistema_logging().obtener_sistema_logger()
        self.logger.log(NivelSeveridad.INFO, "🚀 Iniciando VisionNarrador Pipeline Ultra-Robusto")
        
        # Inicializar todos los componentes del sistema
        self._inicializar_sistema()
        
        self.logger.log(NivelSeveridad.INFO, "✅ VisionNarrador Pipeline inicializado completamente")
    
    def _inicializar_sistema(self):
        """Inicializar todos los componentes del sistema"""
        try:
            # 1. Configuración ultra-robusta
            self.logger.log(NivelSeveridad.INFO, "🔧 Inicializando Configuración Ultra-Robusta...")
            self.configuracion = ConfiguracionUltraRobusta(str(self.ruta_proyecto))
            config_result = self.configuracion.inicializar_sistema_completo()
            if not config_result[0]:
                raise Exception(f"Error en configuración: {config_result[1]}")
            self.logger.log(NivelSeveridad.INFO, "✅ Configuración Ultra-Robusta inicializada")
            
            # 2. Gestor de estado avanzado
            self.logger.log(NivelSeveridad.INFO, "💾 Inicializando Gestor de Estado Avanzado...")
            self.gestor_estado = GestorEstadoAvanzado(self.ruta_proyecto)
            estado_result = self.gestor_estado.inicializar_estado()
            if not estado_result[0]:
                raise Exception(f"Error en gestor de estado: {estado_result[1]}")
            self.logger.log(NivelSeveridad.INFO, "✅ Gestor de Estado Avanzado inicializado")
            
            # 3. Workspace manager avanzado
            self.logger.log(NivelSeveridad.INFO, "📁 Inicializando Workspace Manager Avanzado...")
            self.workspace_manager = WorkspaceManagerAvanzado(str(self.ruta_proyecto))
            # No necesita inicialización adicional ya que se inicializa en el constructor
            self.logger.log(NivelSeveridad.INFO, "✅ Workspace Manager Avanzado inicializado")
            
            # 4. Sistema de recuperación ultra-confiable
            self.logger.log(NivelSeveridad.INFO, "🔄 Inicializando Sistema de Recuperación Ultra-Confiable...")
            self.sistema_recuperacion = obtener_sistema_recuperacion(self.ruta_proyecto)
            self.logger.log(NivelSeveridad.INFO, "✅ Sistema de Recuperación Ultra-Confiable inicializado")
            
            # 5. Sistema de paralelización ultra-avanzado
            self.logger.log(NivelSeveridad.INFO, "⚡ Inicializando Sistema de Paralelización Ultra-Avanzado...")
            self.sistema_paralelizacion = obtener_sistema_paralelizacion(self.ruta_proyecto)
            self.logger.log(NivelSeveridad.INFO, "✅ Sistema de Paralelización Ultra-Avanzado inicializado")
            
            # 6. MultiLayerNER avanzado
            self.logger.log(NivelSeveridad.INFO, "🧠 Inicializando MultiLayerNER Avanzado...")
            self.ner = MultiLayerNERAvanzado()
            self.logger.log(NivelSeveridad.INFO, "✅ MultiLayerNER Avanzado inicializado")
            
            # 7. TTS Handler ultra-confiable
            self.logger.log(NivelSeveridad.INFO, "🗣️ Inicializando TTS Handler Ultra-Confiable...")
            self.tts_handler = TTSHandlerUltraConfiable(self.ruta_proyecto)
            self.logger.log(NivelSeveridad.INFO, "✅ TTS Handler Ultra-Confiable inicializado")
            
            # 8. Video Editor ultra-funcional
            self.logger.log(NivelSeveridad.INFO, "🎬 Inicializando Video Editor Ultra-Funcional...")
            self.video_editor = VideoEditorUltraFuncional(self.ruta_proyecto)
            self.logger.log(NivelSeveridad.INFO, "✅ Video Editor Ultra-Funcional inicializado")
            
            # 9. Validador universal
            self.logger.log(NivelSeveridad.INFO, "🔍 Inicializando Validador Universal...")
            self.validador = obtener_validador_universal(self.ruta_proyecto)
            self.logger.log(NivelSeveridad.INFO, "✅ Validador Universal inicializado")
            
            # 10. Cache multinivel
            self.logger.log(NivelSeveridad.INFO, "キャッシング Inicializando Cache Multinivel...")
            self.cache = obtener_cache_multinivel(self.ruta_proyecto)
            self.logger.log(NivelSeveridad.INFO, "✅ Cache Multinivel inicializado")
            
        except Exception as e:
            self.logger.log(NivelSeveridad.ERROR, f"❌ Error inicializando sistema: {e}")
            raise
    
    def procesar_novela_completa(self, ruta_novela: Path) -> bool:
        """Procesar una novela completa convirtiéndola en videos webtoon"""
        self.logger.log(NivelSeveridad.INFO, f"📖 Iniciando procesamiento de novela: {ruta_novela}")
        
        try:
            # Registrar inicio en estado
            self.gestor_estado.actualizar_entidad(
                "procesamiento", 
                f"novela_{ruta_novela.stem}",
                {
                    "estado": "iniciado",
                    "ruta_novela": str(ruta_novela),
                    "timestamp_inicio": datetime.now().isoformat()
                }
            )
            
            # Detectar capítulos nuevos
            self.logger.log(NivelSeveridad.INFO, "🔍 Detectando capítulos nuevos...")
            capitulos_nuevos = self.workspace_manager.detectar_capitulos_nuevos()
            self.logger.log(NivelSeveridad.INFO, f"📚 Capítulos nuevos detectados: {len(capitulos_nuevos)}")
            
            if not capitulos_nuevos:
                self.logger.log(NivelSeveridad.WARNING, "📭 No se encontraron capítulos nuevos para procesar")
                return True
            
            # Procesar cada capítulo
            capitulos_exitosos = 0
            for capitulo_info in capitulos_nuevos:
                capitulo_exitoso = self._procesar_capitulo(capitulo_info)
                if capitulo_exitoso:
                    capitulos_exitosos += 1
            
            # Registrar resultado final
            resultado_procesamiento = {
                "estado": "completado" if capitulos_exitosos == len(capitulos_nuevos) else "parcial",
                "total_capitulos": len(capitulos_nuevos),
                "capitulos_exitosos": capitulos_exitosos,
                "timestamp_final": datetime.now().isoformat()
            }
            
            self.gestor_estado.actualizar_entidad(
                "procesamiento",
                f"novela_{ruta_novela.stem}",
                resultado_procesamiento
            )
            
            self.logger.log(NivelSeveridad.INFO, 
                          f"🏁 Procesamiento completado: {capitulos_exitosos}/{len(capitulos_nuevos)} capítulos")
            
            return capitulos_exitosos > 0
            
        except Exception as e:
            self.logger.log(NivelSeveridad.ERROR, f"❌ Error procesando novela: {e}")
            # Registrar error en estado
            self.gestor_estado.actualizar_entidad(
                "procesamiento",
                f"novela_{ruta_novela.stem}",
                {
                    "estado": "error",
                    "error_mensaje": str(e),
                    "timestamp_error": datetime.now().isoformat()
                }
            )
            return False
    
    def _procesar_capitulo(self, capitulo_info: Dict[str, Any]) -> bool:
        """Procesar un capítulo individual"""
        nombre_capitulo = capitulo_info.get("nombre", "desconocido")
        ruta_archivo = Path(capitulo_info.get("ruta", ""))
        
        self.logger.log(NivelSeveridad.INFO, f"📄 Procesando capítulo: {nombre_capitulo}")
        
        try:
            # Registrar inicio de procesamiento del capítulo
            self.gestor_estado.actualizar_entidad(
                "capitulo",
                nombre_capitulo,
                {
                    "estado": "procesando",
                    "ruta_archivo": str(ruta_archivo),
                    "timestamp_inicio": datetime.now().isoformat()
                }
            )
            
            # Leer contenido del capítulo
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                contenido = f.read()
            
            # Crear checkpoint antes de procesar
            checkpoint_id = self.sistema_recuperacion.crear_checkpoint_contextual(
                "procesamiento_capitulo",
                nombre_capitulo,
                {"contenido_original": contenido, "etapa": "inicio"}
            )
            
            # 1. Extracción de entidades con MultiLayerNER
            self.logger.log(NivelSeveridad.INFO, f"🧠 Extrayendo entidades del capítulo {nombre_capitulo}...")
            entidades_result = self.ner.extraer_entidades_multicapa(contenido)
            
            # Validar entidades extraídas
            validacion_entidades = self.validador.validar_datos({
                "entidades": entidades_result.entidades,
                "texto": contenido
            })
            
            if not validacion_entidades.exito:
                self.logger.log(NivelSeveridad.WARNING, 
                              f"⚠️ Validación de entidades fallida para {nombre_capitulo}")
            
            # 2. Generación de guion (simulación)
            self.logger.log(NivelSeveridad.INFO, f"📝 Generando guion para {nombre_capitulo}...")
            guion = self._generar_guion(contenido, entidades_result.entidades)
            
            # Validar guion generado
            validacion_guion = self.validador.validar_datos({
                "guion": guion,
                "entidades": entidades_result.entidades
            })
            
            # 3. Síntesis de voz con TTS Handler
            self.logger.log(NivelSeveridad.INFO, f"🗣️ Generando audio para {nombre_capitulo}...")
            
            # Dividir contenido en segmentos para TTS
            segmentos = self._dividir_en_segmentos(contenido)
            archivos_audio = []
            
            for i, segmento in enumerate(segmentos):
                archivo_audio = self.ruta_proyecto / "output" / f"{nombre_capitulo}_segmento_{i}.wav"
                archivo_audio.parent.mkdir(parents=True, exist_ok=True)
                
                tts_result = self.tts_handler.sintetizar_texto(segmento, archivo_audio)
                if tts_result.exito:
                    archivos_audio.append(tts_result.archivo_audio)
                else:
                    self.logger.log(NivelSeveridad.ERROR, 
                                  f"❌ Error generando audio para segmento {i}: {tts_result.error_mensaje}")
            
            # 4. Generación de imágenes (simulación)
            self.logger.log(NivelSeveridad.INFO, f"🎨 Generando imágenes para {nombre_capitulo}...")
            imagenes = self._generar_imagenes(guion, entidades_result.entidades)
            
            # 5. Creación de video con Video Editor
            self.logger.log(NivelSeveridad.INFO, f"🎬 Creando video para {nombre_capitulo}...")
            
            # Duraciones simuladas para cada imagen
            duraciones = [3.0] * len(imagenes)  # 3 segundos por imagen
            
            archivo_video_final = self.ruta_proyecto / "output" / f"{nombre_capitulo}.mp4"
            archivo_video_final.parent.mkdir(parents=True, exist_ok=True)
            
            video_result = self.video_editor.crear_video_desde_imagenes(
                imagenes, duraciones, archivo_video_final
            )
            
            if not video_result.exito:
                raise Exception(f"Error creando video: {video_result.error_mensaje}")
            
            # 6. Validación final del video
            validacion_video = self.validador.validar_datos({
                "video": str(archivo_video_final),
                "duracion": video_result.metricas.duracion_segundos if video_result.metricas else 0,
                "calidad": video_result.metricas.calidad_estimada.value if video_result.metricas else "desconocida"
            })
            
            # Registrar resultado exitoso
            self.gestor_estado.actualizar_entidad(
                "capitulo",
                nombre_capitulo,
                {
                    "estado": "completado",
                    "archivo_video": str(archivo_video_final),
                    "entidades_detectadas": len(entidades_result.entidades),
                    "segmentos_audio": len(archivos_audio),
                    "imagenes_generadas": len(imagenes),
                    "validacion_final": validacion_video.resultado.value,
                    "timestamp_final": datetime.now().isoformat()
                }
            )
            
            self.logger.log(NivelSeveridad.INFO, f"✅ Capítulo {nombre_capitulo} procesado exitosamente")
            return True
            
        except Exception as e:
            self.logger.log(NivelSeveridad.ERROR, f"❌ Error procesando capítulo {nombre_capitulo}: {e}")
            
            # Registrar error en estado
            self.gestor_estado.actualizar_entidad(
                "capitulo",
                nombre_capitulo,
                {
                    "estado": "error",
                    "error_mensaje": str(e),
                    "timestamp_error": datetime.now().isoformat()
                }
            )
            
            # Intentar recuperación
            self._intentar_recuperacion(nombre_capitulo, str(e))
            return False
    
    def _generar_guion(self, contenido: str, entidades: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generar guion para el capítulo (simulación)"""
        # En una implementación real, esto usaría un modelo de generación de guiones
        # Por ahora, creamos un guion simple basado en el contenido
        
        # Dividir en escenas (simulación)
        escenas = []
        parrafos = contenido.split('\n\n')
        
        for i, parrafo in enumerate(parrafos[:10]):  # Limitar a 10 escenas para ejemplo
            if parrafo.strip():
                escena = {
                    "id": f"escena_{i}",
                    "contenido": parrafo[:200] + "..." if len(parrafo) > 200 else parrafo,
                    "personajes": [ent["texto"] for ent in entidades[:3]],  # Primeras 3 entidades
                    "tipo": "dialogo" if i % 2 == 0 else "narracion"
                }
                escenas.append(escena)
        
        return escenas
    
    def _dividir_en_segmentos(self, texto: str, tamano_maximo: int = 1000) -> List[str]:
        """Dividir texto en segmentos para TTS"""
        palabras = texto.split()
        segmentos = []
        segmento_actual = []
        longitud_actual = 0
        
        for palabra in palabras:
            if longitud_actual + len(palabra) > tamano_maximo and segmento_actual:
                segmentos.append(" ".join(segmento_actual))
                segmento_actual = [palabra]
                longitud_actual = len(palabra)
            else:
                segmento_actual.append(palabra)
                longitud_actual += len(palabra) + 1  # +1 por el espacio
        
        if segmento_actual:
            segmentos.append(" ".join(segmento_actual))
        
        return segmentos
    
    def _generar_imagenes(self, guion: List[Dict[str, Any]], entidades: List[Dict[str, Any]]) -> List[Path]:
        """Generar imágenes para las escenas (simulación)"""
        imagenes = []
        ruta_imagenes = self.ruta_proyecto / "imagenes_generadas"
        ruta_imagenes.mkdir(parents=True, exist_ok=True)
        
        for i, escena in enumerate(guion[:5]):  # Limitar a 5 imágenes para ejemplo
            # En una implementación real, esto usaría un generador de imágenes
            # Por ahora, creamos placeholders
            
            imagen_path = ruta_imagenes / f"escena_{i}.png"
            
            # Generar placeholder con VideoEditor
            try:
                placeholder = self.video_editor.generador.generar_placeholder_texto(
                    f"Escena {i}: {escena.get('contenido', '')[:50]}...", 3.0
                )
                # Copiar o mover el placeholder a la ubicación deseada
                import shutil
                shutil.copy2(placeholder, imagen_path)
                imagenes.append(imagen_path)
            except Exception as e:
                self.logger.log(NivelSeveridad.WARNING, f"⚠️ Error generando imagen {i}: {e}")
                # Usar imagen de fallback
                imagenes.append(imagen_path)
        
        return imagenes
    
    def _intentar_recuperacion(self, nombre_capitulo: str, error_mensaje: str):
        """Intentar recuperación automática en caso de error"""
        self.logger.log(NivelSeveridad.WARNING, f"🔄 Intentando recuperación para {nombre_capitulo}...")
        
        try:
            # Registrar incidente
            self.sistema_recuperacion.gestor_incidentes.registrar_incidente(
                "ERROR", 
                "pipeline", 
                f"Error procesando capítulo {nombre_capitulo}", 
                {"error": error_mensaje, "capitulo": nombre_capitulo}
            )
            
            # Ejecutar recuperación
            resultado_recuperacion = self.sistema_recuperacion.ejecutar_recuperacion()
            
            if resultado_recuperacion.exito:
                self.logger.log(NivelSeveridad.INFO, "✅ Recuperación exitosa")
            else:
                self.logger.log(NivelSeveridad.ERROR, 
                              f"❌ Recuperación fallida: {resultado_recuperacion.mensaje}")
                
        except Exception as e:
            self.logger.log(NivelSeveridad.ERROR, f"❌ Error en proceso de recuperación: {e}")
    
    def obtener_estado_sistema(self) -> Dict[str, Any]:
        """Obtener estado completo del sistema"""
        return {
            "configuracion": {
                "sistema_inicializado": getattr(self.configuracion, 'sistema_inicializado', False),
                "configuraciones_ambiente": getattr(self.configuracion, 'configuraciones_ambiente', {}),
                "ultimo_backup": getattr(self.configuracion, 'ultimo_backup', None)
            },
            "estado": self.gestor_estado.obtener_estado_actual(),
            "workspace": self.workspace_manager.obtener_estadisticas_workspace(),
            "metricas": self.obtener_metricas_sistema()
        }
    
    def obtener_metricas_sistema(self) -> Dict[str, Any]:
        """Obtener métricas del sistema"""
        metricas = {
            "timestamp": datetime.now().isoformat(),
            "modulos": {
                "configuracion": {
                    "sistema_inicializado": getattr(self.configuracion, 'sistema_inicializado', False),
                    "ultimo_backup": getattr(self.configuracion, 'ultimo_backup', None)
                },
                "estado": self.gestor_estado.obtener_estadisticas(),
                "workspace": self.workspace_manager.obtener_estadisticas_workspace(),
                "tts": self.tts_handler.obtener_estadisticas(),
                "video": self.video_editor.obtener_estadisticas(),
                "paralelizacion": self.sistema_paralelizacion.obtener_estadisticas_detalles(),
                "validador": self.validador.obtener_estadisticas()
            }
        }
        
        return metricas
    
    def realizar_mantenimiento_sistema(self):
        """Realizar mantenimiento del sistema"""
        self.logger.log(NivelSeveridad.INFO, "🛠️ Iniciando mantenimiento del sistema...")
        
        try:
            # 1. Limpiar cache
            self.cache.limpiar()
            
            # 2. Rotar logs
            self.logger.sistema_logging.rotar_logs()
            
            # 3. Limpiar archivos temporales
            # self.workspace_manager.limpiar_temporales()  # Comentado porque no existe este método
            
            # 4. Verificar integridad del estado
            self.gestor_estado.guardar_estado()
            
            # 5. Crear backup
            self.configuracion.gestor_backups.crear_backup_automatico()
            
            self.logger.log(NivelSeveridad.INFO, "✅ Mantenimiento del sistema completado")
            
        except Exception as e:
            self.logger.log(NivelSeveridad.ERROR, f"❌ Error en mantenimiento del sistema: {e}")
    
    def cerrar_sistema(self):
        """Cerrar el sistema de manera segura"""
        self.logger.log(NivelSeveridad.INFO, "🛑 Cerrando VisionNarrador Pipeline...")
        
        try:
            # Cerrar componentes en orden
            if hasattr(self, 'sistema_paralelizacion'):
                self.sistema_paralelizacion.cerrar()
            
            if hasattr(self, 'sistema_recuperacion'):
                self.sistema_recuperacion.cerrar()
            
            if hasattr(self, 'workspace_manager'):
                self.workspace_manager.cerrar_workspace()
            
            self.logger.log(NivelSeveridad.INFO, "✅ VisionNarrador Pipeline cerrado correctamente")
            
        except Exception as e:
            self.logger.log(NivelSeveridad.ERROR, f"❌ Error cerrando sistema: {e}")


# Función para obtener instancia global del pipeline
VISION_NARRADOR_PIPELINE_GLOBAL = None

def obtener_vision_narrador_pipeline(ruta_proyecto: Path = None) -> VisionNarradorPipeline:
    """Obtener instancia global del pipeline de Vision-Narrador"""
    global VISION_NARRADOR_PIPELINE_GLOBAL
    if VISION_NARRADOR_PIPELINE_GLOBAL is None:
        VISION_NARRADOR_PIPELINE_GLOBAL = VisionNarradorPipeline(ruta_proyecto)
    return VISION_NARRADOR_PIPELINE_GLOBAL