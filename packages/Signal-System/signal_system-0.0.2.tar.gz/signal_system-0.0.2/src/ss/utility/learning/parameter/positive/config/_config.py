from typing import Generic, Type, TypeVar, cast

from dataclasses import dataclass, field

from ss.utility.learning.parameter.manifold.config import (
    ManifoldParameterConfig,
)
from ss.utility.learning.parameter.transformer import Transformer

# from ss.utility.learning.parameter.transformer.config import TC
from ss.utility.learning.parameter.transformer.exp import ExpTransformer
from ss.utility.learning.parameter.transformer.exp.config import ExpTC as ExpTC
from ss.utility.learning.parameter.transformer.exp.config import (
    ExpTransformerConfig,
)

# T = TypeVar("T", bound=Transformer, default=ExpTransformer)
# TC = TypeVar("TC", bound=TransformerConfig)


@dataclass
class PositiveParameterConfig(ManifoldParameterConfig[ExpTC], Generic[ExpTC]):
    # Transformer: Type[T] = field(
    #     default_factory=lambda: cast(Type[T], ExpTransformer)
    # )
    transformer: ExpTC = field(
        default_factory=lambda: cast(ExpTC, ExpTransformerConfig())
    )
