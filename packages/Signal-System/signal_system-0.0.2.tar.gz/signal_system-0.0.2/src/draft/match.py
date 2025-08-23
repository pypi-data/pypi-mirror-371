import h5py
import numpy as np

tensors = [np.random.randn(4, 3), np.random.randn(2, 5), np.random.randn(6, 2)]

with h5py.File("tensors.h5", "w") as f:
    grp = f.create_group("tensor_seq")
    for i, tensor in enumerate(tensors):
        grp.create_dataset(f"tensor_{i}", data=tensor)
