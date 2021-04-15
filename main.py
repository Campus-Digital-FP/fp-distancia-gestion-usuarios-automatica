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
    moodle = get_moodle(SUBDOMAIN)[0]
    alumnosFicheroJson = []
    alumnosMoodle = get_alumnos_moodle(moodle) # Alumnos que figuran en moodle antes de ejecutar el script
    
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
                        procesaJsonEstudiantes(y, alumnosFicheroJson)
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
    for alumnoMoodle in alumnosMoodle:
        existe = False
        # comprobamos si existe por dni/nie/... o si es profesor
        for alumnoSIGAD in alumnosFicheroJson:
            if alumnoMoodle['username'].lower() == alumnoSIGAD.getDocumento().lower() \
                    or alumnoMoodle['username'].lower().startswith("prof") :
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
    alumnos_a_borrar = [ ] # los que no haya que actualizar son para borrar, irán aquí
    for alumnoMoodle in alumnos_en_moodle_pero_no_SIGAD:
        existe = False
        # comprobamos si existe por email
        for alumnoSIGAD in alumnosFicheroJson:
            if alumnoSIGAD.getEmail() is not None \
                    and alumnoMoodle['email'].lower() == alumnoSIGAD.getEmail().lower():
                existe = True
                # TODO: A este alumno de moodle habrá que ponerle el nuevo id que tenga en SIGAD
                print("- Alumno a actualizar su login por coincidencia de email: ", repr(alumnoMoodle) )
                print("habría que ponerle de login ", alumnoSIGAD.getDocumento() )
                break
        if not existe:
            alumnos_a_borrar.append(alumnoMoodle)

    usuarios_moodle_no_borrables = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] # ids de users creados en deploy que no hay que borrar
    print("*** Alumnos a eliminar de Moodle")
    
    for alumnoMoodle in alumnos_a_borrar:
        print("- ", repr(alumnoMoodle) )
        if alumnoMoodle['userid'] not in usuarios_moodle_no_borrables:
            delete_alumno_moodle(alumnoMoodle, moodle)
        else:
            print("NO se borra")
    
    ########################
    # Desmatriculo a aquellos alumnos que SIGAD me dice ya no deberían estar matriculados en un determinado curso
    # Obtengo y recorro los usuarios de moodle. 
    # Itero sobre los alumnos y obtengo en qué están matriculados en moodle:
    # - si están matriculados en algo en que no estén matriculados en SIGAD los desmatriculo
    # excepto si el shortname del curso termina en t (módulo de tutoría del ciclo)
    ########################
    alumnosMoodle = get_alumnos_moodle(moodle) # No me vale valor anterior pues contendrá alumnos
    for alumnoMoodle in alumnosMoodle:
        if not alumnoMoodle['username'].lower().startswith("prof"): # es alumno, lo proceso
            # TODO
            print("TODO: Habría que comprobar en que cursos está actualmente matriculado el usuario de moodle ", alumnoMoodle['username'], " (", alumnoMoodle['userid'] ,")" )
            

    ########################
    # Proceso el fichero JSON (foto de SIGAD)
    # - si un alumno del fichero no existe en moodle lo creo
    # - matriculo a un alumno en los cursos que tenga asignados en SIGAD
    ########################
    for alumno in alumnosFicheroJson:
        # print("-", repr(alumno) )
        id_alumno = ""
        # Creo en moodle los alumnos que estén en el json y no estén en moodle
        if not existeAlumnoEnMoodle(moodle, alumno):
            id_alumno = crearAlumnoEnMoodle(moodle, alumno)
        else:
            id_alumno = get_id_alumno_by_dni(moodle, alumno)
        
        # Revisar si está matriculado dónde corresponda y matricular
        for centro in alumno.getCentros():
            codigo_centro = centro.get_codigo_centro()
            for ciclo in centro.getCiclos():
                siglas_ciclo = ciclo.get_siglas_ciclo()
                for modulo in ciclo.getModulos():
                    id_materia = modulo.get_id_materia()

                    shortname_curso = str(codigo_centro) + "-" + str(siglas_ciclo) + "-" + str(id_materia)

                    if not is_alumno_matriculado_en_curso(moodle, id_alumno, shortname_curso):
                        id_curso = get_id_de_curso_by_shortname(moodle, shortname_curso)
                        matricula_alumno_en_curso(moodle, id_alumno, id_curso)
                        
    ########################
    # Envío email resumen de lo hecho por email a responsables
    ########################
    # TODO # send_email("fp@catedu.es", "asunto", "Hello world!")

    #
    # End of main 
    # 

def get_date_time():
    """
    return the datetime in format yyyymmddhhmmss
    info from  https://www.programiz.com/python-programming/datetime/strftime
    """
    now = datetime.now() # current date and time
    return now.strftime("%Y%m%d%H%M%S")

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
    print("run_moosh_command(...)")
    print("command: '", command, "'")
    command_string = f"docker exec {moodle['container_name']} {command}"
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
    out = run_moosh_command(moodle, cmd, False)

def matricula_alumno_en_curso(moodle, id_alumno, id_curso):
    """
    Dado un alumno y un curso los matricula en el moodle dado
    """
    print("matricula_alumno_en_curso(...)")

    cmd = "moosh -n course-enrol -i " + id_curso + " " + id_alumno
    out = run_moosh_command(moodle, cmd, False)

def get_id_alumno_by_dni(moodle, alumno):
    """
    Dado el dni/nie/... de un alumno (su login) devuelve el id que tiene en moodle
    """
    print("get_id_alumno_by_dni(...)")

    cmd = "moosh -n user-list | grep " + alumno.getDocumento().lower() + " | cut -d \",\" -f 1 | cut -d \"(\" -f 2 | sed 's/)//' "
    id_alumno = run_moosh_command(moodle, cmd, True).rstrip()
    print("id_alumno: ", id_alumno)
    return id_alumno

def is_alumno_matriculado_en_curso(moodle, id_alumno, shortname):
    """
    Dado un moodle, un id_alumno y un curso devuelve:
    - true si el id_alumno existe en el curso
    - false si el id_alumno no existe en el curso
    """
    print("is_alumno_matriculado_en_curso(...)")
    id_curso = get_id_de_curso_by_shortname(moodle, shortname)

    cmd = "moosh -n user-list --course " + id_curso + " | grep \"(" + id_alumno + ")\" "
    out = run_moosh_command(moodle, cmd, True)
    print("out: ", out)

def send_email(destinatario, asunto, texto):
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
    cmd = "moosh -n course-list \"shortname = '" + shortname + "'\" | tail -n 1 | cut -d \",\" -f1 | sed 's/\"//' | sed 's/\"//' " 
    course_info = run_moosh_command(moodle, cmd, True).rstrip()

    print("course_info: ", course_info)

    return course_info

def get_alumnos_moodle(moodle):
    print("get_alumnos_moodle(...)")
    """
    Devuelve una lista de usuarios que actualmente están en moodle:
    #
    """
    cmd = "moosh -n user-list -n 50000" #listado de usuarios limitado a 50.000 # username (id), email,
    alumnosMoodle = run_moosh_command(moodle, cmd, True)
    
    alumnos = []    
    
    data_s = io.StringIO(alumnosMoodle).read()
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

def procesaJsonEstudiantes(y, alumnosFicheroJson):
    """
    Procesa el fichero JSON obteniendo los alumnos y que estudian y los
    añade a alumnosFicheroJson
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
        # Add miAlumno to alumnosFicheroJson
        alumnosFicheroJson.append(miAlumno)
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
    cmd = "moosh -n user-create --password changeme --email " + alumno.getEmail() \
        + " --digest 2 --city Aragón --country ES --firstname \"" +  alumno.getNombre() \
        + "\" --lastname \"" +  alumno.getApellidos() + "\" " \
        + alumno.getDocumento().lower()

    idUser = run_moosh_command(moodle, cmd, True)

    print("idUser: '",idUser,"'")
    print("idUser: '",int(idUser),"'")

    return idUser
    #
    # End of crearAlumnoEnMoodle
    #

###################################################
# Lanzamos!
###################################################
main()