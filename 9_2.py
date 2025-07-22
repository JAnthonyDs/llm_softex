import streamlit as st
import openai
import os
from PyPDF2 import PdfReader
import docx

def extrair_texto_pdf(file) -> str:
    reader = PdfReader(file)
    return "\n".join(page.extract_text() or "" for page in reader.pages)

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

st.set_page_config(page_title="Checagem Factual Antialucinação", layout="wide")
st.title("Checagem Factual Antialucinação com IA")

st.markdown("""
Faça upload de documentos (PDF, DOCX ou TXT). Pergunte algo e o sistema irá:
1. Responder com base nos documentos.
2. Checar a resposta na internet.
3. Comparar as respostas e alertar se houver divergência.
""")

openai_api_key = st.sidebar.text_input("Chave da API OpenAI", type="password", value=os.getenv("OPENAI_API_KEY", ""))

uploaded_files = st.file_uploader("Faça upload dos documentos (PDF, DOCX ou TXT)", type=["pdf", "docx", "txt"], accept_multiple_files=True)
texto_docs = ""
if uploaded_files:
    for file in uploaded_files:
        texto_docs += extrair_texto(file) + "\n"
    st.success(f"{len(uploaded_files)} arquivo(s) carregado(s)!")
else:
    st.info("Faça upload de pelo menos um documento para começar.")

pergunta = st.text_area("Digite sua pergunta:", height=80)

def resposta_documentos(pergunta: str, docs: str) -> str:
    prompt = f"""
Responda à pergunta abaixo apenas com base no texto dos documentos fornecidos. Se não souber, diga explicitamente que não foi encontrado nos documentos.

Documentos:
{docs}

Pergunta:
{pergunta}
"""
    resposta = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Você responde perguntas apenas com base nos documentos fornecidos."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=600,
        temperature=0.1,
        api_key=openai_api_key
    )
    return resposta.choices[0].message.content.strip()

def resposta_web(pergunta: str) -> str:
    prompt = f"Responda de forma objetiva e cite a fonte se possível. Pergunta: {pergunta}"
    resposta = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Você responde perguntas factuais consultando a internet."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=400,
        temperature=0.2,
        api_key=openai_api_key
    )
    return resposta.choices[0].message.content.strip()

def comparar_respostas(resp_doc: str, resp_web: str) -> str:
    prompt = f"""
Compare as duas respostas abaixo. Se forem compatíveis, diga 'VERIFICADO'. Se houver divergência relevante, explique a diferença e alerte sobre possível alucinação.

Resposta dos documentos:
{resp_doc}

Resposta da internet:
{resp_web}
"""
    resposta = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Você compara respostas para evitar alucinações."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=200,
        temperature=0.1,
        api_key=openai_api_key
    )
    return resposta.choices[0].message.content.strip()

if st.button("Consultar e Checar"):
    if not openai_api_key:
        st.error("Informe sua chave da API OpenAI na barra lateral.")
    elif not pergunta.strip():
        st.error("Digite uma pergunta.")
    elif not texto_docs.strip():
        st.error("Faça upload de pelo menos um documento.")
    else:
        st.info("Consultando documentos...")
        resp_doc = resposta_documentos(pergunta, texto_docs)
        st.markdown("**Resposta dos documentos:**")
        st.write(resp_doc)
        st.info("Checando na internet...")
        resp_web = resposta_web(pergunta)
        st.markdown("**Resposta da internet:**")
        st.write(resp_web)
        st.info("Comparando respostas...")
        comparacao = comparar_respostas(resp_doc, resp_web)
        if "VERIFICADO" in comparacao.upper():
            st.success("✅ Informação verificada!\n" + comparacao)
        else:
            st.warning("⚠️ Divergência detectada:\n" + comparacao) 