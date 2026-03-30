"""
Script para avaliar prompts otimizados usando LangSmith Evaluation.

Este script:
1. Carrega dataset de avaliação de arquivo .jsonl (datasets/bug_to_user_story.jsonl)
2. Cria/atualiza dataset no LangSmith
3. Puxa prompts otimizados do LangSmith Hub
4. Executa avaliação via langsmith.evaluation.evaluate()
5. Calcula 4 métricas específicas para User Story
6. Publica resultados no dashboard do LangSmith (experimento visível)
7. Exibe resumo no terminal

Suporta múltiplos providers de LLM:
- OpenAI (gpt-4o, gpt-4o-mini)
- Google Gemini (gemini-2.5-flash)

Configure o provider no arquivo .env através da variável LLM_PROVIDER.
"""

import os
import sys
import json
import time
from typing import List, Dict, Any
from pathlib import Path
from dotenv import load_dotenv
from langsmith import Client
from langsmith.evaluation import evaluate
from langsmith.schemas import Example, Run
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import check_env_vars, format_score, print_section_header, get_llm as get_configured_llm
from metrics import (
    evaluate_tone_score,
    evaluate_acceptance_criteria_score,
    evaluate_user_story_format_score,
    evaluate_completeness_score
)

load_dotenv()


def get_llm():
    return get_configured_llm(temperature=0)


def load_dataset_from_jsonl(jsonl_path: str) -> List[Dict[str, Any]]:
    examples = []

    try:
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    example = json.loads(line)
                    examples.append(example)

        return examples

    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {jsonl_path}")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao parsear JSONL: {e}")
        return []
    except Exception as e:
        print(f"❌ Erro ao carregar dataset: {e}")
        return []


def create_evaluation_dataset(client: Client, dataset_name: str, jsonl_path: str) -> str:
    print(f"Criando dataset de avaliação: {dataset_name}...")

    examples = load_dataset_from_jsonl(jsonl_path)

    if not examples:
        print("❌ Nenhum exemplo carregado do arquivo .jsonl")
        return dataset_name

    print(f"   ✓ Carregados {len(examples)} exemplos do arquivo {jsonl_path}")

    try:
        datasets = client.list_datasets(dataset_name=dataset_name)
        existing_dataset = None

        for ds in datasets:
            if ds.name == dataset_name:
                existing_dataset = ds
                break

        if existing_dataset:
            print(f"   ✓ Dataset '{dataset_name}' já existe, usando existente")
            return dataset_name
        else:
            dataset = client.create_dataset(dataset_name=dataset_name)

            for example in examples:
                client.create_example(
                    dataset_id=dataset.id,
                    inputs=example["inputs"],
                    outputs=example["outputs"]
                )

            print(f"   ✓ Dataset criado com {len(examples)} exemplos")
            return dataset_name

    except Exception as e:
        print(f"   ⚠️  Erro ao criar dataset: {e}")
        return dataset_name


def pull_prompt_from_langsmith(prompt_name: str) -> ChatPromptTemplate:
    try:
        print(f"   Puxando prompt do LangSmith Hub: {prompt_name}")
        prompt = hub.pull(prompt_name)
        print(f"   ✓ Prompt carregado com sucesso")
        return prompt

    except Exception as e:
        error_msg = str(e).lower()

        print(f"\n{'=' * 70}")
        print(f"❌ ERRO: Não foi possível carregar o prompt '{prompt_name}'")
        print(f"{'=' * 70}\n")

        if "not found" in error_msg or "404" in error_msg:
            print("⚠️  O prompt não foi encontrado no LangSmith Hub.")
            print("   python src/push_prompts.py")
        else:
            print(f"Erro técnico: {e}")

        print(f"\n{'=' * 70}\n")
        raise


def make_target(prompt_template: ChatPromptTemplate, llm):
    """Cria a função target para langsmith.evaluation.evaluate()."""
    chain = prompt_template | llm

    def target(inputs: dict) -> dict:
        time.sleep(1)
        response = chain.invoke(inputs)
        return {"answer": response.content}

    return target


def tone_evaluator(run: Run, example: Example) -> dict:
    """Evaluator de Tone Score para LangSmith."""
    time.sleep(1)
    answer = run.outputs.get("answer", "")
    reference = example.outputs.get("reference", "")
    question = example.inputs.get("bug_report", "")
    result = evaluate_tone_score(question, answer, reference)
    return {"key": "tone_score", "score": result["score"]}


def acceptance_criteria_evaluator(run: Run, example: Example) -> dict:
    """Evaluator de Acceptance Criteria Score para LangSmith."""
    time.sleep(1)
    answer = run.outputs.get("answer", "")
    reference = example.outputs.get("reference", "")
    question = example.inputs.get("bug_report", "")
    result = evaluate_acceptance_criteria_score(question, answer, reference)
    return {"key": "acceptance_criteria_score", "score": result["score"]}


def format_evaluator(run: Run, example: Example) -> dict:
    """Evaluator de User Story Format Score para LangSmith."""
    time.sleep(1)
    answer = run.outputs.get("answer", "")
    reference = example.outputs.get("reference", "")
    question = example.inputs.get("bug_report", "")
    result = evaluate_user_story_format_score(question, answer, reference)
    return {"key": "user_story_format_score", "score": result["score"]}


def completeness_evaluator(run: Run, example: Example) -> dict:
    """Evaluator de Completeness Score para LangSmith."""
    time.sleep(1)
    answer = run.outputs.get("answer", "")
    reference = example.outputs.get("reference", "")
    question = example.inputs.get("bug_report", "")
    result = evaluate_completeness_score(question, answer, reference)
    return {"key": "completeness_score", "score": result["score"]}


def main():
    print_section_header("AVALIAÇÃO DE PROMPTS OTIMIZADOS")

    provider = os.getenv("LLM_PROVIDER", "openai")
    llm_model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    eval_model = os.getenv("EVAL_MODEL", "gpt-4o")

    print(f"Provider: {provider}")
    print(f"Modelo Principal: {llm_model}")
    print(f"Modelo de Avaliação: {eval_model}\n")

    required_vars = ["LANGSMITH_API_KEY", "LLM_PROVIDER"]
    if provider == "openai":
        required_vars.append("OPENAI_API_KEY")
    elif provider in ["google", "gemini"]:
        required_vars.append("GOOGLE_API_KEY")

    if not check_env_vars(required_vars):
        return 1

    client = Client()
    project_name = os.getenv("LANGCHAIN_PROJECT", "mba")

    jsonl_path = "datasets/bug_to_user_story.jsonl"

    if not Path(jsonl_path).exists():
        print(f"❌ Arquivo de dataset não encontrado: {jsonl_path}")
        return 1

    dataset_name = f"{project_name}-eval"
    create_evaluation_dataset(client, dataset_name, jsonl_path)

    print("\n" + "=" * 70)
    print("PROMPTS PARA AVALIAR")
    print("=" * 70 + "\n")

    prompts_to_evaluate = [
        "eloiza-souza/bug_to_user_story_v2",
    ]

    all_passed = True

    for prompt_name in prompts_to_evaluate:
        try:
            prompt_template = pull_prompt_from_langsmith(prompt_name)
            llm = get_llm()
            target = make_target(prompt_template, llm)

            experiment_prefix = prompt_name.split("/")[-1]

            print(f"\n🔍 Avaliando: {prompt_name}")
            print(f"   Experimento: {experiment_prefix}")
            print(f"   Dataset: {dataset_name}")
            print(f"   Avaliando com LangSmith evaluate()...\n")

            results = evaluate(
                target,
                data=dataset_name,
                evaluators=[
                    tone_evaluator,
                    acceptance_criteria_evaluator,
                    format_evaluator,
                    completeness_evaluator,
                ],
                experiment_prefix=experiment_prefix,
                metadata={
                    "prompt": prompt_name,
                    "llm_model": llm_model,
                    "eval_model": eval_model,
                    "provider": provider,
                },
                max_concurrency=0,
                client=client,
            )

            # Coletar scores dos resultados
            tone_scores = []
            ac_scores = []
            format_scores = []
            complete_scores = []

            example_details = []

            for i, result in enumerate(results):
                eval_results = result.get("evaluation_results", {})
                feedback = eval_results.get("results", [])
                example_scores = {}
                for fb in feedback:
                    key = fb.key
                    score = fb.score
                    example_scores[key] = score
                    if key == "tone_score":
                        tone_scores.append(score)
                    elif key == "acceptance_criteria_score":
                        ac_scores.append(score)
                    elif key == "user_story_format_score":
                        format_scores.append(score)
                    elif key == "completeness_score":
                        complete_scores.append(score)

                # Get bug report snippet
                run_input = result.get("run", None)
                bug_snippet = ""
                if run_input and hasattr(run_input, 'inputs'):
                    bug_text = run_input.inputs.get("bug_report", "")
                    bug_snippet = bug_text[:80].replace('\n', ' ')

                example_details.append({
                    "index": i + 1,
                    "bug": bug_snippet,
                    "scores": example_scores,
                })

            # Print per-example scores
            print("\n" + "=" * 90)
            print("SCORES POR EXEMPLO")
            print("=" * 90)
            print(f"{'#':>3} | {'Tone':>5} | {'AC':>5} | {'Fmt':>5} | {'Comp':>5} | {'Média':>5} | Bug")
            print("-" * 90)
            for detail in example_details:
                s = detail["scores"]
                t = s.get("tone_score", 0)
                a = s.get("acceptance_criteria_score", 0)
                f = s.get("user_story_format_score", 0)
                c = s.get("completeness_score", 0)
                avg = (t + a + f + c) / 4
                flag = " ⚠️" if avg < 0.85 else ""
                print(f"{detail['index']:>3} | {t:>5.2f} | {a:>5.2f} | {f:>5.2f} | {c:>5.2f} | {avg:>5.2f} | {detail['bug'][:60]}{flag}")
            print("-" * 90)

            scores = {
                "tone_score": round(sum(tone_scores) / len(tone_scores), 4) if tone_scores else 0.0,
                "acceptance_criteria_score": round(sum(ac_scores) / len(ac_scores), 4) if ac_scores else 0.0,
                "user_story_format_score": round(sum(format_scores) / len(format_scores), 4) if format_scores else 0.0,
                "completeness_score": round(sum(complete_scores) / len(complete_scores), 4) if complete_scores else 0.0,
            }

            # Exibir resultados
            print("\n" + "=" * 50)
            print(f"Prompt: {prompt_name}")
            print("=" * 50)

            print("\n📊 Métricas Bug to User Story:")
            print(f"  - Tone Score: {format_score(scores['tone_score'], threshold=0.9)}")
            print(f"  - Acceptance Criteria Score: {format_score(scores['acceptance_criteria_score'], threshold=0.9)}")
            print(f"  - User Story Format Score: {format_score(scores['user_story_format_score'], threshold=0.9)}")
            print(f"  - Completeness Score: {format_score(scores['completeness_score'], threshold=0.9)}")

            average_score = sum(scores.values()) / len(scores)
            print(f"\n{'─' * 50}")
            print(f"📊 MÉDIA GERAL: {average_score:.4f}")
            print(f"{'─' * 50}")

            all_metrics_pass = all(score >= 0.9 for score in scores.values())
            passed = all_metrics_pass and average_score >= 0.9

            if passed:
                print(f"\n✅ STATUS: APROVADO")
                print(f"   ✓ Todas as 4 métricas >= 0.9")
            else:
                print(f"\n❌ STATUS: REPROVADO")
                for name, score in scores.items():
                    if score < 0.9:
                        print(f"   ⚠️  {name}: {score:.4f} (precisa >= 0.9)")

            all_passed = all_passed and passed

        except Exception as e:
            print(f"\n❌ Falha ao avaliar '{prompt_name}': {e}")
            import traceback
            traceback.print_exc()
            all_passed = False

    print("\n" + "=" * 50)
    print("RESUMO FINAL")
    print("=" * 50 + "\n")

    print(f"📎 Dashboard LangSmith:")
    print(f"   https://smith.langchain.com\n")

    if all_passed:
        print("✅ Todos os prompts atingiram média >= 0.9!")
        return 0
    else:
        print("⚠️  Alguns prompts não atingiram média >= 0.9")
        print("\nPróximos passos:")
        print("1. Refatore os prompts com score baixo")
        print("2. Faça push novamente: python src/push_prompts.py")
        print("3. Execute: python src/evaluate.py novamente")
        return 1

if __name__ == "__main__":
    sys.exit(main())
