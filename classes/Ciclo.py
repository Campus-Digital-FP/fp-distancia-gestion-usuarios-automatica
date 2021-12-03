class Ciclo:
    NAME="CICLO"

    def __init__(self, idFicha, codigoCiclo, ciclo, siglasCiclo):
        self.__idFicha = idFicha
        self.__codigoCiclo = codigoCiclo
        self.__ciclo = ciclo
        self.__siglasCiclo = siglasCiclo
        self.__modulos = None

    def addModulo(self, modulo):
        if self.__modulos is None:
            self.__modulos = []
        self.__modulos.append(modulo)

    def get_siglas_ciclo(self):
        return self.__siglasCiclo

    def get_ciclo(self):
        return self.__ciclo

    def getModulos(self):
        return self.__modulos

    def __repr__(self):
        cadena = "idFicha: " +  str(self.__idFicha) \
            + ", codigoCiclo: " + str(self.__codigoCiclo) \
            + ", ciclo: "  + str(self.__ciclo) \
            + ", siglasCiclo: " + str(self.__siglasCiclo)
        
        if self.__modulos is not None:
            for modulo in self.__modulos:
                cadena += "\n\t\t\t" + repr(modulo)
        else:
            cadena += "\n\t\t\t" + "No tiene módulos"
        
        return cadena