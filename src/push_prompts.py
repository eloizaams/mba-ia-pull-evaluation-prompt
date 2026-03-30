"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from langsmith import Client
from utils import load_yaml, check_env_vars, print_section_header

load_dotenv()


def update_repo_visibility(username: str, repo_name: str, private: bool = False) -> bool:
    """
    Atualiza a visibilidade de um repositório no LangSmith.
    
    Args:
        username: Username no LangSmith Hub
        repo_name: Nome do repositório (ex: 'bug_to_user_story_v2')
        private: False para público, True para privado
    
    Returns:
        True se sucesso, False caso contrário
    """
    try:
        client = Client()
        
        # Formato requerido: "{owner}/{repo}"
        full_repo_name = f"{username}/{repo_name}"
        
        print(f"🔄 Atualizando visibilidade de '{full_repo_name}'...")
        
        # Chamar método de atualização do repositório
        client.update_repo(
            repo_name=full_repo_name,
            private=private
        )
        
        status = "PRIVADO" if private else "PÚBLICO"
        print(f"✓ Repositório '{full_repo_name}' agora está {status}")
        print(f"📍 Acesse em: https://smith.langchain.com/hub/{full_repo_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao atualizar visibilidade: {e}")
        return False


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    try:
        from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
        from langchain_core.prompts import PromptTemplate
        
        print(f"📤 Preparando push for '{prompt_name}'...")
        
        # Extrair dados do v2
        system_prompt_text = prompt_data.get('system_prompt', '')
        user_prompt_text = prompt_data.get('user_prompt', '{bug_report}')
        description = prompt_data.get('description', '')
        metadata = prompt_data.get('metadata', {})
        input_vars = prompt_data.get('input_variables', ['bug_report'])
        
        # Validar campos críticos
        if not system_prompt_text or not user_prompt_text:
            print("❌ System prompt ou user prompt vazio")
            return False
        
        # Construir ChatPromptTemplate
        system_template = PromptTemplate(
            template=system_prompt_text,
            input_variables=input_vars
        )
        
        user_template = PromptTemplate(
            template=user_prompt_text,
            input_variables=input_vars
        )
        
        chat_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate(prompt=system_template),
            HumanMessagePromptTemplate(prompt=user_template)
        ])
        
        print("✓ ChatPromptTemplate construído")
        
        # Preparer metadados para push
        techniques = metadata.get('techniques_applied', [])
        tech_names = [t.get('name', '') for t in techniques if isinstance(t, dict)]
        
        # Username do hub
        username = os.getenv('USERNAME_LANGSMITH_HUB', 'default')
        repo_name = f"{username}/bug_to_user_story_v2"
        
        print(f"📤 Fazendo push para: {repo_name}")
        print(f"   Técnicas aplicadas: {', '.join(tech_names)}")
        print(f"   Descrição: {description[:60]}...")
        
        # Criar repo público primeiro
        client = Client()
        try:
            client.create_repo(repo_name, description=description, is_public=True)
            print("✓ Repo público criado")
        except Exception as e:
            print(f"⚠️ Repo já existe ou erro ao criar: {e}")
        
        # Fazer push do prompt
        try:
            client.push_prompt(repo_name, chat_prompt)
            final_repo = repo_name
        except Exception as inner_e:
            if "Cannot create a prompt for another tenant" in str(inner_e):
                fallback_name = prompt_name
                print(f"⚠️ Erro de tenant detectado. Tentando push para o tenant atual com '{fallback_name}'...")
                try:
                    client.create_repo(fallback_name, description=description, is_public=True)
                except:
                    pass
                client.push_prompt(fallback_name, chat_prompt)
                final_repo = fallback_name
            else:
                raise

        print(f"✓ Push completado com sucesso!")
        
        # # Atualizar visibilidade para público - removido pois is_public=True no push
        # if "/" in final_repo:
        #     owner, repo = final_repo.split("/", 1)
        # else:
        #     owner = username  # fallback case
        #     repo = final_repo
        # 
        # update_repo_visibility(owner, repo, private=False)
        
        print(f"\n📍 Acesse seu prompt em:")
        print(f"   https://smith.langchain.com/hub/{final_repo}")

        return True
        
    except Exception as e:
        print(f"❌ Erro ao fazer push: {str(e)}")
        print("\nDicas de debug:")
        print("  1. Verifique se LANGSMITH_API_KEY está correto")
        print("  2. Confirme USERNAME_LANGSMITH_HUB está definido")
        print("  3. Verifique sua conexão com a internet")
        import traceback
        traceback.print_exc()
        return False


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    errors = []
    
    # Campos obrigatórios
    required_fields = ['description', 'system_prompt', 'user_prompt', 'version', 'metadata']
    for field in required_fields:
        if field not in prompt_data:
            errors.append(f"Campo obrigatório faltando: {field}")
    
    # Validar system_prompt
    system_prompt = prompt_data.get('system_prompt', '').strip()
    if not system_prompt:
        errors.append("system_prompt está vazio")
    
    if 'TODO' in system_prompt:
        errors.append("system_prompt ainda contém TODOs")
    
    # Validar user_prompt
    user_prompt = prompt_data.get('user_prompt', '').strip()
    if not user_prompt:
        errors.append("user_prompt está vazio")
    
    # Validar técnicas aplicadas
    metadata = prompt_data.get('metadata', {})
    techniques = metadata.get('techniques_applied', [])
    if len(techniques) < 2:
        errors.append(f"Mínimo de 2 técnicas requeridas, encontradas: {len(techniques)}")
    
    return (len(errors) == 0, errors)


def main():
    """Função principal"""
    # Verificar env vars
    required_vars = ['LANGSMITH_API_KEY', 'USERNAME_LANGSMITH_HUB']
    if not check_env_vars(required_vars):
        return 1
    
    print_section_header("PUSHING OTIMIZED PROMPTS TO LANGSMITH HUB")
    
    # Ler arquivo YAML com prompts v2
    from pathlib import Path
    v2_path = str(Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml")
    
    print(f"📖 Lendo prompts otimizados de: {v2_path}")
    prompt_data = load_yaml(v2_path)
    
    if not prompt_data:
        print("❌ Falha ao carregar arquivo v2")
        return 1
    
    # Extrair dados do v2
    prompt_v2_data = prompt_data.get('bug_to_user_story_v2', {})
    
    if not prompt_v2_data:
        print("❌ Chave 'bug_to_user_story_v2' não encontrada no YAML")
        return 1
    
    print("✓ Arquivo v2 carregado")
    
    # Validar prompts
    print("\n🔍 Validando estrutura do prompt...")
    is_valid, errors = validate_prompt(prompt_v2_data)
    
    if not is_valid:
        print("❌ Validação falhou:")
        for error in errors:
            print(f"   - {error}")
        return 1
    
    print("✓ Validação bem-sucedida")
    
    # Fazer push
    success = push_prompt_to_langsmith('bug_to_user_story_v2', prompt_v2_data)
    
    if success:
        print(f"\n✅ Todos os prompts foram publicados com sucesso!")
        return 0
    else:
        print(f"\n❌ Falha ao fazer push dos prompts")
        return 1


if __name__ == "__main__":
    sys.exit(main())
