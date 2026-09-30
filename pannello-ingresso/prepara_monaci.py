# Estrae il logo Monaci Digitali dal PDF vettoriale di Illustrator (loghi/sorgenti/monaci_logo.pdf)
# e lo salva come SVG ritagliato in loghi/monaci_logo.svg, con due gruppi separati:
#   MONACO  = il monaco pixelato (si puo' togliere se manca spazio)
#   SCRITTA = "MONACI DIGITALI"
# Il PDF usa solo tracciati (m l c h re f) in nero pieno su fondo bianco: basta un piccolo interprete.
import os
import re
from pypdf import PdfReader

QUI = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(QUI, "loghi", "sorgenti", "monaci_logo.pdf")
OUT = os.path.join(QUI, "loghi", "monaci_logo.svg")
NERO = "#000000"


def tracciati(pdf):
    pagina = PdfReader(pdf).pages[0]
    alto = float(pagina.mediabox.height)
    flusso = pagina.get_contents().get_data().decode("latin1")
    tok = re.findall(r"/[^\s/\[\]<>()]+|[-+]?\d*\.?\d+|[A-Za-z*'\"]+", flusso)
    pila, ctm, num, d, colore, out = [], (1, 0, 0, 1, 0, 0), [], [], None, []

    def mul(a, b):
        return (a[0]*b[0] + a[1]*b[2], a[0]*b[1] + a[1]*b[3], a[2]*b[0] + a[3]*b[2],
                a[2]*b[1] + a[3]*b[3], a[4]*b[0] + a[5]*b[2] + b[4], a[4]*b[1] + a[5]*b[3] + b[5])

    def pt(x, y):   # spazio PDF (origine in basso) -> SVG (origine in alto)
        a, b, c, dd, e, f = ctm
        return (a*x + c*y + e, alto - (b*x + dd*y + f))

    for t in tok:
        if re.fullmatch(r"[-+]?\d*\.?\d+", t):
            num.append(float(t))
            continue
        if t == "q":
            pila.append(ctm)
        elif t == "Q":
            ctm = pila.pop()
        elif t == "cm":
            ctm = mul(tuple(num[-6:]), ctm)
        elif t == "k":
            colore = tuple(num[-4:])
        elif t == "m":
            d.append(("M", [pt(*num[-2:])]))
        elif t == "l":
            d.append(("L", [pt(*num[-2:])]))
        elif t == "c":
            x1, y1, x2, y2, x3, y3 = num[-6:]
            d.append(("C", [pt(x1, y1), pt(x2, y2), pt(x3, y3)]))
        elif t == "h":
            d.append(("Z", []))
        elif t == "re":
            x, y, w, h = num[-4:]
            d += [("M", [pt(x, y)]), ("L", [pt(x + w, y)]), ("L", [pt(x + w, y + h)]),
                  ("L", [pt(x, y + h)]), ("Z", [])]
        elif t in ("f", "F", "f*"):
            if colore != (0, 0, 0, 0):          # salta il fondo bianco
                out.append((d, t == "f*"))
            d = []
        elif t == "n":
            d = []
        num = []
    return out


def main():
    paths = tracciati(SRC)
    punti = [p for d, _ in paths for _, pts in d for p in pts]
    x0, y0 = min(p[0] for p in punti), min(p[1] for p in punti)
    x1, y1 = max(p[0] for p in punti), max(p[1] for p in punti)
    # fasce verticali separate da spazio vuoto: la prima e' il monaco, le altre le due righe di testo
    fasce = sorted((min(p[1] for _, pts in d for p in pts), max(p[1] for _, pts in d for p in pts))
                   for d, _ in paths)
    fine_monaco = fasce[0][1]
    for a, b in fasce:
        if a > fine_monaco:
            break
        fine_monaco = max(fine_monaco, b)
    gruppi = {"MONACO": [], "SCRITTA": []}
    for d, pari in paths:
        top = min(p[1] for _, pts in d for p in pts)
        s = "".join(c + " ".join(f"{x - x0:.2f},{y - y0:.2f}" for x, y in pts) for c, pts in d)
        regola = ' fill-rule="evenodd"' if pari else ""
        gruppi["MONACO" if top <= fine_monaco else "SCRITTA"].append(f'<path d="{s}"{regola}/>')
    corpo = "".join(f'<g id="{k}" fill="{NERO}">{"".join(v)}</g>' for k, v in gruppi.items())
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {x1 - x0:.2f} {y1 - y0:.2f}">'
           f'{corpo}</svg>\n')
    open(OUT, "w", encoding="utf-8").write(svg)
    print(f"monaci_logo.svg {x1 - x0:.1f}x{y1 - y0:.1f} pt, "
          f"{len(gruppi['MONACO'])} tracciati monaco, {len(gruppi['SCRITTA'])} scritta")


if __name__ == "__main__":
    main()
