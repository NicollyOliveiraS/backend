# app.py
import os
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from google import genai
from google.genai import types
from dotenv import load_dotenv
from datetime import datetime

# Importando o schema e instrução
from config import VEST_SCHEMA, SYSTEM_INSTRUCTION

# Carrega as variáveis de ambiente
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Verifica se a chave da API existe
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY não encontrada no arquivo .env")

# Inicializa o cliente Gemini
client = genai.Client(api_key=GEMINI_API_KEY)

# Inicializa o Flask
app = Flask(__name__)
CORS(app)


def generate_rotina(nome_vestibular, data_vestibular, tempo_disponivel, materias):
    """Gera um cronograma de estudos baseado nas informações do usuário"""
    
    # Formata as matérias em uma lista legível
    lista_materias = ", ".join(materias)
    
    # Calcula dias restantes (opcional)
    dias_restantes = "não informado"
    if data_vestibular and data_vestibular != "não informada":
        try:
            data_vestibular_obj = datetime.strptime(data_vestibular, "%d/%m/%Y")
            dias_restantes = (data_vestibular_obj - datetime.now()).days
            if dias_restantes > 0:
                dias_restantes = f"{dias_restantes} dias"
            else:
                dias_restantes = "data já passou ou inválida"
        except:
            dias_restantes = "data inválida"
    
    # Cria o prompt detalhado para o Gemini
    conteudo_prompt = f"""
    Crie um plano de estudos PERSONALIZADO com base nas seguintes informações do aluno:
    
    INFORMAÇÕES FORNECIDAS:
    - Vestibular alvo: {nome_vestibular}
    - Data do vestibular: {data_vestibular} (faltam {dias_restantes})
    - Tempo disponível para estudar por dia: {tempo_disponivel}
    - Matérias que precisa estudar: {lista_materias}
    
    INSTRUÇÕES IMPORTANTES:
    1. Considere o tempo disponível ({tempo_disponivel}) para distribuir as matérias
    2. Se faltar pouco tempo ({dias_restantes}), foque nos tópicos mais importantes
    3. Se faltar muito tempo, crie um cronograma mais extenso com revisões
    4. Distribua as matérias de forma equilibrada pelos dias da semana
    5. Para {nome_vestibular}, priorize matérias com maior peso neste vestibular
    6. Inclua tempo para revisão e resolução de exercícios
    
    Crie um plano REALISTA e MOTIVADOR.
    """
    
    # Faz a chamada para o Gemini
    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=conteudo_prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                response_mime_type="application/json",
                response_schema=VEST_SCHEMA,
                temperature=0.7,
                max_output_tokens=4096,
            )
        )
        
        # Verifica se a resposta foi gerada corretamente
        if not response or not response.text:
            raise ValueError("Resposta vazia do Gemini")
            
        return response.text
        
    except Exception as e:
        raise Exception(f"Erro na chamada do Gemini: {str(e)}")


@app.route("/")
def root():
    """Endpoint de verificação da API"""
    return jsonify({
        "status": "success",
        "message": "API Gerador de Rotinas de Estudo funcionando!",
        "version": "3.0",
        "endpoints": {
            "POST /vestrotina": "Envie informações do vestibular, tempo disponível e matérias"
        },
        "exemplo_request": {
            "vestibular": "ENEM",
            "data_vestibular": "10/11/2024", 
            "tempo_disponivel": "2 horas por dia de semana e 3 horas fins de semana",
            "materias": ["Matemática", "Português", "Redação", "Física", "Química"]
        }
    }), 200


@app.route("/vestrotina", methods=["POST"])
def vestrotina():
    """Endpoint principal para gerar cronograma de estudos"""
    
    # Validação 1: JSON foi enviado?
    if not request.is_json:
        return jsonify({
            "status": "error",
            "message": "Requisição deve ser JSON. Use Content-Type: application/json",
            "exemplo": {
                "vestibular": "ENEM",
                "data_vestibular": "10/11/2024",
                "tempo_disponivel": "3 horas por dia de semana e 6 dias por semana",
                "materias": ["Matemática", "Português", "Redação"]
            }
        }), 400
    
    data = request.get_json()
    
    # Validação 2: Campos obrigatórios existem?
    if "vestibular" not in data:
        return jsonify({
            "status": "error",
            "message": "Campo obrigatório 'vestibular' não encontrado.",
            "campos_aceitos": ["vestibular", "data_vestibular", "tempo_disponivel", "materias"]
        }), 400
    
    if "materias" not in data:
        return jsonify({
            "status": "error",
            "message": "Campo obrigatório 'materias' não encontrado.",
            "campos_aceitos": ["vestibular", "data_vestibular", "tempo_disponivel", "materias"]
        }), 400
    
    # Extrai os dados com valores padrão
    nome_vestibular = data.get("vestibular")
    data_vestibular = data.get("data_vestibular", "não informada")
    tempo_disponivel = data.get("tempo_disponivel", "não informado")
    materias = data.get("materias", [])
    
    # Validação 3: Matérias é uma lista de strings?
    if not isinstance(materias, list):
        return jsonify({
            "status": "error",
            "message": "O campo 'materias' deve ser uma lista de matérias (strings).",
            "exemplo": ["Matemática", "Português", "Biologia"]
        }), 400
    
    if len(materias) == 0:
        return jsonify({
            "status": "error",
            "message": "A lista de matérias não pode estar vazia. Envie pelo menos uma matéria."
        }), 400
    
    for item in materias:
        if not isinstance(item, str):
            return jsonify({
                "status": "error",
                "message": "Todos os itens da lista 'materias' devem ser strings (textos)."
            }), 400
    
    try:
        # Gera a rotina usando o Gemini
        rotina_json_string = generate_rotina(
            nome_vestibular, 
            data_vestibular, 
            tempo_disponivel, 
            materias
        )
        
        # Converte a resposta JSON string para dicionário Python
        rotina_estruturada = json.loads(rotina_json_string)
        
        # Retorna resposta de sucesso
        return jsonify({
            "status": "success",
            "message": "Cronograma gerado com sucesso!",
            "informacoes_recebidas": {
                "vestibular": nome_vestibular,
                "data_vestibular": data_vestibular,
                "tempo_disponivel": tempo_disponivel,
                "materias": materias
            },
            "plano_estudos": rotina_estruturada
        }), 200
        
    except json.JSONDecodeError as e:
        return jsonify({
            "status": "error",
            "message": "Erro ao processar resposta do Gemini: Resposta não é JSON válido.",
            "detalhes": str(e)
        }), 500
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Erro ao gerar o cronograma: {str(e)}",
            "dica": "Verifique sua chave API e os dados enviados"
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Tratamento de erro 404"""
    return jsonify({
        "status": "error",
        "message": "Endpoint não encontrado. Use POST /vestrotina"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Tratamento de erro 500"""
    return jsonify({
        "status": "error",
        "message": "Erro interno do servidor. Tente novamente mais tarde."
    }), 500


# Executa o servidor
if __name__ == "__main__":
    print("=" * 50)
    print(" Servidor de Cronograma de Estudos v3.0")
    print("=" * 50)
    print(" Campos esperados:")
    print("   - vestibular (obrigatório): Nome do vestibular")
    print("   - materias (obrigatório): Lista de matérias")
    print("   - data_vestibular (opcional): Data do vestibular")
    print("   - tempo_disponivel (opcional): Tempo disponível por dia")
    print("=" * 50)
    print(" Endpoint principal: http://localhost:5000/vestrotina")
    print("=" * 50)
    
    app.run(debug=True, host="0.0.0.0", port=5000)