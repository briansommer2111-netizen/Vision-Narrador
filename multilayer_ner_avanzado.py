"""
Vision-Narrador: Sistema MultiLayerNER Ultra-Avanzado
====================================================

Sistema de NER de 4 capas con fallbacks inteligentes:
- Capa 1: spaCy para NER básico 
- Capa 2: Transformers para NER contextual
- Capa 3: Patrones personalizados narrativos
- Capa 4: Validación semántica inteligente
"""

import re
import asyncio
import time
import statistics
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import spacy
from spacy.matcher import Matcher

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

from sistema_logging_monitoreo import obtener_sistema_logging, NivelSeveridad


@dataclass
class EntidadCandidato:
    """Candidato de entidad detectado"""
    texto: str
    etiqueta: str
    confianza: float
    inicio: int
    fin: int
    contexto: str
    tipo_sugerido: str
    metodo_extraccion: str
    validaciones: Dict[str, bool] = field(default_factory=dict)
    
    def __hash__(self):
        return hash((self.texto.lower(), self.tipo_sugerido))


@dataclass
class ResultadoExtraccion:
    """Resultado de extracción completo"""
    entidades: List[EntidadCandidato]
    estadisticas: Dict[str, float]
    calidad_general: float
    tiempo_procesamiento: float
    metodo_principal: str


class ExtractorSpaCy:
    """Capa 1: Extractor spaCy optimizado"""
    
    def __init__(self):
        self.modelo = None
        self.matcher = None
        self.disponible = False
        self.logger = obtener_sistema_logging().obtener_sistema_logger()
        
    async def inicializar(self):
        """Inicializar modelo spaCy"""
        try:
            try:
                self.modelo = spacy.load("es_core_news_lg")
            except OSError:
                try:
                    self.modelo = spacy.load("es_core_news_sm")
                except OSError:
                    self.modelo = spacy.blank("es")
            
            self.matcher = Matcher(self.modelo.vocab)
            patron = [{"LOWER": {"IN": ["señor", "don"]}}, {"IS_TITLE": True}]
            self.matcher.add("PERSONAJE", [patron])
            
            self.disponible = True
            self.logger.log(NivelSeveridad.INFO, "spaCy inicializado")
            
        except Exception as e:
            self.logger.log(NivelSeveridad.ERROR, f"Error spaCy: {e}")
    
    def extraer_entidades(self, texto: str) -> List[EntidadCandidato]:
        """Extraer entidades usando spaCy"""
        if not self.disponible:
            return []
        
        try:
            doc = self.modelo(texto)
            entidades = []
            
            for ent in doc.ents:
                tipo = self._mapear_tipo(ent.label_)
                if tipo:
                    entidad = EntidadCandidato(
                        texto=ent.text,
                        etiqueta=ent.label_,
                        confianza=0.7,
                        inicio=ent.start_char,
                        fin=ent.end_char,
                        contexto=self._contexto(texto, ent.start_char, ent.end_char),
                        tipo_sugerido=tipo,
                        metodo_extraccion="spacy"
                    )
                    entidades.append(entidad)
            
            return entidades
        except Exception:
            return []
    
    def _mapear_tipo(self, label: str) -> Optional[str]:
        """Mapear tipos de spaCy"""
        mapeo = {"PER": "characters", "LOC": "locations", "MISC": "objects"}
        return mapeo.get(label)
    
    def _contexto(self, texto: str, inicio: int, fin: int) -> str:
        """Extraer contexto"""
        return texto[max(0, inicio-30):min(len(texto), fin+30)]


class ExtractorTransformers:
    """Capa 2: Extractor Transformers"""
    
    def __init__(self):
        self.pipeline_ner = None
        self.disponible = TRANSFORMERS_AVAILABLE
        self.logger = obtener_sistema_logging().obtener_sistema_logger()
        
    async def inicializar(self):
        """Inicializar Transformers"""
        if not self.disponible:
            return
        
        try:
            self.pipeline_ner = pipeline(
                "ner",
                model="mrm8488/bert-spanish-cased-finetuned-ner",
                aggregation_strategy="simple",
                device=-1,
                batch_size=4
            )
            self.logger.log(NivelSeveridad.INFO, "Transformers inicializado")
        except Exception:
            self.disponible = False
    
    def extraer_entidades(self, texto: str) -> List[EntidadCandidato]:
        """Extraer con Transformers"""
        if not self.disponible:
            return []
        
        try:
            # Procesar en chunks
            chunks = [texto[i:i+500] for i in range(0, len(texto), 450)]
            entidades = []
            offset = 0
            
            for chunk in chunks:
                resultados = self.pipeline_ner(chunk)
                for r in resultados:
                    tipo = self._mapear_tipo(r.get('entity_group', ''))
                    if tipo:
                        entidad = EntidadCandidato(
                            texto=r['word'],
                            etiqueta=r.get('entity_group', ''),
                            confianza=float(r['score']),
                            inicio=r['start'] + offset,
                            fin=r['end'] + offset,
                            contexto=self._contexto(texto, r['start'] + offset, r['end'] + offset),
                            tipo_sugerido=tipo,
                            metodo_extraccion="transformers"
                        )
                        entidades.append(entidad)
                offset += 450
            
            return entidades
        except Exception:
            return []
    
    def _mapear_tipo(self, label: str) -> Optional[str]:
        """Mapear tipos"""
        mapeo = {"PER": "characters", "LOC": "locations", "MISC": "objects"}
        return mapeo.get(label)
    
    def _contexto(self, texto: str, inicio: int, fin: int) -> str:
        """Extraer contexto"""
        return texto[max(0, inicio-30):min(len(texto), fin+30)]


class ExtractorPatrones:
    """Capa 3: Patrones personalizados"""
    
    def __init__(self):
        self.patrones = {
            "characters": [
                r'\b(Don|Doña)\s+([A-ZÁÉÍÓÚ][a-záéíóú]+)\b',
                r'\b([A-ZÁÉÍÓÚ][a-záéíóú]+)\s+(dijo|exclamó)\b'
            ],
            "locations": [
                r'\b(Reino|Ciudad)\s+de\s+([A-ZÁÉÍÓÚ][a-záéíóú\s]+)\b'
            ],
            "objects": [
                r'\b(Espada|Anillo)\s+de\s+([A-ZÁÉÍÓÚ][a-záéíóú\s]+)\b'
            ]
        }
    
    def extraer_entidades(self, texto: str) -> List[EntidadCandidato]:
        """Extraer con patrones"""
        entidades = []
        
        for tipo, patrones in self.patrones.items():
            for patron in patrones:
                for match in re.finditer(patron, texto, re.IGNORECASE):
                    nombre = match.groups()[-1]
                    entidad = EntidadCandidato(
                        texto=nombre,
                        etiqueta="PATRON",
                        confianza=0.8,
                        inicio=match.start(),
                        fin=match.end(),
                        contexto=texto[max(0, match.start()-30):match.end()+30],
                        tipo_sugerido=tipo,
                        metodo_extraccion="patterns"
                    )
                    entidades.append(entidad)
        
        return entidades


class ValidadorSemantico:
    """Capa 4: Validación semántica"""
    
    def __init__(self):
        self.indicadores = {
            "characters": {"persona", "hombre", "mujer", "rey", "reina"},
            "locations": {"lugar", "ciudad", "reino", "bosque"},
            "objects": {"objeto", "arma", "espada", "libro"}
        }
    
    def validar_entidades(self, entidades: List[EntidadCandidato]) -> List[EntidadCandidato]:
        """Validar entidades"""
        validadas = []
        
        for entidad in entidades:
            # Validación básica
            if len(entidad.texto.strip()) < 2:
                continue
            
            # Validación semántica
            contexto = entidad.contexto.lower()
            indicadores_tipo = self.indicadores.get(entidad.tipo_sugerido, set())
            tiene_indicadores = any(ind in contexto for ind in indicadores_tipo)
            
            if tiene_indicadores or entidad.confianza > 0.8:
                entidad.validaciones["semantica"] = True
                validadas.append(entidad)
        
        return validadas


class SistemaFallbacks:
    """Sistema de fallbacks inteligente"""
    
    def evaluar_calidad(self, entidades: List[EntidadCandidato]) -> float:
        """Evaluar calidad de resultados"""
        if not entidades:
            return 0.0
        
        confianza_promedio = statistics.mean([e.confianza for e in entidades])
        factor_cantidad = min(1.0, len(entidades) / 10)
        
        return (confianza_promedio * 0.7) + (factor_cantidad * 0.3)
    
    def seleccionar_mejor(self, resultados: Dict[str, List[EntidadCandidato]]) -> Tuple[str, List[EntidadCandidato]]:
        """Seleccionar mejor resultado"""
        mejor_metodo = "fallback"
        mejor_score = 0
        mejor_entidades = []
        
        for metodo, entidades in resultados.items():
            score = self.evaluar_calidad(entidades)
            if score > mejor_score:
                mejor_score = score
                mejor_metodo = metodo
                mejor_entidades = entidades
        
        return mejor_metodo, mejor_entidades


class ConsolidadorEntidades:
    """Consolidador de duplicados"""
    
    def consolidar(self, entidades: List[EntidadCandidato]) -> List[EntidadCandidato]:
        """Consolidar entidades duplicadas"""
        if not entidades:
            return []
        
        # Agrupar similares
        grupos = self._agrupar_similares(entidades)
        
        # Consolidar cada grupo
        consolidadas = []
        for grupo in grupos:
            if len(grupo) == 1:
                consolidadas.append(grupo[0])
            else:
                # Seleccionar mejor del grupo
                mejor = max(grupo, key=lambda e: e.confianza)
                mejor.confianza = min(1.0, mejor.confianza + (len(grupo) - 1) * 0.1)
                consolidadas.append(mejor)
        
        return consolidadas
    
    def _agrupar_similares(self, entidades: List[EntidadCandidato]) -> List[List[EntidadCandidato]]:
        """Agrupar entidades similares"""
        grupos = []
        procesadas = set()
        
        for entidad in entidades:
            if id(entidad) in procesadas:
                continue
            
            grupo = [entidad]
            procesadas.add(id(entidad))
            
            for otra in entidades:
                if id(otra) in procesadas:
                    continue
                
                if self._son_similares(entidad, otra):
                    grupo.append(otra)
                    procesadas.add(id(otra))
            
            grupos.append(grupo)
        
        return grupos
    
    def _son_similares(self, e1: EntidadCandidato, e2: EntidadCandidato) -> bool:
        """Verificar si son similares"""
        texto1 = e1.texto.lower().strip()
        texto2 = e2.texto.lower().strip()
        
        # Iguales o uno contiene al otro
        if texto1 == texto2 or texto1 in texto2 or texto2 in texto1:
            return True
        
        # Similitud Jaccard para mismo tipo
        if e1.tipo_sugerido == e2.tipo_sugerido:
            set1 = set(texto1.split())
            set2 = set(texto2.split())
            
            if set1 and set2:
                interseccion = len(set1 & set2)
                union = len(set1 | set2)
                similitud = interseccion / union
                return similitud > 0.6
        
        return False


class MultiLayerNERAvanzado:
    """Sistema principal MultiLayerNER"""
    
    def __init__(self):
        self.logger = obtener_sistema_logging().obtener_sistema_logger()
        
        # Extractores de 4 capas
        self.extractor_spacy = ExtractorSpaCy()
        self.extractor_transformers = ExtractorTransformers()
        self.extractor_patrones = ExtractorPatrones()
        self.validador_semantico = ValidadorSemantico()
        
        # Sistemas de soporte
        self.sistema_fallbacks = SistemaFallbacks()
        self.consolidador = ConsolidadorEntidades()
        
        self.inicializado = False
        self.estadisticas = {"extracciones": 0, "entidades_total": 0, "tiempo_promedio": 0.0}
    
    async def inicializar(self):
        """Inicializar sistema completo"""
        try:
            self.logger.log(NivelSeveridad.INFO, "🚀 Inicializando MultiLayerNER...")
            
            await asyncio.gather(
                self.extractor_spacy.inicializar(),
                self.extractor_transformers.inicializar(),
                return_exceptions=True
            )
            
            self.inicializado = True
            self.logger.log(NivelSeveridad.INFO, "✅ MultiLayerNER inicializado")
            
        except Exception as e:
            self.logger.log(NivelSeveridad.ERROR, f"Error inicializando: {e}")
            raise
    
    async def extraer_entidades_multicapa(self, texto: str) -> ResultadoExtraccion:
        """Extraer entidades con las 4 capas"""
        inicio = time.time()
        
        try:
            if not self.inicializado:
                await self.inicializar()
            
            self.logger.log(NivelSeveridad.INFO, f"Extrayendo entidades ({len(texto)} chars)")
            
            # Ejecutar extractores
            resultados = {}
            
            # Capa 1: spaCy
            entidades_spacy = self.extractor_spacy.extraer_entidades(texto)
            if entidades_spacy:
                resultados["spacy"] = entidades_spacy
            
            # Capa 2: Transformers
            entidades_transformers = self.extractor_transformers.extraer_entidades(texto)
            if entidades_transformers:
                resultados["transformers"] = entidades_transformers
            
            # Capa 3: Patrones
            entidades_patrones = self.extractor_patrones.extraer_entidades(texto)
            if entidades_patrones:
                resultados["patterns"] = entidades_patrones
            
            # Seleccionar mejor resultado
            if resultados:
                metodo_principal, entidades_principales = self.sistema_fallbacks.seleccionar_mejor(resultados)
                
                # Combinar con alta calidad de otros métodos
                todas_entidades = entidades_principales.copy()
                for metodo, entidades in resultados.items():
                    if metodo != metodo_principal:
                        alta_calidad = [e for e in entidades if e.confianza > 0.8]
                        todas_entidades.extend(alta_calidad)
            else:
                # Fallback final
                todas_entidades = self._extraccion_fallback(texto)
                metodo_principal = "fallback"
            
            # Capa 4: Validación semántica
            entidades_validadas = self.validador_semantico.validar_entidades(todas_entidades)
            
            # Consolidar duplicados
            entidades_finales = self.consolidador.consolidar(entidades_validadas)
            
            # Calcular métricas
            tiempo_procesamiento = time.time() - inicio
            calidad = self.sistema_fallbacks.evaluar_calidad(entidades_finales)
            
            # Actualizar estadísticas
            self.estadisticas["extracciones"] += 1
            self.estadisticas["entidades_total"] += len(entidades_finales)
            self.estadisticas["tiempo_promedio"] = (
                (self.estadisticas["tiempo_promedio"] * (self.estadisticas["extracciones"] - 1) + tiempo_procesamiento) /
                self.estadisticas["extracciones"]
            )
            
            resultado = ResultadoExtraccion(
                entidades=entidades_finales,
                estadisticas=self.estadisticas.copy(),
                calidad_general=calidad,
                tiempo_procesamiento=tiempo_procesamiento,
                metodo_principal=metodo_principal
            )
            
            self.logger.log(
                NivelSeveridad.INFO,
                f"Extracción completada: {len(entidades_finales)} entidades, calidad: {calidad:.2f}",
                tiempo=tiempo_procesamiento
            )
            
            return resultado
            
        except Exception as e:
            self.logger.log(NivelSeveridad.ERROR, f"Error en extracción: {e}")
            raise
    
    def _extraccion_fallback(self, texto: str) -> List[EntidadCandidato]:
        """Extracción de fallback básica"""
        entidades = []
        
        # Patrones básicos para nombres propios
        nombres = re.finditer(r'\b[A-ZÁÉÍÓÚ][a-záéíóú]+\b', texto)
        for match in nombres:
            entidad = EntidadCandidato(
                texto=match.group(),
                etiqueta="FALLBACK",
                confianza=0.5,
                inicio=match.start(),
                fin=match.end(),
                contexto=texto[max(0, match.start()-20):match.end()+20],
                tipo_sugerido="characters",
                metodo_extraccion="fallback"
            )
            entidades.append(entidad)
        
        return entidades[:10]  # Limitar a 10 para evitar ruido
    
    def obtener_estadisticas(self) -> Dict[str, float]:
        """Obtener estadísticas del sistema"""
        return self.estadisticas.copy()


# Instancia global
MULTILAYER_NER_GLOBAL = None

def obtener_multilayer_ner() -> MultiLayerNERAvanzado:
    """Obtener instancia global"""
    global MULTILAYER_NER_GLOBAL
    if MULTILAYER_NER_GLOBAL is None:
        MULTILAYER_NER_GLOBAL = MultiLayerNERAvanzado()
    return MULTILAYER_NER_GLOBAL