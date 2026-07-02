import sqlite3
import os
from src.models.cliente_entity import Cliente

class ClienteRepository:
    DB_PATH = os.path.join(os.getcwd(), "banco.db")

    @classmethod
    def conectar(cls):
        return sqlite3.connect(cls.DB_PATH)

    @classmethod
    def inicializar_banco(cls):
        with cls.conectar() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS clientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    telefone TEXT,
                    endereco TEXT,
                    status TEXT DEFAULT 'Ativo'
                )
            ''')
            conn.commit()

    @classmethod
    def create(cls, cliente: Cliente):
        cls.inicializar_banco()
        with cls.conectar() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO clientes (nome, telefone, endereco, status) VALUES (?, ?, ?, ?)",
                (cliente.nome, cliente.telefone, cliente.endereco, cliente.status)
            )
            conn.commit()
            cliente.id = cursor.lastrowid
        return cliente

    @classmethod
    def update(cls, cliente: Cliente):
        with cls.conectar() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE clientes SET nome=?, telefone=?, endereco=? WHERE id=?",
                (cliente.nome, cliente.telefone, cliente.endereco, cliente.id)
            )
            conn.commit()

    @classmethod
    def desativar(cls, cliente_id):
        with cls.conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE clientes SET status='Inativo' WHERE id=?", (cliente_id,))
            conn.commit()

    @classmethod
    def get_all_active(cls):
        cls.inicializar_banco()
        with cls.conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nome, telefone, endereco, status FROM clientes WHERE status = 'Ativo' ORDER BY nome")
            rows = cursor.fetchall()
            return [Cliente(id=r[0], nome=r[1], telefone=r[2], endereco=r[3], status=r[4]) for r in rows]
