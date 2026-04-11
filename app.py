import os
import glob
import subprocess
from flask import Flask, render_template, request, jsonify, send_file, url_for

# Configura as pastas modularmente
app = Flask(__name__, template_folder='web/templates', static_folder='web/static')
app.config['UPLOAD_FOLDER'] = 'imgs'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analisar', methods=['POST'])
def analisar():
    if 'image' not in request.files:
        return jsonify({'error': 'Nenhuma imagem enviada.'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'Nome de arquivo vazio.'}), 400
        
    # Limpa imagens analisadas e laudos antigos para esta POC
    for f in glob.glob("laudo_*.pdf"):
        try: os.remove(f)
        except: pass
    try: os.remove(os.path.join(app.config['UPLOAD_FOLDER'], 'imagem_analisada_medica.jpg'))
    except: pass
        
    filename = "temp_upload.jpg"
    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(upload_path)
    
    # Chama o script do terminal
    result = subprocess.run(["python", "analisador_objetos.py", upload_path], capture_output=True, text=True)
    
    # Verifica se a imagem final foi gerada
    img_analisada = os.path.join(app.config['UPLOAD_FOLDER'], 'imagem_analisada_medica.jpg')
    if not os.path.exists(img_analisada):
        return jsonify({
            'error': 'Erro ao analisar a imagem. O marcador ArUco ou objeto pode não ter sido detectado.',
            'logs': result.stdout + "\n" + result.stderr
        }), 500
        
    # Busca qual laudo foi gerado
    laudos = glob.glob("laudo_*.pdf")
    laudo_path = laudos[0] if laudos else None
    
    return jsonify({
        'success': True,
        'image_url': url_for('get_image', filename='imagem_analisada_medica.jpg'),
        'pdf_url': url_for('get_pdf', filename=laudo_path) if laudo_path else None,
        'logs': result.stdout
    })

@app.route('/imgs/<filename>')
def get_image(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), mimetype='image/jpeg')

@app.route('/pdf/<filename>')
def get_pdf(filename):
    return send_file(filename, mimetype='application/pdf', as_attachment=False)

if __name__ == '__main__':
    # Cria pasta imgs se não existir
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    print("Iniciando o servidor da Interface Web da Dasa em http://localhost:5000")
    app.run(debug=True, port=5000)
