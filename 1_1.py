import openai

openai.api_key = ""


sample_transcription = """
    João: Bom dia pessoal, vamos começar nossa reunião de planejamento.
    
    Maria: Oi João, sobre o projeto X, eu preciso finalizar o relatório até sexta-feira.
    
    Pedro: Perfeito Maria. Eu vou revisar os dados do último trimestre e te envio até quarta.
    
    João: Ótimo. Pedro, você também pode verificar se os números do departamento de vendas estão corretos?
    
    Pedro: Sim, vou fazer isso hoje mesmo.
    
    Ana: Gente, eu preciso agendar uma reunião com o cliente ABC para a próxima semana. João, você pode participar?
    
    João: Claro Ana, me avisa o horário. Ah, e não esqueça de preparar a apresentação.
    
    Ana: Pode deixar, vou preparar até quinta.
    
    Maria: Uma coisa importante - precisamos definir o orçamento do próximo projeto. Isso é urgente.
    
    João: Verdade Maria, vou conversar com a diretoria amanhã sobre isso"""	



system_prompt = """
Persona: Você é um assistente de produtividade empresarial altamente treinado.
Task: Sua tarefa é analisar a transcrição de uma reunião e extrair itens de ação específicos (action items).
Guidelines:
- Identifique claramente quem é responsável por cada ação.
- Use verbos no infinitivo e seja claro e conciso.
- Ignore partes irrelevantes ou meramente informativas.
- Cada item deve estar em uma nova linha.
Output format:
- Uma lista simples de itens de ação, cada um com um sujeito (quem), verbo (o que fazer) e, se possível, prazo (quando).
"""

user_prompt = f"""
Transcrição:
{sample_transcription}

Liste os action items:
"""

client = openai.OpenAI(api_key=openai.api_key)

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ],
    temperature=0.2,
    max_tokens=300
)

print(response.choices[0].message.content)
