import json
from pathlib import Path
from typing import Callable

import openslide
import torch
from torchvision import io, transforms
import pandas as pd

from wsiprocess import cli
from wsiprocess.pytorch import utils


class WSIDataset(torch.utils.data.Dataset):

    def __init__(
            self, path: str = False, command: str = None,
            foreground_fn: Callable = False):
        if path and Path(path).is_dir():
            # if wsiprocess is done, load from the result directory.
            # ex: slide=CMU-1.ndpi, save_to=/data/save_to
            #  -> self.path=/data/save_to/CMU-1
            self.path = Path(path)
        else:
            # if not done, extract the patch from the wsi_path.
            args = cli.Args(command)
            self.path = Path(args.save_to)/Path(args.wsi).stem
            if not (self.path/"results.json").exists():
                utils.main(command, foreground_fn=foreground_fn)
            else:
                print(f"skipped because already patched: {self.path}")

        with open(self.path/"results.json", "r") as f:
            self.patch_config = json.load(f)

        self.patch_extracted = not self.patch_config["no_patches"]
        if not self.patch_extracted:
            self.slide = openslide.OpenSlide(self.patch_config["slide"])
            self.read_patch = self.read_patch_from_wsi
            self.to_tensor = transforms.ToTensor()
        else:
            self.read_patch = self.read_patch_from_disk
            self.ext = self.patch_config["ext"]

        self.read_coords()

    def read_coords(self):
        self.coords = pd.read_csv(self.path/"coords.csv")

    def read_patch_from_wsi(self, **kwargs) -> torch.float32:
        x = kwargs["x"]
        y = kwargs["y"]
        w = kwargs["w"]
        h = kwargs["h"]
        patch = self.to_tensor(self.slide.read_region((x, y), 0, (w, h)))
        return patch

    def read_patch_from_disk(self, **kwargs) -> torch.float32:
        x = kwargs["x"]
        y = kwargs["y"]
        label = kwargs.get("label") or "foreground"
        path = str(self.path/"patches"/label/f"{x:06}_{y:06}.{self.ext}")
        patch = io.read_image(path, mode=io.ImageReadMode.RGB)/255
        return patch

    def read_patch(self):
        raise NotImplementedError()

    def __len__(self):
        return len(self.coords)

    def __getitem__(self, idx):
        coord = self.coords.iloc[idx].to_dict()
        patch = self.read_patch(**coord)
        return patch


class WSIsDataset(torch.utils.data.Dataset):

    def __init__(self, datasets: list):
        msg = "some wsi names might be duplicated"
        assert len(set([d.path for d in datasets])) == len(datasets), msg
        for d in datasets:
            d.coords["slide"] = d.patch_config["slide"]
        self.coords = pd.concat([d.coords for d in datasets])
        self.datasets = {d.patch_config["slide"]: d for d in datasets}

    def __len__(self):
        return len(self.coords)

    def __getitem__(self, idx):
        coord = self.coords.iloc[idx].to_dict()
        patch = self.datasets[coord["slide"]].read_patch(**coord)
        return patch
