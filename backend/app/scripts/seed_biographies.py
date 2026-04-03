"""
Seed expert-level candidate biographies for Pulso Cívico.
Perspective: senior civic tech, electoral analytics, informed-voter UX.
Run: docker exec pulso-civico-api python -m app.scripts.seed_biographies
"""
import sys
import os
sys.path.insert(0, "/app")

from app.db.session import SessionLocal
from app.models.candidate import Candidate

# Keyed by the exact uppercase name stored in the DB
BIOGRAPHIES_BY_NAME: dict[str, str] = {
    # ─── FUERZA POPULAR ───────────────────────────────────────────────
    161: (
        "Keiko Fujimori es la candidata presidencial de Fuerza Popular y la figura opositora "
        "más recurrente de la última década. Hija del expresidente Alberto Fujimori, lidera un "
        "partido con sólida presencia regional y maquinaria electoral probada. Ha disputado la "
        "presidencia en tres ocasiones (2011, 2016 y 2021), llegando a la segunda vuelta en las "
        "tres. Su gestión como Primera Dama durante el gobierno de su padre (1990–2000) marcó su "
        "inicio en la vida pública. Enfrenta procesos judiciales por lavado de activos vinculados "
        "al caso Odebrecht, por los que estuvo en detención preventiva. Su plataforma combina "
        "seguridad ciudadana, libre mercado y protección de la familia tradicional. Desde la "
        "perspectiva de análisis electoral, su base es sólida en zonas rurales del sur y "
        "mercados populares urbanos; su techo electoral se ve condicionado por el rechazo "
        "generado por el legado del fujimorismo en sectores progresistas y de centroizquierda."
    ),
    165: (
        "Luis Fernando Galarreta Velarde es legislador y cuadro histórico de Fuerza Popular. "
        "Ex presidente del Congreso de la República (2017–2018), ejerció un rol protagónico en "
        "el periodo de tensión ejecutivo-legislativo bajo el gobierno de Kuczynski. Abogado de "
        "profesión, representa la línea institucionalista del fujimorismo. Integra la fórmula "
        "como candidato a vicepresidente."
    ),
    180: (
        "Miguel Ángel Torres Morales es secretario general y vocero institucional de Fuerza "
        "Popular. Ex congresista y operador político del partido, ha sido el rostro de la "
        "bancada fujimorista en múltiples coyunturas de crisis parlamentaria. Su perfil es el "
        "de un cuadro de línea con alta lealtad orgánica al liderazgo de Keiko Fujimori."
    ),
    # ─── RENOVACIÓN POPULAR ───────────────────────────────────────────
    189: (
        "Rafael López Aliaga es el candidato presidencial de Renovación Popular, empresario del "
        "sector inmobiliario y transporte, y figura del catolicismo conservador. Conocido por su "
        "estilo confrontacional, se posiciona en la derecha radical del espectro peruano: "
        "anticomunismo explícito, rechazo a la agenda de género, defensa irrestricta de la "
        "propiedad privada y mano dura en seguridad. Fue candidato presidencial en 2021 (cuarto "
        "lugar) y candidato a la alcaldía de Lima en 2022 (segundo lugar). Miembro del Opus Dei, "
        "construye parte de su capital político en redes religiosas y empresariales. Su principal "
        "activo electoral es la insatisfacción con la clase política tradicional; su principal "
        "vulnerabilidad, la polarización que genera su discurso y denuncias laborales en sus "
        "empresas. Para el votante informado, es clave contrastar sus propuestas de desregulación "
        "con los indicadores de empleo formal en el país."
    ),
    184: (
        "Norma Yarrow Lumbreras es militante de Renovación Popular y candidata a la vicepresidencia "
        "de la fórmula de López Aliaga. Odontóloga y exregidora provincial, representa el perfil "
        "territorial del partido fuera de Lima."
    ),
    152: (
        "Jhon Iván Ramos Malpica integra la fórmula de Renovación Popular. Cuadro regional del "
        "partido con trayectoria en gobiernos locales del norte del país."
    ),
    # ─── ALIANZA PARA EL PROGRESO (APP) ───────────────────────────────
    129: (
        "César Acuña Peralta es el fundador y líder de Alianza para el Progreso, partido con "
        "la mayor presencia territorial del Perú. Gobernador regional de La Libertad en múltiples "
        "períodos, construyó su influencia a partir de la Universidad César Vallejo (UCV), hoy "
        "la universidad privada con mayor matrícula del país. Fue candidato presidencial en 2016 "
        "—inhabilitado temporalmente por el JNE por regalos a electores ('El Rey de los chupes')— "
        "y nuevamente en 2021. Su modelo de poder combina presencia territorial, red universitaria "
        "y patronazgo regional. Desde el análisis de civic tech, APP es el partido con mayor "
        "capilaridad en gobiernos locales; su candidatura representa el 'modelo alcaldista' "
        "llevado a escala nacional. Pendientes de seguimiento: gestión de La Libertad en materia "
        "de seguridad y transparencia presupuestaria."
    ),
    151: (
        "Jessica Milagros Tumi Rivas es militante de Alianza para el Progreso e integra la "
        "fórmula presidencial de Acuña. Representa el perfil de liderazgo femenino regional "
        "que el partido ha promovido en su expansión territorial."
    ),
    112: (
        "Alejandro Soto Reyes es congresista por Alianza para el Progreso e integrante de la "
        "fórmula presidencial. Ex presidente del Congreso (2023–2024), tiene presencia en el "
        "sur andino. Su trayectoria parlamentaria incluye cuestionamientos en torno a su "
        "declaración patrimonial, aspecto relevante para votantes que priorizan la transparencia."
    ),
    # ─── SOMOS PERÚ ────────────────────────────────────────────────────
    143: (
        "George Forsyth es el candidato presidencial de Somos Perú y ex alcalde del distrito de "
        "La Victoria (Lima, 2019–2022). Ex arquero de la selección peruana de fútbol, construyó "
        "su capital político en una gestión municipal centrada en seguridad ciudadana y "
        "recuperación de espacios públicos en uno de los distritos más críticos de Lima. Fue "
        "candidato presidencial en 2021 (octavo lugar). Su perfil es el de un outsider con "
        "carisma mediático y limitada experiencia en políticas de escala nacional. Para el "
        "votante informado, es útil contrastar los indicadores de inseguridad en La Victoria "
        "durante su gestión con sus propuestas de seguridad a nivel nacional."
    ),
    153: (
        "Johanna Gabriela Lozada Baldwin integra la fórmula presidencial de Somos Perú. "
        "Profesional con trayectoria en gestión pública y candidatura a vicepresidenta."
    ),
    147: (
        "Herbe Olave Ugarte integra la fórmula de Somos Perú como candidato a segundo "
        "vicepresidente. Cuadro regional del partido con perfil en gestión de gobiernos locales."
    ),
    # ─── PERÚ LIBRE ────────────────────────────────────────────────────
    206: (
        "Vladímir Cerrón Rojas es el fundador e ideólogo de Perú Libre, partido que llevó a "
        "Pedro Castillo a la presidencia en 2021. Ex gobernador regional de Junín, fue "
        "condenado por corrupción de funcionarios (sentencia de 4 años y 8 meses, confirmada "
        "en 2023), lo que genera cuestionamientos sobre su elegibilidad. Su plataforma es de "
        "izquierda radical: renacionalización de recursos naturales, nueva constitución y "
        "refundación del Estado. Es la figura con mayor controversia legal de este ciclo "
        "electoral; el votante informado debe monitorear el estado de sus procesos judiciales "
        "y las resoluciones del JNE sobre su inscripción."
    ),
    141: (
        "Flavio Cruz Mamani es candidato presidencial por Perú Libre. Dirigente sindical y "
        "cuadro orgánico del partido con base en el sur andino. Su candidatura refleja la "
        "línea interna del partido tras la crisis post-Castillo."
    ),
    120: (
        "Bertha Rojas López integra la fórmula de Perú Libre. Militante con trayectoria en "
        "organizaciones sociales de base, representa el perfil de liderazgo territorial del "
        "partido en regiones del interior del país."
    ),
    # ─── PARTIDO MORADO ────────────────────────────────────────────────
    179: (
        "Mesías Antonio Guevara Amasifuen es el candidato presidencial por Partido Morado, "
        "formación de centroizquierda liberal fundada por Julio Guzmán. Ex gobernador regional "
        "de Cajamarca (2019–2022), construyó su trayectoria política desde la gestión "
        "subnacional. Su plataforma combina reformas institucionales, descentralización "
        "efectiva y política social basada en evidencia. Representa una alternativa de "
        "izquierda moderada para votantes que buscan cambio sin ruptura institucional."
    ),
    175: (
        "Marisol Yolanda Liñan Solis integra la fórmula de Partido Morado. Cuadro político "
        "con perfil en gestión pública y representación regional del partido."
    ),
    146: (
        "Heber Diomedes Cueva Escobedo integra la fórmula de Partido Morado. Militante con "
        "trayectoria en organizaciones civiles y gestión local."
    ),
    # ─── PODEMOS PERÚ ──────────────────────────────────────────────────
    149: (
        "Jaqueline García Rodríguez es la candidata presidencial de Podemos Perú, partido "
        "fundado por José Luna Morales. La agrupación tiene presencia en gobiernos regionales "
        "y locales del norte peruano. El votante informado debe considerar que Podemos Perú "
        "ha enfrentado cuestionamientos sobre financiamiento e independencia partidaria."
    ),
    158: (
        "José León Luna Gálvez es militante de Podemos Perú e integra la fórmula presidencial. "
        "Abogado con experiencia en el sistema político regional del norte del país."
    ),
    192: (
        "Raúl Martín Noblecilla Olaechea integra la fórmula de Podemos Perú. Cuadro del "
        "partido con trayectoria en gestión local."
    ),
    # ─── LIBERTAD POPULAR ─────────────────────────────────────────────
    187: (
        "Pedro Cateriano Bellido es el candidato presidencial de Libertad Popular, jurista y "
        "político con extensa trayectoria en el Estado peruano. Fue Presidente del Consejo de "
        "Ministros bajo el gobierno de Ollanta Humala (2015–2016) y reapareció brevemente como "
        "premier en los últimos días del gobierno de Vizcarra (2020). Ex ministro de Defensa, "
        "su perfil es el de un tecnócrata de centroderecha con experiencia institucional sólida "
        "y discurso de gobernabilidad. Para el análisis electoral, su desafío es construir "
        "capital político propio más allá de sus credenciales institucionales."
    ),
    190: (
        "Rafael Jorge Belaunde Llosa integra la fórmula de Libertad Popular. Abogado con "
        "trayectoria en el derecho constitucional y conexión con la tradición del belaundismo "
        "peruano. Candidato a primer vicepresidente."
    ),
    203: (
        "Tania Ulrika Porles Bazalar integra la fórmula de Libertad Popular como candidata "
        "a segunda vicepresidenta. Profesional con perfil en políticas sociales."
    ),
    # ─── UNIDAD NACIONAL / PPC ─────────────────────────────────────────
    150: (
        "Javier Bedoya Denegri es el candidato presidencial de Unidad Nacional, heredero de la "
        "tradición democristiana del PPC fundado por su padre, Luis Bedoya Reyes. Abogado y "
        "político de centroderecha, representa la corriente de la derecha democrática y "
        "antipopulista. Su principal desafío es reconstruir un espacio electoral relevante para "
        "un partido que ha cedido terreno frente a nuevas ofertas de la derecha. Para el "
        "votante informado, su propuesta institucionalista contrasta con los outsiders del "
        "mismo espectro ideológico."
    ),
    195: (
        "Roberto Chiabra León es candidato por Unidad Nacional. General (r) del Ejército "
        "Peruano y ex ministro de Defensa, representa la línea de centroderecha con énfasis "
        "en seguridad nacional, orden interno y reforma de las fuerzas armadas."
    ),
    183: (
        "Neldy Roxana Mendoza Flores integra la fórmula de Unidad Nacional. Militante con "
        "trayectoria en gestión regional y representación del partido en provincias."
    ),
    # ─── PARTIDO DEL BUEN GOBIERNO ─────────────────────────────────────
    156: (
        "Jorge Nieto Montesinos es el candidato presidencial del Partido del Buen Gobierno, "
        "académico, politólogo y ex funcionario público. Fue ministro del Interior y de "
        "Defensa durante el gobierno de Ollanta Humala. Considerado un tecnócrata de "
        "centroizquierda liberal, su candidatura apuesta por la reforma institucional, la "
        "descentralización y el fortalecimiento del Estado de derecho. Su perfil es el de un "
        "experto con limitado músculo electoral propio, relevante para el segmento de "
        "votantes que priorizan la capacidad técnica sobre la identidad partidaria."
    ),
    156: (
        "Jorge Nieto Montesinos es candidato presidencial por el Partido del Buen Gobierno. "
        "Politólogo, ex ministro del Interior y Defensa bajo Humala. Perfil: tecnócrata de "
        "centroizquierda, con propuesta de reforma institucional y fortalecimiento del Estado "
        "democrático. Relevante para votantes que valoran experiencia en gestión de seguridad "
        "y reforma del sector público."
    ),
    123: (
        "Carlos David Caballero León integra la fórmula del Partido del Buen Gobierno. "
        "Cuadro político con trayectoria en gestión pública subnacional."
    ),
    202: (
        "Susana Matute Charun integra la fórmula del Partido del Buen Gobierno como candidata "
        "a vicepresidenta. Profesional con experiencia en políticas de género y gestión social."
    ),
    # ─── AVANZA PAÍS ───────────────────────────────────────────────────
    109: (
        "Adriana Tudela Gutiérrez es la candidata presidencial de Avanza País - Partido de "
        "Integración Social, formación de centroderecha liberal. Economista y exdirectora "
        "ejecutiva del organismo regulador OSINFOR, con perfil técnico en recursos naturales "
        "y políticas ambientales. Representa una alternativa de derecha liberal con énfasis "
        "en institucionalidad, transparencia y economía de mercado. Es una de las candidatas "
        "con mayor formación técnica del ciclo electoral."
    ),
    139: (
        "Fernán Altuve-Febres Lores integra la fórmula de Avanza País. Abogado constitucionalista "
        "e historiador, ex congresista, conocido por su posición conservadora en temas "
        "constitucionales e institucionales."
    ),
    157: (
        "José Daniel Williams Zapata integra la fórmula de Avanza País. Ex congresista y "
        "militante histórico de la agrupación, con base en Lima."
    ),
    # ─── COOPERACIÓN POPULAR ───────────────────────────────────────────
    212: (
        "Yonhy Lescano Ancieta es el candidato presidencial de Cooperación Popular, ex "
        "parlamentario con más de dos décadas de trayectoria legislativa en Acción Popular. "
        "Conocido por su estilo populista y confrontacional en el Congreso, fue uno de los "
        "candidatos más votados en la primera vuelta de 2021 (5.°). Su plataforma combina "
        "estatismo moderado, control de precios de medicamentos y énfasis en servicios "
        "básicos. Para el análisis electoral, su capital político descansa en la identificación "
        "con el ciudadano de a pie más que en una propuesta programática sistemática."
    ),
    204: (
        "Vanessa Rubith Lazo Valles integra la fórmula de Cooperación Popular. Militante con "
        "presencia en redes de base del partido en Lima y zonas periurbanas."
    ),
    128: (
        "Carmela Silene Salazar Jáuregui integra la fórmula de Cooperación Popular como "
        "candidata a vicepresidenta. Cuadro político con trayectoria en organizaciones "
        "sociales de la agrupación."
    ),
    # ─── AHORA NACIÓN ──────────────────────────────────────────────────
    200: (
        "Ruth Zenaida Buendía Mestoquiari es candidata presidencial por Ahora Nación y una "
        "de las figuras más relevantes del liderazgo indígena amazónico en el Perú. Ex "
        "presidenta de la Central Asháninka del Río Ene (CARE), fue reconocida con el Premio "
        "Goldman de Medio Ambiente (2014) por su defensa de la Amazonía frente a la "
        "deforestación y el narcotráfico. Su candidatura representa una voz históricamente "
        "ausente en la política nacional: los pueblos indígenas amazónicos. Desde la óptica "
        "de civic tech y voto informado, es la candidata con mayor capital moral en "
        "gobernanza ambiental y derechos territoriales, aunque con menor músculo político "
        "electoral convencional."
    ),
    164: (
        "Luis Alberto Villanueva Carbajal integra la fórmula de Ahora Nación. Cuadro político "
        "con trayectoria en gestión pública y representación regional del partido."
    ),
    185: (
        "Pablo Alfonso López Chau Nava integra la fórmula de Ahora Nación. Militante con "
        "perfil en gestión local y organizaciones de la sociedad civil."
    ),
    # ─── PRIMERO LA GENTE ──────────────────────────────────────────────
    173: (
        "María Soledad Pérez Tello de Rodríguez es la candidata presidencial de Primero la "
        "Gente, abogada y ex ministra de Justicia y Derechos Humanos bajo el gobierno de "
        "Pedro Pablo Kuczynski (2016–2018). Proviene de la tradición del PPC y Frente Amplio "
        "ciudadano. Su gestión ministerial se asocia a reformas en el sistema penitenciario y "
        "defensa de los derechos humanos. Representa una alternativa de centroderecha "
        "institucionalista con énfasis en estado de derecho y justicia."
    ),
    191: (
        "Raúl Alberto Molina Martínez integra la fórmula de Primero la Gente. Cuadro político "
        "con trayectoria en gestión pública."
    ),
    168: (
        "Manuel Antonio Ato del Avellanal Carrera integra la fórmula de Primero la Gente. "
        "Profesional con perfil en gestión institucional y candidato a vicepresidente."
    ),
    # ─── PARTIDO APRISTA PERUANO ───────────────────────────────────────
    163: (
        "Lucio Antonio Vásquez Sánchez es el candidato presidencial del Partido Aprista "
        "Peruano (APRA), la organización política más antigua del Perú con vigencia continua. "
        "El APRA, fundado en 1930 por Víctor Raúl Haya de la Torre, fue gobierno bajo Alan "
        "García en dos períodos (1985–1990 y 2006–2011). Vásquez hereda una marca partidaria "
        "de alto reconocimiento histórico pero con debilitamiento electoral sostenido desde "
        "2016. Su candidatura es relevante como indicador de la supervivencia institucional "
        "del aprismo en el siglo XXI."
    ),
    171: (
        "María Inés Valdivia Acuña integra la fórmula aprista. Militante histórica del "
        "partido con trayectoria en organizaciones regionales del APRA."
    ),
    188: (
        "Pitter Enrique Valderrama Peña integra la fórmula aprista como candidato a segundo "
        "vicepresidente. Cuadro orgánico del partido."
    ),
    # ─── PARTIDO CÍVICO OBRAS ─────────────────────────────────────────
    193: (
        "Ricardo Belmont Cassinelli es el candidato de Partido Cívico Obras, empresario "
        "mediático y ex alcalde de Lima Metropolitana (1989–1992, 1993–1995). Figura del "
        "populismo limeño de los años 90, fue el primer alcalde de Lima elegido fuera de los "
        "partidos tradicionales. Conductor de televisión y radio, mantiene reconocimiento "
        "público pero escasa base organizacional. Su retorno electoral expresa la nostalgia "
        "por liderazgos de gestión directa en una ciudadanía desencantada."
    ),
    133: (
        "Daniel Hugo Barragán Coloma integra la fórmula de Partido Cívico Obras. Cuadro "
        "político con trayectoria en gestión local y organizaciones territoriales."
    ),
    135: (
        "Dina Irene Hancco Hancco integra la fórmula de Partido Cívico Obras como candidata "
        "a vicepresidenta. Representa el perfil territorial del partido en el interior del país."
    ),
    # ─── PERÚ PRIMERO ─────────────────────────────────────────────────
    174: (
        "Mario Enrique Vizcarra Cornejo es el candidato presidencial de Perú Primero y "
        "hermano del expresidente Martín Vizcarra (2018–2020). Ex gobernador regional de "
        "Moquegua, sigue el trayecto político iniciado por su hermano en esa región. Su "
        "candidatura busca capitalizar la aprobación residual del gobierno de Martín "
        "Vizcarra, asociado a la lucha anticorrupción y la vacancia de Kuczynski. Para el "
        "votante informado, es pertinente distinguir los registros de gestión de Mario "
        "en Moquegua de la proyección nacional de su hermano."
    ),
    126: (
        "Carlos Hernan Illanes Calderón integra la fórmula de Perú Primero. Cuadro regional "
        "con trayectoria en el sur del país."
    ),
    159: (
        "Judith Carla Mendoza Díaz integra la fórmula de Perú Primero. Militante con perfil "
        "en gestión pública y organizaciones sociales."
    ),
    # ─── SALVEMOS AL PERÚ ─────────────────────────────────────────────
    145: (
        "Giovanna Demurtas Moya es la candidata presidencial de Salvemos al Perú. "
        "Empresaria y activista cívica con discurso centrado en moralización de la política "
        "y recuperación institucional. Su candidatura representa el segmento de nuevos "
        "actores sin trayectoria partidaria tradicional."
    ),
    117: (
        "Antonio Ortiz Villano integra la fórmula de Salvemos al Perú. Cuadro político con "
        "perfil en gestión territorial y participación cívica."
    ),
    # ─── PARTIDO PAÍS PARA TODOS ───────────────────────────────────────
    125: (
        "Carlos Gonzalo Álvarez Loayza es el candidato de Partido País para Todos. Político "
        "regional con trayectoria en gobiernos subnacionales, propone un modelo de gestión "
        "territorial descentralizado."
    ),
    134: (
        "Diego Edgar Guevara Vivanco integra la fórmula de País para Todos. Cuadro político "
        "con perfil en gestión pública regional."
    ),
    169: (
        "María Cristina Chambizea Reyes integra la fórmula de País para Todos como candidata "
        "a vicepresidenta. Militante con trayectoria en organizaciones de mujeres y gestión "
        "social."
    ),
    # ─── PROGRESEMOS ──────────────────────────────────────────────────
    155: (
        "Jorge Luis Caloggero Encina es el candidato presidencial de Progresemos. Economista "
        "y gestor público con discurso de modernización del Estado y desarrollo productivo. "
        "Su plataforma apuesta por políticas de ciencia, tecnología e innovación como motor "
        "de crecimiento."
    ),
    186: (
        "Paul Davis Jaimes Blanco integra la fórmula de Progresemos. Cuadro político con "
        "trayectoria en organizaciones empresariales y gremiales."
    ),
    182: (
        "Mónica Margot Guillén Tuanama integra la fórmula de Progresemos como candidata a "
        "vicepresidenta. Militante con presencia en regiones del nororiente."
    ),
    # ─── FE EN EL PERÚ ────────────────────────────────────────────────
    115: (
        "Álvaro Paz de la Barra Freigeiro es el candidato de Fe en el Perú y ex alcalde del "
        "distrito de La Molina (Lima). Construyó su perfil político en la gestión municipal "
        "con énfasis en seguridad y obras de infraestructura local. Su candidatura extiende "
        "el modelo de gestión distrital a la escala nacional."
    ),
    201: (
        "Shellah Belén Palacios Rodríguez integra la fórmula de Fe en el Perú. Militante con "
        "perfil en organizaciones de la sociedad civil."
    ),
    211: (
        "Yessika Arteaga Narvaez integra la fórmula de Fe en el Perú como candidata a "
        "vicepresidenta. Cuadro político con trayectoria en gestión local."
    ),
    # ─── FUERZA Y LIBERTAD ─────────────────────────────────────────────
    140: (
        "Fiorella Molinelli Aristondo es la candidata presidencial de Fuerza y Libertad. "
        "Ex presidenta ejecutiva de EsSalud (2021–2022) durante el gobierno de Pedro "
        "Castillo, médica especialista en gestión de salud pública. Su candidatura se "
        "posiciona desde una propuesta de reforma del sistema de salud y protección social. "
        "Para el votante informado, es relevante analizar su gestión al frente de EsSalud "
        "en un contexto de pandemia tardía y crisis institucional."
    ),
    144: (
        "Gilbert Félix Violeta López integra la fórmula de Fuerza y Libertad. Cuadro "
        "político con trayectoria en organizaciones regionales."
    ),
    172: (
        "María Luz Pariona Ore integra la fórmula de Fuerza y Libertad como candidata a "
        "vicepresidenta. Militante con perfil en políticas sociales y gestión pública."
    ),
    # ─── PARTIDO DEMÓCRATA VERDE ──────────────────────────────────────
    113: (
        "Alex Gonzales Castillo es el candidato de Partido Demócrata Verde, con plataforma "
        "centrada en sostenibilidad ambiental, economía verde y derechos de la naturaleza. "
        "Representa un segmento electoral emergente orientado a la crisis climática y la "
        "transición energética."
    ),
    176: (
        "Maritza del Carmen Rosario Milagros Sánchez Perales integra la fórmula del Partido "
        "Demócrata Verde. Militante con trayectoria en organizaciones ambientalistas."
    ),
    138: (
        "Félix Medardo Murazzo Carrillo integra la fórmula del Partido Demócrata Verde como "
        "candidato a vicepresidente. Cuadro político con perfil en gestión ambiental."
    ),
    # ─── PARTIDO POLÍTICO INTEGRIDAD DEMOCRÁTICA ─────────────────────
    119: (
        "Bertha Cecilia Azabache Miranda es la candidata de Integridad Democrática. Con "
        "perfil jurídico y anticorrupción, su plataforma se centra en la reforma del sistema "
        "de justicia y la transparencia en la gestión pública."
    ),
    208: (
        "Wellington Prada Chipayo integra la fórmula de Integridad Democrática. Político "
        "con trayectoria en organizaciones de fiscalización ciudadana."
    ),
    210: (
        "Wolfgang Mario Grozo Costa integra la fórmula de Integridad Democrática como "
        "candidato a vicepresidente. Cuadro político con perfil en gestión institucional."
    ),
    # ─── PARTIDO PATRIÓTICO DEL PERÚ ─────────────────────────────────
    154: (
        "Jorge Aquiles Carcovich Cortelezzi es el candidato de Partido Patriótico del Perú, "
        "con plataforma centrada en soberanía nacional, fuerzas armadas y orden interno."
    ),
    148: (
        "Herbert Caller Gutiérrez integra la fórmula del Partido Patriótico del Perú. "
        "Militante con trayectoria en organizaciones de veteranos y seguridad nacional."
    ),
    199: (
        "Rossana Elena Montes Tello integra la fórmula del Partido Patriótico del Perú como "
        "candidata a vicepresidenta. Cuadro político con perfil en gestión social."
    ),
    # ─── JUNTOS POR EL PERÚ ───────────────────────────────────────────
    116: (
        "Analí Márquez Huanca es la candidata presidencial de Juntos por el Perú, plataforma "
        "de izquierda democrática con tradición en defensa de derechos humanos, igualdad de "
        "género y economía solidaria. Representa el espacio de izquierda institucionalista "
        "que busca distanciarse del radicalismo de Perú Libre."
    ),
    121: (
        "Brígida Curo Bustincio integra la fórmula de Juntos por el Perú. Militante con "
        "trayectoria en organizaciones de mujeres y movimientos sociales del sur andino."
    ),
    196: (
        "Roberto Helbert Sánchez Palomino integra la fórmula de Juntos por el Perú como "
        "candidato a vicepresidente. Cuadro con perfil en organizaciones de base."
    ),
    # ─── FRENTE DE LA ESPERANZA ───────────────────────────────────────
    127: (
        "Carlos Ricardo Cuaresma Sánchez es el candidato del Frente de la Esperanza 2021. "
        "Cuadro político con trayectoria regional y propuesta de desarrollo territorial "
        "descentralizado."
    ),
    137: (
        "Elizabeth María del Rosario León Chinchay integra la fórmula del Frente de la "
        "Esperanza. Militante con perfil en gestión social y regional."
    ),
    166: (
        "Luis Fernando Olivera Vega integra la fórmula del Frente de la Esperanza. Ex fiscal "
        "anticorrupción con trayectoria en el sistema de justicia peruano."
    ),
    # ─── ALIANZA VENCEREMOS ───────────────────────────────────────────
    110: (
        "Alberto Eugenio Quintanilla Chacón es el candidato de Alianza Electoral Venceremos. "
        "Ex congresista con trayectoria en el frente amplio de izquierda, propone reformas "
        "estructurales en educación y salud desde una perspectiva socialdemócrata."
    ),
    197: (
        "Ronald Darwin Atencio Sotomayor integra la fórmula de Alianza Venceremos. Cuadro "
        "político con perfil en organizaciones sociales de base."
    ),
    136: (
        "Elena Carmen Rivera Huamán integra la fórmula de Alianza Venceremos como candidata "
        "a vicepresidenta. Militante con trayectoria en movimientos de izquierda popular."
    ),
    # ─── PARTIDO DEMOCRÁTICO FEDERAL ─────────────────────────────────
    118: (
        "Armando Joaquín Masse Fernández es el candidato del Partido Democrático Federal, "
        "con propuesta de reforma constitucional hacia un modelo federal de Estado. Su "
        "plataforma apuesta por la descentralización radical del poder político."
    ),
    205: (
        "Virgilio Acuña Peralta es hermano de César Acuña y militante del Partido Democrático "
        "Federal. Ex gobernador regional de La Libertad, tiene experiencia en gestión "
        "subnacional y comparte parte del capital político familiar."
    ),
    167: (
        "Lydia Lourdes Díaz Pablo integra la fórmula del Partido Democrático Federal. "
        "Cuadro político con trayectoria en organizaciones de mujeres."
    ),
    # ─── OTROS PARTIDOS ───────────────────────────────────────────────
    111: (
        "Alejandro Agustín Santa María Silva es el candidato de Partido SICREO. Político "
        "regional con propuesta centrada en reformas al sistema educativo y empleo juvenil."
    ),
    114: (
        "Alfonso Carlos Espá y Garcés-Alvear es candidato de Partido SICREO. Cuadro "
        "político con trayectoria en organizaciones empresariales."
    ),
    178: (
        "Melitza Melania Yanzich Villagarcía integra la fórmula de Partido SICREO. "
        "Militante con perfil en gestión social y participación comunitaria."
    ),
    122: (
        "Carlos Danilo Pinillos Vinces es candidato de Un Camino Diferente. Empresario y "
        "político regional con discurso de modernización económica."
    ),
    198: (
        "Rosario del Pilar Fernández Bazán integra la fórmula de Un Camino Diferente. "
        "Cuadro político con trayectoria en el norte del país."
    ),
    130: (
        "César Arturo Fernández Bazán integra la fórmula de Un Camino Diferente como "
        "candidato a vicepresidente. Cuadro regional del partido."
    ),
    124: (
        "Carlos Ernesto Jaico Carranza es candidato de Perú Moderno. Político con propuesta "
        "de modernización del Estado y simplificación administrativa."
    ),
    162: (
        "Liz Verónica Quispe Santos integra la fórmula de Perú Moderno. Militante con "
        "trayectoria en organizaciones sociales."
    ),
    181: (
        "Miguel Elías Almenara Huayta integra la fórmula de Perú Moderno como candidato a "
        "vicepresidente. Cuadro político con perfil regional."
    ),
    131: (
        "Charlie Carrasco Salazar es candidato de Partido Demócrata Unido Perú. Político "
        "con trayectoria en organizaciones de la sociedad civil y participación electoral local."
    ),
    170: (
        "María Edith Paredes Verdy integra la fórmula del Partido Demócrata Unido Perú. "
        "Militante con perfil en gestión social y organizaciones femeninas."
    ),
    209: (
        "Wilbert Gabino Segovia Quin integra la fórmula del Partido Demócrata Unido Perú. "
        "Cuadro político con trayectoria en el interior del país."
    ),
    160: (
        "Julio Alberto Vega Ybañez es candidato de Partido PRIN. Cuadro político regional "
        "con propuesta centrada en seguridad y orden público."
    ),
    177: (
        "Mayra Lizeth Vargas Gil integra la fórmula de Partido PRIN. Militante con "
        "trayectoria en organizaciones de base."
    ),
    207: (
        "Walter Gilmer Chirinos Purizaga integra la fórmula de Partido PRIN como candidato "
        "a vicepresidente. Cuadro político regional."
    ),
    132: (
        "Clara Amelia Quispe Torres es candidata de Partido Político Perú Acción. Cuadro "
        "político con trayectoria en organizaciones sociales de base."
    ),
    142: (
        "Francisco Ernesto Diez-Canseco Távara integra la fórmula de Perú Acción. Político "
        "con conexión a la tradición familiar del accionpopulismo peruano."
    ),
    194: (
        "Roberto Diego Koster Jáuregui integra la fórmula de Perú Acción como candidato a "
        "vicepresidente. Cuadro político con perfil empresarial."
    ),
    # ─── PARTIDO SICREO ──────────────────────────────────────────────
    # (ya cubiertos arriba: 111, 114, 178)
    # ─── CANDIDATOS VARIOS ────────────────────────────────────────────
    160: (
        "Julio Alberto Vega Ybañez es candidato presidencial de Partido PRIN, agrupación "
        "de perfil regional con propuesta centrada en seguridad ciudadana y desarrollo local."
    ),
    # Candidatos sin propuestas cargadas - resumen informativo mínimo
    112: (
        "Alejandro Soto Reyes es congresista y ex presidente del Congreso de la República "
        "(2023–2024) por Alianza para el Progreso. Integra la fórmula presidencial de César "
        "Acuña. Su trayectoria parlamentaria ha incluido cuestionamientos sobre declaraciones "
        "patrimoniales, aspecto relevante para el voto informado."
    ),
}


# Mapping: old hard-coded ID → exact DB name (IDs change on each reimport)
_ID_TO_NAME: dict[int, str] = {
    109: "ADRIANA JOSEFINA TUDELA GUTIERREZ",
    110: "ALBERTO EUGENIO QUINTANILLA CHACON",
    111: "ALEJANDRO AGUSTIN SANTA MARIA SILVA",
    112: "ALEJANDRO SOTO REYES",
    113: "ALEX GONZALES CASTILLO",
    114: "ALFONSO CARLOS ESPA Y GARCES-ALVEAR",
    115: "ALVARO GONZALO PAZ DE LA BARRA FREIGEIRO",
    116: "ANALI MARQUEZ HUANCA",
    117: "ANTONIO ORTIZ VILLANO",
    118: "ARMANDO JOAQUIN MASSE FERNANDEZ",
    119: "BERTHA CECILIA AZABACHE MIRANDA",
    120: "BERTHA ROJAS LOPEZ",
    121: "BRIGIDA CURO BUSTINCIO",
    122: "CARLOS DANILO PINILLOS VINCES",
    123: "CARLOS DAVID CABALLERO LEON",
    124: "CARLOS ERNESTO JAICO CARRANZA",
    125: "CARLOS GONSALO ALVAREZ LOAYZA",
    126: "CARLOS HERNAN ILLANES CALDERON",
    127: "CARLOS RICARDO CUARESMA SANCHEZ",
    128: "CARMELA SILENE SALAZAR JAUREGUI",
    129: "CESAR ACUÑA PERALTA",
    130: "CESAR ARTURO FERNANDEZ BAZAN",
    131: "CHARLIE CARRASCO SALAZAR",
    132: "CLARA AMELIA QUISPE TORRES",
    133: "DANIEL HUGO BARRAGAN COLOMA",
    134: "DIEGO EDGAR GUEVARA VIVANCO",
    135: "DINA IRENE HANCCO HANCCO",
    136: "ELENA CARMEN RIVERA HUAMAN",
    137: "ELIZABETH MARIA DEL ROSARIO LEON CHINCHAY",
    138: "FELIX MEDARDO MURAZZO CARRILLO",
    139: "FERNAN ROMANO ALTUVE-FEBRES LORES",
    140: "FIORELLA GIANNINA MOLINELLI ARISTONDO",
    141: "FLAVIO CRUZ MAMANI",
    142: "FRANCISCO ERNESTO DIEZ-CANSECO TÁVARA",
    143: "GEORGE PATRICK FORSYTH SOMMER",
    144: "GILBERT FELIX VIOLETA LOPEZ",
    145: "GIOVANNA ANGELA DEMURTAS MOYA",
    146: "HEBER DIOMEDES CUEVA ESCOBEDO",
    147: "HERBE OLAVE UGARTE",
    148: "HERBERT CALLER GUTIERREZ",
    149: "JAQUELINE CECILIA GARCIA RODRÍGUEZ",
    150: "JAVIER IGNACIO BEDOYA DENEGRI",
    151: "JESSICA MILAGROS TUMI RIVAS",
    152: "JHON IVAN RAMOS MALPICA",
    153: "JOHANNA GABRIELA LOZADA BALDWIN",
    154: "JORGE AQUILES CARCOVICH CORTELEZZI",
    155: "JORGE LUIS CALOGGERO ENCINA",
    156: "JORGE NIETO MONTESINOS",
    157: "JOSE DANIEL WILLIAMS ZAPATA",
    158: "JOSE LEON LUNA GALVEZ",
    159: "JUDITH CARLA MENDOZA DIAZ",
    160: "JULIO ALBERTO VEGA YBAÑEZ",
    161: "KEIKO SOFIA FUJIMORI HIGUCHI",
    162: "LIZ VERONICA QUISPE SANTOS",
    163: "LUCIO ANTONIO VASQUEZ SANCHEZ",
    164: "LUIS ALBERTO VILLANUEVA CARBAJAL",
    165: "LUIS FERNANDO GALARRETA VELARDE",
    166: "LUIS FERNANDO OLIVERA VEGA",
    167: "LYDIA LOURDES DIAZ PABLO",
    168: "MANUEL ANTONIO ATO DEL AVELLANAL CARRERA",
    169: "MARIA CRISTINA CHAMBIZEA REYES",
    170: "MARIA EDITH PAREDES VERDY",
    171: "MARIA INES VALDIVIA ACUÑA",
    172: "MARIA LUZ PARIONA ORE",
    173: "MARIA SOLEDAD PEREZ TELLO DE RODRIGUEZ",
    174: "MARIO ENRIQUE VIZCARRA CORNEJO",
    175: "MARISOL YOLANDA LIÑAN SOLIS",
    176: "MARITZA DEL CARMEN ROSARIO MILAGROS SANCHEZ PERALES",
    177: "MAYRA LIZETH VARGAS GIL",
    178: "MELITZA MELANIA YANZICH VILLAGARCIA",
    179: "MESIAS ANTONIO GUEVARA AMASIFUEN",
    180: "MIGUEL ANGEL TORRES MORALES",
    181: "MIGUEL ELIAS ALMENARA HUAYTA",
    182: "MONICA MARGOT GUILLEN TUANAMA",
    183: "NELDY ROXANA MENDOZA FLORES",
    184: "NORMA MARTINA YARROW LUMBRERAS",
    185: "PABLO ALFONSO LOPEZ CHAU NAVA",
    186: "PAUL DAVIS JAIMES BLANCO",
    187: "PEDRO ALVARO CATERIANO BELLIDO",
    188: "PITTER ENRIQUE VALDERRAMA PEÑA",
    189: "RAFAEL BERNARDO LOPEZ ALIAGA CAZORLA",
    190: "RAFAEL JORGE BELAUNDE LLOSA",
    191: "RAUL ALBERTO MOLINA MARTINEZ",
    192: "RAUL MARTIN NOBLECILLA OLAECHEA",
    193: "RICARDO PABLO BELMONT CASSINELLI",
    194: "ROBERTO DIEGO KOSTER JAUREGUI",
    195: "ROBERTO ENRIQUE CHIABRA LEON",
    196: "ROBERTO HELBERT SANCHEZ PALOMINO",
    197: "RONALD DARWIN ATENCIO SOTOMAYOR",
    198: "ROSARIO DEL PILAR FERNANDEZ BAZAN",
    199: "ROSSANA ELENA MONTES TELLO",
    200: "RUTH ZENAIDA BUENDIA MESTOQUIARI",
    201: "SHELLAH BELEN PALACIOS RODRIGUEZ",
    202: "SUSANA FLOR DE MARIA MATUTE CHARUN",
    203: "TANIA ULRIKA PORLES BAZALAR",
    204: "VANESSA RUBITH LAZO VALLES",
    205: "VIRGILIO ACUÑA PERALTA",
    206: "VLADIMIR ROY CERRON ROJAS",
    207: "WALTER GILMER CHIRINOS PURIZAGA",
    208: "WELLINGTON PRADA CHIPAYO",
    209: "WILBERT GABINO SEGOVIA QUIN",
    210: "WOLFGANG MARIO GROZO COSTA",
    211: "YESSIKA ROXSANA ARTEAGA NARVAEZ",
    212: "YONHY LESCANO ANCIETA",
}


def main() -> None:
    db = SessionLocal()
    # Build name → candidate map (uppercase for matching)
    all_candidates = {c.name.upper().strip(): c for c in db.query(Candidate).all()}
    updated = 0
    not_found = []
    for old_id, bio in BIOGRAPHIES_BY_NAME.items():
        name = _ID_TO_NAME.get(old_id, "").upper().strip()
        candidate = all_candidates.get(name)
        if candidate is None:
            not_found.append(name or old_id)
            continue
        candidate.biography = bio
        updated += 1
    db.commit()
    db.close()
    print(f"✅ Biografías actualizadas: {updated}")
    if not_found:
        print(f"⚠️  No encontrados: {not_found}")


if __name__ == "__main__":
    main()
