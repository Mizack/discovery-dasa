import os
from fpdf import FPDF
from datetime import datetime

class LaudoPatologicoPDF(FPDF):
    def header(self):
        # Arial bold 15
        self.set_font('Arial', 'B', 15)
        # Título
        self.cell(0, 10, 'Laudo de Analise de Peca Cirurgica', border=False, ln=1, align='C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, 'Sistema de Visao Computacional Automatizado', border=False, ln=1, align='C')
        self.line(10, 30, 200, 30)
        self.ln(10)

    def footer(self):
        # Ir para a posição a 1.5 cm do fundo
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Número da página
        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.cell(0, 10, f'Gerado automaticamente em {data_hora} - Pagina {self.page_no()}/{{nb}}', 0, 0, 'C')

def gerar_laudo_pdf(patient_id, objetos_metricas, caminho_imagem, saida_pdf="laudo_final.pdf"):
    """
    Gera um relatório médico em PDF com a imagem processada e as dimensões calculadas.
    """
    pdf = LaudoPatologicoPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # Info Paciente
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f'ID do Paciente/Etiqueta: {patient_id}', ln=1)
    pdf.ln(5)
    
    # Inserir Imagem Analisada
    if os.path.exists(caminho_imagem):
        pdf.image(caminho_imagem, x=10, w=190)
    else:
        pdf.set_font('Arial', 'I', 10)
        pdf.cell(0, 10, '[Imagem nao disponivel no sistema]', ln=1)
    
    pdf.ln(10)
    
    # Detalhes das Medições
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Analise Morfologica dos Fragmentos', ln=1)
    
    for idx, obj in enumerate(objetos_metricas):
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, f'Fragmento {idx + 1}:', ln=1)
        
        pdf.set_font('Arial', '', 11)
        pdf.cell(0, 8, f" -> Largura Bounding Box: {obj['dim_w']:.2f} cm", ln=1)
        pdf.cell(0, 8, f" -> Altura Bounding Box: {obj['dim_h']:.2f} cm", ln=1)
        pdf.cell(0, 8, f" -> Diametro Maximo (ponta a ponta): {obj['max_feret']:.2f} cm", ln=1)
        pdf.cell(0, 8, f" -> Area: {obj['area_cm2']:.2f} cm²", ln=1)
        
        # Novas métricas
        pdf.cell(0, 8, f" -> Circularidade: {obj['circularity']:.3f} (1.0 = circulo perfeito)", ln=1)
        pdf.cell(0, 8, f" -> Convexidade: {obj['convexity']:.3f} (1.0 = sem reentrancias)", ln=1)
        
        r, g, b = obj['color']
        pdf.cell(0, 8, f" -> Cor Predominante (RGB): ({r}, {g}, {b})", ln=1)
        pdf.ln(5)
        
    pdf.output(saida_pdf, 'F')
    print(f"Laudo gerado com sucesso em: {saida_pdf}")
