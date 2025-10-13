# finder.py
import requests # Importa a biblioteca que acabamos de instalar

print("--- DevFinder Command Line ---")
username = input("Digite o nome de usuário do GitHub: ")

# Cria a URL da API, substituindo o username pelo que foi digitado
url = f"https://api.github.com/users/{username}"

print(f"Buscando informações para o usuário: {username}...")

# Faz a chamada para a API do GitHub
response = requests.get(url)

# Verifica se a resposta foi um sucesso (código 200)
if response.status_code == 200:
    # Transforma a resposta (que é um texto em formato JSON) em um dicionário Python
    user_data = response.json()

    # Extrai e imprime as informações que queremos
    print("\n--- DADOS DO USUÁRIO ---")
    print(f"Nome: {user_data.get('name')}")
    print(f"Bio: {user_data.get('bio')}")
    print(f"Localização: {user_data.get('location')}")
    print(f"Seguidores: {user_data.get('followers')}")
    print(f"Repositórios Públicos: {user_data.get('public_repos')}")
    print(f"Link do Perfil: {user_data.get('html_url')}")
    print("------------------------")
else:
    # Se a resposta não foi um sucesso, exibe uma mensagem de erro
    print(f"\nERRO: Não foi possível encontrar o usuário '{username}'.")
    print(f"Código de Status: {response.status_code}")