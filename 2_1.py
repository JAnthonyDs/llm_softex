import openai
import re

client = openai.OpenAI(api_key="")

def extract_errors_from_log(log_path):
    with open(log_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    error_lines = [line for line in lines if re.search(r"(ERROR|Exception|Traceback)", line)]
    return "\n".join(error_lines[-30:])  

def process_error_with_llm(error_text):
    system_prompt = """
Persona: Você é um engenheiro de software sênior especializado em análise de logs e resolução de bugs.
Task: Analisar logs de erro e explicar a causa provável, além de sugerir uma solução prática.
Guidelines:
- Explique o que o erro significa e por que ele provavelmente aconteceu.
- Sugira uma correção ou investigação útil.
Output format:
Explicação:
<Causa provável>

Solução sugerida:
<Como resolver ou investigar>
"""

    user_prompt = f"""
A seguir estão mensagens de erro extraídas de um log de aplicação:

\"\"\"
{error_text}
\"\"\"

Explique o problema e sugira uma solução:
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,
        max_tokens=800
    )

    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    log_file_path = "./app.log"  

    errors = extract_errors_from_log(log_file_path)
    if errors:
        explanation = process_error_with_llm(errors)
        print(explanation)
    else:
        print("Nenhum erro identificado no log.")
    