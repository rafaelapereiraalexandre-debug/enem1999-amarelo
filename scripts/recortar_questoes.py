import cv2
import pytesseract
import re
import os

# ----------------- CONFIGURAÇÕES (AJUSTE AQUI SE PRECISAR) -----------------
# Se o Tesseract não estiver no PATH do Windows, descomente e informe o caminho:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

PASTA_ORIGINAIS = "../imagens_originais"
PASTA_QUESTOES = "../questoes_recortadas"
NUMERO_QUESTOES = 63   # ENEM 1999 teve 63 questões
# -------------------------------------------------------------------------

os.makedirs(PASTA_QUESTOES, exist_ok=True)

def encontrar_numeros_questoes(imagem):
    """Retorna lista com número e coordenada y de cada questão detectada."""
    gray = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

    dados = pytesseract.image_to_data(thresh, lang='por', output_type=pytesseract.Output.DICT)

    questoes = []
    for i in range(len(dados['text'])):
        texto = dados['text'][i].strip()
        # Padrão para "01", "1.", "1-", "01 -", etc.
        match = re.match(r'^(\d{1,2})\s*[\.\-\–]?', texto)
        if match:
            num = int(match.group(1))
            if 1 <= num <= NUMERO_QUESTOES:
                y = dados['top'][i]
                h = dados['height'][i]
                questoes.append({
                    'numero': num,
                    'y_centro': y + h // 2,
                    'y_topo': y,
                    'altura': h
                })
    # Remove duplicatas (mantendo a primeira ocorrência de cada número)
    vistos = set()
    unicas = []
    for q in questoes:
        if q['numero'] not in vistos:
            vistos.add(q['numero'])
            unicas.append(q)
    unicas.sort(key=lambda q: q['numero'])
    return unicas

def recortar_pagina(caminho_imagem):
    img = cv2.imread(caminho_imagem)
    if img is None:
        print(f"Erro ao ler {caminho_imagem}")
        return
    altura, largura = img.shape[:2]
    questoes = encontrar_numeros_questoes(img)
    if len(questoes) < 2:
        print(f"  Poucas questões encontradas em {caminho_imagem}, pulando.")
        return

    print(f"  {len(questoes)} questões identificadas.")
    for i in range(len(questoes) - 1):
        q_atual = questoes[i]
        q_prox = questoes[i+1]
        # Topo: um pouco acima do número da questão atual
        topo = max(0, q_atual['y_topo'] - 20)
        # Base: um pouco acima do número da próxima questão
        base = min(q_prox['y_topo'] - 10, altura)
        if base - topo < 50:
            continue
        recorte = img[topo:base, 0:largura]
        nome = f"Q{q_atual['numero']:02d}.png"
        cv2.imwrite(os.path.join(PASTA_QUESTOES, nome), recorte)
        print(f"    {nome} salva.")
    
    # Última questão da página (vai até o final da imagem)
    ultima = questoes[-1]
    topo = max(0, ultima['y_topo'] - 20)
    base = altura
    recorte = img[topo:base, 0:largura]
    nome = f"Q{ultima['numero']:02d}.png"
    cv2.imwrite(os.path.join(PASTA_QUESTOES, nome), recorte)
    print(f"    {nome} salva.")

# Processar todas as imagens na pasta originais
arquivos = sorted([
    f for f in os.listdir(PASTA_ORIGINAIS)
    if f.lower().endswith(('.png', '.jpg', '.jpeg'))
])

if not arquivos:
    print("Nenhuma imagem encontrada em 'imagens_originais'. Coloque as imagens lá primeiro.")
else:
    for arquivo in arquivos:
        caminho = os.path.join(PASTA_ORIGINAIS, arquivo)
        print(f"Processando {arquivo}...")
        recortar_pagina(caminho)
    print("\n✅ Recorte finalizado! Verifique a pasta 'questoes_recortadas'.")