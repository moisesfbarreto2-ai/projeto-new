# -*- coding: utf-8 -*-
from dotenv import load_dotenv
import os
from typing import List, Optional
import uuid
from datetime import datetime, date
from enum import Enum
import locale
from fastapi import FastAPI, APIRouter, HTTPException
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field

load_dotenv()

try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'C.UTF-8')
    except locale.Error:
        print("Locale 'pt_BR.UTF-8' and 'C.UTF-8' not supported.")

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

app = FastAPI(title="API Painel Financeiro Ótica", version="1.0.0")

origins = os.getenv('CORS_ORIGINS', '*').split(',')

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter(prefix="/api")

# Enums
class TransactionType(str, Enum):
    ENTRADA = "entrada"
    SAIDA = "saida"

class TransactionCategory(str, Enum):
    VENDA_OCULOS = "venda_oculos"
    VENDA_LENTES = "venda_lentes"
    VENDA_ACESSORIOS = "venda_acessorios"
    SERVICO_EXAME = "servico_exame"
    SERVICO_CONSULTA = "servico_consulta"
    OUTROS_SERVICOS = "outros_servicos"
    CUSTO_PRODUTOS = "custo_produtos"
    ALUGUEL = "aluguel"
    SALARIOS = "salarios"
    ENERGIA = "energia"
    AGUA = "agua"
    TELEFONE = "telefone"
    MARKETING = "marketing"
    MANUTENCAO = "manutencao"
    IMPOSTOS = "impostos"
    OUTROS_CUSTOS = "outros_custos"

class ClientStatus(str, Enum):
    ADIMPLENTE = "adimplente"
    INADIMPLENTE = "inadimplente"
    
class EstadoCivil(str, Enum):
    SOLTEIRO = "solteiro"
    CASADO = "casado"
    DIVORCIADO = "divorciado"
    VIUVO = "viuvo"
    UNIAO_ESTAVEL = "uniao_estavel"

class Escolaridade(str, Enum):
    FUNDAMENTAL = "fundamental"
    MEDIO = "medio"
    SUPERIOR = "superior"
    TECNICO = "tecnico"
    POS_GRADUACAO = "pos_graduacao"

class FrequenciaCompra(str, Enum):
    PRIMEIRA_VEZ = "primeira_vez"
    ESPORADICO = "esporadico"
    REGULAR = "regular"
    FREQUENTE = "frequente"

class TipoCompra(str, Enum):
    ECONOMICO = "economico"
    PADRAO = "padrao"
    PREMIUM = "premium"
    LUXO = "luxo"

class OrigemCliente(str, Enum):
    AMIGO = "amigo"
    INSTAGRAM = "instagram"
    WHATSAPP = "whatsapp"
    FACEBOOK = "facebook"
    GOOGLE = "google"
    PLACA_LOJA = "placa_loja"
    PASSANDO_RUA = "passando_rua"
    OUTROS = "outros"

# Models
class TransactionCreate(BaseModel):
    tipo: Optional[TransactionType] = None
    categoria: Optional[TransactionCategory] = None
    descricao: Optional[str] = None
    valor: Optional[float] = None
    data: Optional[date] = None
    cliente_nome: Optional[str] = None
    cliente_id: Optional[str] = None
    observacoes: Optional[str] = None

class ClientCreate(BaseModel):
    nome: Optional[str] = None
    email: Optional[str] = None
    telefone: Optional[str] = None
    endereco: Optional[str] = None
    status: Optional[ClientStatus] = ClientStatus.ADIMPLENTE
    valor_devido: Optional[float] = 0.0
    data_ultimo_pagamento: Optional[date] = None
    estado_civil: Optional[EstadoCivil] = None
    numero_filhos: Optional[int] = 0
    escolaridade: Optional[Escolaridade] = None
    tem_cartao_credito: Optional[bool] = None
    renda_bruta: Optional[float] = None
    idade: Optional[int] = None
    frequencia_compra: Optional[FrequenciaCompra] = None
    quantidade_compras: Optional[int] = 0
    tipo_compra: Optional[TipoCompra] = None
    origem_cliente: Optional[OrigemCliente] = None
    observacoes: Optional[str] = None

class Transaction(TransactionCreate):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Client(ClientCreate):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TransactionUpdate(BaseModel):
    tipo: Optional[TransactionType] = None
    categoria: Optional[TransactionCategory] = None
    descricao: Optional[str] = None
    valor: Optional[float] = None
    data: Optional[date] = None
    cliente_nome: Optional[str] = None
    cliente_id: Optional[str] = None
    observacoes: Optional[str] = None

class ClientUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[str] = None
    telefone: Optional[str] = None
    endereco: Optional[str] = None
    status: Optional[ClientStatus] = None
    valor_devido: Optional[float] = None
    data_ultimo_pagamento: Optional[date] = None
    estado_civil: Optional[EstadoCivil] = None
    numero_filhos: Optional[int] = None
    escolaridade: Optional[Escolaridade] = None
    tem_cartao_credito: Optional[bool] = None
    renda_bruta: Optional[float] = None
    idade: Optional[int] = None
    frequencia_compra: Optional[FrequenciaCompra] = None
    quantidade_compras: Optional[int] = None
    tipo_compra: Optional[TipoCompra] = None
    origem_cliente: Optional[OrigemCliente] = None
    observacoes: Optional[str] = None

class MonthlyReport(BaseModel):
    mes: int
    ano: int
    total_entradas: float
    total_saidas: float
    faturamento_liquido: float
    transacoes_count: int

# --- ROTAS DA API ---

@api_router.get("/")
async def root():
    return {"message": "Dashboard Financeiro - Ótica API"}

# Routes - Transações
@api_router.post("/transactions", response_model=Transaction)
async def create_transaction(transaction: TransactionCreate):
    """Criar nova transação financeira"""
    transaction_obj = Transaction(**transaction.dict(exclude_unset=True))
    transaction_data = transaction_obj.dict()
    if transaction_data.get('data'):
        transaction_data['data'] = transaction_data['data'].isoformat()
    await db.transactions.insert_one(transaction_data)
    return transaction_obj

@api_router.get("/transactions", response_model=List[Transaction])
async def get_transactions(
    data_inicio: Optional[date] = None, 
    data_fim: Optional[date] = None, 
    cliente_nome: Optional[str] = None,
    skip: int = 0, 
    limit: int = 100
):
    """Listar transações com filtros por data e nome do cliente."""
    query = {}
    if cliente_nome:
        query["cliente_nome"] = {"$regex": cliente_nome, "$options": "i"}

    if data_inicio or data_fim:
        query["data"] = {}
        if data_inicio:
            query["data"]["$gte"] = data_inicio.isoformat()
        if data_fim:
            query["data"]["$lte"] = data_fim.isoformat()

    transactions_from_db = await db.transactions.find(query).skip(skip).limit(limit).sort("data", -1).to_list(limit)
    
    for t in transactions_from_db:
        if t.get('data') and isinstance(t['data'], str):
            t['data'] = date.fromisoformat(t['data'])
    
    return [Transaction(**t) for t in transactions_from_db]

@api_router.delete("/transactions/{transaction_id}")
async def delete_transaction(transaction_id: str):
    """Deletar transação"""
    result = await db.transactions.delete_one({"id": transaction_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    return {"message": "Transação deletada com sucesso"}

@api_router.put("/transactions/{transaction_id}", response_model=Transaction)
async def update_transaction(transaction_id: str, transaction_update: TransactionUpdate):
    """Atualizar transação"""
    update_data = transaction_update.dict(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")
    
    if update_data.get('data'):
        update_data['data'] = update_data['data'].isoformat()
    
    await db.transactions.update_one({"id": transaction_id}, {"$set": update_data})
    
    updated_transaction = await db.transactions.find_one({"id": transaction_id})
    if not updated_transaction:
        raise HTTPException(status_code=404, detail="Transação não encontrada após atualização")

    if updated_transaction.get('data') and isinstance(updated_transaction['data'], str):
        updated_transaction['data'] = date.fromisoformat(updated_transaction['data'])
        
    return Transaction(**updated_transaction)

# Routes - Relatórios
@api_router.get("/reports/monthly")
async def get_monthly_reports(ano: Optional[int] = None):
    """Relatório mensal de entradas e saídas"""
    if not ano:
        ano = datetime.now().year
    
    pipeline = [
        {"$match": {"data": {"$regex": f"^{ano}"}}},
        {"$addFields": {"date_obj": {"$dateFromString": {"dateString": "$data"}}}},
        {"$group": {
            "_id": {"$month": "$date_obj"},
            "entradas": {"$sum": {"$cond": [{"$eq": ["$tipo", "entrada"]}, "$valor", 0]}},
            "saidas": {"$sum": {"$cond": [{"$eq": ["$tipo", "saida"]}, "$valor", 0]}},
            "total_transacoes": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ]
    result = await db.transactions.aggregate(pipeline).to_list(12)
    
    monthly_data = []
    for item in result:
        monthly_data.append({
            "mes": item["_id"], "ano": ano,
            "total_entradas": round(item["entradas"], 2),
            "total_saidas": round(item["saidas"], 2),
            "faturamento_liquido": round(item["entradas"] - item["saidas"], 2),
            "transacoes_count": item["total_transacoes"]
        })
    return monthly_data

@api_router.get("/reports/dashboard")
async def get_dashboard_data():
    """Dados principais para o dashboard"""
    current_date = datetime.now()
    current_month_str = f"{current_date.year}-{current_date.month:02d}"
    
    pipeline_current = [
        {"$match": {"data": {"$regex": f"^{current_month_str}"}}},
        {"$group": {"_id": "$tipo", "total": {"$sum": "$valor"}}}
    ]
    current_month_data = await db.transactions.aggregate(pipeline_current).to_list(2)
    
    entradas_mes = next((item['total'] for item in current_month_data if item['_id'] == 'entrada'), 0)
    saidas_mes = next((item['total'] for item in current_month_data if item['_id'] == 'saida'), 0)
    
    inadimplentes_count = await db.clients.count_documents({"status": "inadimplente"})
    
    pipeline_valor_devido = [
        {"$match": {"status": "inadimplente"}},
        {"$group": {"_id": None, "total": {"$sum": "$valor_devido"}}}
    ]
    valor_total_devido_result = await db.clients.aggregate(pipeline_valor_devido).to_list(1)
    valor_devido = valor_total_devido_result[0]['total'] if valor_total_devido_result else 0
    
    return {
        "mes_atual": {
            "entradas": round(entradas_mes, 2), "saidas": round(saidas_mes, 2),
            "faturamento_liquido": round(entradas_mes - saidas_mes, 2)
        },
        "inadimplentes": {
            "quantidade": inadimplentes_count, "valor_total_devido": round(valor_devido, 2)
        }
    }

# Routes - Clientes
@api_router.post("/clients", response_model=Client)
async def create_client(client: ClientCreate):
    """Criar novo cliente"""
    client_obj = Client(**client.dict(exclude_unset=True))
    client_data = client_obj.dict()
    if client_data.get('data_ultimo_pagamento'):
        client_data['data_ultimo_pagamento'] = client_data['data_ultimo_pagamento'].isoformat()
    await db.clients.insert_one(client_data)
    return client_obj

@api_router.get("/clients", response_model=List[Client])
async def get_clients(skip: int = 0, limit: int = 100, status: Optional[ClientStatus] = None):
    """Listar clientes"""
    query = {}
    if status:
        query["status"] = status
    clients_from_db = await db.clients.find(query).skip(skip).limit(limit).sort("nome", 1).to_list(limit)
    for c in clients_from_db:
        if c.get('data_ultimo_pagamento') and isinstance(c['data_ultimo_pagamento'], str):
            c['data_ultimo_pagamento'] = date.fromisoformat(c['data_ultimo_pagamento'])
    return [Client(**c) for c in clients_from_db]

@api_router.put("/clients/{client_id}", response_model=Client)
async def update_client(client_id: str, client_update: ClientUpdate):
    """Atualizar cliente"""
    update_data = client_update.dict(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")
        
    if update_data.get('data_ultimo_pagamento'):
        update_data['data_ultimo_pagamento'] = update_data['data_ultimo_pagamento'].isoformat()
        
    await db.clients.update_one({"id": client_id}, {"$set": update_data})

    updated_client = await db.clients.find_one({"id": client_id})
    if not updated_client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado após atualização")

    if updated_client.get('data_ultimo_pagamento') and isinstance(updated_client['data_ultimo_pagamento'], str):
        updated_client['data_ultimo_pagamento'] = date.fromisoformat(updated_client['data_ultimo_pagamento'])
        
    return Client(**updated_client)

@api_router.delete("/clients/{client_id}")
async def delete_client(client_id: str):
    """Deletar cliente"""
    result = await db.clients.delete_one({"id": client_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return {"message": "Cliente deletado com sucesso"}

# Routes - Exportação de dados
@api_router.get("/export/transactions")
async def export_transactions():
    """Exportar todas as transações para CSV"""
    transactions = await db.transactions.find().sort("data", -1).to_list(None)
    return [Transaction(**t).dict() for t in transactions]

@api_g_router.et("/export/clients")
async def export_clients():
    """Exportar todos os clientes para CSV"""
    clients = await db.clients.find().sort("nome", 1).to_list(None)
    return [Client(**c).dict() for c in clients]

@api_router.get("/export/dashboard")
async def export_dashboard_data():
    """Exportar dados completos do dashboard"""
    dashboard_data = await get_dashboard_data()
    monthly_data = await get_monthly_reports()
    client_stats_pipeline = [
        {"$group": {
            "_id": "$tipo_compra", "count": {"$sum": 1},
            "valor_total_devido": {"$sum": "$valor_devido"},
            "idade_media": {"$avg": "$idade"}, "renda_media": {"$avg": "$renda_bruta"}
        }}
    ]
    client_stats = await db.clients.aggregate(client_stats_pipeline).to_list(None)
    return {
        "dashboard": dashboard_data, "relatorio_mensal": monthly_data,
        "estatisticas_clientes": client_stats,
        "export_timestamp": datetime.utcnow().isoformat()
    }

# Fim das Rotas

app.include_router(api_router)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()