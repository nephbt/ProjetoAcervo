document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("formLivro");
    const resposta = document.getElementById("resposta");

    form.addEventListener("submit", async function (e) {
        e.preventDefault();

        const formData = new FormData(form);

        const resp = await fetch("/livros/cadastro", {
            method: "POST",
            body: formData
        });

        const data = await resp.json();

        if (resp.ok) {
            resposta.textContent = "Livro cadastrado com sucesso!";
            resposta.style.color = "green";
            form.reset();
        } else {
            resposta.textContent = "Erro ao cadastrar livro: " + JSON.stringify(data);
            resposta.style.color = "red";
        }
    });
});
