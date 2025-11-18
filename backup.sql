BEGIN TRANSACTION;
CREATE TABLE leituras (
            id_usuario TEXT NOT NULL,
            id_livro TEXT NOT NULL,
            status TEXT NOT NULL,
            avaliacao REAL,
            data_leitura DATE,
            comentario TEXT,
            FOREIGN KEY (id_usuario) REFERENCES usuarios (id),
            FOREIGN KEY (id_livro) REFERENCES livros (id),
            PRIMARY KEY (id_usuario, id_livro)
        );
CREATE TABLE livros (
            id TEXT PRIMARY KEY NOT NULL,
            titulo VARCHAR NOT NULL,
            autor VARCHAR NOT NULL,
            genero VARCHAR NOT NULL,
            ano_publicacao INT NOT NULL,
            imagem_url TEXT
        );
CREATE TABLE "usuarios" (
                  id TEXT PRIMARY KEY NOT NULL,
                  nome VARCHAR NOT NULL,
                  email VARCHAR NOT NULL,
                  senha TEXT NOT NULL,
                  data_nasc DATE NOT NULL
              );
INSERT INTO "usuarios" VALUES('5b9214cb-d9e3-4df9-830f-21652e481fd3','Banana','banana@email.com','$2b$12$E00gop5M6LzDj2DUX.t.fOm9l.e9p.PLaIhII4cD2dh6OVXTJNy4a','2025-11-04');
COMMIT;
