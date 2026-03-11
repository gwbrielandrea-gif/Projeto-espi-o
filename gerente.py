import asyncio
import websockets
import json
import base64
import time
import os

# Configuração do período de solicitação em segundos
PERIODO_SOLICITACAO = 60 

# Dicionário para manter o cadastro dos N programas conectados
clientes_conectados = set()

async def lidar_com_cliente(websocket, path=None):
    """Gerencia a conexão e o cadastro de um novo programa gerenciado."""
    clientes_conectados.add(websocket)
    print(f"[+] Novo programa gerenciado conectado. Total: {len(clientes_conectados)}")
    
    try:
        async for mensagem in websocket:
            dados = json.loads(mensagem)
            
            if dados.get("tipo") == "imagens":
                id_cliente = dados["id_cliente"]
                timestamp = int(time.time())
                
                # Decodifica e salva a captura de tela
                if dados["screenshot"]:
                    with open(f"{id_cliente}_tela_{timestamp}.jpg", "wb") as f:
                        f.write(base64.b64decode(dados["screenshot"]))
                
                # Decodifica e salva a foto da webcam
                if dados["webcam"]:
                    with open(f"{id_cliente}_webcam_{timestamp}.jpg", "wb") as f:
                        f.write(base64.b64decode(dados["webcam"]))
                        
                print(f"[*] Imagens salvas para o funcionário: {id_cliente}")
                
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        clientes_conectados.remove(websocket)
        print(f"[-] Programa gerenciado desconectado. Total: {len(clientes_conectados)}")

async def loop_de_solicitacao():
    """Roda em segundo plano solicitando capturas a cada N segundos."""
    while True:
        await asyncio.sleep(PERIODO_SOLICITACAO)
        if clientes_conectados:
            print(f"[*] Solicitando capturas para {len(clientes_conectados)} clientes...")
            # Envia o comando de captura para todos os N clientes cadastrados/conectados
            comando = json.dumps({"comando": "CAPTURAR"})
            websockets.broadcast(clientes_conectados, comando)

async def main():
    print(f"Iniciando Gerenciador... Solicitações a cada {PERIODO_SOLICITACAO} segundos.")
    # Inicia a rotina que pede as fotos a cada N segundos
    asyncio.create_task(loop_de_solicitacao())
    # Inicia o servidor WebSocket na porta 8765
    async with websockets.serve(lidar_com_cliente, "0.0.0.0", 8765):
        await asyncio.Future()  # Roda para sempre

if __name__ == "__main__":
    if not os.path.exists("capturas"):
        os.makedirs("capturas")
    os.chdir("capturas") # Salva tudo na pasta capturas
    asyncio.run(main())