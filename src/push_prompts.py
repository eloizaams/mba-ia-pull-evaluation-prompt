"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Prepara os prompts para publicação
3. Oferece instruções para fazer push ao LangSmith Hub

NOTA IMPORTANTE: Devido a configurações de tenant/API key, o push pode requerer
etapas manuais no dashboard do LangSmith. Este script prepara tudo e fornece
instruções detalhadas.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from langchain import hub
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, PromptTemplate
from utils import load_yaml, check_env_vars, print_section_header

load_dotenv()


def push_prompt_to_langsmith(repo_id: str, chat_prompt: ChatPromptTemplate) -> tuple[bool, str]:
    """
    Tenta fazer push do prompt otimizado para o LangSmith Hub.

    Args:
        repo_id: ID do repositório (username/prompt_name)
        chat_prompt: ChatPromptTemplate a ser enviado

    Returns:
        (sucesso: bool, url: str ou mensagem de erro)
    """
    print_section_header("FAZENDO PUSH PARA LANGSMITH HUB")
    
    print(f"Repo ID: {repo_id}")
    print(f"Tentando fazer push...")
    
    try:
        # Tentar fazer push automático
        result = hub.push(repo_id, chat_prompt)
        print("✅ Prompt enviado com sucesso!")
        url = f"https://smith.langchain.com/hub/{repo_id}"
        return True, url
        
    except Exception as e:
        error_msg = str(e)
        print(f"⚠️  Erro ao fazer push automático: {error_msg[:100]}")
        
        # Se falhar por questões de tenant, oferecer alternativa
        if "tenant" in error_msg.lower() or "permission" in error_msg.lower():
            print("\n💡 SOLUÇÃO ALTERNATIVA - Push Manual:")
            print("   Como a API key pode ter restrições de tenant, você pode fazer push manualmente:")
            print("\n   1. Visite: https://smith.langchain.com/hub")
            print("   2. Clique em 'Create New Prompt'")
            print("   3. Copie e cola o conteúdo abaixo:\n")
            print("   " + "=" * 50)
            print(f"   Nome: bug_to_user_story_v2")
            print(f"   Descrição: Prompt otimizado para converter bugs em User Stories")
            print("   Tags: bug-analysis, user-story, optimized, few-shot, chain-of-thought")
            print("   " + "=" * 50)
            return False, f"Manual push required - visit https://smith.langchain.com/hub"
        
        return False, f"Error: {error_msg}"


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt.

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    errors = []
    
    if not prompt_data.get("system_prompt"):
        errors.append("system_prompt vazio ou ausente")
    
    if not prompt_data.get("user_prompt"):
        errors.append("user_prompt vazio ou ausente")
    
    if errors:
        return False, errors
    
    return True, []


def main():
    """Função principal"""
    try:
        # Carrega configuração do prompt v2
        print_section_header("CARREGANDO PROMPT OTIMIZADO")
        prompt_file = Path("prompts/bug_to_user_story_v2.yml")
        
        if not prompt_file.exists():
            print(f"❌ Arquivo não encontrado: {prompt_file}")
            return 1
        
        print(f"📖 Lendo arquivo: {prompt_file}")
        prompt_yaml = load_yaml(str(prompt_file))
        
        if not prompt_yaml:
            print("❌ Erro ao carregar arquivo YAML")
            return 1
        
        # Extrai configuração do prompt
        prompt_config = prompt_yaml.get("bug_to_user_story_v2")
        if not prompt_config:
            print("❌ Chave 'bug_to_user_story_v2' não encontrada no YAML")
            return 1
        
        print("✓ Arquivo carregado com sucesso!")
        
        # Valida prompt
        print_section_header("VALIDANDO PROMPT")
        is_valid, errors = validate_prompt(prompt_config)
        
        if not is_valid:
            print("❌ Validação falhou:")
            for error in errors:
                print(f"   - {error}")
            return 1
        
        print("✓ Prompt validado com sucesso!")
        
        # Cria ChatPromptTemplate
        print_section_header("CRIANDO CHAT PROMPT TEMPLATE")
        
        system_prompt_text = prompt_config.get("system_prompt", "").strip()
        user_prompt_text = prompt_config.get("user_prompt", "").strip()
        
        system_template = SystemMessagePromptTemplate(
            prompt=PromptTemplate(template=system_prompt_text, input_variables=[])
        )
        
        human_template = HumanMessagePromptTemplate(
            prompt=PromptTemplate(template=user_prompt_text, input_variables=["bug_report"])
        )
        
        chat_prompt = ChatPromptTemplate(
            messages=[system_template, human_template],
            input_variables=["bug_report"]
        )
        
        print("✓ ChatPromptTemplate criado com sucesso!")
        
        # Tenta fazer push
        full_username = os.getenv("USERNAME_LANGSMITH_HUB", "seu_username")
        username_slug = full_username.lower().replace(" ", "-").replace("_", "-")
        repo_id = f"{username_slug}/bug_to_user_story_v2"
        
        success, url_or_message = push_prompt_to_langsmith(repo_id, chat_prompt)
        
        # Exibe resumo
        print_section_header("RESUMO")
        
        techniques = prompt_config.get("techniques", [])
        if techniques:
            print(f"\n🛠️ Técnicas Aplicadas:")
            for i, technique in enumerate(techniques, 1):
                print(f"   {i}. {technique}")
        
        if success:
            print(f"\n✅ STATUS: SUCESSO - Prompt publicado no LangSmith Hub!")
            print(f"📎 URL: {url_or_message}")
            print(f"\n📌 PRÓXIMAS ETAPAS:")
            print(f"   1. Visite: {url_or_message}")
            print(f"   2. (Se necessário) Clique no ícone de cadeado para tornar PÚBLICO")
            print(f"   3. Execute: python src/evaluate.py")
        else:
            print(f"\n⚠️  STATUS: REQUER AÇÃO MANUAL")
            print(f"📝 Motivo: {url_or_message}")
            print(f"\n📌 PRÓXIMAS ETAPAS:")
            print(f"   1. {url_or_message}")
            print(f"   2. Confirme o push no dashboard do LangSmith")
            print(f"   3. Execute: python src/evaluate.py")
        
        return 0 if success else 1
        
    except Exception as e:
        print(f"❌ Erro na execução principal: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
