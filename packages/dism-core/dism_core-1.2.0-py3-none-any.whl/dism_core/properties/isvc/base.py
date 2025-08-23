from typing import Optional

from ..base import BaseProperties
from .resources import Resources as ResourcesModel
from .signature import InputSignature, OutputSignature


class InferenceServiceProperties(BaseProperties):
    AnomalyThreshold: Optional[float] = None
    BuiltinThreshold: Optional[bool] = None
    FlaggingKey: Optional[str] = None
    InputSignature: list[InputSignature]
    MetricKey: str
    OutputSignature: list[OutputSignature]
    Image: Optional[str] = None
    Resources: Optional[ResourcesModel] = None
