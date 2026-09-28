# Vettorializza i loghi dei siti in un solo colore (#333333).
# Sorgenti in loghi/sorgenti/ (scaricate dall'header dei siti), output in loghi/mono/<id>.svg:
# un unico tracciato, niente raster, pronto per stampa UV o incisione.
#
# Metodo: maschera "inchiostro" (tutto cio' che non e' sfondo) -> ingrandimento bicubico
# -> soglia -> potrace. Il bianco dentro le forme colorate diventa foro (es. "more" di Buymore).
import os
import sys
import numpy as np
import cv2
import potrace
from PIL import Image

INK = "#333333"
QUI = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(QUI, "loghi", "sorgenti")
OUT = os.path.join(QUI, "loghi", "mono")

# mode "colore": inchiostro = distanza dal bianco (255 - min(R,G,B)), per loghi su sfondo chiaro
# mode "alpha" : inchiostro = trasparenza, per loghi disegnati per sfondo scuro (testo bianco)
# soglia: distanza dal bianco oltre cui un pixel e' inchiostro (piu' alta = tratti piu' sottili)
# taglio: (x0, y0, x1, y1) in frazioni dell'immagine, per escludere riflessi/decorazioni
LOGHI = {
    "letapparelle":    dict(src="letapparelle.png"),
    "tapparelle":      dict(src="tapparelle.png"),
    "doccia":          dict(src="doccia.png"),
    "docciabox":       dict(src="docciabox.jpg", soglia=110, taglio=(0, 0, 1, 0.66)),
    "veneziane":       dict(src="veneziane.png"),
    "tendecristal":    dict(src="tendecristal.png"),
    "zanzariere":      dict(src="zanzariere.jpg", soglia=125),
    "infissifaidate":  dict(src="infissifaidate.png"),
    "finestro":        dict(src="finestro.jpg", soglia=90),
    "lineadoccia":     dict(src="lineadoccia.png"),
    "zeta24":          dict(src="zeta24.jpg", soglia=90),
    "rollmatik":       dict(src="rollmatik.png"),
    "solidstone":      dict(src="solidstone.png"),
    "cleantechnology": dict(src="cleantechnology.png"),
    "kabinedusch":     dict(src="kabinedusch.png"),
    "mamparaducha":    dict(src="mamparaducha.png", soglia=60),
    "youblind":        dict(src="youblind.png", soglia=50),
    "buymore":         dict(src="buymore.png"),
    "startactive":     dict(src="startactive.png", mode="alpha"),
    "amarodelposto":   dict(src="amarodelposto.png", mode="alpha"),
    "monacidigitali":  dict(src="monacidigitali.png"),
}

LATO_MAX = 3000   # lato lungo della bitmap ingrandita che viene tracciata (px)
SCALA_MAX = 10


def maschera(cfg):
    img = Image.open(os.path.join(SRC, cfg["src"])).convert("RGBA")
    a = np.asarray(img).astype(np.float32)
    rgb, alpha = a[..., :3], a[..., 3:] / 255.0
    if cfg.get("mode") == "alpha":
        ink = alpha[..., 0]
    else:
        su_bianco = rgb * alpha + 255.0 * (1 - alpha)
        dist = 255.0 - su_bianco.min(axis=2)
        s = cfg.get("soglia", 80)
        ink = np.clip((dist - s) / 80.0 + 0.5, 0, 1)   # 0.5 esattamente alla soglia
    if "taglio" in cfg:
        h, w = ink.shape
        x0, y0, x1, y1 = cfg["taglio"]
        m = np.zeros_like(ink)
        m[int(y0 * h):int(y1 * h), int(x0 * w):int(x1 * w)] = 1
        ink = ink * m
    return ink


def ritaglia(ink, margine=2):
    # via puntini isolati (rumore JPEG) prima di calcolare il riquadro utile
    b = (ink > 0.5).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(b, 8)
    tieni = np.zeros(n, bool)
    tieni[1:] = st[1:, cv2.CC_STAT_AREA] >= 6
    b = tieni[lab]
    ys, xs = np.nonzero(b)
    y0, y1 = max(ys.min() - margine, 0), min(ys.max() + margine + 1, ink.shape[0])
    x0, x1 = max(xs.min() - margine, 0), min(xs.max() + margine + 1, ink.shape[1])
    ink = np.where(tieni[lab] | (ink < 0.5), ink, 0)
    return ink[y0:y1, x0:x1]


def traccia(ink):
    h, w = ink.shape
    k = max(1.0, min(SCALA_MAX, LATO_MAX / max(w, h)))
    big = cv2.resize(ink, (round(w * k), round(h * k)), interpolation=cv2.INTER_CUBIC)
    big = cv2.GaussianBlur(big, (0, 0), sigmaX=k * 0.35)
    nero = big > 0.5
    plist = potrace.Bitmap(~nero).trace(turdsize=int(3 * k * k), alphamax=1.0,
                                        opticurve=True, opttolerance=0.2)
    d = []
    f = lambda p: f"{p.x / k:.2f},{p.y / k:.2f}"
    for curve in plist:
        d.append("M" + f(curve.start_point))
        for s in curve.segments:
            if s.is_corner:
                d.append("L" + f(s.c) + "L" + f(s.end_point))
            else:
                d.append("C" + f(s.c1) + " " + f(s.c2) + " " + f(s.end_point))
        d.append("Z")
    return "".join(d), w, h


def main(solo=None):
    os.makedirs(OUT, exist_ok=True)
    for nome, cfg in LOGHI.items():
        if solo and nome not in solo:
            continue
        d, w, h = traccia(ritaglia(maschera(cfg)))
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
               f'width="{w}" height="{h}">\n<path fill="{INK}" fill-rule="evenodd" d="{d}"/>\n</svg>\n')
        open(os.path.join(OUT, nome + ".svg"), "w", encoding="utf-8").write(svg)
        print(f"{nome:16s} {w}x{h}  rapporto {w / h:.2f}")


if __name__ == "__main__":
    main(sys.argv[1:])
