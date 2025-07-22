import streamlit as st
import openai
import os

st.set_page_config(page_title="Tradutor de Código com IA", layout="wide")
st.title("Tradutor de Código com IA")

st.markdown("""
Cole seu código abaixo, escolha a linguagem de origem e a de destino, e a IA irá gerar uma versão equivalente adaptada para a linguagem escolhida, utilizando bibliotecas similares.
""")

openai_api_key = st.sidebar.text_input("Chave da API OpenAI", type="password", value=os.getenv("OPENAI_API_KEY", ""))

linguagens = [
    "Python",
    "JavaScript",
    "Java",
    "C#",
    "Go",
    "Ruby",
    "C++",
    "TypeScript",
    "Rust",
    "PHP"
]

codigo_entrada = st.text_area("Cole o código aqui:", height=300)
linguagem_origem = st.selectbox("Linguagem de origem", linguagens, index=0)
linguagem_destino = st.selectbox("Linguagem de destino", linguagens, index=1)

if st.button("Converter"):
    if not openai_api_key:
        st.error("Por favor, informe sua chave da API OpenAI na barra lateral.")
    elif not codigo_entrada.strip():
        st.error("Cole um código para converter.")
    elif linguagem_origem == linguagem_destino:
        st.warning("Escolha linguagens diferentes para conversão.")
    else:
        st.info("Convertendo código, aguarde...")
        prompt = f"""
Converta o código abaixo de {linguagem_origem} para {linguagem_destino}, adaptando para a sintaxe e melhores práticas da linguagem de destino. Use bibliotecas equivalentes quando possível. Explique brevemente se houver alguma limitação ou adaptação importante.

Código de origem ({linguagem_origem}):
{codigo_entrada}

Código convertido ({linguagem_destino}):
"""
        try:
            openai.api_key = openai_api_key
            resposta = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Você é um especialista em tradução de código entre linguagens."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1200,
                temperature=0.1
            )
            resultado = resposta.choices[0].message.content
            st.subheader(f"Código convertido para {linguagem_destino}:")
            st.code(resultado, language=linguagem_destino.lower())
        except Exception as e:
            st.error(f"Erro ao converter código: {e}") 
