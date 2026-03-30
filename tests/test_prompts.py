"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

class TestPrompts:
    @pytest.fixture(autouse=True)
    def setup(self):
        """Carrega os prompts antes de cada teste."""
        self.prompts = load_prompts("prompts/bug_to_user_story_v2.yml")
        self.prompt_v2 = self.prompts.get("bug_to_user_story_v2", {})

    def test_prompt_has_system_prompt(self):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert "system_prompt" in self.prompt_v2, "Campo 'system_prompt' não encontrado"
        assert self.prompt_v2["system_prompt"], "Campo 'system_prompt' está vazio"
        assert len(self.prompt_v2["system_prompt"]) > 100, "System prompt muito curto"

    def test_prompt_has_role_definition(self):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        system_prompt = self.prompt_v2.get("system_prompt", "").lower()
        
        role_keywords = ["você é", "sou", "expert", "especializado", "manager", "product", "profissional"]
        found_role = any(keyword in system_prompt for keyword in role_keywords)
        
        assert found_role, "Nenhuma definição de persona/role encontrada no system_prompt"

    def test_prompt_mentions_format(self):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        system_prompt = self.prompt_v2.get("system_prompt", "").lower()
        user_prompt = self.prompt_v2.get("user_prompt", "").lower()
        
        prompt_text = system_prompt + user_prompt
        
        format_keywords = ["como", "eu quero", "para que", "given", "when", "then", "formato", "user story"]
        found_format = any(keyword in prompt_text for keyword in format_keywords)
        
        assert found_format, "Formato de User Story (Como... Eu quero... Para que...) não mencionado"

    def test_prompt_has_few_shot_examples(self):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        system_prompt = self.prompt_v2.get("system_prompt", "")
        
        # Procura por padrões que indicam exemplos
        example_markers = ["EXEMPLO", "exemplo", "Bug Report", "User Story", "Critério", "Aceitação"]
        found_examples = sum(1 for marker in example_markers if marker in system_prompt)
        
        assert found_examples >= 3, f"Menos de 3 exemplos encontrados (encontrado {found_examples})"

    def test_prompt_no_todos(self):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        system_prompt = self.prompt_v2.get("system_prompt", "")
        user_prompt = self.prompt_v2.get("user_prompt", "")
        
        prompt_text = system_prompt + user_prompt
        
        assert "[TODO]" not in prompt_text.upper(), "Encontrado [TODO] não preenchido no prompt"

    def test_minimum_techniques(self):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        techniques = self.prompt_v2.get("techniques", [])
        
        assert isinstance(techniques, list), "Campo 'techniques' não é uma lista"
        assert len(techniques) >= 2, f"Menos de 2 técnicas listadas (encontrado {len(techniques)})"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])