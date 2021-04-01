import yaml
import subprocess
import argparse
from pathlib import Path


makers = ["Aperio", "Generic-TIFF", "Hamamatsu", "Hamamatsu-vms",
          "Leica", "Mirax", "Olympus", "Trestle", "Ventana", "Zeiss"]

parser = argparse.ArgumentParser(description="Choice the WSI maker to download.")
parser.add_argument("maker", choices=makers)
args = parser.parse_args()

base = "http://openslide.cs.cmu.edu/download/openslide-testdata"
maker = args.maker

Path(maker).mkdir(exist_ok=True)
subprocess.run(f"wget {base}/{maker}/index.yaml -O {maker}/index.yaml", shell=True)

with open(f"{maker}/index.yaml", "r") as f:
    data = yaml.load(f)

for filename in data["slides"].keys():
    command = f"curl -o {maker}/{filename} -C - {base}/{maker}/{filename}"
    subprocess.run(command, shell=True)