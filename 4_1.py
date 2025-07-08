import streamlit as st
import openai

st.set_page_config(page_title="Refatorador de Código com IA", page_icon="🤖")

st.title("Refatorador de Código com IA")
st.write("Cole seu código abaixo. A IA irá sugerir uma versão refatorada e explicar as melhorias.")

openai_api_key = st.text_input("", type="password")

code_input = st.text_area("Cole seu código aqui:", height=200)
language = st.selectbox("Linguagem do código", ["Python", "JavaScript", "Java", "C#", "C++", "Outros"])

if st.button("Refatorar e Explicar"):
    if not openai_api_key:
        st.warning("Por favor, insira sua chave da API OpenAI.")
    elif not code_input.strip():
        st.warning("Por favor, cole um trecho de código.")
    else:
        with st.spinner("Analisando e refatorando..."):
            openai.api_key = openai_api_key
            system_prompt = f"""
Você é um engenheiro de software sênior. Sua tarefa é analisar um trecho de código em {language}, sugerir uma versão refatorada (mais limpa, eficiente ou legível) e explicar detalhadamente as melhorias feitas.
Output format:
--- Código Refatorado ---
<novo código>
--- Explicação ---
<explicação das melhorias>
"""
            user_prompt = f"""
Código original:
{code_input}

Refatore e explique:
"""
            try:
                response = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.2,
                    max_tokens=1200
                )
                result = response.choices[0].message.content.strip()
                if '--- Código Refatorado ---' in result and '--- Explicação ---' in result:
                    refatorado, explicacao = result.split('--- Explicação ---', 1)
                    refatorado = refatorado.replace('--- Código Refatorado ---', '').strip()
                    explicacao = explicacao.strip()
                    st.subheader("Código Refatorado")
                    st.code(refatorado, language=language.lower())
                    st.subheader("Explicação das Melhorias")
                    st.write(explicacao)
                else:
                    st.write(result)
            except Exception as e:
                st.error(f"Erro ao processar: {e}") 


# Para rodar o projeto streamlit run webapp_refatoracao.py