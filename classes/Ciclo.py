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

    def __repr__(self):
        cadena = "idFicha: " +  str(self.__idFicha) \
            + ", codigoCiclo: " + str(self.__codigoCiclo) \
            + ", ciclo: "  + str(self.__ciclo) \
            + ", siglasCiclo: " + str(self.__siglasCiclo)

        for modulo in self.__modulos:
            cadena = cadena + "\n\t\t\t" + repr(modulo)
        
        return cadena