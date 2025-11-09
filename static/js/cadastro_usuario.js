document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("formUsuario");
    const msg = document.getElementById("mensagem");

    form.addEventListener("submit", async function (e) {
        e.preventDefault(); // evita reload da página

        const formData = new FormData(form);

        const resp = await fetch("/usuarios/cadastro", {
            method: "POST",
            body: formData // vai para request.form no Flask
        });

        if (resp.ok) {
            msg.textContent = "✅ Usuário cadastrado com sucesso!";
            msg.style.color = "green";
            form.reset();
        } else {
            const erro = await resp.json();
            msg.textContent = "❌ " + (erro.erro || "Erro ao cadastrar usuário.");
            msg.style.color = "red";
        }

    });
});
