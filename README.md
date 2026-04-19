# Analisador de Peças Cirúrgicas

Este projeto é um sistema de visão computacional desenvolvido em Python para a análise e medição de peças cirúrgicas e anatômicas. Ele realiza a detecção do contorno, a calibração de escala utilizando marcadores ArUco, extrai métricas morfológicas (área, convexidade, circularidade) e a cor predominante. Ao final, gera um laudo em formato PDF.

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

*(Obs: Algumas das dependências podem precisar de instâncias nativas instaladas no sistema rodando, como ferramentas do pyzbar - no Windows ele costuma trazer os binários embutidos, no Linux pode precisar instalar o `zbar` via gerenciador de pacotes)*.

## 🚀 Como Executar

### 1. Imagem de Entrada
Por padrão, o script principal buscará por uma imagem para analisar. Ele procura em `imgs/image_2.jpeg`. Você também pode passar o caminho de uma imagem específica como argumento.

### 2. Rodando o Analisador
Execute o script principal do projeto:

```bash
# Executa usando a imagem padrão em imgs/image_2.jpeg
python analisador_objetos.py

# Ou, passando uma imagem específica na linha de comando
python analisador_objetos.py caminho/para/sua_imagem.jpg
```

### 3. Resultados
Ao rodar com sucesso, o script emitirá no terminal os dados identificados na imagem e realizará várias rotinas:
- Detecção da identificação do paciente (via Código de Barras / QR Code).
- Detecção do Marcador ArUco para calibrar os pixels para centímetros (considerando que na impressão este deva ter `5.0 cm`).
- Extração dos fragmentos com medidas em centímetros.
- Geração da imagem com overlays visuais: `imgs/imagem_analisada_medica.jpg`.
- Criação de um laudo PDF da análise na mesma pasta que o script (ex: `laudo_Paciente_Desconhecido.pdf`).

### 4. Geração de Marcadores ArUco (Opcional)
Se precisar imprimir um novo marcador ArUco para a escala no ambiente clínico, rode:
```bash
python gerar_aruco_impressao.py
```
Esse script vai gerar ou um arquivo em imagem ou um PDF pronto para a impressão usando um marcador do dicionário 4X4_50.

---

## 📖 Histórico e Contexto Clínico (Anotações do Projeto)

O processo atual foca nos rigorosos requisitos de um sistema de patologia médico:

1. **Padrões de Referência Clínicos:** Utilização de Marcadores ArUco/Fiduciais em vez de papel A4 porque são higienizáveis e escalam milimetricamente.
2. **Tratamento de Reflexos (Tecidos Úmidos):** Filtros previnem que fluidos ou sangramentos sejam lidos como tecido sólido ou que a luz reflita no objeto e mascare buracos, separando tecido sólido válido do fluido circundante.
3. **Rastreabilidade e Gestão de Dados:** Adoção de Pyzbar para relacionar sempre a imagem a um código QR ou bar code que vincula automaticamente os resultados dos fragmentos e amostras para um ID seguro do paciente.
4. **Forma e Margens:** Além do simples Retângulo e Bounding Box, agora é extraída métrica morfológica avançada:
    - Convexidade
    - Circularidade
    - Margens extraídas com diâmetro de Feret para garantir que assimetrias sejam reportadas no laudo anatômico.
5. **Geração de Relatório PDF Final:** Geração automática do resultado que mescla a silhueta, calibrações métricas e as variações de cores com o FPDF, economizando o tempo na tradução das console-logs para interfaces passíveis de leitura por patologistas.