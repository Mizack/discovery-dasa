# Manual Técnico: Sistema de Visão Computacional Médica

Este documento serve como referência para os desenvolvedores e engenheiros envolvidos com o sistema de análise e medição de amostras cirúrgicas via captura de imagem.

---

## 1. Requisitos de Ambiente

Para o setup e suporte do motor do algoritmo, a infraestrutura exige:
- **Linguagem Principal:** Python 3.7 ou superior
- **Arquitetura Base:** Biblioteca Computacional OpenCV (`cv2`), `NumPy`, `SciPy` e ferramentas auxiliares `imutils`.

### Dependências via PIP
As ferramentas não-nativas utilizadas pelas regras médicas e de relatórios requerem as instalações (preferencialmente isoladas num `venv`):
```bash
pip install opencv-contrib-python pyzbar fpdf scipy scikit-learn numpy
```
*(Nota: O PyZBar no Windows requer o pacote redistribuível extra do Visual C++ instalados caso você possua erros de leitura do arquivo DLL)*.

---

## 2. Arquitetura Modular (Como funciona por debaixo dos panos)

A aplicação foi descentralizada do monólito isolado original para os seguintes nós para garantia de manutenibilidade do ciclo estrito e patológico dos dados:

1. **`analisador_objetos.py` (Módulo Orchestrator principal):**
   - É o motor CLI. Ele ingere os argumentos sistêmicos (`img_path`). 
   - Procura o scanner do pyzbar (etiquetas). Orquestra os pacotes importados, e caça ativamente o limiar das detecções morfológicas passando os arrays do ArUco em `.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)`.
2. **`utils_imagem.py` (Visão Avançada e Filtros):** 
   - Possui ferramentas de engenharia de pixel como o `remover_reflexos_especulares()`: uma manipulação robusta por _Inpainting_ na Telea API ou Limiares focando em achatar pontos de saturação causadas nos tecidos hiper-refletivos (brilho úmido do bloco operatório). 
   - E extrações de contorno de métricas clínicas difíceis, como a Convexidade (`cv2.convexHull`) e o limite de Circularidade sobre bordas tumorosas.
3. **`gerador_pdf.py` (Laudos Automatizados):** 
   - Transita as medições abstratas cruas (x, y, distâncias em cm, área em Pixels2Cm2) usando layouts simplificados construídos dentro da camada abstrata no pacote `fpdf`. Este nó não depende de visão, ele apenas desenha em disco o `laudo_Paciente_xyz.pdf`.

---

## 3. Como Executar (Ambiente Produtivo em Consola)

Para processar fotografias e emitir o Laudo PDF:

1. Ative seu Virtual Environment (se aplicável), e garanta estar no caminho CWD da pasta.
2. Mande o Python evocar o script anexando de forma bruta a foto requerida da operação.
```bash
python analisador_objetos.py caminhos/para/fotografia_da_cirurgia.jpg
``` 

*Sintaxe Padrão CLI: `python [script] [input_img_path]`*

**Teste Interno Sistêmico (Mock pipeline)**:  
Para atestar funcionamento dos limiares da máquina (ArUco, OpenCV Kernels, Inpaintings, OCR Pyzbar), criamos o arquivo sintético. Rodar puro: `python gerar_mock_imagem.py`, seguido de uma corrida com o `python analisador_objetos.py imgs/mock_teste.jpeg`. 

---

## 4. Ajustes Manuais Requeridos (Calibrações de Produção)

Ao colocar esse robô numa bancada real de hospital ou ambulatório cirúrgico, o desenvolvedor primário deve editar manualmente os seguintes valores "hardcoded":
1. **Calibração Real Física da Régua:** 
   Procure por `ARUCO_SIZE_CM = 5.0` no cabeçalho do `analisador_objetos.py` e alterne obrigatoriamente e rigidamente para a **mesma** dimensão de largura do quadrado do ArUco que for plotado ou colado no balcão real na lateral da Peça anatômica para garantir o peso dimensional de pixel perfeito na foto.
2. **Adaptações de Sombras:** Dependendo da câmera e do LED Hospitalar superior, o Threshold adaptável presente em `analisador_objetos.py` via _Otsu_, ou as dilatações das bordas da peça podem requerer ajustes nos `iterations=`. Alterações na dilatação da imagem cinza determinam se partes separadas de tecidos e ramificações se unem no mapeamento de massa final ou isolam poças de sangramento como entidades isoladas de tecido.
