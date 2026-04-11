# Guia de Padronização para Captura Fotográfica de Peças Cirúrgicas

Este guia visa padronizar as fotografias de peças anatômicas ou cirúrgicas para que o "Sistema de Visão Computacional" consiga ler, analisar e extrair medidas e propriedades corretamente das imagens. Imagens capturadas fora dessa padronização podem resultar em laudos falhos ou recusa no processamento.

---

## 1. Preparação do Ambiente e Superfície

- **Superfície Contrastante:** Posicione a peça sobre uma superfície lisa, limpa e com cor contrastante. Uma bandeja cirúrgica fosca de cor azul ou campo cirúrgico verde costumam ter resultados ótimos para ressaltar as bordas de tecidos corporais do fundo. Evite superfícies brancas.
- **Limpeza de Fundo:** Remova ao máximo o excesso de sangue vivo ou líquidos esparsos da bandeja ao redor da peça. Poças grandes ao redor da amostra podem fazer com que o sistema contabilize o fluido como "massa da peça".
- **Iluminação Uniforme:** O ambiente deve ser muito bem iluminado. Tente posicionar a luz para que o "Brilho" (Refletividade) na peça úmida não seja tão violento. O uso de refletores e iluminação difusa (que não foque tanto num ponto específico) costuma reduzir muito reflexos especulares indevidos. Reflexos fortes podem seccionar ou binarizar áreas erradas.

---

## 2. Itens Obrigatórios no Enquadramento da Foto

Para que a inteligência de Visão Computacional funcione e reconheça as medidas precisas e identifique o laudo de quem se trata, a foto **deve** conter obrigatoriamente 3 elementos num mesmo enquadramento sem estarem sobrepostos:

### ✔️ Marcador ArUco (Dicionário 4x4)
- **O que é:** É o padrão de rastreamento impresso (um quadrado tipo QR Code pequeno).
- **Posição:** Deve estar perfeitamente plano na mesa ou bandeja, preferencialmente num canto da foto em que o tecido orgânico não o tampe e os fluidos/sangue não manchem suas bordas brancas (Zona Silenciosa do marcador).
- **Importante:** A calibração dos pixels na foto real vai calcular sua medida a partir desse marcador, utilizando `5 cm x 5 cm` como tamanho de borda a borda. Imprima exatamente nessa medida antes de esterilizar.

### ✔️ A Peça ou Múltiplos Fragmentos
- A(s) amostra(s) para medição. Posicione os pequenos fragmentos distantes alguns milímetros uns dos outros para que a IA detecte como objetos fisiológicos distintos (Pedaço 1, Pedaço 2).

### ✔️ Rastreabilidade do Paciente (Barcode / QR Code)
- A foto precisa incluir a etiqueta padrão do paciente, laudo, ou frasco que contenha o impresso em Código de Barras (tradicional) ou QR Code nítido. Essa parte é imperativa para geração do Laudo Automático atrelado ao banco de dados do Hospital.

---

## 3. Direcionamento e Postura da Câmera

1. **Paralelismo (Vista Vertical - Bird's Eye):** Segure a câmera/smartphone *exatamente paralela* (ângulo de 90° graus) à mesa onde a peça se encontra, como se você olhasse puramente de cima. Tirar fotos muito "de lado" ou inclinadas prejudicará profundamente as dimensões e achatamento dos Pixels capturados na fotografia.
2. **Estabilização:** Mantenha a câmera o mais estável possível. Se necessário ou implementado em rotina longa, acople um braço mecânico ou tripé sobre um estande que bata as fotos por comando de voz/pedal. Fotos borradas prejudicarão o contraste de limites e falharão a extração da Circularidade/Área.
3. **Mantenha tudo no quadro:** Não preencha 100% dos cantos da câmera apenas com o tecido. Sempre deixe margem ("espaço de respiro") entre os três elementos vitais (Peça, ArUco, Etiqueta) na tela.

---

*Ciente e seguindo as instruções acima, a validação processual da imagem gerará sistematicamente um PDF perfeito atestando a coleta da arquitetura local.*
