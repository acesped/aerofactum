# -*- coding: utf-8 -*-
"""
AEROFACTUM 3.0 · GitHub Actions + YouTube @aerofactum · MOTOR ORIGINAL MISTERIO CIENCIA · UNA SOLA CELDA DE COLAB / PYTHON
Motor audiovisual original de MISTERIO CIENCIA adaptado a 100 temas aeronáuticos,
Ken Burns cinematográfico, voz Edge TTS, subtítulos ASS y música original de π.
Ninguna API de pago. CPU. Sin fotografías inventadas por IA.

Ejecución: python aerofactum.py. En GitHub Actions, ejecución cron automatizada.
"""
import os,sys,subprocess,importlib.util,random,re,json,math,time,asyncio,threading,html,shutil,wave,hashlib
from pathlib import Path
from urllib.parse import urlparse
from datetime import datetime, timezone

# ==================== CONFIGURACIÓN EDITABLE ====================
TEMA = os.getenv('AERO_TEMA', 'aleatorio')       # caso específico o 'aleatorio'; por defecto no repite episodios
VOZ = 'es-CL-LorenzoNeural'  # voz fija para TODOS los segmentos de narración
VELOCIDAD = '+10%'  # ritmo más ágil, sin acelerar el audio después de sintetizarlo
SALIDA_EN_DRIVE = os.getenv('GITHUB_ACTIONS', '').lower() != 'true'
CREAR_VISTA_PREVIA = os.getenv('AERO_PREVIEW', 'false').lower() == 'true'      # True = solo miniatura + fotogramas de muestra, sin TTS
VIDEOS_POR_EJECUCION = int(os.getenv('AERO_VIDEOS_POR_EJECUCION', '1'))       # 1 por defecto; hasta 100 temas únicos
EVITAR_REPETICIONES = True     # requiere historial en Drive para persistir entre sesiones
REINICIAR_CATALOGO_AL_AGOTAR = False
FOTOGRAMAS_POR_SEGUNDO = 15
ANCHO, ALTO = 1920, 1080        # render nativo Full HD para exportación 1080p real
IMAGENES_MINIMAS = 4            # objetivo visual; buscará imágenes adicionales si faltan
IMAGENES_MINIMAS_ABSOLUTAS = 1 # mínimo de fotografías auténticas; si no hay, detener (sin esquemas)
MAX_IMAGENES = 10
VERIFICACION_OBLIGATORIA = False # si True, detiene cuando no hay referencias oficiales accesibles
OUTPUT_BASE = Path(os.getenv('AERO_OUTPUT_DIR', '/content/AEROFACTUM' if Path('/content').exists() else 'output/AEROFACTUM'))
MUSICA_VOLUMEN = 0.065  # más presencia, con limitador final para evitar clipping
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
        limite='Este contenido es educativo. No sustituye manuales aprobados, procedimientos del operador, cálculos de performance ni requisitos regulatorios aplicables.',
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

def plan_guion_episodio(caso,episodio):
    """Guion educativo sobre el tema concreto, no una historia de misterio reciclada."""
    t=caso['_titulo_caso']; idea=caso['contexto']; cat=caso['categoria']
    observacion,pregunta=ENFOQUE_CATEGORIA[cat]
    # Una frase específica por tema es el núcleo de la explicación.
    return [
        ('gancho',f'¿Qué debería saber un aviador sobre {t.lower()}? Hay una explicación técnica detrás de este concepto, y entenderla importa.'),
        ('pregunta',caso['pregunta']),
        ('contexto',f'Empecemos por la idea central. {idea}'),
        ('pista',f'Para interpretarlo correctamente, hay que situarlo en su ámbito: {cat.lower()}. {observacion}'),
        ('analisis',f'Esta es una pregunta útil para estudiar el tema: {pregunta} La respuesta específica cambia según el equipo, el tipo de operación y la documentación correspondiente.'),
        ('evidencia',f'El dato clave que debemos conservar es el siguiente. {idea} Este principio no reemplaza los valores, tablas o limitaciones de un modelo concreto.'),
        ('aplicacion',f'¿Para qué sirve aprenderlo? {caso["importancia"]} Conviene contrastarlo con un manual vigente o una publicación técnica de la autoridad competente.'),
        ('limites',caso['limite']),
        ('conclusion',f'En resumen, {idea} Consulta las referencias oficiales indicadas en la descripción y comprueba sus ediciones vigentes. AEROFACTUM: el conocimiento detrás de cada vuelo.'),
        ('cta','Si aprendiste algo útil, dale Like y comparte. Suscríbete a AEROFACTUM para seguir explorando la industria aeronáutica.'),
    ]

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
    faltantes=[paquete for modulo,paquete in [('PIL','Pillow>=10.0'),('requests','requests>=2.31'),('edge_tts','edge-tts>=6.1'),('numpy','numpy>=1.24'),('cairosvg','CairoSVG>=2.7')] if importlib.util.find_spec(modulo) is None]
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
    meta=info.get('extmetadata') or {}
    nombre=limpiar_html(meta.get('LicenseShortName',{}).get('value','')).lower()
    terminos=limpiar_html(meta.get('UsageTerms',{}).get('value','')).lower()
    link=limpiar_html(meta.get('LicenseUrl',{}).get('value','')).lower()
    texto=' '.join([nombre,terminos,link])
    if any(x in texto for x in ['noncommercial','non-commercial','no derivatives','no-derivatives','cc-by-nc','cc-by-nd','cc by-nc','cc by-nd']):return False
    return any(x in texto for x in ['public domain','cc0','cc by','cc-by','creativecommons.org/licenses/by/','creativecommons.org/publicdomain','pd-old','pd-us','public-domain'])

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

def evaluar_relevancia_foto(caso, titulo, metadata, busqueda):
    """Puntúa coincidencias del CASO en título o descripción/categorías.
    Nunca se asigna una imagen sólo porque apareció en una búsqueda amplia.
    """
    titulo_n=_normalizar_texto_foto(titulo.replace('File:',''))
    metatexto=' '.join(limpiar_html(metadata.get(k,{}).get('value',''))
                       for k in ('ImageDescription','ObjectName','Categories'))
    meta_n=_normalizar_texto_foto(metatexto[:18000])
    anclas=_anclas_visuales(caso)
    directas=anclas.intersection(set(titulo_n.split()))
    extras=anclas.intersection(set(meta_n.split()))
    # La coincidencia de título importa 3 veces más que un término disperso
    # en la descripción. No puntuar por coincidir con palabras vagas.
    puntos=3*len(directas)+len(extras)
    consulta=_tokens_visuales(busqueda)
    coincidencias_consulta=consulta.intersection(set(titulo_n.split()))
    puntos+=len(coincidencias_consulta)
    # Impedir aceptación por palabras únicas genéricas.
    # Título que menciona solo 'aircraft' no basta; usar dos anclas concretas.
    relevantes=(directas|extras)
    if len(relevantes)<2:
        return 0, []
    if not directas and len(extras)<3:
        return 0, []
    if puntos<4:
        return 0, []
    return puntos, sorted(directas|extras)

def buscar_fotos(caso,session,carpeta):
    from PIL import Image,ImageOps
    from io import BytesIO
    fotos=[];creditos=[];hashes=set();descartes=[]
    queries=_consultas_fotos(caso)
    # Sólo consultas ancladas al caso concreto, NUNCA búsquedas genéricas
    # como «science research laboratory equipment».
    principal=caso.get('_titulo_caso',caso['titulo']).split(':')[0].strip()
    # Las consultas específicas y contextuales ya las aporta _consultas_fotos.
    caso_id=(caso.get('_episodio') or {}).get('caso_id','')
    # Consultas de respaldo dirigidas al fenómeno, NO a temas científicos genéricos.
    queries=list(dict.fromkeys(queries))
    api='https://commons.wikimedia.org/w/api.php'
    candidatos=[];titulos_vistos=set()
    for busqueda in queries:
        try:
            params=dict(action='query',format='json',generator='search',
                        gsrsearch=busqueda,gsrnamespace=6,gsrlimit=24,
                        prop='imageinfo',iiprop='url|extmetadata',iiurlwidth=2200)
            resp=session.get(api,params=params,timeout=30,
                             headers={'User-Agent':'Aerofactum/2.2 (topic image validation)'})
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
            print('  Búsqueda Commons falló:',busqueda,'|',str(exc)[:110])
    candidatos.sort(key=lambda item:item[0],reverse=True)
    for puntos,archivo,info,url,matches,busqueda in candidatos:
        if len(fotos)>=MAX_IMAGENES:break
        try:
            r=session.get(url,timeout=35,
                          headers={'User-Agent':'Aerofactum/2.2 (educational media retrieval)'})
            r.raise_for_status()
            if len(r.content)>22_000_000:continue
            im=Image.open(BytesIO(r.content))
            im=ImageOps.exif_transpose(im).convert('RGB')
            if min(im.size)<600:continue
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
                'uso':'Fotografía documental de contexto; puede no retratar exactamente el caso descrito'
            })
            fotos.append(destino)
            print('  Aprobada:',archivo[:65], '| puntuación:',puntos,'|',','.join(matches[:5]))
        except Exception as exc:
            descartes.append({'archivo':archivo,'razon':'No descargable o baja resolución: '+str(exc)[:100]})
    (carpeta/'creditos_imagenes.json').write_text(
        json.dumps(creditos,ensure_ascii=False,indent=2),encoding='utf-8')
    (carpeta/'imagenes_descartadas.json').write_text(
        json.dumps(descartes[:300],ensure_ascii=False,indent=2),encoding='utf-8')
    with (carpeta/'CREDITOS_Y_LICENCIAS.txt').open('w',encoding='utf-8') as f:
        f.write('Fotografías reales de Wikimedia Commons: se excluyen esquemas, ilustraciones, mapas, renders y gráficos por metadatos.\n')
        f.write('Comprobar pertinencia, licencias y atribución antes de publicar.\n\n')
        for c in creditos:
            f.write(f"{c['archivo']} | {c['titulo']} | Relevancia {c['puntuacion_relevancia']} | {','.join(c['terminos_relacionados'])} | Autor: {c['autor']} | Licencia: {c['licencia']} | {c['licencia_url']} | {c['pagina']}\n")
    if len(fotos) < IMAGENES_MINIMAS_ABSOLUTAS:
        aviso=(f'No se encontró ninguna FOTOGRAFÍA REAL pertinente y con licencia compatible para «{principal}». '
               'Se excluyeron diagramas, ilustraciones, imágenes generadas por ordenador, mapas y esquemas. '
               'No se producirá el video con imágenes no fotográficas. '
               'Consulta imagenes_descartadas.json y prueba otro tema o mejora sus términos visuales.')
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
    trozos.append(('evidencia','Repasemos lo que sí puede comprobarse. '+' '.join('Pista número '+str(i+1)+': '+x+'.' for i,x in enumerate(caso['hechos']))))
    trozos.append(('limites',caso['limite']))
    trozos.append(('significado',caso['importancia']))
    trozos.append(('conclusion',caso['cierre']+' ¿Qué otra pregunta aeronáutica te gustaría investigar? Te leo en los comentarios.'))
    trozos.append(('cta','Si te gustó este fascinante tema, dale like y suscríbete para seguir recibiendo esta interesante información'))
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

def generar_voces(plan,carpeta):
    import edge_tts
    async def tarea():
        bloques=[];cues=[];posicion_muestras=0;salida=carpeta/'narracion.wav';sample_rate=24000
        with wave.open(str(salida),'wb') as final:
            final.setnchannels(1);final.setsampwidth(2);final.setframerate(sample_rate)
            for i,(tipo,texto) in enumerate(plan):
                audio=bytearray();marcas=[]
                # Motor Edge TTS con reintentos; SIEMPRE la misma voz (Lorenzo).
                error_tts=None
                for intento in range(1, 5):
                    voz_actual = VOZ  # nunca usar voces alternativas
                    audio.clear();marcas.clear()
                    try:
                        tts=edge_tts.Communicate(texto,voice=voz_actual,rate=VELOCIDAD)
                        async for dato in tts.stream():
                            if dato['type']=='audio':audio.extend(dato['data'])
                            elif dato['type']=='WordBoundary':marcas.append((dato['text'],dato['offset']/1e7,dato['duration']/1e7))
                        if not audio:raise RuntimeError('Edge TTS devolvió un segmento vacío')
                        if intento>1:print(f'  Narración recuperada en intento {intento}: {voz_actual}',flush=True)
                        break
                    except Exception as e:
                        error_tts=e
                        print(f'  Aviso TTS voz {i+1}, intento {intento}: {type(e).__name__}: {e}',flush=True)
                        if intento<4:await asyncio.sleep(2*intento)
                if not audio:
                    raise RuntimeError(f'No se pudo sintetizar el bloque {i+1} tras cuatro intentos. Último error: {error_tts}')
                mp3=carpeta/f'voz_{i:02}.mp3';mp3.write_bytes(audio)
                wav=carpeta/f'voz_{i:02}.wav'
                subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(mp3),'-ac','1','-ar',str(sample_rate),'-c:a','pcm_s16le',str(wav)],check=True)
                with wave.open(str(wav),'rb') as individual:
                    n=individual.getnframes();final.writeframes(individual.readframes(n))
                inicio=posicion_muestras/sample_rate;dur=n/sample_rate
                bloques.append(dict(tipo=tipo,texto=texto,inicio=inicio,duracion=dur))
                # Las marcas vienen del MISMO segmento de audio y se desplazan al inicio global.
                # La escena final CTA mantiene locución, pero NO subtítulos en pantalla,
                # para no entorpecer la lectura del texto fijo de la imagen.
                if tipo!='cta':
                    if marcas:
                        grupo=[];comienzo=0;fin=0
                        for palabra,offset,duracion in marcas:
                            if not grupo:comienzo=offset
                            grupo.append(palabra.strip());fin=offset+max(.09,duracion)
                            if len(grupo)>=7 or fin-comienzo>2.5:
                                cues.append((inicio+comienzo,inicio+min(dur,fin),' '.join(grupo)));grupo=[]
                        if grupo:cues.append((inicio+comienzo,inicio+min(dur,fin),' '.join(grupo)))
                    else:
                        palabras=texto.split();grupos=max(1,math.ceil(len(palabras)/7))
                        for j in range(grupos):
                            cues.append((inicio+dur*j/grupos,inicio+dur*(j+1)/grupos,' '.join(palabras[j*7:(j+1)*7])))
                posicion_muestras+=n
                print(f'  Voz {i+1:02}/{len(plan)}: {dur:.1f}s',flush=True)
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
def subtitulos(cues,carpeta, inicio_cta=None):
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

# ======================== MÚSICA π ==============================
def mezclar_pi(voz,carpeta):
    import numpy as np
    with wave.open(str(voz),'rb') as w:
        sr=w.getframerate();raw=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(np.float32)/32768.
    result=raw.copy();notas={'1':261.63,'2':293.66,'3':329.63,'4':349.23,'5':392.00,'6':440.00,'7':493.88}
    digitos='1415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679'
    paso=int(sr*.55)
    for j,desde in enumerate(range(0,len(raw),paso)):
        hz=notas.get(digitos[j%len(digitos)])
        if not hz:continue
        n=min(paso,len(raw)-desde);t=np.arange(n,dtype=np.float32)/sr
        env=np.minimum(1,t/.04)*np.minimum(1,np.maximum(0,(n/sr-t)/.14))
        result[desde:desde+n]+=MUSICA_VOLUMEN*env*(np.sin(2*np.pi*hz*t)+.15*np.sin(4*np.pi*hz*t))
    destino=carpeta/'voz_musica_pi.wav'
    with wave.open(str(destino),'wb') as f:
        f.setnchannels(1);f.setsampwidth(2);f.setframerate(sr)
        f.writeframes((np.clip(result,-.97,.97)*32767).astype('<i2').tobytes())
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
    return promesas.get(cat,'EL DATO QUE TODO AVIADOR DEBE CONOCER')

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
    destino=carpeta/'miniatura.jpg'
    im.convert('RGB').save(destino,quality=96,optimize=True,subsampling=0)
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
    from PIL import Image,ImageDraw,ImageFont
    tarjeta=Image.new('RGB',(ANCHO,ALTO),'#000000')
    d=ImageDraw.Draw(tarjeta)
    d.rounded_rectangle((120,760,1800,1015),radius=42,fill=(15,22,34),outline=(255,255,255),width=3)
    f=cargar_fuente(132)
    escribir_en_caja(d,'Dale Like y Suscríbete!',(170,790,1750,995),f,'#FFFFFF',2,interlinea=1.0,stroke_width=4,stroke_fill='#0A1423',centrar_vertical=True)
    ruta=carpeta/'cta_bg.png'; tarjeta.save(ruta)
    return ruta

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
        num_planos=1 if b['tipo']=='cta' else max(1,math.ceil(frames_escena/(fps*11)))
        cortes=[round(j*frames_escena/num_planos) for j in range(num_planos+1)]
        for plano in range(num_planos):
            frames=cortes[plano+1]-cortes[plano]
            if frames<=0:continue
            if b['tipo']!='cta':
                # No usar siempre las mismas fotografías para dos planos consecutivos.
                foto=fotos[(numero+(i//2))%len(fotos)]
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
    concat=carpeta/'clips.ffconcat'
    concat.write_text('ffconcat version 1.0\n'+''.join("file '"+str(c).replace("'","'\\''")+"'\n" for c in clips),encoding='utf-8')
    unido=carpeta/'video_sin_subtitulos.mp4'
    ffmpeg(['ffmpeg','-y','-hide_banner','-loglevel','error','-safe','0','-f','concat','-i',str(concat),'-c','copy',str(unido)])
    return unido

def finalizar_video(video,audio,ass,carpeta):
    # Escalado FullHD en una sola codificación final; burn-in ASS sobre 1920x1080.
    salida=carpeta/'AEROFACTUM.mp4';dur=tiempo_medio_audio(audio)
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


def descripcion_youtube(caso,fuentes,creditos):
    """Créditos de fotografías dentro de YouTube, no solo en archivos locales."""
    parrafos=[
        f"{caso['titulo']} | AEROFACTUM",
        '',
        'Conocimientos técnicos, financieros y operacionales de la industria aeronáutica.',
        'Material divulgativo. No sustituye documentación aeronáutica aprobada, procedimientos ni normas vigentes.',
        'REVISIÓN TÉCNICA DE CONTENIDO PENDIENTE: contrasta cada afirmación con manuales y fuentes vigentes.',
        '', 'FUENTES DE REFERENCIA (no constituyen verificación individual de afirmaciones):']
    for f in fuentes:
        parrafos.append(f"- {f.get('nombre','Fuente')}: {f.get('url','')}")
    parrafos += ['', 'FOTOGRAFÍAS Y CRÉDITOS (Wikimedia Commons):']
    for c in creditos:
        parrafos.append(f"- {c.get('titulo','Foto')} · Autor: {c.get('autor','No indicado')} · {c.get('licencia','Licencia')} · {c.get('pagina','')} · {c.get('licencia_url','')}")
    parrafos+=['','#AEROFACTUM #Aviación #Pilotos #SeguridadAérea']
    texto='\n'.join(parrafos).replace('\\n','\n')
    if len(texto)>4900:
        # No perder atribuciones: impedir publicar antes que recortar créditos obligatorios.
        raise RuntimeError('La descripción y créditos superan el límite seguro de YouTube (4900 caracteres). Revisar metadatos.')
    return texto


def escribir_registro_publicacion(historial,episodio,caso,video_id,carpeta,estado):
    datos=leer_historial(historial)
    existente=next((r for r in datos if r.get('episodio')==episodio['id']),None)
    if existente is None:
        existente={'episodio':episodio['id'],'caso':episodio['caso_id'],
                   'titulo':episodio['titulo'],'fecha_utc':datetime.now(timezone.utc).isoformat()}
        datos.append(existente)
    existente.update(youtube_id=video_id, youtube_url='https://www.youtube.com/watch?v='+video_id,
                     youtube_estado=estado, salida=str(carpeta/'AEROFACTUM.mp4'))
    historial.parent.mkdir(parents=True,exist_ok=True)
    temp=historial.with_suffix('.tmp')
    temp.write_text(json.dumps(datos,ensure_ascii=False,indent=2),encoding='utf-8')
    temp.replace(historial)
    (carpeta/'PUBLICACION_YOUTUBE.json').write_text(json.dumps(existente,ensure_ascii=False,indent=2),encoding='utf-8')
    return existente


def publicar_youtube(video,miniatura,srt,caso,episodio,fuentes,creditos,carpeta,historial):
    from googleapiclient.http import MediaFileUpload
    if YOUTUBE_PRIVACY not in ('private','unlisted','public'):
        raise ValueError('YOUTUBE_PRIVACY debe ser private, unlisted o public.')
    if YOUTUBE_PRIVACY!='private' and not PERMITIR_PUBLICACION_SIN_REVISION:
        raise RuntimeError('No se permitirá difusión pública/no listada de contenido sin revisión: activa ALLOW_UNREVIEWED_PUBLICATION=true tras revisar el sistema.')
    # Verificar créditos y longitud antes de iniciar la subida.
    descripcion_validada=descripcion_youtube(caso,fuentes,creditos)
    servicio=youtube_servicio()
    validar_canal_youtube(servicio)
    titulo=caso['titulo'][:100]
    cuerpo={'snippet':{'title':titulo,
         'description':descripcion_validada,
         'categoryId':'28','defaultLanguage':'es',
         'tags':['AEROFACTUM','aviacion','aeronautica',caso['categoria'][:35]]},
         'status':{'privacyStatus':YOUTUBE_PRIVACY,'selfDeclaredMadeForKids':False}}
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
        servicio.thumbnails().set(videoId=video_id,
            media_body=MediaFileUpload(str(miniatura),mimetype='image/jpeg')).execute()
        print('Miniatura personalizada subida correctamente.',flush=True)
    except Exception as e:
        errores.append('miniatura: '+str(e)[:500])
        print('AVISO: falló la miniatura; el video ya existe:',e,flush=True)
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
    return video_id

# ====================== METADATOS Y PUBLICACIÓN ===================
def guardar_metadatos(caso,bloques,fuentes,creditos,carpeta):
    contenido='\n'.join(f"{i+1}. {b['texto']}" for i,b in enumerate(bloques))
    (carpeta/'GUION_COMPLETO.txt').write_text(contenido,encoding='utf-8')
    desc=(caso['titulo']+'\n\nAEROFACTUM explica conocimientos técnicos, operacionales y económicos de la aviación. '
          'Material educativo: no sustituye documentación aprobada ni normativa vigente.\n\n'
          'Bibliografía orientativa (se debe verificar cada afirmación con la edición y sección aplicable):\n'+
          '\n'.join(f"- {x['nombre']}: {x['url']} (accesibilidad: {x['status']}; hechos aún por contrastar)" for x in fuentes)+
          '\n\nCréditos de imágenes: CREDITOS_Y_LICENCIAS.txt y creditos_imagenes.json.\n'
          'ESTADO EDITORIAL: REVISIÓN TÉCNICA PENDIENTE ANTES DE PUBLICAR.\n'
          '#Aerofactum #Aviación #Pilotos #IndustriaAeronáutica #SeguridadAérea')
    (carpeta/'TITULO_Y_DESCRIPCION.txt').write_text(desc,encoding='utf-8')
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
    fuentes=verificar_fuentes(caso,sesion,carpeta)
    print('Buscando fotos con atribución y licencias abiertas...')
    fotos,creditos=buscar_fotos(caso,sesion,carpeta)
    (carpeta/'RESUMEN_RECURSOS_VISUALES.txt').write_text(
        f'Recursos visuales: {len(fotos)}\nFotografías reales de Wikimedia: {sum(1 for c in creditos if c.get("url_original"))}\nDiagramas e ilustraciones: 0\nObjetivo editorial: {IMAGENES_MINIMAS}\n'
        + ('ADVERTENCIA: Revisar variedad visual y relevancia temática antes de publicar.\n' if len(fotos)<IMAGENES_MINIMAS else 'Cantidad objetivo alcanzada.\n'),
        encoding='utf-8')
    thumb=miniatura(caso,fotos,carpeta)
    (carpeta/'episodio.json').write_text(json.dumps(episodio,ensure_ascii=False,indent=2),encoding='utf-8')
    if CREAR_VISTA_PREVIA:
        print('Vista previa:',thumb)
        guardar_drive(carpeta)
        return thumb
    plan=plan_guion_episodio(caso,episodio)
    print('Produciendo narración...')
    bloques,cues,voz=generar_voces(plan,carpeta)
    print('Duración narrada:',round(tiempo_medio_audio(voz)/60,2),'minutos')
    inicio_cta=next((b['inicio'] for b in bloques if b['tipo']=='cta'),None)
    srt,ass=subtitulos(cues,carpeta,inicio_cta=inicio_cta)
    audio=mezclar_pi(voz,carpeta)
    guardar_metadatos(caso,bloques,fuentes,creditos,carpeta)
    print('Montaje fotográfico con movimiento cinematográfico...')
    base=renderizar_clips(bloques,fotos,caso,carpeta)
    video=finalizar_video(base,audio,ass,carpeta)
    guardar_drive(carpeta)
    if PUBLICAR_EN_YOUTUBE:
        publicar_youtube(video,thumb,srt,caso,episodio,fuentes,creditos,carpeta,historial)
    else:
        anotar_historial(historial,dict(episodio=episodio['id'],caso=episodio['caso_id'],
            titulo=episodio['titulo'],fecha_utc=datetime.now(timezone.utc).isoformat(),salida=str(video)))
    print('\nFINALIZADO\nVideo:',video,'\nMiniatura:',thumb,'\nSubtítulos:',srt)
    return video

def ejecutar():
    asegurar_dependencias()
    historial=ruta_historial()
    cantidad=int(VIDEOS_POR_EJECUCION)
    if cantidad<1 or cantidad>len(CATALOGO_AERONAUTICO):raise ValueError('VIDEOS_POR_EJECUCION debe estar entre 1 y '+str(len(CATALOGO_AERONAUTICO))+'.')
    if PUBLICAR_EN_YOUTUBE:
        if YOUTUBE_PRIVACY!='private' and not PERMITIR_PUBLICACION_SIN_REVISION:
            raise RuntimeError('Publicación pública requiere ALLOW_UNREVIEWED_PUBLICATION=true tras revisión editorial.')
        validar_canal_youtube(youtube_servicio())
    elegidos=elegir_episodios(cantidad,historial)
    usados=len({x.get('episodio') for x in leer_historial(historial)})
    print(f'Catálogo: {len(CATALOGO_AERONAUTICO)} temas aeronáuticos únicos en {len(ENFOQUE_CATEGORIA)} áreas.')
    print('Generados anteriormente:',usados,'| Seleccionados para esta ejecución:',len(elegidos))
    print('Selección aleatoria:',', '.join(e['id'] for e in elegidos))
    resultados=[]
    for i,episodio in enumerate(elegidos,1):
        print(f'\n====== VIDEO {i} DE {cantidad} ======',flush=True)
        resultados.append(producir_episodio(episodio,historial))
    return resultados

if __name__=='__main__':
    if '--auth-init' in sys.argv:
        iniciar_oauth_local()
    elif '--check-auth' in sys.argv:
        validar_canal_youtube(youtube_servicio())
    else:
        ejecutar()
