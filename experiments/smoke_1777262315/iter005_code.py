import numpy as np
import matplotlib.pyplot as plt

# Generate x-values
x = np.linspace(0, 4 * np.pi, 10000)

# Calculate sine function
y_smooth = np.sin(x)

# Calculate random walk
np.random.seed(42)  # for reproducibility
y_noisy = np.cumsum(np.random.normal(size=len(x)))

# Plot both curves
plt.figure(figsize=(10, 6))
plt.plot(x, y_smooth, label='Sine function')
plt.plot(x, y_noisy, 'r:', label='Random walk')
plt.legend()
plt.grid(True)
plt.title('Smoothness Comparison')
plt.savefig('output.png')

# Calculate total variation (simplified vectorized approach)
total_variation = np.sum(np.abs(np.diff(y_smooth)))
print(f'Total Variation of Smooth Curve: {total_variation}')

total_variation = np.sum(np.abs(np.diff(y_noisy)))
print(f'Total Variation of Noisy Curve: {total_variation}')