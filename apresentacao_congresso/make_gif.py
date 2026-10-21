"""Monta o GIF de 5 s (2x2) com os quadros reais das MDs de 10 ns (pH 10,0) dos 4 candidatos.

Quadros: PyMOL no servidor (render_cand.py), 101 estados por trajetoria (a cada 0,1 ns), alinhados
no esqueleto do receptor. Nenhum quadro e interpolado ou sintetico.

Uso: python apresentacao_congresso/make_gif.py <pasta com gif_<SEQ>/>
"""
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
ENTRADA = Path(sys.argv[1])
SAIDA = AQUI / "imagens"
SAIDA.mkdir(exist_ok=True)

CANDS = [("NGGRPDAP", "linear", "A. gemmatalis", (0, 114, 178)),
         ("GQNDS", "linear", "O. nubilalis", (0, 114, 178)),
         ("GGKPGEP", "cíclico", "A. gemmatalis", (42, 157, 143)),
         ("GGHSE", "cíclico", "S. frugiperda", (42, 157, 143))]
T = 340
CAB = 54                     # altura do cabecalho de cada quadro
N = 101
F_B = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 22)
F_R = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 17)
F_T = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 20)

quadros = []
for i in range(1, N + 1):
    tela = Image.new("RGB", (4 * T, T + CAB), "white")
    d = ImageDraw.Draw(tela)
    for k, (seq, forma, esp, cor) in enumerate(CANDS):
        x0, y0 = k * T, 0
        im = Image.open(ENTRADA / f"gif_{seq}" / f"f{i:03d}.png").convert("RGB").resize((T, T), Image.LANCZOS)
        tela.paste(im, (x0, y0 + CAB))
        d.rectangle([x0, y0, x0 + T - 1, y0 + 6], fill=cor)
        d.text((x0 + 14, y0 + 12), seq, font=F_B, fill=(31, 35, 40))
        d.text((x0 + 14 + d.textlength(seq, font=F_B) + 12, y0 + 16), f"{forma} · {esp}", font=F_R, fill=(90, 95, 102))
        d.text((x0 + T - 14, y0 + CAB + T - 30), f"{(i - 1) * 0.1:.1f} ns".replace(".", ","), font=F_T,
               fill=(31, 35, 40), anchor="ra")
    quadros.append(tela)

gif = SAIDA / "md_4candidatos_5s.gif"
g2 = quadros[::2]
g2[0].save(gif, save_all=True, append_images=g2[1:], duration=100, loop=0, optimize=True,
                disposal=2)
print(gif, gif.stat().st_size // 1024, "KB", len(g2), "quadros =", len(g2) * 0.1, "s")

# mp4 (mesmos quadros) e quadro-poster
tmp = AQUI / "_frames_gif"
tmp.mkdir(exist_ok=True)
for i, q in enumerate(quadros):
    q.save(tmp / f"q{i:03d}.png")
mp4 = SAIDA / "md_4candidatos_5s.mp4"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "20", "-i", str(tmp / "q%03d.png"),
                "-pix_fmt", "yuv420p", "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2", str(mp4)], check=True)
quadros[-1].save(SAIDA / "md_4candidatos_poster.png")
for f in tmp.glob("*.png"):
    f.unlink()
tmp.rmdir()
print(mp4)
