import os
import cv2
from fpdf import FPDF
from datetime import datetime

class LaudoPatologicoPDF(FPDF):
    def header(self):
        cor_primaria = (25, 42, 86)   # Azul marinho escuro sofisticado
        cor_cinza = (127, 140, 141)   # Cinza quente apagado
        
        # Logotipo na esquerda
        logo_path = 'imgs/logo.png'
        if os.path.exists(logo_path):
            self.image(logo_path, 10, 10, 40)
            
        # Título alinhado à direita
        self.set_y(15)
        self.set_font('Helvetica', 'B', 20)
        self.set_text_color(*cor_primaria)
        self.cell(0, 10, 'RELATORIO DE ANALISE CIRURGICA', align='R')
        
        # Subtítulo na direita
        self.ln(6)
        self.set_font('Helvetica', 'I', 11)
        self.set_text_color(*cor_cinza)
        self.cell(0, 10, 'Visao Computacional / Relatorio Automatizado', align='R')

        # Finíssima linha de separação
        self.set_y(38)
        self.set_draw_color(230, 230, 232)
        self.set_line_width(0.5)
        self.line(10, 38, 200, 38)
        self.ln(5)

    def footer(self):
        self.set_y(-20)
        
        # Linha separadora do rodapé
        self.set_draw_color(240, 240, 240)
        self.set_line_width(0.3)
        self.line(10, self.get_y(), 200, self.get_y())
        
        self.set_font('Helvetica', '', 9)
        self.set_text_color(160, 160, 160)
        
        data_hora = datetime.now().strftime("%d/%m/%Y as %H:%M")
        
        self.cell(100, 10, f'Documento gerado eletronicamente em {data_hora}', 0, 0, 'L')
        self.cell(0, 10, f'Pagina {self.page_no()} de {{nb}}', 0, 0, 'R')

def gerar_laudo_pdf(patient_id, objetos_metricas, caminho_imagem, saida_pdf="laudo_final.pdf"):
    """
    Gera um relatório médico em PDF com layout premium e imagem corrigindo Y aspect ratio.
    """
    pdf = LaudoPatologicoPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # --- BOX IDENTIFICACAO DO PACIENTE ---
    pdf.set_y(45)
    pdf.set_fill_color(248, 249, 250) # Cinza muito suave (quase branco)
    
    # Preenchimento e label
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(130, 130, 130)
    pdf.cell(50, 14, "   PACIENTE / REF:", fill=True, border=0)
    
    # Valor
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(25, 42, 86)
    pdf.cell(0, 14, str(patient_id), fill=True, border=0, ln=1)
    
    pdf.ln(10)
    
    # --- SESSÃO IMAGEM ---
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(44, 62, 80)
    pdf.cell(0, 8, "REGISTRO FOTOGRAFICO", ln=1)
    
    # Tracinho charmoso embaixo do título
    x_offset = pdf.get_x()
    y_offset = pdf.get_y()
    pdf.set_draw_color(44, 62, 80)
    pdf.set_line_width(0.6)
    pdf.line(x_offset, y_offset, x_offset + 25, y_offset)
    pdf.ln(8)
    
    if os.path.exists(caminho_imagem):
        # Ler tamanho da imagem para corrigir a quebra de página automática do FPDF
        img_loaded = cv2.imread(caminho_imagem)
        if img_loaded is not None:
            h_img, w_img, _ = img_loaded.shape
            aspect_ratio = h_img / w_img
            
            # Limitar largura da imagem a 140mm para ficar com margens bonitas
            render_w = 140
            render_h = render_w * aspect_ratio
            
            # Se a imagem for ocupar mais que a página atual (passar do y=250), joga pra nova página
            if pdf.get_y() + render_h > 250:
                pdf.add_page()
                
            x_img = (210 - render_w) / 2 # centralizar
            y_img = pdf.get_y()
            
            # Adicionar imagem
            pdf.image(caminho_imagem, x=x_img, y=y_img, w=render_w)
            
            # Avançar o cursor do Y proxima linha + margem
            pdf.set_y(y_img + render_h + 15)
        else:
            pdf.set_font('Helvetica', 'I', 11)
            pdf.set_text_color(200, 50, 50)
            pdf.cell(0, 10, '[Falha ao carregar arquivo de imagem]', ln=1)
    else:
        pdf.set_font('Helvetica', 'I', 11)
        pdf.set_text_color(200, 50, 50)
        pdf.cell(0, 10, '[Imagem nao disponivel no sistema]', ln=1)
        
    # --- METRICAS ---
    if pdf.get_y() > 230:
        pdf.add_page()
        
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(44, 62, 80)
    pdf.cell(0, 8, "ANALISE MORFOLOGICA", ln=1)
    
    y_offset = pdf.get_y()
    pdf.set_draw_color(44, 62, 80)
    pdf.set_line_width(0.6)
    pdf.line(10, y_offset, 35, y_offset)
    pdf.ln(8)
    
    for idx, obj in enumerate(objetos_metricas):
        # Evitar que a tabela quebre no meio
        if pdf.get_y() > 220:
             pdf.add_page()
             
        # Título do Fragmento
        pdf.set_fill_color(248, 249, 250)
        pdf.set_font('Helvetica', 'B', 12)
        pdf.set_text_color(25, 42, 86)
        pdf.cell(0, 10, f"  FRAGMENTO {idx + 1}", fill=True, ln=1)
        
        pdf.set_y(pdf.get_y() + 4)
        
        # Grid com 2 colunas
        col1_x = 15
        col2_x = 110
        y_start = pdf.get_y()
        
        def imprimir_linha(label, valor, x, y):
            pdf.set_xy(x, y)
            pdf.set_font('Helvetica', '', 10)
            pdf.set_text_color(140, 140, 140)
            pdf.cell(45, 6, label)
            
            pdf.set_font('Helvetica', 'B', 11)
            pdf.set_text_color(40, 40, 40)
            pdf.cell(40, 6, valor)
            
        # Linha 1
        imprimir_linha("Largura (Bounding):", f"{obj['dim_w']:.2f} cm", col1_x, y_start)
        imprimir_linha("Altura (Bounding):", f"{obj['dim_h']:.2f} cm", col2_x, y_start)
        
        # Linha 2
        y_start += 9
        imprimir_linha("Diametro Maximo:", f"{obj['max_feret']:.2f} cm", col1_x, y_start)
        imprimir_linha("Area Calculada:", f"{obj['area_cm2']:.2f} cm2", col2_x, y_start)
        
        # Linha 3
        y_start += 9
        imprimir_linha("Índice Circularidade:", f"{obj['circularity']:.3f}", col1_x, y_start)
        imprimir_linha("Índice Convexidade:", f"{obj['convexity']:.3f}", col2_x, y_start)
        
        # Linha 4
        y_start += 9
        r, g, b = obj['color']
        pdf.set_xy(col1_x, y_start)
        pdf.set_font('Helvetica', '', 10)
        pdf.set_text_color(140, 140, 140)
        pdf.cell(45, 6, "Cor Predominante:")
        
        # Quadrado de amostra de cor visual + texto RGB
        pdf.set_fill_color(r, g, b)
        pdf.rect(col1_x + 35, y_start + 1.5, 4, 4, 'F')
        
        pdf.set_xy(col1_x + 42, y_start)
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(40, 40, 40)
        pdf.cell(40, 6, f"RGB({r}, {g}, {b})")
        
        # Avançar pra proxima iteração
        pdf.set_y(y_start + 15)
        
    pdf.output(saida_pdf, 'F')
    print(f"Laudo gerado com sucesso em: {saida_pdf}")
