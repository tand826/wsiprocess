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

    with open(args.root/"results.json", "r") as f:
        annotation = json.load(f)

    for patch in annotation["result"]:
        x = patch["x"]
        y = patch["y"]
        bbs = patch["bbs"]
        for bb in bbs:
            w = bb["w"]
            h = bb["h"]
            cls = bb["class"]
            if Path(f"{args.save_to}/{x:06}_{y:06}_with_bb.jpg").exists():
                img_path = f"{args.save_to}/{x:06}_{y:06}_with_bb.jpg"
            else:
                img_path = f"{args.root/'patches'}/{cls}/{x:06}_{y:06}.jpg"
            img = Image.open(img_path)
            show_bb(img, bb["x"], bb["y"], w, h, cls,
                    (255, 255, 255), color[bb["class"]])
            img.save(f"{args.save_to}/{x:06}_{y:06}_with_bb.jpg")


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
