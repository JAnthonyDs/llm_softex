import os
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import html2text

import openai

client = openai.OpenAI(api_key="")

BASE_URL = "https://requests.readthedocs.io/en/latest/"
OUTPUT_DIR = "./docs_md"

#conversor 
html_converter = html2text.HTML2Text()
html_converter.ignore_links = False
html_converter.ignore_images = False
html_converter.bypass_tables = False
html_converter.body_width = 0

visited = set()

def save_markdown(markdown_text, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(markdown_text)

def clean_filename(url):
    parsed = urlparse(url)
    path = parsed.path.strip("/").replace("/", "_")
    if not path:
        path = "index"
    return f"{path}.md"

def is_valid_subpage(link, domain):
    parsed = urlparse(link)
    return (parsed.netloc == domain or parsed.netloc == '') and not link.endswith(('.pdf', '.jpg', '.png', '.zip'))

def scrape_page(url, domain):
    if url in visited:
        return

    visited.add(url)

    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
    except Exception as e:
        print(f"Erro ao acessar {url}: {e}")
        return

    main_content = soup.find("div", {"role": "main"}) #Converter para Markdown
    if not main_content:
        print(f"Conteúdo não encontrado em {url}")
        return

    markdown = html_converter.handle(str(main_content))
    filename = clean_filename(urljoin(BASE_URL, url))
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    save_markdown(markdown, filepath) #Salvar o conteúdo em mark

    summary = summarize_markdown(markdown)
    if summary:
        summary_path = filepath.replace(".md", ".summary.md")
        save_markdown(summary, summary_path) #Salvar o resumo da llm


    for a in soup.find_all("a", href=True):
        href = a['href']
        full_url = urljoin(url, href)
        if is_valid_subpage(full_url, urlparse(BASE_URL).netloc):
            scrape_page(full_url, domain)

def summarize_markdown(markdown_text):
    system_prompt = """
Persona: Você é um assistente técnico especializado em documentação de software.
Task: Resumir o conteúdo de uma página de documentação técnica.
Guidelines:
- Seja conciso e claro.
- Destaque os tópicos abordados e seu propósito.
- Evite copiar blocos de código ou listas longas.
Output format:
<Resumo em até 5 frases>
"""

    user_prompt = f"""
A seguir está o conteúdo em Markdown de uma página de documentação técnica:

\"\"\"
{markdown_text[:50]}
\"\"\"

Gere um resumo do conteúdo:
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=300
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Erro ao gerar resumo com LLM: {e}")
        return ""



def main():
    domain = urlparse(BASE_URL).netloc
    scrape_page(BASE_URL, domain)

if __name__ == "__main__":
    main()
