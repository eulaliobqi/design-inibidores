"""Monta a animacao explicativa (RFdiffusion -> ProteinMPNN -> Boltz-2 -> MD) para o publico.

Exemplo real: GGKPGEP, A. gemmatalis, esqueleto len7_design_9.
 - etapa 1: 50 passos reais do denoising do RFdiffusion (design_9_Xt-1_traj.pdb)
 - etapa 2: sequencia real devolvida pelo ProteinMPNN para esse esqueleto
 - etapa 3: pose predita pelo Boltz-2 (confianca 0,923, Tabela 4 do manuscrito)
 - etapa 4: 101 quadros reais da MD de 10 ns (pH 10,0), tomados de 2 em 2

Uso: python apresentacao_congresso/make_anim.py <pasta com s1/ s3/ s4/>
"""
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
ENT = Path(sys.argv[1])
SAIDA = AQUI / "imagens"
W, H = 1120, 490
IMG = 490
SEQ = "GGKPGEP"

F_B = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 25)
F_R = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 17)
F_S = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 13)
F_N = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 21)
F_L = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 30)

GRAF = (31, 35, 40)
CLARO = (176, 181, 187)
CORES = [(0, 114, 178), (213, 94, 0), (42, 157, 143), (86, 70, 160)]
ETAPAS = [
    ("RFdiffusion", "desenha o esqueleto: parte de ruído e, em 50 passos, forma o anel no bolso da tripsina"),
    ("ProteinMPNN", "escreve a sequência de aminoácidos que dobra nesse esqueleto"),
    ("Boltz-2", "co-dobra: prediz o complexo peptídeo + tripsina e o encaixe no bolso S1"),
    ("Dinâmica molecular", "10 ns: a pose se mantém no bolso?"),
]


def carrega(p):
    return Image.open(p).convert("RGB").resize((IMG, IMG), Image.LANCZOS)


def quadro(img, ativa, letras=0, extra=None, tempo=None):
    tela = Image.new("RGB", (W, H), "white")
    tela.paste(img, (0, 0))
    d = ImageDraw.Draw(tela)
    x0 = IMG + 28
    for i, (nome, desc) in enumerate(ETAPAS):
        y = 12 + i * 118
        cor = CORES[i] if i == ativa else CLARO
        txt = GRAF if i == ativa else (150, 155, 160)
        d.ellipse([x0, y + 4, x0 + 38, y + 42], fill=cor)
        d.text((x0 + 19, y + 23), str(i + 1), font=F_N, fill="white", anchor="mm")
        d.text((x0 + 56, y), nome, font=F_B, fill=cor)
        # descricao quebrada em 2 linhas
        palavras, linhas, atual = desc.split(), [], ""
        for p in palavras:
            if d.textlength(atual + " " + p, font=F_R) > W - x0 - 70 and atual:
                linhas.append(atual)
                atual = p
            else:
                atual = (atual + " " + p).strip()
        linhas.append(atual)
        for k, ln in enumerate(linhas[:2]):
            d.text((x0 + 56, y + 36 + k * 22), ln, font=F_R, fill=txt)
        if i == ativa and i == 1:                      # sequencia aparecendo
            for j, aa in enumerate(SEQ):
                bx = x0 + 56 + j * 46
                if j < letras:
                    cb = (213, 94, 0) if aa == "K" else CORES[1]
                    d.rounded_rectangle([bx, y + 80, bx + 38, y + 112], radius=6, fill=cb)
                    d.text((bx + 19, y + 96), aa, font=F_L, fill="white", anchor="mm")
                else:
                    d.rounded_rectangle([bx, y + 80, bx + 38, y + 112], radius=6, outline=CLARO, width=2)
        if i == ativa and i == 2 and extra:
            d.text((x0 + 56, y + 84), extra, font=F_R, fill=cor)
        if i == ativa and i == 3 and tempo:
            d.text((x0 + 56, y + 84), tempo, font=F_R, fill=cor)
    d.text((IMG + 28, H - 20), "Exemplo real: GGKPGEP · A. gemmatalis · esqueleto len7_design_9", font=F_S, fill=(138, 144, 151))
    return tela


quadros = []
s1 = [carrega(ENT / "s1" / f"f{k:02d}.png") for k in range(50)]
for im in s1:
    quadros.append(quadro(im, 0))
for j in range(16):                                    # etapa 2: letras
    quadros.append(quadro(s1[-1], 1, letras=min(len(SEQ), int(j / 1.6) + 1)))
boltz = carrega(ENT / "s3" / "boltz.png")
for j in range(14):                                    # etapa 3: transicao para o complexo predito
    a = min(1.0, j / 6)
    quadros.append(quadro(Image.blend(s1[-1], boltz, a), 2, extra="confiança do Boltz-2: 0,92" if j >= 6 else None))
for i in range(51):                                    # etapa 4: MD real
    quadros.append(quadro(carrega(ENT / "s4" / f"f{i:02d}.png"), 3,
                          tempo=f"t = {i * 0.2:.1f} ns".replace(".", ",")))
print(len(quadros), "quadros =", len(quadros) * 0.1, "s")

gif = SAIDA / "como_funciona_RFdiff_MPNN_Boltz_MD.gif"
quadros[0].save(gif, save_all=True, append_images=quadros[1:], duration=100, loop=0, optimize=True, disposal=2)
print(gif, gif.stat().st_size // 1024, "KB")

tmp = AQUI / "_frames_anim"
tmp.mkdir(exist_ok=True)
for i, q in enumerate(quadros):
    q.save(tmp / f"q{i:03d}.png")
mp4 = SAIDA / "como_funciona_RFdiff_MPNN_Boltz_MD.mp4"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "10", "-i", str(tmp / "q%03d.png"),
                "-pix_fmt", "yuv420p", "-vf", "scale=1120:490", "-r", "20", str(mp4)], check=True)
quadros[49].save(SAIDA / "como_funciona_poster.png")
for f in tmp.glob("*.png"):
    f.unlink()
tmp.rmdir()
print(mp4, mp4.stat().st_size // 1024, "KB")
