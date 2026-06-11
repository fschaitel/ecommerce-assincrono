from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_rota_home():
    resposta = client.get("/")

    assert resposta.status_code == 200
    assert resposta.json()["mensagem"] == "API do Ecossistema de Processamento Assíncrono está funcionando."


def test_criar_pedido_sem_token_deve_retornar_erro():
    resposta = client.post(
        "/pedidos",
        json={
            "cliente": "Teste",
            "produto": "Produto Teste"
        }
    )

    assert resposta.status_code in [401, 403]