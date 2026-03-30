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
    @pytest.fixture
    def prompt_v2_data(self):
        """Carrega dados do prompt v2 para testes."""
        prompt_file = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"
        data = load_prompts(str(prompt_file))
        return data['bug_to_user_story_v2']

    def test_prompt_has_system_prompt(self, prompt_v2_data):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert 'system_prompt' in prompt_v2_data
        assert prompt_v2_data['system_prompt'].strip() != ""

    def test_prompt_has_role_definition(self, prompt_v2_data):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        system_prompt = prompt_v2_data['system_prompt']
        assert "Product Manager" in system_prompt
        assert "experiente" in system_prompt

    def test_prompt_mentions_format(self, prompt_v2_data):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        system_prompt = prompt_v2_data['system_prompt']
        assert "## User Story" in system_prompt
        assert "## Critérios de Aceitação" in system_prompt
        assert "FORMATO OBRIGATÓRIO" in system_prompt

    def test_prompt_has_few_shot_examples(self, prompt_v2_data):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        system_prompt = prompt_v2_data['system_prompt']
        assert "EXEMPLOS:" in system_prompt
        assert "Bug: Botão de adicionar" in system_prompt
        assert "Bug: API retorna" in system_prompt

    def test_prompt_no_todos(self, prompt_v2_data):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        system_prompt = prompt_v2_data['system_prompt']
        user_prompt = prompt_v2_data.get('user_prompt', '')
        assert "[TODO]" not in system_prompt
        assert "[TODO]" not in user_prompt

    def test_minimum_techniques(self, prompt_v2_data):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        techniques = prompt_v2_data.get('metadata', {}).get('techniques_applied', [])
        assert len(techniques) >= 2
        technique_names = [t['name'] for t in techniques]
        expected_techniques = ["Few-shot Learning", "Chain of Thought (CoT)", "Role Prompting", "Skeleton of Thought"]
        for expected in expected_techniques:
            assert expected in technique_names

    def test_prompt_structure_validation(self, prompt_v2_data):
        """Testa validação completa da estrutura do prompt."""
        is_valid, errors = validate_prompt_structure(prompt_v2_data)
        assert is_valid, f"Erros de validação: {errors}"

    def test_prompt_has_version(self, prompt_v2_data):
        """Verifica se o prompt tem versão definida."""
        assert 'version' in prompt_v2_data
        assert prompt_v2_data['version'] == "v2"

    def test_prompt_has_description(self, prompt_v2_data):
        """Verifica se o prompt tem descrição."""
        assert 'description' in prompt_v2_data
        assert "otimizado" in prompt_v2_data['description']

    def test_prompt_has_input_variables(self, prompt_v2_data):
        """Verifica se o prompt define variáveis de entrada."""
        assert 'input_variables' in prompt_v2_data
        assert 'bug_report' in prompt_v2_data['input_variables']

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])