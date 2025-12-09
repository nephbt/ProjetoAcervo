document.addEventListener("DOMContentLoaded", () => {
    // IDs CORRETOS
    const form = document.getElementById("formNovoLivro");
    const tabela = document.getElementById("tabelaLivros");
    const msg = document.getElementById("mensagem");
    const busca = document.getElementById("busca");
    const btnBuscar = document.getElementById("btnBuscar");
    const btnAtualizar = document.getElementById("btnAtualizar");

    const modal = document.getElementById('modalEditar');
    const fecharModal = document.getElementById("fecharModal");
    const formEditar = document.getElementById("formEditar");

    // Pegar token do localStorage
    const token = localStorage.getItem("token");

    // Verificar se está logado
    if (!token) {
        alert("Você precisa estar logado para gerenciar livros!");
        window.location.href = "/login_usuario";
        return;
    }

    // ✅ Função auxiliar para gerar HTML das ações (só para admin)
    function getAcoesHTML(livro) {
        // isAdmin é definido no HTML antes deste script carregar
        if (typeof isAdmin !== 'undefined' && isAdmin) {
            return `
                <td class="acoes">
                    <button class="btn-editar" data-id="${livro.id}">✏️ Editar</button>
                    <button class="btn-excluir" data-id="${livro.id}">🗑️ Excluir</button>
                </td>
            `;
        }
        return ''; // Usuário comum não vê botões
    }

    // --- CADASTRAR LIVRO ---
    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const formData = new FormData(form);

        // Converter para objeto e renomear campo
        const data = {
            titulo: formData.get("titulo"),
            autor: formData.get("autor"),
            genero: formData.get("genero"),
            ano_publicacao: formData.get("ano_publicacao"),
            imagem_url: formData.get("imagem") || null
        };

        console.log("📚 Cadastrando livro:", data);

        try {
            const resp = await fetch("/livros/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify(data)
            });

            const resultado = await resp.json();
            console.log("📡 Resposta:", resultado);

            if (resp.ok) {
                msg.textContent = "✅ Livro cadastrado com sucesso!";
                msg.className = "mensagem sucesso";
                form.reset();
                carregarLivros();
            } else {
                msg.textContent = "❌ Erro: " + (resultado.erro || "Falha ao cadastrar");
                msg.className = "mensagem erro";
            }
        } catch (erro) {
            console.error("❌ Erro:", erro);
            msg.textContent = "❌ Erro ao cadastrar livro.";
            msg.className = "mensagem erro";
        }
    });

    // --- LISTAR LIVROS (apenas aprovados) ---
    async function carregarLivros() {
        try {
            const resp = await fetch("/livros/");
            const livros = await resp.json();

            console.log("📚 Livros carregados:", livros.length);

            tabela.innerHTML = "";

            if (livros.length === 0) {
                tabela.innerHTML = '<tr><td colspan="6" style="text-align:center; color: #999;">Nenhum livro aprovado ainda.</td></tr>';
                return;
            }

            livros.forEach(livro => {
                const imagem = livro.imagem_url || livro.imagem || '/static/images/default.png';
                const linha = document.createElement("tr");
                linha.innerHTML = `
                    <td><img src="${imagem}" alt="${livro.titulo}" style="width:50px; height:70px; object-fit:cover; border-radius:3px;" onerror="this.src='/static/images/default.png'"></td>
                    <td>${livro.titulo}</td>
                    <td>${livro.autor}</td>
                    <td>${livro.genero}</td>
                    <td>${livro.ano_publicacao}</td>
                    ${getAcoesHTML(livro)}
                `;
                tabela.appendChild(linha);
            });
        } catch (erro) {
            console.error("Erro ao carregar livros:", erro);
            tabela.innerHTML = '<tr><td colspan="6" style="text-align:center; color: red;">Erro ao carregar livros.</td></tr>';
        }
    }

    // --- ABRIR MODAL DE EDIÇÃO (só funciona para admin) ---
    tabela.addEventListener("click", async (e) => {
        // ✅ Verifica se é admin antes de permitir edição/exclusão
        if (typeof isAdmin === 'undefined' || !isAdmin) {
            return; // Não faz nada se não for admin
        }

        // Editar
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

                document.getElementById("editarId").value = livro.id;
                document.getElementById("editarTitulo").value = livro.titulo;
                document.getElementById("editarAutor").value = livro.autor;
                document.getElementById("editarGenero").value = livro.genero;
                document.getElementById("editarAno").value = livro.ano_publicacao;
                document.getElementById("editarImagem").value = livro.imagem_url || livro.imagem || "";

                modal.style.display = "flex";
            } catch (erro) {
                console.error("Erro ao abrir modal:", erro);
                alert("❌ Erro ao carregar dados do livro.");
            }
        }

        // Excluir
        if (e.target.classList.contains("btn-excluir") || e.target.closest(".btn-excluir")) {
            const btn = e.target.classList.contains("btn-excluir") ? e.target : e.target.closest(".btn-excluir");
            const id = btn.dataset.id;

            if (!confirm("🗑️ Deseja realmente excluir este livro?")) return;

            try {
                const resp = await fetch(`/livros/${id}`, {
                    method: "DELETE",
                    headers: {
                        "Authorization": `Bearer ${token}`
                    }
                });

                if (resp.ok) {
                    msg.textContent = "✅ Livro excluído com sucesso!";
                    msg.className = "mensagem sucesso";
                    carregarLivros();
                } else {
                    const erro = await resp.json();
                    msg.textContent = "❌ " + (erro.erro || "Erro ao excluir livro.");
                    msg.className = "mensagem erro";
                }
            } catch (erro) {
                console.error("Erro ao excluir:", erro);
                msg.textContent = "❌ Erro ao excluir livro.";
                msg.className = "mensagem erro";
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
            imagem_url: document.getElementById("editarImagem").value || null
        };

        try {
            const resp = await fetch(`/livros/${id}`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify(dados)
            });

            if (resp.ok) {
                alert("✅ Livro atualizado com sucesso!");
                modal.style.display = "none";
                carregarLivros();
            } else {
                const erro = await resp.json();
                alert("❌ " + (erro.erro || "Erro ao atualizar o livro!"));
            }
        } catch (erro) {
            console.error("Erro na atualização:", erro);
            alert("❌ Erro ao atualizar o livro.");
        }
    });

    // --- FECHAR MODAL ---
    fecharModal.addEventListener("click", () => {
        modal.style.display = "none";
    });

    modal.addEventListener("click", (e) => {
        if (e.target === modal) {
            modal.style.display = "none";
        }
    });

    // --- BUSCAR LIVROS ---
    btnBuscar.addEventListener("click", async () => {
        const termo = busca.value.trim().toLowerCase();

        if (!termo) {
            carregarLivros();
            return;
        }

        try {
            const resp = await fetch(`/livros/busca?q=${encodeURIComponent(termo)}`);
            const livros = await resp.json();

            tabela.innerHTML = "";

            if (livros.length === 0) {
                tabela.innerHTML = '<tr><td colspan="6" style="text-align:center;">Nenhum livro encontrado.</td></tr>';
                return;
            }

            livros.forEach(livro => {
                const imagem = livro.imagem_url || livro.imagem || '/static/images/default.png';
                const linha = document.createElement("tr");
                linha.innerHTML = `
                    <td><img src="${imagem}" alt="${livro.titulo}" style="width:50px; height:70px; object-fit:cover; border-radius:3px;" onerror="this.src='/static/images/default.png'"></td>
                    <td>${livro.titulo}</td>
                    <td>${livro.autor}</td>
                    <td>${livro.genero}</td>
                    <td>${livro.ano_publicacao}</td>
                    ${getAcoesHTML(livro)}
                `;
                tabela.appendChild(linha);
            });
        } catch (erro) {
            console.error("Erro na busca:", erro);
        }
    });

    busca.addEventListener("keypress", (e) => {
        if (e.key === "Enter") btnBuscar.click();
    });

    btnAtualizar.addEventListener("click", carregarLivros);

    // --- INICIALIZA ---
    carregarLivros();
});