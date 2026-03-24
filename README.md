# Pull, Otimização e Avaliação de Prompts com LangChain e LangSmith

## Objetivo

Você deve entregar um software capaz de:

1. **Fazer pull de prompts** do LangSmith Prompt Hub contendo prompts de baixa qualidade
2. **Refatorar e otimizar** esses prompts usando técnicas avançadas de Prompt Engineering
3. **Fazer push dos prompts otimizados** de volta ao LangSmith
4. **Avaliar a qualidade** através de métricas customizadas (F1-Score, Clarity, Precision)
5. **Atingir pontuação mínima** de 0.9 (90%) em todas as métricas de avaliação

---

## Exemplo no CLI

```bash
# Executar o pull dos prompts ruins do LangSmith
python src/pull_prompts.py

# Executar avaliação inicial (prompts ruins)
python src/evaluate.py

Executando avaliação dos prompts...
================================
Prompt: support_bot_v1a
- Helpfulness: 0.45
- Correctness: 0.52
- F1-Score: 0.48
- Clarity: 0.50
- Precision: 0.46
================================
Status: FALHOU - Métricas abaixo do mínimo de 0.9

# Após refatorar os prompts e fazer push
python src/push_prompts.py

# Executar avaliação final (prompts otimizados)
python src/evaluate.py

Executando avaliação dos prompts...
================================
Prompt: support_bot_v2_optimized
- Helpfulness: 0.94
- Correctness: 0.96
- F1-Score: 0.93
- Clarity: 0.95
- Precision: 0.92
================================
Status: APROVADO ✓ - Todas as métricas atingiram o mínimo de 0.9
```
---

## Tecnologias obrigatórias

- **Linguagem:** Python 3.9+
- **Framework:** LangChain
- **Plataforma de avaliação:** LangSmith
- **Gestão de prompts:** LangSmith Prompt Hub
- **Formato de prompts:** YAML

---

## Pacotes recomendados

```python
from langchain import hub  # Pull e Push de prompts
from langsmith import Client  # Interação com LangSmith API
from langsmith.evaluation import evaluate  # Avaliação de prompts
from langchain_openai import ChatOpenAI  # LLM OpenAI
from langchain_google_genai import ChatGoogleGenerativeAI  # LLM Gemini
```

---

## OpenAI

- Crie uma **API Key** da OpenAI: https://platform.openai.com/api-keys
- **Modelo de LLM para responder**: `gpt-4o-mini`
- **Modelo de LLM para avaliação**: `gpt-4o`
- **Custo estimado:** ~$1-5 para completar o desafio

## Gemini (modelo free)

- Crie uma **API Key** da Google: https://aistudio.google.com/app/apikey
- **Modelo de LLM para responder**: `gemini-2.5-flash`
- **Modelo de LLM para avaliação**: `gemini-2.5-flash`
- **Limite:** 15 req/min, 1500 req/dia

---

---

## Técnicas Aplicadas (Fase 2)

A versão otimizada do prompt (`bug_to_user_story_v2.yml`) foi desenvolvida aplicando as seguintes técnicas avançadas de Prompt Engineering:

### 1. **Few-shot Learning** ⭐
**O que é:** Fornecer exemplos claros de entrada/saída para guiar o modelo.

**Como foi aplicado:**
- Inclusos **3 exemplos reais** de transformação bug → user story
- Cada exemplo mostra:
  - O bug report original
  - A user story bem estruturada resultante
  - Os critérios de aceitação completos
  - Context (domínio, complexidade, tipo)

**Por quê:** O modelo aprende pelo exemplo. Ver 3 transformações bem-feitas reduz ambigüidade e garante consistência no formato de saída.

---

### 2. **Chain of Thought (CoT)** ⭐
**O que é:** Instruir o modelo a "pensar passo a passo" antes de gerar a resposta.

**Como foi aplicado:**
- Adicionada seção "PASSO-A-PASSO DE ANÁLISE" no system prompt
- 6 passos estruturados:
  1. Ler o bug e identificar problema/onde/quem
  2. Determinar a persona do usuário
  3. Extrair o valor/benefício
  4. Definir domínio e complexidade
  5. Estruturar critérios de aceitação logicamente
  6. Revisar cases edge e cenários alternativos

**Por quê:** CoT melhora a qualidade de respostas complexas ao forçar raciocínio explícito, reduzindo erros lógicos.

---

### 3. **Role Prompting**
**O que é:** Definir uma persona clara e contexto detalhado.

**Como foi aplicado:**
- Sistema posicionado como "Senior Product Manager especializado em transformar bugs em User Stories"
- Responsabilidade clara: garantir User Stories "claras, acionáveis e bem documentadas"
- Conhecimento de domínios específicos (e-commerce, saas, mobile)

**Por quê:** Role Prompting aumenta a qualidade e profundidade das respostas ao alinhar o LLM com um contexto específico.

---

### 4. **Skeleton of Thought**
**O que é:** Estruturar a resposta em seções claras e bem definidas.

**Como foi aplicado:**
- Resposta segue estrutura obrigatória de 5 seções:
  1. Análise do Bug (identifica problema, contexto, persona, domínio)
  2. User Story (formato "Como... eu quero... para que...")
  3. Critérios de Aceitação (formato Given-When-Then)
  4. Tratamento de Edge Cases
  5. Observações Importantes (notas para desenvolvedores)

**Por quê:** Estrutura fixa previne outputs caóticos e garante que todas as informações necessárias sejam incluídas.

---

### 5. **Regras Explícitas de Comportamento**
**Adicionadas:**
- ✓ Sempre usar formato "Como um... eu quero... para que..."
- ✓ Mínimo de 5 Critérios de Aceitação em formato Given-When-Then
- ✓ Identificar domínio e complexidade
- ✓ Tratar casos especiais (navegador, dispositivo, versão)
- ✓ Priorizar clareza e objetividade (cada critério deve ser testável)

---

## Requisitos

### 1. Pull dos Prompt inicial do LangSmith

✓ **FASE 1 COMPLETADA**

**O que foi feito:**

1. ✓ Configuradas credenciais do LangSmith no arquivo `.env`
2. ✓ Script `src/pull_prompts.py` implementado com sucesso
   - ✓ Conecta ao LangSmith usando API Key do `.env`
   - ✓ Faz pull do prompt `leonanluppi/bug_to_user_story_v1` do Hub
   - ✓ Salva em `prompts/bug_to_user_story_v1.yml` em formato YAML estruturado
   - ✓ Validação de variáveis de ambiente
   - ✓ Mensagens de feedback ao usuário

**Como executar:**
```bash
python src/pull_prompts.py
```

**Output esperado:**
- Prompt puxado com sucesso do LangSmith
- Salvo em `prompts/bug_to_user_story_v1.yml`
- Pronto para otimização

---

### 2. Otimização do Prompt

A versão otimizada foi criada em `prompts/bug_to_user_story_v2.yml` aplicando **4 técnicas avançadas** de Prompt Engineering:

**✓ Tarefas Completadas:**

1. ✓ Analisar o prompt em `prompts/bug_to_user_story_v1.yml` - Identificamos que era muito genérico e vago
2. ✓ Criar arquivo `prompts/bug_to_user_story_v2.yml` com versões otimizadas - **Arquivo criado com sucesso**
3. ✓ Aplicar técnicas avançadas:
   - ✓ **Few-shot Learning**: 3 exemplos reais de transformação bug → user story
   - ✓ **Chain of Thought (CoT)**: 6 passos estruturados de análise
   - ✓ **Role Prompting**: Persona de Senior Product Manager
   - ✓ **Skeleton of Thought**: Estrutura clara em 5 seções de resposta
4. ✓ Documentar técnicas no `README.md` - **Documentação adicionada acima**

**Requisitos do Prompt Otimizado - Todos Atendidos:**
- ✓ **Instruções claras e específicas**: System prompt detalha passo-a-passo de análise
- ✓ **Regras explícitas de comportamento**: Seção "REGRAS OBRIGATÓRIAS" com 5 regras
- ✓ **Exemplos de entrada/saída (Few-shot)**: 3 exemplos completos inclusos
- ✓ **Tratamento de edge cases**: Seção "TRATAMENTO DE EDGE CASES" nas respostas esperadas
- ✓ **System vs User Prompt adequadamente**:
  - System Prompt: Define role, regras, passo-a-passo, exemplos
  - User Prompt: Input do usuário + estrutura esperada da respota

**Estrutura do Prompt Otimizado:**
```yaml
bug_to_user_story_v2:
  system_prompt: "Role (Senior PM) + Regras + Passo-a-passo + 3 Exemplos"
  user_prompt: "Input do bug + Estrutura esperada (Skeleton of Thought)"
  metadata: "Técnicas, autor, métricas esperadas"
```

---

### 3. Push e Avaliação

✅ **FASE 3 COMPLETADA - Push Automático com Sucesso!**

**O que foi feito:**

1. ✅ Script `src/push_prompts.py` implementado com sucesso
   - ✓ Lê prompts otimizados de `prompts/bug_to_user_story_v2.yml`
   - ✓ Valida estrutura do prompt
   - ✓ Cria ChatPromptTemplate do LangChain
   - ✓ Faz push automático para LangSmith Hub
   - ✓ Adiciona metadados (tags, descrição, técnicas)

2. ✅ Prompt publicado com sucesso no LangSmith Hub
   - ✓ Handle criado: `eloiza-souza`
   - ✓ Prompt: `bug_to_user_story_v2`
   - ✓ URL: https://smith.langchain.com/hub/eloiza-souza/bug_to_user_story_v2
   - ✓ Status: PUBLIC

**Como executar o push:**

```bash
# Push automático (agora funciona perfeitamente!)
python src/push_prompts.py
```

**Próxima etapa: Fase 4 - Avaliação**

Agora que o prompt está publicado, execute a avaliação:
```bash
python src/evaluate.py
```

---

### 4. Iteração

- Espera-se 3-5 iterações.
- Analisar métricas baixas e identificar problemas
- Editar prompt, fazer push e avaliar novamente
- Repetir até **TODAS as métricas >= 0.9**

### Critério de Aprovação:

```
- Tone Score >= 0.9
- Acceptance Criteria Score >= 0.9
- User Story Format Score >= 0.9
- Completeness Score >= 0.9

MÉDIA das 4 métricas >= 0.9
```

**IMPORTANTE:** TODAS as 4 métricas devem estar >= 0.9, não apenas a média!

### 5. Testes de Validação

**O que você deve fazer:** Edite o arquivo `tests/test_prompts.py` e implemente, no mínimo, os 6 testes abaixo usando `pytest`:

- `test_prompt_has_system_prompt`: Verifica se o campo existe e não está vazio.
- `test_prompt_has_role_definition`: Verifica se o prompt define uma persona (ex: "Você é um Product Manager").
- `test_prompt_mentions_format`: Verifica se o prompt exige formato Markdown ou User Story padrão.
- `test_prompt_has_few_shot_examples`: Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot).
- `test_prompt_no_todos`: Garante que você não esqueceu nenhum `[TODO]` no texto.
- `test_minimum_techniques`: Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas.

**Como validar:**

```bash
pytest tests/test_prompts.py
```

---

## Estrutura obrigatória do projeto

Faça um fork do repositório base: **[Clique aqui para o template](https://github.com/devfullcycle/mba-ia-pull-evaluation-prompt)**

```
desafio-prompt-engineer/
├── .env.example              # Template das variáveis de ambiente
├── requirements.txt          # Dependências Python
├── README.md                 # Sua documentação do processo
│
├── prompts/
│   ├── bug_to_user_story_v1.yml       # Prompt inicial (após pull)
│   └── bug_to_user_story_v2.yml # Seu prompt otimizado
│
├── src/
│   ├── pull_prompts.py       # Pull do LangSmith
│   ├── push_prompts.py       # Push ao LangSmith
│   ├── evaluate.py           # Avaliação automática
│   ├── metrics.py            # 4 métricas implementadas
│   ├── dataset.py            # 15 exemplos de bugs
│   └── utils.py              # Funções auxiliares
│
├── tests/
│   └── test_prompts.py       # Testes de validação
│
```

**O que você vai criar:**

- `prompts/bug_to_user_story_v2.yml` - Seu prompt otimizado
- `tests/test_prompts.py` - Seus testes de validação
- `src/pull_prompt.py` Script de pull do repositório da fullcycle
- `src/push_prompt.py` Script de push para o seu repositório
- `README.md` - Documentação do seu processo de otimização

**O que já vem pronto:**

- Dataset com 15 bugs (5 simples, 7 médios, 3 complexos)
- 4 métricas específicas para Bug to User Story
- Suporte multi-provider (OpenAI e Gemini)

## Repositórios úteis

- [Repositório boilerplate do desafio](https://github.com/devfullcycle/desafio-prompt-engineer/)
- [LangSmith Documentation](https://docs.smith.langchain.com/)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)

## VirtualEnv para Python

Crie e ative um ambiente virtual antes de instalar dependências:

```bash
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## Como Executar

### Pré-requisitos

1. **Python 3.9+** instalado
2. **Git** para versionamento
3. **API Keys configuradas:**
   - OpenAI API Key (para gpt-4o-mini e gpt-4o)
   - LangSmith API Key (para Pull/Push/Avaliação)

### Dependências

Instale as dependências do projeto:

```bash
# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instalar pacotes
pip install -r requirements.txt
```

### Configuração do Ambiente

1. Copie o arquivo `.env.example` para `.env`:
   ```bash
   cp .env.example .env
   ```

2. Preencha as variáveis no `.env`:
   ```bash
   # LangSmith
   LANGSMITH_API_KEY=lsv2_pt_xxxxx
   LANGSMITH_PROJECT="Seu projeto"
   USERNAME_LANGSMITH_HUB=seu-username
   
   # OpenAI
   OPENAI_API_KEY=sk-proj-xxxxx
   LLM_PROVIDER=openai
   LLM_MODEL=gpt-4o-mini
   EVAL_MODEL=gpt-4o
   ```

### Fase 1: Pull dos Prompts Iniciais

Puxe os prompts de baixa qualidade do LangSmith Hub:

```bash
python src/pull_prompts.py
```

**Resultado esperado:**
- Arquivo `prompts/bug_to_user_story_v1.yml` criado
- Containendo o prompt original com baixa qualidade

### Fase 2: Otimizar Prompts

Edite o arquivo `prompts/bug_to_user_story_v2.yml` aplicando técnicas de Prompt Engineering:

```bash
# (Editor: nano, vim, VS Code, etc)
nano prompts/bug_to_user_story_v2.yml
```

**Técnicas a aplicar (mínimo 2):**
- Few-shot Learning (exemplos claros)
- Chain of Thought (raciocínio passo a passo)
- Role Prompting (definir persona)
- Skeleton of Thought (estrutura clara)

### Fase 3: Testar Validações

Execute os testes de validação do prompt:

```bash
pytest tests/test_prompts.py -v
```

**6 testes executados:**
- ✓ System prompt existe
- ✓ Persona/role definida
- ✓ Formato de User Story mencionado
- ✓ Exemplos Few-shot inclusos
- ✓ Nenhum [TODO] pendente
- ✓ Mínimo 2 técnicas listadas

### Fase 4: Push para LangSmith

Publique o prompt otimizado no LangSmith Hub:

```bash
python src/push_prompts.py
```

**Resultado esperado:**
- Prompt publicado em: `https://smith.langchain.com/hub/{seu-username}/bug_to_user_story_v2`
- Dataset criado no LangSmith

### Fase 5: Executar Avaliação

Avalie a qualidade do prompt otimizado:

```bash
python src/evaluate.py
```

**Métricas calculadas:**
- F1-Score (balanceamento entre precision e recall)
- Clarity (estrutura e clareza)
- Precision (informações corretas e relevantes)
- Helpfulness (média de Clarity + Precision)
- Correctness (média de F1 + Precision)

**Critério de aprovação:** Todas as métricas >= 0.9

### Iteração (se necessário)

Se alguma métrica estiver abaixo de 0.9:

1. Analise os erros no tracing da LangSmith
2. Edite `prompts/bug_to_user_story_v2.yml` com melhorias
3. Execute push novamente: `python src/push_prompts.py`
4. Avalie: `python src/evaluate.py`
5. Repita até atingir 0.9 em todas as métricas

---

## Resultados Finais

### Dashboard LangSmith

**Prompt Publicado:** [eloiza-souza/bug_to_user_story_v2](https://smith.langchain.com/hub/eloiza-souza/bug_to_user_story_v2)

### Métricas Obtidas

#### Avaliação v2 (Prompt Otimizado)

| Métrica           | Score | Limiar | Status |
|-------------------|-------|--------|--------|
| F1-Score          | 0.77  | 0.90   | ⚠️ -0.13 |
| Clarity           | 0.88  | 0.90   | ⚠️ -0.02 |
| Precision         | 0.89  | 0.90   | ⚠️ -0.01 |
| Helpfulness       | 0.89  | 0.90   | ⚠️ -0.01 |
| Correctness       | 0.83  | 0.90   | ⚠️ -0.07 |

### Comparação: v1 vs v2

| Aspecto               | v1 Original | v2 Otimizado | Melhoria |
|----------------------|-----------|------------|----------|
| **F1-Score médio**   | ~0.62     | 0.77       | +0.15 (+24%) |
| **Clarity médio**    | ~0.68     | 0.88       | +0.20 (+29%) |
| **Precision médio**  | ~0.70     | 0.89       | +0.19 (+27%) |
| **Estrutura**        | Genérica  | 5 seções   | ✅ Estruturada |
| **Exemplos**         | 0         | 3          | ✅ Few-shot |
| **Raciocínio**       | Implícito | 6 passos   | ✅ Explícito |
| **Persona**          | Indefinida| Senior PM  | ✅ Definida |

### Análise

**Pontos Fortes da v2:**
- ✅ Melhoria significativa em todas as métricas (24-29%)
- ✅ Estrutura clara e bem definida
- ✅ Persona de Senior Product Manager bem estabelecida
- ✅ 3 exemplos reais de transformação bug→user story
- ✅ 6 passos estruturados de análise (Chain of Thought)

**Próximos Passos:**
A v2 atingiu ~0.85-0.89 em média. Para atingir 0.90+:
- Aumentar completude (F1-Score: adicionar validação de cobertura)
- Reforçar estrutura obrigatória (Clarity: validar 5 seções)
- Restringir escopo (Precision: apenas informações derivadas do bug)

### Testes de Validação

✅ **Todos os 6 testes passando:**
```
tests/test_prompts.py::TestPrompts::test_prompt_has_system_prompt PASSED
tests/test_prompts.py::TestPrompts::test_prompt_has_role_definition PASSED
tests/test_prompts.py::TestPrompts::test_prompt_mentions_format PASSED
tests/test_prompts.py::TestPrompts::test_prompt_has_few_shot_examples PASSED
tests/test_prompts.py::TestPrompts::test_prompt_no_todos PASSED
tests/test_prompts.py::TestPrompts::test_minimum_techniques PASSED
```

---

## Entregável

1. **Repositório público no GitHub** (fork do repositório base) contendo:

   - Todo o código-fonte implementado
   - Arquivo `prompts/bug_to_user_story_v2.yml` 100% preenchido e funcional
   - Arquivo `README.md` atualizado com:

2. **README.md deve conter:**

   A) **Seção "Técnicas Aplicadas (Fase 2)"**:

   - Quais técnicas avançadas você escolheu para refatorar os prompts
   - Justificativa de por que escolheu cada técnica
   - Exemplos práticos de como aplicou cada técnica

   B) **Seção "Resultados Finais"**:

   - Link público do seu dashboard do LangSmith mostrando as avaliações
   - Screenshots das avaliações com as notas mínimas de 0.9 atingidas
   - Tabela comparativa: prompts ruins (v1) vs prompts otimizados (v2)

   C) **Seção "Como Executar"**:

   - Instruções claras e detalhadas de como executar o projeto
   - Pré-requisitos e dependências
   - Comandos para cada fase do projeto

3. **Evidências no LangSmith**:
   - Link público (ou screenshots) do dashboard do LangSmith
   - Devem estar visíveis:

     - Dataset de avaliação com ≥ 20 exemplos
     - Execuções dos prompts v1 (ruins) com notas baixas
     - Execuções dos prompts v2 (otimizados) com notas ≥ 0.9
     - Tracing detalhado de pelo menos 3 exemplos

---

## Dicas Finais

- **Lembre-se da importância da especificidade, contexto e persona** ao refatorar prompts
- **Use Few-shot Learning com 2-3 exemplos claros** para melhorar drasticamente a performance
- **Chain of Thought (CoT)** é excelente para tarefas que exigem raciocínio complexo (como análise de PRs)
- **Use o Tracing do LangSmith** como sua principal ferramenta de debug - ele mostra exatamente o que o LLM está "pensando"
- **Não altere os datasets de avaliação** - apenas os prompts em `prompts/bug_to_user_story_v2.yml`
- **Itere, itere, itere** - é normal precisar de 3-5 iterações para atingir 0.9 em todas as métricas
- **Documente seu processo** - a jornada de otimização é tão importante quanto o resultado final
