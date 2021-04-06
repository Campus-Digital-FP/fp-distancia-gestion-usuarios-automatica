# fp-distancia-gestion-usuarios-automatica
Aplicación para gestionar automáticamente la creación y borrado de usuarios en Moodle así como su matriculación/desmatriculación

# Hacer funcionar este programa
Crea una copia del fichero Config-sample.py llamada Config.py en la misma ruta con los datos de acceso adecuados

# Funcionamiento
1. El programa se conecta a un Web Service que le devuelve un identificador de un fichero a descargar
2. Se espera 10 segundos mientras el fichero JSON se genera.
3. Se llama a un 2º WS y si el fichero está listo lo procesa. Si no está listo se vuelve al punto anterior. Este bucle puede ocurrir un máximo de 10 veces
4. Con 