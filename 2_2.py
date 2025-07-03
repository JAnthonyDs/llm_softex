import openai
import requests
import time

client = openai.OpenAI(api_key="")
STATUS_PAGE_API = "https://www.githubstatus.com/api/v2/incidents.json"  
CHECK_INTERVAL = 60 

seen_incident_ids = set() #Armazenar incidentes já processados

def fetch_incidents():
    response = requests.get(STATUS_PAGE_API)
    if response.status_code == 200:
        return response.json().get("incidents", [])
    else:
        print(f"Erro ao acessar API: {response.status_code}")
        return []

def summarize_incident_with_llm(incident):
    title = incident.get("name", "")
    body = incident.get("incident_updates", [{}])[0].get("body", "")
    
    system_prompt = """
Persona: Você é um analista de incidentes de TI que gera relatórios executivos.
Task: Resumir incidentes técnicos em linguagem clara e objetiva.
Guidelines:
- Seja direto e informativo.
- Destaque o impacto no usuário final.
- Sugira se ação é necessária ou não.
Output format:
**Incidente**: <Título>
**Resumo**: <Resumo em até 3 linhas>
**Status**: <impacto ou gravidade>
**Recomendação**: <ação sugerida>
"""

    user_prompt = f"""
Título: {title}
Detalhes técnicos:
\"\"\"
{body}
\"\"\"
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2,
        max_tokens=500
    )

    return response.choices[0].message.content.strip()

def monitor():
    while True:
        incidents = fetch_incidents()
        for incident in incidents:
            if incident["id"] not in seen_incident_ids:
                seen_incident_ids.add(incident["id"])
                print("incidente detectado")
                summary = summarize_incident_with_llm(incident)
                print(summary)
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    monitor()
