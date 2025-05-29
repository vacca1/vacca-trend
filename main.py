from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import cv2
import numpy as np

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return send_from_directory('.', 'formulario.html')

@app.route('/analisar', methods=['POST'])
def analisar():
    arquivo = request.files.get('foto')
    if not arquivo:
        return jsonify({'sinal': 'NEUTRO', 'mensagem': 'Nenhuma imagem enviada'})

    caminho_imagem = 'imagem_recebida.png'
    arquivo.save(caminho_imagem)

    imagem = cv2.imread(caminho_imagem)
    if imagem is None:
        return jsonify({'sinal': 'NEUTRO', 'mensagem': 'Erro ao ler a imagem'})

    imagem_cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    imagem_borrada = cv2.GaussianBlur(imagem_cinza, (5, 5), 0)
    bordas = cv2.Canny(imagem_borrada, 50, 150, apertureSize=3)

    linhas = cv2.HoughLinesP(bordas, 1, np.pi / 180, threshold=80, minLineLength=40, maxLineGap=10)

    if linhas is None or len(linhas) == 0:
        return jsonify({'sinal': 'NEUTRO'})

    angulos = []
    for linha in linhas:
        for x1, y1, x2, y2 in linha:
            if x2 - x1 == 0:
                continue
            angulo = np.degrees(np.arctan2(y2 - y1, x2 - x1))
            if abs(angulo) > 10:
                angulos.append(angulo)

    if not angulos:
        return jsonify({'sinal': 'NEUTRO'})

    angulo_medio = np.mean(angulos)

    if 'm5' in arquivo.filename.lower():
        limite_alta = -7
        limite_baixa = 7
    else:
        limite_alta = -12
        limite_baixa = 12

    if angulo_medio < limite_alta:
        sinal = 'CALL'
    elif angulo_medio > limite_baixa:
        sinal = 'PUT'
    else:
        sinal = 'NEUTRO'

    return jsonify({'sinal': sinal})

@app.route('/<path:nome_arquivo>')
def arquivos_estaticos(nome_arquivo):
    return send_from_directory('.', nome_arquivo)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
