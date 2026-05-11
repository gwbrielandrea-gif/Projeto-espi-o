import socket
import threading
import json
import time

class ProgramaGerenciado:
    def __init__(self, host_gerenciador='127.0.0.1', port_gerenciador=9999):
        self.host = host_gerenciador
        self.port = port_gerenciador
        self.intervalo = 60 # Intervalo padrão inicial em segundos
        self.rodando = True
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def simular_captura(self):
        # Em um cenário real, você usaria:
        # pyautogui.screenshot() para a tela
        # cv2.VideoCapture(0) para a webcam
        return {
            "tipo": "CAPTURA",
            "tela": "imagem_tela_bytes_simulados.png",
            "webcam": "foto_webcam_bytes_simulados.jpg"
        }

    def loop_de_captura(self):
        while self.rodando:
            time.sleep(self.intervalo)
            dados_captura = self.simular_captura()
            msg_json = json.dumps(dados_captura).encode('utf-8')
            tamanho = len(msg_json).to_bytes(4, byteorder='big')
            
            try:
                self.client_socket.sendall(tamanho + msg_json)
                print(f"[+] Capturas enviadas para o gerenciador. Próxima em {self.intervalo}s.")
            except Exception as e:
                print(f"[-] Falha ao enviar capturas: {e}")
                self.rodando = False
                break

    def escutar_comandos(self):
        while self.rodando:
            try:
                # Recebe os 4 bytes que dizem o tamanho da mensagem
                tamanho_bytes = self.client_socket.recv(4)
                if not tamanho_bytes:
                    break
                tamanho_msg = int.from_bytes(tamanho_bytes, byteorder='big')
                
                # Recebe o JSON de comando
                dados = self.client_socket.recv(tamanho_msg)
                if dados:
                    comando = json.loads(dados.decode('utf-8'))
                    if comando.get("comando") == "ATUALIZAR_INTERVALO":
                        self.intervalo = comando.get("intervalo")
                        print(f"[*] O Gerenciador atualizou o intervalo para {self.intervalo} segundos.")
            except Exception as e:
                print(f"[-] Erro na conexão: {e}")
                break

    def iniciar(self):
        try:
            self.client_socket.connect((self.host, self.port))
            print("[+] Conectado ao Gerenciador com sucesso.")
            
            # Inicia thread para escutar mudanças no intervalo
            thread_comandos = threading.Thread(target=self.escutar_comandos)
            thread_comandos.daemon = True
            thread_comandos.start()

            # Inicia o loop de captura na thread principal
            self.loop_de_captura()

        except ConnectionRefusedError:
            print("[-] Não foi possível conectar ao Gerenciador. Verifique se ele está rodando.")
        finally:
            self.client_socket.close()

if __name__ == "__main__":
    cliente = ProgramaGerenciado()
    cliente.iniciar()