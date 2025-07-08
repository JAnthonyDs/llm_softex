import streamlit as st
import openai
from streamlit_audio_recorder import audio_recorder
import tempfile

st.set_page_config(page_title="Transcrição de Áudio com IA")

st.title("Transcrição de Áudio com IA")
st.write("Faça upload ou grave uma mensagem de voz. O app irá transcrever automaticamente usando IA.")

openai_api_key = st.text_input("", type="password")

st.markdown("**Opção 1: Upload de arquivo de áudio**")
audio_file = st.file_uploader("Faça upload de um arquivo de áudio (WAV, MP3, M4A, etc.)", type=["wav", "mp3", "m4a"]) 

# st.markdown("**Opção 2: Grave sua mensagem de voz**")
# recorded_audio = audio_recorder(text="Clique para gravar", pause_threshold=2.0, sample_rate=16000)

def transcrever_audio(audio_bytes, api_key):
    openai.api_key = api_key
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
        tmpfile.write(audio_bytes)
        tmpfile.flush()
        tmpfile.seek(0)
        audio = open(tmpfile.name, "rb")
        transcript = openai.audio.transcriptions.create(
            model="whisper-1",
            file=audio,
            response_format="text"
        )
        return transcript

if st.button("Transcrever"):
    if not openai_api_key:
        st.warning("Por favor, insira sua chave da API OpenAI.")
    # elif not audio_file and not recorded_audio:
    #     st.warning("Por favor, faça upload ou grave um áudio.")
    else:
        with st.spinner("Transcrevendo..."):
            try:
                if audio_file:
                    audio_bytes = audio_file.read()
                # else:
                #     audio_bytes = recorded_audio
                resultado = transcrever_audio(audio_bytes, openai_api_key)
                st.subheader("Transcrição")
                st.write(resultado)
            except Exception as e:
                st.error(f"Erro ao transcrever: {e}") 


# Para rodar o projeto com streamlit: streamlit run webapp_transcricao.py