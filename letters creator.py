#--CREER LES IMAGES DES LETTRES--#

lang = "FR"

from PIL import Image, ImageDraw, ImageFont

with open(f"{lang}/letPt {lang}.txt", "r") as fich:
    fich = fich.read()
    pts = eval(fich)

letters = [(let, pts[let]) for let in pts]
smallLetters = [let[0].lower() for let in letters]

fond = Image.open("let background.png")
fond.save(f"{lang}/Blanks/blank.png")
w, h = fond.size

fontlet = ImageFont.truetype("arial.ttf", w * 3 // 4)
fontpt = ImageFont.truetype("arial.ttf", w // 7)

# for let in letters:
#     im = Image.new("RGBA", (w, h))
#     im.paste(fond)
#     l, pt = let
#     d = ImageDraw.Draw(im)
#     W = d.textsize(l, font=fontlet)[0]  # Permet de centrer la lettre
#     d.text(((w - W) // 2, h // 10), l, fill="black", font=fontlet)
#     d.text((8 * w // 10, 7 * h // 10), str(pt), fill="black", font=fontpt)
#     im.save(f"{lang}/{l}.png")


for let in smallLetters:
    im = Image.new("RGBA", (w, h))
    im.paste(fond)
    d = ImageDraw.Draw(im)
    W = d.textsize(let, font=fontlet)[0]  # Permet de centrer la lettre
    d.text(((w - W) // 2, h // 15), let, fill="gray", font=fontlet)
    im.save(f"{lang}/Blanks/{let}.png")
