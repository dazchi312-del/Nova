import numpy as np
import matplotlib.pyplot as plt

# Define the x values for both functions
x = np.linspace(0, 4 * np.pi, 10000)

# Generate a random walk with initial value at 0
y_walk = np.cumsum(np.random.normal(size=len(x)))

# Calculate the sine function values
y_sine = np.sin(x)

# Plot both curves
plt.plot(x, y_walk, label='Random Walk')
plt.plot(x, y_sine, label="Sine Function")
plt.legend()
plt.savefig('output.png')

# Calculate total variation for both functions
tv_walk = np.sum(np.abs(np.diff(y_walk)))
tv_sine = np.sum(np.abs(np.diff(y_sine)))

print(f"Total Variation of Random Walk: {tv_walk:.2e}")
print(f"Total Variation of Sine Function: {tv_sine:.2e}")

# Compare smoothness by dividing the total variations
smoothness_ratio = tv_walk / tv_sine
print(f"Smoothness Ratio (Random Walk/Sine): {smoothness_ratio:.2f}")