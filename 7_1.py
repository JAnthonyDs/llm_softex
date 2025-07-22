import os
import subprocess
import time

REQ_FILE = 'requirements.txt'
MAIN_FILE = 'company_chatbot.py'
PORTA_PADRAO = 8501

def gerar_dockerfile():
    conteudo = f'''FROM python:3.10-slim
WORKDIR /app
COPY {REQ_FILE} ./
RUN pip install --no-cache-dir -r {REQ_FILE}
COPY . .
EXPOSE {PORTA_PADRAO}
CMD ["streamlit", "run", "{MAIN_FILE}", "--server.port={PORTA_PADRAO}", "--server.address=0.0.0.0"]
'''
    with open('Dockerfile', 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print('Dockerfile gerado com sucesso.')

def gerar_docker_compose():
    conteudo = f'''version: '3.8'
services:
  chatbot:
    build: .
    ports:
      - "{PORTA_PADRAO}:{PORTA_PADRAO}"
    volumes:
      - .:/app
    environment:
      - OPENAI_API_KEY=\"SUA_CHAVE_AQUI\"
'''
    with open('docker-compose.yml', 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print('docker-compose.yml gerado com sucesso.')

def executar_docker_compose():
    print('Construindo a imagem Docker...')
    subprocess.run(['docker-compose', 'build'], check=True)
    print('Subindo o serviço com docker-compose...')
    subprocess.Popen(['docker-compose', 'up'])
    print('Aguardando o serviço iniciar...')
    time.sleep(15)

def verificar_servico():
    import requests
    try:
        resp = requests.get(f'http://localhost:{PORTA_PADRAO}')
        if resp.status_code == 200:
            print('Serviço Streamlit rodando com sucesso!')
        else:
            print(f'Serviço respondeu com status {resp.status_code}. Verifique os logs.')
    except Exception as e:
        print(f'Não foi possível acessar o serviço: {e}')

if __name__ == '__main__':
    print('AGENTE DOCKER MULTI-ETAPAS')
    gerar_dockerfile()
    gerar_docker_compose()
    executar_docker_compose()
    verificar_servico()
    print('Processo finalizado.') 