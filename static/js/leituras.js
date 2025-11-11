async function iniciarMinhasLeituras() {
    const livrosGrid = document.getElementById("livrosGrid");
    const modal = document.getElementById("modalLeitura");
    const fecharModal = document.getElementById("fecharModal");
    const formLeitura = document.getElementById("formLeitura");
    const livroIdInput = document.getElementById("livroId");
    const estrelasDiv = document.getElementById("estrelas");
    let avaliacao = 0;

    // Pegar token do localStorage
    const token = localStorage.getItem("token");
    if (!token) alert("Você precisa estar logado!");

    // Função para carregar livros
    async function carregarLivros() {
        const resp = await fetch("/livros/");
        const livros = await resp.json();
        console.log("Livros carregados:", livros);


        livrosGrid.innerHTML = "";
        livros.forEach(livro => {
            const imagem = livro.imagem_url && livro.imagem_url.trim() !== ""
                ? livro.imagem_url
                : "/static/images/default.png"; // fallback se não tiver URL

            const card = document.createElement("div");
            card.className = "livro-card";
            card.innerHTML = `
        <img src="${imagem}" alt="${livro.titulo}">
        <h3>${livro.titulo}</h3>
        <p>${livro.autor} - ${livro.ano_publicacao}</p>
        <button onclick="abrirModal('${livro.id}')">Marcar como lido</button>
    `;
            livrosGrid.appendChild(card);
        });

    }

    // Abrir modal
    window.abrirModal = function (livroId) {
        livroIdInput.value = livroId;
        modal.style.display = "flex";
    }

    fecharModal.addEventListener("click", () => {
        modal.style.display = "none";
        avaliacao = 0;
        atualizarEstrelas();
        formLeitura.reset();
    });

    // Avaliação de estrelas
    estrelasDiv.querySelectorAll("span").forEach(star => {
        star.addEventListener("click", () => {
            avaliacao = star.dataset.value;
            atualizarEstrelas();
        });
    });

    function atualizarEstrelas() {
        estrelasDiv.querySelectorAll("span").forEach(star => {
            star.classList.toggle("checked", star.dataset.value <= avaliacao);
        });
    }

    // Submeter formulário
    formLeitura.addEventListener("submit", async (e) => {
        e.preventDefault();

        const data = {
            status: document.getElementById("status").value,
            avaliacao: avaliacao,
            comentario: document.getElementById("comentario").value || null,
            data_leitura: document.getElementById("data_leitura").value

        };

        const usuario_id = JSON.parse(atob(token.split(".")[1])).id;
        const livro_id = livroIdInput.value;

        const resp = await fetch(`/leituras/${usuario_id}/${livro_id}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify(data)
        });

        if (resp.ok) {
            alert("Leitura registrada com sucesso!");
            carregarLivros(); // Recarrega livros após salvar
        } else {
            let erro;
            try {
                erro = await resp.json();
            } catch {
                erro = { erro: await resp.text() };
            }
            alert("Erro: " + (erro.erro || "Falha ao registrar leitura"));
        }
    });

    // Carrega os livros inicialmente
    carregarLivros();
}

async function carregarLivros() {
    const resp = await fetch("/livros/");  // Endpoint que retorna os livros
    const livros = await resp.json();

    livrosGrid.innerHTML = "";

    livros.forEach(livro => {
        const card = document.createElement("div");
        card.className = "livro-card";

        // Usando imagem do banco, se tiver; senão, fallback
        const imagem = livro.imagem_url && livro.imagem_url.trim() !== ""
            ? livro.imagem_url
            : "/static/images/default.png";  // coloque default.png na pasta static/images

        card.innerHTML = `
            <img src="${imagem}" alt="${livro.titulo}">
            <h3>${livro.titulo}</h3>
            <p>${livro.autor} - ${livro.ano_publicacao}</p>
            <button onclick="abrirModal('${livro.id}')">Marcar como lido</button>
        `;
        livrosGrid.appendChild(card);
    });
}
