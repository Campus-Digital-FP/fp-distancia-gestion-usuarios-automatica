def creaEmailsDominio(nombre, pape, sape, documento):
    """
    Creamos un email para los estudiantes a partir de su nombre, apellidos y documento
    """
    
    nombre = nombre.lower()
    nombre = nombre.replace(' ', '')
    nombre = eliminar_tildes_y_enes(nombre)

    pape = pape.lower()
    pape = pape.replace(' ', '')
    pape = eliminar_tildes_y_enes(pape)
    
    sape = sape.lower()
    sape = sape.replace(' ', '')
    sape = eliminar_tildes_y_enes(sape)
    
    documento = documento.lower()
    documento = documento.replace(' ', '')

    palabras = nombre.split()
    iniciales = ''.join([palabra[0] for palabra in palabras])

    return iniciales + pape + sape + documento[-1]

def eliminar_tildes_y_enes(texto):
    
    texto = texto.replace("ñ", "n").replace("Ñ", "N")
    texto = texto.replace("á", "a").replace("Á", "A")
    texto = texto.replace("é", "e").replace("É", "E")
    texto = texto.replace("í", "i").replace("Í", "I")
    texto = texto.replace("ó", "o").replace("Ó", "O")
    texto = texto.replace("ú", "u").replace("Ú", "U")
    texto = texto.replace("ü", "u").replace("Ü", "U")

    
    return texto

def conversionLOFPaLOE(idMateria):
    """
    Dado un idMateria se verifica si existe em LOFP y si existe se devuelve su equivalente en LOE.
    Si no existe en LOFP se considera que ya nos han pasado el LOE y se devuelve tal cual
    """
    print("conversionLOFPaLOE(",idMateria, ")")

    ####################
    # ADG201 - Gestión Administrativa 
    ####################
    if idMateria == "14634": # Comunicación empresarial y atención al cliente
        return "5364"
    elif idMateria == "14638": # Empresa y Administración
        return "5114"
    elif idMateria == "14640": # Inglés profesional (GM)
        return "5111"
    elif idMateria == "14642": # Itinerario personal para la empleabilidad I
        return "5373" # FOL
    elif idMateria == "14644": # Operaciones administrativas de compra-venta
        return "5365"
    elif idMateria == "14646": # Técnica contable
        return "5368"
    elif idMateria == "14649": # Tratamiento informático de la información
        return "5367"
    elif idMateria == "14653": # Empresa en el aula
        return "5119"
    #elif idMateria == "14655": # Itinerario personal para la empleabilidad II
    #    return ""
    #elif idMateria == "14657": # Módulo profesional optativo
    #    return ""
    elif idMateria == "14659": # Operaciones administrativas de recursos humanos
        return "5117"
    elif idMateria == "14661": # Operaciones auxiliares de gestión de tesorería
        return "5120"
    elif idMateria == "14663": # Proyecto intermodular
        return ""
    elif idMateria == "14665": # Sostenibilidad aplicada al sistema productivo
        return ""
    elif idMateria == "14667": # Tratamiento de la documentación contable
        return "5118"
    
    ####################
    # ADG301 - Administración y Finanzas
    ####################
    if idMateria == "14672": # Comunicación y atención al cliente
        return "5297"
    elif idMateria == "14677": # Gestión de la documentación jurídica y empresarial
        return "5194"
    elif idMateria == "14679": # Inglés profesional
        return "5193"
    elif idMateria == "14681": # Itinerario personal para la empleabilidad I
        return "5403" # FOL
    elif idMateria == "14683": # Ofimática y proceso de la información
        return "5295"
    elif idMateria == "14685": # Proceso integral de la actividad comercial
        return "5296"
    elif idMateria == "14687": # Recursos humanos y responsabilidad social corporativa
        return "5294"
    elif idMateria == "14690": # Contabilidad y fiscalidad
        return "5101"
    elif idMateria == "14692": # Gestión de recursos humanos
        return "5099"
    elif idMateria == "14695": # Gestión financiera
        return "5100"
    elif idMateria == "14697": # Gestión logística y comercial
        return "5148"
#    elif idMateria == "14700": # Itinerario personal para la empleabilidad II
#        return ""
#    elif idMateria == "14702": # Módulo profesional optativo
#        return ""
    elif idMateria == "14704": # Proyecto intermodular de administración y finanzas
        return "5150" # Proyecto de administración y finanzas
    elif idMateria == "14706": # Simulación empresarial
        return "5149"
    elif idMateria == "14709": # Sostenibilidad aplicada al sistema productivo
        return ""

    ####################    
    # ADG302 - Asistencia a la Dirección
    ####################
    if idMateria == "14711": # Comunicación y atención al cliente
        return "7855"
#    elif idMateria == "14713": # Digitalización aplicada a los sectores productivos (GS)
#        return ""
    elif idMateria == "14715": # Gestión de la documentación jurídica y empresarial
        return "7851"
    elif idMateria == "14717": # Inglés profesional
        return "7862" # Inglés
    elif idMateria == "14719": # Itinerario personal para la empleabilidad I
        return "8491" # FOL
    elif idMateria == "14721": # Ofimática y proceso de la información
        return "7853"
    elif idMateria == "14723": # Proceso integral de la actividad comercial
        return "7854"
    elif idMateria == "14725": # Recursos humanos y responsabilidad social corporativa
        return "7852"
    elif idMateria == "14728": # Gestión avanzada de la información
        return "7871"
#    elif idMateria == "14730": # Itinerario personal para la empleabilidad II
#        return ""
#    elif idMateria == "14732": # Módulo profesional optativo
#        return ""
    elif idMateria == "14734": # Organización de eventos empresariales
        return "7870"
    elif idMateria == "14737": # Protocolo empresarial
        return "7869"
    elif idMateria == "14739": # Proyecto intermodular de asistencia a la dirección
        return "7872" # Proyecto de asistencia a la dirección
    elif idMateria == "14741": # Segunda Lengua extranjera
        return "7863" # Segunda lengua extranjera: Francés
    elif idMateria == "14743": # Sostenibilidad aplicada al sistema productivo
        return ""
    
    ####################
    # IFC201 - Sistemas Microinformáticos y Redes
    ####################
    if idMateria == "16691": # Aplicaciones ofimáticas
        return "5349"
#    elif idMateria == "16693": # Digitalización aplicada a los sectores productivos (GM)
#        return ""
    elif idMateria == "16695": # Inglés profesional (GM)
        return "5359" # Lengua extranjera profesional: inglés 1
    elif idMateria == "16697": # Itinerario personal para la empleabilidad I
        return "5355" # FOL
    elif idMateria == "16699": # Montaje y mantenimiento de equipo
        return "5347"
    elif idMateria == "16701": # Redes locales
        return "5351"
    elif idMateria == "16703": # Sistemas operativos monopuesto
        return "5348"
#    elif idMateria == "16706": # Tutoría I
#        return ""
    elif idMateria == "16708": # Aplicaciones web
        return "4995"
    elif idMateria == "16711": # Itinerario personal para la empleabilidad II
        return "4997" # Empresa e iniciativa emprendedora
#    elif idMateria == "16713": # Módulo profesional optativo
#        return ""
#    elif idMateria == "16715": # Proyecto intermodular
#        return ""
    elif idMateria == "16717": # Seguridad informática
        return "4993"
    elif idMateria == "16720": # Servicios en red
        return "4994"
    elif idMateria == "16722": # Sistemas operativos en red
        return "4991"
#    elif idMateria == "16724": # Sostenibilidad aplicada al sistema productivo
#        return ""
#    elif idMateria == "16726": # Tutoría II
#        return ""

    ####################
    # COM201 - Actividades Comerciales
    ####################
    if idMateria == "15333": # Aplicaciones informáticas para el comercio
        return "13948"
#    elif idMateria == "15335": # Digitalización aplicada a los sectores productivos (GM)
#        return ""
    elif idMateria == "15337": # Dinamización del punto de venta
        return "13947"
    elif idMateria == "15340": # Gestión de compras
        return "13945"
    elif idMateria == "15342": # Inglés profesional (GM)
        return "13944" # Inglés
    elif idMateria == "15344": # Itinerario personal para la empleabilidad I
        return "13946" # FOL
    elif idMateria == "15346": # Marketing en la actividad comercial
        return "13943"
    elif idMateria == "15348": # Procesos de venta
        return "13942"
#    elif idMateria == "15350": # Tutoría I
#        return ""
    elif idMateria == "15352": # Comercio electrónico
        return "13954"
    elif idMateria == "15354": # Gestión de un pequeño comercio
        return "13952"
#    elif idMateria == "15356": # Itinerario personal para la empleabilidad II
#        return ""
#    elif idMateria == "15358": # Módulo profesional optativo
#        return ""
#    elif idMateria == "15360": # Proyecto intermodular
#        return ""
    elif idMateria == "15362": # Servicios de atención comercial
        return "13951"
#    elif idMateria == "15365": # Sostenibilidad aplicada al sistema productivo
#        return ""
    elif idMateria == "15367": # Técnicas de almacén
        return "13950"
#    elif idMateria == "15369": # Tutoría II
#        return ""
    elif idMateria == "15371": # Venta técnica
        return "13949"

    ####################
    # COM301 - Comercio Internacional
    ####################
#    if idMateria == "15373": # Digitalización aplicada a los sectores productivos (GS)
#        return ""
    if idMateria == "15375": # Gestión administrativa del comercio internacional
        return "5409"
    elif idMateria == "15377": # Gestión económica y financiera de la empresa
        return "5407"
    elif idMateria == "15380": # Inglés profesional
        return "5405" # Inglés
    elif idMateria == "15382": # Itinerario personal para la empleabilidad I
        return "5417" # FOL
    elif idMateria == "15384": # Logística de almacenamiento
        return "5408"
    elif idMateria == "15386": # Transporte internacional de mercancías
        return "5406"
    elif idMateria == "15388": # Comercio digital internacional
        return "5163"
    elif idMateria == "15390": # Financiación internacional
        return "5161"
#    elif idMateria == "15392": # Itinerario personal para la empleabilidad II
#        return ""
    elif idMateria == "15394": # Marketing internacional
        return "5159"
    elif idMateria == "15396": # Medios de pago internacionales
        return "5162"
#    elif idMateria == "15399": # Módulo profesional optativo
#        return ""
    elif idMateria == "15401": # Negociación internacional
        return "5160"
    elif idMateria == "15403": # Proyecto intermodular de comercio internacional
        return "5164" # Proyecto de comercio internacional
    elif idMateria == "15405": # Sistema de información de mercados
        return "5158"
#    elif idMateria == "15407": # Sostenibilidad aplicada al sistema productivo
#        return ""

    ####################
    # COM302 - Gestión de Ventas y Espacios Comerciales
    ####################
#    if idMateria == "15409": # Digitalización aplicada a los sectores productivos (GS) ( Virtual )
#        return ""
#    el
    if idMateria == "15411": # Gestión económica y financiera de la empresa ( Virtual )
        return "7909"
    elif idMateria == "15414": # Inglés profesional ( Virtual )
        return "7913" # Inglés
    elif idMateria == "15416": # Investigación comercial ( Virtual )
        return "7926"
    elif idMateria == "15418": # Itinerario personal para la empleabilidad I ( Virtual )
        return "8412" # FOL
    elif idMateria == "15420": # Marketing digital ( Virtual )
        return "7908"
    elif idMateria == "15422": # Políticas de marketing ( Virtual )
        return "7907"
    elif idMateria == "15424": # Escaparatismo y diseño de espacios comerciales ( Virtual )
        return "7917"
    elif idMateria == "15426": # Gestión de productos y promociones en el punto de venta ( Virtual )
        return "7918"
#    elif idMateria == "15428": # Itinerario personal para la empleabilidad II ( Virtual )
#        return ""
    elif idMateria == "15430": # Logística de almacenamiento ( Virtual )
        return "7910"
    elif idMateria == "15432": # Logística de aprovisionamiento ( Virtual )
        return "7925"
#    elif idMateria == "15435": # Módulo profesional optativo ( Virtual )
#        return ""
    elif idMateria == "15437": # Organización de equipos de ventas ( Virtual )
        return "7919"
    elif idMateria == "15439": # Proyecto intermodular de Gestión de ventas y espacios comerciales ( Virtual )
        return "7928" # Proyecto de gestión de ventas y espacios comerciales
#    elif idMateria == "15441": # Sostenibilidad aplicada al sistema productivo ( Virtual )
#        return ""
    elif idMateria == "15443": # Técnicas de venta y negociación ( Virtual )
        return "7920"
    
    ####################
    # COM303 - Transporte y Logística
    ####################
#    if idMateria == "15445": # Digitalización aplicada a los sectores productivos (GS) ( Virtual )
#        return ""
#    el
    if idMateria == "15447": # Gestión administrativa del comercio internacional ( Virtual )
        return "5426"
    elif idMateria == "15449": # Gestión económica y financiera de la empresa ( Virtual )
        return "5422"
    elif idMateria == "15452": # Inglés profesional ( Virtual )
        return "5419" # Inglés
    elif idMateria == "15454": # Itinerario personal para la empleabilidad I ( Virtual )
        return "5430" # FOL
    elif idMateria == "15456": # Logística de almacenamiento ( Virtual )
        return "5424"
    elif idMateria == "15459": # Transporte internacional de mercancías ( Virtual )
        return "5421"
    elif idMateria == "15461": # Comercialización del transporte y la logística ( Virtual )
        return "5198"
    elif idMateria == "15463": # Gestión administrativa del transporte y la logística ( Virtual )
        return "5195"
#    elif idMateria == "15465": # Itinerario personal para la empleabilidad II ( Virtual )
#        return ""
    elif idMateria == "15467": # Logística de aprovisionamiento ( Virtual )
        return "5200"
#    elif idMateria == "15470": # Módulo profesional optativo ( Virtual )
#        return ""
    elif idMateria == "15472": # Organización del transporte de mercancías ( Virtual )
        return "5203"
    elif idMateria == "15475": # Organización del transporte de viajeros ( Virtual )
        return "5202"
    elif idMateria == "15477": # Proyecto intermodular de transporte y logística ( Virtual )
        return "5204" # Proyecto de transporte y logística
#    elif idMateria == "15479": # Sostenibilidad aplicada al sistema productivo ( Virtual )
#        return ""

    ####################
    # IFC303 - Desarrollo de Aplicaciones WEB
    ####################
    if idMateria == "16803": # Bases de Datos
        return "5180"
#    elif idMateria == "16805": # Digitalización aplicada a los sectores productivos (GS)
#        return ""
    elif idMateria == "16807": # Entornos de desarrollo
        return "5182"
    elif idMateria == "16809": # Inglés profesional
        return "5191" # Lengua Extranjera profesional: Inglés 1
    elif idMateria == "16811": # Itinerario personal para la empleabilidad I
        return "5188" # FOL
    elif idMateria == "16813": # Lenguajes de marcas y sistemas de gestión de información
        return "5178"
    elif idMateria == "16815": # Programación
        return "5181"
    elif idMateria == "16817": # Sistemas informáticos
        return "5179"
    elif idMateria == "16820": # Desarrollo web en entorno cliente
        return "5083"
    elif idMateria == "16822": # Desarrollo web en entorno servidor
        return "5084"
    elif idMateria == "16824": # Despliegue de aplicaciones web
        return "5085"
    elif idMateria == "16827": # Diseño de interfaces WEB
        return "5086"
    elif idMateria == "16829": # Itinerario personal para la empleabilidad II
        return "5089" # Empresa e iniciativa emprendedora
#    elif idMateria == "16831": # Módulo profesional optativo
#        return ""
    elif idMateria == "16833": # Proyecto intermodular de desarrollo de aplicaciones web
        return "5087" # Proyecto de desarrollo de aplicaciones Web
#    elif idMateria == "16835": # Sostenibilidad aplicada al sistema productivo
#        return ""
    
    ####################
    # IMS302 - Producción de Audiovisuales y Espectáculos 
    ####################
#    if idMateria == "17349": # Digitalización aplicada a los sectores productivos (GS) ( Virtual )
#        return ""
#    el
    if idMateria == "17351": # Inglés profesional ( Virtual )
        return "7941" # Lengua extranjera profesional: Inglés 1
    elif idMateria == "17353": # Itinerario personal para la empleabilidad I ( Virtual )
        return "9333" # FOL
    elif idMateria == "17355": # Medios técnicos audiovisuales y escénicos ( Virtual )
        return "7929"
    elif idMateria == "17357": # Planificación de proyectos audiovisuales ( Virtual )
        return "7930"
    elif idMateria == "17359": # Planificación de proyectos de espectáculos y eventos ( Virtual )
        return "7933"
    elif idMateria == "17361": # Recursos expresivos audiovisuales y escénicos ( Virtual )
        return "7935"
    elif idMateria == "17363": # Administración y promoción de audiovisuales y espectáculos ( Virtual )
        return "7950"
    elif idMateria == "17365": # Gestión de proyectos de cine, vídeo y multimedia ( Virtual )
        return "7945"
    elif idMateria == "17367": # Gestión de proyectos de espectáculos y eventos ( Virtual )
        return "7948"
    elif idMateria == "17369": # Gestión de proyectos de televisión y radio ( Virtual )
        return "7946"
    elif idMateria == "17371": # Itinerario personal para la empleabilidad II ( Virtual )
        return "7952" # PAE - Empresa e iniciativa emprendedora
#    elif idMateria == "17373": # Módulo profesional optativo ( Virtual )
#        return ""
    elif idMateria == "17375": # Proyecto intermodular de producción de audiovisuales y espectáculos ( Virtual )
        return "7951" # Proyecto de producción de audiovisuales y espectáculos
    elif idMateria == "17377": # Sostenibilidad aplicada al sistema productivo ( Virtual )
        return ""
    
    ####################
    # QUI301 - Laboratorio de Análisis y de Control de Calidad
    ####################
    if idMateria == "17879": # Análisis químicos ( Virtual )
        return "5256"
#    elif idMateria == "17881": # Digitalización aplicada a los sectores productivos (GS) ( Virtual )
#        return ""
    elif idMateria == "17883": # Ensayos físicos químicos ( Virtual )
        return "5259"
    elif idMateria == "17885": # Ensayos microbiológicos ( Virtual )
        return "5260"
    elif idMateria == "17887": # Inglés profesional ( Virtual )
        return "5270" # Lengua Extranjera profesional: inglés 1
    elif idMateria == "17889": # Itinerario personal para la empleabilidad I ( Virtual )
        return "5266" # FOL
    elif idMateria == "17891": # Muestreo y preparación de la muestra ( Virtual )
        return "5255"
    elif idMateria == "17894": # Análisis instrumental ( Virtual )
        return "5031"
    elif idMateria == "17896": # Calidad y seguridad en el laboratorio ( Virtual )
        return "5036"
    elif idMateria == "17898": # Ensayos biotecnológicos ( Virtual )
        return "5035"
    elif idMateria == "17900": # Ensayos físicos ( Virtual )
        return "5032"
    elif idMateria == "17903": # Itinerario personal para la empleabilidad II ( Virtual )
        return "5041" # Empresa e iniciativa emprendedora
#    elif idMateria == "17905": # Módulo profesional optativo ( Virtual )
#        return ""
    elif idMateria == "17907": # Proyecto intermodular de laboratorio de análisis y de control de calidad ( Virtual )
        return "5039" # Proyecto de laboratorio de análisis y de control de calidad
#    elif idMateria == "17909": # Sostenibilidad aplicada al sistema productivo ( Virtual )
#        return ""
    
    ####################
    # ELE202 - Instalaciones Eléctricas y Automáticas
    ####################
    if idMateria == "15562": # Automatismos industriales ( Virtual )
        return "5335"
#    elif idMateria == "15564": # Digitalización aplicada a los sectores productivos (GM) ( Virtual )
#        return ""
    elif idMateria == "15566": # Electrónica ( Virtual )
        return "12359"
    elif idMateria == "15569": # Electrotecnia ( Virtual )
        return "5337"
#    elif idMateria == "15571": # Inglés profesional (GM) ( Virtual )
#        return ""
    elif idMateria == "15573": # Instalaciones eléctricas interiores ( Virtual )
        return "5338"
    elif idMateria == "15575": # Itinerario personal para la empleabilidad I ( Virtual )
        return "5344" # FOL
#    elif idMateria == "15577": # Tutoría I ( Virtual )
#        return ""
    elif idMateria == "15579": # Infraestructuras comunes de telecomunicación en viviendas y edificios ( Virtual )
        return "4981"
    elif idMateria == "15582": # Instalaciones de distribución ( Virtual )
        return "4980"
    elif idMateria == "15584": # Instalaciones domóticas ( Virtual )
        return "4982"
    elif idMateria == "15586": # Instalaciones solares fotovoltaicas ( Virtual )
        return "12360"
    elif idMateria == "15588": # Itinerario personal para la empleabilidad II ( Virtual )
        return "4986" # Empresa e iniciativa emprendedora
    elif idMateria == "15590": # Máquinas eléctricas ( Virtual )
        return "4984"
#    elif idMateria == "15592": # Módulo profesional optativo ( Virtual )
#        return ""
#    elif idMateria == "15594": # Proyecto intermodular ( Virtual )
#        return ""
#    elif idMateria == "15596": # Sostenibilidad aplicada al sistema productivo ( Virtual )
#        return ""
#    elif idMateria == "15598": # Tutoría II ( Virtual )
#        return ""
    
    ####################
    # SEA301 - Educación y Control Ambiental
    ####################
#    if idMateria == "18379": # Digitalización aplicada a los sectores productivos (GS) ( Virtual )
#        return ""
#    el
    if idMateria == "18381": # Estructura y dinámica del medio ambiente ( Virtual )
        return "12339"
    elif idMateria == "18383": # Gestión ambiental ( Virtual )
        return "12338"
    elif idMateria == "18385": # Inglés profesional ( Virtual )
        return "12341" # Lengua extranjera profesional: inglés, 1
    elif idMateria == "18387": # Itinerario personal para la empleabilidad I ( Virtual )
        return "12340" # FOL
    elif idMateria == "18389": # Medio natural ( Virtual )
        return "12342"
    elif idMateria == "18391": # Métodos y productos cartográficos ( Virtual )
        return "12343"
    elif idMateria == "18393": # Programas de educación ambiental ( Virtual )
        return "12344"
    elif idMateria == "18395": # Actividades de uso público ( Virtual )
        return "12345"
    elif idMateria == "18397": # Actividades humanas y problemática ambiental ( Virtual )
        return "12346"
    elif idMateria == "18399": # Desenvolvimiento en el medio ( Virtual )
        return "12347"
    elif idMateria == "18401": # Habilidades sociales ( Virtual )
        return "12350"
    elif idMateria == "18403": # Itinerario personal para la empleabilidad II ( Virtual )
        return "12348" # EIE
#    elif idMateria == "18405": # Módulo profesional optativo ( Virtual )
#        return ""
    elif idMateria == "18407": # Proyecto intermodular de educación y control ambiental ( Virtual )
        return "12352" # Proyecto de educación y control ambiental
#    elif idMateria == "18409": # Sostenibilidad aplicada al sistema productivo ( Virtual )
#        return ""
    elif idMateria == "18411": # Técnicas de educación ambiental ( Virtual )
        return "12353"
    
    ####################
    # HOT301 - Agencias de Viajes y Gestión de Eventos
    ####################
    if idMateria == "16460": # Destinos turísticos ( Virtual )
        return "5456"
#    elif idMateria == "16462": # Digitalización aplicada a los sectores productivos (GS) ( Virtual )
#        return ""
    elif idMateria == "16464": # Dirección de entidades de intermediación turística ( Virtual )
        return "5463"
    elif idMateria == "16466": # Estructura del mercado turístico ( Virtual )
        return "5447"
    elif idMateria == "16468": # Inglés profesional ( Virtual )
        return "5225" # Inglés  Global
    elif idMateria == "16470": # Itinerario personal para la empleabilidad I ( Virtual )
        return "5458" # FOL
    elif idMateria == "16472": # Protocolo y relaciones públicas ( Virtual )
        return "5223"
    elif idMateria == "16474": # Recursos turísticos ( Virtual )
        return "5457"
    elif idMateria == "16476": # Gestión de productos turísticos ( Virtual )
        return "5236"
    elif idMateria == "16478": # Itinerario personal para la empleabilidad II ( Virtual )
        return "5234" # EIE
    elif idMateria == "16480": # Marketing turístico ( Virtual )
        return "5224"
#    elif idMateria == "16482": # Módulo profesional optativo ( Virtual )
#        return ""
    elif idMateria == "16484": # Proyecto intermodular de agencias de viajes y gestión de eventos ( Virtual )
        return "5239" # Proyecto de agencias de viajes y gestión de eventos
    elif idMateria == "16486": # Segunda lengua extranjera ( Virtual )
        return "5228" # Segunda lengua extranjera: Francés Global
#    elif idMateria == "16488": # Sostenibilidad aplicada al sistema productivo ( Virtual )
#        return ""
    elif idMateria == "16490": # Venta de servicios turísticos ( Virtual )
        return "5237"
    
    ####################
    # IFC301 - Administración de Sistemas Informáticos en Red
    ####################
#    if idMateria == "16728": # Digitalización aplicada a los sectores productivos (GS) ( Virtual )
#        return ""
#    el
    if idMateria == "16730": # Fundamentos de hardware ( Virtual )
        return "5274"
    elif idMateria == "16732": # Gestión de bases de datos ( Virtual )
        return "5275"
    elif idMateria == "16735": # Implantación de sistemas operativos ( Virtual )
        return "5272"
    elif idMateria == "16737": # Inglés profesional ( Virtual )
        return "5286" # Lengua extranjera profesional: inglés 1
    elif idMateria == "16739": # Itinerario personal para la empleabilidad I ( Virtual )
        return "5283" # FOL
    elif idMateria == "16741": # Lenguajes de marcas y sistemas de gestión de información ( Virtual )
        return "5276"
    elif idMateria == "16743": # Planificación y administración de redes ( Virtual )
        return "5273"
    elif idMateria == "16745": # Administración de sistemas gestores de bases de datos ( Virtual )
        return "5054"
    elif idMateria == "16747": # Administración de sistemas operativos ( Virtual )
        return "5051"
    elif idMateria == "16750": # Implantación de aplicaciones web ( Virtual )
        return "5053"
    elif idMateria == "16752": # Itinerario personal para la empleabilidad II ( Virtual )
        return "5058" # EIE
#    elif idMateria == "16754": # Módulo profesional optativo ( Virtual )
#        return ""
    elif idMateria == "16756": # Proyecto intermodular de administración de sistemas informáticos en red ( Virtual )
        return "5056" # Proyecto de administración de sistemas informáticos en red.
    elif idMateria == "16758": # Seguridad y alta disponibilidad ( Virtual )
        return "5055"
    elif idMateria == "16760": # Servicios de red e internet ( Virtual )
        return "5052"
#    elif idMateria == "16762": # Sostenibilidad aplicada al sistema productivo ( Virtual )
#        return ""

    ####################
    # IFC302 - Desarrollo de Aplicaciones Multiplataforma
    ####################
    if idMateria == "16764": # Bases de Datos ( Virtual )
        return "5290"
#    elif idMateria == "16767": # Digitalización aplicada a los sectores productivos (GS) ( Virtual )
#        return ""
    elif idMateria == "16769": # Entornos de desarrollo ( Virtual )
        return "5293"
    elif idMateria == "16771": # Inglés profesional ( Virtual )
        return "5176" # Lengua Extranjera profesional: Inglés 1
    elif idMateria == "16773": # Itinerario personal para la empleabilidad I ( Virtual )
        return "5173" # FOL
    elif idMateria == "16775": # Lenguajes de marcas y sistemas de gestión de información ( Virtual )
        return "5288"
    elif idMateria == "16777": # Programación ( Virtual )
        return "5291"
    elif idMateria == "16779": # Sistemas informáticos ( Virtual )
        return "5289"
    elif idMateria == "16782": # Acceso a datos ( Virtual )
        return "5066"
    elif idMateria == "16784": # Desarrollo de interfaces ( Virtual )
        return "5068"
    elif idMateria == "16787": # Itinerario personal para la empleabilidad II ( Virtual )
        return "5074" # Empresa e iniciativa emprendedora
#    elif idMateria == "16789": # Módulo profesional optativo ( Virtual )
#        return ""
    elif idMateria == "16791": # Programación de servicios y procesos ( Virtual )
        return "5070"
    elif idMateria == "16794": # Programación multimedia y dispositivos móviles ( Virtual )
        return "5069"
    elif idMateria == "16796": # Proyecto intermodular de desarrollo de aplicaciones multiplataforma ( Virtual )
        return "5072" # Proyecto de desarrollo de aplicaciones multiplataforma
    elif idMateria == "16798": # Sistemas de gestión empresarial ( Virtual )
        return "5071"
#    elif idMateria == "16801": # Sostenibilidad aplicada al sistema productivo ( Virtual )
#        return ""
    
    ####################
    # ELE304 - Sistemas de Telecomunicaciones e Informáticos
    ####################
    if idMateria == "15756": # Configuración de infraestructuras de sistemas de telecomunicaciones ( Virtual )
        return "13932"
#    elif idMateria == "15758": # Digitalización aplicada a los sectores productivos (GS) ( Virtual )
#        return ""
    elif idMateria == "15760": # Elementos de sistemas de telecomunicaciones ( Virtual )
        return "13929"
    elif idMateria == "15762": # Gestión de proyectos de instalaciones de telecomunicaciones ( Virtual )
        return "13926" # Gestión de proyectos de instalaciones de telecomunicaciones
    elif idMateria == "15764": # Inglés profesional ( Virtual )
        return "13927" # Lengua Extranjera  profesional: Inglés 1
    elif idMateria == "15766": # Itinerario personal para la empleabilidad I ( Virtual )
        return "13931" # FOL
    elif idMateria == "15768": # Sistemas de producción audiovisual ( Virtual )
        return "13936"
    elif idMateria == "15770": # Sistemas de telefonía fija y móvil ( Virtual )
        return "13930"
    elif idMateria == "15772": # Sistemas informáticos y redes locales ( Virtual )
        return "13928"
    elif idMateria == "15774": # Itinerario personal para la empleabilidad II ( Virtual )
        return "13934" # EIE
#    elif idMateria == "15776": # Módulo profesional optativo ( Virtual )
#        return ""
    elif idMateria == "15778": # Proyecto de sistemas de telecomunicaciones e informáticos ( Virtual )
        return "13941" # Proyecto de Sistemas de Telecomunicaciones e Informáticos
    elif idMateria == "15780": # Redes telemáticas ( Virtual )
        return "13937"
    elif idMateria == "15782": # Sistemas de radiocomunicaciones ( Virtual )
        return "13935"
    elif idMateria == "15784": # Sistemas integrados y hogar digital ( Virtual )
        return "13940"
#    elif idMateria == "15786": # Sostenibilidad aplicada al sistema productivo ( Virtual )
#        return ""
    elif idMateria == "15788": # Técnicas y procesos en infraestructuras de telecomunicaciones ( Virtual )
        return "13933"

    ####################
    # SAN202 - Farmacia y Parafarmacia
    ####################
    if idMateria == "17981": # Anatomofisiología y patología básicas ( Virtual )
        return "5324"
#    elif idMateria == "17983": # Digitalización aplicada a los sectores productivos (GM) ( Virtual )
#        return ""
    elif idMateria == "17985": # Dispensación de productos farmacéuticos ( Virtual )
        return "5327"
    elif idMateria == "17987": # Disposición y venta de productos ( Virtual )
        return "5325"
#    elif idMateria == "17989": # Inglés profesional ( Virtual )
#        return ""
    elif idMateria == "17991": # Itinerario personal para la empleabilidad I ( Virtual )
        return "5332" # FOL
    elif idMateria == "17993": # Oficina de Farmacia ( Virtual )
        return "5326"
    elif idMateria == "17995": # Operaciones básicas de laboratorio ( Virtual )
        return "5329"
    elif idMateria == "17998": # Primeros auxilios ( Virtual )
        return "5323"
#    elif idMateria == "18000": # Tutoría I ( Virtual )
#        return ""
    elif idMateria == "18002": # Dispensación de productos parafarmacéuticos ( Virtual )
        return "4969"
    elif idMateria == "18004": # Formulación magistral ( Virtual )
        return "4971"
    elif idMateria == "18007": # Itinerario personal para la empleabilidad II ( Virtual )
        return "4974" # EIE
#    elif idMateria == "18009": # Módulo profesional optativo ( Virtual )
#        return ""
    elif idMateria == "18011": # Promoción de la salud ( Virtual )
        return "4972"
#    elif idMateria == "18013": # Proyecto intermodular ( Virtual )
#        return ""
#    elif idMateria == "18015": # Sostenibilidad aplicada al sistema productivo ( Virtual )
#        return ""
#    elif idMateria == "18017": # Tutoría II ( Virtual )
#        return ""
    
    ####################
    # SAN203 - Emergencias Sanitarias
    ####################
    if idMateria == "18019": # Anatomofisiología y patología básicas ( Virtual )
        return "5319"
    elif idMateria == "18021": # Apoyo psicológico en situaciones de emergencia ( Virtual )
        return "5316"
    elif idMateria == "18023": # Atención sanitaria inicial en situaciones de emergencia ( Virtual )
        return "5313"
#    elif idMateria == "18025": # Digitalización aplicada a los sectores productivos (GM) ( Virtual )
#        return ""
    elif idMateria == "18027": # Dotación sanitaria ( Virtual )
        return "5312"
    elif idMateria == "18029": # Evacuación y traslado de pacientes ( Virtual )
        return "5315"
#    elif idMateria == "18032": # Inglés profesional ( Virtual )
#        return ""
    elif idMateria == "18034": # Itinerario personal para la empleabilidad I ( Virtual )
        return "5320" # FOL
    elif idMateria == "18036": # Mantenimiento mecánico preventivo del vehículo ( Virtual )
        return "5310"
#    elif idMateria == "18038": # Tutoría I ( Virtual )
#        return ""
    elif idMateria == "18040": # Atención sanitaria especial en situaciones de emergencia ( Virtual )
        return "4955"
    elif idMateria == "18042": # Itinerario personal para la empleabilidad II ( Virtual )
        return "4962" # EIE
    elif idMateria == "18044": # Logística sanitaria en emergencias ( Virtual )
        return "4952"
#    elif idMateria == "18046": # Módulo profesional optativo ( Virtual )
#        return ""
    elif idMateria == "18048": # Planes de emergencia y dispositivos de riesgos previsibles ( Virtual )
        return "4958"
#    elif idMateria == "18050": # Proyecto intermodular ( Virtual )
#        return ""
#    elif idMateria == "18052": # Sostenibilidad aplicada al sistema productivo ( Virtual )
#        return ""
    elif idMateria == "18054": # Tele emergencia ( Virtual )
        return "4959"
#    elif idMateria == "18057": # Tutoría II ( Virtual )
#        return ""
    
    ####################
    # SSC201 - Atención a Personas en situación de Dependencia
    ####################
    if idMateria == "18494": # Atención sanitaria ( Virtual )
        return "5382"
    elif idMateria == "18496": # Atención y apoyo psicosocial ( Virtual )
        return "5379"
    elif idMateria == "18498": # Características y necesidades de las personas en situación de dependencia ( Virtual )
        return "5378"
    elif idMateria == "18500": # Destrezas sociales ( Virtual )
        return "5125"
#    elif idMateria == "18502": # Digitalización aplicada a los sectores productivos (GM) ( Virtual )
#        return ""
#    elif idMateria == "18504": # Inglés profesional (GM) ( Virtual )
#        return ""
    elif idMateria == "18506": # Itinerario personal para la empleabilidad I ( Virtual )
        return "5384" # FOL
    elif idMateria == "18508": # Primeros auxilios ( Virtual )
        return "5375"
#    elif idMateria == "18510": # Tutoría I ( Virtual )
#        return ""
    elif idMateria == "18512": # Apoyo a la comunicación ( Virtual )
        return "5128"
    elif idMateria == "18514": # Apoyo domiciliario ( Virtual )
        return "5381"
    elif idMateria == "18516": # Atención higiénica ( Virtual )
        return "5131"
    elif idMateria == "18518": # Itinerario personal para la empleabilidad II ( Virtual )
        return "5133" # EIE
#    elif idMateria == "18520": # Módulo profesional optativo ( Virtual )
#        return ""
    elif idMateria == "18522": # Organización de la atención a las personas en situación de dependencia ( Virtual )
        return "5124"
#    elif idMateria == "18524": # Proyecto intermodular ( Virtual )
#        return ""
#    elif idMateria == "18526": # Sostenibilidad aplicada al sistema productivo ( Virtual )
#        return ""
    elif idMateria == "18528": # Teleasistencia ( Virtual )
        return "5135"
#    elif idMateria == "18530": # Tutoría II ( Virtual )
#        return ""
    
    ####################
    # SSC302 - Educación Infantil (Formación Profesional)
    ####################
    if idMateria == "18586": # Autonomía personal y salud infantil ( Virtual )
        return "5433"
    elif idMateria == "18588": # Desarrollo cognitivo y motor ( Virtual )
        return "5436"
    elif idMateria == "18591": # Didáctica de la Educación Infantil ( Virtual )
        return "5432"
#    elif idMateria == "18593": # Digitalización aplicada a los sectores productivos (GS) ( Virtual )
#        return ""
    elif idMateria == "18595": # Habilidades sociales ( Virtual )
        return "5213"
    elif idMateria == "18597": # Inglés profesional ( Virtual )
        return "5445" # Lengua extranjera profesional: inglés 1
    elif idMateria == "18599": # Itinerario personal para la empleabilidad I ( Virtual )
        return "5442" # FOL
    elif idMateria == "18601": # Primeros auxilios ( Virtual )
        return "5441"
    elif idMateria == "18603": # Desarrollo socioafectivo ( Virtual )
        return "5212"
    elif idMateria == "18606": # El juego infantil y su metodología ( Virtual )
        return "5434"
    elif idMateria == "18608": # Expresión y comunicación ( Virtual )
        return "5210"
    elif idMateria == "18611": # Intervención con familias y atención a menores en riesgo social  ( Virtual )
        return "5214"
    elif idMateria == "18613": # Itinerario personal para la empleabilidad II ( Virtual )
        return "5218" # EIE
#    elif idMateria == "18615": # Módulo profesional optativo ( Virtual )
#        return ""
    elif idMateria == "18617": # Proyecto intermodular de atención a la infancia ( Virtual )
        return "5215" # Proyecto de atención a la infancia.
#    elif idMateria == "18619": # Sostenibilidad aplicada al sistema productivo ( Virtual )
#        return ""

    ####################
    # SSC303 - Integración Social (Formación Profesional)
    ####################
    if idMateria == "18621": # Contexto de la intervención social ( Virtual )
        return "7874"
#    elif idMateria == "18623": # Digitalización aplicada a los sectores productivos (GS) ( Virtual )
#        return ""
    elif idMateria == "18625": # Habilidades sociales ( Virtual )
        return "7899"
    elif idMateria == "18627": # Inglés profesional ( Virtual )
        return "7884" # Lengua extranjera profesional: Inglés 1
    elif idMateria == "18629": # Inserción sociolaboral ( Virtual )
        return "7875"
    elif idMateria == "18631": # Itinerario personal para la empleabilidad I ( Virtual )
        return "8339" # FOL
    elif idMateria == "18633": # Metodología de la intervención social ( Virtual )
        return "7897"
    elif idMateria == "18635": # Primeros auxilios ( Virtual )
        return "7882"
    elif idMateria == "18637": # Promoción de la autonomía personal ( Virtual )
        return "7879"
    elif idMateria == "18639": # Apoyo a intervención educativa ( Virtual )
        return "7878"
    elif idMateria == "18641": # Atención a las unidades de convivencia ( Virtual )
        return "7892"
    elif idMateria == "18643": # Itinerario personal para la empleabilidad II ( Virtual )
        return "7902" # EIE
    elif idMateria == "18645": # Mediación comunitaria ( Virtual )
        return "7877"
#    elif idMateria == "18647": # Módulo profesional optativo ( Virtual )
#        return ""
    elif idMateria == "18649": # Proyecto intermodular de integración social ( Virtual )
        return "7901" # Proyecto de integración social
    elif idMateria == "18651": # Sistemas aumentativos y alternativos de comunicación  ( Virtual )
        return "7896"
#    elif idMateria == "18653": # Sostenibilidad aplicada al sistema productivo ( Virtual )
#        return ""


    ########################################################################################################################
    # End of conversionLOFPaLOE
    ########################################################################################################################
