from pathlib import Path
from PIL import Image

root = Path(__file__).parent
out = root / "rebuild-auth-assets"
out.mkdir(exist_ok=True)
for key, box in {
    "A02": (23, 161, 490, 309),
    "A04": (29, 229, 484, 349),
    "A05": (29, 229, 484, 372),
}.items():
    image = Image.open(root / "screens" / f"{key}.png")
    image.crop(box).save(out / f"{key}-photo.png")
    print(key, image.getpixel((250, 850)), image.getpixel((250, 700)))
