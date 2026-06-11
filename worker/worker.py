import pika
import json
import time
import random
import requests

NOME_FILA = "fila_pedidos"
TOKEN_API = "meu-token-secreto"
URL_API = "http://localhost:8000"


def atualizar_status(pedido_id, status):
    url = f"{URL_API}/pedidos/{pedido_id}/status"
    headers = {
        "Authorization": f"Bearer {TOKEN_API}"
    }
    params = {
        "status": status
    }

    resposta = requests.patch(url, headers=headers, params=params)

    if resposta.status_code == 200:
        print(f"Pedido {pedido_id} atualizado para {status}")
    else:
        print(f"Erro ao atualizar pedido {pedido_id}: {resposta.text}")


def processar_pedido(ch, method, properties, body):
    dados = json.loads(body)

    pedido_id = dados["id"]
    cliente = dados["cliente"]
    produto = dados["produto"]

    print("----------------------------------------")
    print(f"Pedido recebido: {pedido_id}")
    print(f"Cliente: {cliente}")
    print(f"Produto: {produto}")
    print("Processando pedido...")

    time.sleep(5)

    status_final = random.choice(["Aprovado", "Rejeitado"])

    atualizar_status(pedido_id, status_final)

    ch.basic_ack(delivery_tag=method.delivery_tag)


def iniciar_worker():
    print("Conectando ao RabbitMQ...")

    conexao = pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost")
    )

    canal = conexao.channel()
    canal.queue_declare(queue=NOME_FILA, durable=True)

    canal.basic_qos(prefetch_count=1)

    canal.basic_consume(
        queue=NOME_FILA,
        on_message_callback=processar_pedido
    )

    print("Worker iniciado. Aguardando pedidos...")
    canal.start_consuming()


if __name__ == "__main__":
    iniciar_worker()