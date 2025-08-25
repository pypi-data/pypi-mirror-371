# Copyright (c) FULIUCANSHENG.
# Licensed under the MIT License.

from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union
from unitorch.utils import pop_value, nested_dict_value
from unitorch.models.xpegasus import XPegasusProcessor as _XPegasusProcessor
from unitorch.cli import (
    cached_path,
    add_default_section_for_init,
    add_default_section_for_function,
    register_process,
)
from unitorch.cli import WriterOutputs
from unitorch.cli.models import (
    TensorsInputs,
    GenerationOutputs,
    GenerationTargets,
)
from unitorch.cli.models.xpegasus import pretrained_xpegasus_infos


class XPegasusProcessor(_XPegasusProcessor):
    """XPegasus processor for preprocessing and postprocessing."""

    def __init__(
        self,
        vocab_path: str,
        special_input_ids: Optional[Dict] = dict(),
        max_seq_length: Optional[int] = 128,
        max_gen_seq_length: Optional[int] = 48,
    ):
        """
        Initialize the XPegasusProcessor.

        Args:
            vocab_path (str): The path to the vocabulary file.
            special_input_ids (Dict, optional): A dictionary of special input IDs. Defaults to an empty dictionary.
            max_seq_length (int, optional): The maximum sequence length for input text. Defaults to 128.
            max_gen_seq_length (int, optional): The maximum sequence length for generated text. Defaults to 48.
        """
        super().__init__(
            vocab_path=vocab_path,
            special_input_ids=special_input_ids,
            max_seq_length=max_seq_length,
            max_gen_seq_length=max_gen_seq_length,
        )

    @classmethod
    @add_default_section_for_init("core/process/xpegasus")
    def from_core_configure(cls, config, **kwargs):
        """
        Create an instance of XPegasusProcessor from the core configuration.

        Args:
            config (Config): The core configuration object.

        Returns:
            XPegasusProcessor: An instance of XPegasusProcessor initialized with the provided configuration.
        """
        config.set_default_section("core/process/xpegasus")
        pretrained_name = config.getoption("pretrained_name", "xpegasus-base")
        vocab_path = config.getoption("vocab_path", None)
        vocab_path = pop_value(
            vocab_path,
            nested_dict_value(pretrained_xpegasus_infos, pretrained_name, "vocab"),
        )
        vocab_path = cached_path(vocab_path)

        return {
            "vocab_path": vocab_path,
        }

    @register_process("core/process/xpegasus/generation/inputs")
    def _generation_inputs(
        self,
        text: str,
        max_seq_length: Optional[int] = None,
    ):
        """
        Preprocess the input text for generation tasks.

        Args:
            text (str): The input text.
            max_seq_length (int, optional): The maximum sequence length. Defaults to None.

        Returns:
            TensorsInputs: The processed input tensors.
        """
        outputs = super().generation_inputs(
            text=text,
            max_seq_length=max_seq_length,
        )
        return TensorsInputs(input_ids=outputs.input_ids)

    @register_process("core/process/xpegasus/generation/labels")
    def _generation_labels(
        self,
        text: str,
        max_gen_seq_length: Optional[int] = None,
    ):
        """
        Preprocess the target text for generation tasks.

        Args:
            text (str): The target text.
            max_gen_seq_length (int, optional): The maximum generation sequence length. Defaults to None.

        Returns:
            GenerationTargets: The processed generation targets.
        """
        outputs = super().generation_labels(
            text=text,
            max_gen_seq_length=max_gen_seq_length,
        )
        return GenerationTargets(
            refs=outputs.input_ids,
            masks=outputs.attention_mask,
        )

    @register_process("core/process/xpegasus/generation")
    def _generation(
        self,
        text: str,
        text_pair: Optional[str] = None,
        max_seq_length: Optional[int] = None,
        max_gen_seq_length: Optional[int] = None,
    ):
        """
        Preprocess the input and target texts for generation tasks.

        Args:
            text (str): The input text.
            text_pair (str, optional): The paired input text. Defaults to None.
            max_seq_length (int, optional): The maximum sequence length. Defaults to None.
            max_gen_seq_length (int, optional): The maximum generation sequence length. Defaults to None.

        Returns:
            Tuple[TensorsInputs, GenerationTargets]: The processed input tensors and generation targets.
        """
        outputs = super().generation(
            text=text,
            text_pair=text_pair,
            max_seq_length=max_seq_length,
            max_gen_seq_length=max_gen_seq_length,
        )
        return TensorsInputs(
            input_ids=outputs.input_ids,
            attention_mask=outputs.attention_mask,
            decoder_input_ids=outputs.input_ids_pair,
            decoder_attention_mask=outputs.attention_mask_pair,
        ), GenerationTargets(
            refs=outputs.input_ids_label,
            masks=outputs.attention_mask_label,
        )

    @register_process("core/postprocess/xpegasus/detokenize")
    def _detokenize(
        self,
        outputs: GenerationOutputs,
    ):
        """
        Detokenize the generated sequences.

        Args:
            outputs (GenerationOutputs): The generation outputs.

        Returns:
            WriterOutputs: The detokenized writer outputs.
        """
        results = outputs.to_pandas()
        assert results.shape[0] == 0 or results.shape[0] == outputs.sequences.shape[0]

        decoded = super().detokenize(sequences=outputs.sequences)
        results["decoded"] = decoded
        return WriterOutputs(results)
