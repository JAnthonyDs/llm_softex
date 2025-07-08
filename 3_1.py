import openai
import re
from typing import List, Set

client = openai.OpenAI(api_key="")

sample_job_descriptions = [
    """
    Desenvolvedor Full Stack Python
    
    Estamos procurando um desenvolvedor experiente em Python, Django, React e PostgreSQL.
    Conhecimentos em Docker, AWS e Git são essenciais. Experiência com APIs REST e GraphQL.
    """,
    
    """
    Engenheiro de Dados
    
    Procuramos alguém com experiência em Python, Apache Spark, Hadoop, MongoDB e Redis.
    Conhecimentos em SQL, Pandas, NumPy e machine learning com scikit-learn.
    """,
    
    """
    Desenvolvedor Frontend
    
    Necessário conhecimento em JavaScript, TypeScript, React, Vue.js e Node.js.
    Experiência com CSS, Sass, Webpack e ferramentas de build. Conhecimento em Angular é um plus.
    """,
    
    """
    DevOps Engineer
    
    Experiência com Linux, Docker, Kubernetes, Jenkins, GitLab CI/CD.
    Conhecimentos em AWS, Azure, Terraform, Ansible e monitoramento com Prometheus/Grafana.
    """
]

def extract_technologies_with_ner(job_descriptions: List[str]) -> Set[str]:
    """
    Usa NER para extrair tecnologias das descrições de vagas
    """
    combined_descriptions = "\n\n".join(job_descriptions)
    
    system_prompt = """
Persona: Você é um especialista em análise de vagas de tecnologia com conhecimento profundo em programação, frameworks e ferramentas.
Task: Identificar todas as tecnologias mencionadas em descrições de vagas usando Named Entity Recognition (NER).
Guidelines:
- Identifique linguagens de programação (Python, JavaScript, Java, etc.)
- Detecte frameworks e bibliotecas (React, Django, Spring, etc.)
- Inclua bancos de dados (PostgreSQL, MongoDB, Redis, etc.)
- Considere ferramentas de desenvolvimento (Docker, Git, Jenkins, etc.)
- Identifique plataformas cloud (AWS, Azure, GCP, etc.)
- Retorne apenas nomes de tecnologias, sem descrições adicionais
Output format:
Uma lista simples de tecnologias únicas, uma por linha, sem numeração ou formatação especial.
"""

    user_prompt = f"""
Analise as seguintes descrições de vagas e extraia todas as tecnologias mencionadas:

\"\"\"
{combined_descriptions}
\"\"\"

Liste todas as tecnologias únicas identificadas:
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.1,
        max_tokens=1000
    )

    technologies_text = response.choices[0].message.content.strip()
    technologies = set()
    
    for line in technologies_text.split('\n'):
        tech = line.strip().strip('-').strip('*').strip()
        if tech and len(tech) > 1: 
            technologies.add(tech)
    
    return technologies

def categorize_technologies(technologies: Set[str]) -> dict:
    """
    Categoriza as tecnologias por tipo
    """
    categories = {
        "Linguagens de Programação": [],
        "Frameworks e Bibliotecas": [],
        "Bancos de Dados": [],
        "Ferramentas de Desenvolvimento": [],
        "Cloud e Infraestrutura": [],
        "Outras Tecnologias": []
    }
    
    tech_categories = {
        "Linguagens de Programação": [
            "python", "javascript", "typescript", "java", "c#", "c++", "go", "rust", 
            "php", "ruby", "swift", "kotlin", "scala", "r", "matlab"
        ],
        "Frameworks e Bibliotecas": [
            "react", "vue", "angular", "django", "flask", "spring", "express", 
            "node.js", "laravel", "rails", "asp.net", "fastapi", "scikit-learn",
            "pandas", "numpy", "tensorflow", "pytorch"
        ],
        "Bancos de Dados": [
            "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "cassandra",
            "sqlite", "oracle", "sql server", "dynamodb", "firebase"
        ],
        "Ferramentas de Desenvolvimento": [
            "docker", "kubernetes", "git", "jenkins", "gitlab", "github", "webpack",
            "npm", "yarn", "maven", "gradle", "terraform", "ansible"
        ],
        "Cloud e Infraestrutura": [
            "aws", "azure", "gcp", "heroku", "digitalocean", "prometheus", "grafana",
            "nginx", "apache", "linux", "ubuntu", "centos"
        ]
    }
    
    for tech in technologies:
        tech_lower = tech.lower()
        categorized = False
        
        for category, tech_list in tech_categories.items():
            if any(tech_name in tech_lower for tech_name in tech_list):
                categories[category].append(tech)
                categorized = True
                break
        
        if not categorized:
            categories["Outras Tecnologias"].append(tech)
    
    return categories

def main():
    
    technologies = extract_technologies_with_ner(sample_job_descriptions)
    
    print(f"Total de tecnologias únicas identificadas: {len(technologies)}")
    print("\nLista completa de tecnologias:")
    
    for tech in sorted(technologies):
        print(f"* {tech}")
    
    categories = categorize_technologies(technologies)
    
    print("\n Tecnologias por categoria:")
    
    for category, techs in categories.items():
        if techs:
            print(f"\n{category}:")
            for tech in sorted(techs):
                print(f"  • {tech}")

if __name__ == "__main__":
    main()
