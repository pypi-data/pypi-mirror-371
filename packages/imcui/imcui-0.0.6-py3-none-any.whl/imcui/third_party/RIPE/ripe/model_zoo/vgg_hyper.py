from pathlib import Path

import torch

from ripe.models.backbones.vgg import VGG
from ripe.models.ripe import RIPE
from ripe.models.upsampler.hypercolumn_features import HyperColumnFeatures


def vgg_hyper(model_path: Path = None, desc_shares=None):
    if model_path is None:
        # check if the weights file exists in the current directory
        model_path = Path("/tmp/ripe_weights.pth")

        if model_path.exists():
            print(f"Using existing weights from {model_path}")
        else:
            print("Weights file not found. Downloading ...")
            torch.hub.download_url_to_file(
                "https://cvg.hhi.fraunhofer.de/RIPE/ripe_weights.pth",
                "/tmp/ripe_weights.pth",
            )
    else:
        if not model_path.exists():
            print(f"Error: {model_path} does not exist.")
            raise FileNotFoundError(f"Error: {model_path} does not exist.")

    backbone = VGG(pretrained=False)
    upsampler = HyperColumnFeatures()

    extractor = RIPE(
        net=backbone,
        upsampler=upsampler,
        desc_shares=desc_shares,
    )

    extractor.load_state_dict(torch.load(model_path, map_location="cpu"))

    return extractor
