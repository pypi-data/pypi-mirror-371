# Copyright (c) FULIUCANSHENG.
# Licensed under the MIT License.

from PIL import Image
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union
from unitorch.utils import pop_value, nested_dict_value
from unitorch.models.diffusers import StableFluxProcessor as _StableFluxProcessor
from unitorch.cli import (
    cached_path,
    add_default_section_for_init,
    add_default_section_for_function,
    register_process,
)
from unitorch.cli.models import (
    TensorsInputs,
)
from unitorch.cli.models.diffusers import pretrained_stable_infos


class ControlNetFluxProcessor(_StableFluxProcessor):
    def __init__(
        self,
        vocab_path: str,
        merge_path: str,
        vocab2_path: str,
        vae_config_path: str,
        max_seq_length: Optional[int] = 77,
        max_seq_length2: Optional[int] = 256,
        position_start_id: Optional[int] = 0,
        pad_token: Optional[str] = "<|endoftext|>",
        image_size: Optional[Tuple[int, int]] = None,
        center_crop: Optional[bool] = False,
        random_flip: Optional[bool] = False,
    ):
        super().__init__(
            vocab_path=vocab_path,
            merge_path=merge_path,
            vocab2_path=vocab2_path,
            vae_config_path=vae_config_path,
            max_seq_length=max_seq_length,
            max_seq_length2=max_seq_length2,
            position_start_id=position_start_id,
            pad_token=pad_token,
            image_size=image_size,
            center_crop=center_crop,
            random_flip=random_flip,
        )

    @classmethod
    @add_default_section_for_init("core/process/diffusion/controlnet_flux")
    def from_core_configure(cls, config, **kwargs):
        config.set_default_section("core/process/diffusion/controlnet_flux")
        pretrained_name = config.getoption("pretrained_name", "stable-v3-medium")
        pretrained_infos = nested_dict_value(pretrained_stable_infos, pretrained_name)

        vocab_path = config.getoption("vocab_path", None)
        vocab_path = pop_value(
            vocab_path,
            nested_dict_value(pretrained_infos, "text", "vocab"),
        )
        vocab_path = cached_path(vocab_path)

        merge_path = config.getoption("merge_path", None)
        merge_path = pop_value(
            merge_path,
            nested_dict_value(pretrained_infos, "text", "merge"),
        )
        merge_path = cached_path(merge_path)

        vocab2_path = config.getoption("vocab2_path", None)
        vocab2_path = pop_value(
            vocab2_path,
            nested_dict_value(pretrained_infos, "text2", "vocab"),
        )
        vocab2_path = cached_path(vocab2_path)

        vae_config_path = config.getoption("vae_config_path", None)
        vae_config_path = pop_value(
            vae_config_path,
            nested_dict_value(pretrained_infos, "vae", "config"),
        )
        vae_config_path = cached_path(vae_config_path)

        return {
            "vocab_path": vocab_path,
            "merge_path": merge_path,
            "vocab2_path": vocab2_path,
            "vae_config_path": vae_config_path,
        }

    @register_process("core/process/diffusion/controlnet_flux/text2image")
    def _text2image(
        self,
        prompt: str,
        image: Union[Image.Image, str],
        condition_image: Union[Image.Image, str, List[Union[Image.Image, str]]],
        max_seq_length: Optional[int] = None,
        max_seq_length2: Optional[int] = None,
    ):
        outputs = super().text2image(
            prompt=prompt,
            image=image,
            max_seq_length=max_seq_length,
            max_seq_length2=max_seq_length2,
        )
        if isinstance(condition_image, (list, tuple)):
            control_outputs = super().controlnets_inputs(condition_image)
        else:
            control_outputs = super().controlnet_inputs(condition_image)
        return TensorsInputs(
            pixel_values=outputs.pixel_values,
            condition_pixel_values=control_outputs.pixel_values,
            input_ids=outputs.input_ids,
            attention_mask=outputs.attention_mask,
            input2_ids=outputs.input2_ids,
            attention2_mask=outputs.attention2_mask,
        )

    @register_process("core/process/diffusion/controlnet_flux/text2image/inputs")
    def _text2image_inputs(
        self,
        prompt: str,
        condition_image: Union[Image.Image, str, List[Union[Image.Image, str]]],
        max_seq_length: Optional[int] = None,
        max_seq_length2: Optional[int] = None,
    ):
        text_outputs = super().text2image_inputs(
            prompt=prompt,
            max_seq_length=max_seq_length,
            max_seq_length2=max_seq_length2,
        )
        if isinstance(condition_image, (list, tuple)):
            control_outputs = super().controlnets_inputs(condition_image)
        else:
            control_outputs = super().controlnet_inputs(condition_image)
        return TensorsInputs(
            input_ids=text_outputs.input_ids,
            input2_ids=text_outputs.input2_ids,
            condition_pixel_values=control_outputs.pixel_values,
            attention_mask=text_outputs.attention_mask,
            attention2_mask=text_outputs.attention2_mask,
        )

    @register_process("core/process/diffusion/controlnet_flux/image2image/inputs")
    def _image2image_inputs(
        self,
        prompt: str,
        condition_image: Union[Image.Image, str, List[Union[Image.Image, str]]],
        image: Union[Image.Image, str],
        negative_prompt: Optional[str] = "",
        max_seq_length: Optional[int] = None,
    ):
        text_outputs = super().text2image_inputs(
            prompt=prompt,
            negative_prompt=negative_prompt,
            max_seq_length=max_seq_length,
        )
        image_outputs = super().image2image_inputs(image=image)
        if isinstance(condition_image, (list, tuple)):
            control_outputs = super().controlnets_inputs(condition_image)
        else:
            control_outputs = super().controlnet_inputs(condition_image)
        return TensorsInputs(
            input_ids=text_outputs.input_ids,
            input2_ids=text_outputs.input2_ids,
            pixel_values=image_outputs.pixel_values,
            condition_pixel_values=control_outputs.pixel_values,
            attention_mask=text_outputs.attention_mask,
            attention2_mask=text_outputs.attention2_mask,
        )

    @register_process("core/process/diffusion/controlnet_flux/inpainting")
    def _inpainting(
        self,
        prompt: str,
        condition_image: Union[Image.Image, str, List[Union[Image.Image, str]]],
        image: Union[Image.Image, str],
        mask_image: Union[Image.Image, str],
        negative_prompt: Optional[str] = "",
        max_seq_length: Optional[int] = None,
    ):
        text_outputs = super().text2image_inputs(
            prompt=prompt,
            negative_prompt=negative_prompt,
            max_seq_length=max_seq_length,
        )
        image_outputs = super().inpainting_inputs(
            image=image,
            mask_image=mask_image,
        )
        if isinstance(condition_image, (list, tuple)):
            control_outputs = super().controlnets_inputs(condition_image)
        else:
            control_outputs = super().controlnet_inputs(condition_image)
        return TensorsInputs(
            input_ids=text_outputs.input_ids,
            input2_ids=text_outputs.input2_ids,
            pixel_values=image_outputs.pixel_values,
            pixel_masks=image_outputs.pixel_masks,
            condition_pixel_values=control_outputs.pixel_values,
            attention_mask=text_outputs.attention_mask,
            attention2_mask=text_outputs.attention2_mask,
        )

    @register_process("core/process/diffusion/controlnet_flux/inpainting/inputs")
    def _inpainting_inputs(
        self,
        prompt: str,
        condition_image: Union[Image.Image, str, List[Union[Image.Image, str]]],
        image: Union[Image.Image, str],
        mask_image: Union[Image.Image, str],
        negative_prompt: Optional[str] = "",
        max_seq_length: Optional[int] = None,
    ):
        text_outputs = super().text2image_inputs(
            prompt=prompt,
            negative_prompt=negative_prompt,
            max_seq_length=max_seq_length,
        )
        image_outputs = super().inpainting_inputs(
            image=image,
            mask_image=mask_image,
        )
        if isinstance(condition_image, (list, tuple)):
            control_outputs = super().controlnets_inputs(condition_image)
        else:
            control_outputs = super().controlnet_inputs(condition_image)
        return TensorsInputs(
            input_ids=text_outputs.input_ids,
            input2_ids=text_outputs.input2_ids,
            pixel_values=image_outputs.pixel_values,
            pixel_masks=image_outputs.pixel_masks,
            condition_pixel_values=control_outputs.pixel_values,
            attention_mask=text_outputs.attention_mask,
            attention2_mask=text_outputs.attention2_mask,
        )

    @register_process(
        "core/process/diffusion/controlnet_flux/inpainting/control_inputs"
    )
    def _inpainting_control_inputs(
        self,
        image: Union[Image.Image, str],
        mask_image: Union[Image.Image, str],
        key: Optional[str] = "condition_pixel_values",
    ):
        image_outputs = super().inpainting_control_inputs(
            image=image,
            mask_image=mask_image,
        )
        results = {key: image_outputs.pixel_values}
        return TensorsInputs(**results)
