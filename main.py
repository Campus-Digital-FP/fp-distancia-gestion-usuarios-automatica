#Import the modules
import requests
import json
import time
import urllib.parse
import xml.dom.minidom
import random
import subprocess
import os
import sys
import io
import smtplib
import ssl
import traceback
from datetime import datetime
from Config import *
from Conexion import *
from classes.Alumno import *
from classes.Centro import *
from classes.Ciclo import *
from classes.Modulo import *
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def main():
    #
    mensajes_email = []
    #
    mensajes_email.append("<html><head><title></title></head><body>")
    mensajes_email.append("<h1>" + get_date_time_for_humans() + " Comenzamos:</h1>")
    mensajes_email.append("<b>ENTORNO:</b>")
    mensajes_email.append(SUBDOMAIN)
    mensajes_email.append("<b>RESUMEN DETALLADO</b>")
    usuarios_moodle_no_borrables = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17] # ids de users creados en deploy que no hay que borrar
    # 
    moodle = get_moodle(SUBDOMAIN)[0]
    alumnos_sigad = []
    alumnos_moodle = get_alumnos_moodle_no_borrados(moodle) # Alumnos que figuran en moodle antes de ejecutar el script
    # contadores
    num_alumnos_pre_app = 0
    num_alumnos_post_script = 0
    num_alumnos_suspendidos = 0
    num_alumnos_reactivados = 0
    num_alumnos_modificado_login = 0
    num_alumnos_creados = 0
    num_alumnos_no_creables = 0
    num_modulos_matriculados = 0
    num_matriculas_suspendidas = 0
    num_matriculas_reactivadas = 0
    num_matriculas_borradas = 0
    num_alumnos_no_matriculados_en_cursos_inexistentes = 0
    num_emails_enviados = 0
    num_emails_no_enviados = 0
    num_tutorias_suspendidas = 0
    #
    num_alumnos_pre_app = len(alumnos_moodle)

    #########################################
    # Obtengo curso académico que debo usar
    #########################################
    curso_academico = get_curso_para_REST()
    
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
        guarda_fichero(get_date_time() + "." + SUBDOMAIN + ".ws1.log", str(resp_data) )
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
                    guarda_fichero(get_date_time() + "." + SUBDOMAIN + ".ws2.log", str(resp_data) )
                    if codigo == 0: # éxito de la 2nda llamada
                        procesaJsonEstudiantes(y, alumnos_sigad)
                        break
                    else: # Error  en la 2ª llamada
                        print("Fichero aún no listo. Código: " + str(codigo) 
                            + ", mensaje: " + str(mensaje))
        else: # Error en la 1era llamada
            print("Error en la llamada al 1er web service")

    ########################
    # Obtengo los alumnos (profesores no) que están suspendidos en moodle y miro si están en el fichero de SIGAD
    # Si están en el fichero de SIGAD los reactivo
    ########################
    mensajes_email.append("<br/>")
    mensajes_email.append(get_date_time_for_humans() + "*** <b>Estudiantes suspendidos en Moodle pero que están en el fichero de SIGAD (habria que reactivar)</b>:")
    mensajes_email.append("<br/>")
    alumnos_suspendidos = get_alumnos_suspendidos(moodle)
    for alumnoMoodle in alumnos_suspendidos:
        # comprobamos si existe por dni/nie/...
        for alumnoSIGAD in alumnos_sigad:
            if alumnoMoodle['username'] is not None \
                    and alumnoSIGAD.getDocumento() is not None \
                    and alumnoMoodle['username'].lower() == alumnoSIGAD.getDocumento().lower():
                reactiva_usuario( moodle, alumnoMoodle['userid'] )
                mensajes_email.append("Estudiante '"+ alumnoMoodle['userid']+ "' reactivado")
                matricula_alumno_en_cohorte_alumnado(moodle, alumnoMoodle['userid'] )
                num_alumnos_reactivados = num_alumnos_reactivados + 1
                break

    ########################
    # Localizo los alumnos (los profesores no) que estén en moodle y no en SIGAD (en base a su dni/nie/...)
    ########################
    alumnos_en_moodle_pero_no_SIGAD = [  ]
    for alumnoMoodle in alumnos_moodle:
        existe = False
        # comprobamos si existe por dni/nie/...
        for alumnoSIGAD in alumnos_sigad:
            if alumnoSIGAD.getDocumento() is None:
                continue
                
            if alumnoMoodle['username'].lower() == alumnoSIGAD.getDocumento().lower():
                existe = True
                break
        
        if not existe:
            alumnos_en_moodle_pero_no_SIGAD.append(alumnoMoodle)
            
    print("*** Alumnos que estan en moodle y no en SIGAD:")
    mensajes_email.append("<br/>")
    mensajes_email.append(get_date_time_for_humans() + "*** <b>Alumnos que estan en moodle y no en SIGAD</b>:")
    mensajes_email.append("<br/>")
    for alumnoMoodle in alumnos_en_moodle_pero_no_SIGAD:
        print("alumnoMoodle: ", alumnoMoodle)
        mensajes_email.append("alumnoMoodle: " + str(alumnoMoodle) )
    
    ########################
    # De cada alumno que esté en moodle y no en sigad miro si en moodle hay alguien con ese email
    # - si hay alguien con ese email considero que es la misma persona a la que han actualizado DNI/NIE/... en SIGAD y la actualizo
    # - si no hay nadie con ese email considero que es una baja y lo suspendo
    ########################
    print("*** Alumnos que habría que actualizar su id:")
    mensajes_email.append("<br/>")
    mensajes_email.append( get_date_time_for_humans() + " ***** <b>Alumnos a los que se ha actualizado su login</b>:")
    mensajes_email.append("<br/>")
    alumnos_a_suspender = [ ] # los que no haya que actualizar son para suspender, irán aquí
    for alumnoMoodle in alumnos_en_moodle_pero_no_SIGAD:
        existe = False
        # comprobamos si existe por email
        for alumnoSIGAD in alumnos_sigad:
            if alumnoSIGAD.getEmail() is not None \
                    and alumnoMoodle['email'].lower() == alumnoSIGAD.getEmail().lower():
                existe = True
                print("- Alumno a actualizar su login por coincidencia de email: ", repr(alumnoMoodle) )
                print("habría que ponerle de login ", alumnoSIGAD.getDocumento() )
                userid = alumnoMoodle['userid']
                username_nuevo = alumnoSIGAD.getDocumento().lower()
                update_moodle_username(moodle, userid, username_nuevo)
                num_alumnos_modificado_login = num_alumnos_modificado_login + 1
                mensajes_email.append("- Al alumno que tenia usuario de acceso " + alumnoMoodle['username'] + \
                        " se le ha cambiado a " + alumnoSIGAD.getDocumento() + \
                        "(" + alumnoSIGAD.getEmail().lower() + ").")
                # Le envío email avisándolede su cambio de usuario 
                usuario = alumnoSIGAD.getDocumento()
                oldUsuario = alumnoMoodle['username']
                mensaje = '''Hola,<br/><br/>su cuenta en https://{subdomain}.adistanciafparagon.es/ se ha actualizado.<br/><br/>Su nuevo usuario es: <b>{usuario}</b> en lugar de {oldUsuario}.<br/>Su contrase&ntilde;a NO ha sido modificada.<br/><br/>Recuerde que puede recuperar su contrase&ntilde;a en cualquier momento a trav&eacute;s de https://{subdomain}.adistanciafparagon.es/login/forgot_password.php<br/>No responda a esta cuenta de correo electr&oacute;nico pues se trata de una cuenta automatizada no atendida. En caso de cualquier problema consulte con su coordinador/a de ciclo o acuda a la secci&oacute;n de <a href="https://{subdomain}.adistanciafparagon.es/soporte/">ayuda/incidencias</a>.<br/><br/><br/>Saludos<br/><br/>------<br/>FP distancia Arag&oacute;n'''.format(subdomain = SUBDOMAIN, usuario = usuario, oldUsuario = oldUsuario )
                
                destinatario = "fp@catedu.es"
                if SUBDOMAIN == "www":
                    destinatario = alumnoSIGAD.getEmail().lower()
                else:
                    print("Debería haberse enviado a '", alumnoSIGAD.getEmail().lower(), "'." )

                enviado = send_email( destinatario , "FP a distancia - Aragón", mensaje)

                if enviado:
                    num_emails_enviados = num_emails_enviados + 1
                    print("num_emails_enviados: ", num_emails_enviados)
                else:
                    num_emails_no_enviados = num_emails_no_enviados + 1
                    print("Ha fallado el envío del email a '", destinatario, "'. Total fallos: '", num_emails_no_enviados, "'")

                break
        if not existe:
            alumnos_a_suspender.append(alumnoMoodle)

    
    print("*** Alumnos a suspender totalmente de Moodle")
    mensajes_email.append("<br/>")
    mensajes_email.append( get_date_time_for_humans() + " ***** <b>Estudiantes a suspender totalmente de Moodle al no estar en SIGAD, 1ero matrículas y 2ndo a ellos</b>:")
    mensajes_email.append("<br/>")
    for alumnoMoodle in alumnos_a_suspender:
        print("- ", repr(alumnoMoodle) )
        if int(alumnoMoodle['userid']) not in usuarios_moodle_no_borrables:
            # Antes de suspender a un alumno hay que suspender todas sus matrículas en cursos
            # pero HAY QUE mantenerlo en las cohortes ya que sacarlo puede borrar su progreso
            id_alumno = int(alumnoMoodle['userid'])
            cursos = get_cursos_en_que_esta_matriculado_un_alumno(moodle, id_alumno)
            mensajes_email.append("- Procesando a: " + repr(alumnoMoodle) )
            for curso in cursos:
                courseid = curso['courseid']
                suspende_matricula_en_curso(moodle, id_alumno, courseid)
                mensajes_email.append("--- id_alumno: " + str(id_alumno) + " matrícula suspendida en id_curso: " + str(courseid) )
                num_matriculas_suspendidas = num_matriculas_suspendidas + 1
            #

            # desmatricula_alumno_de_todas_cohortes(moodle, id_alumno) desmatricularlo de las cohortes hace que se pierda su progreso
            # mensajes_email.append("--- cohortes en las que figuraba eliminado:")
            suspende_alumno_moodle(alumnoMoodle['userid'], moodle)
            num_alumnos_suspendidos = num_alumnos_suspendidos + 1
            mensajes_email.append("--- estudiante suspendido")
            
            
        else:
            print("Alumno configurado como NO borrable")
    
    ########################
    # Suspendo la matrícula en un curso de Moodle a aquellos alumnos que SIGAD me dice ya no deberían estar matriculados en un determinado curso
    # Los mantengo en las cohortes
    # Obtengo y recorro los usuarios de moodle. 
    # Itero sobre los alumnos y obtengo en qué están matriculados en moodle:
    # - si están matriculados en algo en que no estén matriculados en SIGAD les suspendo la matrícula
    # excepto si el shortname del curso termina en t (módulo de tutoría del ciclo)
    ########################
    alumnos_moodle = get_alumnos_moodle_no_borrados(moodle) 
    cursos_moodle = get_cursos(moodle)
    mensajes_email.append("<br/>")
    mensajes_email.append( get_date_time_for_humans() + " ***** <b>Alumnos a los que se ha suspendido su matrícula en algún curso pero no a ellos</b>:")
    mensajes_email.append("<br/>")
    for alumno_moodle in alumnos_moodle:
        print(get_date_time_for_humans() + "*** Procesando alumno de Moodle ***")
        print("-", alumno_moodle['username'] )
        userid = alumno_moodle['userid']
        # no recorro los no borrables
        if int(userid) in usuarios_moodle_no_borrables: 
            continue
        username = alumno_moodle['username']
        # Obtengo los cursos en que este alumno moodle está matriculado en moodle
        cursos_matriculado = get_cursos_en_que_esta_matriculado(moodle, userid)
        print("Acualmente se encuentra matriculado en ", cursos_matriculado)
        # recorro los cursos en que el usuario de moodle está matriculado y miro si el usuario de sigad está matriculado en el curso o no
        for curso in cursos_matriculado:
            print("Procesando curso ", curso)
            courseid = curso['courseid']
            course_shortname = curso['shortname']
            course_codes = course_shortname.split("-") # 0 centreid 1 siglas ciclo 2 codigo materia

            # Si el curso es el de ayuda omitir comprobación. Están matriculados vía cohorte
            if course_shortname == "ayuda":
                continue;
            # Si el curso es el de tutoría omitir comprobación. Están matriculados vía cohorte
            if course_codes[2].count("t") == 1:
                continue;
            
            for alumno in alumnos_sigad:
                
                en_sigad_esta_matriculado = False
                if alumno.getDocumento() is not None and alumno.getDocumento().lower() == username.lower(): # he encontrado al alumno en SIGAD
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
                                    if modulos is not None:
                                        for modulo in modulos:
                                            if en_sigad_esta_matriculado:
                                                break
                                            if int(course_codes[2]) == modulo.get_id_materia(): #he llegado al módulo
                                                en_sigad_esta_matriculado = True
                                                print("En SIGAD el alumno", username, "SI está matriculado en", course_shortname, "se le mantiene matriculado en moodle")
                                    else:
                                        print("***No está en ningún módulo")
                                else:
                                    continue;
                        else:
                            continue
                    if not en_sigad_esta_matriculado:
                        print("En SIGAD el alumno", username, "NO está matriculado en", course_shortname, "se procede a suspender su matrícula en el curso de moodle")
                        suspende_matricula_en_curso(moodle, userid, courseid)
                        # NO hay que sacarlo de la cohorte, eso borra progreso
                        mensajes_email.append("- " + username + "  matricula suspendida en " + course_shortname)
                        num_matriculas_suspendidas = num_matriculas_suspendidas + 1
                    break # una vez he procesado al alumno no tiene sentido seguir mirando los demás alumnos de SIGAD
    
    ########################
    # Proceso el fichero JSON (foto de SIGAD)
    # - si un alumno del fichero no existe en moodle lo creo
    # - matriculo a un alumno en los cursos que tenga asignados en SIGAD
    ########################
    mensajes_email.append("<br/>")
    mensajes_email.append( get_date_time_for_humans() + " ***** <b>Alumnos creados y matriculados</b>:")
    mensajes_email.append("<br/>")
    usuarios_no_creables = [ ]
    # Creo diccionario de id_cursoshortname para evitar usar get_id_de_curso_by_shortname en cada iteración
    diccionario_cursos = {curso['shortname'] : curso['courseid'] for curso in cursos_moodle}
    diccionario_alumnos = {alumno['username'] : alumno['userid'] for alumno in alumnos_moodle}
    #
    for alumno in alumnos_sigad:
        if num_emails_enviados >= 1900: # limitacion de 2.000 emails diarios en actual cuenta de gmail
            mensajes_email.append("<br/>")
            mensajes_email.append(" ALCANZADO LÍMITE DE ENVÍO DE EMAILS DIARIOS ")
            mensajes_email.append(" ALCANZADO LÍMITE DE ENVÍO DE EMAILS DIARIOS ")
            mensajes_email.append(" ALCANZADO LÍMITE DE ENVÍO DE EMAILS DIARIOS ")
            mensajes_email.append("<br/>")
            break 
        print(get_date_time_for_humans() + "*** Procesando alumno de fichero JSON ***")
        print("-", repr(alumno) )
        id_alumno = ""
        alumno_es_nuevo = False
        # Creo en moodle los alumnos que estén en el json y no estén en moodle
        if not existeAlumnoEnMoodle(moodle, alumno):
            print("Es nuevo")
            password = random_pass(10)
            try:
                id_alumno = crearAlumnoEnMoodle(moodle, alumno, password)
                num_alumnos_creados = num_alumnos_creados + 1
                mensajes_email.append("- Alumno " + alumno.getDocumento() + " creado.")
                matricula_alumno_en_cohorte_alumnado(moodle, id_alumno)
                alumno_es_nuevo = True
            except ValueError as e:
                usuarios_no_creables.append(alumno)
                continue
        else:
            print("Ya existía en moodle")
            #id_alumno = get_id_alumno_by_dni(moodle, alumno)
            id_alumno = diccionario_alumnos[ alumno.getDocumento().lower().rstrip() ]
            print("Tenía el id_alumno:", id_alumno);
        
        matriculado_en = [ ]
        # Revisar si está matriculado dónde corresponda y matricular
        for centro in alumno.getCentros():
            codigo_centro = centro.get_codigo_centro()
            for ciclo in centro.getCiclos():
                siglas_ciclo = ciclo.get_siglas_ciclo()
                matricula_alumno_en_cohorte(moodle, id_alumno, codigo_centro, siglas_ciclo)
                if ciclo.getModulos() is not None:
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
                            mensajes_email.append("- Alumno "+ alumno.getDocumento()+ " NO puede matricularse en "+ shortname_curso + " por que el curso NO existe.")
                            num_alumnos_no_matriculados_en_cursos_inexistentes = num_alumnos_no_matriculados_en_cursos_inexistentes + 1
                        elif is_alumno_suspendido_en_curso(moodle, id_curso, id_alumno):
                            reactiva_alumno_en_curso(moodle, id_alumno, id_curso)
                            num_matriculas_reactivadas = num_matriculas_reactivadas + 1;
                            mensajes_email.append("- Alumno "+ alumno.getDocumento()+ " reactivada su matricula en "+ shortname_curso + ".")
                            matriculado_en.append("- " + centro.get_centro() + " - " + ciclo.get_ciclo() + " - " + modulo.get_modulo() )
                        elif not is_alumno_matriculado_en_curso(moodle, id_alumno, id_curso):
                            matricula_alumno_en_curso(moodle, id_alumno, id_curso)
                            num_modulos_matriculados = num_modulos_matriculados + 1
                            mensajes_email.append("- Alumno "+ alumno.getDocumento()+ " matriculado en "+ shortname_curso + ".")
                            matriculado_en.append("- " + centro.get_centro() + " - " + ciclo.get_ciclo() + " - " + modulo.get_modulo() )
                        else:
                            print("El alumno (",id_alumno,") ya estaba matriculado en ", shortname_curso, sep="")
        # envío email
        if alumno_es_nuevo:
            matriculado_en_texto = "<br/>".join( map(return_text_for_html, matriculado_en) )
            nombre = return_text_for_html( alumno.getNombre() )
            apellidos = return_text_for_html( alumno.getApellidos() )
            mensaje = '''Bienvenido/a {nombre} {apellidos},<br/><br/>su cuenta se ha creado en https://{subdomain}.adistanciafparagon.es/ y sus datos de acceso son los siguientes:<br/><br/>usuario: <b>{usuario}</b><br/>contrase&ntilde;a: <b>{contrasena}</b> (es recomendable que la cambie)<br/><br/>Ha sido matriculado/a en:<br/>{matriculado_en_texto}<br/><br/>Puede recuperar su contrase&ntilde;a en cualquier momento a trav&eacute;s de https://{subdomain}.adistanciafparagon.es/login/forgot_password.php<br/>No responda a esta cuenta de correo electr&oacute;nico pues se trata de una cuenta automatizada no atendida. En caso de cualquier problema consulte con su coordinador/a de ciclo o acuda a la secci&oacute;n de <a href="https://{subdomain}.adistanciafparagon.es/soporte/">ayuda/incidencias</a>.<br/><br/><br/>Saludos<br/><br/>------<br/>FP distancia Arag&oacute;n'''.format(nombre = nombre, apellidos = apellidos, subdomain = SUBDOMAIN, usuario = alumno.getDocumento().lower(), contrasena = password, matriculado_en_texto = matriculado_en_texto )
            
            destinatario = "fp@catedu.es"
            if SUBDOMAIN == "www":
                destinatario = alumno.getEmail()
            else:
                print("Debería haberse enviado a '", alumno.getEmail(), "'." )

            enviado = send_email( destinatario , "FP a distancia - Aragón", mensaje)

            if enviado:
                num_emails_enviados = num_emails_enviados + 1
                print("num_emails_enviados: ", num_emails_enviados)
            else:
                num_emails_no_enviados = num_emails_no_enviados + 1
                print("Ha fallado el envío del email a '", destinatario, "'. Total fallos: '", num_emails_no_enviados, "'")
            
            
        else:
            if len(matriculado_en) > 0:
                matriculado_en_texto = "<br/>".join( map(return_text_for_html, matriculado_en) )
                nombre = return_text_for_html( alumno.getNombre() )
                apellidos = return_text_for_html( alumno.getApellidos() )
                mensaje = '''Hola {nombre} {apellidos},<br/><br/>a su cuenta en https://{subdomain}.adistanciafparagon.es/ se le han a&ntilde;adido las siguientes matr&iacute;culas:<br/><br/>{matriculado_en_texto}<br/><br/>Puede recuperar su contrase&ntilde;a en cualquier momento a trav&eacute;s de https://{subdomain}.adistanciafparagon.es/login/forgot_password.php<br/>No responda a esta cuenta de correo electr&oacute;nico pues se trata de una cuenta automatizada no atendida. En caso de cualquier problema consulte con su coordinador/a de ciclo o acuda a la secci&oacute;n de <a href="https://{subdomain}.adistanciafparagon.es/soporte/">ayuda/incidencias</a>.<br/><br/><br/>Saludos<br/><br/>------<br/>FP distancia Arag&oacute;n'''.format(nombre = nombre, apellidos = apellidos, subdomain = SUBDOMAIN, matriculado_en_texto = matriculado_en_texto )

                destinatario = "fp@catedu.es"
                if SUBDOMAIN == "www":
                    destinatario = alumno.getEmail()
                else:
                    print("Debería haberse enviado a '", alumno.getEmail(), "'." )
                
                enviado = send_email( destinatario , "FP a distancia - Aragón", mensaje)

                if enviado:
                    num_emails_enviados = num_emails_enviados + 1
                    print("num_emails_enviados: ", num_emails_enviados)
                else:
                    num_emails_no_enviados = num_emails_no_enviados + 1
                    print("Ha fallado el envío del email a '", destinatario, "'. Total fallos: '", num_emails_no_enviados, "'")

    # Evaluo alumnos con 2 tutorías o mas y los comparo con el fichero json origen a ver si están en las tutorías que les corresponde estar
    # suspendo las matrículas de las tutorías que no corresponda
    num_tutorias_suspendidas = eval_estudiantes_con_mas_de_1_tutorias(moodle, alumnos_sigad,mensajes_email)
    
    # Listo alumnos que no se han podido crear
    mensajes_email.append("<br/>")
    mensajes_email.append( get_date_time_for_humans() + " <b>***** Alumnos que no se han podido crear</b>:")
    mensajes_email.append("<br/>")
    print("Alumnos de SIGAD que no se han podido crear en Moodle: ")
    for alumno in usuarios_no_creables:
        print( "- ", repr(alumno) )
        mensajes_email.append("- " + repr(alumno) )
        num_alumnos_no_creables = num_alumnos_no_creables + 1

    ########################
    # En agosto todas las matrículas que están suspendidas las borramos
    ########################
    mes = get_mes()
    if mes == "08": 
        print("Agosto: se borran todas las matrículas suspendidas")
        matriculas = get_alumnos_con_matriculas_suspendidas_en_curso(moodle)
        for matricula in matriculas:
            courseid = matricula['courseid']
            studentid = matricula['studentid']
            desmatricula_alumno_en_curso(moodle, studentid, courseid)
            num_matriculas_borradas = num_matriculas_borradas + 1

    ########################
    # Añado un resumen al final del mensaje
    ########################
    mensajes_email.append("--------------------------------------------------------------------------")
    mensajes_email.append("--------------------------------------------------------------------------")
    mensajes_email.append("--------------------------------------------------------------------------")
    mensajes_email.append("<b>RESUMEN de acciones llevadas a cabo por este script:</b>")
    mensajes_email.append("- Alumnos existentes en moodle antes de ejecutar este programa: " + str(num_alumnos_pre_app) )
    num_alumnos_post_script = len( get_alumnos_moodle_no_borrados(moodle) )
    mensajes_email.append("- Alumnos existentes en moodle despues de ejecutar este programa: " + str(num_alumnos_post_script) )
    mensajes_email.append("- Alumnos creados por este script: " + str(num_alumnos_creados) )
    mensajes_email.append("- Alumnos que NO es posible crear por este script: " + str(num_alumnos_no_creables) )
    mensajes_email.append("- Alumnos reactivados por este script: " + str(num_alumnos_reactivados) )
    mensajes_email.append("- Alumnos suspendidos por este script: " + str(num_alumnos_suspendidos) )
    mensajes_email.append("- Alumnos cuyo login ha sido modificado por este script: " + str(num_alumnos_modificado_login) )
    mensajes_email.append("- Cantidad de matriculas hechas en modulos: " + str(num_modulos_matriculados) )
    mensajes_email.append("- Cantidad de matriculas reactivadas en modulos: " + str(num_matriculas_reactivadas) )
    mensajes_email.append("- Cantidad de matriculas suspendidas en modulos (no cuenta en las tutorías): " + str(num_matriculas_suspendidas) )
    mensajes_email.append("- Cantidad de matriculas suspendidas en tutorías: " + str(num_tutorias_suspendidas) )
    mensajes_email.append("- Cantidad de matriculas borradas en modulos (solo en Agosto): " + str(num_matriculas_borradas) )
    mensajes_email.append("- Cantidad de matriculas no hechas por no existir el curso destino: " + str(num_alumnos_no_matriculados_en_cursos_inexistentes) )
    mensajes_email.append("- Cantidad de emails enviados: " + str(num_emails_enviados) )
    mensajes_email.append("- Cantidad de emails NO enviados: " + str(num_emails_no_enviados) )
    ########################
    # Envío email resumen de lo hecho por email a responsables
    ########################
    texto = "<br/>".join( map(return_text_for_html, mensajes_email) )
    #texto = """{}""".format("<br/>".join(mensajes_email[1:]))
    
    #
    print("Comenzamos con el fichero")
    filename = get_date_time_for_filename()
    print("filename: " + filename)
    full_filename = "/var/fp-distancia-gestion-usuarios-automatica/logs/" + filename + SUBDOMAIN + ".html"
    print("full_filename: " + full_filename)
    fichero = open(full_filename, "x")
    print("fichero abierto")
    fichero.write(texto)
    print("fichero escrito")
    fichero.close()
    print("fichero cerrado")
    print("Printed immediately.")
    time.sleep(10)
    print("Printed after 10 seconds.")
    emails = REPORT_TO.split()
    for email in emails:
        send_email_con_adjunto(email, "Informe automatizado gestión automática usuarios moodle", full_filename)

    #
    # End of main 
    # 

#################################
#################################
#################################
# Funciones
#################################
#################################
#################################

def eval_estudiantes_con_mas_de_1_tutorias(moodle, alumnos_sigad, mensajes_email):
    """
    Procesa a los estudiantes de Moodle que están matriculados en 2 o mas tutorías y verifica si en el 
    fichero de JSON original también están en 2 o mas ciclos
    """
    print("eval_estudiantes_con_mas_de_1_tutorias(...)")
    estudiantes = get_estudiantes_con_mas_de_1_tutorias(moodle)
    num_tutorias_suspendidas = 0
    # Aquellos estudiantes que tengan 2 o mas tutorías los busco en los datos que han llegado de 
    # SIGAD y compruebo si están dónde deberían estar o no y los mantengo en la cohorte o no
    print("Estudiantes con 2 tutorías o mas")
    mensajes_email.append("<br/>")
    mensajes_email.append( get_date_time_for_humans() + " <b>***** Alumnos con mas de 1 tutoría</b>:")
    mensajes_email.append("<br/>")
    for estudianteMoodle in estudiantes:
        print("- Evaluando estudiante: ", estudianteMoodle)
        mensajes_email.append("- Evaluando a: " + estudianteMoodle['username'])
        encontrado = False
        for alumno_sigad in alumnos_sigad:
            # print("alumno_sigad.getDocumento()", alumno_sigad.getDocumento())
            if estudianteMoodle['username'] is not None \
                    and alumno_sigad.getDocumento() is not None \
                    and estudianteMoodle['username'].lower() == alumno_sigad.getDocumento().lower():
                print("Estudiante ENCONTRADO en SIGAD")
                
                cursos = get_cursos_de_tutoria_en_que_esta_matriculado_un_alumno(moodle, estudianteMoodle['userid'])
                print("Cursos de tutoría en que está matriculado el alumno en Moodle: ", cursos)
                
                # Recorrer los cursos en que está matriculado en SIGAD y su shortname tiene una t
                # Por cada curso ver si en los datos de SIGAD estámatriculado en ese centro y ciclo
                for curso in cursos:
                    print("- Evaluando si en SIGAD está en Curso: ", str(curso))
                    
                    codCentro = curso['cshortname'].split("-")[0]
                    codCiclo = curso['cshortname'].split("-")[1]
                    le_correspone_la_tutoria = False
                    # Buscar en los datos de SIGAD si el curso está matriculado en ese centro y ciclo
                    for centro in alumno_sigad.getCentros():
                        print("centro.get_codigo_centro(): ", centro.get_codigo_centro())
                        print("codCentro:", codCentro)
                        if centro.get_codigo_centro() == codCentro:
                            for ciclo in centro.getCiclos():
                                print("ciclo.get_siglas_ciclo: ", ciclo.get_siglas_ciclo())
                                print("codCiclo:", codCiclo)
                                if ciclo.get_siglas_ciclo() == codCiclo:
                                    le_correspone_la_tutoria = True
                                    break
                    # Si no está matriculado en ese centro y ciclo, lo desmatriculo de esa tutoria
                    if not le_correspone_la_tutoria:
                        print("No está matriculado en ese centro (",codCentro,") y ciclo(",codCiclo,"). Suspendiendo matrícula de esa tutoría.")
                        mensajes_email.append("No está matriculado en ese centro ("+codCentro+") y ciclo ("+codCiclo+"). Suspendiendo matrícula de esa tutoría.")
                        suspende_matricula_en_curso(moodle, estudianteMoodle['userid'], curso['courseid'])
                        num_tutorias_suspendidas += 1
                        print("suspendida matrícula de curso: " + curso['courseid'])
                        mensajes_email.append("suspendida matrícula de curso: " + curso['courseid'])
                    else:
                        print("Está matriculado correctamente en esa tutoría ",codCentro, codCiclo, ". No hago nada")
                        mensajes_email.append("Está matriculado correctamente en esa tutoría ("+codCentro+"-"+codCiclo+"). No hago nada")
                # 
                encontrado = True
                break
        if not encontrado:
            print("Estudiante NO ENCONTRADO en SIGAD")
            mensajes_email.append("Estudiante NO ENCONTRADO en SIGAD")

    return num_tutorias_suspendidas
    # raise Exception("Fin de eval_estudiantes_con_mas_de_1_tutorias") # para testing

def get_estudiantes_con_mas_de_1_tutorias(moodle):
    """
    Devuelve una lista de estudiantes que tienen más de 2 tutorias
    """
    
    print("get_estudiantes_con_mas_de_1_tutorias(...)")

    command = '''\
            mysql --user=\"{DB_USER}\" --password=\"{DB_PASS}\" --host=\"{DB_HOST}\" -D \"{DB_NAME}\"  --execute=\"
                SELECT
                    u.id, u.username
                                                
                FROM
                    mdl_role_assignments ra
                    JOIN mdl_user u ON u.id = ra.userid
                    JOIN mdl_role r ON r.id = ra.roleid
                    JOIN mdl_context cxt ON cxt.id = ra.contextid
                    JOIN mdl_course c ON c.id = cxt.instanceid

                WHERE ra.userid = u.id
                                                
                    AND ra.contextid = cxt.id
                    AND cxt.contextlevel =50
                    AND cxt.instanceid = c.id
                    AND  roleid = 5
                    and c.shortname like '%t'
                    AND u.username not like 'prof%'

                group by u.id
                having  count(*) > 1
            \" | tail -n +2
            '''.format(DB_USER = DB_USER, DB_PASS = DB_PASS, DB_HOST = DB_HOST, DB_NAME = DB_NAME )
    
    cursos_en_los_que_esta_matriculado = run_command( command, True ).rstrip()
    
    estudiantes = []    
    
    data_s = io.StringIO(cursos_en_los_que_esta_matriculado).read()
    lines = data_s.splitlines()
    estudiante = [
        {
            "userid": line.split()[0],
            "username": line.split()[1],
        }
        for line in lines
        # if line.split()[-1].endswith("moodle_1")
    ]
    estudiantes.extend(estudiante)
    

    return estudiantes
def get_cursos_de_tutoria_en_que_esta_matriculado_un_alumno(moodle, id_alumno):
    """
    Devuelve una lista los cursos de tutoríaen que un alumno está matriculado sin tener la matrícula suspendida
    """
    print("get_cursos_de_tutoria_en_que_esta_matriculado_un_alumno(...)")

    command = '''\
            mysql --user=\"{DB_USER}\" --password=\"{DB_PASS}\" --host=\"{DB_HOST}\" -D \"{DB_NAME}\"  --execute=\"
                SELECT c.id, ue.userid, c.shortname, c.fullname
                FROM mdl_user_enrolments ue 
                INNER JOIN mdl_enrol e ON e.id = ue.enrolid 
                INNER JOIN mdl_course c ON e.courseid = c.id
                where ue.status = 0 and ue.userid = {id_alumno} and c.shortname like '%t';
            \" | tail -n +2
            '''.format(DB_USER = DB_USER, DB_PASS = DB_PASS, DB_HOST = DB_HOST, DB_NAME = DB_NAME, id_alumno = id_alumno )

    alumnos_con_matriculas_suspendidas_en_curso = run_command( command , True).rstrip()
    
    matriculas = []    
    
    data_s = io.StringIO(alumnos_con_matriculas_suspendidas_en_curso).read()
    lines = data_s.splitlines()
    matricula = [
        {
            "courseid": line.split()[0],
            "studentid": line.split()[1],
            "cshortname": line.split()[2],
            "cfullname": line.split()[3],
        }
        for line in lines
        # if line.split()[-1].endswith("moodle_1")
    ]
    matriculas.extend(matricula)
    print("matriculas: ", matriculas )

    return matriculas
    # End of get_cursos_de_tutoria_en_que_esta_matriculado_un_alumno

def return_text_for_html(cadena):
    """
    Cada una cadena de texto reemplaza los caracteres con tildes por su equivalente en html
    """
    print("return_text_for_html(",cadena,"). Tipo(", type(cadena) , ")" , sep="")
    cadena = cadena.replace("á", "&aacute;")
    cadena = cadena.replace("é", "&eacute;")
    cadena = cadena.replace("í", "&iacute;")
    cadena = cadena.replace("ó", "&oacute;")
    cadena = cadena.replace("ú", "&uacute;")

    cadena = cadena.replace("Á", "&Aacute;")
    cadena = cadena.replace("É", "&Eacute;")
    cadena = cadena.replace("Í", "&Iacute;")
    cadena = cadena.replace("Ó", "&Oacute;")
    cadena = cadena.replace("Ú", "&Uacute;")

    cadena = cadena.replace("ñ", "&ntilde;")
    cadena = cadena.replace("Ñ", "&Ntilde;")

    return cadena

def random_pass(str_size):
    """
    devuelve una cadena aleatoria de la longitud dada de entre los caracteres existentes en allowed_chars
    """
    allowed_chars = "ABCDEFGHJKLMNPRSTUVW23456789"
    return ''.join(random.choice(allowed_chars) for x in range(str_size))

def get_mes():
    """
    devuelve el mes
    """
    now = datetime.now() # current date and time
    mes = now.strftime("%m")
    return mes

def get_curso_para_REST():
    """
    será un valor variable para indicar el curso escolar del que se solicitan datos. 
    Por ejemplo, para solicitar los datos del curso escolar 2020/2021 habrá que utilizar el valor 2020
    """
    now = datetime.now() # current date and time
    anio = now.strftime("%Y")
    mes = now.strftime("%m")
    if int(mes) in [1,2,3,4,5,6,7,8]:
        return str( int(anio) - 1 )
    else:
        return anio

def reactiva_usuario(moodle, id_usuario):
    """
    Reactiva a un usuario que estuviese suspendido
    """
    print("reactiva_usuario(...)")

    command = '''\
            mysql --user=\"{DB_USER}\" --password=\"{DB_PASS}\" --host=\"{DB_HOST}\" -D \"{DB_NAME}\"  --execute=\"
                update mdl_user
                set suspended = 0
                WHERE id = {id_usuario}
            \" 
            '''.format(DB_USER = DB_USER, DB_PASS = DB_PASS, DB_HOST = DB_HOST, DB_NAME = DB_NAME, id_usuario = id_usuario )
    run_command( command , False)
    
    #
    # End of reactiva_usuario
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
    # End of get_cursos_en_que_esta_matriculado

def get_cursos_en_que_esta_matriculado_un_alumno(moodle, id_alumno):
    """
    Devuelve una lista los cursos en que un alumno está matriculado sin tener la matrícula suspendida
    """
    print("get_cursos_en_que_esta_matriculado_un_alumno(...)")

    command = '''\
            mysql --user=\"{DB_USER}\" --password=\"{DB_PASS}\" --host=\"{DB_HOST}\" -D \"{DB_NAME}\"  --execute=\"
                SELECT c.id, ue.userid, c.shortname, c.fullname
                FROM mdl_user_enrolments ue 
                INNER JOIN mdl_enrol e ON e.id = ue.enrolid 
                INNER JOIN mdl_course c ON e.courseid = c.id
                where ue.status = 0 and ue.userid = {id_alumno} ;
            \" | tail -n +2
            '''.format(DB_USER = DB_USER, DB_PASS = DB_PASS, DB_HOST = DB_HOST, DB_NAME = DB_NAME, id_alumno = id_alumno )

    alumnos_con_matriculas_suspendidas_en_curso = run_command( command , True).rstrip()
    
    matriculas = []    
    
    data_s = io.StringIO(alumnos_con_matriculas_suspendidas_en_curso).read()
    lines = data_s.splitlines()
    matricula = [
        {
            "courseid": line.split()[0],
            "studentid": line.split()[1],
            "cshortname": line.split()[2],
            "cfullname": line.split()[3],
        }
        for line in lines
        # if line.split()[-1].endswith("moodle_1")
    ]
    matriculas.extend(matricula)
    print("matriculas: ", matriculas )

    return matriculas
    # End of get_cursos_en_que_esta_matriculado_un_alumno


def get_alumnos_con_matriculas_suspendidas_en_curso(moodle):
    """
    Devuelve una lista de matrículas con el par idcurso idalumno
    """
    print("get_alumnos_con_matriculas_suspendidas_en_curso(...)")

    command = '''\
            mysql --user=\"{DB_USER}\" --password=\"{DB_PASS}\" --host=\"{DB_HOST}\" -D \"{DB_NAME}\"  --execute=\"
                SELECT c.id, ue.userid
                FROM mdl_user_enrolments ue 
                INNER JOIN mdl_enrol e ON e.id = ue.enrolid 
                INNER JOIN mdl_course c ON e.courseid = c.id
                where ue.status = 1;
            \" | tail -n +2
            '''.format(DB_USER = DB_USER, DB_PASS = DB_PASS, DB_HOST = DB_HOST, DB_NAME = DB_NAME )

    alumnos_con_matriculas_suspendidas_en_curso = run_command( command , True).rstrip()
    
    matriculas = []    
    
    data_s = io.StringIO(alumnos_con_matriculas_suspendidas_en_curso).read()
    lines = data_s.splitlines()
    matricula = [
        {
            "courseid": line.split()[0],
            "studentid": line.split()[1],
        }
        for line in lines
        # if line.split()[-1].endswith("moodle_1")
    ]
    matriculas.extend(matricula)
    

    return matriculas
    # End of get_alumnos_con_matriculas_suspendidas_en_curso

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
    return now.strftime("%Y%m%d-%H%M%S")

def get_date_time_for_humans():
    """
    return the datetime in format dd/mm/yyyy hh:mm:ss
    info from  https://www.programiz.com/python-programming/datetime/strftime
    """
    now = datetime.now() # current date and time
    return now.strftime("%d/%m/%Y %H:%M:%S")

def get_date_time_for_filename():
    """
    return the datetime in format yyyy_mm_dd_hh_mm_ss_
    info from  https://www.programiz.com/python-programming/datetime/strftime
    """
    now = datetime.now() # current date and time
    return now.strftime("%Y_%m_%d_%H_%M_%S_")

def guarda_fichero(nombre_fichero, contenido):
    """
    Guarda en disco duro, en la carpeta logs un fichero con el nombre indicado en parámetro y el contenido dado
    """
    print("guarda_fichero(...)")
    text_file = open(PATH + "/logs/" + nombre_fichero, "w")
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

def matricula_alumno_en_cohorte_alumnado(moodle, id_alumno):
    """
    Añade al alumno dado en la cohorte alumnado
    """
    print("matricula_alumno_en_cohorte_alumnado(...)")
    cmd = "moosh -n cohort-enrol -u " + id_alumno + " \"alumnado\""
    run_moosh_command(moodle, cmd, False)

def desmatricula_alumno_de_todas_cohortes(moodle, id_alumno):
    """
    Elimina al alumno dado de la cohorte alumnado
    """
    print("desmatricula_alumno_de_todas_cohortes(...)")

    command = '''\
            mysql --user=\"{DB_USER}\" --password=\"{DB_PASS}\" --host=\"{DB_HOST}\" -D \"{DB_NAME}\"  --execute=\"
                delete from mdl_cohort_members
                where userid = {id_alumno}
            \"
            '''.format(DB_USER = DB_USER, DB_PASS = DB_PASS, DB_HOST = DB_HOST, DB_NAME = DB_NAME, id_alumno = id_alumno )
    run_command( command, False )   

def matricula_alumno_en_cohorte(moodle, id_alumno, cod_centro, id_estudio):
    """
    Dado un alumno y un curso los desmatricula en el moodle dado
    """
    print("matricula_alumno_en_cohorte(...)")
    cmd = "moosh -n cohort-enrol -u " + id_alumno + " \"" + cod_centro + "-" + id_estudio + "\""
    run_moosh_command(moodle, cmd, False)

def desmatricula_alumno_en_curso(moodle, id_alumno, id_curso):
    """
    Dado un alumno y un curso los desmatricula en el moodle dado
    """
    print("desmatricula_alumno_en_curso(...)")

    cmd = "moosh -n course-unenrol " + id_curso + " " + id_alumno
    run_moosh_command(moodle, cmd, False)

def suspende_matricula_en_curso(moodle, id_alumno, id_curso):
    """
    Dado un alumno y un curso suspende la matrícula en el moodle dado
    """
    print("suspende_matricula_en_curso(...)")

    command = '''\
            mysql --user=\"{DB_USER}\" --password=\"{DB_PASS}\" --host=\"{DB_HOST}\" -D \"{DB_NAME}\"  --execute=\"
                update mdl_user_enrolments ue 
                set ue.status = 1 
                where ue.userid = {id_alumno} and ue.enrolid in 
                    (select e.id
                    from mdl_enrol e 
                    where e.courseid = 
                        (select c.id 
                        from mdl_course c 
                        where c.id = {id_curso})  )
            \"
            '''.format(DB_USER = DB_USER, DB_PASS = DB_PASS, DB_HOST = DB_HOST, DB_NAME = DB_NAME, id_alumno = id_alumno, id_curso = id_curso )
    run_command( command, False )
    # Fin de suspende_matricula_en_curso

def reactiva_alumno_en_curso(moodle, id_alumno, id_curso):
    """
    Dado un alumno y un curso reactiva su matrícula en el moodle dado
    """
    print("reactiva_alumno_en_curso(...)")

    command = '''\
            mysql --user=\"{DB_USER}\" --password=\"{DB_PASS}\" --host=\"{DB_HOST}\" -D \"{DB_NAME}\"  --execute=\"
                update mdl_user_enrolments ue 
                set ue.status = 0 
                where ue.userid = {id_alumno} and ue.enrolid in 
                    (select e.id
                    from mdl_enrol e 
                    where e.courseid = 
                        (select c.id 
                        from mdl_course c 
                        where c.id = {id_curso})  )
            \"
            '''.format(DB_USER = DB_USER, DB_PASS = DB_PASS, DB_HOST = DB_HOST, DB_NAME = DB_NAME, id_alumno = id_alumno, id_curso = id_curso )
    run_command( command, False )
    # Fin de suspende_matricula_en_curso

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


def is_alumno_suspendido_en_curso(moodle, id_curso, id_usuario):
    """
    Devuelve verdadero si el alumno dado está suspendido en el curso dado
    """
    print("is_alumno_suspendido_en_curso(...)")

    command = '''\
            mysql --user=\"{DB_USER}\" --password=\"{DB_PASS}\" --host=\"{DB_HOST}\" -D \"{DB_NAME}\"  --execute=\"
                SELECT ue.status -- suspendido = 1 activado = 0
                FROM mdl_user_enrolments ue
                JOIN mdl_enrol e ON ue.enrolid = e.id
                where ue.userid = {id_usuario} and e.courseid = {id_curso} 
            \" | tail -n +2
            '''.format(DB_USER = DB_USER, DB_PASS = DB_PASS, DB_HOST = DB_HOST, DB_NAME = DB_NAME, id_usuario = id_usuario, id_curso = id_curso )

    is_alumno_suspendido_en_curso = run_command( command , True).rstrip()
    
    print("is_alumno_suspendido_en_curso: ", is_alumno_suspendido_en_curso)

    if is_alumno_suspendido_en_curso == "1":
        return True
    return False
    # End of is_alumno_suspendido_en_curso

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

def send_email_con_adjunto(destinatario, asunto, filename):
    print("send_email_con_adjunto(destinatario: '" + destinatario + "', filename: '"+filename+"')")
    """
    Al destinatario envía un email con el asunto y el fichero adjunto facilitado
    """
    # https://www.codespeedy.com/send-email-with-file-attachment-in-python-with-smtp/
    enviado = False
    port = SMTP_PORT  # For starttls
    smtp_server = SMTP_HOSTS
    sender_email = SMTP_USER
    receiver_email = destinatario
    password = SMTP_PASSWORD
    #texto = texto.encode('utf-8')
    message = MIMEMultipart()
    message["From"] = sender_email
    message['To'] = receiver_email
    message['Subject'] = asunto

    # message = f"Subject: {asunto}\nMIME-Version: 1.0\nContent-type: text/html\n\n{texto}".encode("utf-8")
    attachment = open(filename,'rb')

    obj = MIMEBase('application','octet-stream')
    obj.set_payload((attachment).read())
    encoders.encode_base64(obj)
    obj.add_header('Content-Disposition',"attachment; filename= "+filename)

    message.attach(obj)

    my_message = message.as_string()

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        try:
            # server.ehlo()  # Can be omitted
            server.starttls(context=context)
            # server.ehlo()  # Can be omitted
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, my_message)
            enviado = True
        except Exception as e:
            if hasattr(e, 'message'):
                print(e.message)
            else:
                print(e)
        finally:
            server.quit()
    return enviado

def send_email(destinatario, asunto, texto):
    print("send_email(destinatario: '" + destinatario + "')")
    """
    Al destinatario envía un email con el asunto y texto dados
    """
    enviado = False
    port = SMTP_PORT  # For starttls
    smtp_server = SMTP_HOSTS
    sender_email = SMTP_USER
    receiver_email = destinatario
    password = SMTP_PASSWORD
    texto = texto.encode('utf-8')
    message = f"Subject: {asunto}\nMIME-Version: 1.0\nContent-type: text/html\n\n{texto}".encode("utf-8")

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        try:
            # server.ehlo()  # Can be omitted
            server.starttls(context=context)
            # server.ehlo()  # Can be omitted
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)
            enviado = True
        except Exception as e:
            if hasattr(e, 'message'):
                print(e.message)
            else:
                print(e)
        finally:
            server.quit()
    return enviado

def suspende_alumno_moodle(id_usuario, moodle):
    """
    suspende a un usuario que estuviese suspendido
    """
    print("suspende_alumno_moodle(...)")

    command = '''\
            mysql --user=\"{DB_USER}\" --password=\"{DB_PASS}\" --host=\"{DB_HOST}\" -D \"{DB_NAME}\"  --execute=\"
                update mdl_user
                set suspended = 1
                WHERE id = {id_usuario}
            \" 
            '''.format(DB_USER = DB_USER, DB_PASS = DB_PASS, DB_HOST = DB_HOST, DB_NAME = DB_NAME, id_usuario = id_usuario )
    run_command( command , False)
    #
    # End of suspende_alumno_moodle
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

def get_alumnos_suspendidos(moodle):
    print("get_alumnos_suspendidos(...)")
    """
    Devuelve una lista de alumnos (omite usuarios con username que empiece por prof) que actualmente están en moodle suspendidos
    #
    """
    cmd = "moosh -n user-list -n 50000 \"suspended = 1 and username not like 'prof%' \" " #listado de usuarios limitado a 50.000 # username (id), email,
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
    ]
    alumnos.extend(alumno)

    return alumnos
    #
    # End of get_alumnos_suspendidos
    #

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
    if alumno.getDocumento() is None:
        return False

    # moosh -n  user-list "username = 'estudiante1'"
    cmd = "moosh -n user-list \"username = '"+ alumno.getDocumento().lower() +"'\""
    
    username = run_moosh_command(moodle, cmd, True)

    if username == "":
        return False
    return True
    #
    # End of existeAlumnoEnMoodle
    #

def isAlumnoCreable(alumno):
    print("isAlumnoCreable(...)")
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

    return alumno_creable

def crearAlumnoEnMoodle(moodle, alumno, password):
    """
    Crea un usuario en moodle con los datos del objeto alumno
    Devuelve el id del alumno creado
    """
    print("crearAlumnoEnMoodle(...)")
    alumno_creable = isAlumnoCreable(alumno)

    if alumno_creable:
        cmd = "moosh -n user-create --password " + password + " --email " + alumno.getEmail() \
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
###################################################
###################################################
# Lanzamos!
###################################################
###################################################
###################################################
try:
    main()
except Exception as exc:
    print("1.- traceback.print_exc()")
    traceback.print_exc()
    print("2.- traceback.print_exception(*sys.exc_info())")
    traceback.print_exception(*sys.exc_info())
    print("--------------------")
    print(exc)
    send_email("fp@catedu.es", "ERROR - Informe automatizado gestión automática usuarios moodle", "Ha fallado el informe, revisar logs. <br/>Error: " + str(exc) + "<br/><br/><br/>" + str(traceback.print_exc()) + "<br/><br/><br/>" + str(traceback.print_exception(*sys.exc_info())))