import uuid
from fpdf import FPDF
import os
import random
from datetime import datetime
import cv2
from io import BytesIO

class PDF(FPDF):
    def header(self):
        # Define a cor do cabeçalho (RGB)
        self.set_fill_color(70, 130, 180)  # Azul meio-escuro
        # Desenha um retângulo para o fundo do cabeçalho
        self.rect(0, 0, self.w, 20, 'F')  # 'F' para preenchimento sólido
        # Configura o texto do cabeçalho
        self.set_xy(10, 10)
        self.set_text_color(255, 255, 255)  # Texto branco
        self.set_font('Arial', 'B', 50)
        self.cell(0, 10, 'SafeView', 0, 0, 'L')

    def footer(self):
        # Define a cor do rodapé (RGB)
        self.set_fill_color(70, 130, 180)  # Azul meio-escuro, mesma cor do cabeçalho
        # Desenha um retângulo para o fundo do rodapé
        self.rect(0, self.h - 20, self.w, 20, 'F')  # Desenha o retângulo do rodapé
        # Configura o texto do rodapé
        self.set_y(-15)
        self.set_text_color(255, 255, 255)  # Texto branco
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

def create_pdf_report(nome_pessoa, all_ok, img):
    # Criar diretório para relatórios
    pdf_directory = "relatorios"
    os.makedirs(pdf_directory, exist_ok=True)

    # Obter a data e hora atual e formatar para o nome do arquivo
    now = datetime.now()
    data_hora = now.strftime("%d/%m/%Y %H:%M:%S")
    data_hora_nome = now.strftime("%d-%m-%y %H-%M")  # Formato de nome de arquivo seguro

    # Gerar um ID aleatório para o relatório
    report_id = uuid.uuid4().int >> 64
    report_id_str = str(report_id)

    # Nome do arquivo PDF com ID, nome e data
    pdf_filename = f"{report_id_str} - {nome_pessoa} - {data_hora_nome}.pdf"
    pdf_output_path = os.path.join(pdf_directory, pdf_filename)

    # Salvar temporariamente a imagem para o PDF
    temp_img_path = f"temp_{report_id_str}.jpg"
    cv2.imwrite(temp_img_path, img)

    # Gerar o PDF
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.ln(10)

    # Título do relatório
    pdf.ln(10)
    pdf.cell(0, 10, "Relatório de Análise de Segurança", ln=True, align="C")

    # Inserir a imagem analisada no PDF
    pdf.ln(10)
    pdf.cell(0, 10, "Imagem Analisada:", ln=True)

    # Define o posicionamento da imagem um pouco mais para cima
    image_width = 100
    image_height = 100
    x_center = (pdf.w - image_width) / 2
    y_center = (pdf.h - image_height) / 2 - 35  # Ajuste para colocar a imagem mais para cima
    
    pdf.image(temp_img_path, x=x_center, y=y_center, w=image_width, h=image_height)
    pdf.ln(10)

    # Pula uma linha após a imagem
    pdf.ln(image_height / 2 + 40)  # Posição para a seção de informações

    # Detalhes do relatório
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(0, 10, f"Nome: {nome_pessoa}", ln=True)
    pdf.cell(0, 10, f"Status de Segurança: {'OK' if all_ok else 'Faltando itens de segurança'}", ln=True)
    pdf.cell(0, 10, f"Data e Hora da Análise: {data_hora}", ln=True)  # Adiciona a data e hora

    # Salvar o PDF
    pdf.output(pdf_output_path)

    # Remover arquivo temporário da imagem
    os.remove(temp_img_path)

    return pdf_output_path