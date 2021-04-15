class Modulo:
    NAME="MODULO"

    def __init__(self, idMateria, modulo, siglasModulo):
        self.__idMateria = idMateria
        self.__modulo = modulo
        self.__siglasModulo = siglasModulo

    def get_id_materia(self):
        return self.__idMateria

    def __repr__(self):
        return "idMateria: " + str(self.__idMateria) \
            + ", modulo: " + self.__modulo \
            + ", siglasModulo: " + self.__siglasModulo 