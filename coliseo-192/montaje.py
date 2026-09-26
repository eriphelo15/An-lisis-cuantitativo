"""Arma el documental "Un día en el Coliseo" a partir de las tomas renderizadas.

Cada imagen recibe un movimiento lento de cámara (acercamiento + paneo), fundidos
entre tomas y subtítulos con el relato histórico. Salida: MP4 H.264 1920x1080.
Uso: python3 montaje.py
"""
import os, subprocess, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import imageio_ffmpeg

HERE = os.path.dirname(os.path.abspath(__file__))
REN = os.path.join(HERE, 'render')
OUT = os.path.join(HERE, 'un_dia_en_el_coliseo.mp4')
W, H, FPS = 1920, 1080, 24
SHOT_S, FADE_S = 7.5, 1.2

SERIF = '/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf'
SERIF_B = '/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf'
SERIF_I = '/usr/share/fonts/truetype/freefont/FreeSerifItalic.ttf'

TOMAS = [
    ('01_amanecer', 'AMANECER', 'Roma, año 192 d. C.', 'El Anfiteatro Flavio despierta junto al Coloso de Nerón, al que Cómodo le puso su propio rostro.', (1.0, 1.1, -0.02, 0.0)),
    ('02_llegada', 'PRIMERA HORA', 'Llega el público', 'Cada entrada lleva un número tallado. La tésera de cada espectador indica su puerta, su sector y su fila.', (1.06, 1.0, 0.0, 0.02)),
    ('03_velario', 'MEDIA MAÑANA', 'El velario', 'Marineros de la flota de Miseno despliegan el toldo gigante sobre 240 mástiles.', (1.0, 1.08, 0.03, 0.0)),
    ('04_gradas', 'LA CÁVEA', 'Cincuenta mil personas', 'Senadores en el podio, la plebe más arriba y las mujeres en lo más alto. El emperador ocupa el pulvinar.', (1.0, 1.12, 0.0, 0.03)),
    ('05_pompa', 'LA POMPA', 'El desfile de apertura', 'Músicos, gladiadores con capas de púrpura y la imagen de los dioses entran por la Porta Triumphalis.', (1.04, 1.0, -0.03, 0.0)),
    ('06_venatio', 'LA MAÑANA', 'Venationes', 'Sobre un bosque de escenografía, los bestiarios enfrentan leones, osos y avestruces traídos de todo el imperio.', (1.0, 1.1, 0.02, -0.01)),
    ('07_mediodia', 'MEDIODÍA', 'Bajo el toldo', 'El sol cae a plomo sobre Roma. El velario mantiene la sombra sobre las gradas.', (1.1, 1.0, 0.0, 0.0)),
    ('08_gladiadores', 'LA TARDE', 'Munera gladiatoria', 'Parejas de murmillo y tracio combaten bajo la mirada del árbitro, la summa rudis.', (1.0, 1.12, -0.02, 0.01)),
    ('09_comodo', 'EL EMPERADOR EN LA ARENA', 'Cómodo como Hércules', 'Según Dión Casio, Cómodo bajaba a la arena con piel de león y maza, y abatía avestruces ante el público.', (1.0, 1.08, 0.0, 0.02)),
    ('10_atardecer', 'ATARDECER', 'La salida', 'El público vuelve a la ciudad. Cómodo moriría asesinado meses después, el 31 de diciembre de 192.', (1.08, 1.0, 0.02, 0.0)),
]

def font(path, size):
    return ImageFont.truetype(path, size)

def ease(t):
    return 0.5 - 0.5 * math.cos(math.pi * max(0.0, min(1.0, t)))

def kenburns(img, t, params):
    z0, z1, px, py = params
    z = z0 + (z1 - z0) * ease(t)
    cw, ch = W / z, H / z
    cx = W / 2 + px * W * (ease(t) - .5); cy = H / 2 + py * H * (ease(t) - .5)
    x0, y0 = cx - cw / 2, cy - ch / 2
    return img.transform((W, H), Image.AFFINE, (cw / W, 0, x0, 0, ch / H, y0), resample=Image.BICUBIC)

def caption_layer(k, t, title, sub, text):
    """Capa RGBA con el subtítulo de la toma; aparece y desaparece suavemente."""
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    a = min(ease((t - 0.08) / 0.12), ease((0.92 - t) / 0.12))
    if a <= 0: return lay
    d = ImageDraw.Draw(lay)
    grad = Image.new('L', (1, 380)); grad.putdata([int(170 * (i / 379) ** 1.6) for i in range(380)])
    lay.paste(Image.new('RGBA', (W, 380), (0, 0, 0, 255)), (0, H - 380), grad.resize((W, 380)))
    x, y = 110, H - 250
    d.text((x, y), title, font=font(SERIF_B, 26), fill=(217, 168, 102, 255), spacing=4)
    d.text((x, y + 40), sub, font=font(SERIF, 62), fill=(246, 239, 227, 255))
    d.text((x, y + 122), text, font=font(SERIF_I, 32), fill=(232, 222, 205, 255))
    al = lay.getchannel('A').point(lambda v: int(v * a)); lay.putalpha(al)
    return lay

def title_card(t, lines):
    img = Image.new('RGB', (W, H), (8, 7, 6)); d = ImageDraw.Draw(img)
    a = min(ease(t / 0.25), ease((1 - t) / 0.25))
    for text, fnt, y, col in lines:
        f = font(*fnt); w = d.textlength(text, font=f)
        d.text(((W - w) / 2, y), text, font=f, fill=tuple(int(c * a) for c in col))
    return img

def main():
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    proc = subprocess.Popen([ff, '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                             '-c:v', 'libx264', '-preset', 'slow', '-crf', '19', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', OUT],
                            stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    def emit(im): proc.stdin.write(np.asarray(im.convert('RGB'), dtype=np.uint8).tobytes())
    intro = [('UN DÍA EN EL COLISEO', (SERIF, 96), 430, (240, 232, 218)), ('ROMA · AÑO 192 D. C. · REINADO DE CÓMODO', (SERIF, 34), 560, (217, 168, 102))]
    n = int(4.5 * FPS)
    for i in range(n): emit(title_card(i / (n - 1), intro))
    imgs = [(Image.open(os.path.join(REN, f + '.png')).convert('RGB').resize((W, H), Image.LANCZOS), rest) for f, *rest in TOMAS if os.path.exists(os.path.join(REN, f + '.png'))]
    shot_n, fade_n = int(SHOT_S * FPS), int(FADE_S * FPS)
    prev_tail = None
    for k, (img, (title, sub, text, kb)) in enumerate(imgs):
        for i in range(shot_n):
            t = i / (shot_n - 1)
            fr = kenburns(img, t, kb)
            cap = caption_layer(k, t, title, sub, text)
            fr = Image.alpha_composite(fr.convert('RGBA'), cap).convert('RGB')
            if k == 0 and i < fade_n:  # entrada desde negro
                fr = Image.blend(Image.new('RGB', (W, H)), fr, i / fade_n)
            if prev_tail is not None and i < fade_n:
                fr = Image.blend(prev_tail[i], fr, (i + 1) / (fade_n + 1))
            if k < len(imgs) - 1 and i >= shot_n - fade_n:
                continue  # estas últimas imágenes se funden con la toma siguiente
            emit(fr)
        prev_tail = [Image.alpha_composite(kenburns(img, (shot_n - fade_n + j) / (shot_n - 1), kb).convert('RGBA'),
                                           caption_layer(k, (shot_n - fade_n + j) / (shot_n - 1), title, sub, text)).convert('RGB') for j in range(fade_n)]
        print('toma', k + 1, 'lista', flush=True)
    last = fr
    for i in range(fade_n * 2): emit(Image.blend(last, Image.new('RGB', (W, H)), i / (fade_n * 2 - 1)))
    outro = [('Reconstrucción generada con código', (SERIF_I, 38), 470, (232, 222, 205)),
             ('Blender Cycles · geometría y materiales procedurales · figuras simplificadas', (SERIF, 28), 540, (180, 170, 155))]
    n = int(4 * FPS)
    for i in range(n): emit(title_card(i / (n - 1), outro))
    proc.stdin.close(); proc.wait()
    print('OK', OUT, round(os.path.getsize(OUT) / 1e6, 1), 'MB')

if __name__ == '__main__':
    main()
