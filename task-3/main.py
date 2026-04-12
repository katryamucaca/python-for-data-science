import numpy as np

# create array with 200 random numbers from -100 to 100
arr = np.random.randint(-100, 101, size=200)

# mask for positive numbers only
positive_mask = arr > 0
positive_numbers = arr[positive_mask]

print("positive numbers:\n", positive_numbers)

# replace all negative values with zeros
arr[arr < 0] = 0

print("array after replacing negatives:\n", arr)

# calculate mean of the modified array
mean_value = np.mean(arr)

print("mean value:", round(mean_value, 2))

