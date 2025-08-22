#!/usr/bin/env python3
"""
Exemplo de uso do Sidecar Python integrado no PyWhatsWeb
Demonstra como usar a biblioteca sem Node.js
"""

import asyncio
import time
from pywhatsweb import WhatsWebManager

def main():
    """Exemplo principal usando sidecar Python integrado"""
    print("🚀 PyWhatsWeb - Sidecar Python Integrado")
    print("=" * 50)
    
    # Criar manager com sidecar Python (padrão)
    manager = WhatsWebManager(
        sidecar_host="localhost",
        sidecar_port=3000,
        api_key="exemplo-chave",
        auto_start_sidecar=True,  # Inicia automaticamente
        sidecar_type="python"     # Usar sidecar Python (padrão)
    )
    
    print("✅ Manager criado com sidecar Python")
    
    # Criar sessão
    session_id = f"exemplo_{int(time.time())}"
    session = manager.create_session(
        session_id=session_id,
        phone_number="5511999999999"
    )
    
    print(f"✅ Sessão criada: {session_id}")
    
    # Handler para QR Code
    @session.on("qr")
    def on_qr(data):
        print(f"📱 QR Code gerado: {data['qr'][:50]}...")
        print("💡 Escaneie o QR Code com seu WhatsApp!")
    
    # Handler para WhatsApp pronto
    @session.on("ready")
    def on_ready(data):
        print(f"✅ WhatsApp conectado!")
        print(f"📱 Número: {data.get('phone_number', 'N/A')}")
        print(f"📊 Contatos: {data.get('contacts_count', 0)}")
        print(f"👥 Grupos: {data.get('groups_count', 0)}")
    
    # Handler para mensagens recebidas
    @session.on("message")
    def on_message(data):
        print(f"💬 Mensagem recebida:")
        print(f"   De: {data.get('from_number', data.get('from', 'N/A'))}")
        print(f"   Conteúdo: {data.get('body', data.get('content', 'N/A'))}")
        print(f"   Timestamp: {data.get('timestamp', 'N/A')}")
    
    # Handler para desconexão
    @session.on("disconnected")
    def on_disconnected(data):
        print(f"❌ WhatsApp desconectado: {data}")
    
    # Iniciar sessão
    print("🚀 Iniciando sessão...")
    session.start()
    
    # Aguardar eventos
    print("⏳ Aguardando eventos... (Pressione Ctrl+C para parar)")
    
    try:
        # Manter rodando
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Parando...")
        
        # Parar sessão
        if hasattr(session, 'stop'):
            session.stop()
        
        print("✅ Exemplo finalizado!")

if __name__ == "__main__":
    main()
