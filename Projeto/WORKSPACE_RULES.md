# Workspace Rules & Global Guidelines

## 🔄 Project Awareness & Context
- Sempre leia `PLANNING.md` ao iniciar uma nova tarefa para entender arquitetura, objetivos e restrições.
- Consulte `TASK.md` antes de começar qualquer tarefa. Se não estiver listada, adicione com descrição e data.
- Use convenções de nomes, estrutura de arquivos e padrões de arquitetura definidos em `PLANNING.md`.

## 🧱 Code Structure & Modularity
- Nunca crie um arquivo com mais de 500 linhas de código. Se aproximar desse limite, refatore dividindo em módulos ou helpers.
- Organize o código em módulos separados por feature ou responsabilidade.
- Prefira imports relativos dentro de pacotes.

## 🧪 Testing & Reliability
- Sempre crie testes unitários Pytest para novas features (funções, classes, rotas, etc).
- Após atualizar lógica, verifique se testes existentes precisam ser atualizados.
- Os testes devem ficar na pasta `/tests`, espelhando a estrutura principal.
- Inclua ao menos:
  - 1 teste de uso esperado
  - 1 caso de edge
  - 1 caso de falha

## ✅ Task Completion
- Marque tarefas concluídas no `TASK.md` imediatamente após finalizar.
- Adicione novos sub-tasks ou TODOs descobertos durante o trabalho em “Discovered During Work” no `TASK.md`.

## 📎 Style & Conventions
- Use Python como linguagem principal.
- Siga PEP8, use type hints e formate com `black`.
- Use `pydantic` para validação de dados.
- Use `FastAPI` para APIs e `SQLAlchemy` ou `SQLModel` para ORM se aplicável.
- Escreva docstrings para toda função, usando o padrão Google:
```python
def exemplo():
    """
    Resumo breve.
    Args:
        param1 (tipo): Descrição.
    Returns:
        tipo: Descrição.
    """
```

## 📚 Documentation & Explainability
- Atualize o `README.md` ao adicionar features, mudar dependências ou setup.
- Comente código não óbvio e garanta que tudo seja compreensível para um dev intermediário.
- Ao escrever lógica complexa, adicione comentários inline `# Reason:` explicando o porquê, não só o quê.

## 🧠 AI Behavior Rules
- Nunca assuma contexto ausente. Pergunte se incerto.
- Nunca invente bibliotecas ou funções – use apenas pacotes Python conhecidos e verificados.
- Confirme sempre se caminhos de arquivos e módulos existem antes de referenciar.
- Nunca delete ou sobrescreva código existente sem instrução explícita ou se for parte de uma tarefa do `TASK.md`.

---

Essas regras garantem qualidade, clareza e evolução sustentável do projeto. Sempre consulte este arquivo durante o desenvolvimento.
