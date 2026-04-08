# Analisador de Objetos - Prova de Conceito (Visão Computacional)

Este plano descreve o desenvolvimento de um script em Python que servirá como prova de conceito (PoC) para analisar objetos não uniformes em imagens, extraindo características como tamanho (baseado em uma referência), circunferência (perímetro) e cor dominante.

## User Review Required

> [!IMPORTANT]
> O script precisará de uma imagem de teste para funcionar. Essa imagem deve conter:
> 1. O objeto que deseja analisar.
> 2. Um **objeto de referência** (ex: uma moeda com diâmetro conhecido) no canto esquerdo da imagem para calibrarmos o fator de `píxeis_por_centímetro` e obtermos medidas reais no resultado.
> Você tem uma imagem para testarmos depois, ou eu devo gerar uma imagem sintética para testar como base?

## Proposed Changes

Os arquivos serão criados no diretório `f:\TCC`.

---

### Ambiente e Dependências

Criação dos arquivos necessários para rodar o ambiente:

#### [NEW] [requirements.txt](file:///f:/TCC/requirements.txt)
Vamos adicionar as bibliotecas matemáticas e de visão computacional.
- `opencv-python`
- `numpy`
- `scikit-learn` (para clusterização de cor via K-Means)
- `imutils` (funções auxiliares de processamento)

#### [NEW] [analisador_objetos.py](file:///f:/TCC/analisador_objetos.py)
Este será o módulo central. Ele fará as seguintes operações:
1. **Carregar a imagem** de um caminho especificado no disco.
2. **Pré processamento:** Conversão em escala de cinza e aplicação do detector de bordas *Canny*.
3. **Extração de Contornos:** Uso das funções do `cv2` para separar cada objeto.
4. **Calibragem:** Assumiremos sempre que o objeto mais à esquerda na imagem é a "referência" (ex: uma moeda de 2.7 cm).
5. **Cálculos:**
   - **Tamanho:** Extrair as medidas de largura/altura da *Bounding Box* baseada nos pontos extremos, escalando por píxeis da calibragem.
   - **Circunferência:** Computar o comprimento do contorno não regular em centímetros.
   - **Cor:** Utilizar um algoritmo de Máscara em conjunto com K-Means Cluster para descobrir a cor principal do objeto alvo.

## Open Questions

> [!WARNING]
> Inicialmente para o nosso código, o "objeto de referência de tamanho fixo" necessitará ficar posicionado sempre **à esquerda** de todos os outros objetos na foto, para que o robô consiga identificá-lo ordenando as coordenadas X (da esquerda para direita). Podemos manter este critério para a prova de conceito?

## Verification Plan

### Automated Tests
- Executaremos o comando de instalação de dependência via powershell no ambiente local: `pip install -r requirements.txt`.

### Manual Verification
- Rodar o script python passando o endereço de uma foto e validar se no console serão exibidos o *Tamanho, Circunferência e Código das Cores (RGB)* com verossimilhança.
