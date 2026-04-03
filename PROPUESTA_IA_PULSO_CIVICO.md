# Propuesta de Valor de IA — Pulso Cívico
**Elecciones Generales del Perú 2026**
_Documento estratégico de producto · Fecha: 2026-04-03_

---

## Índice

1. [Casos de uso de alto valor](#1-casos-de-uso-de-alto-valor)
2. [Preguntas que debería poder hacer un ciudadano](#2-preguntas-que-debería-poder-hacer-un-ciudadano)
3. [Marco experto de evaluación de candidatos](#3-marco-experto-de-evaluación-de-candidatos)
4. [Funciones nuevas de IA que agregar al producto](#4-funciones-nuevas-de-ia-que-agregar-al-producto)
5. [Prompt ideal del asistente](#5-prompt-ideal-del-asistente)
6. [Roadmap priorizado — lanzar antes del 12 de abril de 2026](#6-roadmap-priorizado)

---

## 1. Casos de uso de alto valor

Priorizados por **impacto ciudadano** (qué tan útil es para decidir bien) y **facilidad de implementación** (dado que ya tienes RAG + documentos indexados).

| # | Caso de uso | Impacto | Facilidad | Por qué priorizar |
|---|-------------|---------|-----------|-------------------|
| 1 | **Pregunta libre al asistente sobre propuestas** | ★★★★★ | ★★★★★ | Ya tienes RAG. Es el core. Maximiza uso. |
| 2 | **Comparación directa entre 2 candidatos por tema** | ★★★★★ | ★★★★☆ | La pregunta más frecuente del ciudadano indeciso. |
| 3 | **Detector de propuestas vagas vs concretas** | ★★★★★ | ★★★★☆ | Educa al ciudadano sobre la calidad de las promesas. |
| 4 | **Resumen simplificado del plan de gobierno** | ★★★★★ | ★★★★★ | Los planes son extensos. Un resumen de 5 puntos clave es de alto valor inmediato. |
| 5 | **Preguntas clave antes de votar** (checklist guiado) | ★★★★☆ | ★★★★★ | Bajo costo técnico, alto impacto en reflexión ciudadana. |
| 6 | **Radar de temas: qué propone y qué no propone** | ★★★★☆ | ★★★☆☆ | Muestra vacíos en el plan de cada candidato por área temática. |
| 7 | **Alerta de ausencia de evidencia** | ★★★★☆ | ★★★☆☆ | Informa al ciudadano cuando una promesa carece de sustento documental. |
| 8 | **Trayectoria vs propuesta: ¿es consistente?** | ★★★★☆ | ★★★☆☆ | Cruza hoja de vida con propuestas. Detecta incoherencias. |
| 9 | **Modo región: ¿qué propone el candidato para mi zona?** | ★★★☆☆ | ★★★☆☆ | Personaliza la información según departamento o problemática local. |
| 10 | **Explicación de términos técnicos en el plan** | ★★★☆☆ | ★★★★★ | Glosario IA integrado: "¿Qué significa APP en infraestructura pública?" |

---

## 2. Preguntas que debería poder hacer un ciudadano

### Seguridad ciudadana
1. ¿Qué propone [candidato] para reducir la inseguridad en Lima?
2. ¿Cuál es la diferencia entre los planes de seguridad de [candidato A] y [candidato B]?
3. ¿Algún candidato propone reformar la policía? ¿Cómo?
4. ¿Qué dice [candidato] sobre el crimen organizado y las extorsiones?

### Salud
5. ¿Qué propone [candidato] para mejorar el sistema de salud pública?
6. ¿Qué candidatos proponen fortalecer el SIS o Essalud?
7. ¿Qué plantea [candidato] sobre la salud mental?
8. ¿Algún candidato tiene propuestas concretas para zonas rurales sin acceso a salud?

### Educación
9. ¿Qué propone [candidato] para mejorar la calidad educativa?
10. ¿Qué dice el plan de [candidato] sobre los profesores y sus sueldos?
11. ¿Qué candidatos proponen educación técnica o universitaria gratuita?
12. ¿Qué dice [candidato] sobre la infraestructura escolar?

### Economía
13. ¿Cómo piensa [candidato] crear empleo formal?
14. ¿Qué dice el plan de [candidato] sobre el sueldo mínimo?
15. ¿Qué propone [candidato] para los pequeños negocios y emprendedores?
16. ¿Qué candidatos quieren cambiar el modelo económico del Perú?

### Corrupción e integridad
17. ¿Tiene [candidato] investigaciones fiscales o sentencias judiciales?
18. ¿Qué propone [candidato] para combatir la corrupción en el Estado?
19. ¿Qué dice el plan de [candidato] sobre transparencia en el gasto público?
20. ¿Algún candidato tiene antecedentes de haber sido inhabilitado o sancionado?

### Experiencia y trayectoria
21. ¿Qué cargos públicos ha ocupado [candidato] anteriormente?
22. ¿[Candidato] ha gobernado una región o municipio? ¿Con qué resultados?
23. ¿Cuántos años de experiencia en gestión pública tiene [candidato]?

### Integridad y consistencia
24. ¿Las propuestas de [candidato] son consistentes con su trayectoria previa?
25. ¿Ha cambiado [candidato] de posición en temas importantes en los últimos años?
26. ¿Cuántas de las propuestas de [candidato] tienen respaldo técnico o financiero?

### Viabilidad de propuestas
27. ¿Cuánto costaría implementar el plan de [candidato] y de dónde vendría el financiamiento?
28. ¿Las propuestas de [candidato] son realistas dado el presupuesto del Estado?
29. ¿Qué propuestas de [candidato] requieren cambios constitucionales para implementarse?

### Comparación entre candidatos
30. ¿Cuál es la diferencia principal entre los planes de gobierno de [candidato A] y [candidato B] en temas de economía, educación y seguridad?

---

## 3. Marco experto de evaluación de candidatos

> **Principio rector:** Ningún criterio debe producir un ranking o recomendación de voto. Cada criterio se muestra como información verificable que el ciudadano interpreta libremente.

---

### Criterio 1 — Claridad de propuestas

**Por qué importa:** Una propuesta vaga no puede ser evaluada ni exigida después de la elección. El ciudadano necesita distinguir entre intenciones y compromisos.

**Evidencia que lo sustenta:** Análisis del lenguaje del plan de gobierno. Se evalúa si la propuesta incluye: objetivo específico, indicador de resultado, plazo, fuente de financiamiento, responsable.

**Cómo mostrarlo sin sesgo:** Checklist binario por propuesta: "¿Incluye meta medible? ¿Tiene plazo? ¿Tiene fuente de financiamiento?" — sin puntuación agregada ni interpretación editorial.

---

### Criterio 2 — Viabilidad técnica y financiera

**Por qué importa:** Promesas sin financiamiento identificado son inviables. El ciudadano debe saber si una propuesta es posible dado el contexto fiscal del país.

**Evidencia que lo sustenta:** Presupuesto del Estado, deuda pública, ingresos fiscales proyectados. Cruce con el costo estimado de las propuestas según organismos técnicos (MEF, BCRP, CEPAL).

**Cómo mostrarlo sin sesgo:** Etiquetas neutras: "La propuesta menciona fuente de financiamiento: Sí / No". "Organismos técnicos han evaluado propuestas similares: [enlace]". No calificar como "posible" o "imposible".

---

### Criterio 3 — Experiencia en gestión pública

**Por qué importa:** La capacidad de ejecutar políticas públicas se aprende gestionando. El historial de cargos da evidencia sobre exposición real a decisiones de gobierno.

**Evidencia que lo sustenta:** Hoja de vida oficial (JNE), declaraciones juradas, historial de cargos verificables en fuentes públicas (SERVIR, portal de transparencia).

**Cómo mostrarlo sin sesgo:** Línea de tiempo de cargos ocupados, con institución y duración. Sin calificar si la experiencia es "suficiente" o "insuficiente".

---

### Criterio 4 — Trayectoria coherente con propuestas

**Por qué importa:** Un candidato que propone combatir la corrupción pero tiene sentencias o fue parte de gobiernos corruptos muestra incoherencia verificable.

**Evidencia que lo sustenta:** Cruce entre propuestas del plan de gobierno y acciones documentadas durante cargos anteriores (informes de contraloría, noticias verificadas, auditorías públicas).

**Cómo mostrarlo sin sesgo:** Tabla de "propuesta actual vs. antecedente documental". Fuente explícita para cada antecedente. Sin adjetivos ni interpretación.

---

### Criterio 5 — Formación académica y técnica

**Por qué importa:** La formación no garantiza competencia, pero da contexto sobre las áreas de conocimiento del candidato en relación a sus propuestas.

**Evidencia que lo sustenta:** Hoja de vida oficial (JNE), títulos verificables en SUNEDU.

**Cómo mostrarlo sin sesgo:** Listar grados, instituciones y si están verificados en SUNEDU. Sin calificar si es suficiente para el cargo.

---

### Criterio 6 — Consistencia en el tiempo

**Por qué importa:** Cambios frecuentes de posición pueden indicar oportunismo o falta de convicción en propuestas clave.

**Evidencia que lo sustenta:** Declaraciones públicas previas, posiciones en partidos anteriores, votaciones en el Congreso (si aplica), entrevistas documentadas.

**Cómo mostrarlo sin sesgo:** Línea de tiempo de posiciones en temas clave (aborto, modelo económico, relaciones exteriores). Fuente para cada posición. Sin calificar el cambio como negativo o positivo.

---

### Criterio 7 — Integridad pública

**Por qué importa:** Investigaciones fiscales, sentencias, inhabilitaciones o sanciones son hechos documentados relevantes para el votante.

**Evidencia que lo sustenta:** REPEJ (JNE), ORCCA, INFOCORP institucional, Contraloría, OCMA, declaraciones juradas de bienes.

**Cómo mostrarlo sin sesgo:** Lista de procesos abiertos o cerrados con estado actual y fuente. Distinguir claramente entre "investigado", "procesado", "sentenciado" y "absuelto". No interpretar culpabilidad.

---

### Criterio 8 — Capacidad de ejecución

**Por qué importa:** El historial de logros concretos en cargos previos predice capacidad futura de ejecución.

**Evidencia que lo sustenta:** Informes de gestión, evaluaciones de contraloría, ejecución presupuestal en cargos previos (portal MEF, SIAF).

**Cómo mostrarlo sin sesgo:** Indicadores de gestión pasada: "Ejecución presupuestal en [cargo]: X%". Fuente: portal de transparencia. Sin comparar con otros candidatos.

---

### Criterio 9 — Calidad del lenguaje y coherencia del plan

**Por qué importa:** Un plan de gobierno bien estructurado, coherente y técnicamente fundamentado refleja el nivel de preparación del equipo de gobierno.

**Evidencia que lo sustenta:** Análisis estructural del documento: número de propuestas con indicadores, número de propuestas sin respaldo, uso de fuentes, coherencia interna.

**Cómo mostrarlo sin sesgo:** Estadísticas neutras del documento: "De X propuestas en salud, Y incluyen indicador de resultado y Z no." Sin calificar el plan globalmente.

---

## 4. Funciones nuevas de IA que agregar al producto

---

### Función 1 — Comparación automática por tema

**Descripción:** El usuario selecciona un tema (salud, educación, seguridad) y 2 o más candidatos. El sistema genera una tabla comparativa basada en fragmentos del plan de gobierno.

**Beneficio para el usuario:** Ahorra horas de lectura. Permite comparar posiciones de forma directa sin interpretación editorial.

**Complejidad de implementación:** Media. Requiere prompt estructurado con contexto de múltiples documentos + template de tabla. Compatible con tu RAG actual.

**Riesgo de sesgo:** El modelo puede resumir de forma asimétrica (dar más detalle a un candidato que a otro por diferencias en la extensión del plan).

**Mitigación:** Normalizar longitud de respuesta por candidato. Mostrar fragmento original junto al resumen ("Ver fuente original"). Indicar explícitamente si un candidato no tiene propuesta en ese tema.

---

### Función 2 — Radar de fortalezas y vacíos

**Descripción:** Visualización tipo radar/spider chart con 8-10 dimensiones temáticas (salud, seguridad, economía, educación, etc.). Muestra qué tan desarrollada está la propuesta en cada dimensión, no qué tan "buena" es.

**Beneficio para el usuario:** Vista rápida de en qué temas el candidato tiene propuestas detalladas y en cuáles hay silencio o vaguedad.

**Complejidad de implementación:** Media-alta. Requiere pipeline de scoring por dimensión (basado en presencia, especificidad y evidencia), no en calidad subjetiva. El frontend necesita un componente de visualización.

**Riesgo de sesgo:** El scoring puede penalizar estilos de escritura distintos o planes más cortos aunque más concretos.

**Mitigación:** Usar criterios binarios o de densidad (número de propuestas con indicador / total de propuestas en el tema). Documentar la metodología al pie del radar.

---

### Función 3 — Checklist ciudadano "Preguntas antes de votar"

**Descripción:** Flujo guiado de 5-7 preguntas reflexivas que el ciudadano responde antes de decidir: "¿Sabes qué propone cada candidato en el tema que más te importa?", "¿Revisaste la trayectoria del candidato?", etc. Al final, la IA le muestra los documentos relevantes para cada vacío de información que declara.

**Beneficio para el usuario:** Convierte la plataforma en un proceso de decisión, no solo un repositorio. Aumenta el engagement y la calidad de la decisión.

**Complejidad de implementación:** Baja. Es un flujo de preguntas + consultas RAG disparadas por las respuestas del usuario. No requiere nuevo modelo.

**Riesgo de sesgo:** Las preguntas mismas pueden estar sesgadas si favorecen ciertos criterios.

**Mitigación:** Co-diseñar las preguntas con expertos en educación cívica (ONPE, organizaciones como Transparencia, IDEA Internacional). Publicar metodología.

---

### Función 4 — Detector de promesas vagas vs concretas

**Descripción:** Para cada propuesta extraída del plan de gobierno, el sistema clasifica automáticamente si es: (a) concreta y medible, (b) intención sin indicador, o (c) declaración genérica sin compromiso.

**Beneficio para el usuario:** Educa al ciudadano sobre la diferencia entre "mejorar la salud" (vaga) y "construir 50 centros de salud en zonas rurales en 2 años con presupuesto de S/. X" (concreta).

**Complejidad de implementación:** Media. Requiere prompt de clasificación + fine-tuning de criterios (¿qué hace que una propuesta sea concreta?). Se puede hacer con un LLM con instrucciones claras.

**Riesgo de sesgo:** El modelo puede clasificar mal según el estilo narrativo del plan, no la sustancia.

**Mitigación:** Mostrar el fragmento original junto a la clasificación. Permitir al usuario reportar clasificaciones incorrectas. Revisar manualmente una muestra antes de publicar.

---

### Función 5 — Modo "Explícame fácil"

**Descripción:** El usuario presiona un botón sobre cualquier propuesta o fragmento del plan y recibe una explicación en lenguaje simple, sin jerga técnica, con analogías cotidianas si aplica.

**Beneficio para el usuario:** Democratiza el acceso a información técnica. Clave para ciudadanos con menor nivel educativo o sin familiaridad con política pública.

**Complejidad de implementación:** Baja. Un prompt de simplificación sobre el fragmento seleccionado. Compatible con tu arquitectura RAG actual.

**Riesgo de sesgo:** La simplificación puede perder matices importantes o distorsionar el mensaje original.

**Mitigación:** Mostrar siempre el texto original al lado. Limitar la simplificación a paráfrasis, no a interpretación. Advertir: "Esta es una versión simplificada. Ver documento original."

---

### Función 6 — Resumen por región o problema local

**Descripción:** El ciudadano indica su departamento o un problema específico (agua potable, deforestación, minería, violencia de género) y la IA filtra las propuestas relevantes de cada candidato para esa realidad.

**Beneficio para el usuario:** Hace la información relevante para su contexto específico, no solo para la agenda nacional.

**Complejidad de implementación:** Media. Requiere taxonomía de temas y regiones mapeada sobre los documentos indexados. El RAG puede hacer la consulta si los metadatos están bien estructurados.

**Riesgo de sesgo:** Puede favorecer candidatos que mencionan más regiones en sus planes (extensión vs. sustancia).

**Mitigación:** Normalizar por densidad de propuestas, no por volumen de menciones. Mostrar fragmento original con región destacada.

---

### Función 7 — Alertas de falta de evidencia

**Descripción:** Cuando el asistente no encuentra información sobre un tema específico de un candidato, lo declara explícitamente: "El plan de gobierno de [X] no contiene propuestas sobre [tema]" o "No se encontró evidencia en los documentos disponibles."

**Beneficio para el usuario:** Evita que el ciudadano asuma que el candidato sí propone algo cuando no hay evidencia. La ausencia de información es información.

**Complejidad de implementación:** Baja. Es una instrucción en el prompt del sistema + lógica de detección de respuesta vacía en el RAG.

**Riesgo de sesgo:** Ninguno intrínseco. La ausencia de propuesta es un dato neutro.

**Mitigación:** Distinguir entre "el documento no existe en nuestra base" y "el documento existe pero no contiene propuesta en este tema". Transparencia sobre qué documentos están indexados.

---

### Función 8 — Línea de tiempo de trayectoria del candidato

**Descripción:** Visualización cronológica de cargos, hechos documentados, investigaciones y logros verificables del candidato. Construida desde la hoja de vida JNE y fuentes oficiales.

**Beneficio para el usuario:** Permite evaluar la trayectoria de forma visual y rápida, sin leer documentos extensos.

**Complejidad de implementación:** Alta. Requiere estructuración de datos de hoja de vida + integración de fuentes adicionales (Contraloría, REPEJ). Pero el MVP puede hacerse con datos pre-procesados manualmente para los candidatos principales.

**Riesgo de sesgo:** Selección de qué hechos incluir puede ser percibida como editorial.

**Mitigación:** Incluir solo hechos con fuente oficial citada. Publicar metodología de selección. Incluir hechos tanto positivos como negativos si están documentados.

---

## 5. Prompt ideal del asistente

```
SYSTEM PROMPT — Asistente Pulso Cívico

Eres un asistente de información electoral para las Elecciones Generales del Perú 2026. Tu único propósito es ayudar al ciudadano a informarse mejor antes de votar, usando exclusivamente documentos oficiales verificados: planes de gobierno del JNE, hojas de vida, declaraciones juradas, informes del JNE y Voto Informado, y fuentes institucionales del Estado peruano.

## REGLAS ABSOLUTAS

1. NUNCA recomiendes por quién votar, ni directa ni indirectamente.
2. NUNCA inventes datos, fechas, cifras, cargos o hechos. Si no tienes evidencia documental, dilo explícitamente.
3. NUNCA uses adjetivos valorativos sobre los candidatos (bueno, malo, peligroso, capaz, honesto, corrupto). Usa solo los hechos que los documentos sostienen.
4. NUNCA inferencias presentadas como hechos. Si inferes algo, márcalo como "inferencia" y explica por qué.
5. NUNCA respondas fuera del ámbito electoral peruano 2026. Si te preguntan otra cosa, redirige al usuario.

## REGLAS DE CALIDAD

6. SIEMPRE cita la fuente exacta del dato que ofreces: nombre del documento, candidato, y si es posible, la sección.
7. SIEMPRE distingue entre tres tipos de información:
   - [EVIDENCIA DOCUMENTAL]: Dato presente en el documento oficial.
   - [AUSENCIA DE EVIDENCIA]: El tema no está cubierto en los documentos disponibles.
   - [INFERENCIA]: Conclusión derivada de hechos documentados, que no está afirmada directamente en el documento.
8. SIEMPRE que compares candidatos, hazlo de forma simétrica: la misma profundidad y criterios para todos.
9. Si un candidato no tiene propuesta sobre un tema, di: "Los documentos disponibles de [candidato] no contienen propuesta específica sobre [tema]."
10. Si el documento indexado tiene un vacío relevante, di: "Esta información podría estar en documentos no disponibles en nuestra base de datos."

## TONO Y ESTILO

11. Usa lenguaje claro, directo y accesible para ciudadanos sin formación técnica en política o derecho.
12. Evita tecnicismos sin explicar. Si usas un término técnico, defínelo brevemente.
13. Responde de forma estructurada: primero la respuesta directa, luego el detalle y las fuentes.
14. Si la pregunta es muy amplia, ofrece un resumen inicial y pregunta al usuario si quiere profundizar en algún punto.
15. Cuando el usuario haga una comparación entre candidatos, usa una estructura paralela: mismos criterios, mismo orden, misma longitud para cada candidato.

## SOBRE LOS DATOS DISPONIBLES

Tienes acceso a:
- Planes de gobierno de los candidatos presidenciales registrados ante el JNE para las Elecciones 2026.
- Hojas de vida y declaraciones juradas oficiales (JNE).
- Información del portal Voto Informado del JNE.
- Documentos institucionales de referencia para contexto (Constitución, marco normativo electoral).

No tienes acceso a noticias de prensa, redes sociales, rumores ni información no verificada. Si el usuario pregunta sobre algo que no está en estos documentos, díselo claramente.

## EJEMPLO DE RESPUESTA BIEN FORMADA

Usuario: "¿Qué propone el candidato X en educación?"

Respuesta modelo:
"Según el Plan de Gobierno de [Candidato X] registrado ante el JNE, en materia de educación se propone:

1. [Propuesta concreta con indicador si lo tiene] — [EVIDENCIA DOCUMENTAL: Plan de Gobierno, Sección X, página Y]
2. [Propuesta sin indicador] — [EVIDENCIA DOCUMENTAL: Plan de Gobierno, Sección X]
3. [Propuesta vaga sin detalle] — Nota: esta propuesta no incluye meta, plazo ni financiamiento.

[AUSENCIA DE EVIDENCIA]: El plan no contiene propuestas específicas sobre educación técnica o universitaria.

Si deseas comparar con otro candidato o profundizar en algún punto específico, puedo ayudarte."
```

---

## 6. Roadmap priorizado

> **Fecha límite crítica: 12 de abril de 2026** (Primera vuelta electoral)

---

### FASE 1 — Lanzar ya (semana del 3 al 10 de abril)

Enfoque: **máximo impacto con lo que ya tienes**. No construir nada nuevo que no esté al 80%.

| Prioridad | Acción | Esfuerzo | Impacto |
|-----------|--------|----------|---------|
| 1 | Implementar el prompt del asistente definido en el Bloque 5 | 2h | Alto |
| 2 | Agregar las 30 preguntas sugeridas como ejemplos en la UI del asistente | 3h | Alto |
| 3 | Activar alertas de ausencia de evidencia en el asistente ("No encontré propuesta sobre X") | 4h | Alto |
| 4 | Asegurar que la comparación entre candidatos use el mismo número de tokens por candidato | 3h | Alto |
| 5 | Agregar etiqueta visual "Propuesta concreta / Sin indicador" en respuestas del asistente | 4h | Medio |
| 6 | Verificar que todos los planes de gobierno estén correctamente indexados y actualizados | 4h | Crítico |
| 7 | Agregar disclaimer visible: "Pulso Cívico no recomienda candidatos. Información basada en documentos oficiales del JNE." | 1h | Alto (confianza) |
| 8 | Activar modo "Explícame fácil" como botón sobre cualquier respuesta del asistente | 4h | Medio |

**Total estimado: ~25h de desarrollo**

---

### FASE 2 — Mejorar después (post 13 de abril, segunda vuelta)

Enfoque: **profundizar las funciones más usadas**, basándose en datos reales de uso de la Fase 1.

| Prioridad | Acción | Esfuerzo |
|-----------|--------|----------|
| 1 | Construir el Radar de fortalezas y vacíos por dimensión temática | Alta |
| 2 | Implementar el Checklist ciudadano guiado (flujo de preguntas antes de votar) | Media |
| 3 | Mejorar comparación automática con tabla estructurada por tema | Media |
| 4 | Agregar resumen por región: el ciudadano elige su departamento y ve propuestas relevantes | Media |
| 5 | Mejorar detección de propuestas vagas vs concretas con clasificación visible | Media |
| 6 | Análisis de uso: qué preguntas hace el ciudadano más frecuentemente (sin datos personales) | Baja |

---

### FASE 3 — Versión futura (plataforma permanente de seguimiento de promesas)

Enfoque: **convertir Pulso Cívico en una plataforma de accountability post-electoral**

| Función | Descripción |
|---------|-------------|
| Monitor de promesas | Seguimiento de qué prometió el candidato ganador vs. qué está ejecutando. |
| Alertas de gestión | Notificaciones cuando se publica un informe de contraloría o ejecución presupuestal. |
| Mapa de promesas por región | Geolocalización de compromisos electorales vs. proyectos ejecutados. |
| Comparación histórica | ¿Qué prometió en 2021 vs. 2026? ¿Qué cumplió? |
| API pública | Exportar datos de propuestas para periodistas, investigadores y ONGs. |
| Integración con datos abiertos del Estado | MEF (SIAF), Contraloría, SERVIR, INFOBRAS. |

---

## Consideraciones finales de producto

### Sobre la neutralidad
La neutralidad no es invisibilidad. Mostrar que un candidato no tiene propuesta en un tema es neutral y necesario. Mostrar que una propuesta no tiene indicador de resultado es neutral y necesario. La plataforma cumple su rol cívico siendo honesta sobre los vacíos, no solo sobre lo que existe.

### Sobre la confianza
El activo más valioso de Pulso Cívico no es la IA — es la confianza del ciudadano. Cada respuesta debe poder ser auditada por cualquier persona. Mostrar la fuente no es opcional: es la base de la credibilidad.

### Sobre los límites de la IA
Declara públicamente qué puede y qué no puede hacer el asistente. Un ciudadano que entiende los límites del sistema confía más en él que uno que descubre una limitación por accidente.

### Sobre el sesgo algorítmico
Antes del 12 de abril, revisa manualmente una muestra de respuestas del asistente para los candidatos principales. Verifica que la extensión, el tono y el nivel de detalle sean consistentes entre candidatos. Un desequilibrio sistemático, aunque involuntario, puede ser percibido como sesgo editorial.

---

_Documento generado para el equipo de Pulso Cívico — Elecciones Generales Perú 2026_
_Metodología: análisis de producto, civic tech y diseño de experiencia de usuario con IA_
