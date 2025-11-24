document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("formNovoLivro");
    const mensagem = document.getElementById("mensagem");
    const tabela = document.getElementById("tabelaLivros");
    const busca = document.getElementById("busca");
    const btnBuscar = document.getElementById("btnBuscar");
    const btnAtualizar = document.getElementById("btnAtualizar");

    // Modal
    const modal = document.getElementById("modalEditar");
    const fecharModal = document.getElementById("fecharModal");
    const formEditar = document.getElementById("formEditar");

    // Mostrar mensagem
    function mostrarMensagem(texto, tipo = "sucesso") {
        mensagem.textContent = texto;
        mensagem.className = `mensagem ${tipo}`;
        setTimeout(() => {
            mensagem.className = "mensagem";
        }, 5000);
    }

    // --- CADASTRAR LIVRO ---
    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const formData = new FormData(form);

        const resp = await fetch("/livros/cadastro", {
            method: "POST",
            body: formData
        });

        if (resp.ok) {
            mostrarMensagem("✅ Livro cadastrado com sucesso!", "sucesso");
            form.reset();
            carregarLivros();
        } else {
            const data = await resp.json();
            mostrarMensagem("❌ Erro ao cadastrar: " + JSON.stringify(data), "erro");
        }
    });

    // --- LISTAR LIVROS ---
    async function carregarLivros() {
        const resp = await fetch("/livros/");
        const livros = await resp.json();

        tabela.innerHTML = "";

        if (livros.length === 0) {
            tabela.innerHTML = '<tr><td colspan="6" style="text-align: center; color: #999;">Nenhum livro cadastrado</td></tr>';
            return;
        }

        livros.forEach(livro => {
            const imagem = livro.imagem_url || "/static/images/default.png";
            const linha = document.createElement("tr");
            linha.innerHTML = `
                <td><img src="${imagem}" alt="${livro.titulo}" onerror="this.src='/static/images/default.png'"></td>
                <td>${livro.titulo}</td>
                <td>${livro.autor}</td>
                <td>${livro.genero}</td>
                <td>${livro.ano_publicacao}</td>
                <td>
                    <div class="acoes">
                        <button class="btn-editar" onclick="abrirEditar('${livro.id}')">✏️ Editar</button>
                        <button class="btn-excluir" onclick="excluirLivro('${livro.id}', '${livro.titulo}')">🗑️ Excluir</button>
                    </div>
                </td>
            `;
            tabela.appendChild(linha);
        });
    }

    // --- ABRIR MODAL DE EDIÇÃO ---
    window.abrirEditar = async function (id) {
        const resp = await fetch(`/livros/${id}`);
        if (!resp.ok) {
            alert("Erro ao carregar dados do livro.");
            return;
        }

        const livro = await resp.json();

        document.getElementById("editarId").value = livro.id;
        document.getElementById("editarTitulo").value = livro.titulo;
        document.getElementById("editarAutor").value = livro.autor;
        document.getElementById("editarGenero").value = livro.genero;
        document.getElementById("editarAno").value = livro.ano_publicacao;
        document.getElementById("editarImagem").value = livro.imagem_url || "";

        modal.style.display = "flex";
    }

    // --- FECHAR MODAL ---
    fecharModal.addEventListener("click", () => {
        modal.style.display = "none";
    });

    window.addEventListener("click", (event) => {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    });

    // --- SALVAR EDIÇÃO ---
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
                mostrarMensagem("✅ Livro atualizado com sucesso!", "sucesso");
                modal.style.display = "none";
                carregarLivros();
            } else {
                mostrarMensagem("❌ Erro ao atualizar o livro!", "erro");
            }
        } catch (erro) {
            console.error("Erro:", erro);
            mostrarMensagem("❌ Erro ao atualizar o livro.", "erro");
        }
    });

    // --- EXCLUIR LIVRO ---
    window.excluirLivro = async function (id, titulo) {
        if (!confirm(`Deseja realmente excluir "${titulo}"?`)) return;

        const resp = await fetch(`/livros/${id}`, { method: "DELETE" });
        if (resp.ok) {
            mostrarMensagem(`✅ Livro "${titulo}" excluído com sucesso!`, "sucesso");
            carregarLivros();
        } else {
            mostrarMensagem("❌ Erro ao excluir livro.", "erro");
        }
    }

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
        if (filtrados.length === 0) {
            tabela.innerHTML = '<tr><td colspan="6" style="text-align: center; color: #999;">Nenhum livro encontrado</td></tr>';
            return;
        }

        filtrados.forEach(livro => {
            const imagem = livro.imagem_url || "/static/images/default.png";
            const linha = document.createElement("tr");
            linha.innerHTML = `
                <td><img src="${imagem}" alt="${livro.titulo}" onerror="this.src='/static/images/default.png'"></td>
                <td>${livro.titulo}</td>
                <td>${livro.autor}</td>
                <td>${livro.genero}</td>
                <td>${livro.ano_publicacao}</td>
                <td>
                    <div class="acoes">
                        <button class="btn-editar" onclick="abrirEditar('${livro.id}')">✏️ Editar</button>
                        <button class="btn-excluir" onclick="excluirLivro('${livro.id}', '${livro.titulo}')">🗑️ Excluir</button>
                    </div>
                </td>
            `;
            tabela.appendChild(linha);
        });
    });

    // --- BOTÃO ATUALIZAR ---
    btnAtualizar.addEventListener("click", carregarLivros);

    // --- INICIALIZA ---
    carregarLivros();
});