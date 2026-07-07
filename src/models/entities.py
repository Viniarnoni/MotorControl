from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import date

class Cliente(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    telefone: Optional[str] = None
    endereco: Optional[str] = None
    status: Optional[str] = "Ativo"

class Motor(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    cliente: str
    tipo: str
    marca: str
    modelo: Optional[str] = None
    cv: Optional[str] = None
    rpm: Optional[str] = None
    tensao: Optional[str] = None
    
    # Campos da Matriz de Orçamento
    fases: Optional[str] = Field(default="Monofásico/Bifásico")
    polos: Optional[str] = Field(default="2 Polos")
    
    problema_relatado: Optional[str] = None
    caminho_foto: Optional[str] = None
    data_entrada: date = Field(default_factory=date.today)
    
    is_active: bool = Field(default=True)

class PrecoServico(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    cv: str                      
    fases: str                   
    polos: str                   
    preco_rebobinagem: float     

class PrecoPeca(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str                    
    preco_unitario: float

class Orcamento(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    motor_id: int
    motor_descricao: str         
    cliente_nome: str            
    data_emissao: date = Field(default_factory=date.today)
    
    # --- NOVOS CAMPOS SEPARADOS ---
    valor_rebobinamento: float = 0.0  # Antigo valor_mao_de_obra geral
    descricao_mao_de_obra: Optional[str] = None  # Texto customizado (Ex: Trocar retentores...)
    valor_mao_de_obra: float = 0.0  # Valor da mão de obra geral descrita acima
    
    valor_pecas: float = 0.0
    valor_total: float = 0.0
    observacoes: Optional[str] = None
    status: str = Field(default="Pendente") 

    def calcular_total(self) -> float:
        return (
            (self.valor_mao_de_obra or 0.0)
            + (self.valor_rebobinamento or 0.0)
            + (self.valor_pecas or 0.0)
        )

class ItemOrcamento(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    orcamento_id: int
    descricao: str               
    quantidade: int = 1
    preco_unitario: float
    preco_total: float
