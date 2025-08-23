import torch

# Set requires_grad=True to track gradients
A = torch.tensor([[3.0, 1.0], [1.0, 2.0]], requires_grad=True)
b = torch.tensor([[9.0], [5.0]], requires_grad=True)

# Solve the linear system Ax = b
x = torch.linalg.solve(A, b)
print("Solution x:", x)

# Define a loss function - for example, the sum of elements in x
loss = x.sum()

# Perform backpropagation
loss.backward()

# Print the gradients
print("Gradient of A:", A.grad)
print("Gradient of b:", b.grad)
