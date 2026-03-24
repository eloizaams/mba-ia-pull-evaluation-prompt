"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()


def pull_prompts_from_langsmith():
    """
    Faz pull dos prompts do LangSmith Prompt Hub.
    
    Pulls:
    - leonanluppi/bug_to_user_story_v1
    
    Returns:
        dict: Dicionário com os prompts ou None se erro
    """
    print_section_header("FAZENDO PULL DE PROMPTS DO LANGSMITH")
    
    # Verifica variáveis de ambiente obrigatórias
    required_vars = ["LANGSMITH_API_KEY"]
    if not check_env_vars(required_vars):
        return None
    
    try:
        # Pull do prompt hub
        print("📥 Puxando prompt: leonanluppi/bug_to_user_story_v1")
        prompt = hub.pull("leonanluppi/bug_to_user_story_v1")
        
        # Serializa o prompt para formato YAML
        prompt_data = serialize_prompt(prompt)
        
        if prompt_data is None:
            print("❌ Erro ao serializar prompt")
            return None
        
        print("✓ Prompt puxado com sucesso!")
        return prompt_data
        
    except Exception as e:
        print(f"❌ Erro ao fazer pull do prompt: {e}")
        return None


def serialize_prompt(prompt_obj) -> Optional[Dict[str, Any]]:
    """
    Serializa objeto do LangChain para dicionário YAML.
    
    Args:
        prompt_obj: Objeto prompt do LangChain
        
    Returns:
        dict: Dicionário com prompt serializado ou None se erro
    """
    try:
        prompt_dict = {
            "bug_to_user_story_v1": {
                "description": "Prompt original de baixa qualidade para converter bugs em User Stories",
                "version": "v1",
                "source": "leonanluppi/bug_to_user_story_v1",
                "tags": ["bug-analysis", "user-story", "product-management", "original"]
            }
        }
        
        system_prompt = None
        user_prompt = None
        
        # Trata ChatPromptTemplate (com múltiplas mensagens)
        if hasattr(prompt_obj, 'messages') and prompt_obj.messages:
            for msg in prompt_obj.messages:
                # Extrai SystemMessagePromptTemplate
                if hasattr(msg, '__class__') and 'SystemMessage' in msg.__class__.__name__:
                    if hasattr(msg, 'prompt') and hasattr(msg.prompt, 'template'):
                        system_prompt = msg.prompt.template
                # Extrai HumanMessagePromptTemplate  
                elif hasattr(msg, '__class__') and 'HumanMessage' in msg.__class__.__name__:
                    if hasattr(msg, 'prompt') and hasattr(msg.prompt, 'template'):
                        user_prompt = msg.prompt.template
        
        # Armazena os prompts extraídos
        if system_prompt:
            prompt_dict["bug_to_user_story_v1"]["system_prompt"] = system_prompt
        if user_prompt:
            prompt_dict["bug_to_user_story_v1"]["user_prompt"] = user_prompt
            
        return prompt_dict
        
    except Exception as e:
        print(f"❌ Erro ao serializar prompt: {e}")
        return None


def main():
    """Função principal"""
    try:
        # Faz pull dos prompts
        prompt_data = pull_prompts_from_langsmith()
        
        if prompt_data is None:
            print("\n❌ Falha ao fazer pull dos prompts")
            return 1
        
        # Define caminho de saída
        output_path = Path("prompts/bug_to_user_story_v1.yml")
        
        # Salva os prompts em YAML
        print(f"\n💾 Salvando prompts em {output_path}")
        if save_yaml(prompt_data, str(output_path)):
            print(f"✓ Prompts salvos com sucesso em {output_path}")
            print("\n📋 Próximas etapas:")
            print("   1. Revise o prompt em prompts/bug_to_user_story_v1.yml")
            print("   2. Crie uma versão otimizada em prompts/bug_to_user_story_v2.yml")
            print("   3. Execute: python src/push_prompts.py")
            print("   4. Execute: python src/evaluate.py")
            return 0
        else:
            print(f"❌ Erro ao salvar prompts em {output_path}")
            return 1
            
    except Exception as e:
        print(f"❌ Erro na execução principal: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
