import os
from flask import Flask, render_template, request
from openai import OpenAI
import fitz  # PyMuPDF
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from dotenv import load_dotenv

# 🔒 Carrega chave da OpenAI de variável de ambiente
load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_key)

# 🚀 Inicializa app Flask
app = Flask(__name__)

# 📘 Extrai texto de PDF
def extrair_texto_pdf(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    return "".join(page.get_text() for page in doc)

# 🌐 Extrai texto de um link
def extrair_texto_link(url):
    try:
        resposta = requests.get(url, timeout=10)
        sopa = BeautifulSoup(resposta.text, 'html.parser')
        return ' '.join([p.text for p in sopa.find_all('p')])
    except Exception as e:
        return f"Erro ao acessar o link: {str(e)}"

# 🧠 Gera perguntas por nível com explicações
def gerar_perguntas_niveis(conteudo):
    prompt = f"""
Crie 3 perguntas FÁCEIS, 3 MÉDIAS e 3 DIFÍCEIS com base no conteúdo abaixo.
Inclua alternativas e explique cada resposta correta.

Conteúdo: {conteudo[:2000]}
"""
    resposta = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return resposta.choices[0].message.content

# 💬 Chatbot IA para dúvidas
def chatbot_resposta(pergunta, contexto):
    prompt = f"{contexto}\n\nPergunta: {pergunta}\nResposta:"
    resposta = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return resposta.choices[0].message.content

# 🎯 Curiosidades sobre o conteúdo
def gerar_curiosidades(conteudo):
    prompt = f"Me dê 5 curiosidades interessantes sobre este conteúdo: {conteudo[:1000]}"
    resposta = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return resposta.choices[0].message.content

# 📊 Gráfico de desempenho (simulado)
def gerar_grafico_desempenho():
    niveis = ['Fácil', 'Médio', 'Difícil']
    acertos = [3, 2, 1]
    plt.figure(figsize=(6, 4))
    plt.bar(niveis, acertos, color='skyblue')
    plt.title('Desempenho do Aluno')
    plt.ylabel('Acertos')
    plt.savefig('static/desempenho.png')
    plt.close()

# 🌐 Rota principal
@app.route('/', methods=['GET', 'POST'])
def index():
    resultado = perguntas = curiosidades = resposta_chat = ""
    if request.method == 'POST':
        conteudo = ""
        if 'pdf' in request.files and request.files['pdf'].filename != "":
            conteudo = extrair_texto_pdf(request.files['pdf'])
        elif 'link' in request.form and request.form['link'] != "":
            conteudo = extrair_texto_link(request.form['link'])

        if conteudo:
            perguntas = gerar_perguntas_niveis(conteudo)
            curiosidades = gerar_curiosidades(conteudo)
            gerar_grafico_desempenho()
            if 'pergunta_chat' in request.form and request.form['pergunta_chat'] != "":
                resposta_chat = chatbot_resposta(request.form['pergunta_chat'], conteudo)
        else:
            resultado = "Nenhum conteúdo fornecido."

    return render_template('index.html',
                           perguntas=perguntas,
                           curiosidades=curiosidades,
                           resposta_chat=resposta_chat,
                           imagem_grafico="static/desempenho.png")

# 🔁 Executa o app
if __name__ == '__main__':
    app.run(debug=True)

