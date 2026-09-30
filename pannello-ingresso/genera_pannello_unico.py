# Pannello unico 400 x 550 mm: ShopNow in alto, Monaci Digitali in basso (1 unita' SVG = 1 mm)
#
# Produce:
#   bozza_pannello_unico_40x55.svg   con lo strato GUIDE per la revisione
#   pannello_unico_40x55_stampa.svg  per lo stampatore: niente GUIDE, fori o sfondo, testi in curve
#   anteprima_pannello_unico.png
#
# Riusa i pezzi di genera_bozza.py; logo Monaci da prepara_monaci.py (loghi/monaci_logo.svg).
import os
import re

from genera_bozza import (W, H, M, INK, QUI, apri, griglia, payoff, logo_shopnow, misura, testo, anteprima)

MONACO = True     # False = solo la scritta MONACI DIGITALI, senza il monaco

# Servizi Monaci Digitali (dal sito: Education, Consulting/Digital Agency, Start-up/Hackathon/Startup Village)
SERVIZI = [
    ("FORMAZIONE", "Percorsi per aziende, professionisti e team"),
    ("CONSULENZA DIGITALE", "Strategia, digital agency e soluzioni per le imprese"),
    ("OPEN INNOVATION", "Startup, hackathon e incubazione d’impresa"),
]

# fasce verticali (mm)
LOGO_Y, LOGO_W = 40, 210            # logo ShopNow ridotto da 300 a 210 mm
GRIGLIA = (138, 323)                # 5 file da 37 mm
DIVISORIO = 345
MONACI = (363, 507)                 # fascia Monaci Digitali


def logo_monaci(x, y, altezza, monaco=True):
    src = open(os.path.join(QUI, "loghi", "monaci_logo.svg"), encoding="utf-8").read()
    vw, vh = [float(v) for v in re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', src).groups()]
    gruppi = dict(re.findall(r'<g id="(\w+)" fill="[^"]+">(.*?)</g>', src))
    if monaco:
        corpo, y0, h = gruppi["MONACO"] + gruppi["SCRITTA"], 0.0, vh
    else:   # solo scritta: ritaglio alla sua fascia
        ys = [float(v) for v in re.findall(r"[\d.]+,([\d.]+)", gruppi["SCRITTA"])]
        corpo, y0, h = gruppi["SCRITTA"], min(ys), max(ys) - min(ys)
    s = altezza / h
    g = (f'<g id="LOGO_MONACI" fill="#000000" transform="translate({x:.2f} {y - y0 * s:.2f}) '
         f'scale({s:.5f})">{corpo}</g>')
    return g, vw * s


def testo_sx(pezzi, corpo, x, base, spaziatura=0.0, **attr):
    """Testo allineato a sinistra in x."""
    larg = misura(pezzi, corpo, spaziatura)[1]
    return testo(pezzi, corpo, x + larg / 2, base, spaziatura, **attr)[0]


def componi(guide=True, sfondo=True, fori=True):
    canali, linee = griglia(*GRIGLIA, area=18 * 70, h_max=20)
    linee = linee + [f'<rect x="{M}" y="{MONACI[0]}" width="{W-2*M}" height="{MONACI[1]-MONACI[0]}" stroke-width="0.2"/>']
    out = apri(guide, sfondo, fori, linee)

    # --- ShopNow
    g, lh = logo_shopnow((W - LOGO_W) / 2, LOGO_Y, LOGO_W)
    out.append(g)
    out.append(payoff(LOGO_Y + lh + 22, corpo=9.5))
    out.append(canali)

    # --- divisorio a tutta larghezza
    out.append(f'<line id="DIVISORIO" x1="{M}" y1="{DIVISORIO}" x2="{W-M}" y2="{DIVISORIO}" '
               f'stroke="{INK}" stroke-width="0.4"/>')

    # --- Monaci Digitali: logo a sinistra, servizi a destra, centrati in verticale nella fascia
    y0, y1 = MONACI
    alt = 126 if MONACO else 34
    lx = M + 12
    g, lw = logo_monaci(lx, (y0 + y1 - alt) / 2, alt, MONACO)
    out.append(g)

    tx = lx + lw + 26                     # colonna testi
    passo, titolo, descr = 37, 9.2, 7.2
    blocco = passo * (len(SERVIZI) - 1) + titolo * 0.7 + 4 + descr
    base = (y0 + y1 - blocco) / 2 + titolo * 0.7
    out.append('<g id="SERVIZI_MONACI">')
    for i, (t, d) in enumerate(SERVIZI):
        yb = base + passo * i
        out.append(testo_sx([(t, 600)], titolo, tx, yb, spaziatura=0.1))
        out.append(testo_sx([(d, 300)], descr, tx, yb + 4 + descr * 0.95, spaziatura=0.01))
    out.append('</g>')
    out.append('</svg>')
    return "\n".join(out)


if __name__ == "__main__":
    os.chdir(QUI)
    open("bozza_pannello_unico_40x55.svg", "w", encoding="utf-8").write(componi(guide=True, sfondo=True))
    open("pannello_unico_40x55_stampa.svg", "w", encoding="utf-8").write(componi(guide=False, sfondo=False, fori=False))
    anteprima(componi(guide=False, sfondo=True), "anteprima_pannello_unico.png")
    print("ok: bozza_pannello_unico_40x55.svg, pannello_unico_40x55_stampa.svg, anteprima_pannello_unico.png")
