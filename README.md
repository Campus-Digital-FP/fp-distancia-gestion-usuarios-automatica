# fp-distancia-gestion-usuarios-automatica
Aplicación para gestionar automáticamente la creación y borrado de usuarios en Moodle así como su matriculación/desmatriculación

# Hacer funcionar este programa
Crea una copia del fichero Config-sample.py llamada Config.py en la misma ruta con los datos de acceso adecuados

# Funcionamiento
1. El programa se conecta a un Web Service que le devuelve un identificador de un fichero a descargar
2. Se espera 10 segundos mientras el fichero JSON se genera.
3. Se llama a un 2º WS y si el fichero está listo lo procesa. Si no está listo se vuelve al punto anterior. Este bucle puede ocurrir un máximo de 10 veces
4. Con el listado de alumnos/as se da de alta a aquellos que no existan y se elimina a aquellos que no figuren en el fichero. Igualmente se matricula a cada alumno/a en los cursos que indique el fichero.

## Ayuda en predesarrollo

Creación de usuarios en mysql:

```sql
CREATE USER 'admin'@'192.168.1.%' IDENTIFIED BY '<rellena con tu contraseña>';
GRANT ALL PRIVILEGES ON predesarrollo_fpvirtualaragon_es.* TO 'admin'@'192.168.1.%';
FLUSH PRIVILEGES;
```

Prueba de que funciona desde `ssh_redestel_moodle`:

```sql
mysql --user="admin" --password="acte1tuna&Roja" --host="192.168.1.110" -D "predesarrollo_fpvirtualaragon_es" --execute="SELECT id, fullname, shortname FROM predesarrollo_fpvirtualaragon_es.mdl_course limit 1;"
```

## Ayuda en www

```sql
CREATE USER 'admin'@'192.168.1.%' IDENTIFIED BY '<rellena con tu contraseña>';
GRANT ALL PRIVILEGES ON www_fpvirtualaragon_es.* TO 'admin'@'192.168.1.%';
FLUSH PRIVILEGES;
```

```sql
mysql --user="admin" --password="acte1tuna&Roja" --host="192.168.1.110" -D "www_fpvirtualaragon_es" --execute="SELECT id, fullname, shortname FROM www_fpvirtualaragon_es.mdl_course limit 1;"
```
 
## Ejecuciones

Antes de meter cualquier alumno habia 246 usuarios en la plataforma.

En el segundo intento, antes de meter cualquier alumno habia 247 usuarios en la plataforma.