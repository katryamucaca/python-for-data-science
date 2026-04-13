import numpy as np

matrix = np.random.randint(1, 101, (3, 3))
total_sum = np.sum(matrix)

max_val = np.max(matrix)
min_val = np.min(matrix)

max_idx = np.unravel_index(np.argmax(matrix), matrix.shape)
min_idx = np.unravel_index(np.argmin(matrix), matrix.shape)

sorted_matrix = np.sort(matrix, axis=1)

print(f"random matrix:")
print(matrix)
print(f"total sum: {total_sum}")
print(f"minimal value: {min_val} (index: {min_idx})")
print(f"maximum value: {max_val} (index: {max_idx})")
print("sorted matrix:")
print(sorted_matrix)