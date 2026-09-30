# Due pannelli ricavati dallo spazio 400 x 550 mm, da montare uno sopra l'altro:
#   ShopNow        400 x 350 mm  logo, payoff, griglia dei 20 canali
#   Monaci Digitali 400 x 200 mm  solo logo (con il monaco), fondo bianco
# Stesso margine (25 mm) su entrambi: i bordi dei contenuti restano allineati.
# Niente fori, neanche in bozza. 1 unita' SVG = 1 mm.
#
# Produce, per ciascun pannello, bozza (con GUIDE), file di stampa (solo tracciati, senza
# guide ne' sfondo) e anteprima PNG; in piu' anteprima_due_pannelli.png montati insieme.
import os
import subprocess
import tempfile

from genera_bozza import W, QUI, apri, griglia, payoff, logo_shopnow, anteprima, chrome
from genera_pannello_unico import logo_monaci

M2 = 25                     # margine di entrambi i pannelli
H_SHOP, H_MONACI = 350, 200

# ShopNow: fasce verticali (mm)
LOGO_Y, LOGO_W = 33, 190
GRIGLIA = (122, 317)        # 5 file da 39 mm

# Monaci: logo centrato
MONACI_ALT = 136            # altezza del logo con il monaco (margini sopra/sotto 32 mm)


def shopnow(guide=True, sfondo=True):
    canali, linee = griglia(*GRIGLIA, m=M2, area=18 * 70, h_max=20)
    out = apri(guide, sfondo, fori=False, linee_guida=linee, h=H_SHOP, m=M2)
    g, lh = logo_shopnow((W - LOGO_W) / 2, LOGO_Y, LOGO_W)
    out += [g, payoff(LOGO_Y + lh + 20, corpo=9.2), canali, '</svg>']
    return "\n".join(out)


def monaci(guide=True, sfondo=True):
    out = apri(guide, sfondo, fori=False, h=H_MONACI, m=M2)
    # larghezza del logo a quell'altezza, per centrarlo
    _, lw = logo_monaci(0, 0, MONACI_ALT, monaco=True)
    g, _ = logo_monaci((W - lw) / 2, (H_MONACI - MONACI_ALT) / 2, MONACI_ALT, monaco=True)
    out += [g, '</svg>']
    return "\n".join(out)


def anteprima_insieme(svgs, png, px_mm=3, stacco=15):
    """I due pannelli su una parete grigia, con uno stacco di `stacco` mm solo per la vista."""
    exe = chrome()
    if not exe:
        return
    parti, alto = [], 30
    for svg, h in svgs:
        s = svg.replace(f'width="{W}mm" height="{h}mm"', f'width="{W*px_mm}" height="{h*px_mm}"', 1)
        parti.append(f'<div style="position:absolute;left:{30*px_mm}px;top:{alto*px_mm}px;'
                     f'box-shadow:0 2px 12px rgba(0,0,0,.25)">{s}</div>')
        alto += h + stacco
    w, h = (W + 60) * px_mm, (alto - stacco + 30) * px_mm
    with tempfile.TemporaryDirectory() as tmp:
        html = os.path.join(tmp, "p.html")
        open(html, "w", encoding="utf-8").write(
            f'<html><body style="margin:0;background:#d9d6d0">{"".join(parti)}</body></html>')
        subprocess.run([exe, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        f"--screenshot={os.path.abspath(png)}", f"--window-size={w},{h}",
                        "file:///" + html.replace(os.sep, "/")], capture_output=True, check=True)


if __name__ == "__main__":
    os.chdir(QUI)
    for nome, fn, h in [("shopnow_40x35", shopnow, H_SHOP), ("monaci_40x20", monaci, H_MONACI)]:
        open(f"pannello_{nome}_bozza.svg", "w", encoding="utf-8").write(fn(guide=True))
        open(f"pannello_{nome}_stampa.svg", "w", encoding="utf-8").write(fn(guide=False, sfondo=False))
        anteprima(fn(guide=False), f"anteprima_{nome}.png", h_mm=h)
    anteprima_insieme([(shopnow(guide=False), H_SHOP), (monaci(guide=False), H_MONACI)],
                      "anteprima_due_pannelli.png")
    print("ok: pannello_shopnow_40x35_*, pannello_monaci_40x20_*, anteprime")
