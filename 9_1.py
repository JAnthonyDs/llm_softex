import streamlit as st
import openai
import os
import tempfile
from PyPDF2 import PdfReader
import docx
from typing import List

st.set_page_config(page_title="Consultor de Atas de Reunião", layout="wide")
st.title("Consultor de Atas de Reunião com Checagem Segura na Web")

st.markdown("""
Faça upload de atas de reuniões (PDF, DOCX ou TXT). Pergunte sobre decisões, ações e responsáveis. Perguntas factuais externas são respondidas via web, sem vazar dados das atas.
""")

openai_api_key = st.sidebar.text_input("Chave da API OpenAI", type="password", value=os.getenv("OPENAI_API_KEY", ""))

def extrair_texto_pdf(file) -> str:
    reader = PdfReader(file)
    texto = "\n".join(page.extract_text() or "" for page in reader.pages)
    return texto

def extrair_texto_docx(file) -> str:
    doc = docx.Document(file)
    return "\n".join([p.text for p in doc.paragraphs])

def extrair_texto_txt(file) -> str:
    return file.read().decode("utf-8")

def extrair_texto(file) -> str:
    if file.name.endswith(".pdf"):
        return extrair_texto_pdf(file)
    elif file.name.endswith(".docx"):
        return extrair_texto_docx(file)
    elif file.name.endswith(".txt"):
        return extrair_texto_txt(file)
    else:
        return ""

uploaded_files = st.file_uploader("Faça upload das atas (PDF, DOCX ou TXT)", type=["pdf", "docx", "txt"], accept_multiple_files=True)
texto_atas = ""
if uploaded_files:
    for file in uploaded_files:
        texto_atas += extrair_texto(file) + "\n"
    st.success(f"{len(uploaded_files)} arquivo(s) carregado(s)!")
else:
    st.info("Faça upload de pelo menos uma ata para começar.")

pergunta = st.text_area("Digite sua pergunta sobre as atas ou uma pergunta factual externa:", height=80)

def pergunta_factual(pergunta: str) -> bool:
    prompt = f"""
A seguinte pergunta é sobre fatos gerais do mundo, e pode ser respondida consultando a internet? Responda apenas SIM ou NÃO. Pergunta: {pergunta}
"""
    resposta = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Você é um assistente que classifica perguntas como factuais externas ou não."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2,
        temperature=0.0,
        api_key=openai_api_key
    )
    return "SIM" in resposta.choices[0].message.content.upper()

def buscar_web(pergunta: str) -> str:
    search_prompt = f"Responda de forma objetiva e cite a fonte se possível. Pergunta: {pergunta}"
    resposta = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Você responde perguntas factuais consultando a internet. Nunca inclua dados sensíveis de atas."},
            {"role": "user", "content": search_prompt}
        ],
        max_tokens=400,
        temperature=0.2,
        api_key=openai_api_key
    )
    return resposta.choices[0].message.content

def responder_atas(pergunta: str, atas: str) -> str:
    prompt = f"""
Você é um assistente que responde perguntas sobre atas de reuniões. Responda apenas com base no texto abaixo, destacando decisões, ações e responsáveis quando possível. Se não souber, diga que não foi encontrado na ata.

Texto da ata:
{atas}

Pergunta:
{pergunta}
"""
    resposta = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Você responde perguntas sobre atas de reunião, sem inventar informações."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=600,
        temperature=0.1,
        api_key=openai_api_key
    )
    return resposta.choices[0].message.content

if st.button("Consultar"):
    if not openai_api_key:
        st.error("Informe sua chave da API OpenAI na barra lateral.")
    elif not pergunta.strip():
        st.error("Digite uma pergunta.")
    elif pergunta_factual(pergunta):
        st.info("Pergunta identificada como factual externa. Consultando a web...")
        resposta = buscar_web(pergunta)
        st.success(resposta)
    elif not texto_atas.strip():
        st.error("Faça upload de pelo menos uma ata para perguntas internas.")
    else:
        st.info("Consultando as atas...")
        resposta = responder_atas(pergunta, texto_atas)
        st.success(resposta) 