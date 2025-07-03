import openai

openai.api_key = ""

def generate_code(description):
    system_prompt = """
Persona: Você é um assistente de desenvolvimento especializado em Python moderno e limpo.
Task: Sua tarefa é gerar código Python com base na descrição de uma classe ou função.
Guidelines:
- Use boas práticas de codificação Python (tipagem, docstrings, nomes significativos).
- Mantenha o código limpo e pronto para uso em um projeto real.
- Se for uma classe, inclua o método __init__ com os atributos descritos.
- Se houver métodos mencionados, implemente-os com lógica básica ou docstrings explicativas.
- Se a descrição for vaga, assuma comportamentos padrão e documente bem.
Output format:
- Apenas o código Python, formatado corretamente. Não inclua explicações.
"""

    user_prompt = f"""
Descrição:
{description}

Gere o código Python correspondente:
"""

    client = openai.OpenAI(api_key=openai.api_key)
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,
        max_tokens=500
    )

    return response.choices[0].message.content

if __name__ == "__main__":
    desc = input("Descreva a classe ou função: ")
    code = generate_code(desc)
    print("\nCódigo gerado:\n")
    print(code)
