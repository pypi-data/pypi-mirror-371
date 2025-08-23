import torch

batch_size = 8
state_dim = 4
dual_function_dim = 2
a = torch.ones(batch_size, state_dim, dual_function_dim)
b = torch.ones(batch_size, state_dim)

c = torch.einsum("bid,bi->bid", a, b)

print(c)
print(c.shape)  # (batch_size, state_dim)
