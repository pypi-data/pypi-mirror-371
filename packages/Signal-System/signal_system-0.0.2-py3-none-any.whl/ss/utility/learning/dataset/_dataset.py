from typing import List, Optional, Sequence, Tuple, TypeVar

from abc import abstractmethod

import torch
from torch.utils.data import DataLoader, Dataset, random_split

from ss.utility.deprecation import deprecated

D = TypeVar("D", bound=Dataset[Tuple[torch.Tensor, ...]])


class BaseDataSubsets(list[D]):
    def __init__(self, *args: D) -> None:
        super().__init__(args)

    def to_loaders(
        self,
        batch_size: Optional[int] = None,
        shuffle: bool = True,
    ) -> List[DataLoader[Tuple[torch.Tensor, ...]]]:
        data_loaders: List[DataLoader[Tuple[torch.Tensor, ...]]] = []
        for data_subset in self:
            data_loaders.append(
                DataLoader(data_subset, batch_size=batch_size, shuffle=shuffle)
            )
        return data_loaders


class BaseDataset(Dataset[Tuple[torch.Tensor, ...]]):

    @classmethod
    @abstractmethod
    def from_batch(
        cls, batch: Tuple[torch.Tensor, ...]
    ) -> Tuple[torch.Tensor, ...]:
        """
        Extracts the data from the batch.

        Parameters
        ----------
        batch: Sequence[torch.Tensor]
            The batch of data.

        Returns
        -------
        data: Tuple[torch.Tensor, ...]
            The data extracted from the batch.
            The data format is defined through the __getitem__ method.
        """
        raise NotImplementedError

    def split(
        self,
        split_ratio: Sequence[float],
        random_seed: Optional[int] = None,
    ) -> BaseDataSubsets:
        generator = (
            torch.Generator().manual_seed(random_seed) if random_seed else None
        )
        data_subsets = random_split(
            dataset=self,
            lengths=split_ratio,
            generator=generator,
        )
        return BaseDataSubsets(*data_subsets)

    def to_loader(
        self,
        batch_size: Optional[int] = None,
        shuffle: bool = True,
    ) -> DataLoader[Tuple[torch.Tensor, ...]]:
        data_loader = DataLoader(self, batch_size=batch_size, shuffle=shuffle)
        return data_loader


@deprecated(alternative_usage="BaseDataset(...).split(...).to_loaders(...)")
def dataset_split_to_loaders(
    dataset: Dataset,
    split_ratio: Sequence[float],
    batch_size: int = 128,
    shuffle: bool = True,
    random_seed: Optional[int] = None,
) -> List[DataLoader]:
    generator = (
        torch.Generator().manual_seed(random_seed) if random_seed else None
    )
    datasets = random_split(
        dataset=dataset,
        lengths=split_ratio,
        generator=generator,
    )
    data_loaders = []
    for dataset in datasets:
        data_loaders.append(
            DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)
        )
    return data_loaders
