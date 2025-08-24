import torch

from franken.metrics.base import BaseMetric
from franken.metrics.functions import *  # noqa: F403
from franken.metrics.registry import registry


__all__ = ["registry"]


def available_metrics() -> list[str]:
    return registry.available_metrics


def register(name: str, metric_class: type) -> None:
    registry.register(name, metric_class)


def init_metric(
    name: str, device: torch.device, dtype: torch.dtype = torch.float32
) -> BaseMetric:
    return registry.init_metric(name, device, dtype)
