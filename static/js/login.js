
document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("formLogin");
    const msg = document.getElementById("mensagem");

    form.addEventListener("submit", async function (e) {
        e.preventDefault();

        // Pegando os dados do formulário
        const formData = new FormData(form);
        const email = formData.get("email");
        const senha = formData.get("senha");

        // Enviando para o endpoint Flask
        const resp = await fetch("/usuarios/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, senha })
        });

        const data = await resp.json();

        if (resp.ok) {
            msg.textContent = "✅ Login realizado com sucesso!";
            msg.style.color = "green";

            // Guardar o token no navegador
            localStorage.setItem("token", data.token);
            console.log("Token salvo:", data.token);

            // redirecionar após login
            setTimeout(() => {
                window.location.href = "/home_page_usuarios";
            }, 1000);
        } else {
            msg.textContent = "❌ Erro: " + (data.erro || "Falha no login");
            msg.style.color = "red";
        }
    });
});
