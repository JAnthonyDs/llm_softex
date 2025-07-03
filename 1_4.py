import openai

client = openai.OpenAI(api_key="")

def generate_test_cases(functional_spec: str):
    system_prompt = """
Persona: Você é um engenheiro de testes especialista em qualidade de software.
Task: Gerar casos de teste com base em especificações funcionais fornecidas.
Guidelines:
- Use uma estrutura clara com: Título, Descrição, Pré-condições, Entradas, Etapas, Resultado esperado.
- Crie múltiplos casos de teste, incluindo positivos, negativos e de borda.
- Seja objetivo, focando no comportamento funcional do sistema.
Output format:
[
  {
    "title": "...",
    "description": "...",
    "preconditions": "...",
    "inputs": "...",
    "steps": "...",
    "expected_result": "..."
  },
  ...
]
"""

    user_prompt = f"""
Especificação funcional:
\"\"\"
{functional_spec}
\"\"\"

Gere os casos de teste correspondentes:
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2,
        max_tokens=1000
    )

    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    spec = input("Digite a especificação funcional:\n")
    test_cases = generate_test_cases(spec)
    print("\nCasos de teste gerados:\n")
    print(test_cases)
