"""
Script de avaliação LOCAL para testar prompts v2 sem LangSmith Hub.

Este script:
1. Carrega prompt v2 do arquivo YAML local
2. Carrega alguns exemplos do dataset
3. Executa o prompt contra os exemplos
4. Calcula métricas localmente
5. Mostra resultados no terminal

Útil para testar e iterar antes do push final.
"""

import os
import sys
import json
from typing import List, Dict, Any
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.prompts import PromptTemplate
from utils import load_yaml, check_env_vars, format_score, print_section_header, get_llm
from metrics import evaluate_tone_score, evaluate_acceptance_criteria_score, evaluate_user_story_format_score, evaluate_completeness_score

load_dotenv()


def load_local_prompt_v2() -> ChatPromptTemplate:
    """Carrega prompt v2 do arquivo YAML local."""
    print("📖 Carregando prompt v2 do arquivo local...")

    v2_path = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"
    prompt_data = load_yaml(str(v2_path))

    if not prompt_data:
        raise ValueError("❌ Falha ao carregar prompt v2")

    v2_data = prompt_data.get('bug_to_user_story_v2', {})
    if not v2_data:
        raise ValueError("❌ Chave 'bug_to_user_story_v2' não encontrada")

    # Construir ChatPromptTemplate
    system_template = PromptTemplate(
        template=v2_data['system_prompt'],
        input_variables=v2_data.get('input_variables', ['bug_report'])
    )

    user_template = PromptTemplate(
        template=v2_data['user_prompt'],
        input_variables=v2_data.get('input_variables', ['bug_report'])
    )

    chat_prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate(prompt=system_template),
        HumanMessagePromptTemplate(prompt=user_template)
    ])

    print("✓ Prompt v2 carregado com sucesso")
    return chat_prompt


def load_sample_examples(jsonl_path: str, num_samples: int = 3) -> List[Dict[str, Any]]:
    """Carrega alguns exemplos do dataset para teste."""
    examples = []

    try:
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i >= num_samples:
                    break
                line = line.strip()
                if line:
                    example = json.loads(line)
                    examples.append(example)

        return examples

    except Exception as e:
        print(f"❌ Erro ao carregar exemplos: {e}")
        return []


def evaluate_prompt_locally(prompt_template: ChatPromptTemplate, examples: List[Dict[str, Any]], llm) -> Dict[str, Any]:
    """Avalia prompt contra exemplos e calcula métricas."""
    results = []

    print(f"\n🔍 Avaliando {len(examples)} exemplos...")

    for i, example in enumerate(examples, 1):
        print(f"\n--- Exemplo {i} ---")

        bug_report = example['inputs']['bug_report']
        expected_output = example['outputs']['reference']

        print(f"Bug: {bug_report[:100]}...")

        try:
            # Executar prompt
            chain = prompt_template | llm
            response = chain.invoke({"bug_report": bug_report})

            generated_output = response.content if hasattr(response, 'content') else str(response)
            print(f"Generated: {generated_output[:200]}...")

            # Calcular métricas
            tone_result = evaluate_tone_score(bug_report, generated_output, expected_output)
            acceptance_result = evaluate_acceptance_criteria_score(bug_report, generated_output, expected_output)
            format_result = evaluate_user_story_format_score(bug_report, generated_output, expected_output)
            completeness_result = evaluate_completeness_score(bug_report, generated_output, expected_output)
            
            tone_score_value = tone_result.get('score', 0.0)
            acceptance_score_value = acceptance_result.get('score', 0.0)
            user_story_format_score_value = format_result.get('score', 0.0)
            completeness_score_value = completeness_result.get('score', 0.0)

            result = {
                'example_id': i,
                'bug_report': bug_report,
                'expected': expected_output,
                'generated': generated_output,
                'tone_score': tone_score_value,
                'acceptance_criteria_score': acceptance_score_value,
                'user_story_format_score': user_story_format_score_value,
                'completeness_score': completeness_score_value
            }

            results.append(result)

            print(f"Tone: {format_score(tone_score_value)}")
            print(f"Acceptance: {format_score(acceptance_score_value)}")
            print(f"Format: {format_score(user_story_format_score_value)}")
            print(f"Completeness: {format_score(completeness_score_value)}")

        except Exception as e:
            print(f"❌ Erro ao avaliar exemplo {i}: {e}")
            continue

    return results


def calculate_overall_scores(results: List[Dict[str, Any]]) -> Dict[str, float]:
    """Calcula médias das métricas."""
    if not results:
        return {}

    scores = {
        'tone_score': [],
        'acceptance_criteria_score': [],
        'user_story_format_score': [],
        'completeness_score': []
    }

    for result in results:
        for metric in scores.keys():
            scores[metric].append(result[metric])

    # Calcular médias
    overall = {}
    for metric, values in scores.items():
        overall[metric] = sum(values) / len(values) if values else 0.0

    return overall


def main():
    """Função principal."""
    print_section_header("AVALIAÇÃO LOCAL DO PROMPT V2")

    # Verificar env vars
    required_vars = ['OPENAI_API_KEY']
    if not check_env_vars(required_vars):
        return 1

    try:
        # Carregar prompt v2
        prompt = load_local_prompt_v2()

        # Carregar exemplos de teste
        dataset_path = Path(__file__).parent.parent / "datasets" / "bug_to_user_story.jsonl"
        examples = load_sample_examples(str(dataset_path), num_samples=1)

        if not examples:
            print("❌ Nenhum exemplo carregado")
            return 1

        # Configurar LLM
        llm = get_llm()

        # Avaliar
        results = evaluate_prompt_locally(prompt, examples, llm)

        if not results:
            print("❌ Nenhuma avaliação realizada")
            return 1

        # Calcular médias
        overall_scores = calculate_overall_scores(results)

        print_section_header("RESULTADOS FINAIS")

        print("Métricas médias:")
        for metric, score in overall_scores.items():
            formatted_metric = metric.replace('_', ' ').title()
            print(f"- {formatted_metric}: {format_score(score)}")

        # Verificar aprovação
        all_above_threshold = all(score >= 0.9 for score in overall_scores.values())

        print(f"\n{'='*50}")
        if all_above_threshold:
            print("✅ APROVADO - Todas as métricas atingiram o mínimo de 0.9")
        else:
            print("❌ FALHOU - Algumas métricas abaixo do mínimo de 0.9")
            print("Precisa de iteração adicional no prompt v2")
        print(f"{'='*50}")

        return 0 if all_above_threshold else 1

    except Exception as e:
        print(f"❌ Erro na avaliação local: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())