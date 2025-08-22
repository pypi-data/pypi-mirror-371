"""
WhatsWebManager - Gerenciador principal do PyWhatsWeb

Gerencia múltiplas sessões WhatsApp e fornece interface unificada para o usuário.
"""

import asyncio
import logging
from typing import Dict, Optional, List, Literal
from datetime import datetime

from .session import Session
from .storage.base import BaseStore
from .storage.filesystem import FileSystemStore
from .exceptions import SessionError, ConnectionError, AuthenticationError
from .enums import SessionStatus


class WhatsWebManager:
    """Gerenciador principal do PyWhatsWeb"""
    
    def __init__(self, 
                 sidecar_host: str = "localhost",
                 sidecar_port: int = 3000,
                 sidecar_ws_port: int = 3001,
                 api_key: str = "pywhatsweb-secret-key",
                 storage: Optional[BaseStore] = None,
                 session_base_dir: str = "./sessions",
                 auto_start_sidecar: bool = True,
                 sidecar_type: Literal["nodejs", "python"] = "python"):  # NOVA OPÇÃO
        """
        Inicializa o manager
        
        Args:
            sidecar_host: Host do sidecar
            sidecar_port: Porta HTTP do sidecar
            sidecar_ws_port: Porta WebSocket do sidecar (apenas Node.js)
            api_key: Chave de API para autenticação
            storage: Storage pluggable (padrão: FileSystemStore)
            session_base_dir: Diretório base para sessões
            auto_start_sidecar: Iniciar sidecar automaticamente
            sidecar_type: Tipo de sidecar ("nodejs" ou "python")
        """
        self.sidecar_host = sidecar_host
        self.sidecar_port = sidecar_port
        self.sidecar_ws_port = sidecar_ws_port
        self.api_key = api_key
        self.session_base_dir = session_base_dir
        self.auto_start_sidecar = auto_start_sidecar
        self.sidecar_type = sidecar_type
        
        # Storage padrão se não especificado
        if storage is None:
            self.storage = FileSystemStore(f"{session_base_dir}/data")
        else:
            self.storage = storage
        
        # Sessões ativas
        self._sessions: Dict[str, Session] = {}
        
        # Configurar logging
        self.logger = logging.getLogger(__name__)
        
        # URLs do sidecar
        self._base_url = f"http://{sidecar_host}:{sidecar_port}"
        self._ws_url = f"ws://{sidecar_host}:{sidecar_ws_port}"
        
        self.logger.info(f"PyWhatsWeb Manager inicializado - Sidecar: {self._base_url} ({self.sidecar_type})")
        
        # Iniciar sidecar automaticamente se solicitado
        if auto_start_sidecar:
            self._start_sidecar()
    
    def _start_sidecar(self):
        """Inicia o sidecar automaticamente baseado no tipo escolhido"""
        if self.sidecar_type == "python":
            self._start_python_sidecar()
        else:
            self._start_nodejs_sidecar()
    
    def _start_python_sidecar(self):
        """Inicia o sidecar Python puro automaticamente"""
        import subprocess
        import sys
        import time
        import requests
        import os  # ADICIONAR ESTE IMPORT
        
        try:
            # Verificar se sidecar já está rodando
            try:
                response = requests.get(f"{self._base_url}/health", timeout=2)
                if response.status_code == 200:
                    self.logger.info("✅ Sidecar Python já está rodando")
                    return
            except:
                pass
            
            # Verificar se qrcode está instalado
            try:
                import qrcode
                self.logger.info("✅ Biblioteca qrcode disponível")
            except ImportError:
                self.logger.error("❌ Biblioteca qrcode não encontrada. Instale: pip install qrcode[pil]")
                return
            
            # Iniciar sidecar Python em processo separado
            self.logger.info("🚀 Iniciando sidecar Python puro...")
            
            # Criar script temporário para iniciar sidecar
            current_dir = os.path.dirname(os.path.abspath(__file__))
            sidecar_script = f"""
import sys
import os
sys.path.insert(0, r'{current_dir}')
from .sidecar.python_sidecar import start_python_sidecar

if __name__ == "__main__":
    try:
        sidecar = start_python_sidecar(host="{self.sidecar_host}", port={self.sidecar_port})
        print("✅ Sidecar Python iniciado")
        
        # Manter rodando
        import time
        while True:
            time.sleep(1)
    except Exception as e:
        print(f"❌ Erro: {{e}}")
        sys.exit(1)
"""
            
            # Salvar script temporário
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(sidecar_script)
                script_path = f.name
            
            # Executar script em processo separado
            self._sidecar_process = subprocess.Popen(
                [sys.executable, script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
            
            # Limpar arquivo temporário
            try:
                os.unlink(script_path)
            except:
                pass
            
            # Aguardar sidecar estar pronto
            max_wait = 30  # máximo 30 segundos
            for i in range(max_wait):
                try:
                    response = requests.get(f"{self._base_url}/health", timeout=1)
                    if response.status_code == 200:
                        self.logger.info("✅ Sidecar Python iniciado e pronto!")
                        return
                except:
                    pass
                time.sleep(1)
                if i % 5 == 0:  # Log a cada 5 segundos
                    self.logger.info(f"⏳ Aguardando sidecar Python... ({i+1}/{max_wait}s)")
            
            self.logger.warning("⚠️  Sidecar Python não respondeu no tempo esperado")
            
        except Exception as e:
            self.logger.error(f"⚠️  Erro ao iniciar sidecar Python: {e}")
            self.logger.info("💡 Execute manualmente ou use sidecar_type='nodejs'")
    
    def _start_nodejs_sidecar(self):
        """Inicia o sidecar Node.js automaticamente"""
        import subprocess
        import os
        import time
        import requests
        
        try:
            # Verificar se sidecar já está rodando
            try:
                response = requests.get(f"{self._base_url}/health", timeout=2)
                if response.status_code == 200:
                    self.logger.info("✅ Sidecar Node.js já está rodando")
                    return
            except:
                pass
            
            # Caminho para o sidecar (relativo à biblioteca instalada)
            current_dir = os.path.dirname(os.path.abspath(__file__))
            sidecar_path = os.path.join(current_dir, '..', '..', 'sidecar')
            
            # Se não encontrar, tentar caminho alternativo
            if not os.path.exists(sidecar_path):
                sidecar_path = os.path.join(current_dir, '..', 'sidecar')
            
            if not os.path.exists(sidecar_path):
                self.logger.warning("⚠️  Caminho do sidecar não encontrado, tentando iniciar manualmente")
                return
            
            # Verificar se Node.js está instalado
            try:
                subprocess.run(['node', '--version'], check=True, capture_output=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                self.logger.error("❌ Node.js não encontrado. Instale Node.js 18+ para usar o auto-start")
                return
            
            # Verificar se package.json existe
            package_json = os.path.join(sidecar_path, 'package.json')
            if not os.path.exists(package_json):
                self.logger.error(f"❌ package.json não encontrado em {sidecar_path}")
                return
            
            # Instalar dependências se necessário
            node_modules = os.path.join(sidecar_path, 'node_modules')
            if not os.path.exists(node_modules):
                self.logger.info("📦 Instalando dependências do sidecar...")
                try:
                    subprocess.run(['npm', 'install'], cwd=sidecar_path, check=True, 
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    self.logger.info("✅ Dependências instaladas")
                except subprocess.CalledProcessError as e:
                    self.logger.error(f"❌ Erro ao instalar dependências: {e}")
                    return
            
            # Iniciar sidecar em background
            self.logger.info("🚀 Iniciando sidecar Node.js...")
            self._sidecar_process = subprocess.Popen(
                ['npm', 'start'], 
                cwd=sidecar_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
            
            # Aguardar sidecar estar pronto
            max_wait = 30  # máximo 30 segundos
            for i in range(max_wait):
                try:
                    response = requests.get(f"{self._base_url}/health", timeout=1)
                    if response.status_code == 200:
                        self.logger.info("✅ Sidecar Node.js iniciado e pronto!")
                        return
                except:
                    pass
                time.sleep(1)
                if i % 5 == 0:  # Log a cada 5 segundos
                    self.logger.info(f"⏳ Aguardando sidecar Node.js... ({i+1}/{max_wait}s)")
            
            self.logger.warning("⚠️  Sidecar Node.js não respondeu no tempo esperado")
            
        except Exception as e:
            self.logger.error(f"⚠️  Erro ao iniciar sidecar Node.js: {e}")
            self.logger.info("💡 Execute manualmente: cd sidecar && npm start")
    
    def create_session(self, session_id: str, **kwargs) -> Session:
        """
        Cria uma nova sessão WhatsApp
        
        Args:
            session_id: ID único da sessão
            **kwargs: Argumentos adicionais para a sessão
            
        Returns:
            Session: Nova sessão criada
            
        Raises:
            SessionError: Se a sessão já existir
        """
        if session_id in self._sessions:
            raise SessionError(f"Sessão {session_id} já existe")
        
        # Criar sessão
        session = Session(
            session_id=session_id,
            manager=self,
            **kwargs
        )
        
        # Armazenar sessão
        self._sessions[session_id] = session
        
        self.logger.info(f"Sessão {session_id} criada")
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Recupera uma sessão existente
        
        Args:
            session_id: ID da sessão
            
        Returns:
            Session ou None se não existir
        """
        return self._sessions.get(session_id)
    
    def list_sessions(self) -> List[str]:
        """
        Lista todas as sessões ativas
        
        Returns:
            Lista de IDs de sessão
        """
        return list(self._sessions.keys())
    
    def remove_session(self, session_id: str) -> bool:
        """
        Remove uma sessão
        
        Args:
            session_id: ID da sessão
            
        Returns:
            True se removida com sucesso
        """
        if session_id not in self._sessions:
            return False
        
        session = self._sessions[session_id]
        
        # Parar sessão se estiver ativa
        if session.is_active():
            try:
                session.stop()
            except Exception as e:
                self.logger.warning(f"Erro ao parar sessão {session_id}: {e}")
        
        # Remover da memória
        del self._sessions[session_id]
        
        self.logger.info(f"Sessão {session_id} removida")
        return True
    
    def get_session_status(self, session_id: str) -> Optional[SessionStatus]:
        """
        Obtém status de uma sessão
        
        Args:
            session_id: ID da sessão
            
        Returns:
            Status da sessão ou None se não existir
        """
        session = self.get_session(session_id)
        if session:
            return session.get_status()
        return None
    
    def get_active_sessions(self) -> List[str]:
        """
        Lista sessões ativas (conectadas e prontas)
        
        Returns:
            Lista de IDs de sessão ativa
        """
        active_sessions = []
        for session_id, session in self._sessions.items():
            if session.is_active():
                active_sessions.append(session_id)
        return active_sessions
    
    def get_session_count(self) -> int:
        """
        Retorna número total de sessões
        
        Returns:
            Número de sessões
        """
        return len(self._sessions)
    
    def get_sidecar_info(self) -> Dict[str, str]:
        """
        Informações do sidecar
        
        Returns:
            Dicionário com informações do sidecar
        """
        return {
            "host": self.sidecar_host,
            "http_port": self.sidecar_port,
            "ws_port": self.sidecar_ws_port,
            "base_url": self._base_url,
            "ws_url": self._ws_url
        }
    
    def close_all_sessions(self):
        """Para e remove todas as sessões"""
        session_ids = list(self._sessions.keys())
        
        for session_id in session_ids:
            try:
                self.remove_session(session_id)
            except Exception as e:
                self.logger.error(f"Erro ao fechar sessão {session_id}: {e}")
        
        self.logger.info("Todas as sessões foram fechadas")
    
    def cleanup(self):
        """Limpa recursos e para o sidecar se foi iniciado automaticamente"""
        try:
            # Parar todas as sessões
            for session in self._sessions.values():
                try:
                    session.stop()
                except:
                    pass
            
            # Parar sidecar se foi iniciado automaticamente
            if hasattr(self, '_sidecar_process') and self._sidecar_process:
                try:
                    if os.name == 'nt':  # Windows
                        self._sidecar_process.terminate()
                    else:  # Linux/Mac
                        self._sidecar_process.terminate()
                    self._sidecar_process.wait(timeout=5)
                    self.logger.info("✅ Sidecar parado")
                except:
                    try:
                        self._sidecar_process.kill()
                    except:
                        pass
        except Exception as e:
            self.logger.error(f"Erro durante cleanup: {e}")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.cleanup()
    
    def __del__(self):
        """Destructor"""
        try:
            self.cleanup()
        except:
            pass
