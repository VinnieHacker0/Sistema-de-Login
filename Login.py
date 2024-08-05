import PySimpleGUI as sg
import sqlite3
import bcrypt
from cryptography.fernet import Fernet

def gerar_chave():
    key = Fernet.generate_key()
    with open('chave.key', 'wb') as chave_file:
         chave_file.write(key)
    return key
try:
    with open('chave.key', 'rb') as chave_file:
        chave = chave_file.read()
except FileNotFoundError:
    chave = gerar_chave()
fernet = Fernet(chave)

def criar_banco_de_dados():
    try:
        conn = sqlite3.connect('usuarios.db')
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                senha TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()
        print("Banco de dados criado com sucesso!")
    except sqlite3.Error as e:
        print(f"Erro ao criar banco de dados:{e}")


def hash_senha(senha):
    senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt())
    return senha_hash.decode()
def verificar_login(nome, senha):
    try:
        conn = sqlite3.connect('usuarios.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE nome=? AND senha=?", (nome, senha))
        usuario = cursor.fetchone()
        conn.close()

        if usuario:
            senha_hash_armazenada = usuario[0]
            if bcrypt.checkpw(senha.encode(), senha_hash_armazenada.encode()):
                return True
            return False
    except sqlite3.Error as e:
        print(f"Erro ao verificar login: {e}")
        return False

def adicionar_usuario(nome, senha):
    try:
        conn = sqlite3.connect('usuarios.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (nome, senha) VALUES (?, ?)", (nome, senha))
        conn.commit()
        conn.close()
        print("Usuario adicionado com sucesso!")
    except sqlite3.Error as e:
        print(f"Erro ao adicionar usuario: {e}")

def criptografar_dados(dados):
    return fernet.encrypt(dados.encode()).decode()

def descriptografar_dados(dados_criptografados):
    return fernet.decrypt(dados_criptografados.encode()).decode()

sg.theme_list()
sg.theme('DarkAmber')

layout = [
    [sg.Text("Nome de Usuario:",justification='left')],
    [sg.InputText(key='-NOME-', size=(30,1), justification="center")],
    [],
    [sg.Text("Senha:", justification='left')],
    [sg.InputText(key='-SENHA-', password_char='*')],
    [sg.Checkbox('Salvar login')],
    [],
    [sg.Button("Login", size=(10, 1)), sg.Button("Cancelar", size=(10, 1))],
    [],
    [sg.Output(size=(60, 10), background_color='black')]
]

window = sg.Window("Login", layout, location=(0, 0))

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == "Cancelar":
        break
    elif event == "Login":
        nome = values['-NOME-']
        senha = values['-SENHA-']

        if verificar_login(nome, senha):
            sg.popup("Login bem-sucedido!")
        else:
            sg.popup_error("Login invalido. Tente novamente.")

window.close()
