import os
import sys
import glob
import subprocess
import base64
from chalice import Chalice, Response, CORSConfig

app = Chalice(app_name='dasa-chalice-backend')

# Permite acesso ao backend de outras origens (ex: Flask no 8080)
cors_config = CORSConfig(
    allow_origin='*',
    allow_headers=['Content-Type', 'X-Amz-Date', 'Authorization', 'X-Api-Key', 'X-Amz-Security-Token'],
    max_age=600,
    expose_headers=['Content-Type']
)

# Configura o Chalice para retornar arquivos binários corretamente
app.api.binary_types.extend(['image/jpeg', 'application/pdf'])

# Obtém a raiz do projeto (como este script tá em f:\TCC\backend, sobe 1 nivel)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'imgs')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/analisar', methods=['POST'], cors=cors_config)
def analisar():
    request = app.current_request
    body = request.json_body
    
    if not body or 'image' not in body:
        return Response(body={'error': 'Nenhuma imagem enviada.'}, status_code=400)
        
    image_data = body['image']
    if ',' in image_data:
        image_data = image_data.split(',')[1]
        
    try:
        image_bytes = base64.b64decode(image_data)
    except Exception:
        return Response(body={'error': 'Falha ao decodificar a imagem Base64.'}, status_code=400)
    
    filename = "temp_upload.jpg"
    upload_path = os.path.join(UPLOAD_FOLDER, filename)
    
    # Limpa imagens analisadas e laudos antigos (no diretório BASE_DIR)
    laudos_pattern = os.path.join(BASE_DIR, "laudo_*.pdf")
    for f in glob.glob(laudos_pattern):
        try: os.remove(f)
        except: pass
        
    img_analisada = os.path.join(UPLOAD_FOLDER, 'imagem_analisada_medica.jpg')
    try: os.remove(img_analisada)
    except: pass
    
    with open(upload_path, 'wb') as f:
        f.write(image_bytes)
    
    # Verifica a inserção do modulo analisador nas importacoes sys path
    if BASE_DIR not in sys.path:
        sys.path.append(BASE_DIR)
        
    from analisador_objetos import AnalisadorObjetos
    
    # Chama o script carregando a classe nativamente em vez do subprocess
    analisador = AnalisadorObjetos()
    resultado = analisador.analisar(upload_path)
    
    if not resultado.get("success", False):
        return Response(body={
            'error': resultado.get("error", "Erro ao analisar a imagem. O marcador ArUco ou objeto pode não ter sido detectado."),
            'logs': resultado.get("logs", "")
        }, status_code=500)
        
    laudo_path = resultado.get("laudo_filename")
    
    return {
        'success': True,
        'image_url': f'http://127.0.0.1:8000/imgs/{resultado.get("imagem_name", "imagem_analisada_medica.jpg")}',
        'pdf_url': f'http://127.0.0.1:8000/pdf/{laudo_path}' if laudo_path else None,
        'logs': resultado.get("logs", "")
    }

@app.route('/imgs/{filename}', methods=['GET'], cors=cors_config)
def get_image(filename):
    path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(path):
        with open(path, 'rb') as f:
            content = f.read()
        return Response(body=content, status_code=200, headers={'Content-Type': 'image/jpeg'})
    return Response(body={'error': 'Not found'}, status_code=404)

@app.route('/pdf/{filename}', methods=['GET'], cors=cors_config)
def get_pdf(filename):
    path = os.path.join(BASE_DIR, filename)
    if os.path.exists(path):
        with open(path, 'rb') as f:
            content = f.read()
        return Response(body=content, status_code=200, headers={'Content-Type': 'application/pdf'})
    return Response(body={'error': 'Not found'}, status_code=404)

@app.route('/swagger.json', methods=['GET'], cors=cors_config)
def get_swagger_json():
    swagger_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'swagger.json')
    if os.path.exists(swagger_path):
        with open(swagger_path, 'r', encoding='utf-8') as f:
            return Response(body=f.read(), status_code=200, headers={'Content-Type': 'application/json'})
    return Response(body={'error': 'swagger.json not found'}, status_code=404)

@app.route('/docs', methods=['GET'], cors=cors_config)
def get_docs():
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <title>PathoScan API Docs</title>
      <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui.css" />
    </head>
    <body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js" crossorigin></script>
    <script>
      window.onload = () => {
        window.ui = SwaggerUIBundle({
          url: '/swagger.json',
          dom_id: '#swagger-ui',
        });
      };
    </script>
    </body>
    </html>
    """
    return Response(body=html, status_code=200, headers={'Content-Type': 'text/html'})
