#Import the modules
import requests
import json
import time
import urllib.parse
import xml.dom.minidom
import subprocess
import os
import sys
import io
import smtplib
import ssl
from datetime import datetime
from Config import *
from Conexion import *
from classes.Alumno import *
from classes.Centro import *
from classes.Ciclo import *
from classes.Modulo import *

def main():
    #
    mensajes_email = []
    usuarios_moodle_no_borrables = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] # ids de users creados en deploy que no hay que borrar
    # 
    moodle = get_moodle(SUBDOMAIN)[0]
    alumnos_sigad = []
    alumnos_moodle = get_alumnos_moodle_no_borrados(moodle) # Alumnos que figuran en moodle antes de ejecutar el script
    
    #########################################
    # Obtengo curso académico que debo usar
    #########################################
    curso_academico = "2020" # TODO
    #########################################
    # Transformo JSON de SIGAD a lista
    #########################################
    # Creo la conexión para la 1era llamada
    conexion_1er_ws = Conexion(url1, path1+curso_academico, usuario1, password1, method1)
    # Hago la 1era llamada
    print( 'Making the call to the 1st web service:')
    resp_data = conexion_1er_ws.getJson()

    y = json.loads(resp_data);
    if y is not None:
        codigo=y["codigo"]
        mensaje=y["mensaje"]
        idSolicitud=y["idSolicitud"]
        print("Código: " , codigo, ", Mensaje: ", mensaje, "idSolicitud: ", idSolicitud)
        guarda_fichero(get_date_time() + ".ws1.log", str(resp_data) )
        if codigo == 0: # éxito en la 1era llamada
            # 
            print( 'Waiting 10 seconds before the first call to the 2nd web service...')
            for x in range(1, 11):
                time.sleep( 10 )
                print( 'Iteration number ' + str(x))
                conexion_2ndo_ws = Conexion(url2, path2 + str(idSolicitud), usuario2, password2, method2)
                resp_data = conexion_2ndo_ws.getJson()
                y = json.loads(resp_data)
                if y is not None:
                    codigo=y["codigo"]
                    mensaje=y["mensaje"]
                    print("codigo: " + str(codigo) + ", mensaje: " + str(mensaje))
                    guarda_fichero(get_date_time() + ".ws2.log", str(resp_data) )
                    if codigo == 0: # éxito de la 2nda llamada
                        procesaJsonEstudiantes(y, alumnos_sigad)
                        break
                    else: # Error  en la 2ª llamada
                        print("Fichero aún no listo. Código: " + str(codigo) 
                            + ", mensaje: " + str(mensaje))
        else: # Error en la 1era llamada
            print("Error en la llamada al 1er web service")
    
    ########################
    # Localizo los alumnos (los profesores no) que estén en moodle y no en SIGAD (en base a su dni/nie/...)
    ########################
    alumnos_en_moodle_pero_no_SIGAD = [  ]
    for alumnoMoodle in alumnos_moodle:
        existe = False
        # comprobamos si existe por dni/nie/...
        for alumnoSIGAD in alumnos_sigad:
            if alumnoMoodle['username'].lower() == alumnoSIGAD.getDocumento().lower():
                existe = True
                break
        if not existe:
            alumnos_en_moodle_pero_no_SIGAD.append(alumnoMoodle)
            
    print("*** Alumnos que estan en moodle y no en SIGAD:")
    for alumnoMoodle in alumnos_en_moodle_pero_no_SIGAD:
        print("alumnoMoodle: ", alumnoMoodle)

    ########################
    # De cada alumno que esté en moodle y no en sigad miro si en moodle hay alguien con ese email
    # - si hay alguien con ese email considero que es la misma persona a la que han actualizado DNI/NIE/... en SIGAD y la actualizo
    # - si no hay nadie con ese email considero que es una baja y lo botto
    ########################
    print("*** Alumnos que habría que actualizar su id:")
    mensajes_email.append( get_date_time() )
    mensajes_email.append("***** Alumnos actualizados su id:")
    alumnos_a_borrar = [ ] # los que no haya que actualizar son para borrar, irán aquí
    for alumnoMoodle in alumnos_en_moodle_pero_no_SIGAD:
        existe = False
        # comprobamos si existe por email
        for alumnoSIGAD in alumnos_sigad:
            if alumnoSIGAD.getEmail() is not None \
                    and alumnoMoodle['email'].lower() == alumnoSIGAD.getEmail().lower():
                existe = True
                # TODO: A este alumno de moodle habrá que ponerle el nuevo id que tenga en SIGAD
                print("- Alumno a actualizar su login por coincidencia de email: ", repr(alumnoMoodle) )
                print("habría que ponerle de login ", alumnoSIGAD.getDocumento() )
                userid = alumnoMoodle['userid']
                username_nuevo = alumnoSIGAD.getDocumento().lower()
                update_moodle_username(moodle, userid, username_nuevo)
                mensajes_email.append("- Al alumno que tenía usuario de acceso " + alumnoMoodle['username'] + \
                        " se le ha cambiado a " + alumnoSIGAD.getDocumento() + \
                        "(" + alumnoSIGAD.getEmail().lower() + ").")
                break
        if not existe:
            alumnos_a_borrar.append(alumnoMoodle)

    
    print("*** Alumnos a eliminar de Moodle")
    mensajes_email.append( get_date_time() )
    mensajes_email.append("***** Alumnos eliminados:")
    for alumnoMoodle in alumnos_a_borrar:
        print("- ", repr(alumnoMoodle) )
        if int(alumnoMoodle['userid']) not in usuarios_moodle_no_borrables: 
            delete_alumno_moodle(alumnoMoodle, moodle)
            mensajes_email.append("- " + alumnoMoodle)
        else:
            print("Alumno configurado como NO borrable")
    ########################
    # Desmatriculo de Moodle a aquellos alumnos que SIGAD me dice ya no deberían estar matriculados en un determinado curso
    # Obtengo y recorro los usuarios de moodle. 
    # Itero sobre los alumnos y obtengo en qué están matriculados en moodle:
    # - si están matriculados en algo en que no estén matriculados en SIGAD los desmatriculo
    # excepto si el shortname del curso termina en t (módulo de tutoría del ciclo)
    ########################
    alumnos_moodle = get_alumnos_moodle_no_borrados(moodle) 
    cursos_moodle = get_cursos(moodle)
    mensajes_email.append( get_date_time() )
    mensajes_email.append("***** Alumnos desmatriculados:")
    for alumno_moodle in alumnos_moodle:
        userid = alumno_moodle['userid']
        # no recorro los no borrables
        if int(userid) in usuarios_moodle_no_borrables: 
            continue
        username = alumno_moodle['username']
        # Obtengo los cursos en que este alumno moodle está matriculado en moodle
        cursos_matriculado = get_cursos_en_que_esta_matriculado(moodle, userid)
        # recorro los cursos en que el usuario de moodle está matriculado y miro si el usuario de sigad está matriculado en el curso o no
        for curso in cursos_matriculado:
            courseid = curso['courseid']
            course_shortname = curso['shortname']
            course_codes = course_shortname.split("-") # 0 centreid 1 siglas ciclo 2 codigo materia
            for alumno in alumnos_sigad:
                
                en_sigad_esta_matriculado = False
                if alumno.getDocumento().lower() == username.lower(): # he encontrado al alumno en SIGAD
                    print("-", repr(alumno) )
                    print("Actualmente el alumno", username, "está ahora matriculado en moodle en el curso", course_shortname, ". Vamos a comprobar si en SIGAD también está")
                    
                    centros = alumno.getCentros()
                    print("*Mirando centros del alumno")
                    for centro in centros:
                        if en_sigad_esta_matriculado:
                            break
                        if course_codes[0] == centro.get_codigo_centro(): #sigo profundizando
                            ciclos = centro.getCiclos()
                            print("**Mirando ciclos del alumno")
                            for ciclo in ciclos:
                                if en_sigad_esta_matriculado:
                                    break;
                                if course_codes[1] == ciclo.get_siglas_ciclo(): #sigo profundizando
                                    modulos = ciclo.getModulos()
                                    print("***Mirando módulos del alumno")
                                    for modulo in modulos:
                                        if en_sigad_esta_matriculado:
                                            break
                                        if int(course_codes[2]) == modulo.get_id_materia(): #he llegado al módulo
                                            en_sigad_esta_matriculado = True
                                            print("En SIGAD el alumno", username, "SI está matriculado en", course_shortname, "se le mantiene matriculado en moodle")
                                else:
                                    continue;
                        else:
                            continue
                    if not en_sigad_esta_matriculado:
                        print("En SIGAD el alumno", username, "NO está matriculado en", course_shortname, "se procede a desmatricular de moodle")
                        desmatricula_alumno_en_curso(moodle, userid, courseid)
                        mensajes_email.append("- " + username + "  desmatriculado de " + course_shortname)
                    break # una vez he procesado al alumno no tiene sentido seguir mirando los demás alumnos de SIGAD
    ########################
    # Proceso el fichero JSON (foto de SIGAD)
    # - si un alumno del fichero no existe en moodle lo creo
    # - matriculo a un alumno en los cursos que tenga asignados en SIGAD
    ########################
    mensajes_email.append( get_date_time() )
    mensajes_email.append("***** Alumnos creados y matriculados:")
    usuarios_no_creables = [ ]
    # Creo diccionario de id_cursoshortname para evitar usar get_id_de_curso_by_shortname en cada iteración
    diccionario_cursos = {curso['shortname'] : curso['courseid'] for curso in cursos_moodle}
    diccionario_alumnos = {alumno['username'] : alumno['userid'] for alumno in alumnos_moodle}
    #
    for alumno in alumnos_sigad:
        print("*** Procesando alumno de fichero JSNON ***")
        print("-", repr(alumno) )
        id_alumno = ""
        # Creo en moodle los alumnos que estén en el json y no estén en moodle
        if not existeAlumnoEnMoodle(moodle, alumno):
            try:
                id_alumno = crearAlumnoEnMoodle(moodle, alumno)
                mensajes_email.append("- Alumno " + alumno.getDocumento() + " creado.")
            except ValueError as e:
                usuarios_no_creables.append(alumno)
                continue
        else:
            #id_alumno = get_id_alumno_by_dni(moodle, alumno)
            id_alumno = diccionario_alumnos[ alumno.getDocumento().lower().rstrip() ]
        
        # Revisar si está matriculado dónde corresponda y matricular
        for centro in alumno.getCentros():
            codigo_centro = centro.get_codigo_centro()
            for ciclo in centro.getCiclos():
                siglas_ciclo = ciclo.get_siglas_ciclo()
                for modulo in ciclo.getModulos():
                    id_materia = modulo.get_id_materia()

                    shortname_curso = str(codigo_centro) + "-" + str(siglas_ciclo) + "-" + str(id_materia)
                    #id_curso = get_id_de_curso_by_shortname(moodle, shortname_curso)
                    id_curso = ""
                    try:
                        id_curso = diccionario_cursos[shortname_curso]
                    except KeyError:
                        id_curso = ""

                    if id_curso == "": # el curso no existe
                        print("El curso ", str(shortname_curso) , " no existe.", sep="")
                        mensajes_email.append("- Alumno "+ alumno.getDocumento()+ " NO puede matricularse en "+ shortname_curso + "por que el curso NO existe.")
                    elif not is_alumno_matriculado_en_curso(moodle, id_alumno, id_curso):
                        matricula_alumno_en_curso(moodle, id_alumno, id_curso)
                        mensajes_email.append("- Alumno "+ alumno.getDocumento()+ " matriculado en "+ shortname_curso + ".")
                    else:
                        print("El alumno (",id_alumno,") ya estaba matriculado en ", shortname_curso, sep="")
    # Listo alumnos que no se han podido crear
    mensajes_email.append( get_date_time() )
    mensajes_email.append("***** Alumnos que no se han podido crear:")
    print("Alumnos de SIGAD que no se han podido crear en Moodle: ")
    for alumno in usuarios_no_creables:
        print( "- ", repr(alumno) )
        mensajes_email.append("- " + alumno.getDocumento() )
    ########################
    # Envío email resumen de lo hecho por email a responsables
    ########################
    texto = """
        {}
        """.format("\n".join(mensajes_email[1:]))
    print(texto)
    send_email("fp@catedu.es", "Informe automatizado gestión automática usuarios moodle", texto)

    #
    # End of main 
    # 

def get_cursos_en_que_esta_matriculado(moodle, id_usuario):
    """
    Devuelve una lista de cursos en los que el alumno está matriculado
    """
    print("get_cursos_en_que_esta_matriculado(...)")

    command = '''\
            mysql --user=\"{DB_USER}\" --password=\"{DB_PASS}\" --host=\"{DB_HOST}\" -D \"{DB_NAME}\"  --execute=\"
                SELECT c.id, c.shortname 
                FROM mdl_user u 
                INNER JOIN mdl_user_enrolments ue ON ue.userid = u.id 
                INNER JOIN mdl_enrol e ON e.id = ue.enrolid 
                INNER JOIN mdl_course c ON e.courseid = c.id
                WHERE u.id = {id_usuario}
            \" | tail -n +2
            '''.format(DB_USER = DB_USER, DB_PASS = DB_PASS, DB_HOST = DB_HOST, DB_NAME = DB_NAME, id_usuario = id_usuario )
    cursos_en_los_que_esta_matriculado = run_command( command , True).rstrip()
    
    cursos = []    
    
    data_s = io.StringIO(cursos_en_los_que_esta_matriculado).read()
    lines = data_s.splitlines()
    curso = [
        {
            "courseid": line.split()[0],
            "shortname": line.split()[1],
        }
        for line in lines
        # if line.split()[-1].endswith("moodle_1")
    ]
    cursos.extend(curso)
    

    return cursos

def update_moodle_username(moodle, userid, username_nuevo):
    """
    En el moodle dado actualiza el usuario userid a un nuevo username
    """
    print("update_moodle_username(...)")

    command = '''\
            mysql --user=\"{DB_USER}\" --password=\"{DB_PASS}\" --host=\"{DB_HOST}\" -D \"{DB_NAME}\"  --execute=\"
                update mdl_user  
                set username = '{username_nuevo}'
                WHERE id = {userid}
            \"
            '''.format(DB_USER = DB_USER, DB_PASS = DB_PASS, DB_HOST = DB_HOST, DB_NAME = DB_NAME, username_nuevo = username_nuevo, userid = userid )
    run_command( command, False )

def get_date_time():
    """
    return the datetime in format yyyymmddhhmmss
    info from  https://www.programiz.com/python-programming/datetime/strftime
    """
    now = datetime.now() # current date and time
    return now.strftime("%Y%m%d %H%M%S")

def guarda_fichero(nombre_fichero, contenido):
    """
    Guarda en disco duro, en la carpeta logs un fichero con el nombre indicado en parámetro y el contenido dado
    """
    print("guarda_fichero(...)")
    text_file = open("./logs/"+nombre_fichero, "w")
    n = text_file.write(contenido)
    text_file.close()

def get_moodle(subdomain):
    """
    Devuelve un objeto como el siguiente:
    #
    """
    # urls = []
    
    data = os.popen(f"docker ps | grep {subdomain}").read()
    data_s = io.StringIO(data).read()
    lines = data_s.splitlines()
    container = [
        {
            "url": line.split()[-1].replace("adistanciafparagones_moodle_1", ".adistanciafparagon.es"),
            "container_name": line.split()[-1],
        }
        for line in lines
        if line.split()[-1].endswith("moodle_1")
    ]
    # urls.extend(container)

    return container

def run_moosh_command(moodle, command, capture=False):
    #print("run_moosh_command(...)")
    print("command: '", command, "'")
    command_string = f"docker exec {moodle['container_name']} {command}"
    if capture:
        data = os.popen(command_string).read()
        return data
    if not capture:
        os.system(command_string)

def run_command(command, capture=False):
    print("run_command(...)")
    print("command: '", command, "'")
    command_string = command
    if capture:
        data = os.popen(command_string).read()
        return data
    if not capture:
        os.system(command_string)

def desmatricula_alumno_en_curso(moodle, id_alumno, id_curso):
    """
    Dado un alumno y un curso los desmatricula en el moodle dado
    """
    print("desmatricula_alumno_en_curso(...)")

    cmd = "moosh -n course-unenrol " + id_curso + " " + id_alumno
    run_moosh_command(moodle, cmd, False)

def matricula_alumno_en_curso(moodle, id_alumno, id_curso):
    """
    Dado un alumno y un curso los matricula en el moodle dado
    """
    print("matricula_alumno_en_curso(...)")

    cmd = "moosh -n course-enrol -i " + id_curso + " " + id_alumno
    run_moosh_command(moodle, cmd, False)

def get_id_alumno_by_dni(moodle, alumno):
    """
    Dado el dni/nie/... de un alumno (su login) devuelve el id que tiene en moodle
    """
    print("get_id_alumno_by_dni(...)")

    cmd = "moosh -n user-list -n 50000 | grep " + alumno.getDocumento().lower() + " | cut -d \",\" -f 1 | cut -d \"(\" -f 2 | sed 's/)//' "
    id_alumno = run_moosh_command(moodle, cmd, True).rstrip()
    print("id_alumno: ", id_alumno)
    return id_alumno

def is_alumno_matriculado_en_curso(moodle, id_alumno, id_curso):
    """
    Dado un moodle, un id_alumno y un curso devuelve:
    - True si el id_alumno existe en el curso
    - False si el id_alumno no existe en el curso
    """
    print("is_alumno_matriculado_en_curso(...)")

    cmd = "moosh -n user-list --course " + id_curso + " | grep \"(" + id_alumno + ")\" "
    out = run_moosh_command(moodle, cmd, True).rstrip()
    print("out: ", out)
    if out == "":
        return False
    else:
        return True

def send_email(destinatario, asunto, texto):
    """
    Al destinatario envía un email con el asunto y texto dados
    """
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(SMTP_HOSTS, SMTP_PORT, context=context) as server:
        try:
            server = smtplib.SMTP_SSL(SMTP_HOSTS, SMTP_PORT,context=context)
            server.login(SMTP_USER, SMTP_PASSWORD)
            message = f"Subject: {asunto}\n\n{texto}"
            server.sendmail(
                SMTP_USER, 
                destinatario, 
                message
            )
        except:
            print("Error de autenticación")
        finally:
            server.quit()

def delete_alumno_moodle(alumnoMoodle, moodle):
    """
    Borra del moodle dado el alumno dado
    """
    print("delete_alumno_moodle(...)")

    # 
    cmd = "moosh -n user-delete " + alumnoMoodle['username']
    
    run_moosh_command(moodle, cmd, False)
    #
    # End of delete_alumno_moodle
    #

def get_id_de_curso_by_shortname(moodle, shortname):
    """
    Dado un moodle y un shotname devuelve el id del curso si el mismo existe
    """
    print("get_id_de_curso_by_shortname(...)")
    cmd = "moosh -n course-list \"shortname = '" + shortname + "'\" | tail -n 1 | cut -d \",\" -f1 | sed 's/\"//' | sed 's/\"//' " 
    id_course = run_moosh_command(moodle, cmd, True).rstrip()

    print("id_course: ", id_course)

    return id_course

def get_alumnos_moodle_no_borrados(moodle):
    print("get_alumnos_moodle_no_borrados(...)")
    """
    Devuelve una lista de alumnos (omite usuarios con username que empiece por prof) que actualmente están en moodle:
    #
    """
    cmd = "moosh -n user-list -n 50000 \"deleted = 0 and username not like 'prof%' \" " #listado de usuarios limitado a 50.000 # username (id), email,
    alumnos_moodle = run_moosh_command(moodle, cmd, True)
    
    alumnos = []    
    
    data_s = io.StringIO(alumnos_moodle).read()
    lines = data_s.splitlines()
    alumno = [
        {
            "username": line.split()[0],
            "userid": line.split()[1].replace("(","").replace("),",""),
            "email": line.split()[2].replace(",",""),
        }
        for line in lines
        # if line.split()[-1].endswith("moodle_1")
    ]
    alumnos.extend(alumno)
    

    return alumnos

def get_cursos(moodle):
    print("get_cursos(...)")
    """
    Devuelve una lista de los cursos que existen en moodle
    #
    """
    cmd = "moosh -n course-list | tail -n +2" 
    cursos_moodle = run_moosh_command(moodle, cmd, True)
    
    cursos = []    
    
    data_s = io.StringIO(cursos_moodle).read()
    lines = data_s.splitlines()
    curso = [
        {
            "courseid": line.split("\",\"")[0].replace("\"","").lstrip(),
            "category": line.split("\",\"")[1].rstrip(),
            "shortname": line.split("\",\"")[2].lstrip(),
            "fullname": line.split("\",\"")[3].rstrip(),
            "visible": line.split("\",\"")[4].replace("\"","").rstrip(),
        }
        for line in lines
        # if line.split()[-1].endswith("moodle_1")
    ]
    cursos.extend(curso)
    

    return cursos    

def procesaJsonEstudiantes(y, alumnos_sigad):
    """
    Procesa el fichero JSON obteniendo los alumnos y que estudian y los
    añade a alumnos_sigad
    """
    estudiantes=y["estudiantes"]
    # print( "type(estudiantes): ", type(estudiantes) ) # str
    estudiantesJson=json.loads(estudiantes)
    # print( "type(estudiantesJson: ",type(estudiantesJson) ) # dict

    fecha=estudiantesJson["fecha"]
    hora=estudiantesJson["hora"]
    alumnos=estudiantesJson["alumnos"]

    # print("fecha: " + str(fecha) + " y hora: " + str(hora) + " de creación del fichero")
    i = 0
    for alumno in alumnos:
        # print("i: ", i)
        # print("type(alumno): ", type(alumno) ) # dict
        idAlumno = alumno["idAlumno"]
        idTipoDocumento = alumno["idTipoDocumento"]
        documento = alumno["documento"]
        nombre = alumno["nombre"]
        apellido1 = alumno["apellido1"]
        apellido2 = alumno["apellido2"]
        email = alumno["email"]
        centros = alumno["centros"]
        # print( "type(centros): ", type(centros) ) # list
        # print( "len(centros): ", len(centros) ) # 
        # creo el objeto
        miAlumno = Alumno(idAlumno, idTipoDocumento, documento, nombre, 
                apellido1, apellido2, email)
        # miAlumno.toText()
        #
        j=0
        for centro in centros:
            # print("  i: " + str(i) + ", j: " + str(j) + ", centro: " + str(centro) )
            # print("type(centro): ", type(centro) ) # dict

            codigoCentro = centro["codigoCentro"]
            centroo = centro["centro"]
            ciclos=centro["ciclos"]
            # print("ciclos: ", ciclos)
            # print("type(ciclos): ", type(ciclos) ) # str

            miCentro = Centro(codigoCentro, centroo)

            k = 0
            for ciclo in ciclos:
                # print("    i: ", i, ", j: ", j, ", k: ", k, ", ciclo: ", ciclo )
                # print("type(ciclo): ", type(ciclo) ) # dict
                
                idFicha = ciclo["idFicha"]
                codigoCiclo = ciclo["codigoCiclo"]
                cicloo = ciclo["ciclo"]
                siglasCiclo = ciclo["siglasCiclo"]
                modulos = ciclo["modulos"]

                miCiclo = Ciclo(idFicha, codigoCiclo, cicloo, siglasCiclo)

                l = 0
                for modulo in modulos:
                    #
                    idMateria = modulo["idMateria"]
                    moduloo = modulo["modulo"]
                    siglasModulo = modulo["siglasModulo"]
                    #
                    miModulo = Modulo(idMateria, moduloo, siglasModulo)
                    #
                    miCiclo.addModulo(miModulo)
                #
                miCentro.addCiclo(miCiclo)
            # Add miCentro to miAlumno
            miAlumno.addCentro(miCentro)
        # Add miAlumno to alumnos_sigad
        alumnos_sigad.append(miAlumno)
    #
    # End of procesaJsonEstudiantes
    #

def existeAlumnoEnMoodle(moodle, alumno):
    """
    Comprueba si el alumno dado existe en moodle
    Devuelve true si existe
    Devuelve false si no existe
    """
    print("existeAlumnoEnMoodle(...)")

    # moosh -n  user-list "username = 'estudiante1'"
    cmd = "moosh -n user-list \"username = '"+ alumno.getDocumento().lower() +"'\""
    
    username = run_moosh_command(moodle, cmd, True)

    if username == "":
        return False
    return True
    #
    # End of existeAlumnoEnMoodle
    #

def crearAlumnoEnMoodle(moodle, alumno):
    """
    Crea un usuario en moodle con los datos del objeto alumno
    Devuelve el id del alumno creado
    """
    print("crearAlumnoEnMoodle(...)")
    alumno_creable = True
    if alumno.getEmail() is None:
        print("El alumno a crear no tiene email")
        alumno_creable = False
    if alumno.getNombre() is None:
        print("El alumno a crear no tiene nombre")
        alumno_creable = False
    if alumno.getApellidos() is None:
        print("El alumno a crear no tiene apellidos")
        alumno_creable = False
    if alumno.getDocumento() is None:
        print("El alumno a crear no tiene documento")
        alumno_creable = False

    if alumno_creable:
        cmd = "moosh -n user-create --password changeme --email " + alumno.getEmail() \
            + " --digest 2 --city Aragón --country ES --firstname \"" +  alumno.getNombre() \
            + "\" --lastname \"" +  alumno.getApellidos() + "\" " \
            + alumno.getDocumento().lower()

        idUser = run_moosh_command(moodle, cmd, True).rstrip()

        print("idUser: '",idUser,"'")

        return idUser
    else:
        raise ValueError
    #
    # End of crearAlumnoEnMoodle
    #

###################################################
# Lanzamos!
###################################################
main()