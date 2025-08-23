import json
from pathlib import Path

import pytest

pytest.importorskip("torchgeo")

from stac_model.examples import unet_mlm


def test_unet_mlm_matches_example_json():
    try:
        item = unet_mlm().item.to_dict()
    except ModuleNotFoundError as e:
        if e.name == "torchgeo":
            pytest.skip("torchgeo is not installed")
        raise

    json_path = Path(__file__).resolve().parents[2] / "examples" / "item_pytorch_geo_unet.json"
    with open(json_path, "r", encoding="utf-8") as f:
        expected = json.load(f)

    assert item == expected, "Generated STAC Item does not match the saved example."
