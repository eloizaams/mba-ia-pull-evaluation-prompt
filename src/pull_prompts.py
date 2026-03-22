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
from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()


def pull_prompts_from_langsmith():
    """
    Faz pull do prompt do LangSmith Hub e salva localmente.
    
    Returns:
        bool: True se sucesso, False se erro
    """
    # Verificar env vars obrigatórias
    required_vars = ['LANGSMITH_API_KEY', 'OPENAI_API_KEY']
    if not check_env_vars(required_vars):
        return False
    
    print_section_header("PULLING PROMPTS DO LANGSMITH HUB")
    
    try:
        print("📥 Puxando prompt 'leonanluppi/bug_to_user_story_v1' do hub...")
        
        # Fazer pull do prompt do hub
        prompt = hub.pull("leonanluppi/bug_to_user_story_v1")
        
        print("✓ Prompt recuperado com sucesso")
        
        # Extrair dados do PromptTemplate/ChatPromptTemplate
        system_prompt_text = ""
        input_vars = []
        
        # Se for ChatPromptTemplate, extrair messages
        if hasattr(prompt, 'messages'):
            # Formato ChatPromptTemplate com SystemMessage e HumanMessage
            for msg in prompt.messages:
                if hasattr(msg, 'prompt') and hasattr(msg.prompt, 'template'):
                    # SystemMessagePromptTemplate
                    template = msg.prompt.template
                    if "assistente" in template.lower() or "você é" in template.lower():
                        system_prompt_text = template
                
                if hasattr(msg, 'prompt'):
                    if hasattr(msg.prompt, 'input_variables'):
                        input_vars = msg.prompt.input_variables
        
        # Se não achou, tentar extrair diretamente
        if not system_prompt_text and hasattr(prompt, 'template'):
            system_prompt_text = prompt.template
        
        if hasattr(prompt, 'input_variables'):
            input_vars = prompt.input_variables
        
        # Estruturar dados no formato esperado
        prompt_data = {
            "bug_to_user_story_v1": {
                "description": "Prompt para converter relatos de bugs em User Stories",
                "system_prompt": system_prompt_text,
                "user_prompt": "{bug_report}",
                "version": "v1",
                "created_at": "2025-01-15",
                "tags": ["bug-analysis", "user-story", "product-management"],
                "input_variables": input_vars
            }
        }
        
        # Salvar em YAML local
        output_path = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v1.yml"
        
        if save_yaml(prompt_data, str(output_path)):
            print(f"✓ Prompt salvo em: {output_path}")
            print(f"\n📊 Resumo:")
            print(f"   - Input variables: {input_vars}")
            print(f"   - Comprimento do template: {len(system_prompt_text)} caracteres")
            print(f"\n✅ Pull completado com sucesso!")
            return True
        else:
            print("❌ Falha ao salvar arquivo YAML")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao fazer pull do prompt: {str(e)}")
        print("\nDicas de debug:")
        print("  1. Verifique se LANGSMITH_API_KEY está correto")
        print("  2. Confirme que o prompt 'leonanluppi/bug_to_user_story_v1' existe")
        print("  3. Verifique sua conexão com a internet")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Função principal"""
    success = pull_prompts_from_langsmith()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
