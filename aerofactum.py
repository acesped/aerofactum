# -*- coding: utf-8 -*-
"""
AEROFACTUM UNIVERSAL 8.4 · CURIOSITY ENGINE · GitHub Actions + YouTube @aerofactum · MOTOR ORIGINAL MISTERIO CIENCIA · UNA SOLA CELDA DE COLAB / PYTHON
Motor audiovisual original de MISTERIO CIENCIA adaptado a 100 temas aeronáuticos,
Ken Burns cinematográfico, voz Edge TTS, subtítulos ASS y música cinematográfica original sintetizada con Python.
IA Gemini/Groq con niveles gratuitos sujetos a cupos. CPU. Sin fotografías inventadas por IA. Para relatos de terror se admiten ilustraciones originales procedurales debidamente identificadas.

Ejecución: python aerofactum.py. En GitHub Actions, ejecución cron automatizada.
"""
import os,sys,subprocess,importlib.util,random,re,json,math,time,asyncio,threading,html,shutil,wave,hashlib
from pathlib import Path
from urllib.parse import urlparse
from datetime import datetime, timezone

# ==================== CONFIGURACIÓN EDITABLE ====================
NICHO = "Datos de la Industria Aeronáutica"  # CAMBIAR SOLO ESTA LÍNEA: p. ej. "Astronomía", "Historia", "Océanos"
TEMA = os.getenv('AERO_TEMA', 'aleatorio')       # caso específico o 'aleatorio'; por defecto no repite episodios
VOZ = 'es-CL-LorenzoNeural'  # voz fija para TODOS los segmentos de narración
VELOCIDAD = os.getenv('AERO_VELOCIDAD_VOZ', '-5%').strip()  # Lorenzo más pausado; configurable en GitHub Variables
if not re.fullmatch(r'[+-]?(?:[0-9]|[1-9][0-9]|100)%', VELOCIDAD):
    raise ValueError('AERO_VELOCIDAD_VOZ debe ser porcentaje válido, por ejemplo -5%')
# Español siempre con Lorenzo; nunca cambiar la voz para términos en inglés.
VOZ_INGLES = os.getenv('AERO_VOZ_INGLES', 'en-US-AndrewNeural').strip()
# La pronunciación inglesa se puede desactivar si se prefiere una sola voz.
PRONUNCIACION_INGLES = False  # voz única Lorenzo en TODOS los fragmentos
SUBTITULOS_ADELANTO = max(0.0,min(0.65,float(os.getenv('AERO_SUBTITULOS_ADELANTO','0.28'))))  # segundos; antes que la voz
SALIDA_EN_DRIVE = os.getenv('GITHUB_ACTIONS', '').lower() != 'true'
CREAR_VISTA_PREVIA = os.getenv('AERO_PREVIEW', 'false').lower() == 'true'      # True = solo miniatura + fotogramas de muestra, sin TTS
VIDEOS_POR_EJECUCION = int(os.getenv('AERO_VIDEOS_POR_EJECUCION', '1'))       # 1 por defecto; hasta 100 temas únicos
EVITAR_REPETICIONES = True     # requiere historial en Drive para persistir entre sesiones
REINICIAR_CATALOGO_AL_AGOTAR = False
FOTOGRAMAS_POR_SEGUNDO = 15
ANCHO, ALTO = 1920, 1080        # render nativo Full HD para exportación 1080p real
IMAGENES_MINIMAS = max(2,min(10,int(os.getenv('AERO_IMAGENES_MINIMAS','4'))))  # mínimo editorial, configurable
IMAGENES_MINIMAS_ABSOLUTAS = 1 # mínimo para crear borradores privados; publicación no privada exige IMAGENES_MINIMAS
MAX_IMAGENES = 10
AERO_PALABRAS_MIN = max(235, min(900, int(os.getenv("AERO_PALABRAS_MIN", "440"))))
# El objetivo editorial no es una barrera rígida. Un mínimo absoluto separado
# evita gastar cuotas para añadir relleno a un guion sustancial y verificado.
AERO_PALABRAS_MIN_ACEPTABLE = max(112, min(AERO_PALABRAS_MIN, int(os.getenv("AERO_PALABRAS_MIN_ABSOLUTO", "235"))))
AERO_PALABRAS_MAX = min(1200, max(AERO_PALABRAS_MIN+80, int(os.getenv("AERO_PALABRAS_MAX", "780"))))
AERO_COLA_DIR = Path(os.getenv("AERO_COLA_DIR", "state/pendientes_youtube"))
VERIFICACION_OBLIGATORIA = False # si True, detiene cuando no hay referencias oficiales accesibles
OUTPUT_BASE = Path(os.getenv('AERO_OUTPUT_DIR', '/content/AEROFACTUM' if Path('/content').exists() else 'output/AEROFACTUM'))
# Guion investigado: Gemini -> Groq -> OpenRouter. Nunca usar plantillas si fallan.
AERO_IA_MODO = os.getenv('AERO_IA_MODO', 'auto').strip().lower()
GEMINI_MODELO = os.getenv('GEMINI_MODELO', 'gemini-3.8-flash')
GROQ_MODELO = os.getenv('GROQ_MODELO', 'openai/gpt-oss-120b')
OPENROUTER_MODELO = os.getenv('OPENROUTER_MODELO', 'openrouter/free').strip()
# Evitar que los modelos reasoning consuman toda la salida antes del JSON.
AERO_OPENROUTER_RAZONAMIENTO = os.getenv('AERO_OPENROUTER_RAZONAMIENTO', 'minimal').strip().lower()
if AERO_OPENROUTER_RAZONAMIENTO not in ('none','minimal','low','medium'):
    raise ValueError('AERO_OPENROUTER_RAZONAMIENTO: none, minimal, low o medium')
AERO_OPENROUTER_MAX_TOKENS = max(4000, min(16000, int(os.getenv('AERO_OPENROUTER_MAX_TOKENS', '11000'))))
# La búsqueda web OpenRouter puede generar cargos; habilitar solo con consentimiento explícito.
AERO_OPENROUTER_WEB_SEARCH = os.getenv('AERO_OPENROUTER_WEB_SEARCH', 'false').strip().lower() == 'true'
AERO_IA_MIN_FUENTES = max(1, int(os.getenv('AERO_IA_MIN_FUENTES', '1')))
AERO_IA_MIN_DATOS = max(2, int(os.getenv('AERO_IA_MIN_DATOS', '3')))
AERO_APLAZAR_SIN_IA = os.getenv('AERO_APLAZAR_SIN_IA','true').lower() == 'true'
AERO_IA_DRY_RUN = os.getenv('AERO_IA_DRY_RUN', 'false').lower() == 'true'
AERO_INVESTIGACION_WEB = os.getenv('AERO_INVESTIGACION_WEB', 'auto').strip().lower()  # auto, gemini, groq, openrouter, ambas, todas, off
AERO_BUSQUEDA_MAX_URLS = max(3,min(24,int(os.getenv('AERO_BUSQUEDA_MAX_URLS','12'))))
AERO_IA_URLS = os.getenv('AERO_IA_URLS', '').strip()  # URLs propias, separadas por |, opcionales
# INVESTIGACIÓN UNIVERSAL 5.0 · todo reside en este archivo Python.
AERO_INVESTIGACION_UNIVERSAL = os.getenv('AERO_INVESTIGACION_UNIVERSAL','true').lower() == 'true'
AERO_PRIORIZAR_FUENTES_PRIMARIAS = True
AERO_INDEXAR_PDF = os.getenv('AERO_INDEXAR_PDF','true').lower() == 'true'
AERO_CACHE_DOCUMENTAL = os.getenv('AERO_CACHE_DOCUMENTAL','true').lower() == 'true'
AERO_CACHE_DIR = Path(os.getenv('AERO_CACHE_DIR','state/aero_documentos'))
AERO_CACHE_DIAS = max(1,int(os.getenv('AERO_CACHE_DIAS','45')))
AERO_CACHE_VERSION = 5  # relevancia financiera específica y extracción mejorada
VERSION_SCRIPT = "8.4"
AERO_GUIONES_DIR = Path(os.getenv("AERO_GUIONES_DIR", "state/aero_guiones"))
AERO_GUIONES_DIAS = max(1, min(30, int(os.getenv("AERO_GUIONES_DIAS", "14"))))
AERO_MAX_DOCUMENTOS = max(1,min(8,int(os.getenv('AERO_MAX_DOCUMENTOS','4'))))
AERO_MIN_FUENTES = max(1,int(os.getenv('AERO_MIN_FUENTES',str(AERO_IA_MIN_FUENTES))))
AERO_MIN_HECHOS_VERIFICABLES = max(2,int(os.getenv('AERO_MIN_HECHOS_VERIFICABLES',str(AERO_IA_MIN_DATOS))))
AERO_CAMBIAR_TEMA_SI_FALLA = os.getenv('AERO_CAMBIAR_TEMA_SI_FALLA','true').lower() == 'true'
AERO_MAX_TEMAS_POR_EJECUCION = max(1,min(100,int(os.getenv('AERO_MAX_TEMAS_POR_EJECUCION','5'))))
AERO_REINTENTOS_POR_FUENTE = max(0,min(3,int(os.getenv('AERO_REINTENTOS_POR_FUENTE','1'))))
AERO_IA_MAX_FUENTES_PROMPT = max(1,min(3,int(os.getenv('AERO_IA_MAX_FUENTES_PROMPT','2'))))
AERO_IA_CARACTERES_FUENTE = max(1400,min(5000,int(os.getenv('AERO_IA_CARACTERES_FUENTE','3200'))))
AERO_IA_TIMEOUT = max(25,min(180,int(os.getenv('AERO_IA_TIMEOUT','75'))))
AERO_IA_CITAS_PRESELECCIONADAS = max(3,min(15,int(os.getenv('AERO_IA_CITAS_PRESELECCIONADAS','9'))))
AERO_PERMITIR_CAMBIO_TEMA_EXPLICITO = os.getenv('AERO_PERMITIR_CAMBIO_TEMA_EXPLICITO','false').lower() == 'true'
AERO_IA_MIN_DATOS = max(AERO_IA_MIN_DATOS,AERO_MIN_HECHOS_VERIFICABLES)
# Banda sonora cinematográfica original. Sin servicios externos ni bibliotecas musicales.
# Volumen en escala lineal (0.045 equivale aproximadamente a -27 dBFS de pico para el pad).
MUSICA_VOLUMEN = max(0.0, min(0.20, float(os.getenv('AERO_MUSICA_VOLUMEN', '0.095'))))
MUSICA_TEMPO = max(60, min(110, int(os.getenv('AERO_MUSICA_BPM', '76'))))
MUSICA_DUCKING = max(0.20, min(1.0, float(os.getenv('AERO_MUSICA_DUCKING', '0.55'))))

# =================== AEROFACTUM VIRAL 7.0 ===================
# Un solo archivo, compatible con el workflow anterior. Estas puntuaciones son
# controles editoriales, no predicciones de viralidad ni métricas de YouTube.
MODO_VIRAL = os.getenv('AERO_MODO_VIRAL', 'true').lower() == 'true'
GANCHO_INMEDIATO = os.getenv('AERO_GANCHO_INMEDIATO', 'true').lower() == 'true'
GUION_NARRATIVO_DINAMICO = os.getenv('AERO_GUION_NARRATIVO', 'true').lower() == 'true'
IMAGENES_POR_ESCENA = os.getenv('AERO_IMAGENES_POR_ESCENA', 'true').lower() == 'true'
AERO_VISUALES_OBJETIVO = max(4,min(10,int(os.getenv('AERO_VISUALES_OBJETIVO','8'))))
TITULOS_CANDIDATOS = max(1,min(3,int(os.getenv('AERO_TITULOS_CANDIDATOS','3'))))
MINIATURAS_CANDIDATAS = max(1,min(3,int(os.getenv('AERO_MINIATURAS_CANDIDATAS','3'))))
PREGUNTA_FINAL_ESPECIFICA = os.getenv('AERO_PREGUNTA_FINAL','true').lower() == 'true'
GENERAR_SHORT_DERIVADO = os.getenv('AERO_GENERAR_SHORT','false').lower() == 'true'
GENERAR_SERIES_TEMATICAS = os.getenv('AERO_GENERAR_SERIES','true').lower() == 'true'
ANALIZAR_YOUTUBE_ANALYTICS = os.getenv('AERO_ANALYTICS','false').lower() == 'true'
HISTORIAL_RENDIMIENTO = os.getenv('AERO_HISTORIAL_RENDIMIENTO','true').lower() == 'true'
# Los Shorts son archivos locales opcionales; NUNCA se suben solos.
AERO_SHORT_DURACION_MAX = max(20,min(59,int(os.getenv('AERO_SHORT_DURACION_MAX','55'))))
# Declaración de uso de IA en YouTube: automática y basada en el contenido.
# "No" para fotografías no alteradas e ilustraciones evidentemente ficticias.
# "Sí" si se incluyen escenas sintéticas realistas, personas reales manipuladas,
# eventos reales alterados, o música generada que sea el foco principal.
# Variables opcionales: AERO_AI_ESCENAS_REALISTAS=true, AERO_AI_PERSONAS_REALES=true,
# AERO_AI_EVENTOS_REALES=true, AERO_AI_MUSICA_PRINCIPAL=true.



LIKE_PAGE_URL = 'https://commons.wikimedia.org/wiki/File:Facebook_Like_button.svg'
LIKE_SVG_URL = 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Facebook_Like_button.svg'
# =================================================================

# ================== CATÁLOGO AERONÁUTICO ==================
# Cada ficha tiene un tema diferente; no se reciclan tres episodios del mismo tema.
# Referencias de categoría son bibliografía para revisión, NO una validación automática de datos.
DATOS_AERONAUTICOS = [{'id': 'aero_01', 'categoria': 'AERODINÁMICA', 'titulo': 'Por qué vuela un avión', 'idea': 'La sustentación depende del flujo de aire, la forma del ala y las condiciones de vuelo.', 'imagenes': ['aircraft wing in flight', 'aircraft wing in flight']}, {'id': 'aero_02', 'categoria': 'AERODINÁMICA', 'titulo': 'El ángulo de ataque explicado', 'idea': 'El ángulo de ataque describe la orientación del perfil respecto del flujo de aire relativo.', 'imagenes': ['aircraft wing airflow', 'aircraft wing airflow']}, {'id': 'aero_03', 'categoria': 'AERODINÁMICA', 'titulo': 'Qué provoca una pérdida aerodinámica', 'idea': 'Una pérdida ocurre cuando el ala supera el ángulo de ataque crítico, no por una velocidad fija universal.', 'imagenes': ['aircraft stall training', 'aircraft stall training']}, {'id': 'aero_04', 'categoria': 'AERODINÁMICA', 'titulo': 'Por qué existen los flaps', 'idea': 'Los flaps modifican características de sustentación y resistencia para distintas fases de vuelo.', 'imagenes': ['aircraft landing flaps', 'aircraft landing flaps']}, {'id': 'aero_05', 'categoria': 'AERODINÁMICA', 'titulo': 'Qué hacen los slats', 'idea': 'Los dispositivos del borde de ataque ayudan a gestionar el flujo de aire a altos ángulos de ataque.', 'imagenes': ['aircraft leading edge slats', 'aircraft leading edge slats']}, {'id': 'aero_06', 'categoria': 'AERODINÁMICA', 'titulo': 'La resistencia inducida', 'idea': 'La generación de sustentación produce una componente de resistencia especialmente relevante a velocidades menores.', 'imagenes': ['wingtip vortex aircraft', 'wingtip vortex airplane']}, {'id': 'aero_07', 'categoria': 'AERODINÁMICA', 'titulo': 'Por qué existen los winglets', 'idea': 'Los dispositivos de punta alar pueden mejorar la eficiencia aerodinámica en determinadas condiciones de diseño.', 'imagenes': ['winglets airplane', 'winglets airplane']}, {'id': 'aero_08', 'categoria': 'AERODINÁMICA', 'titulo': 'Centro de presión y estabilidad', 'idea': 'La distribución de fuerzas aerodinámicas interactúa con el centro de gravedad y los momentos de cabeceo.', 'imagenes': ['aircraft wing in flight photograph', 'aircraft wing in flight photograph']}, {'id': 'aero_09', 'categoria': 'AERODINÁMICA', 'titulo': 'Efecto suelo durante el aterrizaje', 'idea': 'La proximidad al suelo altera la interacción entre el ala, el flujo de aire y la resistencia inducida.', 'imagenes': ['airliner landing runway', 'airliner landing runway']}, {'id': 'aero_10', 'categoria': 'AERODINÁMICA', 'titulo': 'Mach y vuelo transónico', 'idea': 'La compresibilidad del aire transforma el comportamiento aerodinámico cuando aparecen regiones de flujo cercano a la velocidad del sonido.', 'imagenes': ['transonic aircraft wing', 'transonic airplane wing']}, {'id': 'motor_01', 'categoria': 'MOTORES Y SISTEMAS', 'titulo': 'Cómo trabaja un turbofán', 'idea': 'Un turbofán combina el empuje del flujo del ventilador con el de la parte central del motor.', 'imagenes': ['turbofan jet engine', 'turbofan jet engine']}, {'id': 'motor_02', 'categoria': 'MOTORES Y SISTEMAS', 'titulo': 'El compresor de un reactor', 'idea': 'El compresor aumenta la presión del aire antes del proceso de combustión.', 'imagenes': ['jet engine compressor', 'jet engine compressor']}, {'id': 'motor_03', 'categoria': 'MOTORES Y SISTEMAS', 'titulo': 'El papel de la turbina', 'idea': 'La turbina extrae energía de los gases para accionar componentes del motor.', 'imagenes': ['jet engine turbine', 'jet engine turbine']}, {'id': 'motor_04', 'categoria': 'MOTORES Y SISTEMAS', 'titulo': 'Qué significa bypass ratio', 'idea': 'La relación de derivación compara el caudal que pasa por el ventilador con el que atraviesa el núcleo.', 'imagenes': ['high bypass turbofan', 'high bypass turbofan']}, {'id': 'motor_05', 'categoria': 'MOTORES Y SISTEMAS', 'titulo': 'Cómo funciona un turbohélice', 'idea': 'Una turbina de gas transmite potencia a una hélice que genera gran parte del empuje.', 'imagenes': ['turboprop aircraft engine', 'turboprop airplane engine']}, {'id': 'motor_06', 'categoria': 'MOTORES Y SISTEMAS', 'titulo': 'Sistemas hidráulicos del avión', 'idea': 'Los sistemas hidráulicos transmiten potencia para accionar diferentes equipos según el diseño de la aeronave.', 'imagenes': ['aircraft hydraulic landing gear', 'aircraft hydraulic landing gear']}, {'id': 'motor_07', 'categoria': 'MOTORES Y SISTEMAS', 'titulo': 'Por qué se presuriza la cabina', 'idea': 'La presurización mantiene condiciones de cabina más adecuadas durante vuelos a gran altitud.', 'imagenes': ['airliner cabin interior', 'airliner cabin interior']}, {'id': 'motor_08', 'categoria': 'MOTORES Y SISTEMAS', 'titulo': 'Sistema eléctrico de una aeronave', 'idea': 'Generadores, baterías, buses y protecciones distribuyen energía a los equipos del avión.', 'imagenes': ['aircraft avionics electrical', 'aircraft avionics electrical']}, {'id': 'motor_09', 'categoria': 'MOTORES Y SISTEMAS', 'titulo': 'Qué hace el APU', 'idea': 'La unidad auxiliar de potencia puede aportar energía eléctrica y aire neumático según el tipo de aeronave.', 'imagenes': ['aircraft auxiliary power unit', 'aircraft auxiliary power unit']}, {'id': 'motor_10', 'categoria': 'MOTORES Y SISTEMAS', 'titulo': 'El tren de aterrizaje por dentro', 'idea': 'El tren absorbe cargas y permite desplazarse en tierra, con mecanismos distintos según cada modelo.', 'imagenes': ['aircraft landing gear closeup', 'aircraft landing gear closeup']}, {'id': 'nav_01', 'categoria': 'INSTRUMENTOS Y NAVEGACIÓN', 'titulo': 'Velocidad indicada frente a velocidad real', 'idea': 'La velocidad indicada y la verdadera representan magnitudes distintas y requieren contexto atmosférico.', 'imagenes': ['aircraft airspeed indicator', 'aircraft airspeed indicator']}, {'id': 'nav_02', 'categoria': 'INSTRUMENTOS Y NAVEGACIÓN', 'titulo': 'Cómo funciona el altímetro', 'idea': 'El altímetro barométrico estima altitud mediante presión y un ajuste adecuado.', 'imagenes': ['aircraft altimeter', 'aircraft altimeter']}, {'id': 'nav_03', 'categoria': 'INSTRUMENTOS Y NAVEGACIÓN', 'titulo': 'Horizonte artificial y actitud', 'idea': 'El indicador de actitud ayuda a representar la orientación del avión respecto al horizonte.', 'imagenes': ['aircraft attitude indicator', 'aircraft attitude indicator']}, {'id': 'nav_04', 'categoria': 'INSTRUMENTOS Y NAVEGACIÓN', 'titulo': 'Qué es el sistema pitot estático', 'idea': 'El sistema utiliza tomas de presión para alimentar diversos instrumentos de vuelo.', 'imagenes': ['aircraft pitot tube', 'aircraft pitot tube']}, {'id': 'nav_05', 'categoria': 'INSTRUMENTOS Y NAVEGACIÓN', 'titulo': 'Qué informa el transpondedor', 'idea': 'El transpondedor facilita la identificación y vigilancia según sus capacidades y configuración.', 'imagenes': ['aircraft transponder cockpit', 'aircraft transponder cockpit']}, {'id': 'nav_06', 'categoria': 'INSTRUMENTOS Y NAVEGACIÓN', 'titulo': 'Cómo guía una señal ILS', 'idea': 'Un ILS proporciona referencias de guiado lateral y vertical en aproximaciones equipadas.', 'imagenes': ['instrument landing system airport', 'instrument landing system airport']}, {'id': 'nav_07', 'categoria': 'INSTRUMENTOS Y NAVEGACIÓN', 'titulo': 'Navegación por VOR', 'idea': 'Las ayudas VOR ofrecen información de radiales respecto a una estación terrestre.', 'imagenes': ['VOR navigation station', 'VOR navigation station']}, {'id': 'nav_08', 'categoria': 'INSTRUMENTOS Y NAVEGACIÓN', 'titulo': 'GPS y navegación aérea', 'idea': 'La navegación por satélite debe utilizarse de acuerdo con equipos aprobados, procedimientos y limitaciones.', 'imagenes': ['aircraft GPS cockpit', 'aircraft GPS cockpit']}, {'id': 'nav_09', 'categoria': 'INSTRUMENTOS Y NAVEGACIÓN', 'titulo': 'Qué es la navegación RNAV', 'idea': 'RNAV permite volar trayectorias definidas mediante ayudas o sensores apropiados.', 'imagenes': ['airliner glass cockpit', 'airliner glass cockpit']}, {'id': 'nav_10', 'categoria': 'INSTRUMENTOS Y NAVEGACIÓN', 'titulo': 'Qué es RNP y por qué importa', 'idea': 'RNP añade requisitos de monitoreo y alerta de performance de navegación a ciertas operaciones.', 'imagenes': ['airliner navigation display', 'airliner navigation display']}, {'id': 'meteo_01', 'categoria': 'METEOROLOGÍA', 'titulo': 'Cómo leer un METAR', 'idea': 'Un METAR resume observaciones meteorológicas aeronáuticas de un aeródromo.', 'imagenes': ['aviation weather station', 'aviation weather station']}, {'id': 'meteo_02', 'categoria': 'METEOROLOGÍA', 'titulo': 'Qué contiene un TAF', 'idea': 'El TAF proporciona pronósticos de condiciones meteorológicas para un aeródromo y un periodo especificado.', 'imagenes': ['airport thunderstorm clouds', 'airport thunderstorm clouds']}, {'id': 'meteo_03', 'categoria': 'METEOROLOGÍA', 'titulo': 'La amenaza de la cizalladura', 'idea': 'La cizalladura es un cambio de viento que puede afectar la trayectoria y energía del avión.', 'imagenes': ['wind shear storm airport', 'wind shear storm airport']}, {'id': 'meteo_04', 'categoria': 'METEOROLOGÍA', 'titulo': 'Por qué el hielo cambia el vuelo', 'idea': 'La acumulación de hielo puede alterar la aerodinámica y el funcionamiento de sistemas.', 'imagenes': ['aircraft wing icing', 'aircraft wing icing']}, {'id': 'meteo_05', 'categoria': 'METEOROLOGÍA', 'titulo': 'Qué es una tormenta convectiva', 'idea': 'Las tormentas convectivas combinan movimientos verticales fuertes y diversos peligros para el vuelo.', 'imagenes': ['cumulonimbus thunderstorm aviation', 'cumulonimbus thunderstorm aviation']}, {'id': 'meteo_06', 'categoria': 'METEOROLOGÍA', 'titulo': 'Turbulencia en aire claro', 'idea': 'La turbulencia puede aparecer fuera de nubes visibles y requiere interpretación meteorológica.', 'imagenes': ['commercial aircraft clouds', 'commercial airplane clouds']}, {'id': 'meteo_07', 'categoria': 'METEOROLOGÍA', 'titulo': 'Cómo se forman los vientos en altura', 'idea': 'Las diferencias de presión y temperatura contribuyen a grandes patrones de circulación atmosférica.', 'imagenes': ['jet stream satellite map', 'jet stream satellite map']}, {'id': 'meteo_08', 'categoria': 'METEOROLOGÍA', 'titulo': 'Por qué importa el punto de rocío', 'idea': 'La cercanía entre temperatura y punto de rocío ayuda a evaluar condiciones de humedad y niebla.', 'imagenes': ['fog airport runway', 'fog airport runway']}, {'id': 'meteo_09', 'categoria': 'METEOROLOGÍA', 'titulo': 'Niebla y visibilidad operacional', 'idea': 'La visibilidad y el techo de nubes condicionan operaciones conforme a mínimos aplicables.', 'imagenes': ['fog airport aircraft', 'fog airport airplane']}, {'id': 'meteo_10', 'categoria': 'METEOROLOGÍA', 'titulo': 'Qué son los NOTAM meteorológicos', 'idea': 'Los avisos operacionales y los productos meteorológicos cumplen funciones diferentes y deben consultarse por separado.', 'imagenes': ['airport weather briefing', 'airport weather briefing']}, {'id': 'ops_01', 'categoria': 'OPERACIONES DE VUELO', 'titulo': 'Qué significa V1', 'idea': 'V1 es una velocidad de decisión de despegue definida para condiciones y procedimientos específicos.', 'imagenes': ['airliner takeoff runway', 'airliner takeoff runway']}, {'id': 'ops_02', 'categoria': 'OPERACIONES DE VUELO', 'titulo': 'Qué significa VR', 'idea': 'VR indica la velocidad asociada al inicio de la rotación durante el despegue.', 'imagenes': ['airplane rotation takeoff', 'airplane rotation takeoff']}, {'id': 'ops_03', 'categoria': 'OPERACIONES DE VUELO', 'titulo': 'Qué significa V2', 'idea': 'V2 es una velocidad de seguridad de despegue utilizada bajo criterios de performance aplicables.', 'imagenes': ['commercial jet climb', 'commercial jet climb']}, {'id': 'ops_04', 'categoria': 'OPERACIONES DE VUELO', 'titulo': 'Cómo se calcula el peso y balance', 'idea': 'El peso total y la posición del centro de gravedad deben permanecer dentro de límites aprobados.', 'imagenes': ['aircraft weight balance loading', 'aircraft weight balance loading']}, {'id': 'ops_05', 'categoria': 'OPERACIONES DE VUELO', 'titulo': 'Por qué se calcula el combustible', 'idea': 'La planificación de combustible contempla misión, reservas y contingencias según normas aplicables.', 'imagenes': ['aircraft fuel truck apron', 'aircraft fuel truck apron']}, {'id': 'ops_06', 'categoria': 'OPERACIONES DE VUELO', 'titulo': 'Qué es la distancia de aterrizaje', 'idea': 'La performance de aterrizaje depende de factores como peso, pista, viento, configuración y condiciones.', 'imagenes': ['airliner runway landing', 'airliner runway landing']}, {'id': 'ops_07', 'categoria': 'OPERACIONES DE VUELO', 'titulo': 'La importancia de la pista contaminada', 'idea': 'Agua, nieve, hielo y otros contaminantes afectan frenado y performance en pista.', 'imagenes': ['wet runway airliner', 'wet runway airliner']}, {'id': 'ops_08', 'categoria': 'OPERACIONES DE VUELO', 'titulo': 'Para qué sirve una checklist', 'idea': 'Las listas de comprobación estructuran acciones y reducen omisiones en tareas críticas.', 'imagenes': ['pilot cockpit checklist', 'pilot cockpit checklist']}, {'id': 'ops_09', 'categoria': 'OPERACIONES DE VUELO', 'titulo': 'Cómo funciona un briefing de salida', 'idea': 'Un briefing establece expectativas y coordinación antes de fases exigentes del vuelo.', 'imagenes': ['airline pilots cockpit preflight', 'airline pilots cockpit preflight']}, {'id': 'ops_10', 'categoria': 'OPERACIONES DE VUELO', 'titulo': 'Qué es una aproximación estabilizada', 'idea': 'Los criterios de estabilización ayudan a evaluar si es seguro continuar una aproximación.', 'imagenes': ['aircraft final approach', 'aircraft final approach']}, {'id': 'safe_01', 'categoria': 'SEGURIDAD Y FACTOR HUMANO', 'titulo': 'Qué es CRM en aviación', 'idea': 'CRM busca mejorar coordinación, comunicación, decisiones y uso de recursos entre tripulantes.', 'imagenes': ['airline pilots cockpit', 'airline pilots cockpit']}, {'id': 'safe_02', 'categoria': 'SEGURIDAD Y FACTOR HUMANO', 'titulo': 'El peligro de la fatiga', 'idea': 'La fatiga puede degradar atención, rendimiento y toma de decisiones en aviación.', 'imagenes': ['pilot cockpit night', 'pilot cockpit night']}, {'id': 'safe_03', 'categoria': 'SEGURIDAD Y FACTOR HUMANO', 'titulo': 'La conciencia situacional', 'idea': 'La conciencia situacional implica percibir y comprender lo que ocurre y anticipar su evolución.', 'imagenes': ['air traffic control radar', 'air traffic control radar']}, {'id': 'safe_04', 'categoria': 'SEGURIDAD Y FACTOR HUMANO', 'titulo': 'Qué es TEM en vuelo', 'idea': 'Threat and Error Management propone reconocer amenazas y gestionar errores y estados no deseados.', 'imagenes': ['pilot briefing aircraft cockpit', 'pilot briefing airplane cockpit']}, {'id': 'safe_05', 'categoria': 'SEGURIDAD Y FACTOR HUMANO', 'titulo': 'Por qué importa una cultura justa', 'idea': 'Una cultura justa distingue errores humanos de conductas que requieren tratamiento diferente.', 'imagenes': ['aviation safety meeting', 'aviation safety meeting']}, {'id': 'safe_06', 'categoria': 'SEGURIDAD Y FACTOR HUMANO', 'titulo': 'Qué es un SMS aeronáutico', 'idea': 'Un sistema de gestión de seguridad organiza procesos de identificación y tratamiento de riesgos.', 'imagenes': ['airport safety operations', 'airport safety operations']}, {'id': 'safe_07', 'categoria': 'SEGURIDAD Y FACTOR HUMANO', 'titulo': 'Cómo se analiza un incidente', 'idea': 'Las investigaciones buscan identificar factores contribuyentes y mejoras de seguridad.', 'imagenes': ['aircraft safety investigation', 'aircraft safety investigation']}, {'id': 'safe_08', 'categoria': 'SEGURIDAD Y FACTOR HUMANO', 'titulo': 'Qué es la carga de trabajo del piloto', 'idea': 'La distribución de tareas y la automatización influyen en el manejo de la carga de trabajo.', 'imagenes': ['pilot cockpit work', 'pilot cockpit work']}, {'id': 'safe_09', 'categoria': 'SEGURIDAD Y FACTOR HUMANO', 'titulo': 'Peligros de la desorientación espacial', 'idea': 'La percepción humana puede ser engañosa durante maniobras o condiciones visuales degradadas.', 'imagenes': ['aircraft instrument flight cockpit', 'aircraft instrument flight cockpit']}, {'id': 'safe_10', 'categoria': 'SEGURIDAD Y FACTOR HUMANO', 'titulo': 'Por qué importa el go-around', 'idea': 'La maniobra de aproximación frustrada es una opción normal de gestión del riesgo cuando corresponde.', 'imagenes': ['airliner go around', 'airliner go around']}, {'id': 'fin_01', 'categoria': 'FINANZAS Y ECONOMÍA', 'titulo': 'Por qué volar cuesta tanto', 'idea': 'La operación aérea combina costos fijos y variables, y su rentabilidad depende de utilización e ingresos.', 'imagenes': ['airline commercial aircraft fleet', 'airline commercial airplane fleet']}, {'id': 'fin_02', 'categoria': 'FINANZAS Y ECONOMÍA', 'titulo': 'Qué es CASK', 'idea': 'CASK relaciona costos operativos con la capacidad ofrecida medida en asientos-kilómetro disponibles.', 'imagenes': ['airline aircraft seats interior', 'airline airplane seats interior']}, {'id': 'fin_03', 'categoria': 'FINANZAS Y ECONOMÍA', 'titulo': 'Qué es RASK', 'idea': 'RASK compara ingresos operativos con asientos-kilómetro disponibles y ayuda a evaluar desempeño comercial.', 'imagenes': ['airport passenger terminal', 'airport passenger terminal']}, {'id': 'fin_04', 'categoria': 'FINANZAS Y ECONOMÍA', 'titulo': 'Qué es el factor de ocupación', 'idea': 'El factor de ocupación mide qué proporción de la capacidad ofrecida viaja efectivamente ocupada.', 'imagenes': ['aircraft passenger seats cabin', 'aircraft passenger seats cabin']}, {'id': 'fin_05', 'categoria': 'FINANZAS Y ECONOMÍA', 'titulo': 'Por qué el combustible pesa en las cuentas', 'idea': 'El combustible es un componente significativo y volátil de los costos de muchas aerolíneas.', 'imagenes': ['jet fuel aircraft refueling', 'jet fuel airplane refueling']}, {'id': 'fin_06', 'categoria': 'FINANZAS Y ECONOMÍA', 'titulo': 'Comprar o arrendar un avión', 'idea': 'La decisión entre propiedad y arrendamiento considera capital, riesgo, flexibilidad y ciclo de flota.', 'imagenes': ['commercial aircraft leasing fleet', 'commercial airplane leasing fleet']}, {'id': 'fin_07', 'categoria': 'FINANZAS Y ECONOMÍA', 'titulo': 'Cómo gana dinero una aerolínea', 'idea': 'Los ingresos pueden provenir de pasajeros, carga, servicios complementarios y otras actividades.', 'imagenes': ['airport check in airline', 'airport check in airline']}, {'id': 'fin_08', 'categoria': 'FINANZAS Y ECONOMÍA', 'titulo': 'Yield y precio de los billetes', 'idea': 'El yield mide ingresos de pasajeros por pasajero-kilómetro transportado.', 'imagenes': ['airline ticket booking counter', 'airline ticket booking counter']}, {'id': 'fin_09', 'categoria': 'FINANZAS Y ECONOMÍA', 'titulo': 'Qué es el punto de equilibrio de una ruta', 'idea': 'La viabilidad de una ruta requiere comparar ingresos esperados con costos y capacidad.', 'imagenes': ['airline route planning map', 'airline route planning map']}, {'id': 'fin_10', 'categoria': 'FINANZAS Y ECONOMÍA', 'titulo': 'Por qué importa la utilización diaria', 'idea': 'Más horas productivas pueden diluir ciertos costos fijos, siempre dentro de límites operacionales.', 'imagenes': ['aircraft turn around airport apron', 'aircraft turn around airport apron']}, {'id': 'atc_01', 'categoria': 'AEROPUERTOS Y ATC', 'titulo': 'Cómo se organiza una torre de control', 'idea': 'La torre gestiona movimientos y autorizaciones en su ámbito de responsabilidad según procedimientos.', 'imagenes': ['airport control tower', 'airport control tower']}, {'id': 'atc_02', 'categoria': 'AEROPUERTOS Y ATC', 'titulo': 'Qué es el rodaje en un aeropuerto', 'idea': 'El rodaje requiere autorizaciones, conocimiento del aeródromo y prevención de incursiones.', 'imagenes': ['airplane taxiway airport', 'airplane taxiway airport']}, {'id': 'atc_03', 'categoria': 'AEROPUERTOS Y ATC', 'titulo': 'Por qué importan las calles de rodaje', 'idea': 'Las calles de rodaje estructuran los movimientos terrestres entre pistas y plataformas.', 'imagenes': ['airport taxiway aerial', 'airport taxiway aerial']}, {'id': 'atc_04', 'categoria': 'AEROPUERTOS Y ATC', 'titulo': 'Qué significa una incursión en pista', 'idea': 'Una incursión implica presencia incorrecta de aeronaves, vehículos o personas en una zona protegida.', 'imagenes': ['airport runway hold short marking', 'airport runway hold short marking']}, {'id': 'atc_05', 'categoria': 'AEROPUERTOS Y ATC', 'titulo': 'Cómo se asigna una pista en uso', 'idea': 'Viento, tráfico, infraestructura y restricciones influyen en la configuración aeroportuaria.', 'imagenes': ['airport parallel runways aerial', 'airport parallel runways aerial']}, {'id': 'atc_06', 'categoria': 'AEROPUERTOS Y ATC', 'titulo': 'Qué es el slot aeroportuario', 'idea': 'Un slot puede referirse a una asignación temporal de uso de infraestructura bajo reglas aplicables.', 'imagenes': ['busy airport aircraft terminal', 'busy airport airplane terminal']}, {'id': 'atc_07', 'categoria': 'AEROPUERTOS Y ATC', 'titulo': 'Cómo funciona un aeropuerto hub', 'idea': 'Un hub concentra conexiones para combinar flujos de pasajeros y carga entre rutas.', 'imagenes': ['airport transfer hub terminal', 'airport transfer hub terminal']}, {'id': 'atc_08', 'categoria': 'AEROPUERTOS Y ATC', 'titulo': 'Qué es el turnaround', 'idea': 'El turnaround coordina servicios para preparar una aeronave entre llegada y salida.', 'imagenes': ['aircraft ground handling ramp', 'aircraft ground handling ramp']}, {'id': 'atc_09', 'categoria': 'AEROPUERTOS Y ATC', 'titulo': 'Qué hace un despachador de vuelo', 'idea': 'Los despachadores contribuyen a planificación y seguimiento según la regulación y el operador.', 'imagenes': ['airline flight dispatcher operations center', 'airline flight dispatcher operations center']}, {'id': 'atc_10', 'categoria': 'AEROPUERTOS Y ATC', 'titulo': 'Cómo se gestiona el espacio aéreo', 'idea': 'El control y diseño del espacio aéreo buscan separar tráficos y organizar flujos de vuelo.', 'imagenes': ['air traffic control center', 'air traffic control center']}, {'id': 'mnt_01', 'categoria': 'MANTENIMIENTO Y CERTIFICACIÓN', 'titulo': 'Qué es aeronavegabilidad', 'idea': 'La aeronavegabilidad relaciona la conformidad de una aeronave con los requisitos aplicables y su condición segura.', 'imagenes': ['aircraft maintenance hangar', 'aircraft maintenance hangar']}, {'id': 'mnt_02', 'categoria': 'MANTENIMIENTO Y CERTIFICACIÓN', 'titulo': 'Por qué existen las inspecciones', 'idea': 'Las inspecciones ayudan a detectar degradación y confirmar condiciones conforme a mantenimiento aprobado.', 'imagenes': ['aircraft mechanic inspection', 'aircraft mechanic inspection']}, {'id': 'mnt_03', 'categoria': 'MANTENIMIENTO Y CERTIFICACIÓN', 'titulo': 'Qué es una directiva de aeronavegabilidad', 'idea': 'Una directiva de aeronavegabilidad exige acciones de seguridad bajo condiciones regulatorias específicas.', 'imagenes': ['aircraft maintenance documentation', 'aircraft maintenance documentation']}, {'id': 'mnt_04', 'categoria': 'MANTENIMIENTO Y CERTIFICACIÓN', 'titulo': 'Qué es mantenimiento predictivo', 'idea': 'El análisis de datos puede ayudar a anticipar fallas y planificar intervenciones de mantenimiento.', 'imagenes': ['aircraft engine inspection', 'aircraft engine inspection']}, {'id': 'mnt_05', 'categoria': 'MANTENIMIENTO Y CERTIFICACIÓN', 'titulo': 'Qué significa TBO', 'idea': 'El tiempo entre revisiones es un concepto de mantenimiento sujeto a manuales y programas aplicables.', 'imagenes': ['piston aircraft engine mechanic', 'piston airplane engine mechanic']}, {'id': 'mnt_06', 'categoria': 'MANTENIMIENTO Y CERTIFICACIÓN', 'titulo': 'Por qué se revisan los neumáticos', 'idea': 'Los neumáticos aeronáuticos soportan cargas, velocidad y esfuerzos elevados durante operaciones.', 'imagenes': ['aircraft landing gear tires', 'aircraft landing gear tires']}, {'id': 'mnt_07', 'categoria': 'MANTENIMIENTO Y CERTIFICACIÓN', 'titulo': 'Cómo funciona el registro técnico', 'idea': 'La documentación técnica preserva trazabilidad de trabajos, defectos y condiciones de operación.', 'imagenes': ['aircraft maintenance logbook', 'aircraft maintenance logbook']}, {'id': 'mnt_08', 'categoria': 'MANTENIMIENTO Y CERTIFICACIÓN', 'titulo': 'Qué es una MEL', 'idea': 'La lista de equipo mínimo establece condiciones para operar con ciertos equipos inoperativos cuando está autorizada.', 'imagenes': ['aircraft cockpit overhead panel', 'aircraft cockpit overhead panel']}, {'id': 'mnt_09', 'categoria': 'MANTENIMIENTO Y CERTIFICACIÓN', 'titulo': 'Qué es una inspección boroscópica', 'idea': 'Un boroscopio permite observar componentes internos sin desmontajes extensos en determinadas situaciones.', 'imagenes': ['jet engine borescope inspection', 'jet engine borescope inspection']}, {'id': 'mnt_10', 'categoria': 'MANTENIMIENTO Y CERTIFICACIÓN', 'titulo': 'Por qué importa la corrosión', 'idea': 'La corrosión puede afectar integridad de materiales y requiere programas adecuados de prevención y control.', 'imagenes': ['aircraft aluminum skin maintenance', 'aircraft aluminum skin maintenance']}, {'id': 'future_01', 'categoria': 'AVIACIÓN DEL FUTURO', 'titulo': 'Qué es combustible SAF', 'idea': 'El combustible sostenible de aviación se evalúa por vías de producción y criterios de sostenibilidad aplicables.', 'imagenes': ['sustainable aviation fuel aircraft', 'sustainable aviation fuel airplane']}, {'id': 'future_02', 'categoria': 'AVIACIÓN DEL FUTURO', 'titulo': 'Qué limita a un avión eléctrico', 'idea': 'La energía específica, masa, gestión térmica e infraestructura condicionan el diseño eléctrico.', 'imagenes': ['electric aircraft prototype', 'electric airplane prototype']}, {'id': 'future_03', 'categoria': 'AVIACIÓN DEL FUTURO', 'titulo': 'Hidrógeno en aviación', 'idea': 'El hidrógeno plantea retos de almacenamiento, infraestructura y arquitectura propulsiva.', 'imagenes': ['hydrogen aircraft demonstrator photo', 'hydrogen aircraft demonstrator photograph']}, {'id': 'future_04', 'categoria': 'AVIACIÓN DEL FUTURO', 'titulo': 'Cómo se certifica un avión nuevo', 'idea': 'La certificación evalúa diseño y demostraciones de cumplimiento bajo una base regulatoria.', 'imagenes': ['aircraft flight testing', 'aircraft flight testing']}, {'id': 'future_05', 'categoria': 'AVIACIÓN DEL FUTURO', 'titulo': 'Qué aportan los materiales compuestos', 'idea': 'Los compuestos permiten distintas relaciones entre masa, rigidez y características estructurales.', 'imagenes': ['composite aircraft fuselage', 'composite airplane fuselage']}, {'id': 'future_06', 'categoria': 'AVIACIÓN DEL FUTURO', 'titulo': 'Por qué se estudia el vuelo supersónico', 'idea': 'El vuelo supersónico presenta desafíos de ruido, eficiencia y certificación.', 'imagenes': ['supersonic aircraft research', 'supersonic airplane research']}, {'id': 'future_07', 'categoria': 'AVIACIÓN DEL FUTURO', 'titulo': 'Cómo se usan los datos de vuelo', 'idea': 'Los datos operacionales ayudan a analizar rendimiento y tendencias de seguridad según gobernanza aplicable.', 'imagenes': ['aircraft flight data recorder', 'aircraft flight data recorder']}, {'id': 'future_08', 'categoria': 'AVIACIÓN DEL FUTURO', 'titulo': 'El papel de los simuladores', 'idea': 'Los simuladores pueden apoyar entrenamiento y evaluación en condiciones controladas.', 'imagenes': ['airliner flight simulator', 'airliner flight simulator']}, {'id': 'future_09', 'categoria': 'AVIACIÓN DEL FUTURO', 'titulo': 'Qué es UTM para drones', 'idea': 'La gestión de tráfico no tripulado busca organizar operaciones de aeronaves no tripuladas de forma segura.', 'imagenes': ['drone aviation traffic', 'drone aviation traffic']}, {'id': 'future_10', 'categoria': 'AVIACIÓN DEL FUTURO', 'titulo': 'Cómo cambia el diseño de cabina', 'idea': 'La automatización y las interfaces transforman la interacción humana con los sistemas de vuelo.', 'imagenes': ['modern aircraft cockpit avionics', 'modern airplane cockpit avionics']}]
FUENTES_CATEGORIA = {'AERODINÁMICA': ('FAA PHAK - aerodinámica', 'https://www.faa.gov/regulations_policies/handbooks_manuals/aviation/phak', ['Chapter']), 'MOTORES Y SISTEMAS': ('FAA PHAK - sistemas', 'https://www.faa.gov/regulations_policies/handbooks_manuals/aviation/phak', ['Chapter']), 'INSTRUMENTOS Y NAVEGACIÓN': ('FAA PHAK - instrumentos y navegación', 'https://www.faa.gov/regulations_policies/handbooks_manuals/aviation/phak', ['Chapter']), 'METEOROLOGÍA': ('FAA manuales - meteorología aeronáutica', 'https://www.faa.gov/regulations_policies/handbooks_manuals/aviation', ['Weather']), 'OPERACIONES DE VUELO': ('FAA Airplane Flying Handbook', 'https://www.faa.gov/regulations_policies/handbooks_manuals/aviation/airplane_handbook', ['Chapter']), 'SEGURIDAD Y FACTOR HUMANO': ('OACI gestión de seguridad operacional', 'https://www.icao.int/safety-management', ['safety']), 'FINANZAS Y ECONOMÍA': ('IATA Global Outlook for Air Transport - junio 2026', 'https://www.iata.org/en/publications/economics/reports/global-outlook-for-air-transport-june-2026', ['profit']), 'AEROPUERTOS Y ATC': ('FAA información para pilotos', 'https://www.faa.gov/pilots', ['Pilots']), 'MANTENIMIENTO Y CERTIFICACIÓN': ('FAA manuales aeronáuticos y mantenimiento', 'https://www.faa.gov/regulations_policies/handbooks_manuals/aviation', ['Maintenance']), 'AVIACIÓN DEL FUTURO': ('FAA manuales aeronáuticos y certificación', 'https://www.faa.gov/regulations_policies/handbooks_manuals/aviation', ['Handbook'])}

CASOS = {}
for ficha in DATOS_AERONAUTICOS:
    categoria=ficha['categoria']; titulo=ficha['titulo']; idea=ficha['idea']
    nombre,url,anclas=FUENTES_CATEGORIA[categoria]
    CASOS[ficha['id']]=dict(
        titulo=titulo,categoria=categoria,estado='DIVULGACIÓN · DOCUMENTACIÓN POR CONTRASTAR',
        pregunta=f'¿Por qué importa comprender {titulo.lower()} en la aviación?',
        gancho=f'En aeronáutica, una idea puede transformar cómo se comprende un vuelo. Hoy investigamos: {titulo}.',
        contexto=idea, pistas=[idea], hechos=[idea],
        giro='La utilidad del concepto depende del contexto operacional y del diseño de la aeronave. '+idea,
        importancia='Comprender esta idea permite hacer mejores preguntas y evaluar datos técnicos con más criterio.',
        cierre='En AEROFACTUM estudiamos el conocimiento detrás de cada vuelo.',
        fuentes=[(nombre,url,anclas)], imagenes=list(dict.fromkeys(ficha['imagenes'])),
        mini_titulo=titulo.upper(),
        mini_subtitulo='POR QUÉ ESTE CONCEPTO IMPORTA')

CATALOGO_AERONAUTICO = {k:dict(id=k,caso_id=k,modo='conocimiento',titulo=v['titulo'],
    pregunta=v['pregunta'],hecho_clave=v['contexto']) for k,v in CASOS.items()}
assert len(CATALOGO_AERONAUTICO)==100

ENFOQUE_CATEGORIA = {
    'AERODINÁMICA': ('En aerodinámica, hay que distinguir fuerzas, ángulos y condiciones de vuelo.', '¿Cómo cambia este fenómeno cuando varían la velocidad, la configuración o la masa?'),
    'MOTORES Y SISTEMAS': ('En los sistemas de aeronave, cada componente forma parte de una arquitectura con redundancias y límites.', '¿Qué información necesita el piloto o el técnico para comprender ese sistema?'),
    'INSTRUMENTOS Y NAVEGACIÓN': ('En navegación, una indicación depende de sensores, referencias y límites del equipo.', '¿Qué mide realmente el instrumento y qué no puede garantizar?'),
    'METEOROLOGÍA': ('La meteorología aeronáutica exige interpretar observaciones, pronósticos y cambios posibles.', '¿Qué diferencia existe entre el dato meteorológico y una decisión de vuelo?'),
    'OPERACIONES DE VUELO': ('La operación combina procedimientos, rendimiento de la aeronave y coordinación entre personas.', '¿En qué fase del vuelo se aplica este conocimiento y de qué depende?'),
    'SEGURIDAD Y FACTOR HUMANO': ('La seguridad operacional depende también de comunicaciones, organización y decisiones humanas.', '¿Qué barreras pueden reducir el riesgo asociado a esta situación?'),
    'FINANZAS Y ECONOMÍA': ('Una cifra financiera aislada puede resultar engañosa si ignoramos su periodo, unidades y alcance.', '¿Qué gastos e ingresos entran en ese indicador y cuáles quedan fuera?'),
    'AEROPUERTOS Y ATC': ('Un aeropuerto funciona como un sistema coordinado entre aeronaves, personas e infraestructura.', '¿Qué actores necesitan compartir información para que funcione?'),
    'MANTENIMIENTO Y CERTIFICACIÓN': ('En mantenimiento es indispensable distinguir inspección, diagnóstico y acción aprobada.', '¿Cómo queda documentada la condición aeronavegable de la aeronave?'),
    'AVIACIÓN DEL FUTURO': ('Las tecnologías nuevas deben demostrar viabilidad técnica y cumplimiento de seguridad.', '¿Qué limitaciones prácticas impiden pasar del prototipo al servicio?'),
}

# =================== INVESTIGACIÓN Y GUION IA ===================
# Un motor IA jamás se considera fuente: las afirmaciones deben vincularse a textos
# realmente recuperados. Una coincidencia textual no certifica veracidad científica.

def _limpiar_texto_web(contenido, tipo='text/html'):
    """Extrae texto legible, sin ejecutar scripts ni instalar navegadores."""
    if 'pdf' in tipo.lower():
        return ''  # no interpretar binarios como texto contrastado
    try:
        from bs4 import BeautifulSoup
        sopa=BeautifulSoup(contenido,'html.parser')
        for nodo in sopa(['script','style','nav','footer','header','form','noscript','svg']):
            nodo.decompose()
        principal=sopa.find('article') or sopa.find('main') or sopa.body or sopa
        texto=principal.get_text(' ',strip=True)
    except Exception:
        texto=re.sub(r'<[^>]+>',' ',contenido)
    return re.sub(r'\s+',' ',html.unescape(texto)).strip()[:18000]


def _tokens_tema(caso):
    """Palabras temáticas en español e inglés para leer documentación FAA.

    El catálogo usa títulos españoles, pero los manuales de FAA están en inglés.
    No se admiten palabras genéricas como 'aircraft' como única evidencia.
    """
    import unicodedata
    episodio=caso.get('_episodio',{})
    tema_id=episodio.get('caso_id',caso.get('id',''))
    palabras=(caso.get('titulo','')+' '+caso.get('contexto','')+' '
              +' '.join(caso.get('imagenes',[])[:3])).lower()
    palabras=''.join(c for c in unicodedata.normalize('NFKD',palabras) if not unicodedata.combining(c))
    stop={'que','como','para','por','una','del','los','las','the','and','with','this','from',
          'aircraft','aviation','avion','aviones','aeronave','aeronaves','airplane',
          'importa','explicado','funciona','airport','airliner','photo','fotografia',
          'frente','real','indicada','velocidad','instrument','indicator'}
    tokens={p for p in re.findall(r'[a-z]{4,}',palabras) if p not in stop}
    equivalencias={
        'nav_01':{'airspeed','indicated','calibrated','true airspeed','pitot','tas','ias'},
        'nav_02':{'altimeter','altitude','barometric','pressure altitude'},
        'nav_03':{'attitude','artificial horizon','gyroscopic','pitch','bank'},
        'nav_04':{'pitot','static pressure','airspeed','pressure system'},
        'nav_05':{'transponder','secondary surveillance','squawk'},
        'nav_06':{'localizer','glideslope','instrument landing system'},
        'nav_07':{'vor','radial','omnidirectional'},
        'nav_08':{'gps','satellite navigation','gnss'},
        'nav_09':{'rnav','area navigation'},
        'nav_10':{'rnp','required navigation performance'},
        'meteo_07':{'upper winds','jet stream','wind aloft','pressure gradient'},
        'atc_05':{'runway selection','runway in use','active runway',
                  'runway use','crosswind','tailwind','wind','controller-in-charge',
                  'runway'},
        'safe_10':{'go-around','go around','missed approach','rejected landing',
                   'stabilized approach','stabilised approach','approach','landing','goarounds'},
        'future_05':{'composite','composites','advanced composite materials',
                     'carbon fiber','carbon fibre','fiber reinforced','fiberglass',
                     'laminate','lightweight','weight','corrosion','damage tolerance',
                     'composite aircraft','structural','material'},
    }
    return tokens | equivalencias.get(tema_id,set())


def _relevancia_documento(texto, caso):
    import unicodedata
    t=''.join(c for c in unicodedata.normalize('NFKD',texto.lower()) if not unicodedata.combining(c))
    tokens=_tokens_tema(caso)
    coincidencias={x for x in tokens if re.search(r'\b'+re.escape(x)+r'\b',t)}
    tema_id=caso.get('_episodio',{}).get('caso_id',caso.get('id',''))
    if tema_id=='future_05' and not coincidencias.intersection(
            {'composite','composites','advanced composite materials','carbon fiber',
             'carbon fibre','fiber reinforced','fiberglass','laminate',
             'composite aircraft'}):
        return 0
    return len(coincidencias)


def _extraer_pdf_oficial(response, caso):
    """Obtiene fragmentos relevantes de un PDF técnico; nunca lo trata como HTML.

    Solo PDFs publicados bajo dominios de instituciones aeronáuticas confiables.
    Extrae un máximo de páginas y tamaño de fichero para proteger GitHub Actions.
    """
    import io
    from urllib.parse import urlparse
    from pypdf import PdfReader
    host=(urlparse(response.url).hostname or '').lower()
    permitidos=('faa.gov','easa.europa.eu','icao.int','iata.org','weather.gov','noaa.gov',
               'nasa.gov','ntsb.gov','airbus.com','boeing.com','skybrary.aero',
               'eurocontrol.int','caa.co.uk','atsb.gov.au','metoffice.gov.uk',
               'airlines.org','mit.edu','ntrs.nasa.gov','aeronautics.nasa.gov')
    if not any(host==d or host.endswith('.'+d) for d in permitidos):
        return ''
    limite=23_000_000
    if len(response.content)>limite:
        print('  PDF oficial demasiado grande:',response.url[:110],flush=True)
        return ''
    try:
        lector=PdfReader(io.BytesIO(response.content),strict=False)
        secciones=[]
        for i,pagina in enumerate(lector.pages):
            if i>=min(90,len(lector.pages)):break
            txt=re.sub(r'\s+',' ',pagina.extract_text() or '').strip()
            if len(txt)<100:continue
            coincidencias=_relevancia_documento(txt,caso)
            if coincidencias:
                secciones.append((coincidencias,i,txt))
        # Favorecer secciones que realmente hablan del tema, no portadas/índices.
        secciones.sort(key=lambda x:(-x[0],x[1]))
        fragmentos=[]
        for _,num,txt in secciones[:5]:
            claves=_tokens_tema(caso)
            cortes=[]
            for clave in claves:
                for m in list(re.finditer(r'\b'+re.escape(clave)+r'\b',txt,re.I))[:5]:
                    cortes.append((max(0,m.start()-440),min(len(txt),m.end()+950)))
            for a,b in sorted(cortes)[:6]:
                fragmentos.append(f'[Página {num+1}] '+txt[a:b])
                if sum(map(len,fragmentos))>=10500:break
            if sum(map(len,fragmentos))>=10500:break
        return ' '.join(fragmentos)[:11500]
    except Exception as e:
        print('  No se pudo extraer el PDF oficial:',type(e).__name__,str(e)[:110],flush=True)
        return ''


def _leer_documento_web(session,url,caso,origen):
    from urllib.parse import urlparse
    if not url.startswith('https://'):return None
    host=urlparse(url).hostname or ''
    if host in {'localhost','127.0.0.1','0.0.0.0'} or host.endswith('.local'):
        return None
    try:
        # Evita descargar PDFs arbitrariamente grandes; límite por Content-Length.
        respuesta=session.get(url,timeout=(8,25),allow_redirects=True,headers={
            'User-Agent':'AEROFACTUM/4.2 (https://acesped.github.io/aerofactum/; contacto: ari.cesped@gmail.com)'},stream=True)
        respuesta.raise_for_status()
        mime=respuesta.headers.get('Content-Type','text/html').lower()
        es_pdf='pdf' in mime or urlparse(respuesta.url).path.lower().endswith('.pdf')
        limite=23_000_000 if es_pdf else 1_800_000
        if int(respuesta.headers.get('Content-Length','0') or '0')>limite:
            print('  Fuente descartada: supera el límite de tamaño:',respuesta.url[:100],flush=True)
            respuesta.close();return None
        piezas=[];acumulado=0
        for pieza in respuesta.iter_content(chunk_size=65536):
            acumulado+=len(pieza)
            if acumulado>limite:
                print('  Fuente descartada: descarga supera límite de tamaño:',respuesta.url[:100],flush=True)
                respuesta.close();return None
            piezas.append(pieza)
        contenido=b''.join(piezas)
        if es_pdf:
            respuesta._content=contenido
            texto=_extraer_pdf_oficial(respuesta,caso)
        elif 'html' in mime or 'text/plain' in mime:
            texto=_limpiar_texto_web(contenido.decode(respuesta.encoding or 'utf-8','replace'),mime)
        else:
            print('  Fuente descartada: formato no admitido:',mime,respuesta.url[:100],flush=True)
            return None
        puntaje=_relevancia_documento(texto,caso)
        if len(texto)<450 or puntaje<1:
            print(f'  Fuente descartada: texto={len(texto)} caracteres; relevancia={puntaje}; '
                  f'URL={respuesta.url[:100]}',flush=True)
            return None
        dominio=urlparse(respuesta.url).hostname or ''
        if dominio.endswith('news.google.com'):return None
        return {'id':'', 'nombre':origen[:120], 'url':respuesta.url,
                'fecha_consulta':datetime.now(timezone.utc).isoformat(),
                'texto':texto[:11500], 'coincidencias_tema':_relevancia_documento(texto,caso)}
    except Exception as e:
        print('  Fuente no recuperable:',url[:110],str(e)[:100],flush=True)
        return None


def _rutas_documentacion_oficial(caso):
    """Prioriza capítulos técnicos específicos, no portadas genéricas de manuales.

    Las URLs apuntan a FAA; los enlaces a PDF se descubren de su página.
    Si falla una URL, se ensaya la siguiente y se registra el descarte.
    """
    tema_id=caso.get('_episodio',{}).get('caso_id',caso.get('id',''))
    phak='https://www.faa.gov/regulationspolicies/handbooksmanuals/aviation/phak/'
    rutas={
      'nav_01':[
        ('FAA: PHAK, capítulo 8 Flight Instruments (PDF)',
         'https://www.faa.gov/sites/faa.gov/files/10_phak_ch8.pdf'),
        ('FAA: PHAK, capítulo 8 Flight Instruments',phak+'chapter-8-flight-instruments'),
        ('FAA: Instrument Flying Handbook, IAS y TAS',
         'https://www.faa.gov/sites/faa.gov/files/pilots/FAA-H-8083-15B.pdf')],
      'nav_03':[
        ('FAA: PHAK, capítulo 8 Flight Instruments (PDF)',
         'https://www.faa.gov/sites/faa.gov/files/10_phak_ch8.pdf'),
        ('FAA: PHAK, capítulo 8 Flight Instruments',phak+'chapter-8-flight-instruments'),
        ('FAA: Instrument Flying Handbook',
         'https://www.faa.gov/sites/faa.gov/files/pilots/FAA-H-8083-15B.pdf')],
      'future_05':[
        ('FAA: Advanced Composite Materials (certificación y estructuras)',
         'https://www.faa.gov/aircraft/air_cert/step/disciplines/advanced_composite_materials'),
        ('NASA: HiCAM, compuestos y reducción de peso en aeronaves',
         'https://www.nasa.gov/directorates/armd/aavp/hicam/about-hicam/'),
        ('FAA: Reparaciones y alteraciones de estructuras compuestas',
         'https://www.faa.gov/regulations_policies/advisory_circulars/index.cfm/go/document.information/documentid/1029806')],
      'safe_10':[
        ('EASA: Approach and landing safety — go-around',
         'https://www.easa.europa.eu/en/domains/general-aviation/flying-safely/loss-of-control-in-approach-and-landing'),
        ('FAA: AIM Arrival Procedures — missed approaches',
         'https://www.faa.gov/air_traffic/publications/aim_html/chap5_section_4.html'),
        ('FAA: Air Traffic Control — missed approach',
         'https://www.faa.gov/air_traffic/publications/atpubs/atc_html/chap4_section_8.html')],
      'atc_05':[
        ('FAA JO 7110.65: Runway Selection, sección 3-5',
         'https://www.faa.gov/air_traffic/publications/atpubs/atc_html/chap3_section_5.html'),
        ('FAA AIM: Airport Operations, runway assignment',
         'https://www.faa.gov/air_traffic/publications/aim_html/chap4_section_3.html'),
        ('FAA JO 7110.65: Use of Active Runways, sección 3-1',
         'https://www.faa.gov/air_traffic/publications/atpubs/atc_html/chap3_section_1.html')],
    }
    salida=list(rutas.get(tema_id,[]))
    # Fuente de capítulo preferente por categoría. No equivale a fact-check.
    capitulos={
      'INSTRUMENTOS Y NAVEGACIÓN':('FAA: PHAK, capítulo 8 Flight Instruments',
                                  phak+'chapter-8-flight-instruments'),
      'METEOROLOGÍA':('FAA: PHAK, capítulo 12 Weather Theory',
                     phak+'chapter-12-weather-theory'),
    }
    cap=capitulos.get(caso.get('categoria'))
    if cap and cap[1] not in {url for _,url in salida}:salida.append(cap)
    return salida


def _descubrir_pdf_faa(session, url, caso):
    """En páginas de capítulos FAA, localizar el documento PDF asociado."""
    from urllib.parse import urljoin,urlparse
    if 'faa.gov' not in (urlparse(url).hostname or ''):return []
    try:
        from bs4 import BeautifulSoup
        resp=session.get(url,timeout=(7,17))
        if not resp.ok or 'html' not in resp.headers.get('Content-Type','text/html'):return []
        soup=BeautifulSoup(resp.text,'html.parser')
        candidatos=[]
        for a in soup.find_all('a',href=True):
            href=urljoin(resp.url,a['href'])
            nombre=a.get_text(' ',strip=True)
            if urlparse(href).path.lower().endswith('.pdf') and 'faa.gov' in (urlparse(href).hostname or ''):
                candidatos.append((href,nombre))
        return candidatos[:2]
    except Exception:return []


def _url_publica_investigacion(url):
    """Admite fuentes públicas HTTPS; rechaza hosts locales, privados y URLs sospechosas."""
    from urllib.parse import urlsplit, urlunsplit
    import ipaddress
    url=html.unescape(str(url or '')).strip().strip('<>\"\'`.,;)]')
    try:
        p=urlsplit(url)
        if p.scheme!='https' or not p.hostname or p.username or p.password:return None
        host=p.hostname.lower().rstrip('.')
        if host in {'localhost','metadata.google.internal'} or host.endswith(('.local','.internal','.localhost')):return None
        try:
            ip=ipaddress.ip_address(host)
            if not ip.is_global:return None
        except ValueError:pass
        if p.port not in (None,443):return None
        if len(url)>1300:return None
        if host in {'generativelanguage.googleapis.com','api.groq.com'}:return None
        return urlunsplit(('https',p.netloc,p.path,p.query,''))
    except (ValueError,TypeError):return None


def _enlaces_de_texto_investigado(texto):
    """Extrae enlaces explícitos; ninguna mención sin URL cuenta como evidencia."""
    from urllib.parse import unquote
    hallados=[]
    for m in re.finditer(r'https://[^\s<>\"\'`]+',str(texto or ''),re.I):
        url=_url_publica_investigacion(m.group(0))
        if url and url not in hallados:hallados.append(url)
    return hallados


def _prompt_busqueda_ia(caso):
    return (f'Investiga el tema aeronáutico «{caso["titulo"]}», categoría «{caso["categoria"]}». '
            f'Contexto: {caso.get("contexto", "")}. '
            'Usa búsqueda web REAL para encontrar entre 5 y 9 páginas de fuentes diversificadas: '
            'autoridades aeronáuticas de varios países, NASA, EUROCONTROL, OACI, EASA, '
            'fabricantes, universidades, centros de investigación, publicaciones técnicas y prensa especializada. '
            'No restrinjas la búsqueda a FAA ni inventes enlaces o hechos. '
            'Prioriza fuentes primarias accesibles, artículos técnicos específicos y documentación de actualidad '
            'solo cuando sea pertinente. Escribe URLs HTTPS completas, una por línea, '
            'con título breve. NO aportes una conclusión sin enlaces; solo fuentes localizables.')


def _descubrir_fuentes_gemini(caso):
    """Gemini Grounding with Google Search (REST); devuelve URLs, no hechos verificados."""
    import requests
    from urllib.parse import quote
    key=os.getenv('GEMINI_API_KEY','').strip()
    if not key:raise RuntimeError('GEMINI_API_KEY no configurada')
    endpoint=('https://generativelanguage.googleapis.com/v1beta/models/'
              +quote(GEMINI_MODELO,safe='')+':generateContent')
    payload={'contents':[{'parts':[{'text':_prompt_busqueda_ia(caso)}]}],
             'tools':[{'googleSearch':{}}],
             'generationConfig':{'temperature':0.25,'maxOutputTokens':1800}}
    r=requests.post(endpoint,headers={'x-goog-api-key':key,'Content-Type':'application/json'},
                    json=payload,timeout=(10,75))
    if not r.ok:raise RuntimeError(f'Gemini Search HTTP {r.status_code}: {r.text[:180]}')
    candidatos=r.json().get('candidates') or []
    if not candidatos:raise RuntimeError('Gemini Search sin resultados')
    fuentes=[]
    for can in candidatos[:1]:
        texto=' '.join(p.get('text','') for p in can.get('content',{}).get('parts',[]))
        for url in _enlaces_de_texto_investigado(texto):fuentes.append((url,'Gemini Search'))
        # Google entrega URLs con citas en groundingMetadata; son candidatos por verificar.
        for chunk in (can.get('groundingMetadata') or {}).get('groundingChunks',[]):
            web=chunk.get('web') or {}
            url=_url_publica_investigacion(web.get('uri',''))
            if url:fuentes.append((url,(web.get('title') or 'Gemini grounding')[:120]))
    return fuentes


def _descubrir_fuentes_groq(caso):
    """Groq browser_search: API de búsqueda distinta a la generación JSON del guion."""
    import requests
    key=os.getenv('GROQ_API_KEY','').strip()
    if not key:raise RuntimeError('GROQ_API_KEY no configurada')
    payload={'model':GROQ_MODELO,'messages':[{'role':'user','content':_prompt_busqueda_ia(caso)}],
             'temperature':0.2,'max_completion_tokens':2200,
             'tools':[{'type':'browser_search'}],'tool_choice':'required',
             'stream':False}
    r=requests.post('https://api.groq.com/openai/v1/chat/completions',
       headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'},
       json=payload,timeout=(10,100))
    if not r.ok:raise RuntimeError(f'Groq Search HTTP {r.status_code}: {r.text[:180]}')
    data=r.json(); texto='\n'.join(str(c.get('message',{}).get('content') or '')
                          for c in data.get('choices',[]))
    # No usar como evidencia el resumen producido por IA: solo URLs legibles.
    return [(url,'Groq browser_search') for url in _enlaces_de_texto_investigado(texto)]


class OpenRouterSalidaAgotada(RuntimeError):
    """La solicitud agotó sus tokens generando razonamiento, no el guion."""


_OPENROUTER_ALTERNATIVO = None
_OPENROUTER_MODELO_REAL = None
_OPENROUTER_ALTERNATIVO_INTENTADO = False


def _openrouter_elegir_gratuito(modelos, excluido=''):
    candidatos=[]
    for m in modelos:
        try:
            mid=str(m['id']); precio=m['pricing']
            parametros=set(m.get('supported_parameters') or [])
            salida=(m.get('architecture') or {}).get('output_modalities') or []
            maxsalida=(m.get('top_provider') or {}).get('max_completion_tokens')
            if not mid.endswith(':free') or mid==excluido:continue
            if 'text' not in salida:continue
            if float(precio['prompt'])!=0 or float(precio['completion'])!=0:continue
            if float(precio.get('request') or 0)!=0:continue
            if parametros & {'reasoning','include_reasoning','reasoning_effort'}:continue
            if m.get('is_reasoning') or (m.get('architecture') or {}).get('is_reasoning'):continue
            if int(m.get('context_length') or 0)<8192:continue
            if maxsalida is not None and int(maxsalida)<3000:continue
            candidatos.append((('response_format' in parametros), int(m.get('context_length') or 0), mid))
        except (ValueError,TypeError,KeyError):continue
    if not candidatos:return None
    json_ok,_,mid=max(candidatos)
    return {'id':mid,'json':json_ok}


def _openrouter_preparar_alternativo():
    global _OPENROUTER_ALTERNATIVO, _OPENROUTER_ALTERNATIVO_INTENTADO
    # Respect explicit model choice; only switch within the free router family.
    if OPENROUTER_MODELO!='openrouter/free' and not OPENROUTER_MODELO.endswith(':free'):return False
    if _OPENROUTER_ALTERNATIVO_INTENTADO:return False
    _OPENROUTER_ALTERNATIVO_INTENTADO=True
    try:
        import requests
        r=requests.get('https://openrouter.ai/api/v1/models',timeout=(5,15))
        r.raise_for_status()
        _OPENROUTER_ALTERNATIVO=_openrouter_elegir_gratuito(r.json().get('data',[]), _OPENROUTER_MODELO_REAL or OPENROUTER_MODELO)
    except Exception as exc:
        print('  OpenRouter: catálogo de modelos alternativos no disponible:',str(exc)[:150],flush=True)
        return False
    if _OPENROUTER_ALTERNATIVO:
        print('  OpenRouter: siguiente intento con modelo gratuito explícito sin parámetros de razonamiento:',_OPENROUTER_ALTERNATIVO['id'],flush=True)
        return True
    return False


def _openrouter_chat(prompt, *, busqueda=False, limitar_razonamiento=True):
    """Chat Completions; controla razonamiento para reservar tokens al JSON.

    No publica ni reutiliza reasoning_details como guion. Las búsquedas web
    opcionales requieren autorización expresa del usuario.
    """
    import requests
    key=os.getenv('OPENROUTER_API_KEY','').strip()
    if not key:raise RuntimeError('OPENROUTER_API_KEY no configurada')
    global _OPENROUTER_MODELO_REAL
    alternativo=_OPENROUTER_ALTERNATIVO if not busqueda else None
    payload={
        'model':alternativo['id'] if alternativo else OPENROUTER_MODELO,
        'messages':[
            {'role':'system','content':('Investiga el nicho indicado y cita fuentes reales.' if busqueda
                                        else 'Eres guionista del nicho indicado. Devuelve SOLO el JSON solicitado, sin análisis ni markdown.')},
            {'role':'user','content':prompt}],
        'temperature':0.20 if busqueda else 0.35,
        'max_tokens':2200 if busqueda else AERO_OPENROUTER_MAX_TOKENS,
        'stream':False,
    }
    # OpenRouter contabiliza los tokens de razonamiento dentro de max_tokens.
    # 'minimal' reserva una mayor parte al texto visible en modelos compatibles.
    # Un router dinámico puede seleccionar un modelo con razonamiento obligatorio.
    if alternativo:
        payload['max_tokens']=min(AERO_OPENROUTER_MAX_TOKENS,4500)
        if alternativo['json']:payload['response_format']={'type':'json_object'}
    elif not busqueda and limitar_razonamiento:
        payload['reasoning']={'effort':AERO_OPENROUTER_RAZONAMIENTO}
    if busqueda:
        if not AERO_OPENROUTER_WEB_SEARCH:
            raise RuntimeError('Búsqueda OpenRouter desactivada por posible costo; configurar AERO_OPENROUTER_WEB_SEARCH=true')
        payload['tools']=[{'type':'openrouter:web_search','parameters':{'max_uses':1,'max_results':5}}]
    headers={
        'Authorization':'Bearer '+key,
        'Content-Type':'application/json',
        'HTTP-Referer':'https://acesped.github.io/aerofactum/',
        'X-Title':'AEROFACTUM',
    }
    r=requests.post('https://openrouter.ai/api/v1/chat/completions',
                    headers=headers,json=payload,timeout=(10,AERO_IA_TIMEOUT))
    if not r.ok:
        # No reintentar automáticamente con configuraciones que podrían volver
        # a consumir todos los tokens de salida. Diagnóstico concreto.
        raise RuntimeError(f'OpenRouter HTTP {r.status_code}: {r.text[:350]}')
    data=r.json()
    if not busqueda:_OPENROUTER_MODELO_REAL=data.get('model') or payload['model']
    choices=data.get('choices') or []
    if not choices:
        raise RuntimeError('OpenRouter sin respuestas: '+str(data.get('error') or data.get('provider') or '')[:250])
    choice=choices[0]
    msg=choice.get('message') or {}
    content=msg.get('content') or ''
    if isinstance(content,list):
        content='\n'.join(str(x.get('text','')) for x in content if isinstance(x,dict))
    motivo=choice.get('finish_reason') or '?'
    uso=data.get('usage') or {}
    detalle_uso=uso.get('completion_tokens_details') or {}
    razonamiento=detalle_uso.get('reasoning_tokens')
    salida=uso.get('completion_tokens')
    consumido=f' (tokens_salida={salida}, tokens_razonamiento={razonamiento})'
    if not str(content).strip():
        if motivo=='length':
            raise OpenRouterSalidaAgotada('OpenRouter agotó max_tokens sin entregar guion JSON'+consumido)
        raise RuntimeError('OpenRouter devolvió contenido vacío (finish_reason='+str(motivo)+')'+consumido)
    if motivo=='length':
        # Solo aprovechar una respuesta que ya contiene un objeto JSON cerrado.
        # No aplicar json_repair a una salida cortada por el proveedor.
        if busqueda:
            raise OpenRouterSalidaAgotada('OpenRouter agotó la salida de búsqueda'+consumido)
        try:
            completo=json.loads(str(content).strip())
            if not isinstance(completo,dict):raise ValueError('No es un objeto')
        except (ValueError,TypeError):
            raise OpenRouterSalidaAgotada('OpenRouter entregó respuesta truncada antes de cerrar JSON'+consumido)
        print('  OpenRouter: objeto JSON completo pese al límite de salida; se aplicará la validación íntegra.',flush=True)
    return str(content)


def _consultar_openrouter(prompt):
    return _limpiar_json_ia(_openrouter_chat(prompt))


def _descubrir_fuentes_openrouter(caso):
    texto=_openrouter_chat(_prompt_busqueda_ia(caso),busqueda=True)
    return [(url,'OpenRouter web search') for url in _enlaces_de_texto_investigado(texto)]


_AERO_BUSQUEDA_BLOQUEADA = set()

def _descubrir_fuentes_ia(caso):
    """Fuentes candidatas descubiertas con motores IA y herramientas de búsqueda."""
    modo=AERO_INVESTIGACION_WEB
    if modo not in ('auto','gemini','groq','openrouter','ambas','todas','off'):
        raise ValueError('AERO_INVESTIGACION_WEB: auto, gemini, groq, openrouter, ambas, todas u off')
    if modo=='off':return [],[]
    motores={'auto':['gemini','groq'], 'gemini':['gemini'],
             'groq':['groq'], 'openrouter':['openrouter'],
             'ambas':['gemini','groq'],
             'todas':['gemini','groq','openrouter']}[modo]
    # En auto, OpenRouter solo participa en la búsqueda si se habilita la
    # herramienta web potencialmente facturable. Sí participa en guiones gratis.
    if modo=='auto' and AERO_OPENROUTER_WEB_SEARCH:
        motores.append('openrouter')
    encontrados=[]; errores=[]
    for motor in motores:
        if motor in _AERO_BUSQUEDA_BLOQUEADA or motor in _AERO_IA_INHABILITADOS:
            errores.append(motor+': búsqueda omitida por fallo anterior de proveedor')
            continue
        if motor=='openrouter' and not AERO_OPENROUTER_WEB_SEARCH:
            errores.append('OpenRouter búsqueda omitida: herramienta web desactivada para evitar cargos')
            continue
        if motor=='openrouter' and not os.getenv('OPENROUTER_API_KEY','').strip():
            errores.append('OpenRouter búsqueda omitida: clave no configurada')
            continue
        try:
            print(f'  Buscando fuentes en internet con {motor}...',flush=True)
            propuestas=({'gemini':_descubrir_fuentes_gemini,
                         'groq':_descubrir_fuentes_groq,
                         'openrouter':_descubrir_fuentes_openrouter}[motor])(caso)
            print(f'  {motor}: {len(propuestas)} enlaces candidatos (sin verificar)',flush=True)
            encontrados.extend(propuestas)
            if modo=='auto' and len(encontrados)>=4:break
        except Exception as exc:
            msg=f'{motor}: {type(exc).__name__}: {str(exc)[:210]}'
            errores.append(msg);print('  Búsqueda IA no disponible:',msg,flush=True)
            if any(x in msg.lower() for x in ('429','503','500','timeout','timed out','quota','rate limit')):
                _AERO_BUSQUEDA_BLOQUEADA.add(motor)
    unicos=[]; vistos=set()
    for url,nombre in encontrados:
        if url not in vistos and _url_publica_investigacion(url):
            vistos.add(url);unicos.append((url,nombre))
    return unicos[:AERO_BUSQUEDA_MAX_URLS],errores


def _descubrir_fuentes_rss(session, caso):
    """Descubrimiento web independiente de las cuotas de Gemini y Groq.

    Bing RSS es solo un índice de URLs candidatas. Se exige descargar y
    validar la fuente original antes de emplearla como evidencia.
    """
    import xml.etree.ElementTree as ET
    consultas=[caso.get('titulo','') + ' aviation',
               ' '.join((caso.get('imagenes') or [])[:1]) + ' aviation safety']
    tema_id=caso.get('_episodio',{}).get('caso_id',caso.get('id',''))
    if tema_id=='future_03':
        consultas=['hydrogen aircraft fuel cells cryogenic storage EASA Airbus NASA',
                   'hydrogen aviation airport refuelling certification technical']
    if tema_id=='safe_10':
        consultas=['go around rejected landing aviation safety EASA FAA',
                   'go around stabilised approach flight safety']
    urls=[]; errores=[]; vistos=set()
    for consulta in consultas[:2]:
        try:
            r=session.get('https://www.bing.com/search',
                          params={'q':consulta,'format':'rss'},
                          timeout=(5,11), headers={
                              'User-Agent':'AEROFACTUM/4.8 (+https://acesped.github.io/aerofactum/)'
                          })
            r.raise_for_status()
            raiz=ET.fromstring(r.content)
            for item in raiz.findall('.//item')[:8]:
                url=_url_publica_investigacion(item.findtext('link'))
                if not url or url in vistos or 'bing.com' in urlparse(url).hostname:
                    continue
                vistos.add(url)
                urls.append((url,(item.findtext('title') or 'Búsqueda web')[:120]))
        except Exception as exc:
            errores.append('Bing RSS: '+type(exc).__name__+': '+str(exc)[:110])
    return urls[:AERO_BUSQUEDA_MAX_URLS], errores


# =================== INVESTIGACIÓN DOCUMENTAL 4.9 ===================
# Esta capa reemplaza exclusivamente la investigación fallida, preservando
# el motor original de catálogo, narración, música, edición y publicación.

AERO_FUENTES_DOMINIOS_PREFERENTES = (
    'iata.org', 'icao.int', 'faa.gov', 'easa.europa.eu', 'nasa.gov',
    'eurocontrol.int', 'bts.gov', 'transtats.bts.gov', 'ntsb.gov',
    'airlines.org', 'airbus.com', 'boeing.com', 'skybrary.aero', 'ntrs.nasa.gov',
    'caa.co.uk', 'atsb.gov.au', 'mit.edu', 'lufthansagroup.com', 'fca.org.uk', 'easyjet.com'
)

# Fuentes primarias comprobadas para tecnologías aeronáuticas específicas.
# Las URL son candidatas; su contenido debe descargarse y pasar la validación.
FUENTES_DIRECTAS_TECNOLOGIA = {
    'future_03': [
        ('EASA: Hydrogen-powered Aircraft — tecnología y ensayos',
         'https://www.easa.europa.eu/en/domains/environment/eaer/technology-and-design/low-carbon-emissions-aircraft/hydrogen-powered'),
        ('Airbus: Hydrogen — almacenamiento y aviación comercial',
         'https://www.airbus.com/en/innovation/energy-transition/hydrogen'),
        ('Airbus: ZEROe — propulsión con hidrógeno',
         'https://www.airbus.com/en/innovation/energy-transition/hydrogen/zeroe-our-hydrogen-powered-aircraft'),
        ('EASA: Hydrogen and its potential in aviation',
         'https://www.easa.europa.eu/en/light/topics/hydrogen-and-its-potential-aviation'),
        ('Airbus: Hydrogen Hubs at Airports',
         'https://www.airbus.com/en/innovation/energy-transition/hydrogen/hydrogen-hubs-at-airports'),
        ('NASA NTRS: Hydrogen-electric aircraft research (CHEETA)',
         'https://ntrs.nasa.gov/citations/20260001562'),
        ('EASA: Hydrogen aircraft certification workshop',
         'https://www.easa.europa.eu/en/newsroom-and-events/press-releases/easa-holds-first-international-workshop-certifying-hydrogen'),
    ],
}

FUENTES_DIRECTAS_ECONOMIA = {
    'fin_03': [
        ('Lufthansa Group: glosario del informe anual 2025', 'https://report.lufthansagroup.com/2025/annual-report/en/further-information/glossary/'),
        ('Lufthansa Group: resultados de aerolíneas de pasajeros 2025', 'https://report.lufthansagroup.com/2025/annual-report/en/combined-management-report/business-segments/passenger-airlines-business-segment/'),
        ('EasyJet: resultados y glosario publicados ante FCA', 'https://data.fca.org.uk/artefacts/NSM/RNS/5509367.html'),
    ],
    'fin_01': [
        ('IATA: Global Outlook for Air Transport, junio 2026',
         'https://www.iata.org/en/publications/economics/reports/global-outlook-for-air-transport-june-2026/'),
        ('IATA: Informe económico completo, junio 2026',
         'https://www.iata.org/en/iata-repository/publications/economic-reports/global-outlook-for-air-transport-june-2026/'),
        ('IATA: Global Outlook, diciembre 2025',
         'https://www.iata.org/en/iata-repository/publications/economic-reports/global-outlook-for-air-transport-december-2025/'),
        ('BTS: Airline Operating Costs',
         'https://www.transtats.bts.gov/'),
    ],
    'fin_05': [
        ('IATA: Global Outlook for Air Transport, junio 2026',
         'https://www.iata.org/en/publications/economics/reports/global-outlook-for-air-transport-june-2026/'),
        ('IATA: Informe económico completo, junio 2026',
         'https://www.iata.org/en/iata-repository/publications/economic-reports/global-outlook-for-air-transport-june-2026/'),
        ('BTS: Airline Fuel Cost and Consumption',
         'https://www.transtats.bts.gov/fuel.asp'),
    ],
}

def _tema_id_actual(caso):
    return (caso.get('_episodio') or {}).get('caso_id',caso.get('id',''))


def _es_financiero(caso):
    return caso.get('categoria') == 'FINANZAS Y ECONOMÍA'


def _relevancia_documento(texto, caso):
    """Relevancia basada en CONCEPTOS, no en palabras triviales como 'jet'."""
    import unicodedata
    t=''.join(c for c in unicodedata.normalize('NFKD',str(texto).lower())
              if not unicodedata.combining(c))
    tema=_tema_id_actual(caso)
    if _es_financiero(caso):
        terminos_economicos=(
            r'operating costs?', r'operating expenses?', r'non[- ]fuel costs?',
            r'fuel costs?', r'jet fuel prices?', r'profitability', r'net profit',
            r'operating profit', r'net margin', r'operating margin', r'earnings',
            r'cost per available seat', r'cask', r'rask', r'load factor',
            r'fleet utilization', r'lease rates?', r'airline revenues?',
            r'costos? operativos?', r'gastos? operativos?',
            r'rentabilidad', r'margen(?:es)?', r'ingresos', r'combustible'
        )
        contexto=(r'airlines?',r'air carriers?',r'air transport',r'aviation',
                  r'aircraft',r'industria aerea',r'aerolineas?',r'aeronautic')
        especiales={
            'fin_01':(r'operating costs?',r'operating expenses?',r'profitability',
                      r'non[- ]fuel costs?',r'fuel costs?',r'fixed costs?',
                      r'profit margin',r'lease rates?',r'costos?'),
            'fin_05':(r'jet fuel',r'fuel costs?',r'fuel expenses?',
                      r'aviation fuel',r'combustible',r'queroseno'),
            'fin_02':(r'cask',r'cost per available seat',r'unit cost'),
            'fin_03':(r'rask',r'revenue per available seat',r'unit revenue'),
            'fin_04':(r'load factor',r'passenger load factor'),
            'fin_06':(r'aircraft leas',r'lease rates?',r'ownership',r'leasing'),
            'fin_07':(r'airline revenues?',r'ancillary revenues?',r'cargo revenues?'),
            'fin_08':(r'passenger yield',r'yield',r'ticket prices?'),
            'fin_09':(r'route profitability',r'break[- ]even',r'route economics'),
            'fin_10':(r'utilization',r'utilisation',r'fleet utilization'),
        }
        econ=sum(bool(re.search(p,t)) for p in terminos_economicos)
        ambito=sum(bool(re.search(p,t)) for p in contexto)
        especifico=sum(bool(re.search(p,t)) for p in especiales.get(tema,()))
        if tema=='fin_03' and especifico and re.search(r'available seat[- ]kilomet|seat[- ]kilomet|revenue per ask|passenger airlines?',t) and re.search(r'\b(?:rask|unit revenues?|revenue per available seat|revenue per ask)\b',t):
            return 8 + 2*especifico
        if not (ambito and econ and especifico):return 0
        return econ + 2*especifico
    if tema == 'future_03':
        # Ni una página genérica sobre aviación ni una sobre hidrógeno de
        # automóviles basta: exigir el concepto + contexto de vuelo + tecnología.
        hidrogeno = re.search(r'\b(?:hydrogen|hidrogeno|\bh2\b|\blh2\b)\b', t)
        aviacion = re.search(
            r'\b(?:aviation|aviacion|aircraft|airplane|aeroplane|'
            r'aeronautic\w*|aeronave\w*|airports?|aeropuertos?|'
            r'flight|flights|vuelos?|zeroe)\b', t)
        tecnicos = (
            r'fuel cells?', r'pilas? de combustible', r'propulsion',
            r'cryogenic', r'criogenic', r'liquid hydrogen',
            r'hidrogeno liquido', r'hydrogen storage',
            r'storage tanks?', r'almacenamiento', r'refuell?ing',
            r'combustion', r'certification', r'certificacion',
            r'hydrogen-powered', r'hydrogen-electric',
            r'powertrain', r'infrastructure', r'infraestructura',
            r'distribution', r'distribucion', r'emissions?',
        )
        puntos = sum(bool(re.search(x,t)) for x in tecnicos)
        return puntos + 2 if hidrogeno and aviacion and puntos >= 2 else 0
    # Para temas no financieros conservar las salvaguardas originales por tema.
    tokens=_tokens_tema(caso)
    matches={x for x in tokens if re.search(r'\b'+re.escape(x)+r'\b',t)}
    if tema=='meteo_03' and not re.search(r'wind[ -]?shear|windshear|microburst|downburst|cizalladura',t):
        return 0
    if tema=='ops_09' and not re.search(r'(?:take[ -]?off|departure|preflight|flight crew) briefing|briefing de (?:salida|despegue)',t):
        return 0
    if tema=='future_05' and not re.search(r'composites?|carbon fib(?:er|re)|fiberglass|laminate|materiales compuestos',t):
        return 0
    return len(matches)


def _extraer_pdf_oficial(response, caso):
    """Extrae texto contextual de PDF primario, sin perder citas literales."""
    from io import BytesIO
    from urllib.parse import urlparse
    import pypdf
    host=(urlparse(response.url).hostname or '').lower()
    if not any(host==d or host.endswith('.'+d)
               for d in AERO_FUENTES_DOMINIOS_PREFERENTES):return ''
    if len(response.content)>23_000_000:return ''
    try:
        lector=pypdf.PdfReader(BytesIO(response.content),strict=False)
        partes=[]
        for i,pagina in enumerate(lector.pages):
            if i>=min(len(lector.pages),110):break
            texto=re.sub(r'\s+',' ',pagina.extract_text() or '').strip()
            if len(texto)<120:continue
            score=_relevancia_documento(texto,caso)
            if score:partes.append((score,i,texto))
        partes.sort(key=lambda x:(-x[0],x[1]))
        if not partes:return ''
        # Fragmentos continuos, completos y reproducibles en el campo de evidencia.
        salida=[]
        for score,i,txt in partes[:6]:
            salida.append(f'[Página {i+1}] '+txt[:3600])
            if sum(map(len,salida))>=14000:break
        return ' '.join(salida)[:16500]
    except Exception as e:
        print('  PDF no extraíble:',type(e).__name__,str(e)[:140],flush=True)
        return ''


def _leer_documento_web(session,url,caso,origen):
    """HTTP limitado, extracción PDF/HTML y validación temática real."""
    from urllib.parse import urlparse
    from urllib.parse import urljoin
    from bs4 import BeautifulSoup
    from io import BytesIO
    url=_url_publica_investigacion(url)
    if not url:return None
    try:
        with session.get(url,timeout=(8,30),allow_redirects=True,stream=True,
                         headers={'User-Agent':'AEROFACTUM/4.9 (https://acesped.github.io/aerofactum/; ari.cesped@gmail.com)'}) as r:
            r.raise_for_status()
            final=_url_publica_investigacion(r.url)
            if not final:return None
            mime=r.headers.get('Content-Type','').lower()
            es_pdf='pdf' in mime or urlparse(final).path.lower().endswith('.pdf')
            limite=23_000_000 if es_pdf else 2_500_000
            if int(r.headers.get('Content-Length') or 0)>limite:return None
            contenido=bytearray()
            for trozo in r.iter_content(chunk_size=65536):
                contenido.extend(trozo)
                if len(contenido)>limite:return None
            if es_pdf:
                class RespuestaPDF:pass
                resp=RespuestaPDF();resp.url=final;resp.content=bytes(contenido)
                texto=_extraer_pdf_oficial(resp,caso)
            elif 'html' in mime or 'text/plain' in mime or not mime:
                raw=bytes(contenido).decode(r.encoding or 'utf-8','replace')
                texto=_limpiar_texto_web(raw,mime)
                # En artículos IATA el cuerpo completo a menudo está fuera de <main>.
                if _relevancia_documento(texto,caso)<1:
                    soup=BeautifulSoup(raw,'html.parser')
                    for tag in soup(['script','style','nav','footer','header','svg']):tag.decompose()
                    texto=re.sub(r'\s+',' ',soup.get_text(' ',strip=True))[:23000]
            else:return None
        score=_relevancia_documento(texto,caso)
        if len(texto)<450 or score<1:
            print(f'  Fuente descartada: texto={len(texto)}; relevancia={score}; URL={final[:105]}',flush=True)
            return None
        return {'id':'','nombre':origen[:120],'url':final,
                'fecha_consulta':datetime.now(timezone.utc).isoformat(),
                'texto':texto[:16500],'coincidencias_tema':score}
    except Exception as e:
        print('  Fuente no recuperable:',url[:110],type(e).__name__,str(e)[:110],flush=True)
        return None


# ==================== AEROFACTUM 5.3: INVESTIGACIÓN UNIVERSAL ====================
# No hay dependencias adicionales respecto de la versión 4.9.
# El cache almacena respuestas DOCUMENTALES, nunca conclusiones de IA.

class EpisodioRecuperable(RuntimeError):
    """Fallo anterior a la publicación que permite intentar otro tema."""

# Grupos bilingües de términos técnicos; se exigen como CONJUNTOS, no keywords vagas.
AERO_VOCABULARIO = {
 'aero': [('lift','sustentacion','aerodynamic','aerodinamica','airfoil','ala'),('angle of attack','stall','wing','aircraft','drag')],
 'motor': [('engine','turbofan','turbine','powerplant','hydraulic','pressure','cabin','apu','landing gear','electrical'),('aircraft','aviation','flight','airplane','aeronave')],
 'nav': [('instrument','navigation','airspeed','altimeter','attitude','pitot','transponder','ils','vor','gnss','rnav','rnp'),('flight','aircraft','pilot','aviation','cockpit')],
 'meteo': [('wind','weather','meteorology','turbulence','icing','metar','taf','thunderstorm','visibility','dew point'),('aviation','flight','aircraft','airport','pilot')],
 'ops': [('takeoff','landing','runway','flight','fuel','checklist','briefing','performance','weight and balance'),('aircraft','pilot','airline','aeropuerto')],
 'safe': [('safety','crew','fatigue','risk','human factors','go around','situational awareness','crm','sms'),('aviation','flight','pilot','aircraft','airline')],
 'fin': [('airline','air transport','aviation','aircraft','aerolineas'),('operating costs','revenue','fuel costs','profit','cost','lease','yield','load factor')],
 'atc': [('air traffic control','airport','runway','tower','taxi','flight dispatch','slot','airspace'),('aircraft','aviation','flight','airline','aeropuerto')],
 'mnt': [('maintenance','airworthiness','inspection','corrosion','repair','mel','borescope','certification','engine'),('aircraft','aviation','airplane','aeronave')],
 'future': [('sustainable aviation','hydrogen','electric aircraft','composite','supersonic','flight testing','simulator','drone','automation'),('aircraft','aviation','flight','aeronautic')],
}
AERO_CONCEPTOS = {
 'motor_07': ('cabin pressurization','cabin pressure','pressurized cabin','pressurization',
              'pressurisation','cabina presurizada','presurizacion','cabin altitude',
              'outflow valve','differential pressure','hypoxia'),
 'future_03': ('hydrogen aircraft','hydrogen aviation','hydrogen-powered','liquid hydrogen',
               'hydrogen fuel cell','hidrogeno aeronaves','hydrogen propulsion'),
}
AERO_CAPITULOS_FAA = {
 'aero': ('https://www.faa.gov/regulations_policies/handbooks_manuals/aviation/phak',),
 'motor': ('https://www.faa.gov/regulations_policies/handbooks_manuals/aviation/phak',),
 'nav': ('https://www.faa.gov/regulations_policies/handbooks_manuals/aviation/phak',),
 'meteo': ('https://www.faa.gov/regulations_policies/handbooks_manuals/aviation/phak',),
 'ops': ('https://www.faa.gov/regulations_policies/handbooks_manuals/aviation/airplane_handbook',),
}
AERO_FUENTES_TEMATICAS_EXTRA = {
 'motor_07': [
   ('FAA: PHAK — Aircraft Systems, capítulo 7',
    'https://www.faa.gov/regulations_policies/handbooks_manuals/aviation/phak'),
   ('FAA: PHAK, capítulo 7 — Aircraft Systems PDF',
    'https://www.faa.gov/sites/faa.gov/files/09_phak_ch7.pdf'),
   ('FAA: PHAK, capítulo 11 — Aircraft Performance PDF',
    'https://www.faa.gov/sites/faa.gov/files/13_phak_ch11.pdf'),
 ],
}

def _aero_norm(t):
    import unicodedata
    return ''.join(c for c in unicodedata.normalize('NFKD',str(t).lower())
                   if not unicodedata.combining(c))

def _aero_tema_grupo(caso):
    return _tema_id_actual(caso).split('_')[0]

def _aero_consultas(caso):
    """Consultas en inglés basadas en títulos + vocabulario, sin palabras genéricas solas."""
    tema=_tema_id_actual(caso)
    terminos=AERO_CONCEPTOS.get(tema)
    primero=(caso.get('imagenes') or [caso['titulo']])[0]
    principal=terminos[0] if terminos else primero
    return list(dict.fromkeys([
      f'{principal} site:faa.gov aviation',
      f'{principal} site:nasa.gov aircraft',
      f'{principal} site:easa.europa.eu aviation',
      f'{principal} aviation technical pdf',
      f'{primero} aircraft systems aviation',
    ]))

# Vocabulario genérico que NO sirve por sí solo como prueba documental.
_AERO_STOP_TEMATICO = set('aircraft airplane airliner aeroplane aviation airport airports flight flights pilots pilot system systems aviation safety airplane engine engines maintenance technical technology photograph photo aircrafts and with from into about ground aviation general commercial control international information aircraft airplane'.split())
_AERO_TERMINOS_POR_TEMA = {
 'mnt_02':('inspection','inspections','maintenance inspection','aircraft inspection','airworthiness inspection','inspeccion','inspecciones'),
 'motor_02':('compressor','compressors','compressor stage','axial compressor','centrifugal compressor','compresor'),
 'motor_08':('aircraft electrical','electrical power','electrical system','aircraft generator','power distribution','electrical bus','busbar','alternator','sistema electrico'),
 'meteo_04':('icing','ice accretion','airframe icing','aircraft icing','ice protection','engelamiento','hielo','de-icing','anti-icing'),
 'meteo_09':('fog','visibility','rvr','runway visual range','low visibility','niebla','visibilidad'),
 'motor_07': AERO_CONCEPTOS['motor_07'],
 'future_03': AERO_CONCEPTOS['future_03'],
}

# AEROFACTUM 5.3: fuentes primarias directas por tema. No son evidencia
# automática: se descargan, se examinan y deben superar relevancia contextual.
AERO_FUENTES_TEMATICAS_EXTRA.update({
 'nav_01': [('FAA PHAK: Flight Instruments, capítulo 8 (PDF)',
             'https://www.faa.gov/sites/faa.gov/files/regulations_policies/handbooks_manuals/aviation/phak/10_phak_ch8.pdf')],
 'nav_02': [('FAA PHAK: Altimeter, Flight Instruments (PDF)',
             'https://www.faa.gov/sites/faa.gov/files/regulations_policies/handbooks_manuals/aviation/phak/10_phak_ch8.pdf')],
 'nav_03': [('FAA PHAK: Attitude Indicator, Flight Instruments (PDF)',
             'https://www.faa.gov/sites/faa.gov/files/regulations_policies/handbooks_manuals/aviation/phak/10_phak_ch8.pdf')],
 'nav_04': [('FAA PHAK: Pitot-static, Flight Instruments (PDF)',
             'https://www.faa.gov/sites/faa.gov/files/regulations_policies/handbooks_manuals/aviation/phak/10_phak_ch8.pdf')],
 'nav_07': [('FAA AIP: VOR navigation and RNAV, ENR 4.1',
             'https://www.faa.gov/air_traffic/publications/atpubs/aip_html/part2_enr_section_4.1.html'),
            ('FAA PHAK: VOR and navigation, chapter 8 (PDF)',
             'https://www.faa.gov/sites/faa.gov/files/regulations_policies/handbooks_manuals/aviation/phak/10_phak_ch8.pdf')],
 'nav_08': [('FAA AIM: PBN and RNAV',
             'https://www.faa.gov/air_traffic/publications/aim_html/chap1_section_2.html')],
 'nav_09': [('FAA AIM: Performance-Based Navigation / RNAV',
             'https://www.faa.gov/air_traffic/publications/aim_html/chap1_section_2.html'),
            ('FAA AIP: Area Navigation, ENR 4.1',
             'https://www.faa.gov/air_traffic/publications/atpubs/aip_html/part2_enr_section_4.1.html'),
            ('FAA: RNAV routes and procedures',
             'https://www.faa.gov/air_traffic/publications/atpubs/pham_html/chap20_section_5.html')],
 'nav_10': [('FAA AIM: RNAV/RNP and PBN',
             'https://www.faa.gov/air_traffic/publications/aim_html/chap1_section_2.html')],
 'motor_01': [('FAA AMT Powerplant: turbofan and engine components (PDF)',
               'https://www.faa.gov/sites/faa.gov/files/03_amtp_ch1.pdf')],
 'motor_02': [('FAA AMT Powerplant: engine compressors (PDF)',
               'https://www.faa.gov/sites/faa.gov/files/03_amtp_ch1.pdf'),
              ('FAA: Aircraft Engine Operation and Malfunction (PDF)',
               'https://www.faa.gov/sites/faa.gov/files/aircraft/air_cert/design_approvals/engine_prop/engine_malf_famil.pdf')],
 'motor_03': [('FAA AMT Powerplant: turbines and engine operation (PDF)',
               'https://www.faa.gov/sites/faa.gov/files/03_amtp_ch1.pdf')],
 'motor_04': [('FAA AMT Powerplant: Turbofan bypass ratio (PDF)',
               'https://www.faa.gov/sites/faa.gov/files/03_amtp_ch1.pdf'),
              ('FAA: Aircraft Engine Operation and Malfunction (PDF)',
               'https://www.faa.gov/sites/faa.gov/files/aircraft/air_cert/design_approvals/engine_prop/engine_malf_famil.pdf')],
 'motor_05': [('FAA AMT Powerplant: turboprop engine (PDF)',
               'https://www.faa.gov/sites/faa.gov/files/03_amtp_ch1.pdf')],
})

# Anclas específicas: no aceptar RNAV solo por menciones genéricas a navigation.
_AERO_TERMINOS_POR_TEMA.update({
 'nav_01': ('indicated airspeed','true airspeed','airspeed indicator','calibrated airspeed','ias','tas'),
 'nav_02': ('altimeter','barometric altimeter','pressure altitude','altimetro','altimetry','altimeter setting'),
 'nav_03': ('attitude indicator','artificial horizon','attitude gyro','horizonte artificial'),
 'nav_04': ('pitot-static','pitot static','pitot tube','static port','pitot tube pressure'),
 'nav_07': ('vor','vhf omnidirectional','vor station','vor radial','omnidirectional range'),
 'nav_08': ('gps','gnss','global positioning system','satellite navigation'),
 'nav_09': ('rnav','area navigation','area navigational'),
 'nav_10': ('rnp','required navigation performance'),
 'motor_01': ('turbofan','fan engine','bypass airflow'),
 'motor_02': ('compressor','compressors','axial compressor','compressor stage','centrifugal compressor'),
 'motor_03': ('turbine','turbines','turbine blades','gas turbine'),
 'motor_04': ('bypass ratio','bypass air','turbofan bypass','high bypass','bypass flow'),
 'motor_05': ('turboprop','propeller turbine','reduction gearbox'),
})

# Fuentes primarias FAA y texto normativo estadounidense reproducido por Cornell LII.
AERO_FUENTES_TEMATICAS_EXTRA.update({
 'mnt_03': [('FAA: Airworthiness Directives','https://www.faa.gov/aircraft/air_cert/continued_operation/ad'),
            ('FAA: AD responsibilities','https://www.faa.gov/aircraft/air_cert/continued_operation/ad/gen_resp')],
 'mnt_06': [('FAA AC 20-97B: Aircraft Tire Maintenance','https://www.faa.gov/sites/faa.gov/files/2022-11/AC20-97B.pdf'),
            ('FAA AC 20-97B: Aircraft Tire Maintenance and Operational Practices','https://www.faa.gov/regulations_policies/advisory_circulars/index.cfm/go/document.information/documentID/22044')],
 'mnt_07': [('14 CFR 121.563: Reporting mechanical irregularities (EE.UU., Cornell LII)','https://www.law.cornell.edu/cfr/text/14/121.563'),
            ('14 CFR 43.9: Maintenance records (EE.UU., Cornell LII)','https://www.law.cornell.edu/cfr/text/14/43.9'),
            ('14 CFR 91.417: Maintenance records (EE.UU., Cornell LII)','https://www.law.cornell.edu/cfr/text/14/91.417')],
 'atc_09': [('14 CFR 121.533: Operational control (EE.UU., Cornell LII)','https://www.law.cornell.edu/cfr/text/14/121.533'),
            ('14 CFR 121.601: Aircraft dispatcher information (EE.UU., Cornell LII)','https://www.law.cornell.edu/cfr/text/14/121.601')],
})
_AERO_TERMINOS_POR_TEMA.update({
 'fin_03': ('rask','unit revenue','unit revenues','revenue per available seat','revenue per ask','available seat-kilometres','available seat kilometres'),
 'mnt_03': ('airworthiness directive','airworthiness directives','directive de aeronavegabilidad','directiva de aeronavegabilidad'),
 'mnt_06': ('aircraft tire','aircraft tires','tire pressure','tire inflation','tyre pressure','tire maintenance','neumaticos'),
 'mnt_07': ('maintenance record','maintenance records','maintenance log','mechanical irregularities','technical log','aircraft log','registro tecnico'),
 'atc_09': ('aircraft dispatcher','aircraft dispatchers','flight dispatcher','dispatch release','operational control','despachador de vuelo'),
})

def _aero_anclas_especificas(caso):
    """Construye anclas por episodio; no confunde grupos con evidencia."""
    tema=_tema_id_actual(caso)
    if tema in _AERO_TERMINOS_POR_TEMA:
        return tuple(_aero_norm(x) for x in _AERO_TERMINOS_POR_TEMA[tema])
    # En otras fichas, los términos descriptivos ingleses del catálogo actúan
    # como palabras clave específicas; los sustantivos de dominio no cuentan.
    base=' '.join((caso.get('imagenes') or [])[:1])
    palabras=[x for x in re.findall(r'[a-z]{4,}',_aero_norm(base))
              if x not in _AERO_STOP_TEMATICO and x not in {'civil','closeup','interior','aerial','real'}]
    return tuple(dict.fromkeys(palabras))

def _aero_documento_relevante(texto,caso):
    """Exige evidencia del EPISODIO y no solo de su categoría.

    Se usa tanto con textos nuevos como con la caché. Las coincidencias
    léxicas no sustituyen la revisión factual de cada afirmación.
    """
    t=_aero_norm(texto)
    tema=_tema_id_actual(caso)
    if len(t)<180:return 0
    if tema=='future_03' or _es_financiero(caso):return _relevancia_documento(texto,caso)
    anclas=_aero_anclas_especificas(caso)
    hits=[x for x in anclas if re.search(r'(?<![a-z])'+re.escape(x)+r'(?![a-z])',t)]
    if not hits:return 0
    # Documentos de meteorología no deben acreditar mantenimiento ni sistemas.
    grupos=AERO_VOCABULARIO.get(_aero_tema_grupo(caso),())
    contexto=sum(bool(re.search(r'(?<![a-z])'+re.escape(x)+r'(?![a-z])',t)) for x in (grupos[1] if grupos else ()))
    if contexto==0 and not (tema.startswith('meteo_') and ('weather' in t or 'meteorolog' in t)):
        return 0
    if tema=='motor_07' and len(hits)<2:return 0
    if tema=='motor_08' and not any(x in t for x in ('electrical','electric','generator','alternator','power distribution','sistema electrico')):
        return 0
    if tema=='mnt_02' and not any(x in t for x in ('inspection','inspeccion')):return 0
    if tema=='meteo_04' and not any(x in t for x in ('icing','ice accretion','ice protection','de-icing','anti-icing','engelamiento')):return 0
    # Evitar aceptar páginas índice con un enlace a cada tema: se comprueban
    # pasajes contiguos más abajo en _aero_fragmentos.
    return 3*len(hits)+contexto

def _aero_fragmentos(texto,caso,limite=16500):
    """Selecciona pasajes técnicos, evitando validar por la portada entera."""
    texto=re.sub(r'\s+',' ',str(texto or '')).strip()
    ventana=2600;paso=1900;seleccion=[]
    if len(texto)<=ventana:
        return texto if _aero_documento_relevante(texto,caso)>0 else ''
    for i in range(0,len(texto),paso):
        parte=texto[i:i+ventana]
        if len(parte)<350:continue
        score=_aero_documento_relevante(parte,caso)
        if score:seleccion.append((score,i,parte))
    seleccion.sort(key=lambda x:(-x[0],x[1]))
    elegidos=[]
    for _,i,parte in seleccion:
        if all(abs(i-j)>=1200 for j in elegidos):elegidos.append(i)
        if len(elegidos)>=5:break
    if not elegidos:return ''
    return ' '.join(texto[i:i+ventana] for i in sorted(elegidos))[:limite]

def _aero_cache_archivo(url):
    return AERO_CACHE_DIR/(hashlib.sha256(url.encode('utf-8')).hexdigest()+'.json')

def _aero_cache_leer(url,caso):
    if not AERO_CACHE_DOCUMENTAL:return None
    try:
        p=_aero_cache_archivo(url)
        if not p.is_file():return None
        v=json.loads(p.read_text(encoding='utf-8'))
        if v.get('version')!=AERO_CACHE_VERSION:return None
        if time.time()-v.get('timestamp',0)>AERO_CACHE_DIAS*86400:return None
        texto=v['texto']
        fragmento=_aero_fragmentos(texto,caso)
        puntuacion=_aero_documento_relevante(fragmento,caso)
        if puntuacion<=0:return None
        return {'id':'','nombre':v.get('nombre','Biblioteca documental'),
                'url':v['url'],'fecha_consulta':v['fecha_consulta'],
                'texto':fragmento,'coincidencias_tema':puntuacion,'cache':True}
    except (OSError,ValueError,KeyError,TypeError):return None

def _aero_cache_guardar(url,nombre,texto):
    if not AERO_CACHE_DOCUMENTAL or len(texto)<450:return
    try:
        p=_aero_cache_archivo(url);p.parent.mkdir(parents=True,exist_ok=True)
        payload={'version':AERO_CACHE_VERSION,'url':url,'nombre':nombre,'texto':texto[:220000],
                 'timestamp':time.time(),'fecha_consulta':datetime.now(timezone.utc).isoformat()}
        temporal=p.with_suffix('.tmp')
        temporal.write_text(json.dumps(payload,ensure_ascii=False),encoding='utf-8')
        temporal.replace(p)
    except OSError as exc:print('  Cache no persistible:',str(exc)[:100],flush=True)

def _aero_extraer_pdf_completo(datos,caso):
    """Inspecciona hasta 180 páginas e indexa las secciones que mencionan el tema."""
    from io import BytesIO
    import pypdf
    lector=pypdf.PdfReader(BytesIO(datos),strict=False)
    segmentos=[]
    for i,pagina in enumerate(lector.pages[:min(180,len(lector.pages))]):
        try:pagina_txt=re.sub(r'\s+',' ',pagina.extract_text() or '').strip()
        except Exception:continue
        if len(pagina_txt)<120:continue
        # Las menciones del índice no bastan: deben existir textos relevantes.
        for inicio in range(0,len(pagina_txt),2800):
            frag=pagina_txt[inicio:inicio+3600]
            score=_aero_documento_relevante(frag,caso)
            if score>0 and len(frag)>350:
                segmentos.append((score,i,f'[Página {i+1}] '+frag))
    segmentos.sort(key=lambda x:(-x[0],x[1]))
    resultado=[];paginas=set()
    for score,pg,txt in segmentos:
        if pg in paginas:continue
        paginas.add(pg);resultado.append(txt)
        if len(resultado)>=5:break
    return ' '.join(resultado)[:16500]

def _aero_descargar_documento(session,url,caso,nombre):
    """Obtiene y verifica una fuente. Cache solo para textos efectivamente leídos."""
    from urllib.parse import urlparse
    url=_url_publica_investigacion(url)
    if not url:return None
    cached=_aero_cache_leer(url,caso)
    if cached:return cached
    # PDF grande: no descargar contenido arbitrario de dominios no técnicos.
    try:
        for intento in range(AERO_REINTENTOS_POR_FUENTE+1):
            try:
                with session.get(url,timeout=(7,25),stream=True,allow_redirects=True,
                      headers={'User-Agent':'AEROFACTUM/5.0 (https://acesped.github.io/aerofactum/; ari.cesped@gmail.com)'}) as r:
                    if r.status_code in (429,403,404):return None
                    if r.status_code in (500,502,503,504) and intento<AERO_REINTENTOS_POR_FUENTE:
                        time.sleep(1+intento);continue
                    r.raise_for_status()
                    final=_url_publica_investigacion(r.url)
                    if not final:return None
                    mime=r.headers.get('Content-Type','').lower()
                    es_pdf='pdf' in mime or urlparse(final).path.lower().endswith('.pdf')
                    maxbytes=24_000_000 if es_pdf else 3_000_000
                    if int(r.headers.get('Content-Length') or 0)>maxbytes:return None
                    chunks=bytearray()
                    for pedazo in r.iter_content(65536):
                        chunks.extend(pedazo)
                        if len(chunks)>maxbytes:return None
                    if es_pdf:
                        dominio=urlparse(final).hostname or ''
                        if not any(dominio==d or dominio.endswith('.'+d) for d in AERO_FUENTES_DOMINIOS_PREFERENTES):return None
                        texto=_aero_extraer_pdf_completo(bytes(chunks),caso)
                    elif 'html' in mime or 'text/plain' in mime or not mime:
                        raw=bytes(chunks).decode(r.encoding or 'utf-8','replace')
                        texto=_limpiar_texto_web(raw,mime)
                        if _aero_documento_relevante(texto,caso)==0 or _es_financiero(caso):
                            from bs4 import BeautifulSoup
                            sopa=BeautifulSoup(raw,'html.parser')
                            for tag in sopa(['script','style','nav','footer','header','noscript','svg','form']):tag.decompose()
                            texto=re.sub(r'\s+',' ',sopa.get_text(' ',strip=True))
                    else:return None
                    break
            except Exception as exc:
                if intento>=AERO_REINTENTOS_POR_FUENTE:
                    print('  Documento no disponible:',url[:95],str(exc)[:100],flush=True)
                    return None
                time.sleep(1+intento)
        txt=_aero_fragmentos(texto,caso)
        score=_aero_documento_relevante(txt,caso)
        if len(txt)<450 or score==0:
            print('  Fuente descartada por relevancia:',final[:110],flush=True)
            return None
        _aero_cache_guardar(url,nombre,texto)
        return {'id':'','nombre':nombre[:120],'url':final,
                'fecha_consulta':datetime.now(timezone.utc).isoformat(),
                'texto':txt[:16500],'coincidencias_tema':score,'cache':False}
    except Exception as exc:
        print('  Error de extracción:',url[:100],type(exc).__name__,str(exc)[:100],flush=True)
        return None

def _aero_descubrir_en_paginas_oficiales(session,caso,limite=16):
    """Explora PDFs de manuales y prioriza enlaces por capítulo/término técnico."""
    from bs4 import BeautifulSoup
    from urllib.parse import urljoin,urlparse
    grupo=_aero_tema_grupo(caso)
    semillas=list(AERO_CAPITULOS_FAA.get(grupo,()))
    candidatos=[];vistos=set()
    # Catalogar capítulos referenciados por sus títulos y nombres reales.
    for origen in semillas:
        try:
            with session.get(origen,timeout=(6,17)) as resp:
                if not resp.ok or 'html' not in resp.headers.get('Content-Type','text/html'):continue
                raiz=BeautifulSoup(resp.text,'html.parser')
                for a in raiz.find_all('a',href=True):
                    url=_url_publica_investigacion(urljoin(resp.url,a['href']))
                    if not url or url in vistos:continue
                    if not urlparse(url).path.lower().endswith('.pdf'):continue
                    host=urlparse(url).hostname or ''
                    if not (host=='faa.gov' or host.endswith('.faa.gov')):continue
                    titulo=a.get_text(' ',strip=True)
                    etiqueta=_aero_norm(titulo+' '+url)
                    tokens=_tokens_tema(caso)
                    relevancia=sum(1 for tk in tokens if tk in etiqueta)
                    # Chapter 7 Aircraft Systems contiene presurización.
                    if _tema_id_actual(caso)=='motor_07' and re.search(r'chapter[ -]?7|ch7|aircraft systems',etiqueta):relevancia+=10
                    candidatos.append((relevancia,url,titulo or 'FAA: capítulo técnico PDF'))
                    vistos.add(url)
        except Exception as exc:
            print('  Índice FAA no accesible:',str(exc)[:85],flush=True)
    candidatos.sort(key=lambda x:(-x[0],x[1]))
    # No inspeccionar cientos de PDFs genéricos por episodio.
    return [(nombre,url) for _,url,nombre in candidatos[:limite]]

def _aero_busqueda_rss_filtrada(session,caso):
    """RSS es índice no evidencia. Evita páginas Microsoft, reservas y comercios."""
    import xml.etree.ElementTree as ET
    consultas=_aero_consultas(caso)
    resultados=[];vistos=set()
    for consulta in consultas[:3]:
        try:
            r=session.get('https://www.bing.com/search',params={'q':consulta,'format':'rss'},timeout=(6,12))
            r.raise_for_status()
            for item in ET.fromstring(r.content).findall('.//item')[:12]:
                url=_url_publica_investigacion(item.findtext('link'))
                if not url or url in vistos:continue
                dominio=urlparse(url).hostname or ''
                if not any(dominio==d or dominio.endswith('.'+d) for d in AERO_FUENTES_DOMINIOS_PREFERENTES):continue
                titulo=item.findtext('title') or 'Documento técnico'
                if any(term in _aero_norm(titulo) for term in ('login','microsoft','flight booking','cheap tickets')):continue
                vistos.add(url);resultados.append((url,titulo[:120]))
        except Exception as e:print('  Buscador web opcional:',type(e).__name__,str(e)[:85],flush=True)
    return resultados[:AERO_BUSQUEDA_MAX_URLS]

def investigar_episodio(caso, carpeta, session):
    """Biblioteca local -> primarias específicas -> índices FAA -> IA -> RSS filtrado.
    Cada página se lee y verifica; ausencia de evidencia detiene la publicación.
    """
    carpeta=Path(carpeta);carpeta.mkdir(parents=True,exist_ok=True)
    documentos=[];vistos=set();rechazadas=[];errores_busqueda=[];consultas_ia=[]
    minimo=AERO_MIN_FUENTES;maximo=max(AERO_MAX_DOCUMENTOS,minimo)
    objetivo=min(maximo,max(minimo,2))
    tema=_tema_id_actual(caso)
    def probar(url,nombre):
        url=_url_publica_investigacion(url)
        if not url or url in vistos or len(documentos)>=maximo:return False
        vistos.add(url)
        doc=_aero_descargar_documento(session,url,caso,nombre)
        if doc and doc['url'] not in {d['url'] for d in documentos}:
            doc['id']='F'+str(len(documentos)+1)
            documentos.append(doc)
            print('  Evidencia:',doc['id'],doc['nombre'][:70],
                  '(cache)' if doc.get('cache') else '(web)',flush=True)
            return True
        rechazadas.append(url);return False
    for url in AERO_IA_URLS.split('|'):
        if url.strip():probar(url,'Fuente proporcionada')
    directas=(AERO_FUENTES_TEMATICAS_EXTRA.get(tema,[])+
              FUENTES_DIRECTAS_TECNOLOGIA.get(tema,[])+
              FUENTES_DIRECTAS_ECONOMIA.get(tema,[])+
              _rutas_documentacion_oficial(caso))
    for item in caso.get('fuentes',[]):
        if len(item)>=2:directas.append((item[0],item[1]))
    # Primero recursos primarios. Páginas índice se pueden rechazar, pero luego
    # se exploran capítulos específicos: no contabilizar índice como evidencia.
    for nombre,url in directas:
        if len(documentos)>=objetivo:break
        probar(url,nombre)
    if AERO_INVESTIGACION_UNIVERSAL and len(documentos)<objetivo:
        for nombre,url in _aero_descubrir_en_paginas_oficiales(session,caso,limite=8):
            if len(documentos)>=objetivo:break
            probar(url,nombre)
    if len(documentos)<minimo:
        for url,nombre in _aero_busqueda_rss_filtrada(session,caso):
            if len(documentos)>=maximo:break
            probar(url,nombre)
    # Buscar con LLM solo si las fuentes gratuitas y directas no alcanzan.
    if len(documentos)<minimo:
        consultas_ia,errores_busqueda=_descubrir_fuentes_ia(caso)
        for url,nombre in consultas_ia:
            if len(documentos)>=maximo:break
            probar(url,nombre)
    reporte={'tema':caso['titulo'],'caso_id':tema,
             'fecha_utc':datetime.now(timezone.utc).isoformat(),
             'documentos_validos':len(documentos),'minimo':minimo,
             'urls_probadas':len(vistos),'urls_descartadas':rechazadas,
             'errores_descubrimiento':errores_busqueda,
             'candidatos_ia':[{'url':u,'nombre':n} for u,n in consultas_ia],
             'fuentes':[{'id':d['id'],'nombre':d['nombre'],'url':d['url'],
                         'puntuacion':d['coincidencias_tema'],'cache':d.get('cache',False),
                         'extracto':d['texto'][:900]} for d in documentos]}
    (carpeta/'FUENTES_INVESTIGACION.json').write_text(
       json.dumps(reporte,ensure_ascii=False,indent=2),encoding='utf-8')
    if len(documentos)<minimo:
        raise EpisodioRecuperable(f'{tema}: {len(documentos)} fuentes técnicas legibles; '
            f'mínimo {minimo}. Diagnóstico: {carpeta/"FUENTES_INVESTIGACION.json"}')
    return documentos

def _limpiar_json_ia(texto):
    texto=(texto or '').strip()
    if texto.startswith('```'):
        texto=re.sub(r'^```(?:json)?\s*','',texto,flags=re.I)
        texto=re.sub(r'\s*```$','',texto)
    try:return json.loads(texto)
    except json.JSONDecodeError as original_error:
        ini=texto.find('{'); fin=texto.rfind('}')
        if ini>=0 and fin>ini:
            try:return json.loads(texto[ini:fin+1])
            except json.JSONDecodeError:pass
        # Corregir únicamente la sintaxis JSON, nunca inventar citas ni hechos.
        # El validador posterior sigue comprobando cada cita literalmente.
        try:
            from json_repair import repair_json
            candidato=repair_json(texto,return_objects=True)
            if isinstance(candidato,dict) and candidato.get('bloques'):
                return candidato
        except (ImportError,ValueError,TypeError,KeyError):pass
        raise ValueError('JSON incompleto o no recuperable: '+str(original_error)[:200])


def _consultar_gemini(prompt):
    import requests
    from urllib.parse import quote
    key=os.getenv('GEMINI_API_KEY','').strip()
    if not key:raise RuntimeError('GEMINI_API_KEY no configurada')
    endpoint='https://generativelanguage.googleapis.com/v1beta/models/'+quote(GEMINI_MODELO,safe='')+':generateContent'
    payload={'contents':[{'role':'user','parts':[{'text':prompt}]}],
             'generationConfig':{'temperature':0.55,'maxOutputTokens':8192,
                                 'responseMimeType':'application/json'}}
    res=requests.post(endpoint,headers={'x-goog-api-key':key,'Content-Type':'application/json'},
                      json=payload,timeout=(10,AERO_IA_TIMEOUT))
    if not res.ok:raise RuntimeError(f'Gemini HTTP {res.status_code}: '+res.text[:350])
    data=res.json()
    candidatos=data.get('candidates') or []
    if not candidatos:raise RuntimeError('Gemini no devolvió candidatos.')
    partes=candidatos[0].get('content',{}).get('parts',[])
    texto=''.join(p.get('text','') for p in partes)
    return _limpiar_json_ia(texto)


_GROQ_TPM_REINTENTO_USADO = False


def _groq_demora_tpm(respuesta):
    if respuesta.status_code != 429:return None
    t = respuesta.text.lower()
    if any(p in t for p in ('tokens per day','requests per day','(tpd)','(rpd)')):return None
    if not any(p in t for p in ('tokens per minute','requests per minute','(tpm)','(rpm)','(itpm)','(otpm)')):return None
    try:
        demora = float(respuesta.headers.get('retry-after','60'))
    except (ValueError,TypeError):return None
    if not math.isfinite(demora) or not 0 <= demora <= 65:return None
    return max(1.0,demora)+0.5


def _consultar_groq(prompt):
    import requests
    key=os.getenv('GROQ_API_KEY','').strip()
    if not key:raise RuntimeError('GROQ_API_KEY no configurada')
    payload={'model':GROQ_MODELO,'messages':[
        {'role':'system','content':'Eres un redactor especializado en el nicho indicado. Responde solo JSON válido.'},
        {'role':'user','content':prompt}],
        'temperature':0.55,'max_completion_tokens':7000,
        'response_format':{'type':'json_object'}}
    global _GROQ_TPM_REINTENTO_USADO
    url='https://api.groq.com/openai/v1/chat/completions'
    headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'}
    res=requests.post(url,headers=headers,json=payload,timeout=(10,AERO_IA_TIMEOUT))
    demora=_groq_demora_tpm(res)
    if demora is not None and not _GROQ_TPM_REINTENTO_USADO:
        _GROQ_TPM_REINTENTO_USADO=True
        print(f'  Groq: límite por minuto; esperar {demora:.1f}s según Retry-After y reintentar una sola vez.',flush=True)
        time.sleep(demora)
        res=requests.post(url,headers=headers,json=payload,timeout=(10,AERO_IA_TIMEOUT))
    if not res.ok:raise RuntimeError(f'Groq HTTP {res.status_code}: '+res.text[:350])
    respuesta=res.json()['choices'][0]['message']['content']
    return _limpiar_json_ia(respuesta)


def _normalizar_evidencia(texto):
    import unicodedata
    texto=unicodedata.normalize('NFKC',str(texto))
    return re.sub(r'\s+',' ',texto).strip().casefold()


def _validar_titulo_youtube(datos, caso):
    """Título atractivo, informativo y conectado al tema original.

    No inventa noticias, resultados ni cifras; la revisión semántica final
    corresponde al editor, ya que la coincidencia lexical no comprueba hechos.
    """
    import unicodedata
    titulo = re.sub(r'\s+', ' ', str(datos.get('titulo_youtube', ''))).strip().strip('"“”')
    if not 32 <= len(titulo) <= 95:
        raise ValueError('titulo_youtube debe tener entre 32 y 95 caracteres.')
    if titulo.lower().startswith(('qué es ', 'que es ', 'todo sobre ', 'introducción a ', 'introduccion a ')):
        raise ValueError('Título demasiado genérico: debe despertar curiosidad mediante un hecho o pregunta concreta.')
    if re.search(r'[#\n\r]|(?:https?://)|[!]{2,}', titulo):
        raise ValueError('Título con hashtags, URL o puntuación sensacionalista.')
    prohibidos = ('no lo vas a creer', 'nadie te cuenta', 'te dejará sin palabras',
                  'te dejara sin palabras', 'impactante revelación', 'impactante revelacion',
                  'secreto oculto', '100% garantizado')
    normal = ''.join(c for c in unicodedata.normalize('NFKD',titulo.casefold()) if not unicodedata.combining(c))
    if re.search(r'\b(?:videos? de la faa|pagina de la faa|sitio web de la faa|'
                 r'fuentes? de la faa|manuales? de la faa)\b', normal):
        raise ValueError('Título centrado en la fuente, no en el fenómeno aeronáutico.')
    if any(x in normal for x in prohibidos):
        raise ValueError('Título con clickbait no verificable.')
    original = ''.join(c for c in unicodedata.normalize('NFKD',caso['_titulo_caso'].casefold()) if not unicodedata.combining(c))
    palabras_clave = {w for w in re.findall(r'[a-z0-9]+',original) if len(w)>=5 and w not in {
        'porque','cuando','donde','sobre','entre','importa','funciona','explicado','aviones','aviacion'}}
    if palabras_clave and not any(w in normal for w in palabras_clave):
        raise ValueError('Título no menciona ningún concepto identificable del tema; mantén un término técnico central.')
    return titulo


def _aero_citas_preseleccionadas(documentos,caso):
    """Extrae fragmentos literales de documentos; NO genera ni infiere evidencia.

    El modelo puede referirse a C1, C2, etc. y el programa sustituye la
    referencia por el texto REAL de la fuente. Una cita no prueba por sí sola
    que la afirmación sea verdadera: el guion sigue sujeto a revisión.
    """
    import unicodedata
    anclas=_aero_anclas_especificas(caso)
    candidatas=[]
    for doc in documentos[:AERO_IA_MAX_FUENTES_PROMPT]:
        texto=str(doc.get('texto') or '')[:AERO_IA_CARACTERES_FUENTE]
        # El texto ya fue recuperado de una fuente y seleccionado por relevancia.
        # Cortar al final de oración o en límites de bloque, nunca fabricar citas.
        trozos=re.split(r'(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÑ0-9])|\n{2,}',texto)
        vistos=set()
        for trozo in trozos:
            q=re.sub(r'\s+',' ',trozo).strip()
            if len(q)<65:continue
            if len(q)>420:
                # No recortar fragmentos en mitad de una frase: omitirlos.
                continue
            if q.casefold() in vistos:continue
            vistos.add(q.casefold())
            qnorm=''.join(c for c in unicodedata.normalize('NFKD',q.casefold()) if not unicodedata.combining(c))
            valor=sum(3 for palabra in anclas if palabra in qnorm)
            valor+=sum(1 for word in ('aircraft','flight','pilot','aviation','engine','navigation','weather') if word in qnorm)
            candidatas.append((valor,doc['id'],q))
    candidatas.sort(key=lambda x:-x[0])
    resultado=[];por_fuente={}
    for score,sid,q in candidatas:
        if por_fuente.get(sid,0)>=max(5,AERO_IA_MIN_DATOS):continue
        if not score:continue
        resultado.append({'cita_id':'C'+str(len(resultado)+1),'fuente_id':sid,'cita_textual':q})
        por_fuente[sid]=por_fuente.get(sid,0)+1
        if len(resultado)>=AERO_IA_CITAS_PRESELECCIONADAS:break
    return resultado


def _aero_resolver_citas_ia(datos,citas):
    """Resuelve IDs exclusivamente contra pasajes literales recuperados."""
    if not isinstance(datos,dict):return datos
    indice={c['cita_id']:c for c in citas}
    for hecho in datos.get('hechos_con_evidencia',[]) or []:
        if not isinstance(hecho,dict):continue
        cid=str(hecho.get('cita_id') or '').strip().upper()
        if cid in indice:
            original=indice[cid]
            hecho['fuente_id']=original['fuente_id']
            hecho['cita_textual']=original['cita_textual']
    return datos


def _limpiar_etiquetas_locucion(texto):
    return re.sub(r'(?im)(^|(?<=[.!?])\s+)(?:hecho|evidencia|pista)\s*(?:n[uú]mero\s*)?\d+\s*:\s*', r'\1', str(texto)).strip()

def _validar_guion_ia(datos,documentos,caso):
    """Validación estructural, antigenericidad y citas textuales.

    Una cita localizada no prueba que cada afirmación narrada esté verificada.
    """
    if not isinstance(datos,dict):raise ValueError('Respuesta IA no es JSON objeto.')
    hechos=datos.get('hechos_con_evidencia',[])
    if not isinstance(hechos,list) or len(hechos)<AERO_IA_MIN_DATOS:
        raise ValueError(f'Se requieren {AERO_IA_MIN_DATOS} hechos con evidencia textual.')
    fuentes={d['id']:d for d in documentos}
    referencias=set(); citas_usadas=set()
    for hecho in hechos:
        if not isinstance(hecho,dict):raise ValueError('Hecho mal estructurado')
        sid=hecho.get('fuente_id');cita=str(hecho.get('cita_textual','')).strip()
        afirmacion=str(hecho.get('afirmacion','')).strip()
        if sid not in fuentes or len(cita)<28 or len(afirmacion)<25:
            raise ValueError('Hecho sin fuente válida, cita o afirmación detallada.')
        if _normalizar_evidencia(cita) not in _normalizar_evidencia(fuentes[sid]['texto']):
            raise ValueError(f'Cita del hecho no localizada literalmente en fuente {sid}.')
        citas_usadas.add(_normalizar_evidencia(cita))
        referencias.add(sid)
    if len(citas_usadas)<AERO_IA_MIN_DATOS:raise ValueError('Se requieren citas textuales distintas, no repetir una cita para varios hechos.')
    bloques=datos.get('bloques')
    tipos=['gancho','pregunta','contexto','pista','analisis','desarrollo','aplicacion','conclusion']
    if not isinstance(bloques,list) or [b.get('tipo') for b in bloques if isinstance(b,dict)]!=tipos:
        raise ValueError('El guion IA requiere ocho bloques en orden: '+', '.join(tipos))
    frases=[]; total=0
    prohibidas=['este contenido es educativo','no sustituye manuales aprobados',
                'la aviacion es fascinante','el conocimiento detras de cada vuelo',
                'es muy importante','en resumen, es importante']
    for b in bloques:
        txt=re.sub(r'\s+',' ',_limpiar_etiquetas_locucion(b.get('texto',''))).strip()
        b['texto']=txt
        palabras=txt.split();total+=len(palabras)
        if len(palabras)<14 or len(palabras)>160:
            raise ValueError('Bloque '+b['tipo']+' demasiado corto/largo ('+str(len(palabras))+' palabras).')
        norm=_normalizar_evidencia(txt)
        # Datos de verificación internos nunca deben escucharse en la narración.
        if re.search(r'\b(?:hecho|evidencia)\s*(?:n[uú]mero\s*)?\d+\b|\bpista\s+n[uú]mero\s*\d+\s*:', txt, re.I) or re.search(r'\b(?:fuente\s+F\d+|cita\s+C\d+)\b',txt,re.I):
            raise ValueError('El guion está enumerando hechos o citas de verificación en la locución.')
        if any(x in norm for x in prohibidas):raise ValueError('Guion con frase genérica o advertencia eliminada.')
        frases.append(norm)
    if not AERO_PALABRAS_MIN_ACEPTABLE<=total<=AERO_PALABRAS_MAX:
        raise ValueError(f'Guion de {total} palabras fuera de objetivo ({AERO_PALABRAS_MIN_ACEPTABLE} a {AERO_PALABRAS_MAX}).')
    if total<AERO_PALABRAS_MIN:
        print(f'  Extensión: {total} palabras; por debajo del objetivo editorial {AERO_PALABRAS_MIN}, dentro del rango aceptable. Continuando validación.',flush=True)
    from difflib import SequenceMatcher
    for a in range(len(frases)):
        for b in range(a+1,len(frases)):
            if SequenceMatcher(None,frases[a],frases[b]).ratio()>.78:
                raise ValueError('Redundancia excesiva entre escenas '+str(a+1)+' y '+str(b+1))
    return [(b['tipo'],re.sub(r'\s+',' ',b['texto']).strip()) for b in bloques]


# Circuit breaker de disponibilidad por ejecución. No modifica cuotas ni oculta errores.
_AERO_IA_INHABILITADOS = {}

def _aero_motores_guion():
    opciones=['gemini','groq','openrouter'] if AERO_IA_MODO=='auto' else [AERO_IA_MODO]
    variables={'gemini':'GEMINI_API_KEY','groq':'GROQ_API_KEY','openrouter':'OPENROUTER_API_KEY'}
    return [m for m in opciones if os.getenv(variables[m],'').strip() and m not in _AERO_IA_INHABILITADOS]

def _aero_error_proveedor(motor,mensaje):
    """Solo inhabilita fallos de proveedor, NO rechazos editoriales del guion."""
    t=mensaje.lower()
    permanentes=('http 429','http 401','http 403','http 404','no configurada',
                 'rate limit','quota')
    temporales=('http 503','http 500','timed out','read timed out','timeout',
               'connectionerror','connection aborted')
    if any(x in t for x in permanentes+temporales):
        _AERO_IA_INHABILITADOS[motor]=mensaje[:350]
        print(f'  {motor}: deshabilitado para el resto de la ejecución por fallo de proveedor.',flush=True)
        return True
    return False


# ----------------- PAQUETE EDITORIAL 7.0 -----------------
def _viral_variantes_titulos(caso):
    """Hasta tres propuestas sin agregar afirmaciones nuevas. NO es un test A/B de YouTube."""
    principal=str(caso.get('titulo','')).strip()[:95]
    tecnico=str(caso.get('_titulo_caso') or principal).strip().rstrip('.?!')
    pool=[principal, f'{tecnico}: ¿qué explica realmente esta historia?',
          f'{tecnico}: los detalles que importan para entenderlo']
    variantes=[]
    for titulo in pool:
        titulo=re.sub(r'\s+',' ',titulo).strip()
        if len(titulo)>95:titulo=titulo[:95].rsplit(' ',1)[0].strip(' :')
        if 20<=len(titulo)<=100 and titulo.casefold() not in {v.casefold() for v in variantes}:
            variantes.append(titulo)
        if len(variantes)>=TITULOS_CANDIDATOS:break
    return variantes or [principal]


def _viral_pregunta_contextual(caso):
    """Pregunta editorial para comentarios, no sustituye hechos del guion."""
    tema=str(caso.get('_titulo_caso') or caso.get('titulo') or 'este tema').strip(' .?!')
    if _univ_es_terror():
        return f'¿Qué interpretación darías tú al misterio de {tema}? Te leo en los comentarios.'
    return f'¿Qué aspecto de {tema} te gustaría explorar con más detalle? Te leo en los comentarios.'


def _viral_evaluacion(caso,plan,fotos=None):
    """Reglas transparentes; nunca se anuncia como probabilidad de viralidad."""
    escenas=[(t,str(txt)) for t,txt in plan if t!='cta']
    if not escenas:return {'aprobado':False,'advertencias':['Sin escenas narrativas']}
    gancho=escenas[0][1].strip()
    total=sum(len(txt.split()) for _,txt in escenas)
    advertencias=[]
    if len(gancho.split())<14:advertencias.append('Gancho inicial demasiado corto')
    if re.search(r'^(hola|bienvenid[oa]s?|en este video|hoy vamos a|suscr[ií]bete)',gancho,re.I):
        advertencias.append('Gancho comienza con una introducción genérica')
    if not AERO_PALABRAS_MIN<=total<=AERO_PALABRAS_MAX:advertencias.append('Extensión fuera del rango editorial')
    if fotos is not None and len(fotos)<AERO_VISUALES_OBJETIVO:
        advertencias.append('Variedad visual inferior al objetivo editorial')
    longitud_titulo=len(str(caso.get('titulo','')))
    if not 32<=longitud_titulo<=95:advertencias.append('Longitud del título fuera del objetivo')
    return {'version':'8.0','nicho':NICHO,'tema':caso.get('_titulo_caso',caso.get('titulo')),
            'titulo':caso.get('titulo'),'escenas':len(escenas),'palabras':total,
            'palabras_gancho':len(gancho.split()),'visuales':len(fotos) if fotos is not None else None,
            'advertencias':advertencias,'aprobado':not advertencias,
            'aviso':'Evaluación editorial local; no predice clics, retención ni viralidad.'}


def _viral_guardar_paquete(caso,plan,carpeta,fotos=None):
    carpeta=Path(carpeta)
    datos=_viral_evaluacion(caso,plan,fotos)
    datos['titulos_candidatos']=_viral_variantes_titulos(caso)
    datos['pregunta_interaccion']=_viral_pregunta_contextual(caso) if PREGUNTA_FINAL_ESPECIFICA else ''
    datos['serie_sugerida']=str(caso.get('categoria') or NICHO) if GENERAR_SERIES_TEMATICAS else ''
    (carpeta/'PAQUETE_VIRAL.json').write_text(json.dumps(datos,ensure_ascii=False,indent=2),encoding='utf-8')
    return datos


def _viral_miniaturas(caso,fotos,carpeta):
    """Crea versiones locales para revisión, nunca activa A/B remoto inexistente."""
    if not MODO_VIRAL or MINIATURAS_CANDIDATAS<=1:return []
    import copy
    variantes=[]
    tecnico=str(caso.get('_titulo_caso') or caso['titulo']).strip().rstrip(' .?!')
    # Dos composiciones de texto distintas y concisas. Sin agregar hechos.
    recortado=' '.join(tecnico.split()[:7]).upper()
    propuestas=[f'LA HISTORIA DE {recortado}'[:54].rstrip(),
                f'¿QUÉ SABEMOS DE {recortado}?'[:54].rstrip(' ?')+'?']
    for k,propuesta in enumerate(propuestas[:MINIATURAS_CANDIDATAS-1],start=2):
        alternativa=dict(caso)
        alternativa['mini_titulo']=propuesta[:65]
        alternativa['_variante_miniatura']=k
        try:
            variantes.append(str(miniatura(alternativa,fotos,carpeta)))
        except Exception as ex:
            print('  Miniatura candidata opcional no disponible:',str(ex)[:160],flush=True)
    return variantes


def _viral_short_local(video,caso,carpeta):
    """Crea un teaser vertical opcional; no lo publica ni altera el vídeo principal."""
    if not GENERAR_SHORT_DERIVADO:return None
    carpeta=Path(carpeta)
    salida=carpeta/('SHORT_'+nombre_archivo_video(caso,'.mp4'))
    try:
        # La fuente es el propio video final: incluye subtítulos, voz y audio.
        # Es un teaser de apertura, NO se anuncia como historia independiente.
        vf='crop=608:1080:(in_w-608)/2:0,scale=1080:1920:flags=lanczos,format=yuv420p'
        ffmpeg(['ffmpeg','-y','-hide_banner','-loglevel','error',
                '-i',str(video),'-t',str(AERO_SHORT_DURACION_MAX),'-vf',vf,
                '-c:v','libx264','-preset','veryfast','-crf','23','-c:a','aac',
                '-b:a','128k','-movflags','+faststart',str(salida)])
        if not salida.is_file() or salida.stat().st_size<10000:raise RuntimeError('Short vacío')
        (carpeta/'SHORT_NOTA.txt').write_text(
            'Teaser vertical del video principal. Revisar encuadre, subtítulos y sentido narrativo antes de publicar. '
            'No se carga automáticamente a YouTube.\n',encoding='utf-8')
        return salida
    except Exception as exc:
        print('  Short opcional no generado:',str(exc)[:160],flush=True)
        return None


def _viral_analytics_instrucciones(carpeta):
    """Plantilla de seguimiento: no finge métricas ni requiere nuevos scopes OAuth."""
    if not HISTORIAL_RENDIMIENTO:return
    plantilla={'nicho':NICHO,'fecha_creacion_utc':datetime.now(timezone.utc).isoformat(),
        'youtube_id':None,'vistas':None,'impresiones':None,'ctr_impresiones':None,
        'duracion_media_segundos':None,'porcentaje_medio_visto':None,
        'retencion_30s':None,'comentarios':None,'suscriptores_obtenidos':None,
        'fuentes_trafico':None,'metricas_verificadas':False,
        'nota':'Valores nulos hasta consultar YouTube Analytics con OAuth analytics.readonly y permisos adecuados.'}
    (Path(carpeta)/'ANALYTICS_PENDIENTE.json').write_text(json.dumps(plantilla,ensure_ascii=False,indent=2),encoding='utf-8')

def generar_guion_investigado(caso,episodio,documentos,carpeta):
    """Sin plantillas: Gemini -> Groq -> OpenRouter; si fallan, detener."""
    if AERO_IA_MODO not in ('auto','gemini','groq','openrouter'):
        raise ValueError('AERO_IA_MODO debe ser auto, gemini, groq u openrouter')
    fuentes_prompt=[]
    for doc in documentos[:AERO_IA_MAX_FUENTES_PROMPT]:
        fuentes_prompt.append({'id':doc['id'],'titulo':doc['nombre'],
              'url':doc['url']})
    citas_preseleccionadas=_aero_citas_preseleccionadas(documentos,caso)
    if len({ _normalizar_evidencia(c['cita_textual']) for c in citas_preseleccionadas }) < AERO_IA_MIN_DATOS:
        raise EpisodioRecuperable('Documentación insuficiente: no hay suficientes citas literales distintas para redactar sin inventar.')
    historial_textos=[]
    try:
        for item in leer_historial(ruta_historial())[-8:]:
            if item.get('titulo'):historial_textos.append(item['titulo'])
    except Exception:pass
    instruccion={
       'tarea':f'Redacta un guion ORIGINAL de divulgación sobre {NICHO} en ESPAÑOL, nada de plantillas.',
       'tema':caso['titulo'], 'categoria':caso['categoria'],
       'idea_de_partida_no_verificada':caso['contexto'],
       'titulos_previos_para_no_repetir':historial_textos,
       'minimo_referencias_distintas':AERO_IA_MIN_DATOS,
       'objetivo_titulo':'Título humano atractivo y fiel a los hechos; distinto del nombre técnico de catálogo.',
       'objetivo_retencion':'Gancho en el primer enunciado; tensión o curiosidad creciente, recompensa al final sin engañar.',
       'tipo_narrativo': _curiosity_formato(caso),
       'enfoque': 'Una pregunta central concreta y una recompensa clara. Distingue hipótesis, ficción y hechos. No imites canales ni inventes sucesos.',
       'plan_visual':'Cada bloque debe describir un elemento concreto que pueda ilustrarse con recursos legales y pertinentes. Incluye en cada bloque un campo visual_query con 2 a 5 palabras concretas en inglés, fieles al texto, sin nombres inventados.',
       'fuentes_documentales':fuentes_prompt,
       'citas_verificadas_para_elegir':citas_preseleccionadas,
       'normas':[ 'Devuelve un objeto JSON, sin markdown ni texto externo.',
         'Incluye titulo_youtube: título en español de 32 a 95 caracteres, conectado con el tema y con un término central reconocible.',
         'El título debe plantear curiosidad real y una pregunta concreta sobre el nicho seleccionado, basada en las fuentes.',
         'Evita títulos genéricos tipo «Qué es ...», grandilocuencia, falsas primicias, promesas vacías y cifras no documentadas.',
         'Usa EXCLUSIVAMENTE hechos sustentables en las fuentes incluidas; no inventes cifras, fechas, citas o normativa.',
         'Mantén todos los bloques dentro del tema y nicho; no inventes una conexión para rescatar un tema tangencial. Si las fuentes no permiten sostener el tema, no fabules.',
         'Incluye hechos_con_evidencia con al menos tres entradas distintas (o el mínimo indicado): {fuente_id, afirmacion, cita_id}. Elige un cita_id DIFERENTE de citas_verificadas_para_elegir para cada entrada; no copies citas ni inventes IDs. Usa solamente esos pasajes como evidencia. Distingue el alcance estadounidense de las normas 14 CFR.',
         'hechos_con_evidencia es un campo privado de validación: NO enumeres los hechos, no digas «hecho número», «evidencia», «fuente F1», «cita C1», «según la fuente», «pista número» ni introduzcas secciones de hechos durante la locución.',
         'Los ocho bloques deben sonar como un relato fluido e inmersivo, sin encabezados narrados ni listas de hechos. Para ficción, relata la historia como ficción y no como acontecimiento real.',
         'Escribe ocho bloques en orden EXACTO: gancho,pregunta,contexto,pista,analisis,desarrollo,aplicacion,conclusion.',
         f'Cada bloque: {{tipo,texto}}; máximo 160 palabras. Total entre {AERO_PALABRAS_MIN} y {AERO_PALABRAS_MAX} palabras; distribuye el espacio según la complejidad.',
         'Debes aportar al menos tres aprendizajes específicos y un ejemplo explicado sin inventar incidentes.',
         'La primera escena abre DIRECTAMENTE con el hecho o la situación concreta más intrigante, sin saludo ni presentación del canal.',
         'En los ocho bloques mantén progresión: gancho, pregunta central, contexto mínimo, pista, complicación, desarrollo narrativo, aplicación/revelación, cierre satisfactorio.',
         'Al menos cada dos escenas aporta información NUEVA o resuelve una duda específica; no alargues artificialmente la historia.',
         'En ficción literaria distingue trama de hechos reales; evita transformar una leyenda en un hecho demostrado.',
         'No redundancias, frases vacías, repeticiones de conceptos ni palabras de relleno.',
         'No incluyas llamadas a like ni suscripción: se añaden después en una escena independiente.',
         'El cierre del bloque conclusión puede formular una pregunta específica y natural sobre el caso, nunca una pregunta genérica del canal.',
         'No incluyas advertencias tipo "este contenido es educativo".',
         'Evita escribir "un estudio indica" si no hay informe explícito en las fuentes.',
         'El resultado no debe depender de referencias numéricas que no figuren en el texto recuperado.' ],
       'estructura':{'titulo_youtube':'¿Por qué cambia [concepto central] cuando [condición concreta]?', 'hechos_con_evidencia':[{'fuente_id':'F1','afirmacion':'hecho basado en la cita','cita_id':'C1'}],
                     'bloques':[{'tipo':t,'texto':'Narración...','visual_query':'concrete subject'} for t in ('gancho','pregunta','contexto','pista','analisis','desarrollo','aplicacion','conclusion')]}}
    prompt='Escribe JSON válido en español siguiendo esta especificación:\n'+json.dumps(instruccion,ensure_ascii=False)
    motores=_aero_motores_guion()
    errores=[]
    if not motores:
        raise EpisodioRecuperable('No hay proveedores IA de guion disponibles: '+str(_AERO_IA_INHABILITADOS))
    for motor in motores:
        if motor=='openrouter' and OPENROUTER_MODELO=='openrouter/free' and not _OPENROUTER_ALTERNATIVO_INTENTADO:
            _openrouter_preparar_alternativo()
        prompt_motor=prompt
        for intento in range(1,3):
            try:
                print(f'  Redactando con IA: {motor} intento {intento}/2',flush=True)
                datos=({'gemini':_consultar_gemini,'groq':_consultar_groq,
                        'openrouter':_consultar_openrouter}[motor])(prompt_motor)
                datos=_aero_resolver_citas_ia(datos,citas_preseleccionadas)
                plan=_validar_guion_ia(datos,documentos,caso)
                caso['_consultas_escenas']=[str(b.get('visual_query',''))[:100] for b in datos['bloques']]
                try:
                    titulo_ia=_validar_titulo_youtube(datos,caso)
                except ValueError as titulo_error:
                    # No desperdiciar un guion ya validado por un título defectuoso.
                    # Formular una pregunta neutra a partir del catálogo original.
                    tecnico=caso.get('_titulo_caso',caso['titulo']).strip().rstrip('?')
                    alternativas=[f'{tecnico}: ¿qué conviene comprender de este fenómeno?',
                                  f'{tecnico}: ¿qué hay detrás de este concepto?',
                                  f'{tecnico}: una explicación basada en evidencias']
                    titulo_ia=next((t for t in alternativas if 32<=len(t)<=95),None)
                    if titulo_ia is None:raise titulo_error
                    print('  Título IA rechazado; usando título técnico neutral:',titulo_ia,flush=True)

                # La pregunta de interacción forma parte del relato, antes del CTA
                # fijo solicitado por el usuario; no afirma hechos no documentados.
                if MODO_VIRAL and PREGUNTA_FINAL_ESPECIFICA:
                    for k in range(len(plan)-1,-1,-1):
                        if plan[k][0]=='conclusion':
                            cierre=plan[k][1]
                            pregunta=_viral_pregunta_contextual(caso)
                            if '?' not in cierre and len((cierre+' '+pregunta).split())<=105:
                                plan[k]=('conclusion',cierre.rstrip(' .')+'. '+pregunta)
                            break
                # El CTA permanece como escena final sin subtítulos.
                plan.append(('cta','Si te gustó este contenido, dale Like y Suscríbete! Muchas gracias por tu visita y nos vemos en un próximo video!'))
                caso['titulo']=titulo_ia
                episodio['titulo']=titulo_ia
                print('  Título YouTube investigado:',titulo_ia,flush=True)
                (carpeta/'GUION_IA.json').write_text(json.dumps({
                    'motor':motor, 'modelo':{'gemini':GEMINI_MODELO,'groq':GROQ_MODELO,
                              'openrouter':(_OPENROUTER_MODELO_REAL or OPENROUTER_MODELO)}[motor],
                    'fecha_utc':datetime.now(timezone.utc).isoformat(),
                    'fuentes':[{'id':d['id'],'nombre':d['nombre'],'url':d['url']} for d in documentos],
                    'resultado':datos,'verificacion':'Citas textuales localizadas; precisión técnica no certificada automáticamente'
                },ensure_ascii=False,indent=2),encoding='utf-8')
                print(f'  Guion IA validado: {len(plan)-1} escenas + CTA, motor {motor}',flush=True)
                return plan
            except Exception as e:
                mensaje=str(e)[:550]
                errores.append(motor+f' intento {intento}: '+mensaje)
                print('  Motor IA no disponible/guion rechazado:',motor,mensaje[:240],flush=True)
                # Si los tokens se consumen razonando, cambiar la estrategia
                # del siguiente intento; nunca usar razonamiento como guion.
                if motor=='openrouter' and isinstance(e,OpenRouterSalidaAgotada):
                    if intento==1 and _openrouter_preparar_alternativo():
                        # La instrucción compacta conserva el esquema y las citas verificadas.
                        breve={k:instruccion[k] for k in ('tarea','tema','categoria','tipo_narrativo','citas_verificadas_para_elegir','normas','estructura')}
                        prompt_motor='Devuelve solo el objeto JSON completo. Sin análisis externo. '+json.dumps(breve,ensure_ascii=False,separators=(',',':'))
                        continue
                    _AERO_IA_INHABILITADOS[motor]=mensaje[:350]
                    print('  OpenRouter: salida agotada y sin alternativa gratuita utilizable; suspendido para evitar más consumo.',flush=True)
                    break
                # Un cuerpo vacío puede ser transitorio en openrouter/free:
                # reintentar una sola vez, sin convertir razonamiento en evidencia.
                if motor=='openrouter' and 'contenido vacío' in mensaje.lower() and intento==2:
                    _AERO_IA_INHABILITADOS[motor]=mensaje[:350]
                    print('  OpenRouter: dos respuestas vacías, suspendido para esta ejecución.',flush=True)
                    break
                # No insistir ante cuotas, autenticación, modelos retirados o errores de red.
                if _aero_error_proveedor(motor,mensaje):
                    break
                prompt_motor=prompt+'\nIMPORTANTE: La respuesta previa se rechazó por: '+mensaje+                              '. Corrige la estructura y las citas textuales literales.\n'
    (carpeta/'ERROR_GUION_IA.txt').write_text('\n'.join(errores),encoding='utf-8')
    raise RuntimeError('No se obtuvo un guion investigado válido. '
                       'NO se publicará usando una plantilla. '+' | '.join(errores))

# ==================== SELECCIÓN Y HISTORIAL ====================
def ruta_historial():
    if SALIDA_EN_DRIVE:
        try:
            from google.colab import drive
            drive.mount('/content/drive',force_remount=False)
            p=Path('/content/drive/MyDrive/AEROFACTUM/historial_100.json')
            p.parent.mkdir(parents=True,exist_ok=True)
            return p
        except Exception as exc:
            print('AVISO: Drive no disponible. El historial será local y podría perderse al reiniciar Colab:',str(exc)[:130])
    return Path(os.getenv('AERO_HISTORIAL', 'state/historial_100.json' if os.getenv('GITHUB_ACTIONS', '').lower() == 'true' else str(OUTPUT_BASE/'historial_100.json')))

def leer_historial(ruta):
    if ruta.exists():
        try:
            data=json.loads(ruta.read_text(encoding='utf-8'))
            return data if isinstance(data,list) else []
        except Exception:pass
    return []

def anotar_historial(ruta,registro):
    datos=leer_historial(ruta)
    if registro['episodio'] not in {x.get('episodio') for x in datos}:
        datos.append(registro)
    ruta.parent.mkdir(parents=True,exist_ok=True)
    temporal=ruta.with_suffix('.tmp')
    temporal.write_text(json.dumps(datos,ensure_ascii=False,indent=2),encoding='utf-8')
    temporal.replace(ruta)

def elegir_episodios(cantidad,historial):
    import secrets
    rng=secrets.SystemRandom()
    historia=leer_historial(historial)
    usados={r.get('episodio') for r in historia}
    casos_vistos={r.get('caso') for r in historia}
    opciones=list(CATALOGO_AERONAUTICO)
    if TEMA!='aleatorio':
        opciones=[k for k in opciones if k==TEMA or CATALOGO_AERONAUTICO[k]['caso_id']==TEMA]
        if not opciones:raise ValueError('TEMA desconocido: '+TEMA)
    disponibles=[k for k in opciones if not(EVITAR_REPETICIONES and k in usados)]
    if len(disponibles)<cantidad:
        if REINICIAR_CATALOGO_AL_AGOTAR:
            disponibles=list(opciones)
            print('ATENCIÓN: el catálogo está agotado, se permitirán repeticiones.')
        else:
            raise RuntimeError(f'Solo hay {len(disponibles)} episodios disponibles, se solicitaron {cantidad}.')
    # Priorización real por caso: al principio se exploran los 100
    # sucesos antes de generar otras versiones de un mismo caso.
    rng.shuffle(disponibles)
    elegidos=[]
    reservados=set(casos_vistos)
    while disponibles and len(elegidos)<cantidad:
        nuevos=[k for k in disponibles if CATALOGO_AERONAUTICO[k]['caso_id'] not in reservados]
        grupo=nuevos if nuevos else disponibles
        clave=grupo[0]
        elegidos.append(clave)
        reservados.add(CATALOGO_AERONAUTICO[clave]['caso_id'])
        disponibles.remove(clave)
    return [CATALOGO_AERONAUTICO[k] for k in elegidos]

# ======================== DEPENDENCIAS ========================
def asegurar_dependencias():
    faltantes=[paquete for modulo,paquete in [('PIL','Pillow>=10.0'),('requests','requests>=2.31'),('edge_tts','edge-tts>=6.1'),('numpy','numpy>=1.24'),('cairosvg','CairoSVG>=2.7'),('pypdf','pypdf>=4.0'),('bs4','beautifulsoup4>=4.12'),('json_repair','json-repair>=0.30')] if importlib.util.find_spec(modulo) is None]
    if faltantes: subprocess.run([sys.executable,'-m','pip','install','-q',*faltantes],check=True)
    if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):
        if not shutil.which('apt-get'): raise RuntimeError('Se requiere FFmpeg en el entorno.')
        subprocess.run(['apt-get','update','-qq'],check=True)
        subprocess.run(['apt-get','install','-y','-qq','ffmpeg','fonts-dejavu-core'],check=True)
    from PIL import Image
    import requests,numpy,edge_tts,cairosvg

def ffmpeg(cmd):
    """Ejecuta FFmpeg y muestra un diagnóstico útil en caso de fallo.

    Se usa en el montaje, la concatenación y la exportación final.
    """
    if not isinstance(cmd, (list, tuple)) or not cmd:
        raise ValueError('FFmpeg requiere una lista de argumentos no vacía.')
    if not shutil.which(str(cmd[0])):
        raise RuntimeError('No se encontró FFmpeg. Ejecuta asegurar_dependencias() antes de renderizar.')
    proceso = subprocess.run([str(x) for x in cmd], capture_output=True, text=True)
    if proceso.returncode:
        diagnostico = (proceso.stderr or proceso.stdout or 'Error sin detalles').strip()
        raise RuntimeError(
            f'FFmpeg falló (código {proceso.returncode}).\n'
            f'Detalle: {diagnostico[-4500:]}\n'
            f'Comando: {" ".join(str(x) for x in cmd)[:1500]}'
        )
    return proceso

# ====================== FUENTES Y AUDITORÍA =====================
def verificar_fuentes(caso,session,carpeta):
    """Auditoría de disponibilidad de referencias; NO confunde acceso con
    verificación de afirmaciones científicas. Ante bloqueo web, continúa sólo
    si VERIFICACION_OBLIGATORIA=False y deja evidencia de la limitación.
    """
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    session.headers.update({'User-Agent': 'Mozilla/5.0 (compatible; AEROFACTUM/1.1; educational research)',
                            'Accept': 'text/html,application/xhtml+xml;q=0.9,*/*;q=0.8',
                            'Accept-Language': 'en-US,en;q=0.8'})
    try:
        reintentos=Retry(total=2,connect=2,read=1,backoff_factor=0.7,
                          status_forcelist=[429,500,502,503,504],
                          allowed_methods=frozenset(['GET']))
        session.mount('https://',HTTPAdapter(max_retries=reintentos))
    except Exception: pass

    # Referencias alternativas oficiales comprobables, por categoría.
    # Estas fichas NO sustituyen la comprobación de la afirmación concreta.
    alternativas={
      'AERODINÁMICA':['https://www.faa.gov/regulations_policies/handbooks_manuals/aviation/phak',
                      'https://www.faa.gov/regulations_policies/handbooks_manuals/aviation'],
      'MOTORES Y SISTEMAS':['https://www.faa.gov/regulations_policies/handbooks_manuals/aviation/phak'],
      'INSTRUMENTOS Y NAVEGACIÓN':['https://www.faa.gov/regulations_policies/handbooks_manuals/aviation/phak'],
      'METEOROLOGÍA':['https://www.faa.gov/regulations_policies/handbooks_manuals/aviation'],
      'OPERACIONES DE VUELO':['https://www.faa.gov/regulations_policies/handbooks_manuals/aviation/airplane_handbook'],
      'SEGURIDAD Y FACTOR HUMANO':['https://www.icao.int/safety-management/guidance-material',
                                   'https://www.faa.gov/regulations_policies/handbooks_manuals/aviation'],
      'FINANZAS Y ECONOMÍA':['https://www.iata.org/en/publications/economics/reports/global-outlook-for-air-transport-june-2026'],
      'AEROPUERTOS Y ATC':['https://www.faa.gov/pilots',
                             'https://www.faa.gov/regulations_policies/handbooks_manuals/aviation'],
      'MANTENIMIENTO Y CERTIFICACIÓN':['https://www.faa.gov/regulations_policies/handbooks_manuals/aviation'],
      'AVIACIÓN DEL FUTURO':['https://www.faa.gov/regulations_policies/handbooks_manuals/aviation']}
    registro=[]
    urls_vistas=set()
    originales=caso.get('fuentes',[])
    consultas=[(nombre,url,anclas,'principal') for nombre,url,anclas in originales]
    for i,url in enumerate(alternativas.get(caso.get('categoria',''),[]),1):
        consultas.append((f'Referencia oficial alternativa {i}',url,[],'respaldo'))
    for nombre,url,anclas,tipo in consultas:
        if url in urls_vistas:continue
        urls_vistas.add(url)
        fila=dict(nombre=nombre,url=url,tipo=tipo,
                  consultada_utc=datetime.now(timezone.utc).isoformat(),
                  status='no_accesible',anclas=list(anclas),
                  nota='Acceso a la referencia; NO verifica las afirmaciones del guion')
        try:
            r=session.get(url,timeout=(10,22),allow_redirects=True)
            fila['codigo_http']=r.status_code
            fila['url_final']=r.url
            r.raise_for_status()
            tipo_mime=r.headers.get('Content-Type','').lower()
            texto=html.unescape(re.sub(r'<[^>]+>',' ',r.text)) if 'html' in tipo_mime or not tipo_mime else r.text
            texto=re.sub(r'\s+',' ',texto).strip()
            if len(texto)<120:
                fila['status']='contenido_insuficiente'
            else:
                fila['status']='accesible'
                fila['tamano_texto']=len(texto)
                anclas_encontradas=[a for a in anclas if a.casefold() in texto.casefold()]
                fila['anclas_encontradas']=anclas_encontradas
                fila['anclas_no_encontradas']=[a for a in anclas if a not in anclas_encontradas]
                # Una palabra encontrada NO equivale a verificación científica.
        except Exception as exc:
            fila['error']=f'{type(exc).__name__}: {exc}'[:300]
        registro.append(fila)
        if fila['status']=='accesible':
            # Basta una referencia oficial accesible. Evita consultas redundantes.
            break
    accesibles=sum(f['status']=='accesible' for f in registro)
    estado='FUENTE ACCESIBLE · CONTENIDO POR REVISAR' if accesibles else 'PENDIENTE DE VERIFICACIÓN · SIN ACCESO A FUENTES'
    (carpeta/'auditoria_fuentes.json').write_text(json.dumps({
       'estado_global':estado,'verificacion_del_contenido':'NO REALIZADA',
       'consultas':registro},ensure_ascii=False,indent=2),encoding='utf-8')
    (carpeta/'ESTADO_VERIFICACION.txt').write_text(
       estado+'\nLas referencias bibliográficas no certifican por sí solas las afirmaciones.\n'
       'Revisar manual o informe aplicable y fecha antes de publicar.\n',encoding='utf-8')
    print('Fuentes oficiales accesibles:',accesibles,'de',len(registro), '|',estado,flush=True)
    if not accesibles:
        detalles='; '.join((f.get('error') or f.get('status',''))[:110] for f in registro)
        print('ADVERTENCIA: no se pudo verificar la accesibilidad:',detalles,flush=True)
        if VERIFICACION_OBLIGATORIA:
            raise RuntimeError('Ninguna referencia oficial accesible. Revisa auditoria_fuentes.json. '
                               'Si necesitas producir un borrador sin confirmar las fuentes, configura '
                               'VERIFICACION_OBLIGATORIA=False; no lo publiques sin revisión.')
    return registro

# ======================= IMÁGENES ABIERTAS ======================
def limpiar_html(v): return html.unescape(re.sub('<[^>]*>',' ',v or '')).strip()
def licencia_valida(info):
    """Solo CC0 o dominio público para no necesitar créditos en YouTube.

    No considerar meras menciones de «public domain» dentro de advertencias.
    La etiqueta de licencia de Commons debe identificar explícitamente CC0 o PD.
    """
    meta = info.get('extmetadata') or {}
    nombre = limpiar_html(meta.get('LicenseShortName', {}).get('value', '')).strip().lower()
    enlace = limpiar_html(meta.get('LicenseUrl', {}).get('value', '')).strip().lower()
    codigo = limpiar_html(meta.get('License', {}).get('value', '')).strip().lower()
    # Un CC BY/CC BY-SA requiere crédito aunque Commons permita reutilizarlo.
    # Incluye también CC BY-NC/ND y licencias ambiguas en la exclusión.
    if any(term in (nombre + ' ' + enlace + ' ' + codigo)
           for term in ('by-sa', 'by/', 'by-', 'attribution', 'sharealike',
                        'noncommercial', 'non-commercial', 'no derivatives')):
        return False
    es_cc0 = (nombre in ('cc0', 'cc0 1.0', 'creative commons zero')
              or 'creativecommons.org/publicdomain/zero/' in enlace
              or codigo in ('cc0', 'cc-zero'))
    es_pd = (nombre in ('public domain', 'dominio público', 'public domain mark')
             or nombre.startswith('pd-')
             or codigo.startswith('pd-')
             or codigo in ('pd', 'public domain')
             or 'creativecommons.org/publicdomain/mark/' in enlace)
    return es_cc0 or es_pd

# El filtro anterior sólo comprobaba la LICENCIA y permitía fotos de
# «laboratory equipment» aunque el episodio tratase sobre un magnetar.
# Este motor exige una conexión temática explícita en los METADATOS DE COMMONS.
# No utiliza reconocimiento de imagen: la relevancia semántica sigue requiriendo
# revisión humana, pero elimina los falsos positivos más evidentes.
PALABRAS_GENERICAS_IMAGEN = set("""
    a an and are art artist astronomy astronomical beautiful big black blue
    camera colour color dark earth experiment experimental image images
    figure file from galaxy general high illustration illustrations in
    infrared interesting laboratory large light long nasa national natural
    new night of on photo photograph photos picture planet planets research
    science scientific space star stars study system telescope telescopes
    the this university view with world technology historical historic
    mysteri mystery misterioso mystery mysterious phenomenon phenomena
    el la de del los las un una por que para sobre como caso ciencia
    scientific instrument equipment observatory background landscape sky
""".split())

# Sinónimos específicos auditables para los casos originales: son contexto
# documental legítimo, pero NO se acepta cualquier foto del mar/cielo.
# Los conceptos operacionales no siempre aparecen literalmente en los metadatos.
# Descriptores documentales específicos para fotografías reales en Wikimedia Commons.
ALIASES_VISUALES = {
    'ops_01': ['pilots cockpit briefing', 'flight crew briefing'],
}

CONSULTAS_VISUALES_AERONAUTICAS = {
    'briefing': [
        'pilots cockpit preflight preparation', 'flight crew briefing airline',
        'airline pilots cockpit crew', 'pilots flight planning cockpit',
        'briefing tripulación cabina pilotos', 'cockpit crew preparing flight',
    ],
    'salida': ['airliner flight deck crew', 'airport departure runway cockpit'],
    'metar': ['aviation weather station airport', 'airport meteorological station'],
    'combustible': ['aircraft fuel truck refuelling', 'aircraft refueling airport'],
    'mantenimiento': ['aircraft maintenance engineers hangar', 'airplane mechanic inspection'],
    'costos': ['commercial airliner airport terminal', 'airline operations control'],
}

CONTEXTO_VISUAL_CATEGORIA = {
    'OPERACIONES DE VUELO': ['flight deck', 'cockpit', 'pilot', 'pilots', 'crew', 'airline', 'preflight', 'departure', 'flight planning', 'briefing'],
    'AERODINÁMICA': ['aircraft wing', 'airfoil', 'flaps', 'slats', 'wingtip', 'vortex'],
    'MOTORES Y SISTEMAS': ['turbofan', 'jet engine', 'aircraft engine', 'landing gear', 'apu'],
    'INSTRUMENTOS Y NAVEGACIÓN': ['aircraft cockpit', 'avionics', 'flight instrument', 'navigation'],
    'METEOROLOGÍA': ['airport weather', 'aircraft clouds', 'aviation meteorology'],
    'SEGURIDAD Y FACTOR HUMANO': ['airline flight crew', 'pilot cockpit', 'aviation safety'],
    'FINANZAS Y ECONOMÍA': ['commercial airliner airport', 'airline fleet', 'airport terminal'],
    'AEROPUERTOS Y ATC': ['airport control tower', 'air traffic control', 'airfield'],
    'MANTENIMIENTO Y CERTIFICACIÓN': ['aircraft mechanic maintenance', 'aircraft hangar'],
    'AVIACIÓN DEL FUTURO': ['experimental aircraft', 'electric airplane', 'aviation technology'],
}

# Hay términos genéricos que solos no sirven; las anclas se validan por pares.
ANCLAS_TEMATICAS_SEGURAS = {
    'cockpit', 'pilot', 'pilots', 'crew', 'airline', 'airliner', 'flight',
    'preflight', 'briefing', 'departure', 'planning', 'aircraft', 'aviation',
    'runway', 'airport', 'turbofan', 'wing', 'flaps', 'hydraulic', 'weather',
    'maintenance', 'engine', 'avionics', 'refueling', 'control', 'tower',
}

def _consultas_fotos(caso):
    titulo=caso.get('_titulo_caso',caso.get('titulo',''))
    categoria=caso.get('categoria','')
    consultas=list(caso.get('imagenes',[]))
    # La ficha antigua de meteo_07 buscaba 'satellite map' y el filtro
    # descarta mapas, correctamente. Buscar FOTOGRAFÍAS atmosféricas reales.
    if caso.get('_episodio', {}).get('caso_id') == 'meteo_07':
        consultas = [
            'cirrus clouds high altitude photograph',
            'aircraft contrails blue sky',
            'cirrus clouds sky',
            'lenticular cloud mountain',
            'clouds viewed from airplane window',
            'high altitude clouds aerial photograph',
        ]
    # Fenómenos meteorológicos de aviación: fotos reales, no mapas ni diagramas.
    # Para windshear, la imagen puede mostrar la tormenta o nube causante
    # sin que aparezca literalmente una aeronave en el nombre del archivo.
    if (caso.get('_episodio') or {}).get('caso_id') == 'meteo_03':
        consultas = [
            'cumulonimbus thunderstorm',
            'microburst storm clouds',
            'thunderstorm rain shaft',
            'cumulonimbus anvil cloud',
            'airport thunderstorm weather',
            'wind shear storm',
        ]
    if (caso.get('_episodio') or {}).get('caso_id') == 'atc_02':
        consultas = [
            'aircraft taxiing', 'airplane taxiing', 'airliner taxiway',
            'aircraft ground movement', 'airport taxiway aircraft',
            'commercial aircraft taxiing', 'jet taxiing runway',
            'aircraft taxiway hold short', 'airport ground traffic',
            'avion rodaje aeropuerto',
        ] + consultas
    # Consultas documentales relacionadas con la utilización de aeronaves:
    # rotaciones, escalas y operaciones reales, no diagramas conceptuales.
    if re.search(r'utilizaci[oó]n diaria|horas de utilizaci[oó]n|rotaci[oó]n de aeronaves', titulo, re.I):
        consultas = [
            'aircraft turnaround airport apron',
            'airliner boarding at airport gate',
            'aircraft ground handling airport',
            'airliner taxiing airport',
            'aircraft parked at airport terminal',
            'airline aircraft boarding passengers',
        ] + consultas
    if re.search(r'briefing|reunión previa|preparación de salida', titulo, re.I):
        consultas=CONSULTAS_VISUALES_AERONAUTICAS['briefing']+consultas
    for palabra, alternativas in CONSULTAS_VISUALES_AERONAUTICAS.items():
        if palabra!='briefing' and palabra in titulo.lower():
            consultas=alternativas+consultas
    consultas+=CONTEXTO_VISUAL_CATEGORIA.get(categoria,[])[:4]
    consultas+=[titulo]
    # Priorizar consultas de fotos y no esquemas, aunque el catálogo original
    # contuviera términos como 'schematic' o 'concept'.
    fotografias=[]
    for q in consultas:
        q=re.sub(r'\b(schematic|diagram|illustration|drawing|blueprint|render|concept|infographic)\b','',q,flags=re.I).strip()
        q=re.sub(r'\s+',' ',q)
        if not q: continue
        fotografias.append(q)
    # Búsquedas específicas con términos habituales en fotografías documentales.
    favoritas=fotografias[:5]
    fotografias += [q+' photo' for q in favoritas]
    fotografias += [q+' photograph' for q in favoritas[:3]]
    # Ampliar ligeramente las búsquedas sin aceptar fotos sin relación con el caso.
    return list(dict.fromkeys(fotografias))[:18]


# Sólo fotografía real: la extensión JPEG/PNG por sí sola NO demuestra que
# una imagen sea una foto. Se excluyen diagramas, mapas, renders y gráficos.
PATRONES_NO_FOTOGRAFICOS = (
    r'\b(?:diagrams?|diagramas?|schematics?|esquemas?|blueprints?|drawings?|dibujos?|'
    r'illustrations?|ilustraciones?|illustrated|graphics?|infographics?|infografias?|'
    r'flowchart|chart|grafico|graph|plot|map|mapa|cartoon|caricatura|'
    r'icon|icono|logo|symbol|simulated|simulation|simulacion|'
    r'renders?|rendered|rendering|cgi|computer generated|3d model|'
    r'3d reconstruction|artist impression|artist conception|concept art|'
    r'cutaway|cross section|section view|technical drawing|line art|'
    r'wireframe|vector|svg|poster|slide|presentation|screenshot|'
    r'captura de pantalla|screen capture|collage|composite image|'
    r'conceptual illustration|aircraft silhouette|infografico|model kit)\b',
)

def es_foto_real_metadata(titulo, metadata):
    """Filtro conservador: rechaza indicios explícitos de imagen no fotográfica.
    No certifica el contenido visual; comprobar la hoja de revisión antes de publicar.
    """
    titulo_limpio = limpiar_html(titulo).lower().replace('_',' ')
    campos = ('ImageDescription','ObjectName','Categories','LicenseShortName')
    detalles = ' '.join(limpiar_html(metadata.get(k, {}).get('value','')) for k in campos)
    texto = (titulo_limpio+' '+detalles.lower()).replace('_',' ')
    for patron in PATRONES_NO_FOTOGRAFICOS:
        if re.search(patron, texto, re.IGNORECASE):
            return False
    return True

def _normalizar_texto_foto(texto):
    import unicodedata
    t=unicodedata.normalize('NFKD',str(texto or '').lower())
    t=''.join(c for c in t if not unicodedata.combining(c))
    t=re.sub(r'[^a-z0-9]+',' ',t)
    return ' '+re.sub(r'\s+',' ',t).strip()+' '

def _tokens_visuales(texto):
    return {t for t in _normalizar_texto_foto(texto).split()
            if len(t)>=4 and t not in PALABRAS_GENERICAS_IMAGEN}

def _anclas_visuales(caso):
    origen=caso.get('_episodio',{}).get('caso_id','')
    semillas=_consultas_fotos(caso)[:9]
    anclas=set().union(*(_tokens_visuales(q) for q in semillas))
    if caso.get('fuentes'):
        anclas |= _tokens_visuales(caso['fuentes'][0][1].split('/wiki/')[-1].replace('_',' '))
    for alias in ALIASES_VISUALES.get(origen,[]):
        anclas |= _tokens_visuales(alias)
    return anclas

# Exigir un objeto o contexto aeronáutico identificable en el NOMBRE del archivo.
# Categorías enormes de Commons pueden contener etiquetas irrelevantes y no bastan.
AVIACION_EN_TITULO = re.compile(
    r"\b(?:aircraft|aeroplane|airplane|airliner|airlines?|airbus|boeing|"
    r"embraer|bombardier|cessna|beechcraft|fokker|turboprop|turbofan|"
    r"airport|airfield|airstrip|airway|flightdeck|cockpit|aircrew|"
    r"helicopter|rotorcraft|aeropuerto|aeronave|avion|aviacion|"
    r"runway|taxiway|airtraffic|atc|hangar|a380|a320|a350|b737|b747|b777|b787|"
    r"winglet|landinggear|flaps|slats|"
    r"jetengine|jetliner|airplaneengine|plane|propeller|"
    r"airfieldcontrol|controltower)\b", re.I)

# Si el nombre no menciona el sector aeronáutico, se descarta, aun cuando
# una categoría general o la búsqueda haga parecer pertinente el resultado.
def evaluar_relevancia_foto(caso, titulo, metadata, busqueda):
    """Filtro estricto basado en el nombre y los metadatos, sin fingir visión de IA.

    Requiere evidencia aeronáutica en el título y conexión con las anclas del
    episodio. Falsos negativos son preferibles a publicar fotografías ajenas.
    """
    titulo_n = _normalizar_texto_foto(titulo.replace('File:', ''))
    titulo_l = titulo_n.strip()
    # Excepción temática deliberada: el viento en altura se ilustra con
    # fotografías de cirros, estelas de condensación y atmósfera real.
    # No todo elemento meteorológico tiene 'aircraft' en el nombre.
    if (caso.get('_episodio') or {}).get('caso_id') == 'meteo_07':
        tokens = set(titulo_n.split())
        contexto = {'cirrus', 'cirrostratus', 'cirrocumulus', 'contrail',
                    'contrails', 'lenticular', 'lenticularis', 'cloud', 'clouds',
                    'nubes', 'nube', 'estelas', 'atmosphere', 'atmospheric'}
        especial = {'cirrus', 'cirrostratus', 'cirrocumulus', 'contrail',
                    'contrails', 'lenticular', 'lenticularis', 'high',
                    'altitude', 'upper', 'aerial', 'flight', 'aircraft',
                    'airplane', 'aviation', 'jet', 'stream'}
        # 'clouds' solo no es suficiente. Se requieren dos señales
        # independientes y al menos una específica de altura/aviación.
        pistas = tokens & contexto
        detalles = tokens & especial
        if pistas and detalles and (len(pistas | detalles) >= 2):
            matches = sorted(pistas | detalles)
            return 12 + 3 * len(detalles) + len(pistas), matches
        return 0, []
    if (caso.get('_episodio') or {}).get('caso_id') == 'meteo_03':
        # Evidencias directas y específicas de tormenta convectiva, no basta
        # la palabra 'clouds', 'sky', 'rain' ni un paisaje genérico.
        tokens = set(titulo_n.split())
        fuertes = {'cumulonimbus', 'thunderstorm', 'thunderstorms',
                   'microburst', 'microbursts', 'downburst', 'downbursts',
                   'windshear', 'cizalladura', 'tormenta', 'tormentas'}
        corroborantes = {'anvil', 'convective', 'convection', 'storm',
                         'stormcloud', 'stormclouds', 'lightning', 'rainshaft',
                         'squall', 'airport', 'aircraft', 'aviation', 'downdraft'}
        en_titulo = tokens & fuertes
        if en_titulo:
            indicios = en_titulo | (tokens & corroborantes)
            return 14 + 3 * len(en_titulo) + len(indicios), sorted(indicios)
        # Cuando el título dice «anvil cloud» o «rain shaft» puede ser
        # pertinente, siempre que haya dos señales meteorológicas concretas.
        pares = ({'anvil', 'cloud'}, {'rain', 'shaft'},
                 {'storm', 'cloud'}, {'convective', 'cloud'})
        if any(par.issubset(tokens) for par in pares):
            return 12, sorted(tokens & (corroborantes | {'cloud','rain','shaft'}))
        # Si no hay evidencia fuerte en el título, no basarse solamente
        # en categorías amplias o etiquetas de búsqueda de Commons.
        return 0, []
    if (caso.get('_episodio') or {}).get('caso_id') == 'atc_02':
        # Rodaje: una torre ATC o fachada de aeropuerto NO es prueba visual
        # de una aeronave rodando. La evidencia principal debe estar en el título.
        movimiento = re.search(r'\b(?:taxi(?:ing)?|taxiway|taxiways|taxiing|'
                              r'ground movement|ground handling|rodaje|rodando)\b', titulo_l)
        aeronave = re.search(r'\b(?:aircraft|airplane|aeroplane|airliner|'
                            r'airbus|boeing|jet|a320|b737|plane|avion|aeronave)\b', titulo_l)
        if not (movimiento and aeronave):
            return 0, []
        return 22 + 3*len(set(titulo_l.split()) & {'taxiing','taxiway','rodaje'}), ['rodaje','aeronave']
    if not AVIACION_EN_TITULO.search(titulo_l):
        return 0, []
    metatexto = ' '.join(limpiar_html(metadata.get(k, {}).get('value', ''))
                         for k in ('ImageDescription', 'ObjectName', 'Categories'))
    meta_n = _normalizar_texto_foto(metatexto[:18000])
    anclas = _anclas_visuales(caso)
    tokens_titulo = set(titulo_n.split())
    tokens_meta = set(meta_n.split())
    directas = anclas.intersection(tokens_titulo)
    extras = anclas.intersection(tokens_meta)
    relevantes = directas | extras
    # La única referencia directa a 'aircraft' o 'airport' no basta: exigir
    # evidencia contextual y coincidencia fuerte con el tema actual.
    if len(relevantes) < 2 or len(directas) < 1:
        return 0, []
    puntos = 4 * len(directas) + len(extras)
    puntos += len(_tokens_visuales(busqueda).intersection(tokens_titulo))
    if puntos < 7:
        return 0, []
    return puntos, sorted(relevantes)


def configurar_reintentos_wikimedia(session):
    """Consultas respetuosas de los límites Wikimedia: sin reintentar HTTP 429.

    La sesión puede haber sido configurada para otras fuentes oficiales.
    Aquí se usa un adaptador específico de Commons que evita reintentos
    agresivos y una identificación clara de la aplicación con su sitio público.
    """
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    reintentos = Retry(
        total=1, connect=1, read=0, status=1,
        backoff_factor=1.5,
        status_forcelist=(500, 502, 503, 504),
        allowed_methods=frozenset({'GET'}),
        respect_retry_after_header=True,
        raise_on_status=False,
    )
    adaptador = HTTPAdapter(max_retries=reintentos, pool_connections=2, pool_maxsize=2)
    session.mount('https://commons.wikimedia.org/', adaptador)
    session.mount('https://upload.wikimedia.org/', adaptador)
    # No simular que somos un navegador: Wikimedia exige un agente reconocible.
    session.headers['User-Agent'] = (
        'AEROFACTUM-Bot/3.3 (https://acesped.github.io/aerofactum/; '
        'ari.cesped@gmail.com) python-requests'
    )
    return session


# ----------------- DIRECCIÓN VISUAL SEMÁNTICA 7.2 -----------------
# No se confunden escenas estilizadas con fotografías de acontecimientos reales.
_MOTIVOS_TERROR = {
 'alquimia': r'alquimis|poci[oó]n|laboratorio|frasco|elixir|qu[ií]mic|brebaje',
 'libro': r'libro|p[aá]gina|manuscrito|escrit|diario|biblioteca|hechizo',
 'puerta': r'puerta|cerradura|llave|abr[ií]|cerr[oó]|umbral|entrada',
 'espejo': r'espejo|reflejo|reflejad|cristal|vidrio',
 'reloj': r'reloj|medianoche|hora|campanad|tiempo',
 'ventana': r'ventana|cortina|balc[oó]n|mir[oó] hacia',
 'fantasma': r'fantasma|aparici[oó]n|esp[ií]ritu|espectro|alma',
 'persona': r'mujer|hombre|niñ[oa]|familia|visitante|viajero|persona|alguien|sombra|silueta',
 'escalera': r'escalera|peldañ|s[oó]tano|subi[oó]|baj[oó]',
 'bosque': r'bosque|[aá]rbol|sendero|monte|vegetaci[oó]n',
 'casa': r'casa|mansi[oó]n|habitaci[oó]n|castillo|edificio|hogar|pasillo',
 'vehiculo': r'tren|vag[oó]n|coche|carro|cami[oó]n|veh[ií]culo',
 'huellas': r'huella|paso|pisada|rastro|suelo|sangre',
 'carta': r'carta|mensaje|nota|sobre|postal',
 'luna': r'luna|noche|oscuridad|cielo|estrella',
}

# Priorización de objetos visibles frente a palabras atmosféricas. La detección
# es heurística: no se afirma que una imagen dibujada represente un hecho real.
_MOTIVOS_TERROR_EXTRA = {
    'calavera': r'calavera|cr[aá]neo|esqueleto|huesos?',
    'vela': r'vela|velas|candelabro|llama|cirio',
    'tumba': r'tumba|sepultura|cementerio|l[aá]pida|ata[uú]d',
    'ojo': r'ojos?|mirada|pupila|observaba',
    'mano': r'manos?|dedos?|garra|toc[oó]|agarr[oó]',
    'telefono': r'tel[eé]fono|llamada|auricular|timbre',
    'muñeca': r'muñeca|juguete|marioneta',
    'linterna': r'linterna|farol|l[aá]mpara|antorcha',
    'cuchillo': r'cuchillo|daga|puñal|hoja afilada',
    'puente': r'puente|pasarela',
    'pozo': r'pozo|agujero profundo|fosa',
    'silla': r'silla|sill[oó]n|asiento',
    'cuadro': r'cuadro|retrato|pintura|lienzo',
}
_MOTIVOS_TERROR.update(_MOTIVOS_TERROR_EXTRA)
_MOTIVOS_ABSTRACTOS={'luna','persona','casa'}

def _plan_visual_semantico(caso):
    """Cada escena se fundamenta EXCLUSIVAMENTE en sus palabras narradas.

    Evita inventar un libro o un fantasma ante frases abstractas. Para escenas
    sin objeto dibujable usa una lámina tipográfica con una frase auténtica.
    """
    plan=caso.get('_plan_visual') or []
    escenas=[]
    for indice,(tipo,voz) in enumerate(plan):
        if tipo=='cta':continue
        texto=re.sub(r'\s+',' ',str(voz)).strip()
        candidatos=[]
        for motivo,patron in _MOTIVOS_TERROR.items():
            for m in re.finditer(patron,texto,re.I):
                # Dar prioridad a objetos exactos; términos atmosféricos son
                # secundarios aunque aparezcan al principio del párrafo.
                exactitud=2 if motivo in _MOTIVOS_ABSTRACTOS else 7
                candidatos.append((exactitud, m.start(), motivo,m.group(0)))
        candidatos.sort(key=lambda x:(-x[0],x[1],x[2]))
        motivo=candidatos[0][2] if candidatos else 'texto_contextual'
        # Frase visible literalmente copiada del texto, nunca generada.
        primera=re.split(r'(?<=[.!?])\s+',texto,maxsplit=1)[0]
        palabras=primera.split()
        extracto=' '.join(palabras[:min(11,len(palabras))])
        if len(palabras)>11:extracto+='…'
        escenas.append({'indice':indice,'tipo':tipo,'texto':texto[:700],
                        'motivo':motivo,
                        'motivos_detectados':list(dict.fromkeys(c[2] for c in candidatos))[:8],
                        'coincidencia_literal':candidatos[0][3] if candidatos else '',
                        'frase_visual':extracto,'recurso':f'imagen_{indice:02}.jpg',
                        'origen':'texto narrado de esta escena'})
    return escenas


def _dibujar_motivo_terror(draw, motivo, w, h, rng):
    """Objeto reconocible, central, ilustrado localmente; sin modelo ni API."""
    cx=int(w*.53); cy=int(h*.53)
    borde=(168,196,213,255); oscuro=(12,17,27,255); oro=(214,171,99,255)
    if motivo in ('puerta','casa','ventana'):
        x0,y0=cx-205,cy-275;x1,y1=cx+205,cy+325
        draw.rectangle((x0,y0,x1,y1),fill=(13,18,30,245),outline=borde,width=11)
        if motivo=='puerta':
            draw.polygon([(x0+50,y0+35),(x1-35,y0+50),(x1-35,y1-20),(x0+50,y1-30)],fill=(53,39,45,255),outline=oro)
            draw.ellipse((x1-99,cy+12,x1-78,cy+33),fill=oro)
        elif motivo=='ventana':
            draw.line((cx,y0,cx,y1),fill=borde,width=12)
            draw.line((x0,cy,x1,cy),fill=borde,width=12)
            draw.ellipse((cx-110,cy-120,cx-15,cy-25),fill=(177,189,186,200))
        else:
            draw.polygon([(x0-90,y0),(cx,y0-190),(x1+90,y0)],fill=oscuro,outline=borde)
            draw.rectangle((cx-65,cy+50,cx+65,y1),fill=(7,9,17,255),outline=oro,width=6)
    elif motivo in ('libro','carta'):
        if motivo=='libro':
            draw.polygon([(cx-340,cy-185),(cx,cy-125),(cx,cy+230),(cx-340,cy+165)],fill=(188,173,143,255),outline=oro)
            draw.polygon([(cx,cy-125),(cx+340,cy-185),(cx+340,cy+165),(cx,cy+230)],fill=(159,149,126,255),outline=oro)
            for y in range(cy-95,cy+130,35):
                draw.line((cx-300,y,cx-55,y+30),fill=(57,58,60,180),width=4)
                draw.line((cx+55,y+30,cx+300,y),fill=(57,58,60,180),width=4)
        else:
            draw.rectangle((cx-320,cy-205,cx+320,cy+205),fill=(180,169,144,255),outline=oro,width=8)
            draw.polygon([(cx-320,cy-205),(cx,cy+60),(cx+320,cy-205)],outline=(69,55,45,255),width=8)
    elif motivo=='alquimia':
        draw.polygon([(cx-65,cy-275),(cx+65,cy-275),(cx+65,cy-80),(cx+250,cy+230),(cx-250,cy+230),(cx-65,cy-80)],fill=(35,84,95,225),outline=borde)
        draw.polygon([(cx-187,cy+90),(cx+188,cy+90),(cx+245,cy+228),(cx-244,cy+228)],fill=(75,162,157,210))
        for q in range(18):
            a=rng.randint(-150,150);b=rng.randint(90,195);rad=rng.randint(5,17)
            draw.ellipse((cx+a-rad,cy+b-rad,cx+a+rad,cy+b+rad),outline=(193,228,220,200),width=3)
    elif motivo=='espejo':
        draw.ellipse((cx-215,cy-300,cx+215,cy+300),fill=(34,66,88,240),outline=oro,width=24)
        draw.ellipse((cx-155,cy-220,cx+155,cy+210),outline=(137,195,206,210),width=6)
        draw.ellipse((cx-45,cy-65,cx+45,cy+32),fill=(10,15,23,230))
    elif motivo=='reloj':
        draw.ellipse((cx-255,cy-255,cx+255,cy+255),fill=(31,39,51,245),outline=oro,width=18)
        for a in range(12):
            theta=a*math.pi/6
            xx=cx+int(210*math.sin(theta)); yy=cy-int(210*math.cos(theta))
            draw.ellipse((xx-7,yy-7,xx+7,yy+7),fill=oro)
        draw.line((cx,cy,cx-85,cy-155),fill=borde,width=14)
        draw.line((cx,cy,cx+140,cy-35),fill=borde,width=9)
    elif motivo in ('persona','fantasma'):
        draw.ellipse((cx-75,cy-250,cx+75,cy-90),fill=(173,185,192,235) if motivo=='fantasma' else oscuro,outline=borde,width=5)
        draw.polygon([(cx-80,cy-110),(cx+80,cy-110),(cx+190,cy+290),(cx-195,cy+290)],fill=(115,139,153,195) if motivo=='fantasma' else oscuro,outline=borde)
        if motivo=='fantasma':
            for x in (cx-30,cx+30):draw.ellipse((x-12,cy-193,x+12,cy-167),fill=oscuro)
    elif motivo=='escalera':
        for k in range(8):
            y=cy-225+k*66
            size=80+k*24
            draw.polygon([(cx-size,y),(cx+size,y),(cx+size+23,y+44),(cx-size-23,y+44)],fill=(45+k*4,50+k*4,64+k*4,245),outline=borde)
    elif motivo=='vehiculo':
        draw.rectangle((cx-320,cy-125,cx+320,cy+175),fill=(30,35,47,255),outline=borde,width=9)
        for x in range(cx-235,cx+240,155):draw.rectangle((x,cy-85,x+95,cy+35),fill=(74,107,125,230),outline=borde)
        for x in (cx-205,cx+205):draw.ellipse((x-65,cy+125,x+65,cy+255),fill=oscuro,outline=oro,width=12)
    elif motivo=='huellas':
        for k in range(5):
            x=cx+(-1 if k%2 else 1)*(75+k*18);y=cy-245+k*112
            draw.ellipse((x-40,y-60,x+40,y+33),fill=(139,157,163,210))
            draw.ellipse((x+18,y-90,x+48,y-52),fill=(139,157,163,210))
    elif motivo in ('calavera','ojo','mano','vela','linterna','telefono','muñeca',
                    'tumba','cuchillo','puente','pozo','silla','cuadro'):
        # Símbolos figurativos originales con composición dependiente del motivo.
        if motivo=='calavera':
            draw.ellipse((cx-170,cy-225,cx+170,cy+125),fill=(190,185,167,255),outline=borde,width=9)
            for dx in (-75,75):draw.ellipse((cx+dx-50,cy-100,cx+dx+40,cy-5),fill=oscuro)
            draw.polygon([(cx,cy-35),(cx-36,cy+40),(cx+36,cy+40)],fill=oscuro)
            draw.rectangle((cx-105,cy+115,cx+105,cy+205),fill=(179,170,154,255),outline=borde,width=6)
        elif motivo=='ojo':
            draw.ellipse((cx-335,cy-130,cx+335,cy+145),fill=(180,194,193,255),outline=oro,width=12)
            draw.ellipse((cx-120,cy-128,cx+120,cy+140),fill=(58,106,122,255))
            draw.ellipse((cx-48,cy-125,cx+48,cy+138),fill=oscuro)
        elif motivo=='mano':
            draw.polygon([(cx-135,cy+230),(cx-175,cy-70),(cx-140,cy-240),(cx-90,cy-55),
                          (cx-45,cy-310),(cx+5,cy-60),(cx+75,cy-290),(cx+100,cy-30),
                          (cx+175,cy-170),(cx+160,cy+110),(cx+75,cy+250)],fill=(130,149,156,240),outline=borde)
        elif motivo in ('vela','linterna'):
            draw.rectangle((cx-80,cy-110,cx+80,cy+250),fill=(184,170,145,255),outline=oro,width=8)
            draw.ellipse((cx-75,cy-300,cx+75,cy-105),fill=(231,174,76,230))
            draw.ellipse((cx-32,cy-260,cx+32,cy-115),fill=(255,235,163,245))
        elif motivo=='tumba':
            draw.rounded_rectangle((cx-190,cy-255,cx+190,cy+290),radius=110,
                 fill=(101,113,126,255),outline=borde,width=12)
            draw.line((cx-75,cy-40,cx+75,cy-40),fill=oscuro,width=13)
        elif motivo in ('telefono','muñeca'):
            draw.rounded_rectangle((cx-155,cy-240,cx+155,cy+245),radius=35,
                                  fill=(64,70,83,255),outline=oro,width=9)
            draw.ellipse((cx-75,cy-105,cx+75,cy+65),outline=borde,width=14)
        elif motivo=='cuchillo':
            draw.polygon([(cx-35,cy-310),(cx+60,cy+35),(cx-10,cy+125)],fill=(183,195,197,255),outline=borde)
            draw.rectangle((cx-55,cy+100,cx+40,cy+295),fill=(79,58,43,255),outline=oro,width=8)
        elif motivo=='puente':
            draw.line((cx-425,cy+170,cx+425,cy+170),fill=borde,width=28)
            for xx in range(cx-360,cx+380,120):draw.line((xx,cy+170,xx,cy-50),fill=borde,width=14)
        elif motivo=='pozo':
            draw.ellipse((cx-300,cy-105,cx+300,cy+155),fill=(73,82,91,255),outline=borde,width=18)
            draw.ellipse((cx-230,cy-50,cx+230,cy+95),fill=oscuro)
        elif motivo=='silla':
            draw.rectangle((cx-180,cy-255,cx+180,cy+85),fill=(67,52,49,255),outline=oro,width=13)
            draw.rectangle((cx-225,cy+90,cx+225,cy+160),fill=(83,64,48,255),outline=oro,width=9)
            for xx in (cx-150,cx+150):draw.line((xx,cy+155,xx,cy+310),fill=borde,width=19)
        else:
            draw.rectangle((cx-250,cy-285,cx+250,cy+285),fill=(80,64,59,255),outline=oro,width=22)
            draw.ellipse((cx-100,cy-175,cx+100,cy+100),fill=(130,150,160,255))
    elif motivo=='bosque':
        for k in range(6):
            x=cx-390+k*150
            draw.line((x,cy+330,x,cy-290),fill=oscuro,width=28)
            draw.line((x,cy-100,x-120,cy-230),fill=oscuro,width=14)
            draw.line((x,cy-150,x+140,cy-280),fill=oscuro,width=13)
    else:
        # Escena abstracta: no inventar objetos que no están en el relato.
        draw.rectangle((cx-275,cy-200,cx+275,cy+200),outline=(85,107,130,120),width=4)

def _terror_escenas_procedurales(caso, carpeta, numero):
    """Ilustraciones contextuales: una por párrafo del guion narrado."""
    from PIL import Image,ImageDraw,ImageFilter
    import numpy as np
    carpeta=Path(carpeta);carpeta.mkdir(parents=True,exist_ok=True)
    escenas=_plan_visual_semantico(caso)
    if not escenas:
        escenas=[{'indice':i,'tipo':'escena','texto':caso.get('titulo',''),
                 'motivo':'libro','motivos_detectados':['libro'],'recurso':f'imagen_{i:02}.jpg'}
                for i in range(max(1,numero))]
    numero=len(escenas)
    W,H=1600,900
    seed=int.from_bytes(hashlib.sha256(str(caso.get('id',caso.get('titulo',''))).encode()).digest()[:8],'big')
    archivos=[]
    for i,escena in enumerate(escenas):
        rng=random.Random(seed+i*7919)
        y=np.linspace(0,1,H,dtype=np.float32)[:,None,None]
        arriba=np.array((9,13,26),dtype=np.float32)[None,None,:]
        abajo=np.array((31+i%5*3,35,52+i%4*4),dtype=np.float32)[None,None,:]
        img=Image.fromarray(np.broadcast_to((arriba*(1-y)+abajo*y).astype('uint8'),(H,W,3)).copy())
        d=ImageDraw.Draw(img,'RGBA')
        for j in range(80):
            x=rng.randrange(W);yy=rng.randrange(H);rad=rng.choice((1,2,3))
            d.ellipse((x-rad,yy-rad,x+rad,yy+rad),fill=(130,167,190,rng.randrange(18,85)))
        # Escenario deliberadamente ilustrado; sujeto principal ocupa el centro.
        d.ellipse((430,90,1290,810),fill=(36,53,72,160))
        _dibujar_motivo_terror(d,escena['motivo'],W,H,rng)
        if escena['motivo']=='texto_contextual':
            from PIL import ImageFont
            try:
                font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',39)
            except OSError:
                font=ImageFont.load_default()
            frase=escena['frase_visual']
            lineas=[];actual=''
            for palabra in frase.split():
                propuesta=(actual+' '+palabra).strip()
                if d.textlength(propuesta,font=font)>990 and actual:
                    lineas.append(actual);actual=palabra
                else:actual=propuesta
            if actual:lineas.append(actual)
            for idx,linea in enumerate(lineas[:4]):
                d.text((280,345+idx*66),linea,font=font,
                       fill=(224,226,228,255),stroke_width=2,stroke_fill=(8,11,20,255))
        capa=Image.new('RGBA',(W,H));niebla=ImageDraw.Draw(capa)
        for j in range(4):
            yy=H-130+j*55
            niebla.ellipse((80,yy-65,W-80,yy+55),fill=(130,147,172,25))
        img=Image.alpha_composite(img.convert('RGBA'),capa.filter(ImageFilter.GaussianBlur(30))).convert('RGB')
        archivo=carpeta/f'imagen_{i:02}.jpg'
        img.save(archivo,quality=92,optimize=True)
        archivos.append(archivo)
    (carpeta.parent/'PLAN_VISUAL_ESCENAS.json').write_text(
        json.dumps(escenas,ensure_ascii=False,indent=2),encoding='utf-8')
    return archivos

def _completar_visual_terror(caso,carpeta,fotos,creditos):
    if not (caso.get('_universal') and _univ_es_terror()):return fotos,creditos
    # Priorizar el argumento de cada escena frente a fotografías genéricas.
    originales=_terror_escenas_procedurales(caso,Path(carpeta)/'escenas_originales',
             max((AERO_VISUALES_OBJETIVO if MODO_VIRAL and IMAGENES_POR_ESCENA else IMAGENES_MINIMAS),len(caso.get('_plan_visual') or [])-1))
    fotos.clear();creditos.clear()
    escenas_contextuales=_plan_visual_semantico(caso)
    for i,origen in enumerate(originales):
        destino=Path(carpeta)/f'imagen_{i:02}.jpg'
        shutil.copy2(origen,destino)
        fotos.append(destino)
        motivo=escenas_contextuales[i]['motivo'] if i<len(escenas_contextuales) else 'texto_contextual'
        creditos.append({'archivo':destino.name,'titulo':f'Ilustración contextual: {motivo}',
            'pagina':'','url_original':'','licencia':'Arte procedural original creado para este video',
            'licencia_url':'','autor':'AEROFACTUM Universal (generación algorítmica local)',
            'atribucion':'Ilustración, no evidencia de hechos reales',
            'puntuacion_relevancia':20,'terminos_relacionados':[motivo],
            'frase_narrada':escenas_contextuales[i]['frase_visual'] if i<len(escenas_contextuales) else '',
            'consulta_origen':'generación local sin API','uso':'Ilustración ficticia de la escena',
            'tipo_recurso':'ilustracion_procedural'})
    print(f'  Visual contextual: {len(fotos)} ilustraciones, una por escena narrativa.',flush=True)
    return fotos,creditos


def buscar_fotos(caso,session,carpeta):
    from PIL import Image,ImageOps
    from io import BytesIO
    fotos=[];creditos=[];hashes=set();descartes=[]
    if caso.get('_universal') and _univ_es_terror() and caso.get('_plan_visual'):
        fotos,creditos=_completar_visual_terror(caso,carpeta,fotos,creditos)
        (carpeta/'creditos_imagenes.json').write_text(json.dumps(creditos,ensure_ascii=False,indent=2),encoding='utf-8')
        (carpeta/'imagenes_descartadas.json').write_text('[]',encoding='utf-8')
        (carpeta/'CREDITOS_Y_LICENCIAS.txt').write_text('Escenas originales ilustradas; no fotografías de hechos reales.\n',encoding='utf-8')
        return fotos,creditos
    configurar_reintentos_wikimedia(session)
    queries=_consultas_fotos(caso)
    # Sólo consultas ancladas al caso concreto, NUNCA búsquedas genéricas
    # como «science research laboratory equipment».
    principal=caso.get('_titulo_caso',caso['titulo']).split(':')[0].strip()
    # Las consultas específicas y contextuales ya las aporta _consultas_fotos.
    caso_id=(caso.get('_episodio') or {}).get('caso_id','')
    # Consultas de respaldo dirigidas al fenómeno, NO a temas científicos genéricos.
    queries=list(dict.fromkeys(queries))[:max(6,min(18,int(os.getenv('AERO_CONSULTAS_FOTOS','14'))))]
    api='https://commons.wikimedia.org/w/api.php'
    candidatos=[];titulos_vistos=set()
    rate_limitado = False
    for i_busqueda, busqueda in enumerate(queries):
        # Parar una vez exista un banco suficiente de candidatos para descargar.
        if not caso.get('_consultas_escenas') and i_busqueda >= 6 and len(candidatos) >= max(18, IMAGENES_MINIMAS*4):
            print('  Commons: suficientes candidatos; se evita consultar búsquedas adicionales.',flush=True)
            break
        if i_busqueda:
            time.sleep(1.5)  # Evitar ráfagas a la API de Wikimedia
        try:
            params=dict(action='query',format='json',generator='search',
                        gsrsearch=busqueda,gsrnamespace=6,gsrlimit=12,
                        prop='imageinfo',iiprop='url|extmetadata',iiurlwidth=2200)
            resp=session.get(api,params=params,timeout=(8,16))
            if resp.status_code == 429:
                rate_limitado = True
                espera = resp.headers.get('Retry-After', 'no especificado')
                aviso = (f'Wikimedia Commons respondió HTTP 429. Se detienen todas las búsquedas '
                         f'para respetar su límite. Retry-After: {espera}. '
                         'No se fuerza la publicación sin fotografías válidas.')
                print('  ' + aviso, flush=True)
                descartes.append({'busqueda':busqueda,'razon':'HTTP 429; búsqueda detenida',
                                  'retry_after':str(espera)})
                break
            resp.raise_for_status()
            paginas=resp.json().get('query',{}).get('pages',{})
            for page in paginas.values():
                info=(page.get('imageinfo') or [None])[0]
                if not info:continue
                titulo_archivo=page.get('title','')
                if titulo_archivo in titulos_vistos:continue
                titulos_vistos.add(titulo_archivo)
                meta=info.get('extmetadata') or {}
                if not es_foto_real_metadata(titulo_archivo,meta):
                    descartes.append({'archivo':titulo_archivo,'razon':'No es fotografía real: esquema, mapa, render, ilustración u otro recurso gráfico','busqueda':busqueda})
                    continue
                puntos,matches=evaluar_relevancia_foto(caso,titulo_archivo,meta,busqueda)
                if puntos==0:
                    descartes.append({'archivo':titulo_archivo,'razon':'Sin anclas temáticas suficientes','busqueda':busqueda})
                    continue
                if not licencia_valida(info):
                    descartes.append({'archivo':titulo_archivo,'razon':'Licencia no compatible','busqueda':busqueda})
                    continue
                url=info.get('url','')
                mini=info.get('thumburl') or url
                if not url.lower().split('?')[0].endswith(('.jpg','.jpeg','.png','.webp')):
                    continue
                if not mini.startswith('https://'):continue
                candidatos.append((puntos,titulo_archivo,info,mini,matches,busqueda))
        except Exception as exc:
            motivo=str(exc)[:400]
            descartes.append({'busqueda':busqueda,'razon':'Error de consulta a Wikimedia Commons',
                              'detalle':motivo})
            print('  Búsqueda Commons falló:',busqueda,'|',motivo[:150],flush=True)
    if rate_limitado and not candidatos:
        (carpeta/'AVISO_WIKIMEDIA_429.txt').write_text(
            'Wikimedia Commons limitó el acceso HTTP 429. No insistir con más búsquedas; '
            'reprogramar la ejecución o utilizar fotografías ya verificadas con licencias y atribución.\n',
            encoding='utf-8')
    candidatos=_ordenar_candidatos_83(caso,candidatos)
    print(f'  Commons: {len(candidatos)} fotografías candidatas tras {len(queries)} consultas planificadas.',flush=True)
    for puntos,archivo,info,url,matches,busqueda in candidatos:
        if len(fotos)>=MAX_IMAGENES:break
        try:
            r=session.get(url,timeout=(8,20))
            if r.status_code == 429:
                print('  Wikimedia limitó también la descarga de fotos (HTTP 429).',flush=True)
                descartes.append({'archivo':archivo,'razon':'HTTP 429 en descarga'})
                break
            r.raise_for_status()
            if len(r.content)>22_000_000:continue
            im=Image.open(BytesIO(r.content))
            im=ImageOps.exif_transpose(im).convert('RGB')
            if min(im.size)<600:continue
            huella=_huella_foto_83(im)
            if any((huella ^ h).bit_count()<=5 for h in hashes):
                descartes.append({'archivo':archivo,'razon':'Imagen visualmente casi duplicada'})
                continue
            im.thumbnail((2400,1800),Image.Resampling.LANCZOS)
            destino=carpeta/f'imagen_{len(fotos):02}.jpg'
            im.save(destino,quality=91,optimize=True)
            metadata=info.get('extmetadata') or {}
            creditos.append({
                'archivo':destino.name,'titulo':archivo,
                'pagina':'https://commons.wikimedia.org/wiki/'+archivo.replace(' ','_'),
                'url_original':info.get('url',''),
                'licencia':limpiar_html(metadata.get('LicenseShortName',{}).get('value','')),
                'licencia_url':limpiar_html(metadata.get('LicenseUrl',{}).get('value','')),
                'autor':limpiar_html(metadata.get('Artist',{}).get('value','')),
                'atribucion':limpiar_html(metadata.get('Attribution',{}).get('value','')),
                'puntuacion_relevancia':puntos,
                'terminos_relacionados':matches,
                'consulta_origen':busqueda,
                'objeto_visual': ' '.join(limpiar_html(metadata.get(k,{}).get('value','')) for k in ('ImageDescription','ObjectName'))[:3000],
                'detalle_visual': ' '.join(limpiar_html(metadata.get(k,{}).get('value','')) for k in ('ImageDescription','ObjectName','Categories'))[:3000],
                'uso':'Fotografía documental de contexto; puede no retratar exactamente el caso descrito'
            })
            fotos.append(destino)
            hashes.add(huella)
            print('  Aprobada:',archivo[:65], '| puntuación:',puntos,'|',','.join(matches[:5]))
        except Exception as exc:
            descartes.append({'archivo':archivo,'razon':'No descargable o baja resolución: '+str(exc)[:100]})
    fotos,creditos=_completar_visual_terror(caso,carpeta,fotos,creditos)
    (carpeta/'creditos_imagenes.json').write_text(
        json.dumps(creditos,ensure_ascii=False,indent=2),encoding='utf-8')
    (carpeta/'imagenes_descartadas.json').write_text(
        json.dumps(descartes[:300],ensure_ascii=False,indent=2),encoding='utf-8')
    with (carpeta/'CREDITOS_Y_LICENCIAS.txt').open('w',encoding='utf-8') as f:
        f.write('Fotografías reales de Commons más, cuando corresponde a ficción de terror, ilustraciones procedurales originales identificadas como tales.\n')
        f.write('Comprobar pertinencia, licencias y atribución antes de publicar.\n\n')
        for c in creditos:
            f.write(f"{c['archivo']} | {c['titulo']} | Relevancia {c['puntuacion_relevancia']} | {','.join(c['terminos_relacionados'])} | Autor: {c['autor']} | Licencia: {c['licencia']} | {c['licencia_url']} | {c['pagina']}\n")
    if len(fotos) < IMAGENES_MINIMAS_ABSOLUTAS:
        aviso=(f'No se encontraron recursos visuales suficientes y válidos para «{principal}». '
               'Las fotos externas requieren licencia CC0 o dominio público y pertinencia; '
               'para el nicho de terror también se admiten escenas procedurales originales. '
               'Consulta imagenes_descartadas.json y los diagnósticos de generación.')
        (carpeta/'AVISO_SIN_FOTOGRAFIAS.txt').write_text(aviso+'\n',encoding='utf-8')
        raise RuntimeError(aviso)
    if len(fotos)<IMAGENES_MINIMAS:
        aviso=(f'REVISIÓN VISUAL: sólo {len(fotos)} recurso(s) pertinentes para «{principal}» '
               f'(objetivo: {IMAGENES_MINIMAS}). Se crearán varios encuadres de los '
               'recursos válidos; revisa el video antes de publicar.')
        print(aviso,flush=True)
        (carpeta/'AVISO_REVISION_VISUAL.txt').write_text(aviso+'\n',encoding='utf-8')
    # Hoja visual de auditoría: miniaturas reales de todos los archivos aceptados
    # con nombre y puntuación para detectar falsos positivos antes de publicar.
    from PIL import ImageDraw,ImageFont,ImageOps
    columnas=2; ancho_celda=600; alto_celda=420
    filas=max(1,math.ceil(len(fotos)/columnas))
    hoja=Image.new('RGB',(columnas*ancho_celda,filas*alto_celda),'#0e1727')
    dib=ImageDraw.Draw(hoja)
    try: ft=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',19)
    except Exception: ft=ImageFont.load_default()
    for i,(foto,credito) in enumerate(zip(fotos,creditos)):
        x=(i%columnas)*ancho_celda;y=(i//columnas)*alto_celda
        with Image.open(foto) as base:
            img=ImageOps.fit(base.convert('RGB'),(580,330),method=Image.Resampling.LANCZOS)
        hoja.paste(img,(x+10,y+8))
        etiqueta=f"{i+1:02}  R:{credito['puntuacion_relevancia']}  {credito['titulo'].removeprefix('File:')[:49]}"
        dib.text((x+12,y+346),etiqueta,fill='#ffffff',font=ft)
        dib.text((x+12,y+375),'Tema: '+', '.join(credito['terminos_relacionados'][:5])[:65],fill='#9ee9ff',font=ft)
    hoja.save(carpeta/'REVISION_VISUAL_IMAGENES.jpg',quality=87)
    return fotos,creditos

# ======================== GUION ORIGINAL =========================
def plan_guion(caso):
    """Una escena = un párrafo de voz = una duración medida de TTS.
    Se parafrasean fichas documentales curadas; no se inventan testimonios ni citas.
    """
    pistas=caso['pistas']; trozos=[]
    trozos.append(('gancho',caso['gancho']))
    trozos.append(('pregunta',caso['pregunta']+' Antes de escuchar la respuesta, reconstruyamos lo que realmente se observó. No confundiremos lo que está registrado con lo que alguien imaginó después.'))
    trozos.append(('contexto',caso['contexto']))
    for i,p in enumerate(pistas):
        entradas=['La primera pista documentada es esta.','La investigación encontró un segundo detalle.','Con el tiempo apareció una conexión reveladora.','Y aquí llegó la pista que cambió la interpretación.']
        trozos.append(('pista',entradas[min(i,3)]+' '+p))
    trozos.append(('hipotesis','Llegados a este punto conviene preguntarse qué explicación puede acomodar todas las pistas sin exigir fenómenos inventados. La hipótesis más llamativa no siempre es la que tiene mejores pruebas. Una investigación rigurosa distingue entre coincidencia, inferencia y observación directa.'))
    trozos.append(('revelacion',caso['giro']))
    trozos.append(('desarrollo',caso['importancia']))
    trozos.append(('significado',caso['cierre']))
    trozos.append(('conclusion',caso['cierre']+' ¿Qué otra pregunta aeronáutica te gustaría investigar? Te leo en los comentarios.'))
    trozos.append(('cta','Si te gustó este contenido, dale Like y Suscríbete! Muchas gracias por tu visita y nos vemos en un próximo video!'))
    return trozos

# ======================== NARRACIÓN TTS ==========================
def en_hilo(coro):
    caja={}
    def tarea():
        try:caja['resultado']=asyncio.run(coro())
        except BaseException as e:caja['error']=e
    t=threading.Thread(target=tarea,daemon=True);t.start();t.join()
    if 'error' in caja:raise caja['error']
    return caja.get('resultado')

def tiempo_medio_audio(path):
    with wave.open(str(path),'rb') as w:return w.getnframes()/w.getframerate()

# Términos aeronáuticos que habitualmente se pronuncian en inglés.
# Emparejar frases largas antes que palabras sueltas evita cortes incorrectos.
_TERMINOS_INGLES = (
    'angle of attack', 'ground handling', 'flight management system',
    'indicated airspeed', 'true airspeed', 'calibrated airspeed',
    'ground speed', 'flight deck', 'flight director', 'flight level',
    'glass cockpit', 'traffic collision avoidance system',
    'instrument landing system', 'wind shear', 'jet stream',
    'go-around', 'go around', 'touch and go', 'pushback', 'turnaround',
    'holding pattern', 'stall', 'spoiler', 'slat', 'flap', 'flaps',
    'thrust reverser', 'autothrottle', 'autopilot', 'cockpit',
    'airspeed', 'aircraft', 'airliner', 'airbus', 'boeing',
    'runway', 'taxiway', 'taxi', 'takeoff', 'landing',
    'pitch', 'roll', 'yaw', 'heading', 'altitude',
    'crosswind', 'headwind', 'tailwind', 'downwind',
    'upwind', 'holding', 'briefing', 'debriefing',
    'checklist', 'clearance', 'mayday', 'pan-pan',
    'readback', 'squawk', 'call sign', 'callsign',
    'bleed air', 'bleed', 'overspeed', 'windshear',
    'fly-by-wire', 'fly by wire', 'airworthiness',
    'airframe', 'flight plan', 'ground effect',
    'wet lease', 'dry lease', 'load factor', 'hub',
    'slot', 'slots', 'yield', 'block time',
    'wake turbulence', 'microburst', 'jet lag',
)
_SIGLAS_INGLES = (
    'IAS','TAS','CAS','EAS','ATC','ILS','VOR','DME','GPS','GNSS','TCAS',
    'GPWS','EGPWS','NOTAM','METAR','TAF','RVR','RNAV','RNP','APU','GPU',
    'EFB','MEL','ETOPS','FMS','FMC','SID','STAR','VFR','IFR','IATA',
    'FAA','EASA','ICAO','PAPI','VASI','QNH','QFE','MACH','NDB','ADF',
)
# Siglas no ambiguas: se requiere mayúscula exacta (evita 'tas' o 'cas' en español).
_PATRON_INGLES = re.compile(
    r'(?<!\w)(?:' + '|'.join(
        re.escape(t) for t in sorted(_TERMINOS_INGLES, key=len, reverse=True)
    ) + r')(?!\w)', re.IGNORECASE
)
_PATRON_SIGLAS = re.compile(
    r'(?<![A-Za-zÁÉÍÓÚÜÑáéíóúüñ])(?:' + '|'.join(
        re.escape(x) for x in sorted(_SIGLAS_INGLES, key=len, reverse=True)
    ) + r')(?![A-Za-zÁÉÍÓÚÜÑáéíóúüñ])'
)

def fragmentar_por_idioma(texto):
    """Conserva el texto original; detecta anglicismos técnicos sin traducirlos."""
    if not PRONUNCIACION_INGLES:
        return [('es', texto)]
    encontrados=[]
    for m in _PATRON_INGLES.finditer(texto):
        encontrados.append((m.start(),m.end(),False))
    for m in _PATRON_SIGLAS.finditer(texto):
        encontrados.append((m.start(),m.end(),True))
    # Ordenar por posición, privilegiando coincidencia más larga.
    encontrados.sort(key=lambda item:(item[0],-(item[1]-item[0])))
    fragmentos=[]; cursor=0
    for ini,fin,sigla in encontrados:
        if ini < cursor: continue
        if ini>cursor:
            fragmentos.append(('es',texto[cursor:ini]))
        literal=texto[ini:fin]
        pronunciacion=' '.join(literal) if sigla else literal
        fragmentos.append(('en',literal,pronunciacion))
        cursor=fin
    if cursor<len(texto):fragmentos.append(('es',texto[cursor:]))
    # La puntuación aislada no debe enviarse como un fragmento de voz:
    # Edge TTS podría devolver audio vacío y detener toda la producción.
    limpios=[]
    for item in fragmentos:
        if not item[1].strip(' \t\r\n,.;:!?¡¿()«»"'):
            if limpios:
                anterior=limpios[-1]
                if len(anterior)==3:
                    limpios[-1]=(anterior[0],anterior[1]+item[1],anterior[2]+item[1])
                else:
                    limpios[-1]=(anterior[0],anterior[1]+item[1])
            else:
                # Conservar la puntuación inicial y adjuntarla al siguiente fragmento.
                limpios.append(item)
        else:
            if limpios and not limpios[-1][1].strip(' \t\r\n,.;:!?¡¿()«»"'):
                previo=limpios.pop()[1]
                item=(item[0],previo+item[1],previo+item[2]) if len(item)==3 else (item[0],previo+item[1])
            limpios.append(item)
    return limpios or [('es',texto)]

def normalizar_unidades_narracion(texto):
    """Expande NM/nm como millas náuticas únicamente para la locución.

    No modifica el guion original ni los documentos fuente. Evita la lectura
    incorrecta como newton metros y respeta límites de palabra (no altera
    términos como GNMM, nombres ni textos que contengan esas letras).
    """
    patron = re.compile(r'(?<!\w)(NM|nm)(?!\w)')
    def sustituir(coincidencia):
        prefijo = texto[:coincidencia.start()]
        # Con una unidad explícitamente precedida por 1, usar singular.
        es_uno = bool(re.search(r'(?<![\d.,])\b1\s*$', prefijo))
        return 'milla náutica' if es_uno else 'millas náuticas'
    return patron.sub(sustituir, str(texto))


def generar_voces(plan,carpeta):
    import edge_tts
    async def tarea():
        bloques=[];cues=[];posicion_muestras=0;salida=carpeta/'narracion.wav';sample_rate=24000
        with wave.open(str(salida),'wb') as final:
            final.setnchannels(1);final.setsampwidth(2);final.setframerate(sample_rate)
            for i,(tipo,texto) in enumerate(plan):
                inicio=posicion_muestras/sample_rate
                marcas=[]
                fragmentos=fragmentar_por_idioma(texto)
                voces_usadas=[]
                for j,frag in enumerate(fragmentos):
                    idioma,literal=frag[:2]
                    texto_tts=(normalizar_unidades_narracion(frag[2] if len(frag)>2 else literal) if _nicho_aeronautico() else (frag[2] if len(frag)>2 else literal))
                    voz_actual=VOZ  # Lorenzo en todos los fragmentos
                    voces_usadas.append(idioma)
                    audio=bytearray();marcas_fragmento=[];error_tts=None
                    for intento in range(1,5):
                        audio.clear();marcas_fragmento.clear()
                        try:
                            tts=edge_tts.Communicate(texto_tts,voice=voz_actual,rate=VELOCIDAD)
                            async for dato in tts.stream():
                                if dato['type']=='audio':audio.extend(dato['data'])
                                elif dato['type']=='WordBoundary':
                                    marcas_fragmento.append((dato['text'],dato['offset']/1e7,dato['duration']/1e7))
                            if not audio:raise RuntimeError('Edge TTS devolvió audio vacío')
                            break
                        except Exception as e:
                            error_tts=e
                            print(f'  Aviso TTS escena {i+1} fragmento {j+1}, intento {intento}: {type(e).__name__}: {e}',flush=True)
                            if intento<4:await asyncio.sleep(2*intento)
                    if not audio:
                        raise RuntimeError(f'TTS falló en escena {i+1}, fragmento {j+1} ({voz_actual}): {error_tts}')
                    mp3=carpeta/f'voz_{i:02}_{j:02}.mp3';mp3.write_bytes(audio)
                    wav=carpeta/f'voz_{i:02}_{j:02}.wav'
                    subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error',
                                    '-i',str(mp3),'-ac','1','-ar',str(sample_rate),
                                    '-c:a','pcm_s16le',str(wav)],check=True)
                    with wave.open(str(wav),'rb') as individual:
                        n=individual.getnframes()
                        final.writeframes(individual.readframes(n))
                    inicio_fragmento=posicion_muestras/sample_rate
                    dur=n/sample_rate
                    if tipo!='cta':
                        if idioma=='en':
                            # Mostrar la grafía original (IAS, turnaround) en los subtítulos.
                            marcas.append((literal.strip(),inicio_fragmento-inicio,dur))
                        elif marcas_fragmento:
                            marcas.extend((palabra,inicio_fragmento-inicio+offset,duracion)
                                          for palabra,offset,duracion in marcas_fragmento)
                        else:
                            # Respaldo para fragmentos sin WordBoundary.
                            palabras=literal.split()
                            for k,palabra in enumerate(palabras):
                                marcas.append((palabra,inicio_fragmento-inicio+dur*k/max(1,len(palabras)),
                                               dur/max(1,len(palabras))))
                    posicion_muestras+=n
                dur_total=posicion_muestras/sample_rate-inicio
                bloques.append(dict(tipo=tipo,texto=texto,inicio=inicio,duracion=dur_total))
                if tipo!='cta' and marcas:
                    grupo=[];comienzo=0;fin=0
                    for palabra,offset,duracion in marcas:
                        if not grupo:comienzo=offset
                        grupo.append(palabra.strip());fin=offset+max(.09,duracion)
                        if len(grupo)>=7 or fin-comienzo>2.5:
                            cues.append((inicio+comienzo,inicio+min(dur_total,fin),' '.join(grupo)))
                            grupo=[]
                    if grupo:cues.append((inicio+comienzo,inicio+min(dur_total,fin),' '.join(grupo)))
                if 'en' in voces_usadas:
                    print(f'  Voz {i+1:02}/{len(plan)}: {dur_total:.1f}s · inglés nativo en {voces_usadas.count("en")} término(s)',flush=True)
                else:
                    print(f'  Voz {i+1:02}/{len(plan)}: {dur_total:.1f}s',flush=True)
        inicio_cta=next((b['inicio'] for b in bloques if b['tipo']=='cta'),None)
        if inicio_cta is not None:
            cues=[(a,min(b,inicio_cta-0.12),txt) for a,b,txt in cues
                  if a<inicio_cta-0.12 and min(b,inicio_cta-0.12)-a>=0.15]
        return bloques,cues,salida
    return en_hilo(tarea)

# ==================== SUBTÍTULOS ESTILO ORIGINAL ====================
def srt_marca(t):
    n=round(max(0,t)*1000);hh,n=divmod(n,3600000);mm,n=divmod(n,60000);ss,ms=divmod(n,1000)
    return f'{hh:02}:{mm:02}:{ss:02},{ms:03}'
def ass_marca(t):
    n=round(max(0,t)*100);hh,n=divmod(n,360000);mm,n=divmod(n,6000);ss,cc=divmod(n,100)
    return f'{hh}:{mm:02}:{ss:02}.{cc:02}'
def ass_escape(t):return str(t).replace('\\','\\\\').replace('{','(').replace('}',')').replace('\n','\\N')
def anticipar_subtitulos(cues, adelanto=SUBTITULOS_ADELANTO):
    """Desplaza texto respecto a la locución y preserva orden sin solapamientos.

    El archivo ASS incrustado y el SRT externo reciben idénticos tiempos.
    El texto comienza ligeramente antes que el audio; el final de cada frase
    no se solapa con la frase siguiente ni con el CTA.
    """
    adelantados=[]
    for a,b,txt in sorted(cues, key=lambda x:(x[0],x[1])):
        inicio=max(0.0,float(a)-adelanto)
        fin=max(inicio+0.16,float(b)-adelanto)
        if adelantados and inicio < adelantados[-1][1]:
            previo=adelantados[-1]
            adelantados[-1]=(previo[0],max(previo[0]+0.08,inicio-0.015),previo[2])
            # Es preferible no mostrar dos cajas encima a la vez.
            inicio=max(inicio,adelantados[-1][1]+0.015)
            fin=max(fin,inicio+0.16)
        adelantados.append((inicio,fin,txt))
    return adelantados


def subtitulos(cues,carpeta, inicio_cta=None):
    cues=anticipar_subtitulos(cues)
    # Corte adicional: ningún subtítulo, incluido el último anterior,
    # puede aparecer cuando comienza la escena final de Like/Suscríbete.
    # Se aplica tanto al SRT como al ASS incrustado en el MP4.
    if inicio_cta is not None:
        limite=max(0.0, float(inicio_cta)-0.12)
        cues=[(max(0.0,a),min(b,limite),txt)
              for a,b,txt in cues if a<limite and min(b,limite)-a>=0.15]
    srt=carpeta/'subtitulos.srt';ass=carpeta/'subtitulos.ass'
    with srt.open('w',encoding='utf-8') as f:
        for i,(a,b,txt) in enumerate(cues,1):f.write(f'{i}\n{srt_marca(a)} --> {srt_marca(max(a+.15,b))}\n{txt}\n\n')
    # ASS: mismo estilo de texto grande blanco con contorno/caja discreta, abajo.
    # BorderStyle=3 = caja opaca ajustada al texto (no barra de ancho completo).
    ass_head='''[Script Info]
Title: AEROFACTUM - Subtitulos
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
ScaledBorderAndShadow: yes
WrapStyle: 0
[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Main,DejaVu Sans,53,&H00FFFFFF,&H00FFFFFF,&H99000000,&HAA06111E,-1,0,0,0,100,100,0,0,3,13,0,2,105,105,92,1
[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
'''
    with ass.open('w',encoding='utf-8') as f:
        f.write(ass_head)
        for a,b,txt in cues:
            if b>a:f.write(f'Dialogue: 0,{ass_marca(a)},{ass_marca(max(a+.15,b))},Main,,0,0,0,,{ass_escape(txt)}\n')
    return srt,ass

# ============== MÚSICA CINEMATOGRÁFICA ORIGINAL ==============
def _acorde_cinematico(t, notas, sr):
    """Pad cálido de acordes menores: suma de senos suaves sin samples externos."""
    import numpy as np
    salida=np.zeros_like(t,dtype=np.float64)
    for indice,hz in enumerate(notas):
        # Fundamentos con ligeras desafinaciones y armónicos atenuados.
        fase=2*np.pi*hz*t
        oscilador=(np.sin(fase)+0.20*np.sin(2*fase+0.3)
                    +0.055*np.sin(3*fase+0.8))
        oscilador+=0.12*np.sin(2*np.pi*hz*1.0031*t+indice*1.9)
        salida+=(0.35 if indice==0 else 0.22)*oscilador
    # Respiración lenta sin oscilaciones bruscas.
    return salida*(0.78+0.10*np.sin(2*np.pi*0.085*t))


def _bloque_musica_cinematica(desde_muestra, cantidad, sr, duracion, semilla, tempo):
    """Composición original reproducible con pad, arpegio y pulso sutil.

    La composición depende del identificador del episodio; no usa pistas grabadas,
    los dígitos de pi ni ninguna API. Se sintetiza por bloques para ahorrar RAM.
    """
    import numpy as np
    t=(desde_muestra+np.arange(cantidad,dtype=np.float64))/sr
    # Progresiones en re menor, con distintas inversiones según el episodio.
    progresiones=(
        ((146.83,220.00,293.66,349.23), (116.54,174.61,233.08,293.66),
         (130.81,174.61,220.00,349.23), (130.81,196.00,261.63,329.63)),
        ((146.83,220.00,293.66,349.23), (98.00,146.83,196.00,233.08),
         (116.54,174.61,233.08,293.66), (110.00,164.81,220.00,277.18)),
    )
    acordes=progresiones[semilla % len(progresiones)]
    compas_seg=4*60.0/tempo
    acorde_seg=compas_seg*2
    posicion=t/acorde_seg
    actual=np.floor(posicion).astype(np.int64)
    fraccion=posicion-actual
    # Crossfade armónico en el último 20% de cada sección, sin saltos.
    mezcla=np.clip((fraccion-0.80)/0.20,0.0,1.0)
    mezcla=mezcla*mezcla*(3-2*mezcla)
    pad=np.zeros(cantidad,dtype=np.float64)
    for k in np.unique(actual):
        mascara=actual==k
        acorde=acordes[int(k)%4]
        siguiente=acordes[(int(k)+1)%4]
        onda=_acorde_cinematico(t[mascara],acorde,sr)
        onda2=_acorde_cinematico(t[mascara],siguiente,sr)
        pad[mascara]=onda*(1-mezcla[mascara])+onda2*mezcla[mascara]
    # Arpegio puntillista con notas de los acordes, ataque suave y cola amplia.
    paso=60.0/tempo
    numero_paso=np.floor(t/paso).astype(np.int64)
    edad=t-numero_paso*paso
    arpegio=np.zeros(cantidad,dtype=np.float64)
    for numero in np.unique(numero_paso):
        if numero%4==3:  # una pausa regular evita competir con la voz
            continue
        mask=numero_paso==numero
        acorde=acordes[(int(numero)//8)%4]
        indice=(int(numero)*3+semilla)%len(acorde)
        frecuencia=acorde[indice]*2
        local=edad[mask]
        envelope=(1-np.exp(-local/0.055))*np.exp(-local/0.44)
        arpegio[mask]=0.20*envelope*(np.sin(2*np.pi*frecuencia*t[mask])+
                                    0.12*np.sin(4*np.pi*frecuencia*t[mask]))
    # Pulso grave moderado (uno cada dos tiempos), sin baterías ni samples.
    periodo=2*paso
    golpe=t%periodo
    pulso=0.11*np.exp(-golpe/0.17)*np.sin(2*np.pi*(47+18*np.exp(-golpe/0.08))*golpe)
    pista=pad*0.73+arpegio+pulso
    # Entrada y salida gradual para evitar cortes musicales al final.
    entrada=np.clip(t/2.8,0,1)
    salida=np.clip((duracion-t)/3.5,0,1)
    envelope=np.sin(entrada*np.pi/2)**2*np.sin(salida*np.pi/2)**2
    return (pista*envelope).astype(np.float32)


def mezclar_cinematica(voz,carpeta):
    """Genera banda sonora instrumental original y mezcla voz sin perder claridad.

    Bloques de 4 segundos, atenuación musical bajo narración y control de picos.
    Respeta los canales, frecuencia de muestreo y duración originales de la voz.
    """
    import numpy as np
    destino=carpeta/'voz_musica_cinematica.wav'
    # Semilla estable por episodio: cada producción tiene variantes musicales.
    semilla=int(hashlib.sha256(carpeta.name.encode('utf-8')).hexdigest()[:8],16)
    with wave.open(str(voz),'rb') as entrada:
        sr=entrada.getframerate()
        canales=entrada.getnchannels()
        ancho=entrada.getsampwidth()
        if ancho!=2 or canales not in (1,2):
            raise RuntimeError('Música cinematográfica requiere audio PCM de 16 bits mono o estéreo')
        muestras=entrada.getnframes()
        duracion=muestras/sr if sr else 0
        with wave.open(str(destino),'wb') as salida:
            salida.setnchannels(canales)
            salida.setsampwidth(2)
            salida.setframerate(sr)
            por_bloque=max(1,int(sr*4))
            cursor=0
            # Detector lento de presencia vocal, persistente entre bloques.
            presencia=0.0
            while cursor<muestras:
                n=min(por_bloque,muestras-cursor)
                origen=np.frombuffer(entrada.readframes(n),dtype='<i2').astype(np.float32)
                if len(origen)!=n*canales:
                    raise RuntimeError('Audio de voz truncado al generar música')
                audio=origen.reshape(n,canales)/32768.0
                pista=_bloque_musica_cinematica(cursor,n,sr,duracion,semilla,MUSICA_TEMPO)
                # Ducking con resolución de 50 ms; evita enmascarar consonantes.
                tam=max(1,int(sr*.05))
                voz_mono=np.mean(audio,axis=1)
                ganancia=np.empty(n,dtype=np.float32)
                for inicio in range(0,n,tam):
                    final=min(inicio+tam,n)
                    rms=float(np.sqrt(np.mean(voz_mono[inicio:final]**2)))
                    objetivo=1.0-(1.0-MUSICA_DUCKING)*np.clip(rms/.035,0,1)
                    presencia=0.75*presencia+0.25*objetivo
                    ganancia[inicio:final]=presencia
                musica=(pista*ganancia*MUSICA_VOLUMEN)[:,None]
                mezcla=audio+musica
                # Limitador por bloque sin clipping y sin amplificar silencios.
                pico=float(np.max(np.abs(mezcla))) if n else 0
                if pico>0.97:
                    mezcla*=0.97/pico
                salida.writeframes((np.clip(mezcla,-.97,.97)*32767).astype('<i2').tobytes())
                cursor+=n
    return destino

# ======================== TARJETAS E IMÁGENES ====================
def font_path():
    """Busca fuentes existentes en diferentes versiones de Colab/Pillow."""
    opciones=[
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf',
        '/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf',
        '/usr/local/share/fonts/DejaVuSans-Bold.ttf',
    ]
    return next((p for p in opciones if Path(p).is_file()),None)


def cargar_fuente(tamano, condensada=False):
    """No pasa None a ImageFont.truetype; usa un respaldo escalable."""
    from PIL import ImageFont
    candidatos=(
        ['/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf',
         '/usr/share/fonts/truetype/liberation2/LiberationSansNarrow-Bold.ttf']
        if condensada else []
    )+[
        font_path(),
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
        '/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf',
        'DejaVuSans-Bold.ttf',
        'DejaVuSans.ttf',
    ]
    for candidato in candidatos:
        if not candidato: continue
        try:
            return ImageFont.truetype(candidato,int(tamano))
        except (OSError,AttributeError,TypeError):
            continue
    try:
        return ImageFont.load_default(size=int(tamano))
    except TypeError:
        return ImageFont.load_default()

def escribir_en_caja(d,texto,caja,fuente,color,max_lineas=4,interlinea=1.12,stroke_width=2,stroke_fill='#101820',centrar_vertical=False):
    x0,y0,x1,y1=caja;palabras=texto.split();lineas=[];linea=''
    for palabra in palabras:
        prueba=(linea+' '+palabra).strip()
        ancho=d.textbbox((0,0),prueba,font=fuente,stroke_width=stroke_width)[2]
        if ancho>x1-x0 and linea:lineas.append(linea);linea=palabra
        else:linea=prueba
    if linea:lineas.append(linea)
    lineas=lineas[:max_lineas]
    alto=round(fuente.size*interlinea)
    y_inicio=y0
    if centrar_vertical:
        total=alto*len(lineas)
        y_inicio=y0+max(0,((y1-y0)-total)//2)
    for i,s in enumerate(lineas):
        ancho=d.textbbox((0,0),s,font=fuente,stroke_width=stroke_width)[2];xx=x0+((x1-x0)-ancho)//2
        d.text((xx,y_inicio+i*alto),s,font=fuente,fill=color,stroke_width=stroke_width,stroke_fill=stroke_fill)

# ============= MINIATURAS DE ALTO IMPACTO =============
# En las miniaturas no se utilizan textos informativos pequeños ni etiquetas.
# La promesa debe proceder de un hecho del caso, no de afirmaciones inventadas.
def gancho_miniatura(caso):
    """Título principal autónomo; no se corta ni depende del subtítulo."""
    return caso.get('mini_titulo',caso.get('_titulo_caso',caso['titulo']).upper())

def subtitulo_miniatura(caso,titulo_principal):
    """La promesa didáctica agrega valor sin inventar resultados."""
    cat=caso.get('categoria','')
    promesas={
        'AERODINÁMICA':'LA FÍSICA DETRÁS DE CADA VUELO',
        'MOTORES Y SISTEMAS':'ASÍ FUNCIONA POR DENTRO',
        'INSTRUMENTOS Y NAVEGACIÓN':'EL DETALLE QUE CAMBIA SU LECTURA',
        'METEOROLOGÍA':'ENTENDERLO AYUDA A PREVENIR RIESGOS',
        'OPERACIONES DE VUELO':'LA LÓGICA DETRÁS DE LA OPERACIÓN',
        'SEGURIDAD Y FACTOR HUMANO':'DECISIONES QUE IMPORTAN',
        'FINANZAS Y ECONOMÍA':'EL NEGOCIO DETRÁS DEL VUELO',
        'AEROPUERTOS Y ATC':'CÓMO ENCAJAN TODAS LAS PIEZAS',
        'MANTENIMIENTO Y CERTIFICACIÓN':'QUÉ REVISAN LOS ESPECIALISTAS',
        'AVIACIÓN DEL FUTURO':'LOS RETOS QUE FALTAN SUPERAR',
    }
    return caso.get('_mini_subtitulo') or promesas.get(cat,'EL MISTERIO DETRÁS DE LA HISTORIA' if _univ_es_terror() else 'DESCUBRE LA EXPLICACIÓN')

def portada_font_path():
    """Compatibilidad con código anterior; no se requiere una ruta válida."""
    return next((p for p in [
        '/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf',
        '/usr/share/fonts/truetype/liberation2/LiberationSansNarrow-Bold.ttf',
        font_path(),
    ] if p and Path(p).is_file()),None)

def foto_portada(fotos):
    """Escoge una foto ya verificada que además tenga contraste y detalle,
    evitando en lo posible fondos con texto o gráficos rotulados.
    No cambia la verificación temática ni introduce imágenes externas.
    """
    from PIL import Image,ImageOps
    import numpy as np, re
    terminos_evitar=('map','diagram','chart','poster','logo','inscription','text','caption','figure','drawing','illustration','label','newspaper','document','table')
    candidatos=[]
    for p in fotos:
        try:
            nombre=Path(p).name.lower()
            penal_meta=32 if any(t in nombre for t in terminos_evitar) else 0
            with Image.open(p) as f:
                orig=f.convert('RGB')
            if min(orig.size)<520: 
                continue
            im=ImageOps.fit(orig,(320,180),method=Image.Resampling.LANCZOS)
            arr=np.asarray(im,dtype=np.float32)
            g=np.asarray(im.convert('L'),dtype=np.float32)
            # detalle / contraste general
            borde=np.abs(np.diff(g,axis=0)).mean()+np.abs(np.diff(g,axis=1)).mean()
            contrast=float(g.std())
            color=float(arr.std(axis=2).mean())
            # interés visual hacia la derecha (sujeto de miniatura)
            zona=g[:,155:]
            detalle_dcha=float(np.abs(np.diff(zona,axis=1)).mean())
            # penalización simple para imágenes con texto: demasiados trazos pequeños
            gx=np.abs(np.diff(g,axis=1)); gy=np.abs(np.diff(g,axis=0))
            edge=((gx[:gy.shape[0],:]>26) & (gy[:,:gx.shape[1]]>26)).astype(np.uint8)
            # texto típico: muchas micro-esquinas repartidas en líneas horizontales
            row_density=edge.mean(axis=1)
            bands=((row_density>0.18).sum())
            text_penalty=min(38, bands*1.7)
            score=contrast*0.34+borde*0.33+detalle_dcha*0.34+color*0.10-penal_meta-text_penalty
            candidatos.append((score,p,{'penal_meta':penal_meta,'text_penalty':round(float(text_penalty),2)}))
        except Exception:
            continue
    if not candidatos:
        return fotos[0]
    mejor=max(candidatos,key=lambda x:x[0])
    return mejor[1]


def nombre_archivo_video(caso, extension):
    """Ruta legible derivada del título público, válida en Windows/Linux/macOS."""
    import unicodedata
    titulo = unicodedata.normalize('NFC', str(caso.get('titulo', '')).strip())
    titulo = re.sub(r'[\\/:*?"<>|\x00-\x1f\x7f]', ' ', titulo)
    titulo = re.sub(r'\s+', ' ', titulo).strip(' .')
    if not titulo:
        titulo = 'Video sin titulo'
    if titulo.upper().split('.')[0] in {
        'CON', 'PRN', 'AUX', 'NUL', *('COM'+str(i) for i in range(1,10)),
        *('LPT'+str(i) for i in range(1,10))
    }:
        titulo = 'Video ' + titulo
    titulo = titulo[:120].rstrip(' .')
    return titulo + extension

def miniatura(caso,fotos,carpeta):
    """Miniatura estilo YouTube: fondo llamativo sin textos, titular enorme en Sans Serif,
    y subtítulo pequeño justo debajo, sin contenedores.
    """
    from PIL import Image,ImageOps,ImageDraw,ImageEnhance
    imagen=foto_portada(fotos)
    with Image.open(imagen) as foto:
        base=ImageOps.fit(foto.convert('RGB'),(1280,720),method=Image.Resampling.LANCZOS,centering=(0.64,0.5))
    base=ImageEnhance.Contrast(base).enhance(1.34)
    base=ImageEnhance.Color(base).enhance(1.18)
    base=ImageEnhance.Sharpness(base).enhance(1.16)
    sombra=Image.new('RGBA',base.size,(0,0,0,0))
    d=ImageDraw.Draw(sombra)
    for x in range(980):
        a=int(248*max(0,1-x/980)**0.68)
        d.line((x,0,x,720),fill=(2,8,18,a))
    im=Image.alpha_composite(base.convert('RGBA'),sombra)
    draw=ImageDraw.Draw(im)
    titulo_txt=gancho_miniatura(caso)
    subtitulo_txt=subtitulo_miniatura(caso,titulo_txt)
    # Medir y ajustar el titular COMPLETO. No se elimina ninguna palabra.
    # Se permiten hasta tres líneas para los títulos más extensos.
    palabras=titulo_txt.split()
    def particiones(words, numero):
        from itertools import combinations
        for cortes in combinations(range(1,len(words)),numero-1):
            posiciones=(0,)+cortes+(len(words),)
            yield tuple(' '.join(words[posiciones[i]:posiciones[i+1]]) for i in range(numero))
    propuestas=[]
    for numero in (1,2,3):
        if numero<=len(palabras):
            propuestas.extend(particiones(palabras,numero))
    max_width=910
    max_title_height=400
    best=None
    for n in range(176,69,-2):
        font=cargar_fuente(n,condensada=False)
        for lines in propuestas:
            widths=[draw.textbbox((0,0),line,font=font,stroke_width=8)[2] for line in lines]
            if max(widths)>max_width:continue
            step=int(n*1.08)
            if len(lines)*step>max_title_height:continue
            balance=min(widths)/max(widths)
            score=n*3+balance*22-len(lines)*12
            if best is None or score>best[0]:best=(score,n,lines)
        if best and best[1]>=n:break
    if best is None:
        raise RuntimeError('No se pudo ajustar el título completo de la miniatura: '+titulo_txt)
    _,n,lines=best
    font=cargar_fuente(n,condensada=False)
    step=int(n*1.08)
    block_h=step*len(lines)
    x=52
    # Reservar debajo un subtítulo independiente sin caja.
    y=max(70,min(270,(720-block_h-90)//2))
    for j,line in enumerate(lines):
        color='#FFFFFF' if j==0 else '#FFE14A'
        yy=y+j*step
        draw.text((x+6,yy+6),line,font=font,fill='#000000',stroke_width=12,stroke_fill='#000000')
        draw.text((x,yy),line,font=font,fill=color,stroke_width=7,stroke_fill='#09111E')
    sub_font=cargar_fuente(39,condensada=False)
    sub_y=y+block_h+8
    draw.text((x+3,sub_y+3),subtitulo_txt,font=sub_font,fill='#000000',stroke_width=7,stroke_fill='#000000')
    draw.text((x,sub_y),subtitulo_txt,font=sub_font,fill='#FFFFFF',stroke_width=3,stroke_fill='#09111E')
    destino=carpeta/nombre_archivo_video(caso,('_opcion_'+str(caso['_variante_miniatura']) if caso.get('_variante_miniatura') else '')+'.jpg')
    # YouTube thumbnails: 16:9, 1280x720 y máximo 2 MB (API).
    # El JPG anterior Full HD, quality=96, frecuentemente superaba 2 MB.
    from PIL import ImageOps
    portada = ImageOps.fit(im.convert('RGB'), (1280,720), method=Image.Resampling.LANCZOS)
    for calidad in (90, 84, 76, 68, 58):
        portada.save(destino, format='JPEG', quality=calidad, optimize=True, progressive=False)
        if destino.stat().st_size <= 1_850_000:
            break
    if destino.stat().st_size > 2_000_000:
        raise RuntimeError('La miniatura supera 2 MB incluso tras comprimirla.')
    print('Miniatura validada: 1280x720,', destino.stat().st_size, 'bytes', flush=True)
    (carpeta/'TEXTO_MINIATURA.txt').write_text(titulo_txt+'\nSUBTITULO: '+subtitulo_txt+'\nIMAGEN: '+str(imagen),encoding='utf-8')
    return destino

def obtener_icono_like(carpeta, session=None):
    """Siempre utiliza exactamente File:Facebook_Like_button.svg.
    Nunca lo sustituye por dibujos improvisados o emojis deformados.
    """
    import requests, cairosvg
    from PIL import Image
    png_path=carpeta/'facebook_like_button.png'
    if png_path.exists():return png_path
    ses=session or requests.Session()
    api='https://commons.wikimedia.org/w/api.php'
    params={'action':'query','format':'json','titles':'File:Facebook_Like_button.svg',
            'prop':'imageinfo','iiprop':'url'}
    try:
        resp=ses.get(api,params=params,timeout=30,headers={'User-Agent':'Aerofactum/2.2 (Wikimedia media fetch)'})
        resp.raise_for_status()
        paginas=resp.json()['query']['pages']
        informacion=next(iter(paginas.values()))['imageinfo'][0]
        origen=informacion['url']
        resp=ses.get(origen,timeout=30,headers={'User-Agent':'Aerofactum/2.2 (Wikimedia media fetch)'})
        resp.raise_for_status()
        svg=resp.content
        if b'<svg' not in svg.lower():raise ValueError('El recurso descargado no es SVG.')
        (carpeta/'facebook_like_button.svg').write_bytes(svg)
        cairosvg.svg2png(bytestring=svg,write_to=str(png_path),output_width=640,output_height=640)
        with Image.open(png_path) as img:
            im=img.convert('RGBA')
            # Recortar márgenes transparentes del vector, conservando la forma EXACTA.
            bbox=im.getchannel('A').getbbox()
            if not bbox:raise ValueError('SVG sin contenido visible.')
            im.crop(bbox).save(png_path)
        return png_path
    except Exception as exc:
        raise RuntimeError('No se descargó el SVG auténtico desde Wikimedia Commons. '
                           'Se detiene el montaje para evitar un Like deformado. '
                           f'Página: {LIKE_PAGE_URL} | Error: {exc}') from exc

def crear_cta_base(carpeta):
    """CTA centrado y contenido EN el recuadro oscuro, nunca fuera de él."""
    from PIL import Image, ImageDraw
    tarjeta = Image.new('RGB', (ANCHO, ALTO), '#000000')
    d = ImageDraw.Draw(tarjeta)
    # El icono parpadeante está encima del panel; el texto completo va dentro.
    caja = (105, 710, ANCHO-105, ALTO-58)
    d.rounded_rectangle(caja, radius=40, fill=(15,22,34),
                        outline=(255,255,255), width=4)
    texto = 'Dale Like y Suscríbete!'
    x0,y0,x1,y1 = 145, 745, ANCHO-145, ALTO-92
    # Medir el texto realmente. Nunca truncarlo ni sobrepasar el panel.
    elegido = None
    for tam in range(128, 35, -2):
        fuente = cargar_fuente(tam)
        bbox = d.textbbox((0,0), texto, font=fuente, stroke_width=3)
        ancho,alto = bbox[2]-bbox[0], bbox[3]-bbox[1]
        if ancho <= x1-x0 and alto <= y1-y0:
            elegido = (fuente,bbox,ancho,alto)
            break
    if elegido is None:
        raise RuntimeError('CTA: no cabe el texto en su panel.')
    fuente,bbox,ancho,alto = elegido
    x = (ANCHO-ancho)//2-bbox[0]
    y = (y0+y1-alto)//2-bbox[1]
    d.text((x,y), texto, font=fuente, fill='#FFFFFF',
           stroke_width=3, stroke_fill='#0A1423')
    # Validación física del encuadre tipográfico.
    fin = d.textbbox((x,y), texto, font=fuente, stroke_width=3)
    if fin[0] < caja[0]+15 or fin[2] > caja[2]-15 or fin[1] < caja[1]+15 or fin[3] > caja[3]-15:
        raise RuntimeError('CTA: texto fuera del contenedor.')
    ruta = carpeta/'cta_bg.png'
    tarjeta.save(ruta)
    return ruta


def _foto_por_escena(caso, indice, fotos):
    if not fotos:raise RuntimeError('Montaje sin recursos visuales')
    mapa=caso.get('_mapa_visual',[])
    if indice<len(mapa):return Path(mapa[indice])
    if caso.get('_universal') and _univ_es_terror():return fotos[min(indice,len(fotos)-1)]
    return fotos[0]


def renderizar_clips(bloques,fotos,caso,carpeta):
    """Montaje con cambio de plano cada 8-12 s para evitar una foto estática
    durante párrafos completos. Todos los planos usan la línea de tiempo TTS.
    """
    from PIL import Image,ImageOps,ImageDraw,ImageFont
    clips=[];fps=FOTOGRAMAS_POR_SEGUNDO;acum_frames=0;numero=0
    like_png=obtener_icono_like(carpeta)
    cta_bg=crear_cta_base(carpeta)
    for i,b in enumerate(bloques):
        objetivo=round((b['inicio']+b['duracion'])*fps)
        frames_escena=max(1,objetivo-acum_frames)
        acum_frames+=frames_escena
        num_planos=1 if b['tipo']=='cta' else max(1,math.ceil(frames_escena/(fps*(7 if MODO_VIRAL else 11))))
        cortes=[round(j*frames_escena/num_planos) for j in range(num_planos+1)]
        for plano in range(num_planos):
            frames=cortes[plano+1]-cortes[plano]
            if frames<=0:continue
            if b['tipo']!='cta':
                # No usar siempre las mismas fotografías para dos planos consecutivos.
                if caso.get('_universal') and _univ_es_terror() and caso.get('_plan_visual'):
                    # Un párrafo -> su propia ilustración. Los planos varían el
                    # encuadre, nunca sustituyen el sujeto por otra escena.
                    foto=fotos[min(i,len(fotos)-1)]
                else:
                    foto=_foto_por_escena(caso,i,fotos)
            clip=carpeta/f'clip_{numero:04}.mp4'
            dur=frames/fps
            if b['tipo']=='cta':
                blink_on=0.61
                icon_h=int(ALTO*0.43)
                icon_w=icon_h
                x='(W-w)/2'
                y=str(int(ALTO*0.14))
                filtro=(f"[0:v]scale={ANCHO}:{ALTO},format=yuv420p[bg];" 
                        f"[1:v]scale={icon_w}:{icon_h}:flags=lanczos[like];"
                        f"[bg][like]overlay=x={x}:y={y}:enable='lt(mod(t,0.92),{blink_on})',format=yuv420p[v]")
                cmd=['ffmpeg','-y','-hide_banner','-loglevel','error',
                     '-loop','1','-framerate',str(fps),'-i',str(cta_bg),
                     '-loop','1','-framerate',str(fps),'-i',str(like_png),
                     '-filter_complex',filtro,'-map','[v]','-frames:v',str(frames),'-r',str(fps),'-an',
                     '-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p',str(clip)]
            else:
                # Ken Burns: encuadre flotante, panorámica alternada y zoom suave.
                z=f"min(1.0+on*{(.09/max(frames,1)):.9f},1.09)"
                x='(iw-iw/zoom)*0.18' if numero%2 else '(iw-iw/zoom)*0.82'
                y='(ih-ih/zoom)*0.30' if numero%3 else '(ih-ih/zoom)*0.70'
                vf=(f'scale=1500:850:force_original_aspect_ratio=increase,crop=1500:850,'
                    f"zoompan=z='{z}':x='{x}':y='{y}':d={frames}:s={ANCHO}x{ALTO}:fps={fps},"
                    'eq=contrast=1.08:saturation=0.90,format=yuv420p')
                cmd=['ffmpeg','-y','-hide_banner','-loglevel','error','-loop','1','-framerate','1','-i',str(foto),'-vf',vf,'-frames:v',str(frames),'-an','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p',str(clip)]
            ffmpeg(cmd)
            clips.append(clip);numero+=1
        print(f'  Escena {i+1:02}/{len(bloques)}: {frames_escena/fps:.1f}s / {num_planos} planos · {b["tipo"]}',flush=True)
    # El demuxer concat resuelve cada ruta respecto de clips.ffconcat.
    # str(c) era una ruta relativa al directorio de trabajo e introducía
    # dos veces 'output/AEROFACTUM/.../' al resolverla FFmpeg.
    concat=carpeta/'clips.ffconcat'
    if not clips:
        raise RuntimeError('No se generaron clips para concatenar.')
    lineas=['ffconcat version 1.0']
    for clip in clips:
        if not clip.is_file() or clip.stat().st_size == 0:
            raise FileNotFoundError(f'Clip inexistente o vacío: {clip}')
        # Solo el nombre del archivo, ya que todos los clips comparten carpeta.
        nombre=clip.name.replace("'", "'\\''")
        lineas.append(f"file '{nombre}'")
    concat.write_text('\n'.join(lineas)+'\n',encoding='utf-8')
    unido=carpeta/'video_sin_subtitulos.mp4'
    ffmpeg(['ffmpeg','-y','-hide_banner','-loglevel','error','-safe','0','-f','concat','-i',str(concat),'-c','copy',str(unido)])
    return unido

def finalizar_video(video,audio,ass,carpeta,caso):
    # Escalado FullHD en una sola codificación final; burn-in ASS sobre 1920x1080.
    salida=carpeta/nombre_archivo_video(caso,'.mp4');dur=tiempo_medio_audio(audio)
    ruta_ass=str(ass.resolve()).replace('\\','/').replace(':','\\:').replace("'","\\'")
    filtro=f'scale=1920:1080:flags=lanczos,tpad=stop_mode=clone:stop_duration=0.4,ass=filename=\'{ruta_ass}\''
    ffmpeg(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(video),'-i',str(audio),'-filter_complex',f'[0:v]{filtro}[v]','-map','[v]','-map','1:a:0','-t',f'{dur:.6f}','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart',str(salida)])
    meta=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','json',str(salida)]))
    real=float(meta['format']['duration'])
    if abs(real-dur)>.45:raise RuntimeError(f'Duración inconsistente: {real:.2f}s video / {dur:.2f}s voz')
    return salida

# ===================== PUBLICACIÓN AUTOMÁTICA YOUTUBE =====================
# OAUTH: usar Secrets YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN.
# ¡Nunca introducir estas credenciales en el repositorio!
YOUTUBE_CANAL = '@aerofactum'
YOUTUBE_PRIVACY = os.getenv('YOUTUBE_PRIVACY', 'private').lower().strip()
PUBLICAR_EN_YOUTUBE = os.getenv('PUBLICAR_EN_YOUTUBE', 'false').lower() == 'true'
PERMITIR_PUBLICACION_SIN_REVISION = os.getenv('ALLOW_UNREVIEWED_PUBLICATION', 'false').lower() == 'true'
YOUTUBE_SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']


def iniciar_oauth_local():
    """Única vez, desde un equipo con navegador: python aerofactum.py --auth-init
    Google OAuth Desktop: descargar client_secret.json y guardarlo FUERA del repositorio.
    """
    from google_auth_oauthlib.flow import InstalledAppFlow
    fichero = Path(os.getenv('YOUTUBE_OAUTH_CLIENT_FILE', 'client_secret.json'))
    if not fichero.is_file():
        raise FileNotFoundError('Falta client_secret.json (OAuth Desktop) para la autorización inicial.')
    flow = InstalledAppFlow.from_client_secrets_file(str(fichero), YOUTUBE_SCOPES)
    credenciales = flow.run_local_server(port=0, access_type='offline', prompt='consent')
    if not credenciales.refresh_token:
        raise RuntimeError('Google no entregó refresh_token. Reintenta el consentimiento de OAuth.')
    print('Autorización conseguida. Copia los valores siguientes a GitHub Secrets; no los compartas:')
    print('YT_CLIENT_ID =', credenciales.client_id)
    print('YT_CLIENT_SECRET =', credenciales.client_secret)
    print('YT_REFRESH_TOKEN =', credenciales.refresh_token)
    print('IMPORTANTE: configura la pantalla de consentimiento de OAuth en producción si procede.')


def youtube_servicio():
    """Refresca OAuth sin interfaz gráfica (apto para GitHub Actions)."""
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    valores = {n:os.getenv(n,'').strip() for n in ('YT_CLIENT_ID','YT_CLIENT_SECRET','YT_REFRESH_TOKEN')}
    faltantes = [n for n,v in valores.items() if not v]
    if faltantes:
        raise RuntimeError('Faltan los secretos de GitHub: '+', '.join(faltantes))
    creds = Credentials(token=None, refresh_token=valores['YT_REFRESH_TOKEN'],
        token_uri='https://oauth2.googleapis.com/token',
        client_id=valores['YT_CLIENT_ID'],client_secret=valores['YT_CLIENT_SECRET'],
        scopes=YOUTUBE_SCOPES)
    creds.refresh(Request())
    return build('youtube','v3',credentials=creds,cache_discovery=False)


def validar_canal_youtube(servicio):
    """Nunca publicar por accidente en otro canal de la cuenta Google."""
    mis_canales = servicio.channels().list(part='id,snippet',mine=True).execute().get('items',[])
    objetivo = servicio.channels().list(part='id,snippet',forHandle=YOUTUBE_CANAL).execute().get('items',[])
    if len(objetivo)!=1:
        raise RuntimeError('No se pudo encontrar el canal '+YOUTUBE_CANAL+' por su identificador. Revisa que exista.')
    correcto=objetivo[0]['id']
    if correcto not in {i['id'] for i in mis_canales}:
        raise RuntimeError('El token OAuth NO está vinculado al canal '+YOUTUBE_CANAL+'. No se publicará en otro canal.')
    print('Canal OAuth verificado:',objetivo[0]['snippet'].get('title'),correcto)
    return correcto


def subir_reanudable(solicitud, descripcion):
    """Reintentos acotados para errores transitorios durante una carga reanudable."""
    import random as _random
    from googleapiclient.errors import HttpError
    from httplib2 import HttpLib2Error
    respuesta=None
    fallos=0
    while respuesta is None:
        try:
            estado,respuesta=solicitud.next_chunk()
            if estado is not None:
                print(f'  {descripcion}: {int(estado.progress()*100)}%',flush=True)
            fallos=0
        except (HttpError, HttpLib2Error, OSError) as exc:
            codigo=getattr(getattr(exc,'resp',None),'status',None)
            if isinstance(exc,HttpError) and codigo not in (429,500,502,503,504):
                raise
            fallos+=1
            if fallos>6:raise
            espera=min(60,2**fallos+_random.uniform(0,1))
            print(f'  {descripcion}: error temporal, reintento {fallos}/6 en {espera:.1f}s: {exc}',flush=True)
            time.sleep(espera)
    return respuesta


def _credito_recurso_visual_valido(c):
    """Las ilustraciones hechas localmente no requieren licencia de Commons.

    Recursos externos continúan exigiendo CC0 o dominio público. El marcador
    procedural por sí solo NO puede justificar la omisión de una atribución:
    debe estar acompañado por procedencia local coherente y sin URL externa.
    """
    if not isinstance(c, dict):
        return False
    if c.get('tipo_recurso') == 'ilustracion_procedural':
        return (not (c.get('pagina') or c.get('url_original') or c.get('licencia_url'))
                and c.get('licencia') == 'Arte procedural original creado para este video'
                and c.get('autor') == 'AEROFACTUM Universal (generación algorítmica local)'
                and c.get('consulta_origen') == 'generación local sin API'
                and str(c.get('archivo', '')).startswith('imagen_')
                and str(c.get('archivo', '')).endswith('.jpg'))
    return licencia_valida({'extmetadata': {
        'LicenseShortName': {'value': c.get('licencia', '')},
        'LicenseUrl': {'value': c.get('licencia_url', '')},
    }})


def descripcion_youtube(caso, fuentes, creditos):
    """Descripción pública neutra: sin marca antigua, series ni bibliografía.

    La trazabilidad de fuentes continúa en FUENTES_INVESTIGACION.json y
    metadatos internos. Nunca se omite una atribución externa obligatoria.
    """
    for c in creditos:
        if not _credito_recurso_visual_valido(c):
            raise RuntimeError(
                'Recurso visual sin procedencia local verificada ni licencia externa CC0/PD: '
                + str(c.get('titulo', c.get('archivo', '?')))
                + '. No se omitirá ninguna atribución obligatoria.'
            )
    hashtags = [w.capitalize() for w in _aero_norm(NICHO).split() if len(w)>2]
    hashtags += ['Historias','Misterio','Relatos','Narracion','Curiosidades',
                 'Videos','Descubre','Aprende','Contenido','Cultura'] if _univ_es_terror() else [
                 'Divulgacion','Aprender','Conocimiento','Documental','Curiosidades',
                 'Cultura','Videos','Informacion','Explorar','Educacion']
    hashtags=list(dict.fromkeys(re.sub(r'[^a-zA-Z0-9ÁÉÍÓÚáéíóúÑñ]', '',h)
                                for h in hashtags if h))
    titulo_publico=str(caso.get('titulo','')).strip()
    parrafos=[titulo_publico, '',
             ('Una historia para dejarse llevar por el misterio.' if _univ_es_terror()
              else 'Una mirada al tema desde una perspectiva clara y entretenida.')]
    if MODO_VIRAL and PREGUNTA_FINAL_ESPECIFICA:
        parrafos.extend(['',_viral_pregunta_contextual(caso)])
    parrafos.extend(['',' '.join('#'+h for h in hashtags)])
    texto='\n'.join(parrafos)
    if len(texto)>4900:raise RuntimeError('Descripción supera 4900 caracteres.')
    return texto


def escribir_registro_publicacion(historial,episodio,caso,video_id,carpeta,estado):
    datos=leer_historial(historial)
    existente=next((r for r in datos if r.get('episodio')==episodio['id']),None)
    if existente is None:
        existente={'episodio':episodio['id'],'caso':episodio['caso_id'],
                   'titulo':episodio['titulo'],'fecha_utc':datetime.now(timezone.utc).isoformat()}
        datos.append(existente)
    existente.update(youtube_id=video_id, youtube_url='https://www.youtube.com/watch?v='+video_id,
                     youtube_estado=estado, salida=str(carpeta/nombre_archivo_video(caso,'.mp4')))
    historial.parent.mkdir(parents=True,exist_ok=True)
    temp=historial.with_suffix('.tmp')
    temp.write_text(json.dumps(datos,ensure_ascii=False,indent=2),encoding='utf-8')
    temp.replace(historial)
    (carpeta/'PUBLICACION_YOUTUBE.json').write_text(json.dumps(existente,ensure_ascii=False,indent=2),encoding='utf-8')
    return existente


def subir_miniatura_con_reintentos(servicio, video_id, miniatura, carpeta):
    """Reintenta errores transitorios, comunica causas permanentes y valida JPG.

    Nunca convierte un rechazo de miniatura en falso éxito.
    """
    from googleapiclient.http import MediaFileUpload
    from googleapiclient.errors import HttpError
    from PIL import Image
    ruta = Path(miniatura)
    if not ruta.is_file():
        raise FileNotFoundError(f'No existe la miniatura: {ruta}')
    with Image.open(ruta) as im:
        im.verify()
    with Image.open(ruta) as im:
        if im.format != 'JPEG' or im.size != (1280, 720):
            raise ValueError(f'Miniatura inválida: {im.format}, {im.size}. Se requiere JPG 1280x720.')
    if ruta.stat().st_size > 2_000_000:
        raise ValueError('La miniatura supera el límite de 2 MB de YouTube.')
    ultimo_error = None
    for intento in range(1, 7):
        try:
            servicio.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(str(ruta),mimetype='image/jpeg',resumable=False)
            ).execute(num_retries=2)
            (carpeta/'MINIATURA_YOUTUBE.json').write_text(
                json.dumps({'video_id':video_id,'estado':'correcto',
                            'archivo':ruta.name,'bytes':ruta.stat().st_size},ensure_ascii=False,indent=2),
                encoding='utf-8')
            print('Miniatura personalizada confirmada en YouTube.',flush=True)
            return
        except Exception as exc:
            ultimo_error = exc
            codigo = getattr(getattr(exc,'resp',None),'status',None)
            try: cuerpo = exc.content.decode('utf-8','replace')[:800]
            except Exception: cuerpo = str(exc)[:800]
            print(f'  Miniatura intento {intento}/6: HTTP {codigo}: {cuerpo}',flush=True)
            permanente = codigo in (401,403) or (codigo == 400 and
                not any(t in cuerpo.lower() for t in ('processing','not ready','not found','try again')))
            if permanente or intento == 6:
                break
            time.sleep(min(35,3*intento**1.5))
    mensaje = str(ultimo_error)
    if getattr(getattr(ultimo_error,'resp',None),'status',None)==403:
        mensaje += (' | Comprueba la verificación/eligibilidad de miniaturas '
                    'personalizadas del canal y la autorización OAuth de YouTube.')
    (carpeta/'MINIATURA_YOUTUBE.json').write_text(
        json.dumps({'video_id':video_id,'estado':'fallo','detalle':mensaje[:1200]},
                   ensure_ascii=False,indent=2), encoding='utf-8')
    raise RuntimeError('La miniatura NO se publicó: '+mensaje[:700])


def _aero_indicador_positivo(valor):
    return str(valor).strip().casefold() in ('1', 'true', 'yes', 'si', 'sí', 'on')


def _aero_declaracion_ia_youtube(caso, creditos):
    """Decisión verificable para YouTube `status.containsSyntheticMedia`.

    No debe marcarse "No" de forma indiscriminada: si hay material visual
    fotorealista generado, una persona real suplantada o hechos reales alterados,
    la respuesta es "Sí". Las ilustraciones procedurales del motor de terror
    están expresamente identificadas como NO fotográficas y no muestran personas
    reales simuladas. Música de fondo y voz TTS genérica no se convierten en
    supuestas imitaciones de personas reales.
    """
    motivos = []
    indicadores = (
        ('AERO_AI_ESCENAS_REALISTAS', 'escenas sintéticas realistas'),
        ('AERO_AI_PERSONAS_REALES', 'personas reales representadas de forma artificial'),
        ('AERO_AI_EVENTOS_REALES', 'eventos o lugares reales alterados'),
        ('AERO_AI_MUSICA_PRINCIPAL', 'música generada como contenido principal'),
    )
    for env, motivo in indicadores:
        if _aero_indicador_positivo(os.getenv(env, 'false')):
            motivos.append(motivo)
    for recurso in creditos or []:
        if not isinstance(recurso, dict):
            # Metadatos no interpretables: abstenerse de declarar "No".
            motivos.append('procedencia visual sin identificar')
            continue
        tipo = str(recurso.get('tipo_recurso', '')).strip().casefold()
        if tipo == 'ilustracion_procedural':
            # Sólo el arte estilizado que crea esta versión del programa.
            if recurso.get('url_original') or 'generación local' not in str(recurso.get('consulta_origen', '')).casefold():
                motivos.append('ilustración procedimental de origen no verificable')
            continue
        if tipo in ('escena_fotorealista_ia', 'video_sintetico_realista', 'deepfake', 'recreacion_realista'):
            motivos.append('recreación sintética realista identificada')
            continue
        if not recurso.get('url_original') and not recurso.get('pagina'):
            motivos.append('recurso visual sin procedencia verificable')
    requiere_declaracion = bool(motivos)
    return requiere_declaracion, list(dict.fromkeys(motivos))


def publicar_youtube(video,miniatura,srt,caso,episodio,fuentes,creditos,carpeta,historial,canal_esperado=None):
    from googleapiclient.http import MediaFileUpload
    if YOUTUBE_PRIVACY not in ('private','unlisted','public'):
        raise ValueError('YOUTUBE_PRIVACY debe ser private, unlisted o public.')
    if YOUTUBE_PRIVACY!='private' and not PERMITIR_PUBLICACION_SIN_REVISION:
        raise RuntimeError('No se permitirá difusión pública/no listada de contenido sin revisión: activa ALLOW_UNREVIEWED_PUBLICATION=true tras revisar el sistema.')
    # Verificar créditos y longitud antes de iniciar la subida.
    descripcion_validada=descripcion_youtube(caso,fuentes,creditos)
    servicio=youtube_servicio()
    canal=validar_canal_youtube(servicio)
    if canal_esperado and canal!=canal_esperado:raise RuntimeError('Canal de la cola distinto del canal OAuth; no publicar.')
    titulo=caso['titulo'][:100]
    ia_requiere_si, ia_motivos = _aero_declaracion_ia_youtube(caso,creditos)
    (Path(carpeta)/'DECLARACION_IA_YOUTUBE.json').write_text(json.dumps({
        'ai_use': 'Yes' if ia_requiere_si else 'No',
        'status.containsSyntheticMedia': ia_requiere_si,
        'motivos': ia_motivos,
        'criterio': 'YouTube: declarar contenido sintético o alterado que parezca real'
    },ensure_ascii=False,indent=2),encoding='utf-8')
    print('YouTube AI use:', 'Yes' if ia_requiere_si else 'No', '|', ', '.join(ia_motivos) or 'sin indicios de contenido sintético realista',flush=True)
    cuerpo={'snippet':{'title':titulo,
         'description':descripcion_validada,
         'categoryId':('28' if _nicho_aeronautico() else '27'),'defaultLanguage':'es',
         'tags':[NICHO[:35], caso['categoria'][:35], caso.get('_titulo_caso',caso['titulo'])[:35]]},
         'status':{'privacyStatus':YOUTUBE_PRIVACY,'selfDeclaredMadeForKids':False,
                   'containsSyntheticMedia':ia_requiere_si}}
    # Solo videos nuevos: una vez obtenido el ID, se guarda de inmediato para impedir duplicados.
    solicitud=servicio.videos().insert(part='snippet,status',body=cuerpo,
        media_body=MediaFileUpload(str(video),mimetype='video/mp4',chunksize=8*1024*1024,resumable=True))
    respuesta=subir_reanudable(solicitud,'Subida de vídeo')
    video_id=respuesta.get('id')
    if not video_id:raise RuntimeError('YouTube no devolvió un ID de video. Consultar el canal antes de reintentar la carga.')
    escribir_registro_publicacion(historial,episodio,caso,video_id,carpeta,'video_subido')
    print('YouTube: video registrado:',video_id,flush=True)
    errores=[]
    try:
        subir_miniatura_con_reintentos(servicio,video_id,miniatura,carpeta)
    except Exception as e:
        errores.append('miniatura: '+str(e)[:500])
        print('ERROR: video existente, pero falta miniatura:',e,flush=True)
    try:
        # SRT como pista propia; los subtítulos ya están incrustados en el MP4 salvo en CTA.
        servicio.captions().insert(part='snippet',body={'snippet':{
          'videoId':video_id,'language':'es','name':'Español','isDraft':False}},
          media_body=MediaFileUpload(str(srt),mimetype='application/octet-stream',resumable=True)).execute()
        print('Pista SRT en español subida correctamente.',flush=True)
    except Exception as e:
        errores.append('subtitulos: '+str(e)[:500])
        print('AVISO: falló SRT; el video ya existe:',e,flush=True)
    estado='completo' if not errores else 'pendiente: '+' | '.join(errores)
    escribir_registro_publicacion(historial,episodio,caso,video_id,carpeta,estado)
    if any(err.startswith('miniatura:') for err in errores):
        raise RuntimeError('El video ya se subió a YouTube (ID '+video_id+
                           '), pero la miniatura no se completó. NO vuelvas a subir '
                           'el video como uno nuevo; revisa MINIATURA_YOUTUBE.json '
                           'o carga la miniatura existente desde YouTube Studio. '+
                           ' | '.join(errores))
    return video_id


def _viral_consultar_historico_analytics():
    """Consulta bajo demanda de métricas reales. Requiere refresh token adicional
    autorizado explícitamente para yt-analytics.readonly; NO usa el scope de
    publicación del YML para fingir permisos. Nunca modifica el historial de videos.
    """
    import requests
    token=os.getenv('YT_ANALYTICS_REFRESH_TOKEN','').strip()
    if not token:
        raise RuntimeError('Para --analytics se requiere YT_ANALYTICS_REFRESH_TOKEN con alcance yt-analytics.readonly. El YML actual no lo incluye.')
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from datetime import timedelta
    creds=Credentials(token=None,refresh_token=token,
        token_uri='https://oauth2.googleapis.com/token',
        client_id=os.getenv('YT_CLIENT_ID',''),client_secret=os.getenv('YT_CLIENT_SECRET',''),
        scopes=['https://www.googleapis.com/auth/yt-analytics.readonly'])
    creds.refresh(Request())
    ruta=ruta_historial()
    historial=leer_historial(ruta)
    hoy=datetime.now(timezone.utc).date()
    hasta=(hoy-timedelta(days=2)).isoformat()
    salida=[]
    sesion=requests.Session()
    for row in historial[-80:]:
        video_id=row.get('youtube_id')
        if not video_id:continue
        try:
            fecha=datetime.fromisoformat(str(row.get('fecha_utc','')).replace('Z','+00:00')).date()
        except Exception:
            continue
        inicio=(fecha+timedelta(days=1)).isoformat()
        if inicio>hasta:continue
        params={'ids':'channel==MINE','startDate':inicio,'endDate':hasta,
                'metrics':'views,estimatedMinutesWatched,averageViewDuration,likes,comments,subscribersGained',
                'filters':'video=='+video_id}
        respuesta=sesion.get('https://youtubeanalytics.googleapis.com/v2/reports',params=params,
            headers={'Authorization':'Bearer '+creds.token},timeout=(10,35))
        if respuesta.status_code in (401,403):
            raise RuntimeError('Permiso Analytics insuficiente o acceso denegado: '+respuesta.text[:300])
        respuesta.raise_for_status()
        js=respuesta.json()
        heads=[h['name'] for h in js.get('columnHeaders',[])]
        data=dict(zip(heads,(js.get('rows') or [[]])[0])) if js.get('rows') else {}
        salida.append({'episodio':row.get('episodio'),'video_id':video_id,'titulo':row.get('titulo'),
                       'fecha_consulta_utc':datetime.now(timezone.utc).isoformat(),
                       'metricas':data,'fuente':'YouTube Analytics API v2',
                       'nota':'La disponibilidad de métricas depende de procesamiento y permisos del canal.'})
        time.sleep(.15)
    salida_ruta=OUTPUT_BASE/'ANALYTICS_HISTORICO_REAL.json'
    salida_ruta.parent.mkdir(parents=True,exist_ok=True)
    salida_ruta.write_text(json.dumps(salida,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Analytics: {len(salida)} videos consultados; {salida_ruta}',flush=True)
    return salida


def consultar_analytics_verificado(carpeta, youtube_id, credenciales=None):
    """Consulta real OPCIONAL. Requiere credenciales con youtube.readonly + yt-analytics.readonly.

    El OAuth del YML anterior normalmente NO incluye analytics.readonly: en ese
    caso se registra el error, sin simular impresiones, retención ni vistas.
    """
    if not ANALIZAR_YOUTUBE_ANALYTICS or not youtube_id:return None
    try:
        from googleapiclient.discovery import build
        if credenciales is None:
            raise RuntimeError('Faltan credenciales OAuth con permiso yt-analytics.readonly')
        servicio=build('youtubeAnalytics','v2',credentials=credenciales,cache_discovery=False)
        desde=(datetime.now(timezone.utc).date()).isoformat()
        # Un video recién publicado no tiene 7 días de métricas:
        # la consulta se ejecuta manualmente en días posteriores.
        respuesta=servicio.reports().query(ids='channel==MINE',startDate=desde,
            endDate=desde,metrics='views,estimatedMinutesWatched,averageViewDuration,likes,comments,subscribersGained',
            dimensions='video',filters='video=='+youtube_id).execute()
        (Path(carpeta)/'ANALYTICS_VERIFICADO.json').write_text(
            json.dumps(respuesta,ensure_ascii=False,indent=2),encoding='utf-8')
        return respuesta
    except Exception as exc:
        (Path(carpeta)/'ANALYTICS_ERROR.txt').write_text(
            'Analytics no consultado o sin permisos/datos: '+str(exc)[:550],encoding='utf-8')
        return None

# ====================== METADATOS Y PUBLICACIÓN ===================
def guardar_metadatos(caso,bloques,fuentes,creditos,carpeta):
    contenido='\n'.join(f"{i+1}. {b['texto']}" for i,b in enumerate(bloques))
    (carpeta/'GUION_COMPLETO.txt').write_text(contenido,encoding='utf-8')
    (carpeta/'TITULO_Y_DESCRIPCION.txt').write_text(
        descripcion_youtube(caso,fuentes,creditos), encoding='utf-8')
    (carpeta/'manifest.json').write_text(json.dumps(dict(titulo=caso['titulo'],categoria=caso['categoria'],
        estado=caso['estado'],fuentes=fuentes,creditos=creditos,bloques=bloques),ensure_ascii=False,indent=2),encoding='utf-8')


def guardar_drive(carpeta):
    if not SALIDA_EN_DRIVE:return
    try:
        from google.colab import drive
        drive.mount('/content/drive',force_remount=False)
        destino=Path('/content/drive/MyDrive/AEROFACTUM')/carpeta.name
        destino.mkdir(parents=True,exist_ok=True)
        for f in carpeta.iterdir():
            if f.is_file() and f.suffix.lower() in {'.mp4','.srt','.ass','.jpg','.txt','.json'} and not f.name.startswith(('clip_','imagen_','cta','video_sin_')):
                shutil.copy2(f,destino/f.name)
        print('Guardado en Drive:',destino)
    except Exception as e:print('No se pudo guardar en Drive:',str(e))

def producir_episodio(episodio,historial):
    import requests
    caso=CASOS[episodio['caso_id']].copy()
    caso['_titulo_caso']=caso['titulo']
    caso['titulo']=episodio['titulo']
    caso['_episodio']=episodio
    carpeta=OUTPUT_BASE/(episodio['id']+'_'+datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
    carpeta.mkdir(parents=True,exist_ok=True)
    print('\nAEROFACTUM · EPISODIO',episodio['id'],'\n',caso['titulo'])
    print('Estado de documentación:',caso['estado'])
    sesion=requests.Session()
    try:
        previo=_guion_cache_cargar(episodio,caso)
        if previo:
            documentos,plan=previo
            _cola_json(carpeta/'GUION_RECUPERADO.json',{'episodio':episodio['id'],'titulo':caso['titulo'],'plan':plan,'fuentes':documentos})
            _cola_json(carpeta/'FUENTES_INVESTIGACION.json',{'recuperado':True,'fuentes':documentos})
            print('  Guion aprobado recuperado: no se consume IA nuevamente.',flush=True)
        else:
            verificar_fuentes(caso,sesion,carpeta)
            print('Investigando documentos y noticias accesibles...')
            documentos=investigar_episodio(caso,carpeta,sesion)
            plan=generar_guion_investigado(caso,episodio,documentos,carpeta)
            _guion_cache_guardar(episodio,caso,documentos,plan,carpeta)
    except Exception as exc:
        # Solo fases anteriores a TTS y publicación admiten cambiar de tema.
        (carpeta/'ERROR_PREPRODUCCION.txt').write_text(
            f'{type(exc).__name__}: {exc}\n',encoding='utf-8')
        raise EpisodioRecuperable(str(exc)) from exc
    fuentes=[{'nombre':d['nombre'],'url':d['url'],'status':'documento_leido',
              'id':d['id']} for d in documentos]
    if AERO_IA_DRY_RUN:
        (carpeta/'GUION_PREVIO.txt').write_text('\n\n'.join(f'{tipo.upper()}: {txt}' for tipo,txt in plan),encoding='utf-8')
        print('PRUEBA GUION COMPLETADA, sin fotos, TTS ni publicación:',carpeta,flush=True)
        return carpeta/'GUION_PREVIO.txt'
    caso['_plan_visual']=plan
    print('Preparando imágenes coherentes con cada escena del guion...')
    try:
        fotos,creditos=buscar_fotos(caso,sesion,carpeta)
    except Exception as exc:
        (carpeta/'ERROR_FOTOGRAFIAS.txt').write_text(str(exc)+'\n',encoding='utf-8')
        raise EpisodioRecuperable('No hay suficientes fotografías descargables: '+str(exc)) from exc
    (carpeta/'RESUMEN_RECURSOS_VISUALES.txt').write_text(
        f'Recursos visuales: {len(fotos)}\nFotografías reales de Wikimedia: {sum(1 for c in creditos if c.get("url_original"))}\nIlustraciones procedurales originales: {sum(1 for c in creditos if c.get("tipo_recurso")=="ilustracion_procedural")}\nObjetivo editorial: {IMAGENES_MINIMAS}\n'
        + ('ADVERTENCIA: Revisar variedad visual y relevancia temática antes de publicar.\n' if len(fotos)<IMAGENES_MINIMAS else 'Cantidad objetivo alcanzada.\n'),
        encoding='utf-8')
    # Una sola foto puede servir como borrador privado para revisión.
    # Sin embargo, nunca publicar automáticamente un episodio visible
    # con menos fotografías pertinentes que el objetivo editorial.
    if (PUBLICAR_EN_YOUTUBE and YOUTUBE_PRIVACY in ('public','unlisted')
            and len(fotos) < IMAGENES_MINIMAS and not _es_financiero(caso)):
        aviso=(f'PUBLICACIÓN BLOQUEADA: {len(fotos)} recurso(s) visual(es) validado(s) '
               f'pertinente(s), mínimo editorial {IMAGENES_MINIMAS} para '
               f'YOUTUBE_PRIVACY={YOUTUBE_PRIVACY}. '
               'No se publicará un video visualmente repetitivo. '
               'Reintenta luego de recuperar Wikimedia Commons o ejecuta '
               'con privacidad private para revisar un borrador.')
        (carpeta/'AVISO_PUBLICACION_BLOQUEADA.txt').write_text(aviso+'\n',encoding='utf-8')
        print(aviso,flush=True)
        raise EpisodioRecuperable(aviso)
    caso['_creditos_visuales']=creditos
    _curiosity_asignar_escenas(caso,fotos,creditos,carpeta)
    if MODO_VIRAL:
        auditoria=_viral_guardar_paquete(caso,plan,carpeta,fotos)
        print('  Evaluación editorial:', 'sin alertas' if auditoria['aprobado'] else '; '.join(auditoria['advertencias']),flush=True)
    thumb=miniatura(caso,fotos,carpeta)
    alternativas_miniaturas=_viral_miniaturas(caso,fotos,carpeta) if MODO_VIRAL else []
    if alternativas_miniaturas:
        print('  Miniaturas candidatas locales:',len(alternativas_miniaturas),flush=True)
        paquete=carpeta/'PAQUETE_VIRAL.json'
        if paquete.exists():
            info=json.loads(paquete.read_text(encoding='utf-8'))
            info['miniaturas_candidatas']=[str(thumb)]+alternativas_miniaturas
            info['experimento_ab_youtube']='No iniciado: las variantes se guardan para revisión o prueba manual en YouTube Studio.'
            paquete.write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf-8')
    (carpeta/'episodio.json').write_text(json.dumps(episodio,ensure_ascii=False,indent=2),encoding='utf-8')
    if CREAR_VISTA_PREVIA:
        print('Vista previa:',thumb)
        guardar_drive(carpeta)
        return thumb
    print(f'Produciendo narración investigada... voz={VOZ} velocidad={VELOCIDAD}; subtítulos adelantados {SUBTITULOS_ADELANTO:.2f}s',flush=True)
    bloques,cues,voz=generar_voces(plan,carpeta)
    print('Duración narrada:',round(tiempo_medio_audio(voz)/60,2),'minutos')
    inicio_cta=next((b['inicio'] for b in bloques if b['tipo']=='cta'),None)
    srt,ass=subtitulos(cues,carpeta,inicio_cta=inicio_cta)
    audio=mezclar_cinematica(voz,carpeta)
    guardar_metadatos(caso,bloques,fuentes,creditos,carpeta)
    if MODO_VIRAL:
        _viral_analytics_instrucciones(carpeta)
    print('Montaje fotográfico con movimiento cinematográfico...')
    base=renderizar_clips(bloques,fotos,caso,carpeta)
    video=finalizar_video(base,audio,ass,carpeta,caso)
    if MODO_VIRAL and GENERAR_SHORT_DERIVADO:
        _viral_short_local(video,caso,carpeta)
    guardar_drive(carpeta)
    if PUBLICAR_EN_YOUTUBE:
        _cola_publicar(video,thumb,srt,caso,episodio,fuentes,creditos,carpeta,historial)
    else:
        anotar_historial(historial,dict(episodio=episodio['id'],caso=episodio['caso_id'],
            titulo=episodio['titulo'],fecha_utc=datetime.now(timezone.utc).isoformat(),salida=str(video)))
    print('\nFINALIZADO\nVideo:',video,'\nMiniatura:',thumb,'\nSubtítulos:',srt)
    return video

# ==================== AEROFACTUM UNIVERSAL 6.0 ====================
# Contrato de compatibilidad: mismo aerofactum.py, mismo YML, claves OAuth,
# carpetas de salida, estados y proveedores. La ÚNICA línea editorial es NICHO.
# El catálogo de 100 temas aeronáuticos permanece intacto si NICHO = "Aviación".
# Otros nichos se descubren en Wikipedia (catálogo dinámico; títulos NO son hechos).
# Una búsqueda fallida no genera títulos inventados ni material sin fuentes.

def _nicho_es_aviacion():
    import unicodedata
    valor=''.join(c for c in unicodedata.normalize('NFKD',NICHO.casefold())
                  if not unicodedata.combining(c)).strip()
    return valor in ('aviacion','aeronautica','aviation')

def _nicho_es_industria_aeronautica():
    n = _univ_normalizar(NICHO)
    return n in {
        'datos de la industria aeronautica', 'industria aeronautica',
        'datos de la industria de la aviacion', 'industria de la aviacion',
        'industria de aviacion', 'industria aerea', 'datos de la industria aerea',
        'aviation industry', 'aerospace aviation industry',
    }


def _nicho_aeronautico():
    return _nicho_es_aviacion() or _nicho_es_industria_aeronautica() or _motor_nicho(NICHO)


def _catalogo_industria_aeronautica(casos, catalogo):
    """Use the already curated aviation cases, without Wikipedia search noise.

    Original IDs, sources and technical anchors remain unchanged. This also
    avoids re-publishing an original episode under a newly created niche ID.
    """
    prefijos = ('fin_', 'atc_', 'mnt_', 'future_', 'motor_', 'ops_')
    elegidos = [k for k in catalogo if k.startswith(prefijos) and k in casos]
    return ({k: dict(casos[k]) for k in elegidos},
            {k: dict(catalogo[k]) for k in elegidos})


def _univ_normalizar(valor):
    import unicodedata
    s=''.join(c for c in unicodedata.normalize('NFKD',str(valor).casefold())
              if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]+',' ',s).strip()

def _univ_slug(valor):
    import unicodedata
    s=''.join(c for c in unicodedata.normalize('NFKD',str(valor).casefold())
              if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]+','-',s).strip('-')[:55] or 'general'

def _univ_tokens(texto):
    stop={'para','como','cual','cuales','sobre','entre','desde','hacia','todo',
          'historia','concepto','mundo','general','informacion','porque','partir',
          'where','which','through','about','their','with','from','that','this',
          'article','categoria','temas','cientifico','ciencia','tipos','sistema',
          'teoria','funcionamiento','principales','diferentes'}
    return {w for w in _univ_normalizar(texto).split() if len(w)>=4 and w not in stop}

def _univ_es_terror():
    n=_univ_normalizar(NICHO)
    return 'terror' in n and any(w in n for w in ('historias','relatos','cuentos','leyendas'))

def _univ_consultas_temas():
    if _motor_nicho(NICHO):
        return ['motor aeronáutico','turbofán motor','turborreactor motor','turbohélice avión', 'motor radial avión','motor de pistón aeronáutico','motor aeronáutico compresor','motor aeronáutico turbina','motor aeronáutico propulsión']
    if _univ_es_terror():
        return ['cuento de fantasmas','relato de terror','leyenda urbana',
                'leyenda de fantasmas','literatura de terror','casa encantada']
    return [NICHO, NICHO+' tipos', NICHO+' fenómenos',
            NICHO+' descubrimientos', NICHO+' tecnología', NICHO+' investigación']

def _univ_tema_terror_pertinente(titulo,resumen):
    # Excluye artículos ajenos a relatos de terror.
    t=_univ_normalizar(titulo+' '+resumen)
    excluidos=('videojuego','video game','banda musical','album musical',
               'grupo musical','terrorismo','terrorista','partido politico',
               'competicion deportiva','pelicula pornografica')
    if any(x in t for x in excluidos):return False
    conceptos=('fantasma','espectro','aparicion','embruj','encantad',
               'terror','horror','miedo','leyenda','misterio','sobrenatural',
               'cuento','relato','folclor','folklor','creepypasta','mitologia',
               'espiritu','monstruo','bruj','demonio','gotic')
    return any(x in t for x in conceptos)

def _univ_descubrir_catalogo(session=None):
    """Usa índice público Wikipedia; IDs basados en páginas, estables por nicho.

    Los títulos recuperados son candidatos y no pruebas; cada episodio debe
    descargar y validar documentación por separado antes de narrar.
    """
    import requests
    from urllib.parse import quote
    ses=session or requests.Session()
    ses.headers.update({'User-Agent':'AEROFACTUM-Universal/6.1 (https://acesped.github.io/aerofactum/; educational video research)'})
    api='https://es.wikipedia.org/w/api.php'
    nicho_id=_univ_slug(NICHO)
    vistos=set();entradas=[];errores=[]
    for consulta in _univ_consultas_temas():
        try:
            r=ses.get(api,params={'action':'query','list':'search','srsearch':consulta,
                'srnamespace':0,'srlimit':35,'format':'json','formatversion':2},
                timeout=(8,24))
            if r.status_code==429:
                print('  Wikipedia limitó el catálogo (HTTP 429).',flush=True)
                break
            r.raise_for_status()
            items=r.json().get('query',{}).get('search',[])
        except Exception as e:
            errores.append(str(e)[:150]);continue
        for it in items:
            titulo=re.sub(r'\s+',' ',html.unescape(it.get('title',''))).strip()
            if not titulo or ':' in titulo or len(titulo)<5 or len(titulo)>90:continue
            if re.search(r'\b(desambiguaci[oó]n|anexo|lista de|categor[ií]a:)\b',titulo,re.I):continue
            identificador=it.get('pageid')
            if not isinstance(identificador,int) or identificador<=0:continue
            if identificador in vistos:continue
            vistos.add(identificador)
            resumen=re.sub('<[^>]+>',' ',it.get('snippet',''))
            resumen=re.sub(r'\s+',' ',html.unescape(resumen)).strip()
            # La consulta puede devolver artículos vagamente relacionados; se
            # requiere coincidencia con el nicho en la sinopsis o el título.
            relacionados=_univ_tokens(NICHO)
            corpus=_univ_normalizar(titulo+' '+resumen)
            if _univ_es_terror():
                if not _univ_tema_terror_pertinente(titulo,resumen):continue
            elif not _curiosity_tema_pertinente(titulo,resumen):
                continue
            from urllib.parse import quote as _quote
            url='https://es.wikipedia.org/wiki/'+_quote(titulo.replace(' ','_'),safe='()_,-')
            uid=nicho_id+'-'+str(identificador)
            entradas.append({'id':uid,'titulo':titulo,'resumen':resumen,'url':url,'pageid':identificador})
            if len(entradas)>=125:break
        if len(entradas)>=125:break
    if not entradas:
        raise RuntimeError('No fue posible obtener artículos del nicho '+repr(NICHO)+
                           '. Wikipedia puede estar inaccesible o no tiene resultados; '+str(errores[:2]))
    # La raíz aparece primero y se conservan IDs estables para la deduplicación.
    casos={};catalogo={}
    for it in entradas:
        titulo=it['titulo'];uid=it['id']
        consulta_foto=[titulo+' photograph',titulo+' fotografía',
                        titulo+' image',NICHO+' '+titulo+' photo',titulo]
        caso={'id':uid,'titulo':titulo,'categoria':NICHO,
              'estado':'DIVULGACIÓN · DOCUMENTACIÓN POR CONTRASTAR',
              'pregunta':'¿Cómo se explica '+titulo+'?',
              'gancho':'Investigamos un aspecto de '+NICHO+': '+titulo,
              'contexto':it['resumen'] or titulo,
              'pistas':[titulo], 'hechos':[],
              'giro':'', 'importancia':'',
              'cierre':'Una nueva mirada documentada sobre '+NICHO+'.',
              'fuentes':[('Wikipedia en español: '+titulo,it['url'],[titulo])],
              'imagenes':consulta_foto,'mini_titulo':titulo.upper(),
              'mini_subtitulo':NICHO.upper()[:40],
              '_universal':True,'_wiki_pageid':it['pageid']}
        casos[uid]=caso
        catalogo[uid]={'id':uid,'caso_id':uid,'modo':'conocimiento',
                       'titulo':titulo,'pregunta':caso['pregunta'],
                       'hecho_clave':caso['contexto']}
    return casos,catalogo

# Guardar implementaciones aeronáuticas para compatibilidad.
_UNIV_INVESTIGAR_ORIGINAL = investigar_episodio
_UNIV_RELEVANCIA_ORIGINAL = _aero_documento_relevante
_UNIV_ANCLAS_ORIGINAL = _aero_anclas_especificas
_UNIV_CONSULTAS_FOTOS_ORIGINAL = _consultas_fotos
_UNIV_FOTO_RELEVANCIA_ORIGINAL = evaluar_relevancia_foto
_UNIV_CONSULTAS_ORIGINAL = _aero_consultas
_UNIV_EJECUTAR_ORIGINAL = None  # se asigna después de definir ejecutar

def _aero_anclas_especificas(caso):
    if not caso.get('_universal'):return _UNIV_ANCLAS_ORIGINAL(caso)
    # Anclas específicas: el título de artículo, nunca solo "ciencia" o NICHO.
    palabras=_univ_tokens(caso.get('_titulo_caso',caso['titulo']))
    return tuple(sorted(palabras,key=len,reverse=True))

def _aero_documento_relevante(texto,caso):
    if not caso.get('_universal'):return _UNIV_RELEVANCIA_ORIGINAL(texto,caso)
    t=_univ_normalizar(texto)
    if len(t)<180:return 0
    if _motor_nicho(NICHO) and not _motor_evidencia(t):return 0
    anclas=_aero_anclas_especificas(caso)
    if not anclas:return 0
    aciertos=sum(bool(re.search(r'(?<![a-z0-9])'+re.escape(w)+r'(?![a-z0-9])',t)) for w in anclas)
    # El artículo del asunto debe tratar del concepto central, no solo del nicho.
    return (3*aciertos) if aciertos>=1 else 0

def _aero_consultas(caso):
    if not caso.get('_universal'):return _UNIV_CONSULTAS_ORIGINAL(caso)
    titulo=caso.get('_titulo_caso',caso['titulo'])
    return [titulo+' '+NICHO, titulo+' investigación',
            '"'+titulo+'" site:edu', '"'+titulo+'" site:gov',
            '"'+titulo+'" documentación técnica']

def _consultas_fotos(caso):
    if not caso.get('_universal'):
        base=_UNIV_CONSULTAS_FOTOS_ORIGINAL(caso)
        contextual=_consultas_visuales_83(caso)
        return list(dict.fromkeys(contextual+base))
    titulo=caso.get('_titulo_caso',caso['titulo'])
    return _curiosity_consultas_fotos(caso,titulo)

def evaluar_relevancia_foto(caso,titulo,metadata,busqueda):
    if not caso.get('_universal'):
        if _es_financiero(caso):
            return _foto_financiera_83(caso,titulo,metadata)
        return _UNIV_FOTO_RELEVANCIA_ORIGINAL(caso,titulo,metadata,busqueda)
    # Sin exigencia de aeronaves: evaluar el tema concreto a partir de archivo
    # y metadatos. Si no aparece el sujeto, descartar antes de descargar.
    nombre=_normalizar_texto_foto(titulo.replace('File:',''))
    detalle=_normalizar_texto_foto(' '.join(limpiar_html(metadata.get(k,{}).get('value',''))
        for k in ('ImageDescription','ObjectName','Categories')))
    anclas=_univ_tokens(caso.get('_titulo_caso',caso['titulo']))
    if not anclas:return (0,[])
    hits_nombre={w for w in anclas if re.search(r'\b'+re.escape(w)+r'\b',nombre)}
    hits_meta={w for w in anclas if re.search(r'\b'+re.escape(w)+r'\b',detalle)}
    if _motor_nicho(NICHO):
        anclas=_curiosity_tokens_visuales(caso.get('_titulo_caso',caso['titulo']))
        hits_nombre=anclas & _curiosity_tokens_visuales(nombre)
        hits_meta=anclas & _curiosity_tokens_visuales(detalle)
        centrales=anclas-{'engine','aircraft','aviation','motor','motores','aeronautico','aeronauticos','aeronave','avion'}
        if centrales and not (centrales & (hits_nombre | hits_meta)):return (0,[])
        objeto=' '.join(limpiar_html(metadata.get(k,{}).get('value','')) for k in ('ImageDescription','ObjectName'))
        if not _motor_foto(nombre,objeto):return (0,[])
        # Topic must appear in filename or actual object description, not category only.
        if not hits_nombre and not (anclas & _curiosity_tokens_visuales(objeto)):return (0,[])
    elif not hits_nombre:return (0,[])
    hits=hits_nombre|hits_meta
    puntos=8*len(hits_nombre)+2*len(hits_meta)
    return (max(8,puntos),sorted(hits)) if hits else (0,[])

def _univ_recuperar_wikipedia(caso,session):
    """Extrae texto visible de la API oficial Wikimedia sin inventar fuentes.

    URL de Wikipedia identifica la página. Si la API falla, el documento
    puede intentarse por HTML en el motor de investigación original.
    """
    pageid=caso.get('_wiki_pageid')
    if not pageid:return None
    try:
        r=session.get('https://es.wikipedia.org/w/api.php',params={
            'action':'query','prop':'extracts','explaintext':'1',
            'exsectionformat':'plain','pageids':str(pageid),
            'format':'json','formatversion':2},timeout=(8,25),
            headers={'User-Agent':'AEROFACTUM-Universal/6.1 (educational documentary)'})
        r.raise_for_status()
        pages=r.json().get('query',{}).get('pages',[])
        if not pages or pages[0].get('missing'):return None
        texto=re.sub(r'\s+',' ',pages[0].get('extract','')).strip()
        if len(texto)<550:return None
        fragmento=_aero_fragmentos(texto,caso)
        score=_aero_documento_relevante(fragmento,caso)
        if len(fragmento)<450 or not score:return None
        url=caso['fuentes'][0][1]
        return {'id':'F1','nombre':'Wikipedia: '+caso['titulo'],'url':url,
                'fecha_consulta':datetime.now(timezone.utc).isoformat(),
                'texto':fragmento[:16500],'coincidencias_tema':score,'cache':False}
    except Exception as e:
        print('  Fuente Wikipedia API no accesible:',type(e).__name__,str(e)[:120],flush=True)
        return None

def investigar_episodio(caso,carpeta,session):
    if not caso.get('_universal'):
        return _UNIV_INVESTIGAR_ORIGINAL(caso,carpeta,session)
    # Para nichos nuevos, no consultar fuentes FAA por defecto: wikipedia,
    # URLs opcionales del usuario y búsqueda filtrada primero.
    carpeta=Path(carpeta);carpeta.mkdir(parents=True,exist_ok=True)
    documentos=[];rechazadas=[]
    inicial=_univ_recuperar_wikipedia(caso,session)
    if inicial:documentos.append(inicial)
    # Las fuentes del catálogo universal se representan como
    # (nombre, url, palabras_clave). No desempaquetar suponiendo dos campos.
    # Además, ignorar entradas incompletas y registrar fuentes independientes.
    for entrada in caso.get('fuentes',[]):
        if len(documentos)>=max(1,AERO_MIN_FUENTES):break
        if not isinstance(entrada,(tuple,list)) or len(entrada)<2:continue
        nombre,url=entrada[:2]
        if not isinstance(url,str) or not url.startswith(('https://','http://')):continue
        if any(d['url']==url for d in documentos):continue
        doc=_aero_descargar_documento(session,url,caso,nombre)
        if doc and doc['url'] not in {d['url'] for d in documentos}:
            doc['id']='F'+str(len(documentos)+1)
            documentos.append(doc)
    # El usuario puede aportar fuentes específicas con AERO_IA_URLS (YML existente).
    for url in AERO_IA_URLS.split('|'):
        if len(documentos)>=max(AERO_MAX_DOCUMENTOS,AERO_MIN_FUENTES):break
        if not url.strip():continue
        doc=_aero_descargar_documento(session,url.strip(),caso,'Fuente adicional')
        if doc and doc['url'] not in {x['url'] for x in documentos}:
            doc['id']='F'+str(len(documentos)+1);documentos.append(doc)
    if len(documentos)<AERO_MIN_FUENTES:
        for url,nombre in _aero_busqueda_rss_filtrada(session,caso):
            if len(documentos)>=AERO_MIN_FUENTES:break
            doc=_aero_descargar_documento(session,url,caso,nombre)
            if doc and doc['url'] not in {x['url'] for x in documentos}:
                doc['id']='F'+str(len(documentos)+1);documentos.append(doc)
    reporte={'nicho':NICHO,'tema':caso['titulo'],'id':caso['id'],
             'fecha_utc':datetime.now(timezone.utc).isoformat(),
             'fuentes':[{'id':d['id'],'url':d['url'],'nombre':d['nombre'],
                         'extracto':d['texto'][:750]} for d in documentos],
             'descartes':rechazadas,'fuentes_minimas':AERO_MIN_FUENTES}
    (carpeta/'FUENTES_INVESTIGACION.json').write_text(
         json.dumps(reporte,ensure_ascii=False,indent=2),encoding='utf-8')
    if len(documentos)<AERO_MIN_FUENTES:
        raise EpisodioRecuperable(f'No se encontraron {AERO_MIN_FUENTES} fuentes legibles sobre {caso["titulo"]}; no se fabrica un guion.')
    return documentos

# El prompt y el título de YouTube son contextuales; no alterar la validación
# literal de citas ni la cantidad mínima de aprendizajes exigidos.
_UNIV_CITAS_ORIGINAL = _aero_citas_preseleccionadas

def _aero_citas_preseleccionadas(documentos,caso):
    if not caso.get('_universal'):return _UNIV_CITAS_ORIGINAL(documentos,caso)
    anclas=_univ_tokens(caso.get('_titulo_caso',caso['titulo']))
    ranking=[]
    for doc in documentos[:AERO_IA_MAX_FUENTES_PROMPT]:
        texto=doc['texto'][:AERO_IA_CARACTERES_FUENTE]
        frases=re.split(r'(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÑ0-9])',texto)
        for frag in frases:
            f=re.sub(r'\s+',' ',frag).strip()
            if not 65<=len(f)<=250:continue
            norm=_univ_normalizar(f)
            score=sum(3 for w in anclas if w in norm.split())
            if score:ranking.append((score,doc['id'],f))
    ranking.sort(key=lambda x:-x[0]);vistos=set();salida=[]
    for score,fuente,cita in ranking:
        if cita in vistos:continue
        vistos.add(cita)
        salida.append({'cita_id':'C'+str(len(salida)+1),'fuente_id':fuente,'cita_textual':cita})
        if len(salida)>=AERO_IA_CITAS_PRESELECCIONADAS:break
    return salida

_UNIV_VALIDAR_TITULO_ORIGINAL = _validar_titulo_youtube

def _validar_titulo_youtube(datos,caso):
    if not caso.get('_universal'):return _UNIV_VALIDAR_TITULO_ORIGINAL(datos,caso)
    titulo=re.sub(r'\s+',' ',str(datos.get('titulo_youtube',''))).strip()
    if not 32<=len(titulo)<=95 or re.search(r'https?://|[#\n\r]',titulo):
        raise ValueError('Título de YouTube no válido.')
    tema=_univ_tokens(caso.get('_titulo_caso',caso['titulo']))
    if tema and not (tema & _univ_tokens(titulo)):
        raise ValueError('Título no está vinculado al tema.')
    return titulo

# Los nichos que impliquen salud, finanzas o seguridad requerirán revisión
# humana antes de difusión pública. El YML actual se prueba en modo private.
_UNIV_EJECUTAR_IMPL = None

def _univ_activar_catalogo():
    global CASOS,CATALOGO_AERONAUTICO,ENFOQUE_CATEGORIA,TEMA
    if _nicho_es_aviacion():return
    if not NICHO.strip() or len(NICHO)>85:
        raise ValueError('NICHO debe contener entre 1 y 85 caracteres.')
    if _nicho_es_industria_aeronautica():
        nuevos, episodios = _catalogo_industria_aeronautica(CASOS, CATALOGO_AERONAUTICO)
        if not episodios:
            raise RuntimeError('El catálogo técnico de industria aeronáutica está vacío.')
        CASOS = nuevos
        CATALOGO_AERONAUTICO = episodios
        categorias = {c['categoria'] for c in nuevos.values()}
        ENFOQUE_CATEGORIA = {k: v for k, v in ENFOQUE_CATEGORIA.items() if k in categorias}
        print('NICHO TÉCNICO:', NICHO, '| catálogo aeronáutico curado:', len(episodios), flush=True)
        if TEMA != 'aleatorio' and TEMA not in episodios:
            print('AERO_TEMA no pertenece a este perfil; selección aleatoria.', flush=True)
            TEMA = 'aleatorio'
        return
    import requests
    nuevos,episodios=_univ_descubrir_catalogo()
    CASOS=nuevos;CATALOGO_AERONAUTICO=episodios
    ENFOQUE_CATEGORIA={NICHO:('Investigación específica y prudente sobre '+NICHO,
                              '¿Qué indican realmente las fuentes recuperadas?')}
    # AERO_TEMA del YML puede conservar el ID fijo de un nicho anterior.
    # Si no existe en el catálogo dinámico, seleccionar aleatorio sin cambiar YML.
    if TEMA!='aleatorio' and TEMA not in CATALOGO_AERONAUTICO:
        print('AERO_TEMA no pertenece al catálogo de este nicho; usando selección aleatoria.',flush=True)
        TEMA='aleatorio'
    print('NICHO UNIVERSAL:',NICHO,'| temas documentales candidatos:',len(episodios),flush=True)

def ejecutar():
    """Un fallo de fuentes/guion permite probar otro tema, sin repetir publicaciones."""
    if not AERO_IA_DRY_RUN:asegurar_dependencias()
    historial=ruta_historial()
    cantidad=int(VIDEOS_POR_EJECUCION)
    if not 1<=cantidad<=len(CATALOGO_AERONAUTICO):
        raise ValueError('AERO_VIDEOS_POR_EJECUCION fuera del catálogo.')
    if PUBLICAR_EN_YOUTUBE and not AERO_IA_DRY_RUN:
        if (not _nicho_es_aviacion() and YOUTUBE_PRIVACY!='private' and
            any(p in _univ_slug(NICHO) for p in ('salud','medicina','farmaco','inversion','finanzas','politica'))):
            raise RuntimeError('Este nicho requiere revisión editorial humana; usar YOUTUBE_PRIVACY=private.')
        if YOUTUBE_PRIVACY!='private' and not PERMITIR_PUBLICACION_SIN_REVISION:
            raise RuntimeError('Publicación pública requiere ALLOW_UNREVIEWED_PUBLICATION=true.')
        validar_canal_youtube(youtube_servicio())
    ya={r.get('episodio') for r in leer_historial(historial)}
    if PUBLICAR_EN_YOUTUBE and not AERO_IA_DRY_RUN and not CREAR_VISTA_PREVIA:
        pendientes=_cola_reanudar(historial,cantidad)
        if pendientes is not None:return pendientes
    ya |= _cola_ids()
    candidatos=[x for x in CATALOGO_AERONAUTICO if x not in ya]
    if TEMA!='aleatorio':
        if TEMA not in CATALOGO_AERONAUTICO:raise ValueError('Tema desconocido: '+TEMA)
        candidatos=[TEMA] if TEMA not in ya else []
        if AERO_PERMITIR_CAMBIO_TEMA_EXPLICITO and AERO_CAMBIAR_TEMA_SI_FALLA:
            candidatos += [x for x in CATALOGO_AERONAUTICO if x not in ya and x!=TEMA]
    rng=random.SystemRandom();cola=candidatos[:1] if TEMA!='aleatorio' else []
    restantes=[x for x in candidatos if x not in cola]
    rng.shuffle(restantes)
    if _motor_nicho(NICHO):
        restantes.sort(key=lambda x: _motor_evidencia(CATALOGO_AERONAUTICO[x]['titulo']),reverse=True)
    restantes.sort(key=lambda x: _guion_cache_path(x).is_file(),reverse=True)
    cola.extend(restantes)
    print(f'Catálogo: {len(CATALOGO_AERONAUTICO)} temas en {len(ENFOQUE_CATEGORIA)} áreas.')
    print('Publicados o generados antes:',len(ya),'| objetivo actual:',cantidad)
    if not cola:raise RuntimeError('No hay episodios nuevos disponibles.')
    max_intentos=min(len(cola),max(cantidad,AERO_MAX_TEMAS_POR_EJECUCION))
    if not AERO_CAMBIAR_TEMA_SI_FALLA:max_intentos=min(max_intentos,cantidad)
    resultados=[];fallos=[]
    for episodio_id in cola[:max_intentos]:
        if len(resultados)>=cantidad:break
        if not _aero_motores_guion() and not _guion_cache_path(episodio_id).is_file():
            print('  Sin proveedores IA ni guion aprobado recuperable para este tema; se omite.',flush=True)
            continue
        episodio=dict(CATALOGO_AERONAUTICO[episodio_id])
        print(f'\n=== INTENTO {len(resultados)+len(fallos)+1}/{max_intentos} '
              f'· {episodio_id} · videos completados {len(resultados)}/{cantidad} ===',flush=True)
        try:
            resultado=producir_episodio(episodio,historial)
            resultados.append(resultado)
        except PublicacionAplazada as exc:
            print(str(exc),flush=True)
            _cola_json(OUTPUT_BASE/'ULTIMO_INFORME_EJECUCION.json', {'estado':'publicacion_aplazada','detalle':str(exc),'videos_completados':len(resultados),'videos_solicitados':cantidad})
            return resultados
        except EpisodioRecuperable as exc:
            fallos.append({'tema':episodio_id,'error':str(exc)[:900],
                           'fecha_utc':datetime.now(timezone.utc).isoformat()})
            print('  TEMA PENDIENTE (no marcado como publicado):',episodio_id,str(exc)[:330],flush=True)
            if not AERO_CAMBIAR_TEMA_SI_FALLA:break
        # Fallos documentales y visuales son recuperables antes de TTS/subida.
        # Errores posteriores pueden producir cargas parciales y NO se reintentan.
    OUTPUT_BASE.mkdir(parents=True,exist_ok=True)
    aplazado=(len(resultados)<cantidad and bool(_AERO_IA_INHABILITADOS) and not _aero_motores_guion())
    (OUTPUT_BASE/'ULTIMO_INFORME_EJECUCION.json').write_text(json.dumps({
        'estado': 'aplazado_sin_ia' if aplazado else ('completado' if len(resultados)>=cantidad else 'incompleto'),
        'fecha_utc':datetime.now(timezone.utc).isoformat(),
        'videos_completados':len(resultados),'videos_solicitados':cantidad,
        'fallos_preproduccion':fallos,'proveedores_ia_inhabilitados':_AERO_IA_INHABILITADOS,
        'resultados':[str(r) for r in resultados]
    },ensure_ascii=False,indent=2),encoding='utf-8')
    if aplazado and AERO_APLAZAR_SIN_IA:
        print(f'PRODUCCIÓN APLAZADA: {len(resultados)}/{cantidad} videos; proveedores IA agotados o indisponibles. No se publica ni se registra como completado ningún tema fallido. Revisar ULTIMO_INFORME_EJECUCION.json.',flush=True)
        return resultados
    if len(resultados)<cantidad:
        raise RuntimeError(f'Se completaron {len(resultados)}/{cantidad} videos. '
                           f'Se probaron hasta {max_intentos} temas. '
                           'Revisar ULTIMO_INFORME_EJECUCION.json. '
                           'Nunca se publican guiones sin evidencia.')
    return resultados

def prueba_interna():
    """Pruebas locales sin HTTP, credenciales, imagen ni publicación."""
    assert "'evidencia','aplicacion'" not in __import__('inspect').getsource(_validar_guion_ia)
    assert not any('Repasemos lo que sí puede comprobarse' in texto for _,texto in plan_guion(CASOS['motor_07']))
    assert len(CATALOGO_AERONAUTICO)==100  # catálogo aeronáutico original se conserva
    assert VOZ=='es-CL-LorenzoNeural' and PRONUNCIACION_INGLES is False
    assert normalizar_unidades_narracion('1 NM y 120 nm')=='1 milla náutica y 120 millas náuticas'
    caso=dict(CASOS['motor_07'],_episodio={'caso_id':'motor_07'})
    bueno=('Aircraft cabin pressurization provides a pressurized cabin. '
           'Cabin altitude and differential pressure are controlled by an outflow valve. ')*10
    assert _aero_documento_relevante(bueno,caso)>0
    assert _aero_documento_relevante('Microsoft account login and consumer software '*30,caso)==0
    assert _aero_documento_relevante('Aviation aircraft flight information '*30,caso)==0
    caso2=dict(CASOS['future_03'],_episodio={'caso_id':'future_03'})
    hid=('Hydrogen aircraft hydrogen propulsion and liquid hydrogen storage '
         'for aviation certification and infrastructure. ')*12
    assert _aero_documento_relevante(hid,caso2)>0
    # Regresión: jamás utilizar una página meteorológica para mantenimiento.
    inspeccion=dict(CASOS['mnt_02'],_episodio={'caso_id':'mnt_02'})
    meteorologia=('Aviation aircraft weather icing wind visibility forecasts flight pilot. '*60)
    assert _aero_documento_relevante(meteorologia,inspeccion)==0
    mantenimiento=('Aircraft maintenance inspections check structural defects and airworthiness. '*60)
    assert _aero_documento_relevante(mantenimiento,inspeccion)>0
    sistema=dict(CASOS['motor_08'],_episodio={'caso_id':'motor_08'})
    assert _aero_documento_relevante(meteorologia,sistema)==0
    assert _aero_documento_relevante(('Aircraft electrical power distribution and electrical system generator. '*50),sistema)>0
    assert not _aero_fragmentos(meteorologia,inspeccion)
    rodaje=dict(CASOS['atc_02'],_episodio={'caso_id':'atc_02'})
    assert evaluar_relevancia_foto(rodaje,'File:Airport ATC Control Tower.jpg',{},'airport taxiway') == (0, [])
    assert evaluar_relevancia_foto(rodaje,'File:Airbus A320 taxiing at airport.jpg',{},'aircraft taxiing')[0] > 0
    assert len(_consultas_fotos(rodaje)) >= 10
    try:
        _validar_titulo_youtube({'titulo_youtube':'¿Por qué el rodaje seguro depende de los videos de la FAA?'},
                                dict(rodaje,_titulo_caso='Qué es el rodaje en un aeropuerto'))
        raise AssertionError('Título sobre videos de FAA debería rechazarse')
    except ValueError:
        pass
    doc={'id':'F1','texto':('The aircraft altimeter measures altitude using atmospheric pressure. '
          'Pilots must set the altimeter using the published pressure reference. ')*5}
    nav=dict(CASOS['nav_02'],_episodio={'caso_id':'nav_02'})
    citas=_aero_citas_preseleccionadas([doc],nav)
    assert citas and citas[0]['cita_id']=='C1'
    datos={'hechos_con_evidencia':[{'cita_id':'C1','afirmacion':'El altímetro indica altitud según presión atmosférica.'}]}
    _aero_resolver_citas_ia(datos,citas)
    assert datos['hechos_con_evidencia'][0]['cita_textual']==citas[0]['cita_textual']
    assert datos['hechos_con_evidencia'][0]['fuente_id']=='F1'
    # Regresión universal: una fuente (nombre,url,palabras) no debe generar
    # ValueError: too many values to unpack (expected 2).
    if not _nicho_es_aviacion():
        from tempfile import TemporaryDirectory
        from unittest.mock import patch
        prueba={'id':'horror_test','titulo':'Cuento de fantasmas',
                '_universal':True,'fuentes':[('Wikipedia: Cuento de fantasmas',
                'https://es.wikipedia.org/wiki/Cuento_de_fantasmas',['fantasmas'])]}
        doc_prueba={'nombre':'Wikipedia: Cuento de fantasmas',
                    'url':'https://es.wikipedia.org/wiki/Cuento_de_fantasmas',
                    'texto':'Un cuento de fantasmas es una narración literaria de ficción. '*15,
                    'coincidencias_tema':3,'cache':False}
        def simular_descarga(*args,**kwargs):return dict(doc_prueba)
        with TemporaryDirectory() as td, \
             patch.dict(globals(),{'AERO_MIN_FUENTES':1}), \
             patch.dict(globals(),{'_univ_recuperar_wikipedia':lambda *a:None,
                                   '_aero_descargar_documento':simular_descarga}):
            docs=investigar_episodio(prueba,td,None)
            assert len(docs)==1 and docs[0]['id']=='F1'
        assert _univ_tema_terror_pertinente('Cuento de fantasmas','Relato de miedo')
        assert not _univ_tema_terror_pertinente('Urban Terror','Videojuego de disparos')
        if _univ_es_terror():
            with TemporaryDirectory() as td:
                prueba_arte=dict(prueba,id='terror-test-01')
                arte,reg=_completar_visual_terror(prueba_arte,td,[],[])
                assert len(arte)==(AERO_VISUALES_OBJETIVO if MODO_VIRAL and IMAGENES_POR_ESCENA else IMAGENES_MINIMAS) and len(reg)==len(arte)
                assert all(x.exists() for x in arte)
                assert all(x.get('tipo_recurso')=='ilustracion_procedural' for x in reg)
                # Regresión: los metadatos de las imágenes procedurales no
                # deben bloquear la producción antes de renderizar el vídeo.
                assert all(_credito_recurso_visual_valido(x) for x in reg)
                descripcion_youtube(prueba_arte, [{'nombre':'Ensayo','url':'https://example.org/fuente'}], reg)
                cc0={'archivo':'imagen_90.jpg','titulo':'Foto externa CC0', 'licencia':'CC0', 'licencia_url':'', 'pagina':'https://commons.wikimedia.org/wiki/File:Example.jpg'}
                assert _credito_recurso_visual_valido(cc0)
                by={'archivo':'imagen_91.jpg','titulo':'Foto externa con atribución', 'licencia':'CC BY-SA 4.0', 'licencia_url':'https://creativecommons.org/licenses/by-sa/4.0/'}
                assert not _credito_recurso_visual_valido(by)
                assert not _credito_recurso_visual_valido(dict(reg[0], url_original='https://example.org/external.jpg'))
                try:
                    descripcion_youtube(prueba_arte, [], reg+[by])
                except RuntimeError as exc:
                    assert 'licencia' in str(exc).lower() or 'atribución' in str(exc).lower()
                else:
                    raise AssertionError('La imagen CC BY-SA sin créditos no fue rechazada')
                assert len({hashlib.sha256(x.read_bytes()).hexdigest() for x in arte})==len(arte)
                print('OK: terror con escenas originales distintas, sin fotografías falsas')
    # Test de la declaración automatizada de YouTube (sin subir videos).
    prueba_procedural={'tipo_recurso':'ilustracion_procedural','consulta_origen':'generación local sin API','url_original':''}
    assert _aero_declaracion_ia_youtube({},[prueba_procedural])[0] is False
    assert _aero_declaracion_ia_youtube({},[{'url_original':'https://commons.wikimedia.org/wiki/Sample.jpg'}])[0] is False
    assert _aero_declaracion_ia_youtube({},[{'tipo_recurso':'escena_fotorealista_ia'}])[0] is True
    assert _aero_declaracion_ia_youtube({},[{'archivo':'desconocida.png'}])[0] is True
    print('OK: declaración AI use No para arte estilizado; Yes si es fotorealista o de origen desconocido')
    # Controles de regresión del paquete viral (sin API ni publicación).
    assert len(_viral_variantes_titulos({'titulo':'¿Por qué ocurre este fenómeno tan extraño?', '_titulo_caso':'El fenómeno extraño'})) >= 1
    assert 'comentarios' in _viral_pregunta_contextual({'titulo':'Leyendas', '_titulo_caso':'Leyendas'})
    assert MODO_VIRAL and TITULOS_CANDIDATOS in (1,2,3) and MINIATURAS_CANDIDATAS in (1,2,3)
    test_qa=_viral_evaluacion({'titulo':'¿Por qué ocurre este fenómeno tan extraño?'}, [('gancho','La puerta del sótano estaba cerrada por dentro y aun así se oyó una voz desde el otro lado.')])
    assert 'advertencias' in test_qa and test_qa['escenas']==1
    assert VOZ=='es-CL-LorenzoNeural'
    print('OK: 100 temas, Lorenzo, NM, fuentes, citas literales, fotos, títulos y auditoría viral')

# ==================== 8.0: CURIOSITY ENGINE Y COLA SEGURA ====================
def _motor_nicho(nicho):
    n=_univ_normalizar(nicho)
    return bool(re.search(r'\b(motor\w*|engine\w*|propulsion)\b',n) and re.search(r'aeronaut|aviacion|aircraft|aviation',n))

def _motor_evidencia(texto):
    t=_univ_normalizar(texto)
    if re.search(r'\b(turbofan\w*|turborreactor\w*|turbojet\w*|turboprop\w*|turbohelice\w*|aeroengine\w*)\b',t):return True
    motores=list(re.finditer(r'\b(motor\w*|engine\w*|propulsion|turbina\w*|turbine\w*|compresor\w*|compressor\w*|piston\w*)\b',t))
    aereo=list(re.finditer(r'\b(aeronaut\w*|aviacion|avion\w*|aeronave\w*|aircraft|airplane\w*|aviation|aero)\b',t))
    return any(abs(m.start()-a.start())<=120 for m in motores for a in aereo)


def _motor_foto(nombre,detalle):
    t=_univ_normalizar(nombre+' '+detalle)
    # Penalizar el objeto de la foto, no solo el nombre de la empresa.
    if re.search(r'\b(landaulet|viktoria|automovil\w*|automobile\w*|car|cars|truck|camion\w*|locomotiv\w*|railway|tram|tranvia|electric car)\b',_univ_normalizar(nombre)):return False
    if re.search(r'\b(automobile|automovil|truck|locomotive|railway)\b',t) and not _motor_evidencia(nombre):return False
    return _motor_evidencia(t)

def _curiosity_tema_pertinente(titulo,resumen):
    if _nicho_es_industria_aeronautica():
        # Production uses the curated catalogue; reject generic results here as well.
        t = _univ_normalizar(titulo)
        if re.search(r'\b(submarin\w*|naval|automovil\w*|locomotiv\w*|ferrocarril\w*)\b',t):return False
        return bool(re.search(r'\b(aeronaut\w*|aviacion|aerolinea\w*|aeropuerto\w*|avion\w*|aeronave\w*|turbofan\w*|turborreactor\w*|turbohelice\w*|aeronavegabilidad)\b',t))
    if _motor_nicho(NICHO):
        if re.search(r'\b(automovil\w*|automobile\w*|landaulet|locomotiv\w*|camion\w*)\b',_univ_normalizar(titulo)):return False
        return _motor_evidencia(titulo+' '+resumen)
    anclas=_univ_tokens(NICHO) or set(_univ_normalizar(NICHO).split())
    # Strip editorial framing, not actual niche terms ("datos de X" etc.).
    anclas -= {'datos','industria','curiosidades','documentales','informacion'} if len(anclas)>1 else set()
    corpus=set(_univ_normalizar(titulo+' '+resumen).split())
    # All remaining anchors: safer than accepting 65% on compound niches.
    return bool(anclas and anclas.issubset(corpus))

def _curiosity_formato(caso):
    t=_univ_normalizar(caso.get('_titulo_caso',caso['titulo']))
    if _univ_es_terror():return 'Relato inmersivo, conflicto, tensión y desenlace; identificar ficción o leyenda sin presentarla como hecho real.'
    if _motor_nicho(NICHO):return 'Enigma técnico: funcionamiento del motor, mecanismo causal, comparación o consecuencia verificable, resolución. No convertirlo en historia general de la empresa.'
    if _nicho_es_industria_aeronautica():return 'Curiosidad documentada sobre la industria aeronáutica: mecanismo, causa, consecuencia operacional o económica, comparación con datos comprobables y respuesta clara. Mantén el enfoque aeronáutico; no inventes conexiones con otras industrias.'
    if any(x in t for x in ('historia','batalla','imperio','revolucion')):return 'Narrativa histórica causal, protagonistas y acontecimientos documentados, consecuencias.'
    return 'Selecciona el formato pertinente: cómo funciona, por qué ocurre, comparación fundamentada o escenario hipotético explícito. Resuelve la pregunta inicial con evidencia.'

def _curiosity_consultas_fotos(caso,titulo):
    contexto=' aircraft engine' if _motor_nicho(NICHO) else ' '+NICHO
    consultas=[titulo+contexto, titulo+contexto+' photograph']
    for q in caso.get('_consultas_escenas',[]):
        if q.strip():consultas.append(titulo+' '+q+(' aircraft engine' if _motor_nicho(NICHO) else ''))
    consultas += [titulo+' motor aeronáutico',titulo+' aircraft engine museum'] if _motor_nicho(NICHO) else [titulo+' fotografía',titulo+' photograph',titulo+' '+NICHO]
    return list(dict.fromkeys(consultas))

def _curiosity_tokens_visuales(txt):
    tokens=_univ_tokens(txt)
    equivalencias={
      'motor':'engine','motores':'engine','engines':'engine','aeronaves':'aircraft','aeronave':'aircraft','avion':'aircraft','aviones':'aircraft','aeronautico':'aviation','aeronauticos':'aviation','aeronautica':'aviation','aviacion':'aviation',
      'compresor':'compressor','compresores':'compressor','compressors':'compressor',
      'turbina':'turbine','turbinas':'turbine','turbines':'turbine',
      'combustion':'combustion','combustible':'fuel','combustibles':'fuel',
      'helice':'propeller','helices':'propeller','propellers':'propeller',
      'pistones':'piston','pistons':'piston','cilindro':'cylinder','cilindros':'cylinder','cylinders':'cylinder',
      'radiales':'radial','turbofan':'turbofan','turbohelice':'turboprop','turborreactor':'turbojet',
      'rotor':'rotor','rotores':'rotor','aspas':'blade','alabes':'blade','blades':'blade',
      'reactor':'jet','inyector':'injector','inyectores':'injector','injectors':'injector',
      'escape':'exhaust','gases':'gas','tobera':'nozzle','toberas':'nozzle','nozzles':'nozzle',
      'camara':'chamber','camaras':'chamber','chambers':'chamber','corte':'cutaway',
      'navegacion':'navigation','cohete':'rocket','cohetes':'rocket','planeta':'planet','planetas':'planet',
      'estrellas':'star','galaxia':'galaxy','galaxias':'galaxy','bosque':'forest','oceano':'ocean'}
    ruido=set('photograph photography photo fotografias fotografia imagen image images pictures archivo file commons wikimedia museo museum historico historical antiguo antigua old modelo model muestra shown view lado side vista parte section detail detalles equipo equipment general tecnico technical'.split())
    return {equivalencias.get(t,t) for t in tokens if t not in ruido}

def _curiosity_asignar_escenas(caso,fotos,creditos,carpeta):
    """A photo without scene-level match is replaced by an explicit text card.
    No search query counts as evidence that an image contains a subject."""
    if caso.get('_universal') and _univ_es_terror():return
    from PIL import Image,ImageDraw
    plan=[p for p in caso.get('_plan_visual',[]) if p[0]!='cta']
    registros=[];mapa=[];usos={}
    # Never use the company name alone to prove relevance to a scene.
    tema=_curiosity_tokens_visuales(caso.get('_titulo_caso',caso['titulo']))
    genericos=set('motor motores engine engines aeronave aeronaves aircraft avion aviones aviation aviacion aeronauticos aeronautico funcionamiento sistema tecnologia'.split())
    for i,(tipo,txt) in enumerate(plan):
        tokens=_curiosity_tokens_visuales(txt)-tema-genericos
        consultas=caso.get('_consultas_escenas',[])
        qtokens=(_curiosity_tokens_visuales(consultas[i])-tema-genericos) if i<len(consultas) else set()
        opciones=[]
        for j,foto in enumerate(fotos):
            c=creditos[j]
            evidencia=c.get('titulo','')+' '+c.get('objeto_visual',c.get('detalle_visual',''))
            score,hits=_score_escena_83(caso,i,evidencia)
            if score>0:
                opciones.append((score-2*usos.get(j,0),-usos.get(j,0),j,hits))
        if opciones:
            _,_,j,hits=max(opciones); usos[j]=usos.get(j,0)+1; path=fotos[j]
            registros.append({'escena':i+1,'archivo':Path(path).name,'criterio':'coincidencia textual en metadatos, no comprobación visual directa','coincidencias':hits})
        else:
            # Text card is deliberately not a documentary photograph.
            path=Path(carpeta)/f'tarjeta_contextual_{i:02}.jpg'
            im=Image.new('RGB',(1600,900),'#101b2d');d=ImageDraw.Draw(im)
            frase=_frase_visual_83(txt)
            d.rectangle((100,155,115,720),fill='#43c7dc')
            escribir_en_caja(d,frase,(155,205,1480,725),cargar_fuente(56),'#ffffff',max_lineas=5,centrar_vertical=True)
            im.save(path,quality=92)
            registros.append({'escena':i+1,'archivo':path.name,'criterio':'tarjeta textual del relato; sin fotografía atingente','texto':frase})
        mapa.append(str(path))
    caso['_mapa_visual']=mapa
    (Path(carpeta)/'PLAN_VISUAL_ESCENAS.json').write_text(json.dumps(registros,ensure_ascii=False,indent=2),encoding='utf-8')
    n_fotos=sum('coincidencias' in r for r in registros)
    print('  Plan visual: ',n_fotos,'escenas con foto contextual de',len(registros),flush=True)
    if plan and PUBLICAR_EN_YOUTUBE and YOUTUBE_PRIVACY!='private':
        if _es_financiero(caso):
            # Reportajes de economía: los conceptos abstractos se pueden explicar
            # mediante tarjetas originales; se exigen fotos CIVILES contextuales.
            fotos_usadas={r['archivo'] for r in registros if 'coincidencias' in r}
            total_recursos=len({r['archivo'] for r in registros})
            if len(fotos_usadas)<2 or total_recursos<IMAGENES_MINIMAS:
                raise EpisodioRecuperable('Finanzas: se requieren al menos dos fotos civiles distintas asignadas a escenas y el mínimo editorial de recursos distintos. Revisar PLAN_VISUAL_ESCENAS.json.')
        elif n_fotos < math.ceil(len(plan)*0.5):
            raise EpisodioRecuperable('Menos de la mitad de las escenas tiene apoyo fotográfico pertinente; no publicar automáticamente. Revisar PLAN_VISUAL_ESCENAS.json.')

class PublicacionAplazada(RuntimeError):pass

def _cola_json(path,datos):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(datos,ensure_ascii=False,indent=2),encoding='utf-8');tmp.replace(path)

def _cola_manifiestos():
    for p in sorted(AERO_COLA_DIR.glob('*/pendiente.json')):
        yield p,json.loads(p.read_text(encoding='utf-8'))

def _cola_ids():
    return {d['episodio']['id'] for _,d in _cola_manifiestos() if d.get('estado') in ('listo','limite','intento_incierto','publicado')}

def _cola_intento(p,d,historial):
    # Check history FIRST: an upload with a returned ID must never be repeated.
    existente=next((r for r in leer_historial(historial) if r.get('episodio')==d['episodio']['id'] and r.get('youtube_id')),None)
    if existente:
        d.update(estado='publicado',youtube_id=existente['youtube_id'],youtube_estado=existente.get('youtube_estado','video_subido'))
        _cola_json(p,d)
        print('Video ya registrado; no se vuelve a subir:',existente['youtube_id'],flush=True)
        return existente['youtube_id']
    if d.get('estado') not in ('listo','limite'):
        raise PublicacionAplazada('Carga anterior incierta: revisar YouTube Studio antes de reintentar '+str(p))
    if time.time()<d.get('reintentar_desde',0):raise PublicacionAplazada('Límite YouTube: publicación pendiente conservada hasta '+datetime.fromtimestamp(d['reintentar_desde'],timezone.utc).isoformat())
    if d['privacidad']!=YOUTUBE_PRIVACY:raise PublicacionAplazada('Privacidad de la cola distinta de la configuración actual; revisar antes de publicar.')
    for k in ('video','miniatura','srt'):
        if not (p.parent/d[k]).is_file():raise RuntimeError('Archivo pendiente faltante: '+d[k])
    d['estado']='intento_incierto';_cola_json(p,d)
    try:
        vid=publicar_youtube(p.parent/d['video'],p.parent/d['miniatura'],p.parent/d['srt'],d['caso'],d['episodio'],d['fuentes'],d['creditos'],p.parent,historial,canal_esperado=d.get('canal_id'))
    except Exception as exc:
        if 'uploadLimitExceeded' in str(exc) and not any(r.get('episodio')==d['episodio']['id'] and r.get('youtube_id') for r in leer_historial(historial)):
            d.update(estado='limite',reintentar_desde=time.time()+86400,error='uploadLimitExceeded');_cola_json(p,d)
            raise PublicacionAplazada('YouTube alcanzó el límite de subida. Video conservado: '+str(p.parent/d['video'])) from exc
        # Other errors may be after upload; history or manual reconciliation required.
        d['error']=str(exc)[:500];_cola_json(p,d);raise
    d.update(estado='publicado',youtube_id=vid);_cola_json(p,d)
    # Keep manifest; remove duplicate media only when original still exists locally.
    original=Path(d.get('carpeta_original',''))
    if original.is_dir() and original.resolve()!=p.parent.resolve() and all((original/d[k]).is_file() for k in ('video','miniatura','srt')):
        for archivo in ('PUBLICACION_YOUTUBE.json','DECLARACION_IA_YOUTUBE.json','MINIATURA_YOUTUBE.json'):
            if (p.parent/archivo).is_file():shutil.copy2(p.parent/archivo,original/archivo)
        datos=leer_historial(historial)
        for r in datos:
            if r.get('episodio')==d['episodio']['id']:r['salida']=str(original/d['video'])
        _cola_json(historial,datos)
        for k in ('video','miniatura','srt'):(p.parent/d[k]).unlink(missing_ok=True)
    return vid

def _cola_publicar(video,thumb,srt,caso,episodio,fuentes,creditos,carpeta,historial):
    p=AERO_COLA_DIR/episodio['id']/ 'pendiente.json'
    if p.exists():raise PublicacionAplazada('Ya existe una cola para este episodio: '+str(p))
    canal_id=validar_canal_youtube(youtube_servicio())
    p.parent.mkdir(parents=True,exist_ok=True)
    for archivo in (video,thumb,srt):shutil.copy2(archivo,p.parent/Path(archivo).name)
    d={'estado':'listo','nicho':NICHO,'canal_id':canal_id,'carpeta_original':str(carpeta),'privacidad':YOUTUBE_PRIVACY,'video':Path(video).name,'miniatura':Path(thumb).name,'srt':Path(srt).name,'caso':{k:v for k,v in caso.items() if not k.startswith('_') or k in ('_titulo_caso','_universal')},'episodio':episodio,'fuentes':fuentes,'creditos':creditos,'creado_utc':datetime.now(timezone.utc).isoformat()}
    _cola_json(p,d);return _cola_intento(p,d,historial)

def _cola_reanudar(historial,cantidad):
    # Block on pending of current channel/niche; never mix niches automatically.
    activos=[(p,d) for p,d in _cola_manifiestos() if d.get('estado')!='publicado']
    if not activos:return None
    if YOUTUBE_PRIVACY!='private' and not PERMITIR_PUBLICACION_SIN_REVISION:
        raise RuntimeError('Publicación de pendientes requiere ALLOW_UNREVIEWED_PUBLICATION=true.')
    if any(d.get('nicho')!=NICHO for _,d in activos):
        print('Hay publicaciones pendientes de otro nicho; restaurar ese nicho o revisar la cola antes de producir.',flush=True);return []
    resultados=[]
    for p,d in activos[:cantidad]:
        try:resultados.append(_cola_intento(p,d,historial))
        except PublicacionAplazada as exc:
            print(str(exc),flush=True)
            _cola_json(OUTPUT_BASE/'ULTIMO_INFORME_EJECUCION.json',{'estado':'publicacion_aplazada','detalle':str(exc),'videos_completados':len(resultados),'videos_solicitados':cantidad})
            break
    if len(resultados)==min(len(activos),cantidad):
        _cola_json(OUTPUT_BASE/'ULTIMO_INFORME_EJECUCION.json',{'estado':'cola_procesada','videos_completados':len(resultados),'videos_solicitados':cantidad,'videos_youtube':resultados})
    return resultados

def _self_test_8():
    from unittest.mock import patch
    from tempfile import TemporaryDirectory
    assert _motor_nicho('Motores Aeronáuticos')
    assert not _motor_foto('Siemens-Schuckert Typ B Landaulet.jpg','Siemens Schuckert')
    assert _motor_foto('Siemens aircraft engine.jpg','aircraft piston engine')
    assert _motor_evidencia('motor de avión de pistón')
    with patch.dict(globals(),{'NICHO':'Motores Aeronáuticos'}):
        caso={'titulo':'Siemens-Schuckert','_universal':True}
        assert evaluar_relevancia_foto(caso,'File:Siemens-Schuckert Typ B Landaulet.jpg',{},'aircraft engine')==(0,[])
        assert evaluar_relevancia_foto(caso,'File:Siemens-Schuckert aircraft radial engine.jpg',{},'aircraft engine')[0]>0
        caso={'titulo':'Motor radial','_universal':True}
        assert evaluar_relevancia_foto(caso,'File:Aircraft radial piston engine.jpg',{},'motor radial')[0]>0
    with TemporaryDirectory() as td:
        root=Path(td); h=root/'historial.json'; p=root/'pendiente.json'
        for name in ('v.mp4','t.jpg','s.srt'):(root/name).write_bytes(b'test')
        d={'estado':'listo','episodio':{'id':'test'},'privacidad':YOUTUBE_PRIVACY,'video':'v.mp4','miniatura':'t.jpg','srt':'s.srt','caso':{},'fuentes':[],'creditos':[]}
        def limite(*args,**kwargs):raise RuntimeError('uploadLimitExceeded')
        with patch.dict(globals(),{'publicar_youtube':limite}):
            try:_cola_intento(p,d,h)
            except PublicacionAplazada:pass
            else:raise AssertionError('Límite no detectado')
            assert d['estado']=='limite' and (root/'v.mp4').exists()
            try:_cola_intento(p,d,h)
            except PublicacionAplazada:pass
            else:raise AssertionError('Reintento prematuro')
        d['estado']='intento_incierto';d['reintentar_desde']=0
        try:_cola_intento(p,d,h)
        except PublicacionAplazada:pass
        else:raise AssertionError('Reintento ambiguo')
        d['estado']='limite'
        def exito(*args,**kwargs):
            _cola_json(h,[{'episodio':'test','youtube_id':'ID_SIMULADO','youtube_estado':'completo'}]);return 'ID_SIMULADO'
        with patch.dict(globals(),{'publicar_youtube':exito}):
            assert _cola_intento(p,d,h)=='ID_SIMULADO' and d['estado']=='publicado'
        with patch.dict(globals(),{'publicar_youtube':lambda *a,**k: (_ for _ in ()).throw(AssertionError('Duplicado'))}):
            assert _cola_intento(p,d,h)=='ID_SIMULADO'
    from PIL import Image
    with TemporaryDirectory() as td, patch.dict(globals(),{'NICHO':'Motores Aeronáuticos','PUBLICAR_EN_YOUTUBE':False}):
        root=Path(td); fotos=[root/'compresor.jpg',root/'turbina.jpg']
        for f in fotos:Image.new('RGB',(800,600),'#183857').save(f)
        creditos=[{'titulo':'Aircraft axial compressor rotor','detalle_visual':'compressor blade rotor'},{'titulo':'Aircraft gas turbine exhaust nozzle','detalle_visual':'turbine exhaust nozzle'}]
        caso={'titulo':'Motor aeronáutico','_universal':True,'_plan_visual':[('gancho','El compresor contiene un rotor y álabes.'),('contexto','La turbina dirige los gases hacia la tobera.'),('desarrollo','Consideremos este fenómeno con atención.')]}
        _curiosity_asignar_escenas(caso,fotos,creditos,root)
        assert _foto_por_escena(caso,0,fotos)==fotos[0]
        assert _foto_por_escena(caso,1,fotos)==fotos[1]
        assert Path(caso['_mapa_visual'][2]).name.startswith('tarjeta_contextual_')
        assert Path(caso['_mapa_visual'][2]).is_file()
    print('OK: nicho motores, exclusión automóviles, cola límite y protección de reintentos')

def _self_test_81():
    from unittest.mock import patch
    from types import SimpleNamespace
    with patch.dict(globals(),{'NICHO':'Datos de la Industria Aeronáutica'}):
        c, e = _catalogo_industria_aeronautica(CASOS,CATALOGO_AERONAUTICO)
        assert len(c)==len(e)==60
        assert set(e).issubset(CATALOGO_AERONAUTICO)
        assert all(not x.get('_universal') for x in c.values())
        for t in ('Ravensburg','Historia de la ciencia y la tecnología en España','К-535 Yuri Dolgoruki'):
            assert not _curiosity_tema_pertinente(t,'menciona la industria aeronáutica')
        assert _curiosity_tema_pertinente('Mantenimiento de aeronaves','')
        assert _nicho_aeronautico()
        assert normalizar_unidades_narracion('120 NM')=='120 millas náuticas'
        with patch.dict(globals(),{'_univ_descubrir_catalogo':lambda: (_ for _ in ()).throw(AssertionError('no debe consultar Wikipedia'))}):
            # Activation mutates globals; patch restores original 100-case catalogue.
            _univ_activar_catalogo()
            assert len(CATALOGO_AERONAUTICO)==60 and 'fin_01' in CATALOGO_AERONAUTICO
    assert len(CATALOGO_AERONAUTICO)==100
    assert _groq_demora_tpm(SimpleNamespace(status_code=429,text='tokens per minute (TPM)',headers={'retry-after':'3'}))==3.5
    assert _groq_demora_tpm(SimpleNamespace(status_code=429,text='tokens per day (TPD)',headers={'retry-after':'3'})) is None
    base=dict(id='fixture/text:free',pricing={'prompt':'0','completion':'0'},architecture={'output_modalities':['text']},context_length=16384,supported_parameters=['response_format'])
    assert _openrouter_elegir_gratuito([base])=={'id':'fixture/text:free','json':True}
    assert _openrouter_elegir_gratuito([dict(base,id='fixture/paid',pricing={'prompt':'0.1','completion':'0'}),dict(base,id='fixture/reasoning:free',supported_parameters=['reasoning'])]) is None
    print('OK: perfil industria de 60 temas, tres casos ajenos rechazados, TPM vs TPD, OpenRouter gratuito alternativo')



# ========== 8.3: coherencia visual + cache de guiones aprobados ==========
# El cache guarda textos, no credenciales ni tokens. Un guion recuperado pasa
# nuevamente las reglas de estructura, longitud, citas y pertinencia documental.
def _guion_cache_path(episodio_id):
    clave=hashlib.sha256((_univ_slug(NICHO)+'|'+str(episodio_id)).encode()).hexdigest()
    return AERO_GUIONES_DIR/(clave+'.json')

def _guion_cache_guardar(episodio,caso,documentos,plan,carpeta):
    try:
        registro=json.loads((Path(carpeta)/'GUION_IA.json').read_text(encoding='utf-8'))
        _cola_json(_guion_cache_path(episodio['id']),{
            'version':VERSION_SCRIPT,'timestamp':time.time(),'nicho':NICHO,
            'episodio':episodio['id'],'tema':caso.get('_titulo_caso'),
            'titulo':caso['titulo'],'documentos':documentos,'datos':registro['resultado'],
            'plan':plan,'consultas':caso.get('_consultas_escenas',[]),'modo_viral':MODO_VIRAL,
            'pregunta_final':PREGUNTA_FINAL_ESPECIFICA})
    except (OSError,ValueError,KeyError,TypeError) as exc:
        print('  Aviso: guion aprobado no persistido:',str(exc)[:150],flush=True)

def _guion_cache_cargar(episodio,caso):
    try:
        p=_guion_cache_path(episodio['id'])
        guarda=json.loads(p.read_text(encoding='utf-8'))
        if (guarda['version']!=VERSION_SCRIPT or guarda['nicho']!=NICHO or
            guarda['episodio']!=episodio['id'] or guarda['tema']!=caso.get('_titulo_caso') or
            guarda['modo_viral']!=MODO_VIRAL or guarda['pregunta_final']!=PREGUNTA_FINAL_ESPECIFICA or
            not 0<=time.time()-guarda['timestamp']<=AERO_GUIONES_DIAS*86400):return None
        docs=guarda['documentos']
        if len(docs)<AERO_MIN_FUENTES or len({d['url'] for d in docs})<AERO_MIN_FUENTES:return None
        if any(not _url_publica_investigacion(d['url']) or _aero_documento_relevante(d['texto'],caso)<=0 for d in docs):return None
        plan=_validar_guion_ia(guarda['datos'],docs,caso)
        titulo=guarda['titulo']
        if not isinstance(titulo,str) or not 32<=len(titulo)<=95:return None
        # Reconstruir la llamada editorial; no confiar ciegamente en plan guardado.
        if MODO_VIRAL and PREGUNTA_FINAL_ESPECIFICA:
            for k in range(len(plan)-1,-1,-1):
                if plan[k][0]=='conclusion':
                    cierre=plan[k][1]; pregunta=_viral_pregunta_contextual(caso)
                    if '?' not in cierre and len((cierre+' '+pregunta).split())<=105:
                        plan[k]=('conclusion',cierre.rstrip(' .')+'. '+pregunta)
                    break
        plan.append(('cta','Si te gustó este contenido, dale Like y Suscríbete! Muchas gracias por tu visita y nos vemos en un próximo video!'))
        if [list(x) for x in plan]!=guarda['plan']:return None
        caso['titulo']=episodio['titulo']=titulo
        caso['_consultas_escenas']=[str(b.get('visual_query',''))[:100] for b in guarda['datos']['bloques']]
        return docs,plan
    except (OSError,ValueError,KeyError,TypeError,AttributeError):return None

# Bilingüe, orientado a objetos visibles y no a coincidencias de palabras vacías.
_VIS_83_EQ={
 'repostaje':'refueling','reabastecimiento':'refueling','abastecimiento':'refueling','refuel':'refueling','refuelling':'refueling','refueled':'refueling','refueling':'refueling','defueling':'defueling',
 'queroseno':'fuel','kerosene':'fuel','carburante':'fuel','combustibles':'fuel','combustible':'fuel','jetfuel':'fuel','camion':'truck','camiones':'truck','trucks':'truck','cisterna':'truck','tanker':'truck',
 'aerolinea':'airline','aerolineas':'airline','airlines':'airline','airliners':'airliner','avion':'aircraft','aviones':'aircraft','aeronave':'aircraft','aeronaves':'aircraft','airplanes':'aircraft','airplane':'aircraft',
 'aeropuerto':'airport','aeropuertos':'airport','airports':'airport','pasajero':'passenger','pasajeros':'passenger','passengers':'passenger','asiento':'seat','asientos':'seat','seats':'seat','cabina':'cabin','cabins':'cabin',
 'embarque':'boarding','embarcando':'boarding','terminales':'terminal','puerta':'gate','puertas':'gate','gates':'gate','equipajes':'baggage','equipaje':'baggage','maletas':'baggage','carga':'cargo','cargamento':'cargo',
 'flota':'fleet','vuelos':'flight','vuelo':'flight','flights':'flight','rutas':'route','ruta':'route','routes':'route','billetes':'ticket','billete':'ticket','boletos':'ticket','boleto':'ticket','tickets':'ticket',
 'mantenimiento':'maintenance','neumatico':'tire','neumaticos':'tire','tires':'tire','tyres':'tire','tyre':'tire','ruedas':'wheel','rueda':'wheel','wheels':'wheel','ingeniero':'engineer','ingenieros':'engineer','hangares':'hangar',
 'gasolina':'fuel','tanques':'tank','tanque':'tank','tanks':'tank','deposito':'tank','depositos':'tank','manguera':'hose','mangueras':'hose','hoses':'hose',
 'costos':'cost','costes':'cost','gastos':'cost','costs':'cost','expenses':'cost','ingresos':'revenue','revenues':'revenue','precios':'price','precio':'price','prices':'price','consumo':'consumption','consumir':'consumption',
 'kilometros':'kilometre','kilometers':'kilometre','kilometres':'kilometre','margenes':'margin','margen':'margin','rentabilidad':'profit','beneficios':'profit','beneficio':'profit',
 'avion comercial':'airliner','hidrogeno':'hydrogen','baterias':'battery','baterias':'battery','batteries':'battery','bateria':'battery','ala':'wing','alas':'wing','wings':'wing'}
_VIS_83_GENERIC=set('aircraft aviation airplane flight airport airline airliner system systems general funcionamiento tecnologia industry industria contexto figure public domain united states photograph aviation aircraft air aircrafts photo picture'.split())
_VIS_83_STRONG=set('fuel refueling truck passenger seat cabin boarding terminal gate baggage cargo fleet ticket route tank hose engine compressor turbine turbofan rotor blade nozzle combustion piston propeller cylinder exhaust tire wheel hangar hydraulic hydrogen battery wing altimeter radar runway taxiway runway landing'.split())
_VIS_83_MILITAR=re.compile(r'\b(?:military|militar|usaf|usn|usmc|raf|royal air force|air force|airman|airmen|navy|army|marine corps|armed forces|defense gov|department of defense|dod|air base|airbase|fighter|combat|squadron|bomber|warplane|kc 135|kc 46|c 130|c 17|c 23b|f 16|f 35|f 18)\b',re.I)
_VIS_83_CIVIL=re.compile(r'\b(?:civil aviation|commerci(?:al|al aviation|al aircraft)|airline|airlines|airliner|airliners|airbus|boeing|embraer|lufthansa|easyjet|ryanair|delta air lines|united airlines|american airlines|air france|klm|latam|jetblue|southwest|passenger aircraft|passenger plane|passenger cabin|passenger terminal|a320|a321|a330|a350|a380|b737|b747|b777|b787|737|747|777|787|airport terminal|commercial airport)\b',re.I)
def _tokens_83(txt):
    base=_curiosity_tokens_visuales(txt)
    return {_VIS_83_EQ.get(w,w) for w in base}

def _metadatos_objeto_83(titulo,meta):
    return str(titulo)+' '+' '.join(limpiar_html(meta.get(k,{}).get('value','')) for k in ('ImageDescription','ObjectName'))

def _score_escena_83(caso,i,evidencia):
    plan=[x for x in caso.get('_plan_visual',[]) if x[0]!='cta']
    if i>=len(plan):return 0,[]
    txt=plan[i][1]
    narr=_tokens_83(txt)-_VIS_83_GENERIC
    met=_tokens_83(evidencia)-_VIS_83_GENERIC
    q=caso.get('_consultas_escenas',[])
    consulta=_tokens_83(q[i])-_VIS_83_GENERIC if i<len(q) else set()
    # Una búsqueda sugerida por IA no prueba el contenido de una foto.
    # Sólo aporta peso si coincide también con lo narrado y los metadatos.
    hits=narr&met; corroborados=hits&consulta; fuertes=hits&_VIS_83_STRONG
    if _es_financiero(caso):
        n=_univ_normalizar(evidencia)
        if _VIS_83_MILITAR.search(n) or not _VIS_83_CIVIL.search(n):return 0,[]
        if not fuertes:return 0,[]
        return 5*len(fuertes)+2*len(corroborados)+len(hits),sorted(hits)
    # Un componente técnico explícito es suficiente con contexto del caso;
    # para conceptos no catalogados todavía se requieren dos coincidencias.
    if len(hits)>=2 or (fuertes and corroborados):
        return 3*len(hits)+2*len(corroborados)+2*len(fuertes),sorted(hits)
    return 0,[]

def _foto_financiera_83(caso,titulo,meta):
    evidencia=_metadatos_objeto_83(titulo,meta)
    n=_univ_normalizar(evidencia)
    if _VIS_83_MILITAR.search(n) or not _VIS_83_CIVIL.search(n):return 0,[]
    plan=[x for x in caso.get('_plan_visual',[]) if x[0]!='cta']
    if not plan:
        return (0,[])  # no selección sin el guion real
    scores=[_score_escena_83(caso,i,evidencia) for i in range(len(plan))]
    maximo=max(scores,key=lambda x:x[0])
    return (maximo[0]+8,maximo[1]) if maximo[0] else (0,[])

def _consultas_visuales_83(caso):
    plan=[x for x in caso.get('_plan_visual',[]) if x[0]!='cta']
    sugeridas=caso.get('_consultas_escenas',[]); salida=[]
    # Buscar sujetos concretos, sin prefijar el título español a cada consulta.
    for i,(_,txt) in enumerate(plan):
        n=_tokens_83(txt); q=str(sugeridas[i]).strip()[:100] if i<len(sugeridas) else ''
        if q and (n&_tokens_83(q))-_VIS_83_GENERIC:
            salida.append(q+(' commercial airline' if _es_financiero(caso) else ' aviation'))
        if _es_financiero(caso):
            for palabra,consulta in [('fuel','commercial airliner jet fuel refueling'),('refueling','airport airline refueling truck'),('seat','commercial airplane passenger cabin seats'),('passenger','commercial airport passenger boarding'),('cargo','airline cargo loading aircraft'),('fleet','commercial airline aircraft airport apron'),('baggage','commercial airport baggage loading'),('tank','commercial aircraft fuel tank')]:
                if palabra in n:salida.append(consulta)
    if _es_financiero(caso):
        if _tema_id_actual(caso)=='fin_05':salida+=['commercial aircraft refueling airport','airliner refueling fuel truck','Lufthansa aircraft refueling','commercial jet aircraft fuel truck']
        else:salida+=['commercial passenger aircraft cabin seats','commercial airline passenger boarding','airline aircraft airport gate']
    return list(dict.fromkeys(salida))

def _ordenar_candidatos_83(caso,candidatos):
    # Cobertura codiciosa: priorizar una foto que cubra una escena aún no cubierta.
    plan=[x for x in caso.get('_plan_visual',[]) if x[0]!='cta']
    if not plan:return sorted(candidatos,key=lambda x:x[0],reverse=True)
    bolsa=[]; cubiertas=set();resultado=[]
    for item in candidatos:
        puntos,titulo,info,*_=item
        evidencia=_metadatos_objeto_83(titulo,info.get('extmetadata') or {})
        scores={i:_score_escena_83(caso,i,evidencia)[0] for i in range(len(plan))}
        bolsa.append((item,{i:v for i,v in scores.items() if v>0}))
    while bolsa:
        j=max(range(len(bolsa)),key=lambda k:(len(set(bolsa[k][1])-cubiertas),max(bolsa[k][1].values(),default=0),bolsa[k][0][0]))
        item,scores=bolsa.pop(j);cubiertas.update(scores);resultado.append(item)
    return resultado

def _huella_foto_83(im):
    from PIL import Image
    pix=list(im.convert('L').resize((9,8),Image.Resampling.LANCZOS).getdata())
    return sum((pix[y*9+x]>pix[y*9+x+1]) << (y*8+x) for y in range(8) for x in range(8))

def _frase_visual_83(txt):
    frases=[f.strip() for f in re.split(r'(?<=[.!?])\s+',txt.strip()) if f.strip()]
    candidatas=[f for f in frases if 25<=len(f)<=190]
    if candidatas:return max(candidatas,key=lambda f:(bool(re.search(r'\b\d',f)),len(_tokens_83(f)&(_VIS_83_STRONG|{'cost','revenue','margin','price','profit','consumption'})),len(f)))
    # Truncamiento explícito para no presentar una cita como una frase completa.
    f=frases[0] if frases else txt
    return f if len(f)<=190 else f[:185].rsplit(' ',1)[0]+'…'

def _self_test_83():
    from tempfile import TemporaryDirectory
    from unittest.mock import patch
    from PIL import Image
    caso=dict(CASOS['fin_05']);caso['_episodio']={'caso_id':'fin_05'}
    caso['_plan_visual']=[('gancho','El combustible de un avión comercial se carga por medio de un camión de repostaje.'),('desarrollo','Los pasajeros ocupan asientos disponibles en la cabina.'),('conclusion','El margen depende de los ingresos y los costos.')]
    caso['_consultas_escenas']=['airliner fuel refueling truck','aircraft passenger cabin seats','airline operating costs']
    for foto in ['File:US Navy aviation fuel aircraft.jpg','File:USAF aircraft refueling truck at Pleiku Air Base.jpg','File:914th Airman defuels aircraft refueling truck.jpg']:
        assert evaluar_relevancia_foto(caso,foto,{},'airline refueling')==(0,[]),foto
    assert evaluar_relevancia_foto(caso,'File:Lufthansa airliner fuel refueling truck.jpg',{},'airline fuel')[0]>0
    assert evaluar_relevancia_foto(caso,'File:Lufthansa commercial passenger cabin seats.jpg',{},'airline passenger')[0]>0
    assert evaluar_relevancia_foto(caso,'File:Commercial airline pilot portrait.jpg',{},'airline fuel')==(0,[])
    assert _score_escena_83(caso,2,'Lufthansa airliner fuel truck')==(0,[])
    with TemporaryDirectory() as td,patch.dict(globals(),{'PUBLICAR_EN_YOUTUBE':False,'AERO_GUIONES_DIR':Path(td)/'guiones'}):
        root=Path(td); fotos=[root/'fuel.jpg',root/'seat.jpg']
        for f in fotos:Image.new('RGB',(800,600),'#102030').save(f)
        creditos=[{'titulo':'Lufthansa airliner fuel refueling truck','objeto_visual':''},{'titulo':'Lufthansa commercial passenger cabin seats','objeto_visual':''}]
        _curiosity_asignar_escenas(caso,fotos,creditos,root)
        assert Path(caso['_mapa_visual'][0])==fotos[0]
        assert Path(caso['_mapa_visual'][1])==fotos[1]
        assert Path(caso['_mapa_visual'][2]).name.startswith('tarjeta_contextual_')
        assert _guion_cache_cargar({'id':'x'},caso) is None
        # Cache round-trip of stored, already validated structure; production
        # validation is tested by the inherited self-tests.
        ep={'id':'fin_05','titulo':'¿Por qué cuesta tanto el combustible de una aerolínea?'}
        c=dict(caso,_titulo_caso='Por qué el combustible pesa en las cuentas',titulo=ep['titulo'])
        doc={'id':'F1','nombre':'Fuente simulada','url':'https://example.com/report','texto':'Airline fuel costs and jet fuel expenses affect airline operating costs. '*6}
        base=[('conclusion','La relación entre costos e ingresos explica el margen.')]
        with patch.dict(globals(),{'_validar_guion_ia':lambda *a:list(base),'MODO_VIRAL':False}):
            plan=base+[('cta','Si te gustó este contenido, dale Like y Suscríbete! Muchas gracias por tu visita y nos vemos en un próximo video!')]
            (root/'GUION_IA.json').write_text(json.dumps({'resultado':{'bloques':[]}}))
            _guion_cache_guardar(ep,c,[doc],plan,root)
            assert _guion_cache_cargar(dict(ep),dict(c))[1]==plan
    rask=dict(CASOS['fin_03']);rask['_episodio']={'caso_id':'fin_03'}
    assert _aero_documento_relevante('Key performance indicator for air transport. Unit revenue (RASK) denotes the revenue divided by available seat-kilometres. '*3,rask)>0
    assert _aero_documento_relevante('Generic flight airport pilots aviation aircraft engines. '*6,rask)==0
    print('OK: finanzas civiles, asignación contextual, RASK y recuperación de guiones aprobados')

def _self_test_84():
    from unittest.mock import patch
    tipos=['gancho','pregunta','contexto','pista','analisis','desarrollo','aplicacion','conclusion']
    citas=['Hydrogen aircraft use alternative propulsion technologies.',
           'Liquid hydrogen requires dedicated storage and handling infrastructure.',
           'Certification requires assessment of the aircraft systems.']
    palabras=['hidrógeno','almacenamiento','propulsión','infraestructura','seguridad','certificación','operaciones','balance']
    # Fixture artificial únicamente para verificar la barrera de palabras.
    bloques=[{'tipo':t,'texto':' '.join([w+str(j) for j in range(50 if i<5 else 49)])} for i,(t,w) in enumerate(zip(tipos,palabras))]
    datos={'bloques':bloques,'hechos_con_evidencia':[{'fuente_id':'F1','cita_textual':c,'afirmacion':'Afirmación documental de prueba número '+str(i)} for i,c in enumerate(citas)]}
    docs=[{'id':'F1','texto':' '.join(citas)}]
    assert sum(len(b['texto'].split()) for b in bloques)==397
    with patch.dict(globals(),{'AERO_PALABRAS_MIN':440,'AERO_PALABRAS_MIN_ACEPTABLE':235,'AERO_PALABRAS_MAX':780,'AERO_IA_MIN_DATOS':3}):
        assert len(_validar_guion_ia(datos,docs,{}))==8
        import copy
        malo=copy.deepcopy(datos);malo['hechos_con_evidencia'][0]['cita_textual']='Cita inventada que no figura en el documento original.'
        try:_validar_guion_ia(malo,docs,{})
        except ValueError:pass
        else:raise AssertionError('No debe aceptar una cita inventada')
        corto=copy.deepcopy(datos)
        for b in corto['bloques']:b['texto']=' '.join(b['texto'].split()[:20])
        try:_validar_guion_ia(corto,docs,{})
        except ValueError:pass
        else:raise AssertionError('No debe aceptar un guion inferior al mínimo absoluto')
    print('OK: guion de 397 palabras aceptado; citas inventadas y guiones demasiado cortos rechazados')

if __name__=='__main__':
    print(f'AEROFACTUM UNIVERSAL {VERSION_SCRIPT} | Nicho: {NICHO}',flush=True)
    if '--self-test' in sys.argv:
        prueba_interna()
        _self_test_8()
        _self_test_81()
        _self_test_83()
        _self_test_84()
        from unittest.mock import patch
        with patch.dict(globals(),{'NICHO':'Astronomía'}):
            ejemplo={'id':'prueba','titulo':'Agujeros negros','_universal':True,'_titulo_caso':'Agujeros negros'}
            assert _aero_documento_relevante('Los agujeros negros concentran masa en regiones del espacio. '*10,ejemplo)>0
            assert _aero_documento_relevante('Aeronaves, terminales, aeropuertos y vuelos comerciales. '*10,ejemplo)==0
            assert evaluar_relevancia_foto(ejemplo,'File:Black holes agujeros negros photo.jpg',{},'agujeros negros')[0]>0
        print('OK: nicho universal, documentación y recursos visuales sin restricciones aeronáuticas')
    elif '--auth-init' in sys.argv:
        iniciar_oauth_local()
    elif '--check-auth' in sys.argv:
        validar_canal_youtube(youtube_servicio())
    elif '--analytics' in sys.argv:
        _viral_consultar_historico_analytics()
    elif '--check-ia' in sys.argv:
        if not (os.getenv('GEMINI_API_KEY') or os.getenv('GROQ_API_KEY') or os.getenv('OPENROUTER_API_KEY')):
            raise RuntimeError('Configura GEMINI_API_KEY, GROQ_API_KEY u OPENROUTER_API_KEY en GitHub Secrets.')
        print('Motores configurados:', ', '.join(k for k,e in [
            ('Gemini',os.getenv('GEMINI_API_KEY')),('Groq',os.getenv('GROQ_API_KEY')),
            ('OpenRouter',os.getenv('OPENROUTER_API_KEY'))] if e))
    else:
        if PUBLICAR_EN_YOUTUBE and not AERO_IA_DRY_RUN and not CREAR_VISTA_PREVIA:
            asegurar_dependencias()
            _previos=_cola_reanudar(ruta_historial(),VIDEOS_POR_EJECUCION)
            if _previos is None:
                _univ_activar_catalogo()
                ejecutar()
        else:
            _univ_activar_catalogo()
            ejecutar()
