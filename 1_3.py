import openai

client = openai.OpenAI(api_key="")

def classify_email(email_text):
    system_prompt = """
Persona: Você é um classificador de e-mails especializado em suporte ao cliente.
Task: Classifique o conteúdo de um e-mail de suporte como uma das seguintes categorias:
- "Technical Question"
- "Billing Problem"
- "Product Feedback"

Guidelines:
- Analise cuidadosamente o conteúdo do e-mail.
- Se o e-mail estiver pedindo ajuda sobre uma funcionalidade, classifique como "Technical Question".
- Se estiver questionando faturas, cobranças ou preços, classifique como "Billing Problem".
- Se for uma sugestão, crítica ou elogio ao produto, classifique como "Product Feedback".
- Escolha **apenas uma** das três categorias.
Output format:
- Apenas a categoria exata, sem explicações.
"""

    user_prompt = f"""
E-mail:
\"\"\"
{email_text}
\"\"\"

Classifique este e-mail:
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0,
        max_tokens=10
    )

    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    email = input("Cole o conteúdo do e-mail:\n")
    category = classify_email(email)
    print(f"\nCategoria identificada: {category}")
