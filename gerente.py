import socket
import threading
import json

class Gerenciador:
    def __init__(self, host='0.0.0.0', port=9999):
        self.host = host
        self.port = port
        self.clientes = []
        self.lock = threading.Lock()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"[*] Gerenciador iniciado em {self.host}:{self.port}")

    def lidar_com_cliente(self, conn, addr):
        print(f"[+] Novo funcionário conectado: {addr}")
        with self.lock:
            self.clientes.append(conn)
        
        try:
            while True:
                # Recebe o tamanho do cabeçalho primeiro (4 bytes) para saber o tamanho da mensagem
                tamanho_bytes = conn.recv(4)
                if not tamanho_bytes:
                    break
                tamanho_msg = int.from_bytes(tamanho_bytes, byteorder='big')
                
                # Recebe a mensagem real (o JSON com os dados simulados da imagem)
                dados = conn.recv(tamanho_msg)
                if dados:
                    mensagem = json.loads(dados.decode('utf-8'))
                    if mensagem.get('tipo') == 'CAPTURA':
                        print(f"\n[RECEBIDO de {addr}] Tela: {mensagem['tela']} | Webcam: {mensagem['webcam']}")
        except Exception as e:
            print(f"[-] Erro na conexão com {addr}: {e}")
        finally:
            with self.lock:
                if conn in self.clientes:
                    self.clientes.remove(conn)
            conn.close()
            print(f"[-] Funcionário desconectado: {addr}")

    def atualizar_intervalo(self, novo_intervalo):
        comando = {
            "comando": "ATUALIZAR_INTERVALO",
            "intervalo": novo_intervalo
        }
        msg_json = json.dumps(comando).encode('utf-8')
        tamanho = len(msg_json).to_bytes(4, byteorder='big')
        
        with self.lock:
            for conn in self.clientes:
                try:
                    # Envia o cabeçalho de tamanho seguido do comando JSON
                    conn.sendall(tamanho + msg_json)
                except Exception as e:
                    print(f"Erro ao enviar para cliente: {e}")
        print(f"[*] Comando de atualização (Intervalo: {novo_intervalo}s) enviado para {len(self.clientes)} programas gerenciados.")

    def iniciar(self):
        # Thread para aceitar conexões em background
        def aceitar_conexoes():
            while True:
                conn, addr = self.server_socket.accept()
                cliente_thread = threading.Thread(target=self.lidar_com_cliente, args=(conn, addr))
                cliente_thread.daemon = True
                cliente_thread.start()
        
        threading.Thread(target=aceitar_conexoes, daemon=True).start()

        # Loop principal para o painel de controle do administrador
        while True:
            try:
                cmd = input("Digite o novo intervalo em segundos (ou 'sair' para encerrar): \n")
                if cmd.lower() == 'sair':
                    break
                novo_intervalo = int(cmd)
                self.atualizar_intervalo(novo_intervalo)
            except ValueError:
                print("Por favor, digite um número válido.")

if __name__ == "__main__":
    gerenciador = Gerenciador()
    gerenciador.iniciar()