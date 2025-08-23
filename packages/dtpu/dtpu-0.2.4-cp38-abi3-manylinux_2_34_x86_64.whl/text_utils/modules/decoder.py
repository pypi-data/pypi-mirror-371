import copy
from typing import Optional, List, Tuple, Any, Dict, Callable

import torch
from torch import nn

from text_utils.mask import square_subsequent_mask
from text_utils.modules import utils
from text_utils.modules.moe import MoeLayer
from text_utils.modules.embedding import Alibi


class Decoder(nn.Module):
    def additional_losses(self) -> Dict[str, torch.Tensor]:
        return {}

    def forward(
        self,
        x: torch.Tensor,
        pos: Optional[torch.Tensor],
        **kwargs: Any
    ) -> Tuple[torch.Tensor, Dict[str, Any]]:
        raise NotImplementedError


def decoder_from_config(
    cfg: Dict[str, Any],
    additional_decoder_fn: Optional[Callable[[Dict[str, Any]], Decoder]] = None
) -> Decoder:
    cfg = copy.deepcopy(cfg)
    enc_type = cfg.pop("type")
    if enc_type == "transformer":
        return TransformerDecoder(**cfg)
    else:
        if additional_decoder_fn is not None:
            return additional_decoder_fn(cfg)
        raise ValueError(f"unknown encoder type {enc_type}")


# modified version of pytorch transformer decoder layer
# supports multiple memories
class TransformerDecoderLayer(nn.Module):
    def __init__(
        self,
        d_model: int,
        nhead: int,
        add_pos: bool,
        memories: List[str],
        dim_feedforward: int = 2048,
        dropout: float = 0.1,
        activation: str = "gelu",
        ffw_type: str = "standard",
        ffw_kwargs: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__()
        self.self_attn = nn.MultiheadAttention(
            d_model,
            nhead,
            dropout=dropout,
            batch_first=True,
        )
        self.memories = memories
        self.memory_attns = nn.ModuleDict({
            memory: nn.MultiheadAttention(
                d_model, nhead, dropout=dropout, batch_first=True,
            )
            for memory in self.memories
        })
        self.memory_norms = nn.ModuleDict({
            memory: nn.LayerNorm(d_model)
            for memory in self.memories
        })
        self.memory_dropouts = nn.ModuleDict({
            memory: nn.Dropout(dropout)
            for memory in self.memories
        })

        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.dropout1 = nn.Dropout(dropout)

        self.ffw_type = ffw_type
        if ffw_type == "moe":
            assert ffw_kwargs is not None and "num_experts" in ffw_kwargs
            self.ffw = MoeLayer(
                d_model,
                dim_feedforward,
                d_model,
                ffw_kwargs["num_experts"],
                dropout=dropout,
                activation=activation
            )
        elif ffw_type == "standard":
            self.linear1 = nn.Linear(d_model, dim_feedforward)
            self.dropout = nn.Dropout(dropout)
            self.linear2 = nn.Linear(dim_feedforward, d_model)
            self.dropout2 = nn.Dropout(dropout)
        else:
            raise ValueError(f"unknown ffw type {ffw_type}")

        self.activation = utils.activation(activation)
        self.add_pos = add_pos

    def forward(
        self,
        src: torch.Tensor,
        pos: Optional[torch.Tensor] = None,
        padding_mask: Optional[torch.Tensor] = None,
        attn_mask: Optional[torch.Tensor] = None,
        memories: Optional[Dict[str, torch.Tensor]] = None,
        memory_padding_masks: Optional[Dict[str, torch.Tensor]] = None,
        memory_attn_masks: Optional[Dict[str, torch.Tensor]] = None,
        **kwargs: Any
    ) -> torch.Tensor:
        r"""Pass the input through the encoder layer.
        Args:
            src: the sequence to the encoder layer (required).
            pos: sequence of positional features (optional).
            padding_mask: the mask for the src keys per batch (optional).
            attn_mask: mask added to the attention weights (optional).
            memories: values to attend to (optional).
            memory_padding_masks: masks indicating padding values in the memories (optional).
            memory_attn_masks: masks added to the memory attention weights (optional).
        Shape:
            see the docs in Transformer class.
        """

        # see Fig. 1 of https://arxiv.org/pdf/2002.04745v1.pdf
        x = src
        x = self.norm1(x + self._sa_block(x, pos, padding_mask, attn_mask))
        for memory in self.memories:
            x = self.memory_norms[memory](
                x + self._memory_block(
                    x,
                    memory,
                    memories,
                    memory_padding_masks,
                    memory_attn_masks
                )
            )
        x = self.norm2(x + self._ff_block(x))
        return x

    def _add_pos(self, x: torch.Tensor, pos: Optional[torch.Tensor]) -> torch.Tensor:
        if self.add_pos and pos is not None:
            return x + pos
        else:
            return x

    # self-attention block
    def _sa_block(
        self,
        x: torch.Tensor,
        pos: Optional[torch.Tensor],
        padding_mask: Optional[torch.Tensor],
        attn_mask: Optional[torch.Tensor]
    ) -> torch.Tensor:
        x = self.self_attn(
            self._add_pos(x, pos),
            self._add_pos(x, pos),
            x,
            key_padding_mask=padding_mask,
            attn_mask=attn_mask,
            need_weights=True,
            average_attn_weights=False
        )[0]
        return self.dropout1(x)

    # feed forward block
    def _ff_block(self, x: torch.Tensor) -> torch.Tensor:
        if self.ffw_type == "moe":
            x, _ = self.ffw(x)
            return x
        else:
            x = self.linear2(self.dropout(self.activation(self.linear1(x))))
            return self.dropout2(x)

    # cross-attention block (memory-block called here)
    def _memory_block(
        self,
        x: torch.Tensor,
        memory: str,
        memories: Optional[Dict[str, torch.Tensor]] = None,
        memory_padding_masks: Optional[Dict[str, torch.Tensor]] = None,
        memory_attn_masks: Optional[Dict[str, torch.Tensor]] = None
    ) -> torch.Tensor:
        assert memories is not None
        memory_padding_mask = None if memory_padding_masks is None \
            else memory_padding_masks.get(memory)
        attn_mask = None if memory_attn_masks is None \
            else memory_attn_masks.get(memory)
        x = self.memory_attns[memory](
            x,
            memories[memory],
            memories[memory],
            key_padding_mask=memory_padding_mask,
            attn_mask=attn_mask,
            need_weights=True,
            average_attn_weights=False
        )[0]
        return self.memory_dropouts[memory](x)


class TransformerDecoder(Decoder):
    def __init__(
        self,
        dim: int,
        num_layers: int,
        heads: int,
        ffw_dim: int,
        dropout: float,
        with_pos: Optional[str] = None,
        memories: Optional[List[str]] = None,
        activation: str = "gelu",
        share_parameters: bool = False,
        causal: bool = True,
        ffw_type: str = "standard",
        ffw_kwargs: Optional[Dict[str, Any]] = None
    ):
        super().__init__()
        self.num_layers = num_layers
        self.share_parameters = share_parameters
        self.causal = causal

        self.transformer = nn.ModuleList(
            TransformerDecoderLayer(
                d_model=dim,
                nhead=heads,
                add_pos=with_pos == "attention",
                dim_feedforward=ffw_dim,
                dropout=dropout,
                activation=activation,
                memories=[] if memories is None else memories,
                ffw_type=ffw_type,
                ffw_kwargs=ffw_kwargs
            ) for _ in range(1 if self.share_parameters else num_layers)
        )

        self.with_pos = with_pos
        if self.with_pos == "alibi":
            self.alibi = Alibi(heads)

    def forward(
        self,
        x: torch.Tensor,
        pos: Optional[torch.Tensor],
        **kwargs: Any
    ) -> Tuple[torch.Tensor, Dict[str, Any]]:
        if self.causal:
            attn_mask = square_subsequent_mask(
                x.shape[1],
                float_mask=self.with_pos == "alibi",
                device=x.device
            )
        else:
            attn_mask = None

        if self.with_pos == "alibi":
            alibi_mask = self.alibi(x)
            if attn_mask is None:
                attn_mask = alibi_mask
            else:
                attn_mask += alibi_mask
        elif self.with_pos == "attention":
            assert pos is not None, "expected positional features for with_pos='attention'"
        elif self.with_pos is None:
            pass
        else:
            raise ValueError(f"unknown with_pos={self.with_pos}, must be either None or one of alibi, attention")

        dec = x
        for i in range(self.num_layers):
            dec = self.transformer[0 if self.share_parameters else i](
                src=dec,
                pos=pos,
                attn_mask=attn_mask,
                **kwargs
            )
        return dec, kwargs


def decoder(config: Dict[str, Any]) -> Decoder:
    decoder_type = config.pop("type")
    assert decoder_type is not None, "required key type not found in decoder config"
    if decoder_type == "transformer":
        return TransformerDecoder(**config)
    else:
        raise ValueError(f"unknown decoder type {decoder_type}")
