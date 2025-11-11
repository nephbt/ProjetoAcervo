document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("formLivro");
    const tabela = document.getElementById("tabelaLivros");
    const msg = document.getElementById("mensagem");
    const busca = document.getElementById("busca");
    const btnBuscar = document.getElementById("btnBuscar");
    const btnAtualizar = document.getElementById("btnAtualizar");

    // --- ELEMENTOS DO MODAL ---
    const modal = document.getElementById("modalEditar");
    const fecharModal = document.getElementById("fecharModal");
    const formEditar = document.getElementById("formEditar");

    // --- CADASTRAR LIVRO ---
    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const formData = new FormData(form);
        const resp = await fetch("/livros/cadastro", {
            method: "POST",
            body: formData
        });

        if (resp.ok) {
            msg.textContent = "Livro cadastrado com sucesso!";
            msg.style.color = "green";
            form.reset();
            carregarLivros();
        } else {
            msg.textContent = "Erro ao cadastrar livro.";
            msg.style.color = "red";
        }
    });

    // --- LISTAR LIVROS ---
    async function carregarLivros() {
        const resp = await fetch("/livros/");
        const livros = await resp.json();

        tabela.innerHTML = "";
        livros.forEach(livro => {
            const linha = document.createElement("tr");
            linha.innerHTML = `
                <td>${livro.titulo}</td>
                <td>${livro.autor}</td>
                <td>${livro.genero}</td>
                <td>${livro.ano_publicacao}</td>
                <td><img src="${livro.imagem_url || ''}" width="50"></td>
                <td>
                    <button class="editar" data-id="${livro.id}">✏️</button>
                    <button class="excluir" data-id="${livro.id}">🗑️</button>
                </td>
            `;
            tabela.appendChild(linha);
        });
    }

    // --- ABRIR MODAL DE EDIÇÃO ---
    tabela.addEventListener("click", async (e) => {
        if (e.target.classList.contains("editar")) {
            const id = e.target.dataset.id;

            const resp = await fetch(`/livros/${id}`);
            if (!resp.ok) {
                alert("Erro ao carregar dados do livro.");
                return;
            }

            const livro = await resp.json();

            // Preenche os campos do modal
            document.getElementById("editarId").value = livro.id;
            document.getElementById("editarTitulo").value = livro.titulo;
            document.getElementById("editarAutor").value = livro.autor;
            document.getElementById("editarGenero").value = livro.genero;
            document.getElementById("editarAno").value = livro.ano_publicacao;
            document.getElementById("editarImagem").value = livro.imagem_url || "";

            modal.style.display = "flex"; // Exibe o modal
        }
    });

    // --- SALVAR ALTERAÇÕES DO MODAL ---
    formEditar.addEventListener("submit", async (e) => {
        e.preventDefault();

        const id = document.getElementById("editarId").value;
        const dados = {
            titulo: document.getElementById("editarTitulo").value,
            autor: document.getElementById("editarAutor").value,
            genero: document.getElementById("editarGenero").value,
            ano_publicacao: document.getElementById("editarAno").value,
            imagem_url: document.getElementById("editarImagem").value
        };

        try {
            const resp = await fetch(`/livros/${id}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(dados)
            });

            if (resp.ok) {
                alert("Livro atualizado com sucesso!");
                modal.style.display = "none";
                carregarLivros();
            } else {
                alert("Erro ao atualizar o livro!");
            }
        } catch (erro) {
            console.error("Erro na atualização:", erro);
            alert("Erro ao atualizar o livro.");
        }
    });

    // --- FECHAR MODAL ---
    fecharModal.addEventListener("click", () => {
        modal.style.display = "none";
    });

    // --- EXCLUIR LIVRO ---
    tabela.addEventListener("click", async (e) => {
        if (e.target.classList.contains("excluir")) {
            const id = e.target.dataset.id;
            if (!confirm("Deseja excluir este livro?")) return;

            const resp = await fetch(`/livros/${id}`, { method: "DELETE" });
            if (resp.ok) {
                msg.textContent = "Livro excluído com sucesso!";
                msg.style.color = "green";
                carregarLivros();
            } else {
                msg.textContent = "Erro ao excluir livro.";
                msg.style.color = "red";
            }
        }
    });

    // --- BUSCAR LIVROS ---
    btnBuscar.addEventListener("click", async () => {
        const termo = busca.value.toLowerCase();
        const resp = await fetch("/livros/");
        const livros = await resp.json();
        const filtrados = livros.filter(l =>
            l.titulo.toLowerCase().includes(termo) ||
            l.autor.toLowerCase().includes(termo) ||
            l.genero.toLowerCase().includes(termo)
        );

        tabela.innerHTML = "";
        filtrados.forEach(livro => {
            const linha = document.createElement("tr");
            linha.innerHTML = `
                <td>${livro.titulo}</td>
                <td>${livro.autor}</td>
                <td>${livro.genero}</td>
                <td>${livro.ano_publicacao}</td>
                <td><img src="${livro.imagem_url || ''}" width="50"></td>
                <td>
                    <button class="editar" data-id="${livro.id}">✏️</button>
                    <button class="excluir" data-id="${livro.id}">🗑️</button>
                </td>
            `;
            tabela.appendChild(linha);
        });
    });

    // --- BOTÃO DE ATUALIZAR ---
    btnAtualizar.addEventListener("click", carregarLivros);

    // --- INICIALIZA ---
    carregarLivros();
});
