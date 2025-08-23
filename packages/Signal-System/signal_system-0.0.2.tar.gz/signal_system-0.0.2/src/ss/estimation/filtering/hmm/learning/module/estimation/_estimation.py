from typing import Callable, Generic, assert_never

import torch

from ss.estimation.filtering.hmm.learning.module.estimation.config import (
    EstimationConfig,
)
from ss.estimation.filtering.hmm.learning.module.filter.config import (
    FilterConfig,
)
from ss.utility.learning.module import BaseLearningModule
from ss.utility.learning.parameter.probability import ProbabilityParameter
from ss.utility.learning.parameter.transformer import T
from ss.utility.learning.parameter.transformer.config import TC


class EstimationModule(
    BaseLearningModule[EstimationConfig[TC]], Generic[T, TC]
):
    def __init__(
        self,
        config: EstimationConfig[TC],
        filter_config: FilterConfig,
    ) -> None:
        super().__init__(config)
        self._state_dim = filter_config.state_dim
        self._estimation_dim = filter_config.estimation_dim

        self._matrix = ProbabilityParameter[T, TC](
            self._config.matrix.probability_parameter,
            (self._state_dim, self._estimation_dim),
        )

        # self._forward: Callable[[torch.Tensor, torch.Tensor], torch.Tensor]
        self._forward: Callable[[torch.Tensor], torch.Tensor]
        self._init_forward()

    def _init_forward(self) -> None:
        match self._config.option:
            case EstimationConfig.Option.ESTIMATED_STATE:
                self._forward = self._forward_estimated_state
            # case EstimationConfig.Option.PREDICTED_STATE:
            #     self._forward = self._forward_predicted_state
            case EstimationConfig.Option.PREDICTED_OBSERVATION_PROBABILITY:
                self._forward = self._forward_estimation
            case EstimationConfig.Option.LINEAR_TRANSFORM_ESTIMATION:
                self._forward = self._forward_estimation
            # case EstimationConfig.Option.LINEAR_TRANSFORM_PREDICTION:
            #     self._forward = self._forward_prediction
            case _ as _estimation_config:
                assert_never(_estimation_config)

    @property
    def option(self) -> EstimationConfig.Option:
        return self._config.option

    @option.setter
    def option(self, option: EstimationConfig.Option) -> None:
        self._config.option = option
        self._init_forward()

    @property
    def matrix_parameter(
        self,
    ) -> ProbabilityParameter[T, TC]:
        return self._matrix

    @property
    def matrix(self) -> torch.Tensor:
        matrix: torch.Tensor = self._matrix()
        return matrix

    @matrix.setter
    def matrix(self, matrix: torch.Tensor) -> None:
        self._matrix.set_value(matrix)

    @torch.compile
    def _forward_estimated_state(
        self,
        estimated_state_trajectory: torch.Tensor,
        # predicted_state_trajectory: torch.Tensor,
    ) -> torch.Tensor:
        # (batch_size, horizon, estimation_dim=state_dim) or (batch_size, estimation_dim=state_dim)
        return estimated_state_trajectory

    # @torch.compile
    # def _forward_predicted_state(
    #     self,
    #     estimated_state_trajectory: torch.Tensor,
    #     predicted_state_trajectory: torch.Tensor,
    # ) -> torch.Tensor:
    #     # (batch_size, horizon, estimation_dim=state_dim) or (batch_size, estimation_dim=state_dim)
    #     return predicted_state_trajectory

    @torch.compile
    def _forward_estimation(
        self,
        estimated_state_trajectory: torch.Tensor,
        # predicted_state_trajectory: torch.Tensor,
    ) -> torch.Tensor:
        estimation_matrix = self.matrix  # (state_dim, estimation_dim)
        estimation = torch.matmul(
            estimated_state_trajectory,  # (batch_size, horizon, state_dim) or (batch_size, state_dim)
            estimation_matrix,
        )  # (batch_size, horizon, estimation_dim) or (batch_size, estimation_dim)
        return estimation

    # @torch.compile
    # def _forward_prediction(
    #     self,
    #     estimated_state_trajectory: torch.Tensor,
    #     predicted_state_trajectory: torch.Tensor,
    # ) -> torch.Tensor:
    #     estimation_matrix = self.matrix  # (state_dim, estimation_dim)
    #     estimation = torch.matmul(
    #         predicted_state_trajectory,  # (batch_size, horizon, state_dim) or (batch_size, state_dim)
    #         estimation_matrix,
    #     )  # (batch_size, horizon, estimation_dim) or (batch_size, estimation_dim)
    #     return estimation

    def forward(
        self,
        estimated_state_trajectory: torch.Tensor,
        # predicted_state_trajectory: torch.Tensor,
    ) -> torch.Tensor:
        estimation_trajectory = self._forward(
            estimated_state_trajectory,  # (batch_size, horizon, state_dim) or (batch_size, state_dim)
            # predicted_state_trajectory,  # (batch_size, horizon, state_dim) or (batch_size, state_dim)
        )  # (batch_size, horizon, estimation_dim) or (batch_size, estimation_dim)
        return estimation_trajectory
