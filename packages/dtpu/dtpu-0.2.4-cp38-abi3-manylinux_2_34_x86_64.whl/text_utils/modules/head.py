from typing import Any, Dict, Optional, Callable
import copy

import torch
from torch import nn

from text_utils.modules import utils


class Head(nn.Module):
    def forward(self, x: torch.Tensor, **kwargs: Any) -> torch.Tensor:
        raise NotImplementedError


def head_from_config(
    cfg: Dict[str, Any],
    additional_head_fn: Optional[Callable[[Dict[str, Any]], Head]] = None
) -> Head:
    cfg = copy.deepcopy(cfg)
    head_type = cfg.pop("type")
    if head_type == "classification":
        return ClassificationHead(**cfg)
    elif head_type == "sequence_classification":
        return SequenceClassificationHead(**cfg)
    else:
        if additional_head_fn is not None:
            return additional_head_fn(cfg)
        raise ValueError(f"unknown head type {head_type}")


class ClassificationHead(Head):
    def __init__(
            self,
            dim: int,
            num_classes: int,
            num_layers: int,
            dropout: float,
            activation: str = "gelu"
    ):
        super().__init__()

        layers = []
        for i in range(num_layers):
            if i < num_layers - 1:
                layers.append(nn.Linear(dim, dim))
                layers.append(utils.activation(activation))
                layers.append(nn.Dropout(dropout))
            else:
                # final linear layer
                layers.append(nn.Linear(dim, num_classes))

        self.head = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor, **kwargs: Any) -> torch.Tensor:
        return self.head(x[:, 0, :])


class SequenceClassificationHead(ClassificationHead):
    def forward(self, x: torch.Tensor, **kwargs: Any) -> torch.Tensor:
        return self.head(x)
