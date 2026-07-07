import sqlite3

# Coloque o nome exato do seu arquivo de banco de dados aqui
NOME_DO_BANCO = "motorcontrol.bd" 

try:
    conn = sqlite3.connect(NOME_DO_BANCO)
    cursor = conn.cursor()
    # Força a criação da coluna sem apagar a tabela
    cursor.execute("ALTER TABLE orcamento ADD COLUMN valor_rebobinamento FLOAT DEFAULT 0.0;")
    conn.commit()
    print("✅ Coluna 'valor_rebobinamento' injetada com sucesso! Pode rodar o Flet.")
except sqlite3.OperationalError as e:
    print(f"⚠️ Aviso: {e} (Talvez a coluna já exista ou o nome do banco esteja errado no script)")
finally:
    conn.close()
