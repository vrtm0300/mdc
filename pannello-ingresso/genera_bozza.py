# Pannello ingresso ShopNow Srl - sede di Salerno - 400 x 550 mm (1 unita' SVG = 1 mm)
#
# Produce:
#   bozza_pannello_40x55.svg   con lo strato GUIDE (margini, fori) per la revisione
#   pannello_40x55_stampa.svg  per lo stampatore: niente GUIDE, fori o sfondo, testi in curve
#   anteprima.png              render del pannello finito (senza guide)
#
# Richiede: loghi/shopnow_logo.svg, loghi/mono/*.svg (da prepara_loghi.py),
# font Montserrat variabile (Google Fonts, OFL) in font/ o installato nel sistema.
import io
import os
import re
import glob
import shutil
import subprocess
import tempfile

import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

QUI = os.path.dirname(os.path.abspath(__file__))
W, H, M = 400, 550, 30
INK = "#333333"   # colore unico per canali e testi (monocromia)

# Canali di vendita, in ordine di griglia (id = file in loghi/mono/)
# 1a fila per importanza; 2a-4a ordine scelto dal cliente; 5a fila: siti esteri.
siti = ["letapparelle", "docciabox", "bricobros", "finestro",
        "cleantechnology", "lineadoccia", "solidstone", "doccia",
        "rollmatik", "tapparelle", "infissifaidate", "buymore",
        "tendecristal", "zeta24", "veneziane", "zanzariere",
        "kabinedusch", "youblind", "mamparaducha", "mosquiteras24"]
# fuori griglia: startactive, amarodelposto (non su misura), monacidigitali (non e' un sito di vendita)

cols, rows = 4, 5
GY0, GY1 = 222, 452           # fascia verticale della griglia
CW = (W - 2 * M) / cols       # passo colonne

# Dimensionamento ottico: stessa area apparente (20 mm x 70 mm per un logo 3.5:1),
# con tetti in altezza e larghezza per restare nella casella.
AREA, H_MAX, W_MAX = 20 * 70, 22, 72
OTTICA = {                    # correzioni a occhio (moltiplicano l'altezza)
    "rollmatik": 0.9, "finestro": 0.9, "zeta24": 0.88, "buymore": 0.88, "cleantechnology": 0.9,
    "mamparaducha": 1.08, "startactive": 1.1, "amarodelposto": 1.05, "bricobros": 0.95,
    "mosquiteras24": 1.06,
}
W_OTTICA = 76                 # tetto di larghezza per i loghi ingranditi a occhio


# ---------------------------------------------------------------- testi in curve
def trova_font():
    nomi = ["Montserrat-VariableFont_wght.ttf", "Montserrat[wght].ttf"]
    dirs = [os.path.join(QUI, "font"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Windows", "Fonts"),
            r"C:\Windows\Fonts", "/usr/share/fonts/truetype/montserrat",
            os.path.expanduser("~/Library/Fonts"), os.path.expanduser("~/.fonts")]
    for d in dirs:
        for n in nomi:
            if os.path.exists(os.path.join(d, n)):
                return os.path.join(d, n)
    raise SystemExit("Font Montserrat variabile non trovato: scaricalo da Google Fonts in font/")


_font = {}


def font(peso):
    if peso not in _font:
        tt = instancer.instantiateVariableFont(TTFont(trova_font()), {"wght": peso})
        buf = io.BytesIO()
        tt.save(buf)
        _font[peso] = (tt, hb.Font(hb.Face(buf.getvalue())))
    return _font[peso]


def misura(pezzi, corpo, spaziatura):
    """pezzi = [(testo, peso), ...] sulla stessa riga. Ritorna glifi posizionati e larghezza."""
    glifi, x = [], 0.0
    for testo, peso in pezzi:
        tt, hbf = font(peso)
        s = corpo / tt["head"].unitsPerEm
        buf = hb.Buffer()
        buf.add_str(testo)
        buf.guess_segment_properties()
        hb.shape(hbf, buf, {"kern": True, "liga": True})
        ordine = tt.getGlyphOrder()
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            glifi.append((tt, ordine[info.codepoint], x + pos.x_offset * s, pos.y_offset * s, s))
            x += pos.x_advance * s + spaziatura * corpo
    return glifi, x - spaziatura * corpo


def testo(pezzi, corpo, cx, base, spaziatura=0.0, **attr):
    glifi, larg = misura(pezzi, corpo, spaziatura)
    x0 = cx - larg / 2
    d = []
    for tt, nome, gx, gy, s in glifi:
        pen = SVGPathPen(tt.getGlyphSet(), ntos=lambda v: f"{v:.3f}".rstrip("0").rstrip("."))
        tt.getGlyphSet()[nome].draw(TransformPen(pen, (s, 0, 0, -s, x0 + gx, base - gy)))
        d.append(pen.getCommands())
    a = " ".join(f'{k}="{v}"' for k, v in attr.items())
    return f'<path {a} fill="{INK}" d="{"".join(d)}"/>', larg


# ---------------------------------------------------------------- loghi
def logo_shopnow(x, y, larghezza):
    """Logo vettoriale originale, a colori; le classi CSS diventano attributi (piu' robusto in RIP/Illustrator)."""
    src = open(os.path.join(QUI, "loghi", "shopnow_logo.svg"), encoding="utf-8").read()
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', src).group(1).split()]
    stili = {}
    for sel, corpo in re.findall(r"([^{}]+)\{([^}]*)\}", re.search(r"<style>(.*?)</style>", src, re.S).group(1)):
        for c in sel.split(","):
            stili.setdefault(c.strip().lstrip("."), []).extend(p for p in corpo.split(";") if p)

    def attr(m):
        props = dict(p.split(":") for p in stili[m.group(1)])
        return " ".join(f'{k}="{v.replace("px", "")}"' for k, v in props.items())

    corpo = re.search(r"</defs>(.*)</svg>", src, re.S).group(1)
    corpo = re.sub(r'class="(\w+)"', attr, corpo)
    s = larghezza / vb[2]
    return (f'<g id="LOGO_SHOPNOW" transform="translate({x:.2f} {y:.2f}) scale({s:.5f})">{corpo}</g>',
            vb[3] * s)


def logo_mono(nome):
    src = open(os.path.join(QUI, "loghi", "mono", nome + ".svg"), encoding="utf-8").read()
    w, h = [float(v) for v in re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', src).groups()]
    d = re.search(r' d="([^"]+)"', src).group(1)
    return d, w, h


def dimensione(w, h, nome, area=AREA, h_max=H_MAX):
    r = w / h
    hh = min(h_max, (area / r) ** 0.5, W_MAX / r) * OTTICA.get(nome, 1.0)
    hh = min(hh, W_OTTICA / r)
    return hh * r, hh


# ---------------------------------------------------------------- composizione
# Pezzi riusati anche da genera_pannello_unico.py
def apri(guide=True, sfondo=True, fori=True, linee_guida=()):
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">']
    if sfondo:
        out.append(f'<rect id="SFONDO" width="{W}" height="{H}" fill="#ffffff"/>')
    if guide:
        out += ['<g id="GUIDE_non_stampare" fill="none" stroke="#e05a5a" stroke-width="0.4" stroke-dasharray="3 2">',
                f'<rect x="{M}" y="{M}" width="{W-2*M}" height="{H-2*M}"/>', *linee_guida, '</g>']
    # fori per i distanziali: solo in bozza e anteprima, non nel file di stampa
    if fori:
        out.append('<g id="FORI_distanziali" fill="none" stroke="#bbbbbb" stroke-width="0.4">')
        for cx, cy in [(18, 18), (W-18, 18), (18, H-18), (W-18, H-18)]:
            out.append(f'<circle cx="{cx}" cy="{cy}" r="6"/>')
        out.append('</g>')
    return out


def griglia(gy0, gy1, **dim):
    """Canali di vendita (monocromatici, stessa altezza ottica) nella fascia gy0-gy1.
    Ritorna il gruppo SVG e le linee guida delle caselle."""
    rh = (gy1 - gy0) / rows
    out = ['<g id="CANALI">']
    for i, nome in enumerate(siti):
        r, c = divmod(i, cols)
        n_riga = min(cols, len(siti) - r * cols)          # riga incompleta: centrata
        cx = W / 2 + (c - (n_riga - 1) / 2) * CW
        cy = gy0 + rh * r + rh / 2
        d, w, h = logo_mono(nome)
        lw_, lh_ = dimensione(w, h, nome, **dim)
        s = lh_ / h
        out.append(f'<path id="{nome}" transform="translate({cx - lw_/2:.2f} {cy - lh_/2:.2f}) scale({s:.5f})" '
                   f'fill="{INK}" fill-rule="evenodd" d="{d}"/>')
    out.append('</g>')
    guide = [f'<line x1="{M}" y1="{gy0 + rh * r:.1f}" x2="{W-M}" y2="{gy0 + rh * r:.1f}" stroke-width="0.2"/>'
             for r in range(rows + 1)]
    guide += [f'<line x1="{M + CW * c:.1f}" y1="{gy0}" x2="{M + CW * c:.1f}" y2="{gy1}" stroke-width="0.2"/>'
              for c in range(cols + 1)]
    return "\n".join(out), guide


def payoff(base, corpo=11.2):
    return testo([("Specialisti nella vendita online di prodotti su misura", 300)], corpo, W / 2, base,
                 spaziatura=0.015, id="PAYOFF")[0]


def separatore(y, mezza=18, id_=""):
    a = f' id="{id_}"' if id_ else ""
    return f'<line{a} x1="{W/2-mezza}" y1="{y:.1f}" x2="{W/2+mezza}" y2="{y:.1f}" stroke="{INK}" stroke-width="0.5"/>'


def componi(guide=True, sfondo=True, fori=True):
    canali, linee = griglia(GY0, GY1)
    out = apri(guide, sfondo, fori, linee)

    # 1. Logo ShopNow a colori, ~30 cm, meta' superiore
    lw, ly = 300, 60
    g, lh = logo_shopnow((W - lw) / 2, ly, lw)
    out.append(g)
    # 2. Payoff
    out.append(payoff(ly + lh + 34))
    out.append(separatore(ly + lh + 52))
    # 3. Canali di vendita
    out.append(canali)
    # 4. Dominio
    t, _ = testo([("www.", 300), ("shopnow", 600), (".it", 300)], 14, W / 2, 493, spaziatura=0.06, id="DOMINIO")
    out.append(t)
    out.append('</svg>')
    return "\n".join(out)


def chrome():
    for p in [os.environ.get("CHROME", ""),
              r"C:\Program Files\Google\Chrome\Application\chrome.exe",
              r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
              shutil.which("google-chrome") or "", shutil.which("chromium") or ""]:
        if p and os.path.exists(p):
            return p


def anteprima(svg, png, px_mm=3):
    exe = chrome()
    if not exe:
        print("Chrome/Edge non trovato: anteprima PNG non generata")
        return
    w, h = W * px_mm, H * px_mm
    svg = svg.replace(f'width="{W}mm" height="{H}mm"', f'width="{w}" height="{h}"', 1)
    with tempfile.TemporaryDirectory() as tmp:
        html = os.path.join(tmp, "p.html")
        open(html, "w", encoding="utf-8").write(f'<html><body style="margin:0">{svg}</body></html>')
        subprocess.run([exe, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        f"--screenshot={os.path.abspath(png)}", f"--window-size={w},{h}",
                        "file:///" + html.replace(os.sep, "/")], capture_output=True, check=True)


if __name__ == "__main__":
    os.chdir(QUI)
    bozza = componi(guide=True, sfondo=True)
    open("bozza_pannello_40x55.svg", "w", encoding="utf-8").write(bozza)
    open("pannello_40x55_stampa.svg", "w", encoding="utf-8").write(componi(guide=False, sfondo=False, fori=False))
    anteprima(componi(guide=False, sfondo=True), "anteprima.png")
    print("ok: bozza_pannello_40x55.svg, pannello_40x55_stampa.svg, anteprima.png")
