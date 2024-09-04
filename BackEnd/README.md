# SafeView - Pasta BackEnd

A pasta backend deste projeto consiste na logica do aplicativo/software para a detecção dos EPI. (Possivelmente o servidor(API) python para envio de informações para o Front-End).
<br>
<br>

## Descrição dos arquivos:
<strong> phot.py </strong> --> Tira uma foto pela webcam, manda para o modelo analisar e retorna a foto analisada.

<strong> real_time.py </strong> --> Abre a Webcam e verifica em tempo real a detecção de EPI's.

<strong> ppe.pt </strong> --> Modelo YOLOv8 que analisa a detecção de EPI.
<br>
<br>
## Executar codigo:

1. Clone o repositorio:
```bash
git clone https://github.com/PauloPalauro/SafeView_v01.git
```

2. Abra o projeto no seu VScode e o acesse:
```bash
cd SafeView_v01
```

3. Crie um ambiente virtual e o ative:
```bash
python -m venv env
```

```bash
.\env\Scripts\activate
```

4. Instale as dependências:
```bash
pip install -r requirements.txt # Demora um pouco
```

5. Apos instalar todas as dependencias, execute os projeto:
```bash
python phot.py 
```
```bash
python real_time.py 
```

* OBS: Alterar o caminho dos modelos e da imagem nos codigos.