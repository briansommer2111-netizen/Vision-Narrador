# Vision-Narrador 🎬

**Sistema de código abierto para convertir novelas en videos animados estilo webtoon**

Vision-Narrador es un pipeline modular que transforma capítulos de texto narrativo en videos animados verticales, optimizado para funcionar completamente en CPU con control total del usuario sobre el proceso creativo.

## ✨ Características Principales

- 🤖 **Extracción Inteligente de Entidades**: Sistema NER multicapa que identifica personajes, lugares y objetos
- 💬 **Chat IA Interactivo**: Validación y edición de entidades con interfaz conversacional
- 🎭 **Generación Automática de Guiones**: Conversión de texto narrativo a formato screenplay
- 🔊 **Síntesis de Voz Multiidioma**: Audio de alta calidad con soporte para español
- 🎨 **Generación de Imágenes**: Compatible con Stable Diffusion optimizado para CPU
- 🎞️ **Montaje Automático**: Videos MP4 finales con sincronización de audio y subtítulos
- 💾 **Estado Persistente**: Preserva entidades y configuraciones entre sesiones

## 🛠️ Requisitos del Sistema

### Hardware Mínimo
- **CPU**: Intel Core i5 o equivalente (recomendado Intel Xeon para mejor rendimiento)
- **RAM**: 16GB mínimo
- **Almacenamiento**: 10GB+ libres para modelos y recursos
- **GPU**: No requerida (operación 100% en CPU)

### Software
- **Python**: 3.9+ (requerido para compatibilidad con OpenVINO)
- **Sistema Operativo**: Windows 10+, macOS 10.15+, Ubuntu 20.04+

## 🚀 Instalación Rápida

### 1. Clonar el Repositorio
```bash
git clone https://github.com/tu-usuario/Vision-Narrador.git
cd Vision-Narrador
```

### 2. Instalación Automática
```bash
# Ejecutar instalador automático
python setup.py
```

### 3. Instalación Manual (Opcional)
```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\\Scripts\\activate

# Instalar dependencias
pip install -r requirements.txt

# Instalar modelos de spaCy
python -m spacy download es_core_news_lg
```

## 📖 Uso Básico

### Modo Interactivo
```bash
# Iniciar interfaz interactiva
python main.py
```

### Procesamiento Automático
```bash
# Procesar todos los capítulos nuevos
python main.py --process
```

### Chat IA para Gestión de Entidades
```bash
# Abrir chat para validar/editar entidades
python main.py --chat
```

### Ver Estado del Proyecto
```bash
# Mostrar estadísticas y configuración
python main.py --status
```

## 📁 Estructura del Proyecto

```
./novela/
├── chapters/                    # 📚 Archivos .txt de capítulos
│   ├── capitulo_01.txt
│   ├── capitulo_02.txt
│   └── ...
├── assets/                      # 🎨 Recursos generados
│   ├── characters/              # 👥 Imágenes de personajes
│   ├── locations/               # 🏰 Imágenes de lugares
│   ├── objects/                 # ⚔️ Imágenes de objetos
│   └── scenes/                  # 🎬 Escenas compuestas
├── audio/                       # 🔊 Archivos TTS generados
├── videos/                      # 🎞️ Videos de escenas individuales
├── output/                      # 📤 Videos finales exportados
├── state.json                   # 💾 Estado persistente del proyecto
└── vision_narrador.log         # 📋 Logs del sistema
```

## 🎯 Flujo de Trabajo

### 1. Preparación
1. Coloca tus archivos de capítulos (.txt) en `chapters/`
2. Ejecuta `python main.py` para inicializar el proyecto

### 2. Procesamiento
1. El sistema detecta automáticamente nuevos capítulos
2. Extrae entidades (personajes, lugares, objetos) usando NLP avanzado
3. Te permite validar y editar las entidades mediante chat IA
4. Genera guión estructurado con diálogos y descripciones
5. Crea audio mediante síntesis de voz (TTS)
6. Genera imágenes para cada escena
7. Compone las escenas finales
8. Monta el video final con sincronización de audio

### 3. Personalización
- **Entidades**: Edita descripciones, agrega imágenes personalizadas
- **Voces**: Asigna voces específicas a cada personaje
- **Estilo Visual**: Personaliza prompts para generación de imágenes
- **Configuración**: Ajusta resolución, FPS, y otros parámetros

## 🎨 Ejemplo de Capítulo

Crea un archivo `chapters/capitulo_01.txt`:

```
# Capítulo 1: El Despertar

En la pequeña aldea de Lunaria, el joven Alexis despertó con el sonido de los pájaros cantando fuera de su ventana. El sol matutino iluminaba su habitación con una luz dorada y cálida.

—¡Alexis, el desayuno está listo! —gritó su madre Elena desde la cocina.

Alexis se levantó rápidamente y se dirigió hacia la ventana. Desde allí podía ver el Bosque Encantado a lo lejos, sus árboles mecían suavemente con la brisa.

—Ya voy, mamá —respondió mientras se vestía.

Al bajar las escaleras, encontró a Elena preparando panqueques en la cocina. El aroma llenaba toda la casa.

—Hoy es un día especial —dijo Elena con una sonrisa misteriosa—. Tu padre quiere hablarte sobre algo importante.

Alexis sintió curiosidad pero decidió no preguntar más por el momento. Se sentó a desayunar, sin saber que ese día cambiaría su vida para siempre.
```

## ⚙️ Configuración Avanzada

### Modelos de IA Disponibles

#### Síntesis de Voz (TTS)
- `tts_models/es/css10/vits` (recomendado para español)
- `tts_models/es/mai/tacotron2-DDC`
- `tts_models/multilingual/multi-dataset/your_tts`

#### Procesamiento de Lenguaje Natural
- spaCy: `es_core_news_lg` (recomendado)
- Transformers: `mrm8488/bert-spanish-cased-finetuned-ner`

### Personalización de config.py

```python
# Ejemplo de configuración personalizada
config = VisionNarradorConfig("./mi_proyecto")

# Configurar resolución de video
config.video.resolution = (1080, 1920)  # Vertical para webtoon
config.video.fps = 24

# Personalizar estilo de imágenes
config.models.style_prompt = "anime, webtoon, digital art, clean lines, vibrant colors"

# Configurar modelos
config.models.tts_model = "tts_models/es/css10/vits"
```

## 🐛 Solución de Problemas

### Error: "Modelo spaCy no encontrado"
```bash
python -m spacy download es_core_news_lg
# O alternativamente:
python -m spacy download es_core_news_sm
```

### Error: "TTS no disponible"
```bash
pip install TTS
# O desde código fuente:
pip install git+https://github.com/coqui-ai/TTS.git
```

### Problemas de Memoria
- Reduce el tamaño de los chunks de procesamiento en `entity_extractor.py`
- Usa modelos más pequeños (es_core_news_sm en lugar de es_core_news_lg)
- Procesa capítulos más cortos

### Videos sin Audio
- Verifica que TTS esté correctamente instalado
- Revisa los logs en `vision_narrador.log`
- Asegúrate de que hay diálogos detectados en el texto

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Por favor:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 🙏 Agradecimientos

- [Coqui-TTS](https://github.com/coqui-ai/TTS) - Síntesis de voz
- [spaCy](https://spacy.io/) - Procesamiento de lenguaje natural
- [Transformers](https://huggingface.co/transformers/) - Modelos de IA
- [OpenVINO](https://github.com/openvinotoolkit/openvino) - Optimización para CPU
- [MoviePy](https://zulko.github.io/moviepy/) - Edición de video
- [Rich](https://rich.readthedocs.io/) - Interfaz de terminal

## 📞 Soporte

- 📧 **Email**: soporte@vision-narrador.com
- 🐛 **Issues**: [GitHub Issues](https://github.com/tu-usuario/Vision-Narrador/issues)
- 💬 **Discusiones**: [GitHub Discussions](https://github.com/tu-usuario/Vision-Narrador/discussions)
- 📖 **Wiki**: [Documentación Completa](https://github.com/tu-usuario/Vision-Narrador/wiki)

---

**¡Transforma tus historias en experiencias visuales increíbles! 🎬✨**