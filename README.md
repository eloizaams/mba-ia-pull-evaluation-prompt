# Entrega Oficial - MBA IA Prompt Engineering

Este repositorio contem a entrega final do desafio de otimizacao e avaliacao de prompt (`bug_to_user_story`).

## Documentos principais

- Relatorio executivo de resultados: [RESULTADO.md](RESULTADO.md)
- README anterior (documentacao completa original): [README_ANTERIOR.md](README_ANTERIOR.md)
- Prompt final otimizado: [prompts/bug_to_user_story_v2.yml](prompts/bug_to_user_story_v2.yml)

## Evidencias LangSmith

- Prompt publicado no Hub: https://smith.langchain.com/hub/eloiza-souza/bug_to_user_story_v2
- Dashboard publico da avaliacao (R17): https://smith.langchain.com/o/094c48d0-a048-4983-a7aa-47b14f5297b4/datasets/57642db8-5147-4270-8692-d71745148b97/compare?selectedSessions=db179fc2-6dc5-4a98-a48d-489733c99695

## Resultado final (resumo)

- Media geral: `0.9077`
- Acceptance Criteria: `0.90`
- Completeness: `0.91`
- User Story Format: `0.92`
- Tone: `0.8967` (aprox. 0.90)

## Como executar rapidamente

1. Criar e ativar o ambiente virtual:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Configurar variaveis de ambiente em `.env` (OpenAI e LangSmith).

3. Executar fluxo completo:

```bash
python src/pull_prompts.py
python src/push_prompts.py
python src/evaluate.py
pytest tests/test_prompts.py -q
```

## Estrutura relevante

- `prompts/` - prompts v1 e v2
- `src/` - scripts de pull, push, avaliacao e metricas
- `tests/` - testes de validacao dos prompts
- `datasets/` - dataset usado na avaliacao

## Observacao

Este `README.md` foi reduzido para formato de entrega.
A documentacao detalhada original foi preservada em `README_ANTERIOR.md`.
