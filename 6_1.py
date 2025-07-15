import streamlit as st
import openai
import os
import tempfile
from typing import List, Dict, Optional
import json
import time

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.schema import Document
from langchain.prompts import PromptTemplate

st.set_page_config(
    page_title="Chatbot de Documentos da Empresa",
    layout="wide"
)

if 'vectorstore' not in st.session_state:
    st.session_state.vectorstore = None
if 'documents_loaded' not in st.session_state:
    st.session_state.documents_loaded = False
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

class CompanyDocumentChatbot:
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        openai.api_key = api_key
        self.embeddings = OpenAIEmbeddings(openai_api_key=api_key)
        self.llm = ChatOpenAI(
            openai_api_key=api_key,
            model_name="gpt-3.5-turbo",
            temperature=0.1
        )
        self.vectorstore = None
        self.qa_chain = None
    
    def load_pdf_documents(self, pdf_files: List) -> bool:
        try:
            documents = []
            
            for pdf_file in pdf_files:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    tmp_file.write(pdf_file.read())
                    tmp_file.flush()
                    
                    loader = PyPDFLoader(tmp_file.name)
                    pdf_documents = loader.load()
                    documents.extend(pdf_documents)
                    
                    os.unlink(tmp_file.name)
            
            if not documents:
                st.error("Nenhum documento foi carregado")
                return False
            
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
            )
            
            chunks = text_splitter.split_documents(documents)
            
            self.vectorstore = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory="./chroma_db"
            )
            
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.vectorstore.as_retriever(
                    search_type="similarity",
                    search_kwargs={"k": 5}
                ),
                return_source_documents=True
            )
            
            st.success(f"{len(documents)} documentos carregados com sucesso!")
            return True
            
        except Exception as e:
            st.error(f"Erro ao carregar documentos: {e}")
            return False
    
    def answer_question(self, question: str) -> Dict:
        if not self.qa_chain:
            return {
                "answer": "Nenhum documento foi carregado. Por favor, carregue documentos primeiro.",
                "sources": [],
                "confidence": 0
            }
        
        try:
            result = self.qa_chain({"query": question})
            
            answer = result["result"]
            source_documents = result["source_documents"]
            
            sources = []
            for doc in source_documents:
                source_info = {
                    "content": doc.page_content[:200] + "...",
                    "metadata": doc.metadata,
                    "page": doc.metadata.get("page", "N/A")
                }
                sources.append(source_info)
            
            return {
                "answer": answer,
                "sources": sources,
                "confidence": self._calculate_confidence(answer, sources)
            }
            
        except Exception as e:
            return {
                "answer": f"Erro ao processar pergunta: {e}",
                "sources": [],
                "confidence": 0
            }
    
    def _calculate_confidence(self, answer: str, sources: List) -> float:
        if not answer or answer.startswith("Erro"):
            return 0.0
        
        confidence = 0.5
        
        if len(sources) > 0:
            confidence += min(len(sources) * 0.1, 0.3)
        
        if len(answer) > 100:
            confidence += 0.1
        
        if any("página" in answer.lower() or "documento" in answer.lower() for source in sources):
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def get_document_summary(self) -> Dict:
        if not self.vectorstore:
            return {"total_documents": 0, "topics": []}
        
        try:
            docs = self.vectorstore.similarity_search("", k=20)
            
            topics = []
            for doc in docs:
                content = doc.page_content.lower()
                if "política" in content or "policy" in content:
                    topics.append("Políticas Internas")
                elif "projeto" in content or "project" in content:
                    topics.append("Projetos")
                elif "relatório" in content or "report" in content:
                    topics.append("Relatórios")
                elif "procedimento" in content or "procedure" in content:
                    topics.append("Procedimentos")
                elif "manual" in content:
                    topics.append("Manuais")
            
            unique_topics = list(set(topics))
            
            return {
                "total_documents": len(docs),
                "topics": unique_topics,
                "sample_content": docs[0].page_content[:200] + "..." if docs else ""
            }
            
        except Exception as e:
            return {"total_documents": 0, "topics": [], "error": str(e)}

def display_chat_interface():
    st.subheader("Chat com Documentos da Empresa")
    
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(f"**Você:** {message['content']}")
            else:
                st.markdown(f"**Assistente:** {message['content']}")
                
                if "sources" in message and message["sources"]:
                    with st.expander("Ver fontes"):
                        for i, source in enumerate(message["sources"][:3]):
                            st.markdown(f"**Fonte {i+1}:**")
                            st.markdown(f"Página: {source['page']}")
                            st.markdown(f"Conteúdo: {source['content']}")
                            st.markdown("---")
        
        user_question = st.text_input(
            "Digite sua pergunta sobre os documentos da empresa:",
            placeholder="Ex: Qual é a política de férias da empresa?",
            key="user_input"
        )
        
        col1, col2 = st.columns([1, 4])
        
        with col1:
            if st.button("Perguntar", type="primary"):
                if user_question and st.session_state.documents_loaded:
                    st.session_state.chat_history.append({
                        "role": "user",
                        "content": user_question,
                        "timestamp": time.time()
                    })
                    
                    with st.spinner("Buscando informações..."):
                        chatbot = st.session_state.chatbot
                        result = chatbot.answer_question(user_question)
                    
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": result["answer"],
                        "sources": result["sources"],
                        "confidence": result["confidence"],
                        "timestamp": time.time()
                    })
                    
                    st.rerun()
                elif not st.session_state.documents_loaded:
                    st.error("Carregue documentos primeiro!")
                else:
                    st.error("Digite uma pergunta!")
        
        with col2:
            if st.button("Limpar Chat"):
                st.session_state.chat_history = []
                st.rerun()

def display_document_upload():
    st.subheader("Carregar Documentos da Empresa")
    
    uploaded_files = st.file_uploader(
        "Selecione os documentos PDF da empresa:",
        type=['pdf'],
        accept_multiple_files=True,
        help="Carregue políticas internas, relatórios de projetos, manuais, etc."
    )
    
    if uploaded_files:
        st.info(f"{len(uploaded_files)} arquivo(s) selecionado(s)")
        
        file_names = [f.name for f in uploaded_files]
        st.write("**Arquivos selecionados:**")
        for name in file_names:
            st.write(f"• {name}")
        
        if st.button("Processar Documentos", type="primary"):
            with st.spinner("Processando documentos..."):
                api_key = st.session_state.get('openai_api_key')
                if not api_key:
                    st.error("Configure a chave da API OpenAI primeiro!")
                    return
                
                chatbot = CompanyDocumentChatbot(api_key)
                success = chatbot.load_pdf_documents(uploaded_files)
                
                if success:
                    st.session_state.chatbot = chatbot
                    st.session_state.documents_loaded = True
                    
                    summary = chatbot.get_document_summary()
                    st.success("Documentos processados com sucesso!")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Documentos", summary["total_documents"])
                    with col2:
                        st.metric("Tópicos", len(summary["topics"]))
                    
                    if summary["topics"]:
                        st.write("**Tópicos identificados:**")
                        for topic in summary["topics"]:
                            st.write(f"• {topic}")

def display_settings():
    st.sidebar.subheader("Configurações")
    
    api_key = st.sidebar.text_input(
        "Chave da API OpenAI",
        type="password",
        help="Insira sua chave da API OpenAI"
    )
    
    if api_key:
        st.session_state.openai_api_key = api_key
    
    st.sidebar.markdown("### Configurações do Modelo")
    
    model_name = st.sidebar.selectbox(
        "Modelo",
        ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview"],
        index=0
    )
    
    temperature = st.sidebar.slider(
        "Temperatura",
        min_value=0.0,
        max_value=1.0,
        value=0.1,
        step=0.1
    )
    
    st.sidebar.markdown("### Configurações de Busca")
    
    search_k = st.sidebar.number_input(
        "Número de documentos para buscar",
        min_value=1,
        max_value=10,
        value=5
    )
    
    chunk_size = st.sidebar.number_input(
        "Tamanho do chunk",
        min_value=500,
        max_value=2000,
        value=1000,
        step=100
    )
    
    return {
        "api_key": api_key,
        "model_name": model_name,
        "temperature": temperature,
        "search_k": search_k,
        "chunk_size": chunk_size
    }

def display_analytics():
    if not st.session_state.chat_history:
        return
    
    st.subheader("Análise de Uso")
    
    total_questions = len([m for m in st.session_state.chat_history if m["role"] == "user"])
    total_answers = len([m for m in st.session_state.chat_history if m["role"] == "assistant"])
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Perguntas", total_questions)
    
    with col2:
        st.metric("Respostas", total_answers)
    
    with col3:
        avg_confidence = 0
        if total_answers > 0:
            confidences = [m.get("confidence", 0) for m in st.session_state.chat_history if m["role"] == "assistant"]
            avg_confidence = sum(confidences) / len(confidences)
        st.metric("Confiança Média", f"{avg_confidence:.1%}")
    
    if st.session_state.chat_history:
        st.write("**Perguntas recentes:**")
        recent_questions = [m["content"] for m in st.session_state.chat_history[-5:] if m["role"] == "user"]
        for i, question in enumerate(recent_questions, 1):
            st.write(f"{i}. {question}")

def main():
    st.title("Chatbot de Documentos da Empresa")
    st.markdown("Faça perguntas sobre políticas internas, relatórios de projetos e outros documentos da empresa.")
    
    settings = display_settings()
    
    tab1, tab2, tab3 = st.tabs(["Upload", "Chat", "Análise"])
    
    with tab1:
        display_document_upload()
    
    with tab2:
        if st.session_state.documents_loaded:
            display_chat_interface()
        else:
            st.info("Carregue documentos na aba 'Upload' para começar a fazer perguntas.")
    
    with tab3:
        display_analytics()
    
    with st.sidebar:
        st.markdown("""
        Este chatbot permite fazer perguntas sobre documentos da empresa usando IA.
        
        **Funcionalidades:**
        - Upload de PDFs
        - Busca inteligente
        - Chat interativo
        - Citação de fontes
        """)

if __name__ == "__main__":
    main() 