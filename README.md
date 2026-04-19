# Analisador de Peças Cirúrgicas (PathoScan)

Este projeto é um sistema de visão computacional desenvolvido em Python para a análise e medição de peças cirúrgicas e anatômicas. Ele realiza a detecção do contorno, a calibração de escala utilizando marcadores ArUco, extrai métricas morfológicas (área, convexidade, circularidade) e a cor predominante. O projeto também atua como uma WebApp com uma Interface Visual clínica, comunicando-se com uma API e gerando um laudo de patologia automaticamente em formato PDF.

## ⚙️ Pré-requisitos e Instalação

1. Certifique-se de ter o Python 3.x instalado.
2. É recomendado o uso de um ambiente virtual (ex: `venv`).

Para criar e ativar o ambiente virtual:
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

*(Obs: Algumas das dependências podem precisar de binários instalados no sistema para funcionar perfeitamente, como ferramentas do pyzbar - no Windows ele costuma trazer embutido, no Linux instale o `zbar` via gerenciador de pacotes)*.

## 🚀 Arquitetura e Como Executar a WebApp

Para garantir uma escalabilidade futura para nuvem (AWS Serverless), o projeto está dividido em duas frentes de microsserviços. O Backend faz o processamento das imagens e chamadas de classes usando **AWS Chalice** (pronto para ser deployado como Lambda Function na nuvem), e o Frontend age orquestrando a interface Web utilizando as engrenagens de servidor **Flask**.

Para rodar a prova de conceito Web completa, você deverá levantar ambas as aplicações localmente utilizando dois terminais isolados.

### Terminal 1: Iniciando o Backend API (Chalice)
A API recebe a chamada e atua nativamente em POO injetando a classe `AnalisadorObjetos` provinda do Script de inferência de visão computacional.

1. Abra um terminal e ative o seu `venv`.
2. Entre na pasta dedicada do backend.
3. Inicie o framework local do chalice:
```bash
cd backend
chalice local
```
*-> Seu backend processador computará em `http://127.0.0.1:8000`.*

### Terminal 2: Iniciando o Frontend Web (Flask)
O Server web se responsabiliza unicamente de empacotar o HTML/CSS/JS usando o micro-sistema de views Jinja2 do Flask, atuando totalmente desacoplado da lógica cirúrgica.

1. Abra outro terminal na pasta raiz do projeto e ative o seu `venv`.
2. Inicie o servidor frontend client-side:
```bash
python app.py
```
*-> Sua tela de exames e logs estará servindo as sessões em `http://127.0.0.1:8080`.*

Você pode entrar via Navegador na porta 8080 e enviar uma de suas imagens ou blocos de corte!

---

## 🔧 Depuração Via Terminal / Modo CLI 

Se você trabalha como engenheiro de dados precisando validar calibrações sem necessitar das subidas de rede Localhost e Endpoints, o script mãe detém invocações por Main independentemente:

```bash
# Executa usando a imagem padrão (se ele encontrar e existir) em imgs/image_2.jpeg
python analisador_objetos.py

# Ou testando uma casuística própria passando o caminho de uma imagem específica via argumento local
python analisador_objetos.py caminho/para/sua_foto_com_Aruco.jpg
```

### Geração de Marcadores de Escala Real (Opcional)
Você irá precisar do ArUco próximo das peças orgânicas para que o algoritmo destrinche a calibragem. Se perder a etiqueta original pode reimprimir um com o tamanho exato universal da Dasa (`5.0cm`):
```bash
python gerar_aruco_impressao.py
```

---

## 📖 Contexto Cirúrgico (Anotações e Práticas)

O pipeline do OpenCV foca nos rigorosos requisitos de um sistema de avaliação de macroscopia:

1. **Padrões de Referência Clínicos:** Utilização de Marcadores ArUco/Fiduciais em vez de réguas clássicas em fotos, facilitando identificações matemáticas de 4 cantos perfeitos independente de rotações manuais enviesadas por humanos fotógrafos.
2. **Tratamento Especular (Tecidos Úmidos):** Filtros previnem que fluidos e iluminação de centro cirúrgico mascarem buracos fisiológicos, separando perfeitamente a gordura/epitélio de poças de água e sangue pelo uso de saturação de canais HSV e Gaussian Blurs.
3. **Rastreamento de ID (End-to-End):** Adoção de decoders pyzbar correlacionando o pedaço biológico ao braço QR Code fixo ou pulseira da pessoa em imagem, validando as pontas antes da cirurgia transacionar para patologia clínica final.
4. **Morfologia Atípica:** Além de extrair retângulos óbvios, as fórmulas geram coeficientes vitais a tumores de beiras irregulares, como dados de Convexidade, Diâmetro e Circularidade paramétricos por Diâmetro Feret Máximo.
5. **Automação do Emissor Documental (PDF):** Relatórios montados programaticamente com todas as métricas preenchidas em conjunto com a coloração RGB dominante mapeada, não apenas otimizando e abolindo o erro humano analógico mas cortando minutos vitais a diagnósticos patológicos pós-operação.