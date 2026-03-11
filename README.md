# Sistema de Monitoramento Remoto

Este projeto implementa um sistema de monitoramento remoto simples usando WebSockets em Python. Consiste em dois componentes principais: o **Gerente** (servidor) e o **Espião** (cliente). O sistema permite capturar screenshots e imagens da webcam de máquinas remotas de forma periódica.

## ⚠️ Aviso Importante

Este código é fornecido apenas para fins educacionais e de demonstração. O uso para monitoramento não autorizado de terceiros pode violar leis de privacidade e ser considerado ilegal. Sempre obtenha consentimento explícito antes de usar em qualquer ambiente real.

## Como Funciona

### Arquitetura
- **Gerente (gerente.py)**: Servidor WebSocket que coordena as operações. Aceita conexões de múltiplos clientes, solicita capturas periodicamente e salva as imagens recebidas em arquivos.
- **Espião (espiao.py)**: Cliente que se conecta ao servidor, aguarda comandos e executa capturas de tela e webcam quando solicitado.

### Fluxo de Operação
1. O Gerente inicia um servidor WebSocket.
2. Os Espiões se conectam ao servidor usando o IP configurado.
3. A cada 60 segundos (configurável), o Gerente envia um comando "CAPTURAR" para todos os clientes conectados.
4. Cada Espião captura:
   - Screenshot da tela principal (usando PIL/Pillow)
   - Foto da webcam padrão (usando OpenCV)
5. As imagens são codificadas em Base64 e enviadas de volta ao Gerente.
6. O Gerente decodifica e salva as imagens em arquivos JPG na pasta `capturas/`.

## Pré-requisitos

- Python 3.7 ou superior
- Bibliotecas Python:
  - `websockets`
  - `Pillow` (para capturas de tela)
  - `opencv-python` (para webcam)

## Instalação

1. Clone ou baixe este repositório:
   ```bash
   git clone https://github.com/gwbrielandrea/Projeto-espi-o.git
   cd Projeto-espi-o
   ```

2. Instale as dependências:
   ```bash
   pip install websockets Pillow opencv-python
   ```

## Uso

### Executando o Gerente (Servidor)

1. Execute o script do gerente:
   ```bash
   python gerente.py
   ```

2. O servidor iniciará na porta 8765 e criará uma pasta `capturas/` para salvar as imagens.

### Executando o Espião (Cliente)

1. Configure o IP do gerente no arquivo `espiao.py`:
   ```python
   IP_GERENCIADOR = "ws://SEU_IP_AQUI:8765"  # ou "ws://localhost:8765" para teste local
   ```

2. Execute o script do espião:
   ```bash
   python espiao.py
   ```

3. O cliente tentará conectar ao servidor e aguardará comandos.

### Configurações

- **Período de captura**: Modifique `PERIODO_SOLICITACAO` em `gerente.py` (padrão: 60 segundos).
- **ID do funcionário**: Altere `ID_FUNCIONARIO` em `espiao.py` para identificar diferentes clientes.
- **Porta do servidor**: A porta 8765 pode ser alterada em `gerente.py`.

## Estrutura dos Arquivos

```
.
├── gerente.py          # Servidor (Gerente) - coordena operações
├── espiao.py           # Cliente (Espião) - executa capturas
├── capturas/           # Pasta criada automaticamente para salvar imagens
│   ├── Funcionario_01_tela_1647000000.jpg
│   ├── Funcionario_01_webcam_1647000000.jpg
│   └── ...
└── README.md           # Este arquivo
```

## Funcionalidades

- ✅ Conexão WebSocket persistente com reconexão automática
- ✅ Captura periódica de screenshots e webcam
- ✅ Suporte a múltiplos clientes simultâneos
- ✅ Salvamento automático de imagens com timestamp
- ✅ Codificação Base64 para transmissão segura
- ✅ Tratamento básico de erros

## Limitações

- Requer câmera webcam funcional no cliente
- Captura apenas a tela principal (não múltiplos monitores)
- Não inclui autenticação ou criptografia avançada
- Imagens são salvas localmente no servidor (considere armazenamento remoto para produção)

## Desenvolvimento

Para modificar o código:
- Adicione mais tipos de captura (áudio, teclado, etc.)
- Implemente autenticação de clientes
- Adicione compressão de imagens
- Integre com bancos de dados para armazenamento


## Contribuição

Contribuições são bem-vindas! Abra uma issue ou envie um pull request.
