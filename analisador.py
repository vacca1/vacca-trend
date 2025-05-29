import cv2
import numpy as np

def analisar_tendencia(caminho_imagem):
    imagem = cv2.imread(caminho_imagem)
    if imagem is None:
        return {
            "sinal": "NEUTRO",
            "linhas_detectadas": 0,
            "timeframe": "DESCONHECIDO"
        }

    cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    altura, largura = cinza.shape
    recorte = cinza[0:altura, int(largura * 0.85):largura]

    if "_M1" in caminho_imagem or "1M" in caminho_imagem or "1m" in caminho_imagem:
        minLineLength = 15
        maxLineGap = 3
        limite_inclinacao = 0.2
        timeframe = "M1"
    else:
        minLineLength = 25
        maxLineGap = 5
        limite_inclinacao = 0.15
        timeframe = "M5"

    bordas = cv2.Canny(recorte, 50, 150)
    linhas = cv2.HoughLinesP(bordas, 1, np.pi / 180, threshold=40,
                              minLineLength=minLineLength, maxLineGap=maxLineGap)

    resultado = {
        "sinal": "NEUTRO",
        "linhas_detectadas": 0,
        "timeframe": timeframe
    }

    if linhas is None:
        return resultado

    inclinacoes = []

    for linha in linhas:
        for x1, y1, x2, y2 in linha:
            if x2 - x1 == 0:
                continue
            inclinacao = (y2 - y1) / (x2 - x1)
            if abs(inclinacao) > 0.05:
                inclinacoes.append(inclinacao)

    if not inclinacoes:
        return resultado

    media = np.mean(inclinacoes)
    resultado["linhas_detectadas"] = len(inclinacoes)

    if media < -limite_inclinacao:
        resultado["sinal"] = "CALL"
    elif media > limite_inclinacao:
        resultado["sinal"] = "PUT"

    return resultado
