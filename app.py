import os
from flask import Flask, render_template

# Configura as pastas static e templates
app = Flask(__name__, template_folder='web/templates', static_folder='web/static')

@app.route('/')
def index():
    # Rotas estáticas (como imagens retornadas) vão para o backend
    return render_template('index.html')

if __name__ == '__main__':
    print("Iniciando o servidor FrontEnd da Interface Web da Dasa em http://127.0.0.1:8080")
    print("Certifique-se de que o backend do Chalice está rodando (na pasta backend/ usando 'chalice local')")
    app.run(debug=True, port=8080)
