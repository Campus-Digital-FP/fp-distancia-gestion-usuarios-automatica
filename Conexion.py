import http.client

class Conexion:
    NAME="CONEXION"


    def __init__(self, url, path, usuario, password, method):
        self.url = url
        self.path = path
        self.usuario = usuario
        self.password = password
        self.method = method
    

    def getJson(self):
        print( self.NAME + ".getJson()" )
        headers = {"Usuario" : self.usuario, "Password": self.password}
        conn = http.client.HTTPSConnection(self.url, 443) # si http 80 https 443
        conn.request(self.method, self.path, "", headers)
        response = conn.getresponse()
        resp_data = response.read()

        if response.status == 200: #exito
            conn.close()
            # print("resp_data: "+ str(resp_data) )
            return resp_data
        else:
            print( 'Status:' + str(response.status) + ': ' + str(resp_data) )
            return 
        