import requests
import os.path
import tempfile
from PIL import Image
from typing import Optional


def download_image(url: str, headers: Optional[dict] = None, output: Optional[str] = None) -> str:
    r = requests.get(url, headers=headers)

    if not os.path.exists(output):
        os.mkdir(output)

    with tempfile.TemporaryFile('wb', dir=output, delete=False) as f:
        f.write(r.content)

    return f.name


def show_img(img: str) -> None:
    im = Image.open(img)
    im.show()
    return
