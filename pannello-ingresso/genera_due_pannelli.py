# Due pannelli ricavati dallo spazio 400 x 550 mm, da montare uno sopra l'altro:
#   ShopNow        400 x 350 mm  logo, payoff, griglia dei 20 canali
#   Monaci Digitali 400 x 200 mm  fondo bianco, tre varianti (vedi sotto)
# Stesso margine (25 mm) su entrambi: i bordi dei contenuti restano allineati.
# Niente fori, neanche in bozza. 1 unita' SVG = 1 mm.
#
# Produce, per ciascun pannello, bozza (con GUIDE), file di stampa (solo tracciati, senza
# guide ne' sfondo) e anteprima PNG; in piu' anteprima_due_pannelli.png montati insieme.
import os
import subprocess
import tempfile

from genera_bozza import W, QUI, apri, griglia, payoff, logo_shopnow, anteprima, chrome, misura, testo
from genera_pannello_unico import logo_monaci, testo_sx, SERVIZI

M2 = 25                     # margine di entrambi i pannelli
H_SHOP, H_MONACI = 350, 200

# ShopNow: fasce verticali (mm)
LOGO_Y, LOGO_W = 33, 190
GRIGLIA = (122, 317)        # 5 file da 39 mm

# Monaci: tre varianti
#   "logo"     logo completo con il monaco, centrato
#   "servizi"  logo con il monaco a sinistra, servizi con descrizione a destra
#   "scritta"  solo MONACI DIGITALI al centro, in basso i tre servizi su una riga
MONACI_ALT = 136            # altezza del logo con il monaco (margini sopra/sotto 32 mm)
SCRITTA_ALT = 92            # altezza della sola scritta (variante "scritta")


def shopnow(guide=True, sfondo=True):
    canali, linee = griglia(*GRIGLIA, m=M2, area=18 * 70, h_max=20)
    out = apri(guide, sfondo, fori=False, linee_guida=linee, h=H_SHOP, m=M2)
    g, lh = logo_shopnow((W - LOGO_W) / 2, LOGO_Y, LOGO_W)
    out += [g, payoff(LOGO_Y + lh + 20, corpo=9.2), canali, '</svg>']
    return "\n".join(out)


def monaci(guide=True, sfondo=True, variante="logo"):
    out = apri(guide, sfondo, fori=False, h=H_MONACI, m=M2)
    if variante == "logo":
        _, lw = logo_monaci(0, 0, MONACI_ALT)          # larghezza a quell'altezza, per centrarlo
        out.append(logo_monaci((W - lw) / 2, (H_MONACI - MONACI_ALT) / 2, MONACI_ALT)[0])

    elif variante == "servizi":
        titolo, descr, passo, stacco = 9.2, 7.2, 37, 28
        _, lw = logo_monaci(0, 0, MONACI_ALT)
        larg_testi = max(max(misura([(t, 600)], titolo, 0.1)[1], misura([(d, 300)], descr, 0.01)[1])
                         for t, d in SERVIZI)
        x0 = (W - (lw + stacco + larg_testi)) / 2     # logo + testi centrati come un blocco unico
        out.append(logo_monaci(x0, (H_MONACI - MONACI_ALT) / 2, MONACI_ALT)[0])
        tx = x0 + lw + stacco
        blocco = passo * (len(SERVIZI) - 1) + titolo * 0.7 + 4 + descr
        base = (H_MONACI - blocco) / 2 + titolo * 0.7
        out.append('<g id="SERVIZI_MONACI">')
        for i, (t, d) in enumerate(SERVIZI):
            yb = base + passo * i
            out.append(testo_sx([(t, 600)], titolo, tx, yb, spaziatura=0.1))
            out.append(testo_sx([(d, 300)], descr, tx, yb + 4 + descr * 0.95, spaziatura=0.01))
        out.append('</g>')

    elif variante == "scritta":
        corpo, stacco = 7.5, 30
        riga = "  ·  ".join(t for t, _ in SERVIZI)
        blocco = SCRITTA_ALT + stacco + corpo * 0.7
        y0 = (H_MONACI - blocco) / 2
        _, sw = logo_monaci(0, 0, SCRITTA_ALT, monaco=False)
        out.append(logo_monaci((W - sw) / 2, y0, SCRITTA_ALT, monaco=False)[0])
        out.append(testo([(riga, 500)], corpo, W / 2, y0 + blocco, spaziatura=0.15, id="SERVIZI_MONACI")[0])
    out.append('</svg>')
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
    pannelli = [("shopnow_40x35", shopnow, H_SHOP),
                ("monaci_40x20", monaci, H_MONACI),
                ("monaci_40x20_servizi", lambda **k: monaci(variante="servizi", **k), H_MONACI),
                ("monaci_40x20_scritta", lambda **k: monaci(variante="scritta", **k), H_MONACI)]
    for nome, fn, h in pannelli:
        open(f"pannello_{nome}_bozza.svg", "w", encoding="utf-8").write(fn(guide=True))
        open(f"pannello_{nome}_stampa.svg", "w", encoding="utf-8").write(fn(guide=False, sfondo=False))
        anteprima(fn(guide=False), f"anteprima_{nome}.png", h_mm=h)
    anteprima_insieme([(shopnow(guide=False), H_SHOP), (monaci(guide=False), H_MONACI)],
                      "anteprima_due_pannelli.png")
    anteprima_insieme([(monaci(guide=False, variante=v), H_MONACI) for v in ("logo", "servizi", "scritta")],
                      "anteprima_monaci_varianti.png")
    print("ok: pannello_shopnow_40x35_*, pannello_monaci_40x20[_servizi|_scritta]_*, anteprime")
