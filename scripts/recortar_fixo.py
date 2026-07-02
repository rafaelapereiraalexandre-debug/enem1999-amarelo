import cv2
import os

PASTA_ORIGINAIS = "../imagens_originais"
PASTA_QUESTOES = "../questoes_recortadas"
os.makedirs(PASTA_QUESTOES, exist_ok=True)

# Lista das páginas que contêm questões (ajuste os índices conforme identificado)
# Exemplo: se as questões estão nas páginas 3 a 9, use range(3, 10)
PAGINAS_QUESTOES = [3, 4, 5, 6, 7, 8, 9]  # <-- ALTERE AQUI DEPOIS DE VERIFICAR

questao_atual = 1

for num_pagina in PAGINAS_QUESTOES:
    arquivo = f"pagina_{num_pagina:02d}.png"
    caminho = os.path.join(PASTA_ORIGINAIS, arquivo)
    if not os.path.exists(caminho):
        print(f"Página {arquivo} não encontrada, pulando.")
        continue
    
    img = cv2.imread(caminho)
    if img is None:
        print(f"Erro ao ler {arquivo}.")
        continue
    
    altura, largura = img.shape[:2]
    
    # Divide a página em 3 colunas e 3 linhas (9 questões)
    col_w = largura // 3
    row_h = altura // 3
    
    for row in range(3):
        for col in range(3):
            x1 = col * col_w
            y1 = row * row_h
            x2 = x1 + col_w
            y2 = y1 + row_h
            recorte = img[y1:y2, x1:x2]
            
            nome = f"Q{questao_atual:02d}.png"
            cv2.imwrite(os.path.join(PASTA_QUESTOES, nome), recorte)
            print(f"{nome} salva da página {num_pagina}.")
            questao_atual += 1

print(f"Total de questões recortadas: {questao_atual - 1}")