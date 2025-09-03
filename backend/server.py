from dotenv import load_dotenv
import os

# Carrega as variáveis do arquivo .env para o ambiente
load_dotenv()
from fastapi import FastAPI, APIRouter, HTTPException
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, date
from enum import Enum
import locale

# Configurar locale para UTF-8
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'C.UTF-8')
    except:
        pass

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware

# Define de quais origens (sites) o backend aceitará conexões
origins = [
    "https://projeto-new-zeta.vercel.app", # A URL do seu frontend na Vercel
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Enums para categorização
class TransactionType(str, Enum):
    ENTRADA = "entrada"
    SAIDA = "saida"

class TransactionCategory(str, Enum):
    # Entradas
    VENDA_OCULOS = "venda_oculos"
    VENDA_LENTES = "venda_lentes"
    VENDA_ACESSORIOS = "venda_acessorios"
    SERVICO_EXAME = "servico_exame"
    SERVICO_CONSULTA = "servico_consulta"
    OUTROS_SERVICOS = "outros_servicos"
    
    # Saídas
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
class Transaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tipo: TransactionType
    categoria: TransactionCategory
    descricao: str
    valor: float
    data: date
    cliente_nome: Optional[str] = None
    cliente_id: Optional[str] = None
    observacoes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TransactionCreate(BaseModel):
    tipo: TransactionType
    categoria: TransactionCategory
    descricao: str
    valor: float
    data: date
    cliente_nome: Optional[str] = None
    cliente_id: Optional[str] = None
    observacoes: Optional[str] = None

class TransactionUpdate(BaseModel):
    tipo: Optional[TransactionType] = None
    categoria: Optional[TransactionCategory] = None
    descricao: Optional[str] = None
    valor: Optional[float] = None
    data: Optional[date] = None
    cliente_nome: Optional[str] = None
    cliente_id: Optional[str] = None
    observacoes: Optional[str] = None

class Client(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nome: str
    email: Optional[str] = None
    telefone: Optional[str] = None
    endereco: Optional[str] = None
    status: ClientStatus = ClientStatus.ADIMPLENTE
    valor_devido: float = 0.0
    data_ultimo_pagamento: Optional[date] = None
    
    # Campos para análise de clusterização
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
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ClientCreate(BaseModel):
    nome: str
    email: Optional[str] = None
    telefone: Optional[str] = None
    endereco: Optional[str] = None
    status: ClientStatus = ClientStatus.ADIMPLENTE
    valor_devido: float = 0.0
    data_ultimo_pagamento: Optional[date] = None
    
    # Campos para análise de clusterização
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

class ClientUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[str] = None
    telefone: Optional[str] = None
    endereco: Optional[str] = None
    status: Optional[ClientStatus] = None
    valor_devido: Optional[float] = None
    data_ultimo_pagamento: Optional[date] = None
    
    # Campos para análise de clusterização
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

# Routes - Dashboard Principal
@api_router.get("/")
async def root():
    return {"message": "Dashboard Financeiro - Ótica API"}

# Routes - Transações
@api_router.post("/transactions", response_model=Transaction)
async def create_transaction(transaction: TransactionCreate):
    """Criar nova transação financeira"""
    transaction_dict = transaction.dict()
    transaction_obj = Transaction(**transaction_dict)
    
    # Converter date para string para MongoDB
    transaction_data = transaction_obj.dict()
    transaction_data['data'] = transaction_data['data'].isoformat()
    
    await db.transactions.insert_one(transaction_data)
    return transaction_obj

@api_router.get("/transactions", response_model=List[Transaction])
async def get_transactions(
    skip: int = 0, 
    limit: int = 100,
    tipo: Optional[TransactionType] = None,
    categoria: Optional[TransactionCategory] = None,
    mes: Optional[int] = None,
    ano: Optional[int] = None
):
    """Listar transações com filtros opcionais"""
    query = {}
    
    if tipo:
        query["tipo"] = tipo
    if categoria:
        query["categoria"] = categoria
    if mes and ano:
        # Filtrar por mês/ano
        start_date = f"{ano}-{mes:02d}-01"
        if mes == 12:
            end_date = f"{ano+1}-01-01"
        else:
            end_date = f"{ano}-{mes+1:02d}-01"
        query["data"] = {"$gte": start_date, "$lt": end_date}
    
    transactions = await db.transactions.find(query).skip(skip).limit(limit).sort("data", -1).to_list(limit)
    
    # Converter string data de volta para date
    for transaction in transactions:
        if isinstance(transaction['data'], str):
            transaction['data'] = datetime.fromisoformat(transaction['data']).date()
    
    return [Transaction(**transaction) for transaction in transactions]

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
    update_data = {k: v for k, v in transaction_update.dict().items() if v is not None}
    
    if update_data.get('data'):
        update_data['data'] = update_data['data'].isoformat()
    
    if not update_data:
        raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")
    
    result = await db.transactions.update_one(
        {"id": transaction_id},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    
    updated_transaction = await db.transactions.find_one({"id": transaction_id})
    if isinstance(updated_transaction['data'], str):
        updated_transaction['data'] = datetime.fromisoformat(updated_transaction['data']).date()
    
    return Transaction(**updated_transaction)

# Routes - Relatórios
@api_router.get("/reports/monthly")
async def get_monthly_reports(ano: Optional[int] = None):
    """Relatório mensal de entradas e saídas"""
    if not ano:
        ano = datetime.now().year
    
    pipeline = [
        {
            "$match": {
                "data": {
                    "$regex": f"^{ano}"
                }
            }
        },
        {
            "$addFields": {
                "date_obj": {"$dateFromString": {"dateString": "$data"}}
            }
        },
        {
            "$group": {
                "_id": {"$month": "$date_obj"},
                "entradas": {
                    "$sum": {
                        "$cond": [{"$eq": ["$tipo", "entrada"]}, "$valor", 0]
                    }
                },
                "saidas": {
                    "$sum": {
                        "$cond": [{"$eq": ["$tipo", "saida"]}, "$valor", 0]
                    }
                },
                "total_transacoes": {"$sum": 1}
            }
        },
        {
            "$sort": {"_id": 1}
        }
    ]
    
    result = await db.transactions.aggregate(pipeline).to_list(12)
    
    monthly_data = []
    for item in result:
        monthly_data.append({
            "mes": item["_id"],
            "ano": ano,
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
    current_month = current_date.month
    current_year = current_date.year
    
    # Dados do mês atual
    current_month_str = f"{current_year}-{current_month:02d}"
    
    pipeline_current = [
        {
            "$match": {
                "data": {"$regex": f"^{current_month_str}"}
            }
        },
        {
            "$group": {
                "_id": "$tipo",
                "total": {"$sum": "$valor"}
            }
        }
    ]
    
    current_month_data = await db.transactions.aggregate(pipeline_current).to_list(10)
    
    entradas_mes = 0
    saidas_mes = 0
    
    for item in current_month_data:
        if item["_id"] == "entrada":
            entradas_mes = item["total"]
        elif item["_id"] == "saida":
            saidas_mes = item["total"]
    
    # Total de clientes inadimplentes
    inadimplentes_count = await db.clients.count_documents({"status": "inadimplente"})
    valor_total_devido = await db.clients.aggregate([
        {"$match": {"status": "inadimplente"}},
        {"$group": {"_id": None, "total": {"$sum": "$valor_devido"}}}
    ]).to_list(1)
    
    valor_devido = valor_total_devido[0]["total"] if valor_total_devido else 0
    
    return {
        "mes_atual": {
            "entradas": round(entradas_mes, 2),
            "saidas": round(saidas_mes, 2),
            "faturamento_liquido": round(entradas_mes - saidas_mes, 2)
        },
        "inadimplentes": {
            "quantidade": inadimplentes_count,
            "valor_total_devido": round(valor_devido, 2)
        }
    }

# Routes - Clientes
@api_router.post("/clients", response_model=Client)
async def create_client(client: ClientCreate):
    """Criar novo cliente"""
    client_dict = client.dict()
    client_obj = Client(**client_dict)
    
    client_data = client_obj.dict()
    if client_data.get('data_ultimo_pagamento'):
        client_data['data_ultimo_pagamento'] = client_data['data_ultimo_pagamento'].isoformat()
    
    await db.clients.insert_one(client_data)
    return client_obj

@api_router.get("/clients", response_model=List[Client])
async def get_clients(
    skip: int = 0,
    limit: int = 100,
    status: Optional[ClientStatus] = None
):
    """Listar clientes"""
    query = {}
    if status:
        query["status"] = status
    
    clients = await db.clients.find(query).skip(skip).limit(limit).sort("nome", 1).to_list(limit)
    
    for client in clients:
        if client.get('data_ultimo_pagamento') and isinstance(client['data_ultimo_pagamento'], str):
            client['data_ultimo_pagamento'] = datetime.fromisoformat(client['data_ultimo_pagamento']).date()
    
    return [Client(**client) for client in clients]

@api_router.put("/clients/{client_id}", response_model=Client)
async def update_client(client_id: str, client_update: ClientUpdate):
    """Atualizar cliente"""
    update_data = {k: v for k, v in client_update.dict().items() if v is not None}
    
    if update_data.get('data_ultimo_pagamento'):
        update_data['data_ultimo_pagamento'] = update_data['data_ultimo_pagamento'].isoformat()
    
    if not update_data:
        raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")
    
    result = await db.clients.update_one(
        {"id": client_id},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    updated_client = await db.clients.find_one({"id": client_id})
    if updated_client.get('data_ultimo_pagamento') and isinstance(updated_client['data_ultimo_pagamento'], str):
        updated_client['data_ultimo_pagamento'] = datetime.fromisoformat(updated_client['data_ultimo_pagamento']).date()
    
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
    
    # Converter para formato de exportação
    export_data = []
    for transaction in transactions:
        export_data.append({
            "ID": transaction["id"],
            "Data": transaction["data"],
            "Tipo": transaction["tipo"].title(),
            "Categoria": transaction["categoria"].replace("_", " ").title(),
            "Descrição": transaction["descricao"],
            "Valor": transaction["valor"],
            "Cliente": transaction.get("cliente_nome", ""),
            "Observações": transaction.get("observacoes", ""),
            "Data Criação": transaction["created_at"]
        })
    
    return {"data": export_data, "total": len(export_data)}

@api_router.get("/export/clients")
async def export_clients():
    """Exportar todos os clientes para CSV"""
    clients = await db.clients.find().sort("nome", 1).to_list(None)
    
    # Converter para formato de exportação
    export_data = []
    for client in clients:
        export_data.append({
            "ID": client["id"],
            "Nome": client["nome"],
            "Email": client.get("email", ""),
            "Telefone": client.get("telefone", ""),
            "Endereço": client.get("endereco", ""),
            "Status": client["status"].title(),
            "Valor Devido": client["valor_devido"],
            "Último Pagamento": client.get("data_ultimo_pagamento", ""),
            
            # Campos para análise
            "Estado Civil": client.get("estado_civil", "").replace("_", " ").title() if client.get("estado_civil") else "",
            "Número de Filhos": client.get("numero_filhos", 0),
            "Escolaridade": client.get("escolaridade", "").replace("_", " ").title() if client.get("escolaridade") else "",
            "Tem Cartão de Crédito": "Sim" if client.get("tem_cartao_credito") else "Não" if client.get("tem_cartao_credito") is not None else "",
            "Renda Bruta": client.get("renda_bruta", ""),
            "Idade": client.get("idade", ""),
            "Frequência de Compra": client.get("frequencia_compra", "").replace("_", " ").title() if client.get("frequencia_compra") else "",
            "Quantidade de Compras": client.get("quantidade_compras", 0),
            "Tipo de Compra": client.get("tipo_compra", "").title() if client.get("tipo_compra") else "",
            "Origem do Cliente": client.get("origem_cliente", "").replace("_", " ").title() if client.get("origem_cliente") else "",
            
            "Observações": client.get("observacoes", ""),
            "Data Criação": client["created_at"]
        })
    
    return {"data": export_data, "total": len(export_data)}

@api_router.get("/export/dashboard")
async def export_dashboard_data():
    """Exportar dados completos do dashboard"""
    # Obter dados do dashboard
    dashboard_data = await get_dashboard_data()
    monthly_data = await get_monthly_reports()
    
    # Estatísticas de clientes por perfil
    client_stats = await db.clients.aggregate([
        {
            "$group": {
                "_id": "$tipo_compra",
                "count": {"$sum": 1},
                "valor_total_devido": {"$sum": "$valor_devido"},
                "idade_media": {"$avg": "$idade"},
                "renda_media": {"$avg": "$renda_bruta"}
            }
        }
    ]).to_list(10)
    
    return {
        "dashboard": dashboard_data,
        "relatorio_mensal": monthly_data,
        "estatisticas_clientes": client_stats,
        "export_timestamp": datetime.utcnow().isoformat()
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()