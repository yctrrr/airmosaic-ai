"""Tiny numeric encoders for synthetic software checks, not published architectures."""
from __future__ import annotations

import torch
from torch import nn


BRANCHES = {
    "tabular": ("static",),
    "sequence": ("history",),
    "grid": ("grid",),
    "fusion": ("static", "history", "grid"),
}
SHAPES = {"static": (4,), "history": (8, 3), "grid": (1, 4, 4)}


class SyntheticTransformer(nn.Module):
    """Encode feature/time/patch units and pool a shared readout token."""

    def __init__(self, case: str, config: dict):
        super().__init__()
        if case not in BRANCHES:
            raise ValueError("unsupported_demo_case")
        self.branches = BRANCHES[case]
        width = config["d_model"]
        dimensions = {"static": (1, 4), "history": (3, 8), "grid": (4, 4)}
        self.projections = nn.ModuleDict({
            name: nn.Linear(dimensions[name][0], width) for name in self.branches
        })
        self.positions = nn.ParameterDict({
            name: nn.Parameter(torch.empty(1, dimensions[name][1], width))
            for name in self.branches
        })
        self.modalities = nn.ParameterDict({
            name: nn.Parameter(torch.empty(1, 1, width)) for name in self.branches
        })
        self.readout = nn.Parameter(torch.empty(1, 1, width))
        layer = nn.TransformerEncoderLayer(
            d_model=width, nhead=config["heads"], dim_feedforward=2 * width,
            dropout=config["dropout"], activation="gelu", batch_first=True,
            norm_first=True,
        )
        self.encoder = nn.TransformerEncoder(
            layer, num_layers=config["layers"], enable_nested_tensor=False,
        )
        self.head = nn.Sequential(nn.LayerNorm(width), nn.Linear(width, 1))
        # Reset cloned encoder layers independently rather than retaining equal
        # initial values. No pretrained weights or remote code are loaded.
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
            if isinstance(module, nn.MultiheadAttention):
                nn.init.xavier_uniform_(module.in_proj_weight)
                nn.init.zeros_(module.in_proj_bias)
        for parameter in [self.readout, *self.positions.values(), *self.modalities.values()]:
            nn.init.normal_(parameter, std=0.02)

    def forward(self, inputs: dict[str, torch.Tensor]) -> torch.Tensor:
        if set(inputs) != set(self.branches):
            raise ValueError("demo_modality_mismatch")
        batches = {int(value.shape[0]) for value in inputs.values()}
        if len(batches) != 1:
            raise ValueError("demo_batch_mismatch")
        units = []
        for name in self.branches:
            value = inputs[name]
            if tuple(value.shape[1:]) != SHAPES[name] or not torch.isfinite(value).all():
                raise ValueError("invalid_demo_tensor")
            if name == "static":
                value = value.unsqueeze(-1)
            elif name == "grid":
                batch = value.shape[0]
                value = value.unfold(2, 2, 2).unfold(3, 2, 2)
                value = value.permute(0, 2, 3, 1, 4, 5).reshape(batch, 4, 4)
            units.append(self.projections[name](value) + self.positions[name] + self.modalities[name])
        readout = self.readout.expand(next(iter(batches)), -1, -1)
        representation = self.encoder(torch.cat([readout, *units], dim=1))
        return self.head(representation[:, 0]).squeeze(-1)
