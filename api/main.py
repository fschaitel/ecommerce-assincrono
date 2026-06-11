from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import pika
import json
import uuid
from database import pedidos

app = FastAPI(
    title="API de Pedidos - E-commerce Assíncrono",
    description="API para simular pedidos com processamento assíncrono usando RabbitMQ.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TOKEN_API = "meu-token-secreto"
NOME_FILA = "fila_pedidos"

security = HTTPBearer()


class PedidoEntrada(BaseModel):
    cliente: str
    produto: str


def validar_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != TOKEN_API:
        raise HTTPException(status_code=401, detail="Token inválido ou ausente")


def publicar_na_fila(mensagem: dict):
    try:
        conexao = pika.BlockingConnection(
            pika.ConnectionParameters(host="localhost")
        )

        canal = conexao.channel()
        canal.queue_declare(queue=NOME_FILA, durable=True)

        canal.basic_publish(
            exchange="",
            routing_key=NOME_FILA,
            body=json.dumps(mensagem),
            properties=pika.BasicProperties(delivery_mode=2)
        )

        conexao.close()

    except Exception as erro:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao publicar mensagem na fila: {erro}"
        )


@app.get("/")
def home():
    return {
        "mensagem": "API do Ecossistema de Processamento Assíncrono está funcionando."
    }


@app.post("/pedidos", status_code=201)
def criar_pedido(
    pedido: PedidoEntrada,
    autenticado: None = Depends(validar_token)
):
    pedido_id = str(uuid.uuid4())

    pedidos[pedido_id] = {
        "id": pedido_id,
        "cliente": pedido.cliente,
        "produto": pedido.produto,
        "status": "Pendente"
    }

    publicar_na_fila({
        "id": pedido_id,
        "cliente": pedido.cliente,
        "produto": pedido.produto
    })

    return {
        "mensagem": "Pedido criado com sucesso e enviado para processamento.",
        "pedido": pedidos[pedido_id]
    }


@app.get("/pedidos/{pedido_id}")
def consultar_pedido(
    pedido_id: str,
    autenticado: None = Depends(validar_token)
):
    if pedido_id not in pedidos:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    return pedidos[pedido_id]


@app.patch("/pedidos/{pedido_id}/status")
def atualizar_status(
    pedido_id: str,
    status: str,
    autenticado: None = Depends(validar_token)
):
    if pedido_id not in pedidos:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    pedidos[pedido_id]["status"] = status

    return {
        "mensagem": "Status atualizado com sucesso.",
        "pedido": pedidos[pedido_id]
    }