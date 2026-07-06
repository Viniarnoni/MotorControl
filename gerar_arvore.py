import os
from pathlib import Path

# Configuração de ícones por extensão ou tipo
ICONS = {
    "dir": "📁",
    "dir_open": "📂",
    "py": "🐍",
    "tsx": "⚛️",
    "ts": "📘",
    "json": "⚙️",
    "yml": "🐳",
    "yaml": "🐳",
    "ini": "⚙️",
    "md": "📝",
    "txt": "📄",
    "default": "📄"
}

# Pastas que devemos ignorar para não poluir a árvore
IGNORE_DIRS = {"venv", "__pycache__", "node_modules", ".git", ".vite"}

def generate_tree(dir_path: Path, prefix: str = "") -> list:
    tree = []
    
    # Lista e ordena os itens (pastas primeiro, depois arquivos)
    try:
        items = sorted(
            [item for item in dir_path.iterdir() if item.name not in IGNORE_DIRS],
            key=lambda x: (not x.is_dir(), x.name.lower())
        )
    except PermissionError:
        return tree

    count = len(items)
    for i, item in enumerate(items):
        is_last = (i == count - 1)
        connector = "└── " if is_last else "├── "
        
        # Define o ícone correto
        if item.is_dir():
            icon = ICONS["dir"]
        else:
            ext = item.suffix.lower().replace(".", "")
            icon = ICONS.get(ext, ICONS["default"])
            
            # Ícone especial para docker
            if "docker" in item.name.lower():
                icon = ICONS["yml"]

        # Adiciona a linha atual
        tree.append(f"{prefix}{connector}{icon} {item.name}")
        
        # Se for pasta, avança recursivamente
        if item.is_dir():
            next_prefix = prefix + ("    " if is_last else "│   ")
            tree.extend(generate_tree(item, next_prefix))
            
    return tree

if __name__ == "__main__":
    # Define o caminho para a raiz do seu projeto
    root_path = Path(__file__).parent.resolve()
    arquivo_saida = root_path / "estrutura_projeto.txt"
    
    cabecalho = f"🌲 ESTRUTURA DO PROJETO: {root_path.name} 🌲\n\n📂 {root_path.name}\n"
    
    print(cabecalho)
    linhas_arvore = generate_tree(root_path)
    
    # Salva no arquivo e imprime na tela ao mesmo tempo
    with open(arquivo_saida, "w", encoding="utf-8") as f:
        f.write(cabecalho)
        for linha in linhas_arvore:
            print(linha)
            f.write(linha + "\n")
            
    print("\n" + "="*50)
    print(f"✅ Pronto! A estrutura foi salva no arquivo: {arquivo_saida.name}")
