import sqlite3

def migrate_db():
    conn = sqlite3.connect("motorcontrol.db")
    cursor = conn.cursor()
    
    queries = [
        "ALTER TABLE cliente ADD COLUMN gov_id VARCHAR DEFAULT '000.000.000-00'",
        "ALTER TABLE cliente ADD COLUMN email VARCHAR",
        "ALTER TABLE motor ADD COLUMN cliente_id INTEGER REFERENCES cliente(id)",
        "ALTER TABLE motor ADD COLUMN serial_number VARCHAR DEFAULT 'S/N'",
        "ALTER TABLE motor ADD COLUMN hp_kw FLOAT DEFAULT 0.0",
        "ALTER TABLE motor ADD COLUMN power_unit VARCHAR DEFAULT 'CV'",
        "ALTER TABLE motor ADD COLUMN voltage VARCHAR DEFAULT '220V'",
        "ALTER TABLE motor ADD COLUMN current FLOAT",
        "ALTER TABLE motor ADD COLUMN insulation_class VARCHAR",
        "ALTER TABLE orcamento ADD COLUMN desconto FLOAT DEFAULT 0.0",
        "ALTER TABLE orcamento ADD COLUMN test_voltage FLOAT",
        "ALTER TABLE orcamento ADD COLUMN test_current FLOAT",
        "ALTER TABLE orcamento ADD COLUMN test_insulation FLOAT"
    ]
    
    for q in queries:
        try:
            cursor.execute(q)
            print(f"Sucesso: {q}")
        except Exception as e:
            print(f"Erro ignorado (possivelmente a coluna já existe): {e} na query {q}")
            
    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate_db()
