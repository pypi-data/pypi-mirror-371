"""
Sidecar Python integrado para PyWhatsWeb
Fornece funcionalidade WhatsApp sem dependências externas
"""

import json
import time
import logging
import threading
import base64
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import qrcode
from io import BytesIO
import uuid

# Configurar logging
logger = logging.getLogger("PyWhatsWeb.PythonSidecar")

class WhatsAppSession:
    """Sessão WhatsApp usando apenas Python puro"""
    
    def __init__(self, session_id: str, phone_number: str = None):
        self.session_id = session_id
        self.phone_number = phone_number
        self.is_authenticated = False
        self.qr_code = None
        self.status = "disconnected"
        self.event_handlers = {}
        self.session_data = {}
        self.logger = logging.getLogger(f"WhatsAppSession.{session_id}")
        
        # Gerar QR code inicial
        self._generate_initial_qr()
        
    def _generate_initial_qr(self):
        """Gera QR code inicial para conexão"""
        try:
            # Dados para o QR code (formato compatível com WhatsApp Web)
            qr_data = f"https://web.whatsapp.com/session/{self.session_id}"
            
            # Gerar QR code usando biblioteca Python pura
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            # Criar imagem
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Converter para base64
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            qr_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            # Salvar como data URL (compatível com templates HTML)
            self.qr_code = f"data:image/png;base64,{qr_base64}"
            self.status = "qr_ready"
            
            self.logger.info(f"QR Code gerado para sessão {self.session_id}")
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar QR code: {e}")
            self.status = "error"
    
    def start(self) -> bool:
        """Inicia a sessão WhatsApp (simulada)"""
        try:
            self.logger.info(f"Iniciando sessão {self.session_id}")
            self.status = "connecting"
            
            # Simular processo de conexão
            def simulate_connection():
                time.sleep(2)  # Simular tempo de conexão
                
                # Simular QR code sendo escaneado
                if "qr" in self.event_handlers:
                    for handler in self.event_handlers["qr"]:
                        try:
                            handler({
                                "qr": self.qr_code,
                                "expires_in": 60,
                                "attempts": 0
                            })
                        except Exception as e:
                            self.logger.error(f"Erro no handler QR: {e}")
                
                # Simular autenticação após 10 segundos
                time.sleep(10)
                self._simulate_authentication()
            
            # Executar simulação em thread separada
            connection_thread = threading.Thread(target=simulate_connection)
            connection_thread.daemon = True
            connection_thread.start()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao iniciar sessão: {e}")
            self.status = "error"
            return False
    
    def _simulate_authentication(self):
        """Simula processo de autenticação"""
        try:
            self.is_authenticated = True
            self.qr_code = None
            self.status = "ready"
            
            self.logger.info(f"Simulação: WhatsApp autenticado para sessão {self.session_id}")
            
            # Notificar handlers
            if "ready" in self.event_handlers:
                for handler in self.event_handlers["ready"]:
                    try:
                        handler({
                            "phone_number": self.phone_number,
                            "device_info": {"type": "simulated"},
                            "contacts_count": 0,
                            "groups_count": 0
                        })
                    except Exception as e:
                        self.logger.error(f"Erro no handler ready: {e}")
                        
        except Exception as e:
            self.logger.error(f"Erro ao simular autenticação: {e}")
    
    def on(self, event: str, handler: Callable):
        """Registra um handler de evento"""
        if event not in self.event_handlers:
            self.event_handlers[event] = []
        self.event_handlers[event].append(handler)
    
    def send_text(self, to: str, message: str) -> str:
        """Simula envio de mensagem"""
        try:
            if not self.is_authenticated:
                raise Exception("WhatsApp não está autenticado")
            
            # Simular envio
            message_id = f"msg_{uuid.uuid4().hex[:8]}"
            
            self.logger.info(f"Simulação: Mensagem enviada para {to}: {message_id}")
            
            # Simular delay de envio
            time.sleep(1)
            
            return message_id
            
        except Exception as e:
            self.logger.error(f"Erro ao enviar mensagem: {e}")
            raise
    
    def stop(self):
        """Para a sessão"""
        try:
            self.status = "disconnected"
            self.logger.info(f"Sessão {self.session_id} parada")
        except Exception as e:
            self.logger.error(f"Erro ao parar sessão: {e}")

class PythonSidecar:
    """Sidecar Python puro integrado na lib PyWhatsWeb"""
    
    def __init__(self, host: str = "localhost", port: int = 3000):
        self.host = host
        self.port = port
        self.sessions: Dict[str, WhatsAppSession] = {}
        self.logger = logging.getLogger("PyWhatsWeb.PythonSidecar")
        
    def start(self):
        """Inicia o servidor HTTP"""
        try:
            # Criar servidor
            server = HTTPServer((self.host, self.port), SidecarHandler)
            server.sidecar = self
            
            self.logger.info(f"🚀 Sidecar Python PyWhatsWeb iniciado em {self.host}:{self.port}")
            
            # Iniciar servidor em thread separada
            server_thread = threading.Thread(target=server.serve_forever)
            server_thread.daemon = True
            server_thread.start()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao iniciar sidecar: {e}")
            return False
    
    def create_session(self, session_id: str, phone_number: str = None) -> WhatsAppSession:
        """Cria uma nova sessão"""
        if session_id in self.sessions:
            raise Exception(f"Sessão {session_id} já existe")
        
        session = WhatsAppSession(session_id, phone_number)
        self.sessions[session_id] = session
        
        self.logger.info(f"Sessão {session_id} criada")
        return session
    
    def get_session(self, session_id: str) -> Optional[WhatsAppSession]:
        """Recupera uma sessão"""
        return self.sessions.get(session_id)
    
    def stop_session(self, session_id: str):
        """Para uma sessão"""
        if session_id in self.sessions:
            self.sessions[session_id].stop()
            del self.sessions[session_id]

class SidecarHandler(BaseHTTPRequestHandler):
    """Handler HTTP para o sidecar Python integrado"""
    
    def do_GET(self):
        """Handles GET requests"""
        try:
            parsed_path = urllib.parse.urlparse(self.path)
            path = parsed_path.path
            
            if path == "/health":
                self._send_response({
                    "status": "ok", 
                    "sidecar": "python_pywhatsweb",
                    "version": "0.4.8+",
                    "timestamp": datetime.now().isoformat()
                })
            elif path.startswith("/session/"):
                self._handle_session_get(path)
            else:
                self._send_error(404, "Not Found")
                
        except Exception as e:
            self._send_error(500, str(e))
    
    def do_POST(self):
        """Handles POST requests"""
        try:
            parsed_path = urllib.parse.urlparse(self.path)
            path = parsed_path.path
            
            if path.startswith("/session/"):
                self._handle_session_post(path)
            else:
                self._send_error(404, "Not Found")
                
        except Exception as e:
            self._send_error(500, str(e))
    
    def _handle_session_get(self, path: str):
        """Handle GET /session/{id}"""
        try:
            session_id = path.split("/")[2]
            sidecar = self.server.sidecar
            session = sidecar.get_session(session_id)
            
            if not session:
                self._send_error(404, "Session not found")
                return
            
            self._send_response({
                "session_id": session_id,
                "status": session.status,
                "authenticated": session.is_authenticated,
                "qr_code": session.qr_code,
                "phone_number": session.phone_number
            })
            
        except Exception as e:
            self._send_error(500, str(e))
    
    def _handle_session_post(self, path: str):
        """Handle POST /session/{id}/start"""
        try:
            parts = path.split("/")
            session_id = parts[2]
            action = parts[3] if len(parts) > 3 else None
            
            sidecar = self.server.sidecar
            
            if action == "start":
                # Iniciar sessão
                if session_id not in sidecar.sessions:
                    self._send_error(404, "Session not found")
                    return
                
                session = sidecar.sessions[session_id]
                success = session.start()
                
                self._send_response({
                    "success": success,
                    "session_id": session_id,
                    "status": session.status
                })
                
            else:
                self._send_error(400, "Invalid action")
                
        except Exception as e:
            self._send_error(500, str(e))
    
    def _send_response(self, data: Dict[str, Any]):
        """Envia resposta JSON"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode())
    
    def _send_error(self, code: int, message: str):
        """Envia erro HTTP"""
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        """Suprime logs de acesso"""
        pass

# Função para iniciar o sidecar
def start_python_sidecar(host: str = "localhost", port: int = 3000) -> PythonSidecar:
    """Inicia o sidecar Python integrado"""
    try:
        # Verificar se qrcode está disponível
        import qrcode
        logger.info("✅ Biblioteca qrcode disponível")
    except ImportError:
        raise ImportError("Biblioteca qrcode não está disponível. Instale: pip install qrcode[pil]")
    
    sidecar = PythonSidecar(host, port)
    if sidecar.start():
        return sidecar
    else:
        raise RuntimeError("Falha ao iniciar sidecar Python integrado")

if __name__ == "__main__":
    # Teste do sidecar
    try:
        sidecar = start_python_sidecar()
        print("✅ Sidecar Python PyWhatsWeb iniciado com sucesso!")
        print("📍 Endpoint: http://localhost:3000")
        print("🔍 Health check: http://localhost:3000/health")
        print("🛑 Pressione Ctrl+C para parar...")
        
        # Manter rodando
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Parando sidecar...")
            
    except Exception as e:
        print(f"❌ Erro ao iniciar sidecar: {e}")
        print("\n🔧 Soluções:")
        print("1. Instale qrcode: pip install qrcode[pil]")
        print("2. Verifique se a porta 3000 está livre")
        print("3. Verifique se tem permissões de rede")
