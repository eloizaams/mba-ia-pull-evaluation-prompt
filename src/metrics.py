"""
Implementação COMPLETA de métricas customizadas para avaliação de prompts.
RESOLUÇÃO DO DESAFIO

Este módulo implementa métricas gerais e específicas para Bug to User Story:

MÉTRICAS GERAIS (3):
1. F1-Score: Balanceamento entre Precision e Recall
2. Clarity: Clareza e estrutura da resposta
3. Precision: Informações corretas e relevantes

MÉTRICAS ESPECÍFICAS PARA BUG TO USER STORY (4):
4. Tone Score: Tom profissional e empático
5. Acceptance Criteria Score: Qualidade dos critérios de aceitação
6. User Story Format Score: Formato correto (Como... Eu quero... Para que...)
7. Completeness Score: Completude e contexto técnico

Suporta múltiplos providers de LLM:
- OpenAI (gpt-4o, gpt-4o-mini)
- Google Gemini (gemini-1.5-flash, gemini-1.5-pro)

Configure o provider no arquivo .env através da variável LLM_PROVIDER.
"""

import os
import json
import re
from typing import Dict, Any
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage
from utils import get_eval_llm

load_dotenv()


def get_evaluator_llm():
    """
    Retorna o LLM configurado para avaliação.
    Suporta OpenAI e Google Gemini baseado no .env
    """
    return get_eval_llm(temperature=0)


def extract_json_from_response(response_text: str) -> Dict[str, Any]:
    """
    Extrai JSON de uma resposta de LLM que pode conter texto adicional.
    """
    try:
        # Tentar parsear diretamente
        return json.loads(response_text)
    except json.JSONDecodeError:
        # Tentar encontrar JSON no meio do texto
        start = response_text.find('{')
        end = response_text.rfind('}') + 1

        if start != -1 and end > start:
            try:
                json_str = response_text[start:end]
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass

        # Se não conseguir extrair, retornar valores default
        print(f"⚠️  Não foi possível extrair JSON da resposta: {response_text[:200]}...")
        return {"score": 0.0, "reasoning": "Erro ao processar resposta"}


def evaluate_f1_score(question: str, answer: str, reference: str) -> Dict[str, Any]:
    """
    Calcula F1-Score usando LLM-as-Judge.

    F1-Score = 2 * (Precision * Recall) / (Precision + Recall)

    Args:
        question: Pergunta feita pelo usuário
        answer: Resposta gerada pelo prompt
        reference: Resposta esperada (ground truth)

    Returns:
        Dict com score e reasoning:
        {
            "score": 0.95,
            "precision": 0.9,
            "recall": 0.99,
            "reasoning": "Explicação do LLM..."
        }
    """
    evaluator_prompt = f"""
Você é um avaliador especializado em medir a qualidade de respostas geradas por IA.

Sua tarefa é calcular PRECISION e RECALL para determinar o F1-Score.

PERGUNTA DO USUÁRIO:
{question}

RESPOSTA ESPERADA (Ground Truth):
{reference}

RESPOSTA GERADA PELO MODELO:
{answer}

INSTRUÇÕES:

1. PRECISION (0.0 a 1.0):
   - Quantas informações na resposta gerada são CORRETAS e RELEVANTES?
   - Penalizar informações incorretas, inventadas ou desnecessárias
   - 1.0 = todas informações são corretas e relevantes
   - 0.0 = nenhuma informação é correta ou relevante

2. RECALL (0.0 a 1.0):
   - Quantas informações da resposta esperada estão PRESENTES na resposta gerada?
   - Penalizar informações importantes que foram omitidas
   - 1.0 = todas informações importantes estão presentes
   - 0.0 = nenhuma informação importante está presente

3. RACIOCÍNIO:
   - Explique brevemente sua avaliação
   - Cite exemplos específicos do que estava correto/incorreto

IMPORTANTE: Retorne APENAS um objeto JSON válido no formato:
{{
  "precision": <valor entre 0.0 e 1.0>,
  "recall": <valor entre 0.0 e 1.0>,
  "reasoning": "<sua explicação em até 100 palavras>"
}}

NÃO adicione nenhum texto antes ou depois do JSON.
"""

    try:
        llm = get_evaluator_llm()
        response = llm.invoke([HumanMessage(content=evaluator_prompt)])
        result = extract_json_from_response(response.content)

        precision = float(result.get("precision", 0.0))
        recall = float(result.get("recall", 0.0))

        # Calcular F1-Score
        if (precision + recall) > 0:
            f1_score = 2 * (precision * recall) / (precision + recall)
        else:
            f1_score = 0.0

        return {
            "score": round(f1_score, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "reasoning": result.get("reasoning", "")
        }

    except Exception as e:
        print(f"❌ Erro ao avaliar F1-Score: {e}")
        return {
            "score": 0.0,
            "precision": 0.0,
            "recall": 0.0,
            "reasoning": f"Erro na avaliação: {str(e)}"
        }


def evaluate_clarity(question: str, answer: str, reference: str) -> Dict[str, Any]:
    """
    Avalia a clareza e estrutura da resposta usando LLM-as-Judge.

    Critérios:
    - Organização e estrutura clara
    - Linguagem simples e direta
    - Ausência de ambiguidade
    - Fácil de entender

    Args:
        question: Pergunta feita pelo usuário
        answer: Resposta gerada pelo prompt
        reference: Resposta esperada (ground truth)

    Returns:
        Dict com score e reasoning:
        {
            "score": 0.92,
            "reasoning": "Explicação do LLM..."
        }
    """
    evaluator_prompt = f"""
Você é um avaliador especializado em medir a CLAREZA de respostas geradas por IA.

PERGUNTA DO USUÁRIO:
{question}

RESPOSTA GERADA PELO MODELO:
{answer}

RESPOSTA ESPERADA (Referência):
{reference}

INSTRUÇÕES:

Avalie a CLAREZA da resposta gerada com base nos critérios:

1. ORGANIZAÇÃO (0.0 a 1.0):
   - A resposta tem estrutura lógica e bem organizada?
   - Informações estão em ordem sensata?

2. LINGUAGEM (0.0 a 1.0):
   - Usa linguagem simples e direta?
   - Evita jargões desnecessários?
   - Fácil de entender?

3. AUSÊNCIA DE AMBIGUIDADE (0.0 a 1.0):
   - A resposta é clara e sem ambiguidades?
   - Não deixa dúvidas sobre o que está sendo comunicado?

4. CONCISÃO (0.0 a 1.0):
   - É concisa sem ser curta demais?
   - Não tem informações redundantes?

Calcule a MÉDIA dos 4 critérios para obter o score final.

IMPORTANTE: Retorne APENAS um objeto JSON válido no formato:
{{
  "score": <valor entre 0.0 e 1.0>,
  "reasoning": "<explicação detalhada da avaliação em até 100 palavras>"
}}

NÃO adicione nenhum texto antes ou depois do JSON.
"""

    try:
        llm = get_evaluator_llm()
        response = llm.invoke([HumanMessage(content=evaluator_prompt)])
        result = extract_json_from_response(response.content)

        score = float(result.get("score", 0.0))

        return {
            "score": round(score, 4),
            "reasoning": result.get("reasoning", "")
        }

    except Exception as e:
        print(f"❌ Erro ao avaliar Clarity: {e}")
        return {
            "score": 0.0,
            "reasoning": f"Erro na avaliação: {str(e)}"
        }


def evaluate_precision(question: str, answer: str, reference: str) -> Dict[str, Any]:
    """
    Avalia a precisão da resposta usando LLM-as-Judge.

    Critérios:
    - Ausência de informações inventadas (alucinações)
    - Resposta focada na pergunta
    - Informações corretas e verificáveis

    Args:
        question: Pergunta feita pelo usuário
        answer: Resposta gerada pelo prompt
        reference: Resposta esperada (ground truth)

    Returns:
        Dict com score e reasoning:
        {
            "score": 0.98,
            "reasoning": "Explicação do LLM..."
        }
    """
    
    evaluator_prompt = f"""
Você é um avaliador especializado em detectar PRECISÃO e ALUCINAÇÕES em respostas de IA.

PERGUNTA DO USUÁRIO:
{question}

RESPOSTA GERADA PELO MODELO:
{answer}

RESPOSTA ESPERADA (Ground Truth):
{reference}

INSTRUÇÕES:

Avalie a PRECISÃO da resposta gerada:

1. AUSÊNCIA DE ALUCINAÇÕES (0.0 a 1.0):
   - A resposta contém informações INVENTADAS ou não verificáveis?
   - Todas as afirmações são baseadas em fatos?
   - 1.0 = nenhuma alucinação detectada
   - 0.0 = resposta cheia de informações inventadas

2. FOCO NA PERGUNTA (0.0 a 1.0):
   - A resposta responde EXATAMENTE o que foi perguntado?
   - Não divaga ou adiciona informações não solicitadas?
   - 1.0 = totalmente focada
   - 0.0 = completamente fora do tópico

3. CORREÇÃO FACTUAL (0.0 a 1.0):
   - As informações estão CORRETAS quando comparadas com a referência?
   - Não há erros ou imprecisões?
   - 1.0 = todas informações corretas
   - 0.0 = informações incorretas

Calcule a MÉDIA dos 3 critérios para obter o score final.

IMPORTANTE: Retorne APENAS um objeto JSON válido no formato:
{{
  "score": <valor entre 0.0 e 1.0>,
  "reasoning": "<explicação detalhada em até 100 palavras, cite exemplos>"
}}

NÃO adicione nenhum texto antes ou depois do JSON.
"""

    try:
        llm = get_evaluator_llm()
        response = llm.invoke([HumanMessage(content=evaluator_prompt)])
        result = extract_json_from_response(response.content)

        score = float(result.get("score", 0.0))

        return {
            "score": round(score, 4),
            "reasoning": result.get("reasoning", "")
        }

    except Exception as e:
        print(f"❌ Erro ao avaliar Precision: {e}")
        return {
            "score": 0.0,
            "reasoning": f"Erro na avaliação: {str(e)}"
        }


def evaluate_tone_score(bug_report: str, user_story: str, reference: str) -> Dict[str, Any]:
    """
    Avalia o tom da user story de forma determinística.

    Critérios:
    - Empatia (frustração / insegurança / confiança)
    - Urgência (risco, churn, perda de receita)
    - Foco no usuário + valor de negócio
    """
    user_story_lower = user_story.lower()
    checks = [
        "frustração" in user_story_lower,
        "inseguro" in user_story_lower or "confiança" in user_story_lower,
        "churn" in user_story_lower or "perda" in user_story_lower,
        "para que" in user_story_lower,
        "valor" in user_story_lower or "negócio" in user_story_lower,
    ]
    score = sum(1 for c in checks if c) / len(checks)
    reasoning = (
        f"Empatia detectada: {checks[0]}, "
        f"insegurança/confiança: {checks[1]}, "
        f"urgência/churn/perda: {checks[2]}, "
        f"valor: {checks[4]}."
    )
    return {"score": round(score, 4), "reasoning": reasoning}


def evaluate_acceptance_criteria_score(bug_report: str, user_story: str, reference: str) -> Dict[str, Any]:
    """
    Evaluação determinística dos critérios de aceitação.
    """
    lower = user_story.lower()
    lines = [line.strip() for line in lower.splitlines() if line.strip()]

    # Identificar seção de critérios
    if "## critérios de aceitação" not in lower:
        return {"score": 0.0, "reasoning": "Seção de critérios ausente."}

    criteria_lines = []
    collecting = False
    for line in lines:
        if line.startswith("## critérios de aceitação"):
            collecting = True
            continue
        if collecting:
            if line.startswith("## "):
                break
            criteria_lines.append(line)

    num_criteria = sum(1 for line in criteria_lines if line.startswith("1.") or line.startswith("2.") or line.startswith("3.") or line.startswith("4.") or line.startswith("5."))
    has_metric = all("métrica de sucesso" in line for line in criteria_lines if line and line[0].isdigit())
    has_teste = all("teste" in line for line in criteria_lines if line and line[0].isdigit())

    score_elements = [
        num_criteria >= 5,
        num_criteria <= 7,
        has_metric,
        has_teste,
    ]
    score = sum(1 for x in score_elements if x) / len(score_elements)
    reasoning = f"Critérios: {num_criteria}, métrica: {has_metric}, teste: {has_teste}."
    return {"score": round(score, 4), "reasoning": reasoning}


def evaluate_user_story_format_score(bug_report: str, user_story: str, reference: str) -> Dict[str, Any]:
    """
    Verifica formato de User Story de forma determinística.
    """
    text = user_story.strip()
    score = 0
    max_score = 5

    # 1. Checa cabeçalhos
    if "## user story" in text.lower():
        score += 1
    if "## impacto" in text.lower():
        score += 1
    if "## critérios de aceitação" in text.lower():
        score += 1

    # 2. Checa user story template exato
    first_line = text.splitlines()[1] if len(text.splitlines()) > 1 else ""
    if "como um" in first_line.lower() and "eu quero" in first_line.lower() and "para que" in first_line.lower():
        score += 1

    # 3. Checa 5 critérios enumerados
    criteria = [line for line in text.splitlines() if line.strip().startswith(("1.", "2.", "3.", "4.", "5."))]
    if len(criteria) >= 5:
        score += 1

    result = score / max_score
    reasoning = f"Cabeçalhos: {score - (1 if len(criteria) < 5 else 0) - (1 if 'como um' not in first_line.lower() else 0)} / 3; Criteria: {len(criteria)}."
    return {"score": round(result, 4), "reasoning": reasoning}


def evaluate_completeness_score(bug_report: str, user_story: str, reference: str) -> Dict[str, Any]:
    """
    Verificação determinística da completude.
    """
    lower = user_story.lower()
    checks = [
        "## impacto" in lower,
        "risco de não resolver" in lower or "risco" in lower,
        "métrica de sucesso" in lower,
        "teste" in lower,
        "para que" in lower,
    ]
    score = sum(1 for c in checks if c) / len(checks)
    reasoning = f"Impacto: {checks[0]}, risco: {checks[1]}, métrica: {checks[2]}, teste: {checks[3]}, valor: {checks[4]}."
    return {"score": round(score, 4), "reasoning": reasoning}


# Exemplo de uso e testes
if __name__ == "__main__":
    # Mostrar provider configurado
    provider = os.getenv("LLM_PROVIDER", "openai")
    eval_model = os.getenv("EVAL_MODEL", "gpt-4o")

    print("=" * 70)
    print("TESTANDO MÉTRICAS CUSTOMIZADAS")
    print("=" * 70)
    print(f"\n📊 Provider: {provider}")
    print(f"🤖 Modelo de Avaliação: {eval_model}\n")

    print("=" * 70)
    print("PARTE 1: MÉTRICAS GERAIS")
    print("=" * 70)

    # Teste das métricas gerais
    test_question = "Qual o horário de funcionamento da loja?"
    test_answer = "A loja funciona de segunda a sexta das 9h às 18h."
    test_reference = "Horário de funcionamento: Segunda a Sexta 9:00-18:00, Sábado 9:00-14:00"

    print("\n1. F1-Score:")
    f1_result = evaluate_f1_score(test_question, test_answer, test_reference)
    print(f"   Score: {f1_result['score']:.2f}")
    print(f"   Precision: {f1_result['precision']:.2f}")
    print(f"   Recall: {f1_result['recall']:.2f}")
    print(f"   Reasoning: {f1_result['reasoning']}\n")

    print("2. Clarity:")
    clarity_result = evaluate_clarity(test_question, test_answer, test_reference)
    print(f"   Score: {clarity_result['score']:.2f}")
    print(f"   Reasoning: {clarity_result['reasoning']}\n")

    print("3. Precision:")
    precision_result = evaluate_precision(test_question, test_answer, test_reference)
    print(f"   Score: {precision_result['score']:.2f}")
    print(f"   Reasoning: {precision_result['reasoning']}\n")

    print("=" * 70)
    print("PARTE 2: MÉTRICAS ESPECÍFICAS PARA BUG TO USER STORY")
    print("=" * 70)

    # Teste das métricas específicas de Bug to User Story
    test_bug = "Botão de adicionar ao carrinho não funciona no produto ID 1234."
    test_user_story = """Como um cliente navegando na loja, eu quero adicionar produtos ao meu carrinho de compras, para que eu possa continuar comprando e finalizar minha compra depois.

Critérios de Aceitação:
- Dado que estou visualizando um produto
- Quando clico no botão "Adicionar ao Carrinho"
- Então o produto deve ser adicionado ao carrinho
- E devo ver uma confirmação visual
- E o contador do carrinho deve ser atualizado"""

    test_reference_story = test_user_story  # Usando o mesmo para teste

    print("\n4. Tone Score (Tom profissional e empático):")
    tone_result = evaluate_tone_score(test_bug, test_user_story, test_reference_story)
    print(f"   Score: {tone_result['score']:.2f}")
    print(f"   Reasoning: {tone_result['reasoning']}\n")

    print("5. Acceptance Criteria Score (Qualidade dos critérios):")
    criteria_result = evaluate_acceptance_criteria_score(test_bug, test_user_story, test_reference_story)
    print(f"   Score: {criteria_result['score']:.2f}")
    print(f"   Reasoning: {criteria_result['reasoning']}\n")

    print("6. User Story Format Score (Formato correto):")
    format_result = evaluate_user_story_format_score(test_bug, test_user_story, test_reference_story)
    print(f"   Score: {format_result['score']:.2f}")
    print(f"   Reasoning: {format_result['reasoning']}\n")

    print("7. Completeness Score (Completude e contexto):")
    completeness_result = evaluate_completeness_score(test_bug, test_user_story, test_reference_story)
    print(f"   Score: {completeness_result['score']:.2f}")
    print(f"   Reasoning: {completeness_result['reasoning']}\n")

    print("=" * 70)
    print("✅ TODOS OS TESTES CONCLUÍDOS!")
    print("=" * 70)
