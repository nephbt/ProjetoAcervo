from database import BancoDados, bd
print("✅ Importação funcionou!")
print(f"Tipo de bd: {type(bd)}")
print(f"Número de livros no cache: {len(bd.livros)}")
print(f"Número de usuários no cache: {len(bd.usuarios)}")