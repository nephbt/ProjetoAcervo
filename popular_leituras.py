"""
Script para popular leituras e avaliações.
Busca livros por TÍTULO e usuários por EMAIL (não por índice).

Execute: python popular_leituras.py
"""

import uuid
import bcrypt
from dbpostgres import get_connection

# ============================================================
# DADOS DOS USUÁRIOS
# ============================================================

usuarios_data = [
    ("Maria Silva", "maria@test.com", "senha123", "1995-05-15"),
    ("João Santos", "joao@test.com", "senha123", "1990-08-20"),
    ("Ana Costa", "ana@test.com", "senha123", "1998-12-10"),
    ("Joana Santos", "joana@test.com", "senha123", "1978-12-10"),
    ("Miriam Santana", "miriam@test.com", "senha123", "1988-12-10"),
    ("José Silveira", "jose@test.com", "senha123", "1968-12-10"),
    ("Karen dos Santos", "karen@test.com", "senha123", "1977-01-20"),
    ("Alan Silva", "alan@test.com", "senha123", "1989-12-13"),
    ("Bruno da Silva", "bruno@test.com", "senha123", "1999-06-10"),
    ("Juliana da Costa", "juliana@test.com", "senha123", "2000-07-21"),
    ("Arthur Duarte", "arthur@test.com", "senha123", "1995-06-09"),
    ("Amanda Soares", "amanda@test.com", "senha123", "1995-01-20"),
    ("Paulo dos Santos", "paulo@test.com", "senha123", "2005-09-29"),
    ("Ana Paula", "anapaula@test.com", "senha123", "2001-12-11"),
    ("Daniel Santana", "daniel@test.com", "senha123", "1980-05-05"),
    ("Larissa da Costa", "larissa@test.com", "senha123", "1988-09-21"),
    ("Luís Gomes", "luis@test.com", "senha123", "1993-03-24"),
    ("Silvia Santana", "silvia@test.com", "senha123", "1994-09-10"),
    ("Alexandre da Silva", "alexandre@test.com", "senha123", "1996-03-30"),
    ("César Daniel", "cesar@test.com", "senha123", "1997-04-03"),
    ("Cássia Moraes", "cassia@test.com", "senha123", "1998-05-30"),
    ("Clara Martins", "clara@test.com", "senha123", "1999-09-30"),
    ("Marisa Santana", "marissa@test.com", "senha123", "1985-09-30"),
    ("Roberto da Silva", "roberto@test.com", "senha123", "1988-09-27"),
    ("Eduardo dos Santos", "eduardo@test.com", "senha123", "2000-01-29"),
]

# ============================================================
# LEITURAS POR USUÁRIO (usando TÍTULOS dos livros)
# ============================================================

leituras_por_usuario = {
    "maria@test.com": [  # Gosta de Ficção Científica
        ("Alice no pais das maravilhas", 8.0),
    ],
    "joao@test.com": [  # Gosta de Fantasia

    ],
    "ana@test.com": [  # Gosta de Romance
        ("Alice no pais das maravilhas", 8.0),
    ],
    "joana@test.com": [  # Gosta de Ficção Científica
        ("Alice no pais das maravilhas", 9.0),
    ],
    "miriam@test.com": [# Gosta de Romance
        ("Alice no pais das maravilhas", 9.0),
    ],
    "jose@test.com": [  # Gosta de Não-ficção
        ("Alice no pais das maravilhas", 9.0),
    ],
    "karen@test.com": [  # Gosta de Romance
        ("Alice no pais das maravilhas", 9.0),
    ],
    "alan@test.com": [  # Gosta de Ficção Científica

    ],
    "bruno@test.com": [  # Gosta de Fantasia


    ],
    "juliana@test.com": [  # Gosta de Romance

    ],
    "arthur@test.com": [  # Gosta de Ficção Científica

    ],
    "amanda@test.com": [  # Gosta de Romance

    ],
    "paulo@test.com": [  # Gosta de Fantasia


    ],
    "anapaula@test.com": [  # Gosta de Romance

    ],
    "daniel@test.com": [  # Gosta de Não-ficção

    ],
    "larissa@test.com": [  # Gosta de Romance

    ],
    "luis@test.com": [  # Gosta de Aventura

    ],
    "silvia@test.com": [  # Gosta de Romance

    ],
    "alexandre@test.com": [  # Gosta de Ficção Científica

    ],
    "cesar@test.com": [  # Gosta de Fantasia

    ],
    "cassia@test.com": [  # Gosta de Romance

    ],
    "clara@test.com": [  # Gosta de Romance

    ],
    "marissa@test.com": [  # Gosta de Romance

    ],
    "roberto@test.com": [  # Gosta de Ficção Científica

    ],
    "eduardo@test.com": [  # Gosta de Fantasia

    ],
}


# ============================================================
# FUNÇÕES
# ============================================================

def hash_senha(senha):
    """Gera hash bcrypt da senha."""
    return bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def popular_usuarios():
    """Insere usuários e retorna mapeamento email -> id."""
    usuarios_map = {}

    print("\n" + "=" * 60)
    print("👥 INSERINDO USUÁRIOS")
    print("=" * 60 + "\n")

    with get_connection() as conn:
        cursor = conn.cursor()

        for nome, email, senha, data_nasc in usuarios_data:
            try:
                # Verificar se já existe
                cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
                row = cursor.fetchone()

                if row:
                    print(f"⏭️  Já existe: {nome}")
                    usuarios_map[email] = row[0]
                    continue

                # Inserir
                usuario_id = str(uuid.uuid4())
                senha_hash = hash_senha(senha)

                cursor.execute("""
                    INSERT INTO usuarios (id, nome, email, senha, data_nasc, role)
                    VALUES (%s, %s, %s, %s, %s, 'usuario')
                """, (usuario_id, nome, email, senha_hash, data_nasc))

                usuarios_map[email] = usuario_id
                print(f"✅ Inserido: {nome}")

            except Exception as e:
                print(f"❌ Erro: {e}")
                conn.rollback()

        conn.commit()

    print(f"\n✅ Usuários mapeados: {len(usuarios_map)}")
    return usuarios_map


def buscar_livros():
    """Busca todos os livros e retorna mapeamento titulo -> id."""
    livros_map = {}

    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, titulo FROM livros WHERE status_aprovacao = 'aprovado'
        """)

        for row in cursor.fetchall():
            livros_map[row[1]] = row[0]  # titulo -> id

    print(f"📚 Livros mapeados: {len(livros_map)}")
    return livros_map


def popular_leituras(usuarios_map, livros_map):
    """Insere leituras baseado nos títulos."""
    print("\n" + "=" * 60)
    print("📖 INSERINDO LEITURAS")
    print("=" * 60 + "\n")

    total = 0
    erros = 0

    with get_connection() as conn:
        cursor = conn.cursor()

        for email, leituras in leituras_por_usuario.items():
            usuario_id = usuarios_map.get(email)

            if not usuario_id:
                print(f"⚠️  Usuário não encontrado: {email}")
                continue

            nome = email.split('@')[0].capitalize()
            inseridos = 0

            for titulo, nota in leituras:
                livro_id = livros_map.get(titulo)

                if not livro_id:
                    print(f"   ⚠️  Livro não encontrado: {titulo}")
                    erros += 1
                    continue

                # Verificar se já existe
                cursor.execute("""
                    SELECT id FROM leituras 
                    WHERE id_usuario = %s AND id_livro = %s
                """, (usuario_id, livro_id))

                if cursor.fetchone():
                    continue

                # Inserir leitura
                try:
                    cursor.execute("""
                        INSERT INTO leituras (id, id_usuario, id_livro, status, avaliacao, data_leitura)
                        VALUES (%s, %s, %s, 'lido', %s, '2024-06-15')
                    """, (str(uuid.uuid4()), usuario_id, livro_id, nota))

                    inseridos += 1
                    total += 1

                except Exception as e:
                    print(f"   ❌ Erro: {e}")
                    conn.rollback()

            print(f"👤 {nome}: {inseridos} leituras")

        conn.commit()

    print(f"\n✅ Total de leituras: {total}")
    if erros > 0:
        print(f"⚠️  Livros não encontrados: {erros}")


def mostrar_estatisticas():
    """Mostra estatísticas finais."""
    print("\n" + "=" * 60)
    print("📊 ESTATÍSTICAS FINAIS")
    print("=" * 60 + "\n")

    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM usuarios")
        print(f"👥 Usuários: {cursor.fetchone()[0]}")

        cursor.execute("SELECT COUNT(*) FROM livros WHERE status_aprovacao = 'aprovado'")
        print(f"📚 Livros: {cursor.fetchone()[0]}")

        cursor.execute("SELECT COUNT(*) FROM leituras")
        print(f"📖 Leituras: {cursor.fetchone()[0]}")

        cursor.execute("SELECT COUNT(*) FROM leituras WHERE avaliacao IS NOT NULL")
        print(f"⭐ Com avaliação: {cursor.fetchone()[0]}")

        cursor.execute("SELECT AVG(avaliacao) FROM leituras WHERE avaliacao IS NOT NULL")
        media = cursor.fetchone()[0] or 0
        print(f"📈 Média: {media:.2f}")

    print("\n" + "=" * 60)
    print("✅ BANCO POPULADO!")
    print("=" * 60 + "\n")


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":
    print("\n🚀 Populando banco de dados...\n")

    # 1. Buscar livros existentes
    livros_map = buscar_livros()

    # 2. Inserir/buscar usuários
    usuarios_map = popular_usuarios()

    # 3. Inserir leituras
    popular_leituras(usuarios_map, livros_map)

    # 4. Estatísticas
    mostrar_estatisticas()