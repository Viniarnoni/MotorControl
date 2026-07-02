from typing import Optional, List
from datetime import date
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from typing import Optional

class Motor(SQLModel, table=True):
    __tablename__ = "motores"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    cliente_id: Optional[int] = Field(foreign_key="clientes.id", default=None)
    
    tipo: str
    marca: str
    modelo: str
    cv: str
    rpm: str
    tensao: str
    numero_serie: Optional[str] = Field(default=None, index=True)
    data_entrada: date = Field(default_factory=date.today)
    status: str = Field(default="Recebido")
    responsavel: Optional[str] = Field(default=None)
    problema_relatado: Optional[str] = Field(default=None)
    diagnostico: Optional[str] = Field(default=None)
    observacoes: Optional[str] = Field(default=None)
    is_active: bool = Field(default=True)
    caminho_foto: Optional[str] = Field(default=None)   
    cliente: Optional["Cliente"] = Relationship(back_populates="motores")

class Cliente(SQLModel, table=True):
    __tablename__ = "clientes"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str = Field(index=True)
    telefone: str
    cidade: str
    observacoes: Optional[str] = Field(default=None)
    is_active: bool = Field(default=True) 
    motores: List[Motor] = Relationship(back_populates="cliente")