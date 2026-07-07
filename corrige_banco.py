import sqlite3
import os

db_name = 'motorcontrol.bd' if os.path.exists('motorcontrol.bd') else 'database.db'

try:
    conn = sqlite3.connect(db_name)
    conn.execute('ALTER TABLE orcamento ADD COLUMN valor_rebobinamento FLOAT DEFAULT 0.0;')
    conn.commit()
    conn.close()
    print('? Banco corrigido com sucesso! A coluna foi criada.')
except Exception as e:
    print(f'?? Aviso: {e}')
