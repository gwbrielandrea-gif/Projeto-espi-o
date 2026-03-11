import asyncio
import websockets
import json
import base64
import cv2
from PIL import ImageGrab
import io

# Identificação única deste funcionário/máquina
ID_FUNCIONARIO = "Funcionario_01"
# IP do Gerenciador (coloque 'localhost' se for testar no mesmo PC)
IP_GERENCIADOR = "ws://localhost:8765"

def capturar_tela():
    """Tira um print da tela principal e retorna em Base64."""
    try:
        imagem = ImageGrab.grab()
        buffer = io.BytesIO()
        imagem.save(buffer, format='JPEG')
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    except Exception as e:
        print(f"Erro ao capturar tela: {e}")
        return None

def capturar_webcam():
    """Tira uma foto da webcam padrão e retorna em Base64."""
    try:
        cap = cv2.VideoCapture(0) # 0 é a câmera padrão
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            _, buffer = cv2.imencode('.jpg', frame)
            return base64.b64encode(buffer).decode('utf-8')
    except Exception as e:
        print(f"Erro ao capturar webcam: {e}")
    return None

async def conectar_ao_gerenciador():
    """Conecta ao servidor e aguarda comandos."""
    print(f"Tentando conectar ao gerenciador em {IP_GERENCIADOR}...")
    
    async for websocket in websockets.connect(IP_GERENCIADOR):
        print("Conectado com sucesso. Aguardando comandos...")
        try:
            async for mensagem in websocket:
                dados = json.loads(mensagem)
                
                if dados.get("comando") == "CAPTURAR":
                    print("Solicitação recebida! Capturando tela e webcam...")
                    
                    # Realiza as capturas
                    tela_b64 = capturar_tela()
                    webcam_b64 = capturar_webcam()
                    
                    # Monta o pacote de resposta
                    resposta = {
                        "tipo": "imagens",
                        "id_cliente": ID_FUNCIONARIO,
                        "screenshot": tela_b64,
                        "webcam": webcam_b64
                    }
                    
                    # Envia de volta ao gerenciador
                    await websocket.send(json.dumps(resposta))
                    print("Imagens enviadas com sucesso.")
                    
        except websockets.exceptions.ConnectionClosed:
            print("Conexão com o gerenciador perdida. Tentando reconectar...")
            await asyncio.sleep(5) # Espera antes de tentar reconectar

if __name__ == "__main__":
    asyncio.run(conectar_ao_gerenciador())
