# config.py
VEST_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "nome_do_vestibular": {
            "type": "STRING", 
            "description": "Nome do vestibular (ex: ENEM, Fuvest, Unicamp)"
        },
        "data_do_vestibular": {
            "type": "STRING", 
            "description": "Data principal do vestibular (ex: 10/11/2024)"
        },
        "dias_de_estudo_por_semana": {
            "type": "STRING", 
            "description": "Quantos dias por semana a pessoa deve estudar"
        },
        "horas_por_dia": {
            "type": "STRING", 
            "description": "Quantas horas por dia de estudo recomendado"
        },
        "cronograma_semanal": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "dia_semana": {"type": "STRING"},
                    "materia": {"type": "STRING"},
                    "topicos": {
                        "type": "ARRAY", 
                        "items": {"type": "STRING"}
                    },
                    "tempo_estimado": {"type": "STRING"}
                },
                "required": ["dia_semana", "materia", "topicos", "tempo_estimado"]
            },
            "description": "Cronograma detalhado de estudos por dia"
        },
        "dicas_estudo": {
            "type": "ARRAY",
            "items": {"type": "STRING"},
            "description": "Dicas e estratégias para seguir o plano de estudos"
        }
    },
    "required": ["nome_do_vestibular", "data_do_vestibular", "dias_de_estudo_por_semana", 
                 "horas_por_dia", "cronograma_semanal", "dicas_estudo"]
}

SYSTEM_INSTRUCTION = """
Você é um assistente especializado em planejamento de estudos para vestibulares brasileiros.

Sua tarefa é criar um plano de estudos personalizado e realista baseado nos tópicos que o usuário precisa estudar.

Regras importantes:
1. Seja prático e realista com o tempo disponível
2. Distribua os tópicos uniformemente pelos dias da semana
3. Inclua revisões periódicas e descanso
4. Priorize matérias com maior peso no vestibular
5. Sugira técnicas de estudo ativo (exercícios, resumos, flashcards)

O plano deve ser motivador e executável.
"""