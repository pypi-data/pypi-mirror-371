# Copyright (c) FULIUCANSHENG.
# Licensed under the MIT License.

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch import autocast
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Union
from unitorch.models.bria import BRIAForSegmentation as _BRIAForSegmentation
from unitorch.cli import (
    cached_path,
    add_default_section_for_init,
    add_default_section_for_function,
    register_model,
)
from unitorch.cli.models import (
    detection_model_decorator,
    segmentation_model_decorator,
    DetectionOutputs,
    SegmentationOutputs,
    LossOutputs,
)


@register_model("core/model/segmentation/bria", segmentation_model_decorator)
class BRIAForSegmentation(_BRIAForSegmentation):
    def __init__(self):
        super().__init__()

    @classmethod
    @add_default_section_for_init("core/model/segmentation/bria")
    def from_core_configure(cls, config, **kwargs):
        config.set_default_section("core/model/segmentation/bria")

        inst = cls()
        weight_path = config.getoption("pretrained_weight_path", None)
        if weight_path is not None:
            inst.from_pretrained(weight_path)

        return inst

    @autocast(device_type=("cuda" if torch.cuda.is_available() else "cpu"))
    def forward(self, images):
        outputs = super().forward(images)
        return SegmentationOutputs(
            masks=outputs,
        )

    def segment(self, images, sizes: Optional[List[Tuple[int, int]]] = None):
        outputs = super().forward(images)
        if sizes is None:
            return SegmentationOutputs(
                masks=outputs.logits,
            )
        masks = [
            F.interpolate(mask.unsqueeze(0), size=list(size), mode="bilinear").squeeze(
                0
            )
            for mask, size in zip(outputs.logits, sizes)
        ]
        masks = [m.permute(1, 2, 0) for m in masks]
        masks = [(m - m.min()) / (m.max() - m.min()) for m in masks]
        return SegmentationOutputs(
            masks=masks,
        )
