# Bozza pannello ingresso ShopNow Srl - 400 x 550 mm (1 unita' SVG = 1 mm)
W, H, M = 400, 550, 30
INK = "#333333"   # colore unico per canali e testi (monocromia)
siti = ["leTapparelle.com", "DocciaBox.com", "Zanzariere24.it", "BricoBros.com",
        "LineaDoccia.it", "Veneziane.it", "TendeCristal.it", "Doccia.it",
        "Tapparelle.it", "InfissiFaiDaTe.it", "SolidStone.it", "BuyMore.it",
        None, None, None, None]  # slot da completare

cols, rows = 4, 4
gx0, gy0, cw, rh = M, 322, (W - 2 * M) / cols, 34
sw, sh = 72, 24

out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">',
       f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
       '<g id="GUIDE_non_stampare" fill="none" stroke="#e05a5a" stroke-width="0.4" stroke-dasharray="3 2">',
       f'<rect x="{M}" y="{M}" width="{W-2*M}" height="{H-2*M}"/>']
for cx, cy in [(18, 18), (W-18, 18), (18, H-18), (W-18, H-18)]:
    out.append(f'<circle cx="{cx}" cy="{cy}" r="6"/>')
out.append('</g>')

# 1. Logo ShopNow (segnaposto: sostituire con logo vettoriale originale, a colori)
out += ['<g id="LOGO_SHOPNOW">',
        '<rect x="50" y="95" width="300" height="120" rx="4" fill="#f3f6fa" stroke="#9fb3c8" stroke-width="0.6" stroke-dasharray="4 3"/>',
        '<text x="200" y="172" text-anchor="middle" font-family="Helvetica, Arial, sans-serif" font-size="58" font-weight="700" fill="#1f5fa8">ShopNow</text>',
        '<text x="200" y="205" text-anchor="middle" font-family="Helvetica, Arial, sans-serif" font-size="6" fill="#7a8ea3">[ segnaposto — inserire logo_shopnow originale in vettoriale, a colori ]</text>',
        '</g>']

# 2. Riga descrittiva
out.append(f'<text id="PAYOFF" x="200" y="262" text-anchor="middle" font-family="Helvetica, Arial, sans-serif" font-size="11" fill="{INK}">Leader nella vendita online di prodotti su misura</text>')

# separatore
out.append(f'<line x1="150" y1="295" x2="250" y2="295" stroke="{INK}" stroke-width="0.6"/>')

# 3. Canali di vendita (monocromatici)
out.append('<g id="CANALI">')
for i, s in enumerate(siti):
    r, c = divmod(i, cols)
    cx = gx0 + cw * c + cw / 2
    cy = gy0 + rh * r + sh / 2
    if s:
        out.append(f'<text x="{cx:.1f}" y="{cy+2.3:.1f}" text-anchor="middle" font-family="Helvetica, Arial, sans-serif" font-size="6.6" font-weight="700" fill="{INK}">{s}</text>')
    else:
        out.append(f'<rect x="{cx-sw/2:.1f}" y="{cy-sh/2:.1f}" width="{sw}" height="{sh}" fill="none" stroke="#bbbbbb" stroke-width="0.5" stroke-dasharray="2 2"/>')
        out.append(f'<text x="{cx:.1f}" y="{cy+1.5:.1f}" text-anchor="middle" font-family="Helvetica, Arial, sans-serif" font-size="4.5" fill="#aaaaaa">sito da indicare</text>')
out.append('</g>')

# 4. Dominio
out.append(f'<text id="DOMINIO" x="200" y="505" text-anchor="middle" font-family="Helvetica, Arial, sans-serif" font-size="16" font-weight="700" letter-spacing="0.5" fill="{INK}">www.shopnow.it</text>')
out.append('</svg>')

open("bozza_pannello_40x55.svg", "w").write("\n".join(out))
