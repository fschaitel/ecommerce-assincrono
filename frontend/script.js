const API_URL = "http://localhost:8000";
const TOKEN_API = "meu-token-secreto";

const formPedido = document.getElementById("formPedido");
const resultado = document.getElementById("resultado");

const pedidoId = document.getElementById("pedidoId");
const pedidoCliente = document.getElementById("pedidoCliente");
const pedidoProduto = document.getElementById("pedidoProduto");
const pedidoStatus = document.getElementById("pedidoStatus");

function atualizarTela(pedido) {
  pedidoId.textContent = pedido.id;
  pedidoCliente.textContent = pedido.cliente;
  pedidoProduto.textContent = pedido.produto;
  pedidoStatus.textContent = pedido.status;

  pedidoStatus.className = "status";

  if (pedido.status === "Pendente") {
    pedidoStatus.classList.add("pendente");
  }

  if (pedido.status === "Aprovado") {
    pedidoStatus.classList.add("aprovado");
  }

  if (pedido.status === "Rejeitado") {
    pedidoStatus.classList.add("rejeitado");
  }

  resultado.classList.remove("oculto");
}

async function consultarStatus(id) {
  const resposta = await fetch(`${API_URL}/pedidos/${id}`, {
    method: "GET",
    headers: {
      "Authorization": `Bearer ${TOKEN_API}`
    }
  });

  const pedido = await resposta.json();
  atualizarTela(pedido);

  return pedido.status;
}

formPedido.addEventListener("submit", async function (evento) {
  evento.preventDefault();

  const cliente = document.getElementById("cliente").value;
  const produto = document.getElementById("produto").value;

  pedidoStatus.textContent = "Enviando pedido...";
  resultado.classList.remove("oculto");

  const resposta = await fetch(`${API_URL}/pedidos`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${TOKEN_API}`
    },
    body: JSON.stringify({
      cliente: cliente,
      produto: produto
    })
  });

  const dados = await resposta.json();

  if (!resposta.ok) {
    alert("Erro ao criar pedido: " + JSON.stringify(dados));
    return;
  }

  atualizarTela(dados.pedido);

  const pedidoCriadoId = dados.pedido.id;

  setTimeout(async function () {
    await consultarStatus(pedidoCriadoId);
  }, 6000);
});