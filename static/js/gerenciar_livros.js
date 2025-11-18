/*document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("formLivro");
    const tabela = document.getElementById("tabelaLivros");
    const msg = document.getElementById("mensagem");
    const busca = document.getElementById("busca");
    const btnBuscar = document.getElementById("btnBuscar");
    const btnAtualizar = document.getElementById("btnAtualizar");

    // --- ELEMENTOS DO MODAL ---
    const modal = document.getElementById('modalEditar').classList.add('ativo');
    const fecharModal = document.getElementById("fecharModal");
    const formEditar = document.getElementById('modalEditar').classList.remove('ativo');

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
                    <button class="btn-editar" onclick="abrirModalEditar(${livro.id})">Editar</button>
                    <button class="btn-excluir" onclick="excluirLivro(${livro.id})">Excluir</button>
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
*/
document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("formLivro");
    const tabela = document.getElementById("tabelaLivros");
    const msg = document.getElementById("mensagem");
    const busca = document.getElementById("busca");
    const btnBuscar = document.getElementById("btnBuscar");
    const btnAtualizar = document.getElementById("btnAtualizar");

    // --- ELEMENTOS DO MODAL ---
    const modal = document.getElementById('modalEditar');
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
            msg.textContent = "✅ Livro cadastrado com sucesso!";
            msg.className = "sucesso";
            msg.style.display = "block";
            form.reset();
            carregarLivros();
        } else {
            msg.textContent = "❌ Erro ao cadastrar livro.";
            msg.className = "erro";
            msg.style.display = "block";
        }
    });

    // --- LISTAR LIVROS ---
    async function carregarLivros() {
        try {
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
                    <td><img src="${livro.imagem_url || '/static/images/default.png'}" alt="${livro.titulo}"></td>
                    <td>
                        <button class="btn-editar" data-id="${livro.id}">✏️ Editar</button>
                        <button class="btn-excluir" data-id="${livro.id}">🗑️ Excluir</button>
                    </td>
                `;
                tabela.appendChild(linha);
            });
        } catch (erro) {
            console.error("Erro ao carregar livros:", erro);
            msg.textContent = "❌ Erro ao carregar livros.";
            msg.className = "erro";
            msg.style.display = "block";
        }
    }

    // --- ABRIR MODAL DE EDIÇÃO ---
    tabela.addEventListener("click", async (e) => {
        // Verifica se clicou no botão de editar
        if (e.target.classList.contains("btn-editar") || e.target.closest(".btn-editar")) {
            const btn = e.target.classList.contains("btn-editar") ? e.target : e.target.closest(".btn-editar");
            const id = btn.dataset.id;

            try {
                const resp = await fetch(`/livros/${id}`);
                if (!resp.ok) {
                    alert("❌ Erro ao carregar dados do livro.");
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

                modal.classList.add("ativo"); // Exibe o modal
            } catch (erro) {
                console.error("Erro ao abrir modal:", erro);
                alert("❌ Erro ao carregar dados do livro.");
            }
        }

        // Verifica se clicou no botão de excluir
        if (e.target.classList.contains("btn-excluir") || e.target.closest(".btn-excluir")) {
            const btn = e.target.classList.contains("btn-excluir") ? e.target : e.target.closest(".btn-excluir");
            const id = btn.dataset.id;

            if (!confirm("🗑️ Deseja realmente excluir este livro?")) return;

            try {
                const resp = await fetch(`/livros/${id}`, { method: "DELETE" });
                if (resp.ok) {
                    msg.textContent = "✅ Livro excluído com sucesso!";
                    msg.className = "sucesso";
                    msg.style.display = "block";
                    carregarLivros();
                } else {
                    msg.textContent = "❌ Erro ao excluir livro.";
                    msg.className = "erro";
                    msg.style.display = "block";
                }
            } catch (erro) {
                console.error("Erro ao excluir:", erro);
                msg.textContent = "❌ Erro ao excluir livro.";
                msg.className = "erro";
                msg.style.display = "block";
            }
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
                alert("✅ Livro atualizado com sucesso!");
                modal.classList.remove("ativo");
                carregarLivros();
            } else {
                alert("❌ Erro ao atualizar o livro!");
            }
        } catch (erro) {
            console.error("Erro na atualização:", erro);
            alert("❌ Erro ao atualizar o livro.");
        }
    });

    // --- FECHAR MODAL ---
    fecharModal.addEventListener("click", () => {
        modal.classList.remove("ativo");
    });

    // Fechar modal clicando fora
    modal.addEventListener("click", (e) => {
        if (e.target === modal) {
            modal.classList.remove("ativo");
        }
    });

    // --- BUSCAR LIVROS ---
    btnBuscar.addEventListener("click", async () => {
        const termo = busca.value.toLowerCase();

        try {
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
                    <td><img src="${livro.imagem_url || '/static/images/default.png'}" alt="${livro.titulo}"></td>
                    <td>
                        <button class="btn-editar" data-id="${livro.id}">✏️ Editar</button>
                        <button class="btn-excluir" data-id="${livro.id}">🗑️ Excluir</button>
                    </td>
                `;
                tabela.appendChild(linha);
            });

            if (filtrados.length === 0) {
                tabela.innerHTML = '<tr><td colspan="6" style="text-align:center;">Nenhum livro encontrado.</td></tr>';
            }
        } catch (erro) {
            console.error("Erro na busca:", erro);
        }
    });

    // Buscar ao pressionar Enter
    busca.addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            btnBuscar.click();
        }
    });

    // --- BOTÃO DE ATUALIZAR ---
    btnAtualizar.addEventListener("click", carregarLivros);

    // --- INICIALIZA ---
    carregarLivros();
});