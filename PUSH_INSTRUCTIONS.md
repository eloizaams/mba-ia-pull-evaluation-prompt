# Instruções para Push do Prompt no LangSmith Hub

## Status
✅ Prompt otimizado criado e validado: `prompts/bug_to_user_story_v2.yml`  
✅ Push automático funcionando perfeitamente via Python!

## Solução Recomendada: Push via Python (Automático)

### Opção 1: Via CLI (Recomendado) ⭐

Agora que você criou seu **handle** no LangSmith, o push automático funciona perfeitamente!

```bash
python src/push_prompts.py
```

**O que acontece:**
- ✅ Carrega o prompt otimizado
- ✅ Valida a estrutura
- ✅ Cria ChatPromptTemplate
- ✅ Publica no LangSmith automaticamente
- ✅ Exibe URL pública

**Output esperado:**
```
✅ SUCESSO - Prompt publicado no LangSmith Hub!
📎 URL: https://smith.langchain.com/hub/eloiza-souza/bug_to_user_story_v2
```

### Opção 2: Interface Web (Manual)

Se preferir fazer manualmente:

1. **Abra o LangSmith Hub**
   - Visite: https://smith.langchain.com/hub
   - Faça login com sua conta

2. **Crie um novo prompt**
   - Clique em "New" ou "Create Prompt"
   - Selecione "Chat Prompt"

3. **Defina as informações básicas**

   **Nome do Prompt:**
   ```
   bug_to_user_story_v2
   ```

   **Descrição:**
   ```
   Prompt otimizado para converter relatos de bugs em User Stories de alta qualidade
   ```

   **Tags:**
   ```
   bug-analysis, user-story, optimized, few-shot, chain-of-thought, advanced-techniques
   ```

4. **Copie o System Prompt**

   Abra o arquivo `prompts/bug_to_user_story_v2.yml` e copie todo o conteúdo da seção `system_prompt`
   
   Cole na aba "System" do prompt no LangSmith

5. **Copie o User Prompt**

   Copie o conteúdo de `user_prompt` do arquivo YAML
   
   Cole na aba "Human" ou "User" do prompt no LangSmith

6. **Salve e Publique**
   - Clique em "Save" ou "Create"
   - Clique no ícone de cadeado para tornar o prompt **PÚBLICO**
   - Copie o link público gerado

---

## Estrutura do Prompt Otimizado

### System Prompt
- **Técnicas:** Few-shot Learning, Chain of Thought, Role Prompting
- **Tamanho:** ~60+ linhas
- **Inclui:** 3 exemplos completos, 6-step analysis framework, 5 regras explícitas

### User Prompt  
- **Entrada:** Bug report em texto livre
- **Estrutura esperada:** 5 seções de resposta obrigatórias
- **Variável:** `{bug_report}`

---

##Próximos Passos Após Push

1. ✅ Prompt publicado no LangSmith Hub
2. ⬜ Executar avaliação: `python src/evaluate.py`
3. ⬜ Analisar métricas (Tone, Acceptance Criteria, Format, Completeness)
4. ⬜ Iterar se alguma métrica < 0.9
5. ⬜ Documentar resultados finais

---

## URL do Seu Prompt

Após publicar, seu prompt estará em:
```
https://smith.langchain.com/hub/eloiza-souza/bug_to_user_story_v2
```

---

## Troubleshooting

### Problema: "Current tenant: None"
**Causa:** API key pessoal não configurada para criar prompts em workspace específico  
**Solução:** Use o push manual via dashboard (Opção 1)

### Problema: Nome de prompt já existe
**Solução:** Adicione um sufixo, ex: `bug_to_user_story_v2_optimized`

### Problema: Visibilidade não está pública
**Solução:** Clique no ícone de cadeado → "Make Public"

---

## Verificação Final

Após fazer push, verifique:
- [ ] Prompt está visível em https://smith.langchain.com/hub
- [ ] Sistema prompt contém todos os exemplos
- [ ] User prompt tem a estrutura esperada
- [ ] Prompt está marcado como PUBLIC
- [ ] Tags estão definidas

Então execute:
```bash
python src/evaluate.py
```

---

**Última atualização:** 24 de março de 2026  
**Status:** Pronto para push manual
