import streamlit as st
import openai
import json
import time
from typing import Dict, List, Tuple

st.set_page_config(page_title="Detector de Alucinações em LLMs", layout="wide")

st.title("Detector de Alucinações em LLMs")
st.markdown("Sistema multi-etapas para verificar se um modelo de linguagem está alucinando")

openai_api_key = st.sidebar.text_input("", type="password")
model_name = st.sidebar.selectbox(
    "Modelo a ser testado",
    ["gpt-4o-mini"],
    index=0
)

st.sidebar.markdown("### Configurações do Teste")
temperature = st.sidebar.slider("Temperatura", 0.0, 2.0, 0.7, 0.1)
max_tokens = st.sidebar.number_input("Máximo de tokens", 100, 4000, 1000)

def call_openai_api(messages: List[Dict], model: str, temperature: float, max_tokens: int) -> str:
    """Faz uma chamada para a API OpenAI"""
    try:
        openai.api_key = openai_api_key
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Erro na API: {e}")
        return None

def step_1_ask_question(question: str) -> str:
    """Etapa 1: Fazer a pergunta inicial ao LLM"""
    st.subheader("Etapa 1: Pergunta Inicial")
    
    messages = [
        {"role": "system", "content": "Você é um assistente útil. Responda à pergunta de forma clara e detalhada."},
        {"role": "user", "content": question}
    ]
    
    with st.spinner("Obtendo resposta inicial..."):
        response = call_openai_api(messages, model_name, temperature, max_tokens)
    
    if response:
        st.success("Resposta obtida")
        st.text_area("Resposta do LLM:", response, height=200)
        return response
    return None

def step_2_ask_for_sources(question: str, initial_response: str) -> str:
    """Etapa 2: Pedir fontes ao LLM"""
    st.subheader("Etapa 2: Solicitação de Fontes")
    
    source_request = f"""
    Baseado na sua resposta anterior, por favor forneça as fontes específicas que você usou para responder à pergunta: "{question}"
    
    Sua resposta foi: {initial_response}
    
    Por favor, liste:
    1. Fontes específicas (livros, artigos, sites, etc.)
    2. Autores ou organizações
    3. Datas de publicação (se aplicável)
    4. URLs ou referências específicas
    
    Se você não tem fontes específicas, seja honesto e diga isso claramente.
    """
    
    messages = [
        {"role": "system", "content": "Você é um assistente honesto. Sempre seja transparente sobre suas fontes."},
        {"role": "user", "content": source_request}
    ]
    
    with st.spinner("Solicitando fontes..."):
        sources_response = call_openai_api(messages, model_name, temperature, max_tokens)
    
    if sources_response:
        st.success("Fontes solicitadas")
        st.text_area("Fontes citadas:", sources_response, height=200)
        return sources_response
    return None

def step_3_verify_against_sources(question: str, initial_response: str, sources: str) -> Dict:
    """Etapa 3: Verificar a resposta contra as fontes"""
    st.subheader("🔍 Etapa 3: Verificação contra Fontes")
    
    verification_prompt = f"""
    Você é um verificador de fatos. Analise a seguinte situação:
    
    Pergunta original: "{question}"
    Resposta do LLM: {initial_response}
    Fontes citadas: {sources}
    
    Por favor, avalie:
    1. A resposta está alinhada com as fontes citadas?
    2. As fontes são confiáveis e específicas?
    3. Há informações na resposta que não são suportadas pelas fontes?
    4. O LLM foi honesto sobre suas limitações?
    
    Responda em formato JSON com os seguintes campos:
    {{
        "alinhamento_com_fontes": "alto/médio/baixo",
        "confiabilidade_fontes": "alta/média/baixa",
        "informacoes_nao_suportadas": "sim/não",
        "honestidade_sobre_limitacoes": "sim/não",
        "probabilidade_alucinacao": "alta/média/baixa",
        "explicacao": "explicação detalhada da análise"
    }}
    """
    
    messages = [
        {"role": "system", "content": "Você é um verificador de fatos especializado em detectar alucinações em LLMs."},
        {"role": "user", "content": verification_prompt}
    ]
    
    with st.spinner("Verificando contra fontes..."):
        verification_response = call_openai_api(messages, model_name, 0.1, max_tokens)
    
    if verification_response:
        try:
            if verification_response.strip().startswith('{'):
                result = json.loads(verification_response)
            else:
                result = {
                    "alinhamento_com_fontes": "indeterminado",
                    "confiabilidade_fontes": "indeterminado", 
                    "informacoes_nao_suportadas": "indeterminado",
                    "honestidade_sobre_limitacoes": "indeterminado",
                    "probabilidade_alucinacao": "indeterminado",
                    "explicacao": verification_response
                }
            
            st.success("✅ Verificação concluída")
            return result
        except json.JSONDecodeError:
            st.warning("⚠️ Resposta não está em formato JSON válido")
            return {"explicacao": verification_response}
    
    return None

def display_results(verification_result: Dict):
    """Exibe os resultados da verificação"""
    st.subheader("Resultados da Análise")
    
    if not verification_result:
        st.error("Não foi possível obter resultados da verificação")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Métricas de Verificação")
        
        hallucination_color = {
            "alta": "alta",
            "média": "média", 
            "baixa": "baixa",
            "indeterminado": "indeterminado"
        }
        
        prob = verification_result.get("probabilidade_alucinacao", "indeterminado")
        st.metric(
            "Probabilidade de Alucinação",
            f"{hallucination_color.get(prob, '⚪')} {prob.title()}"
        )
        
        st.metric(
            "Alinhamento com Fontes",
            verification_result.get("alinhamento_com_fontes", "indeterminado").title()
        )
        
        st.metric(
            "Confiabilidade das Fontes",
            verification_result.get("confiabilidade_fontes", "indeterminado").title()
        )
    
    with col2:
        st.markdown("### Indicadores")
        
        st.checkbox(
            "Informações não suportadas pelas fontes",
            value=verification_result.get("informacoes_nao_suportadas", "indeterminado") == "sim",
            disabled=True
        )
        
        st.checkbox(
            "Honestidade sobre limitações",
            value=verification_result.get("honestidade_sobre_limitacoes", "indeterminado") == "sim",
            disabled=True
        )
    
    st.markdown("###Explicação Detalhada")
    st.write(verification_result.get("explicacao", "Nenhuma explicação disponível"))

def main():
    """Função principal"""
    
    question = st.text_area(
        "Digite a pergunta que você quer testar:",
        placeholder="Ex: Qual é a capital do Brasil?",
        height=100
    )
    
    if st.button("🚀 Iniciar Teste de Alucinação", type="primary"):
        
        with st.container():
            initial_response = step_1_ask_question(question)
            if not initial_response:
                return
            
            st.markdown("---")
            
            sources = step_2_ask_for_sources(question, initial_response)
            if not sources:
                return
            
            st.markdown("---")
            
            verification_result = step_3_verify_against_sources(question, initial_response, sources)
            
            st.markdown("---")
            
            display_results(verification_result)
    
    
if __name__ == "__main__":
    main() 