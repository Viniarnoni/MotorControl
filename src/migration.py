import sqlite3
from src.core.paths import get_database_path

def migrate_db():
    conn = sqlite3.connect(get_database_path())
    cursor = conn.cursor()
    
    queries = [
        "ALTER TABLE cliente ADD COLUMN gov_id VARCHAR",
        "ALTER TABLE cliente ADD COLUMN email VARCHAR",
        "ALTER TABLE cliente ADD COLUMN numero VARCHAR",
        "ALTER TABLE cliente ADD COLUMN bairro VARCHAR",
        "ALTER TABLE cliente ADD COLUMN cidade VARCHAR",
        "ALTER TABLE cliente ADD COLUMN estado VARCHAR",
        "ALTER TABLE motor ADD COLUMN cliente_id INTEGER REFERENCES cliente(id)",
        "ALTER TABLE motor ADD COLUMN serial_number VARCHAR DEFAULT 'S/N'",
        "ALTER TABLE motor ADD COLUMN hp_kw FLOAT DEFAULT 0.0",
        "ALTER TABLE motor ADD COLUMN power_unit VARCHAR DEFAULT 'CV'",
        "ALTER TABLE motor ADD COLUMN voltage VARCHAR DEFAULT '220V'",
        "ALTER TABLE motor ADD COLUMN current FLOAT",
        "ALTER TABLE motor ADD COLUMN insulation_class VARCHAR",
        "ALTER TABLE orcamento ADD COLUMN valor_rebobinamento FLOAT DEFAULT 0.0",
        "ALTER TABLE orcamento ADD COLUMN descricao_mao_de_obra VARCHAR",
        "ALTER TABLE orcamento ADD COLUMN valor_mao_de_obra FLOAT DEFAULT 0.0",
        "ALTER TABLE orcamento ADD COLUMN valor_pecas FLOAT DEFAULT 0.0",
        "ALTER TABLE orcamento ADD COLUMN valor_total FLOAT DEFAULT 0.0",
        "ALTER TABLE orcamento ADD COLUMN observacoes VARCHAR",
        "ALTER TABLE orcamento ADD COLUMN status VARCHAR DEFAULT 'Pendente'",
        "ALTER TABLE orcamento ADD COLUMN desconto FLOAT DEFAULT 0.0",
        "ALTER TABLE orcamento ADD COLUMN test_voltage FLOAT",
        "ALTER TABLE orcamento ADD COLUMN test_current FLOAT",
        "ALTER TABLE orcamento ADD COLUMN test_insulation FLOAT"
    ]
    
    for q in queries:
        try:
            cursor.execute(q)
        except Exception:
            # Coluna já existe — migração idempotente
            pass
            
    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate_db()
