from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
from crud_usuarios import CrudUsuarios

port = 3000
crud = CrudUsuarios()

class MiServidor(SimpleHTTPRequestHandler):
    def do_POST(self):
        longitud = int(self.headers.get('Content-Length', 0))
        datos = self.rfile.read(longitud).decode("utf-8")
        
        try:
            datos_json = json.loads(datos) if datos else {}
        except:
            datos_json = {}

        # --- PUNTO 5: PROCESAR LOGIN ---
        if self.path == '/api/login':
            usuario = datos_json.get('usuario')
            clave = datos_json.get('clave')
            
            if crud.validar_login(usuario, clave):
                respuesta = {'status': 'ok', 'redirect': '/usuarios.html'}
            else:
                respuesta = {'status': 'error', 'msg': 'Acceso denegado: Usuario o clave incorrectos.'}

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(respuesta).encode("utf-8"))

        # --- PUNTO 3 Y 4: CRUD (GUARDAR / ACTUALIZAR) ---
        elif self.path == '/api/usuarios/guardar':
            resultado = crud.crud_usuarios_usss005825(datos_json)
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(resultado).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        urlParse = urlparse(self.path)
        qs = parse_qs(urlParse.query)

        # --- PUNTO 5: EL LOGIN ES LA PRIMERA PÁGINA AL EJECUTAR ---
        if urlParse.path == "/" or urlParse.path == "":
            self.path = "/login.html"
            return SimpleHTTPRequestHandler.do_GET(self)

        # --- PUNTO 4: CONSULTAR / BUSCAR USUARIOS ---
        elif urlParse.path == "/api/usuarios":
            buscar = qs.get('buscar', [''])[0]
            datos = crud.consultar(buscar)
            
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(datos).encode("utf-8"))
            
        else:
            return SimpleHTTPRequestHandler.do_GET(self)

    def do_DELETE(self):
        urlParse = urlparse(self.path)
        if urlParse.path.startswith('/api/usuarios/eliminar/'):
            try:
                id_usuario = urlParse.path.split('/')[-1]
                resultado = crud.eliminar(id_usuario)
            except Exception as e:
                resultado = {'status': 'error', 'msg': str(e)}

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(resultado).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

print(f"Servidor ejecutándose en http://localhost:{port}")
server = HTTPServer(("localhost", port), MiServidor)
server.serve_forever()