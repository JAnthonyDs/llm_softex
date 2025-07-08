import openai

client = openai.OpenAI(api_key="")

ticket_example = {
    'username': 'JoaoSilva123', 
    'OS': 'linux', 
    'Software version': '22.04', 
    'description': 'Problemas com o banco de dados PostgreSQL. O sistema não consegue conectar e está retornando erro de timeout. Isso está afetando a produção.'
}

def analise_ticket(ticket):
    system_prompt = """
Persona: Você é um analista de suporte técnico sênior especializado em classificação e priorização de tickets.
Task: Analisar tickets de suporte técnico e extrair entidades-chave, classificando por prioridade e categoria.
Guidelines:
- Extraia todas as entidades mencionadas (username, OS, software version, description)
- Classifique a prioridade baseada em impacto e urgência: HIGH=Problemas críticos, MEDIUM=Problemas funcionais, LOW=Dúvidas, melhorias, feature requests, documentação
  
- Categorize o ticket baseado no conteúdo:
  * BUG: Problemas, erros, falhas no sistema
  * QUESTION: Dúvidas, consultas, esclarecimentos
  * FEATURE_REQUEST: Solicitações de novas funcionalidades
  * PERFORMANCE: Problemas de velocidade, otimização
  * SECURITY: Vulnerabilidades, problemas de segurança
  * INFRASTRUCTURE: Problemas de rede, servidores, deploy
Output format:
**Entidades Extraídas:**
- username: <username>
- OS: <OS>
- Software version: <version>
- Tec: <tech_list>
- Erros: <error_list>

**Classificação:**
- Prioridade: <HIGH/MEDIUM/LOW>
- Categoria: <BUG/QUESTION/FEATURE_REQUEST/etc>
- Justificativa: <explicação da classificação>
"""

    user_prompt = f"""
Analise o seguinte ticket de suporte técnico:

Username: {ticket['username']}
Sistema Operacional: {ticket['OS']}
Versão: {ticket['Software version']}
Descrição: {ticket['description']}

Extraia as entidades e classifique o ticket:
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2,
        max_tokens=800
    )

    return response.choices[0].message.content.strip()

def main(): 
    
    resultado = analise_ticket(ticket_example)
    print(resultado)

if __name__ == '__main__':
    main()


