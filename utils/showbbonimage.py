from PIL import Image, ImageDraw
from pathlib import Path
import argparse
import json


def main():
    parser = argparse.ArgumentParser(
        description="Show Bounding Boxes on Extracted Image")
    parser.add_argument("root", type=Path,
                        help="Root directory of processed result")
    parser.add_argument("-st", "--save_to", type=Path, default="./",
                        help="Directory to save images.")
    args = parser.parse_args()

    color = {"positive": (255, 0, 0),
             "negative": (0, 128, 0)}

    if not args.save_to.exists():
        args.save_to.mkdir(parents=True, exist_ok=True)

    imgs = (args.root/"patches").glob("*/*.png")
    annot_path = args.root/"results.json"
    with open(annot_path, "r") as f:
        annotation = json.load(f)

    for path in imgs:
        img = Image.open(path)
        stem = path.stem
        x, y = stem.split("_")
        patch = find_patch(annotation, x, y)
        for bb in patch["bbs"]:
            show_bb(img, bb["x"], bb["y"], bb["w"], bb["h"], bb["class"],
                    (255, 255, 255), color[bb["class"]])
            """
            draw = ImageDraw.Draw(img)
            x2 = bb["x"]+bb["w"]
            y2 = bb["y"]+bb["h"]
            outline = color[bb["class"]]
            draw.rectangle((bb["x"], bb["y"], x2, y2),
                           width=2,
                           outline=outline)
            """
        img.save(f"{args.save_to}/{stem}_with_bb.png")


def show_bb(img, x, y, w, h, text, textcolor, bbcolor):
    draw = ImageDraw.Draw(img)
    textwidth, textheight = draw.textsize(text)
    draw.rectangle((x, y, x+w, y+h), outline=bbcolor, width=2)
    draw.rectangle((x, y-textheight, x+textwidth, y), outline=bbcolor, fill=bbcolor)
    draw.text((x, y-textheight), text, fill=textcolor)


def find_patch(annotation, x, y):
    for patch in annotation["result"]:
        if int(x) == patch["x"] and int(y) == patch["y"]:
            return patch


if __name__ == '__main__':
    main()
