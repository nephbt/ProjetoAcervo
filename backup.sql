BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS leituras (
    id TEXT PRIMARY KEY NOT NULL,
    id_usuario TEXT NOT NULL,
    id_livro TEXT NOT NULL,
    status TEXT NOT NULL,
    avaliacao REAL,
    data_leitura DATE,
    comentario TEXT,
    FOREIGN KEY (id_usuario) REFERENCES usuarios (id),
    FOREIGN KEY (id_livro) REFERENCES livros (id)
)

CREATE TABLE livros (
    id TEXT PRIMARY KEY NOT NULL,
    titulo VARCHAR NOT NULL,
    autor VARCHAR NOT NULL,
    genero VARCHAR NOT NULL,
    ano_publicacao INT NOT NULL,
    imagem_url TEXT
);
CREATE TABLE usuarios (
    id TEXT PRIMARY KEY NOT NULL,
    nome VARCHAR NOT NULL,
    email VARCHAR NOT NULL,
    senha TEXT NOT NULL,
    data_nasc DATE NOT NULL
);
INSERT INTO "usuarios" VALUES('b0799b0f-de7f-4415-9437-8bf2bc01100f','Teste','teste@emil.com','teste123','2000-04-19');
COMMIT;
