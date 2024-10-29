import os
import random
from datetime import datetime
import uuid
import cv2
from fpdf import FPDF
import firebase_admin
from firebase_admin import credentials, storage

# Inicializa o Firebase Admin SDK
def initialize_firebase():
    cred = credentials.Certificate("/home/ideal_pad/Documentos/Projetos/credenciais.json")  # Caminho para o arquivo JSON das credenciais do Firebase
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'safeviewbd.appspot.com'  # Substitua pelo seu ID do projeto
    })

# Classe para gerar o PDF
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

def create_pdf_report(nome_pessoa, all_ok, img_path):
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

    # Carregar a imagem
    img = cv2.imread(img_path)
    if img is None:
        raise ValueError(f"Erro ao carregar a imagem: {img_path}")

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

    # Salvar o PDF em bytes
    byte_string = pdf.output(dest="S").encode('latin1')
    
    return byte_string, pdf_filename

# Função para fazer o upload do PDF para o Firebase Storage
def upload_pdf_to_firebase(byte_string, filename):
    # Acessar o bucket do Firebase
    bucket = storage.bucket()

    # Criar um blob (arquivo no bucket)
    blob = bucket.blob(f'{filename}')  # Pode ajustar o caminho como quiser
    
    # Fazer o upload do PDF
    blob.upload_from_string(byte_string, content_type='application/pdf')

    # Gerar uma URL de acesso ao arquivo (se público)
    blob.make_public()
    return blob.public_url

# Função para listar os PDFs do Firebase Storage
def list_pdfs_in_firebase():
    # Acessar o bucket do Firebase
    bucket = storage.bucket()

    # Listar todos os blobs (arquivos) no bucket
    blobs = bucket.list_blobs()

    pdf_files = []
    for blob in blobs:
        # Adiciona à lista apenas os arquivos PDF
        if blob.name.endswith('.pdf'):
            pdf_files.append(blob.name)

    return pdf_files

# Função para fazer o download do PDF do Firebase Storage
def download_pdf_from_firebase(pdf_filename, local_download_path):
    # Acessar o bucket do Firebase
    bucket = storage.bucket()

    # Criar um blob (arquivo no bucket) com base no nome do arquivo
    blob = bucket.blob(pdf_filename)

    # Fazer o download do arquivo para o caminho especificado
    blob.download_to_filename(local_download_path)

    print(f"PDF '{pdf_filename}' baixado com sucesso para {local_download_path}")

# Função principal
def main():
    # Inicializar Firebase
    initialize_firebase()
    
    # Gerar o PDF como bytes
    nome_pessoa = "A"
    all_OK = True
    analyzed_image_path = "/home/ideal_pad/Documentos/Projetos/SafeView_v01/BackEnd/ScreenShot/faces/Paulo.jpeg"
    
    # Passando o caminho da imagem em vez do objeto
    pdf_bytes, pdf_filename = create_pdf_report(nome_pessoa, all_OK, analyzed_image_path)

    # Fazer o upload para o Firebase
    public_url = upload_pdf_to_firebase(pdf_bytes, pdf_filename)
    print("URL pública do PDF:", public_url)

    # Listar os arquivos PDF no bucket
    print("\nLista de arquivos PDF no bucket do Firebase:")
    pdf_files = list_pdfs_in_firebase()
    
    for pdf_file in pdf_files:
        print(pdf_file)

    # Solicitar o nome do PDF a ser baixado
    pdf_to_download = input("\nDigite o nome do PDF que deseja baixar: ")

    if pdf_to_download in pdf_files:
        # Caminho local para salvar o PDF baixado
        local_download_path = os.path.join("downloads", pdf_to_download)
        os.makedirs("downloads", exist_ok=True)

        # Fazer o download do PDF do Firebase para o caminho local
        download_pdf_from_firebase(pdf_to_download, local_download_path)
    else:
        print(f"O arquivo '{pdf_to_download}' não está disponível no bucket.")

if __name__ == "__main__":
    main()
