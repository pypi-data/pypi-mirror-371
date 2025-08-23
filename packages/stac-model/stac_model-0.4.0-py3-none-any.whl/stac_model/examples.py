from typing import cast

import pystac
import shapely
from dateutil.parser import parse as parse_dt
from pystac.extensions.eo import Band, EOExtension
from pystac.extensions.file import FileExtension

from stac_model.base import ProcessingExpression, TaskEnum
from stac_model.input import InputStructure, ModelInput, ValueScalingObject
from stac_model.output import MLMClassification, ModelOutput, ModelResult
from stac_model.schema import ItemMLModelExtension, MLModelExtension, MLModelProperties


def eurosat_resnet() -> ItemMLModelExtension:
    input_struct = InputStructure(
        shape=[-1, 13, 64, 64],
        dim_order=["batch", "bands", "height", "width"],
        data_type="float32",
    )
    band_names = [
        "B01",
        "B02",
        "B03",
        "B04",
        "B05",
        "B06",
        "B07",
        "B08",
        "B8A",
        "B09",
        "B10",
        "B11",
        "B12",
    ]
    stats_mean = [
        1354.40546513,
        1118.24399958,
        1042.92983953,
        947.62620298,
        1199.47283961,
        1999.79090914,
        2369.22292565,
        2296.82608323,
        732.08340178,
        12.11327804,
        1819.01027855,
        1118.92391149,
        2594.14080798,
    ]
    stats_stddev = [
        245.71762908,
        333.00778264,
        395.09249139,
        593.75055589,
        566.4170017,
        861.18399006,
        1086.63139075,
        1117.98170791,
        404.91978886,
        4.77584468,
        1002.58768311,
        761.30323499,
        1231.58581042,
    ]
    value_scaling = [
        cast(
            ValueScalingObject,
            dict(
                type="z-score",
                mean=mean,
                stddev=stddev,
            ),
        )
        for mean, stddev in zip(stats_mean, stats_stddev, strict=False)
    ]
    model_input = ModelInput(
        name="13 Band Sentinel-2 Batch",
        bands=band_names,
        input=input_struct,
        resize_type=None,
        value_scaling=value_scaling,
        pre_processing_function=ProcessingExpression(
            format="python",
            expression="torchgeo.datamodules.eurosat.EuroSATDataModule.collate_fn",
        ),  # noqa: E501
    )
    result_struct = ModelResult(
        shape=[-1, 10],
        dim_order=["batch", "class"],
        data_type="float32",
    )
    class_map = {
        "Annual Crop": 0,
        "Forest": 1,
        "Herbaceous Vegetation": 2,
        "Highway": 3,
        "Industrial Buildings": 4,
        "Pasture": 5,
        "Permanent Crop": 6,
        "Residential Buildings": 7,
        "River": 8,
        "SeaLake": 9,
    }
    class_objects = [
        MLMClassification(
            value=class_value,
            name=class_name,
        )
        for class_name, class_value in class_map.items()
    ]
    model_output = ModelOutput(
        name="classification",
        tasks={"classification"},
        classes=class_objects,
        result=result_struct,
        post_processing_function=None,
    )
    assets = {
        "model": pystac.Asset(
            title="Pytorch weights checkpoint",
            description=(
                "A Resnet-18 classification model trained on normalized Sentinel-2 "
                "imagery with Eurosat landcover labels with torchgeo."
            ),
            href="https://huggingface.co/torchgeo/resnet18_sentinel2_all_moco/resolve/main/resnet18_sentinel2_all_moco-59bfdff9.pth",
            media_type="application/octet-stream; application=pytorch",
            roles=[
                "mlm:model",
                "mlm:weights",
                "data",
            ],
            extra_fields={"mlm:artifact_type": "torch.save"},
        ),
        "source_code": pystac.Asset(
            title="Model implementation.",
            description="Source code to run the model.",
            href="https://github.com/microsoft/torchgeo/blob/61efd2e2c4df7ebe3bd03002ebbaeaa3cfe9885a/torchgeo/models/resnet.py#L207",
            media_type="text/x-python",
            roles=[
                "mlm:source_code",
                "code",
            ],
        ),
    }

    ml_model_size = 43000000
    ml_model_meta = MLModelProperties(
        name="Resnet-18 Sentinel-2 ALL MOCO",
        architecture="ResNet-18",
        tasks={"classification"},
        framework="pytorch",
        framework_version="2.1.2+cu121",
        accelerator="cuda",
        accelerator_constrained=False,
        accelerator_summary="Unknown",
        file_size=ml_model_size,
        memory_size=1,
        pretrained=True,
        pretrained_source="EuroSat Sentinel-2",
        total_parameters=11_700_000,
        input=[model_input],
        output=[model_output],
    )
    # TODO, this can't be serialized but pystac.item calls for a datetime
    # in docs. start_datetime=datetime.strptime("1900-01-01", "%Y-%m-%d")
    # Is this a problem that we don't do date validation if we supply as str?
    start_datetime_str = "1900-01-01"
    end_datetime_str = "9999-01-01"  # cannot be None, invalid against STAC Core!
    start_datetime = parse_dt(start_datetime_str).isoformat() + "Z"
    end_datetime = parse_dt(end_datetime_str).isoformat() + "Z"
    bbox = [
        -7.882190080512502,
        37.13739173208318,
        27.911651652899923,
        58.21798141355221,
    ]
    geometry = shapely.geometry.Polygon.from_bounds(*bbox).__geo_interface__
    item_name = "eurosat-resnet-mlm-example"
    col_name = "ml-model-examples"
    item = pystac.Item(
        id=item_name,
        collection=col_name,
        geometry=geometry,
        bbox=bbox,
        datetime=None,
        properties={
            "start_datetime": start_datetime,
            "end_datetime": end_datetime,
            "description": "Sourced from torchgeo python library, identifier is ResNet18_Weights.SENTINEL2_ALL_MOCO",
        },
        assets=assets,
    )

    # note: cannot use 'item.add_derived_from' since it expects a 'Item' object, but we refer to a 'Collection' here
    # item.add_derived_from("https://earth-search.aws.element84.com/v1/collections/sentinel-2-l2a")
    item.add_link(
        pystac.Link(
            target="https://earth-search.aws.element84.com/v1/collections/sentinel-2-l2a",
            rel=pystac.RelType.DERIVED_FROM,
            media_type=pystac.MediaType.JSON,
        )
    )

    # define more link references
    col = pystac.Collection(
        id=col_name,
        title="Machine Learning Model examples",
        description="Collection of items contained in the Machine Learning Model examples.",
        extent=pystac.Extent(
            temporal=pystac.TemporalExtent([[parse_dt(start_datetime), parse_dt(end_datetime)]]),
            spatial=pystac.SpatialExtent([bbox]),
        ),
    )
    col.set_self_href("./examples/collection.json")
    col.add_item(item)
    item.set_self_href(f"./examples/{item_name}.json")

    model_asset = cast(
        FileExtension[pystac.Asset],
        FileExtension.ext(assets["model"], add_if_missing=True),
    )
    model_asset.apply(size=ml_model_size)

    eo_model_asset = cast(
        EOExtension[pystac.Asset],
        EOExtension.ext(assets["model"], add_if_missing=True),
    )
    # NOTE:
    #  typically, it is recommended to add as much details as possible for the band description
    #  minimally, the names (which are well-known for sentinel-2) are sufficient
    eo_bands = []
    for name in band_names:
        band = Band({})
        band.apply(name=name)
        eo_bands.append(band)
    eo_model_asset.apply(bands=eo_bands)

    item_mlm = MLModelExtension.ext(item, add_if_missing=True)
    item_mlm.apply(ml_model_meta.model_dump(by_alias=True, exclude_unset=True, exclude_defaults=True))
    return item_mlm


def unet_mlm() -> ItemMLModelExtension: # pragma: has-torch
    """
    Example of a UNet model using PyTorchGeo SENTINEL2_2CLASS_NC_FTW default weights.

    Returns an ItemMLModelExtension with Machine Learning Model Extension metadata.
    """
    from torchgeo.models import Unet_Weights, unet
    # Set the STAC version to 1.0.0 for compatibility with the example using relative links
    pystac.set_stac_version("1.0.0")

    weights = Unet_Weights.SENTINEL2_2CLASS_NC_FTW
    model = unet(weights=weights)
    item_id = "pytorch_geo_unet"
    collection_id = "ml-model-examples"
    bbox = [-7.88, 37.13, 27.91, 58.21]
    geometry = {
        "type": "Polygon",
        "coordinates": [
            [
                [-7.88, 37.13],
                [-7.88, 58.21],
                [27.91, 58.21],
                [27.91, 37.13],
                [-7.88, 37.13],
            ]
        ],
    }
    datetime_range: tuple[str, str] = (
        "2015-06-23T00:00:00Z",  # Sentinel-2A launch date (first Sentinel-2 data available)
        "2024-08-27T23:59:59Z",  # Dataset publication date Fields of The World (FTW)
    )

    task = {TaskEnum.SEMANTIC_SEGMENTATION}

    properties = {
        "description": "STAC item generated using unet_mlm() in stac_model/examples.py example. "
        "Specified in https://github.com/fieldsoftheworld/ftw-baselines "
        "First 4 S2 bands are for image t1 and last 4 bands are for image t2",
    }

    item_ext = MLModelExtension.from_torch(
        model,
        task=task,
        weights=weights,
        item_id=item_id,
        collection=collection_id,
        bbox=bbox,
        geometry=geometry,
        datetime_range=datetime_range,
        stac_properties=properties,
    )

    # Add additional metadata regarding the examples to have a valid STAC Item
    item = item_ext.item
    item_name = f"item_{item_id}.json"
    item_self_href = f"./{item_name}"

    link = pystac.Link(rel="self", target=item_self_href, media_type=pystac.MediaType.GEOJSON)
    link._target_href = item_self_href
    item.add_link(link)
    item.add_link(pystac.Link(rel="collection", target="./collection.json", media_type=pystac.MediaType.JSON))

    item_ext.item = item
    return item_ext
