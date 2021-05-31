class Centro:
    NAME="CENTRO"

    def __init__(self, codigoCentro, centro):
        self.__codigoCentro = codigoCentro
        self.__centro = centro
        self.__ciclos = None

    def addCiclo(self, ciclo):
        if self.__ciclos is None:
            self.__ciclos = []
        self.__ciclos.append(ciclo)

    def get_codigo_centro(self):
        return self.__codigoCentro

    def get_centro(self):
        return self.__centro

    def getCiclos(self):
        return self.__ciclos

    def __repr__(self):
        cadena =  "codigoCentro: " + self.__codigoCentro \
            + ", centro: " + self.__centro

        for ciclo in self.__ciclos:
            cadena = cadena + "\n\t\t" + repr(ciclo)
        
        return cadena