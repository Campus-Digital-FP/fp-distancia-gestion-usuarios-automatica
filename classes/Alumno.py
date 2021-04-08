class Alumno:
    NAME = "ALUMNO"

    def __init__(
            self, idAlumno, idTipoDocumento, documento, nombre, pape,
            sape, email ):
        self.__idAlumno = idAlumno
        self.__idTipoDocumento = idTipoDocumento
        self.__documento = documento
        self.__nombre = nombre
        self.__pape = pape
        self.__sape = sape
        self.__email = email
        self.__centros = None

    def addCentro(self, centro):
        if self.__centros is None:
            self.__centros = []
        self.__centros.append(centro)

    def getDocumento(self):
        return self.__documento

    def getNombre(self):
        return self.__nombre

    def getPape(self):
        return self.__pape

    def getSape(self):
        return self.__sape

    def getEmail(self):
        return self.__email

    def __repr__(self):
        cadena =  "idAlumno: " + str(self.__idAlumno) \
            + ", idTipoDocumento: " + str(self.__idTipoDocumento) \
            + ", documento: " + str(self.__documento) \
            + ", nombre: " + str(self.__nombre) \
            + ", pape: " + str(self.__pape) \
            + ", sape " + str(self.__sape) \
            + ", email: " + str(self.__email)
            
        for centro in self.__centros:
            cadena = cadena +  "\n\t" + repr(centro)
        
        return cadena