import numpy as np
import matplotlib.pyplot as plt

# Generate x values for sine function
x_sine = np.linspace(0, 4*np.pi, 10000)

# Calculate corresponding y values for sine function
y_sine = np.sin(x_sine)

# Generate random walk on [0, 4π]
np.random.seed(0)  # For reproducibility
n_steps = len(x_sine)
x_walk = np.cumsum(np.random.normal(size=n_steps))
y_walk = np.mod((x_walk + x_sine), 1) * np.sin(x_sine)

# Calculate total variation for sine function
dy_dx_sine = np.gradient(y_sine, x_sine)
total_variation_sine = np.sum(np.abs(dy_dx_sine))

# Calculate total variation for random walk
dy_dx_walk = np.gradient(y_walk, x_walk)
total_variation_walk = np.sum(np.abs(dy_dx_walk))

print("Total Variation of Sine Function:", total_variation_sine)
print("Total Variation of Random Walk:", total_variation_walk)

plt.figure(figsize=(8, 6))
plt.plot(x_sine, y_sine, label='Sine Function')
plt.plot(x_walk, y_walk, label='Random Walk', linestyle='--')
plt.legend()
plt.title('Comparison of Sine Function and Random Walk')
plt.xlabel('x')
plt.ylabel('y')
plt.savefig('output.png')

print("Plot saved as output.png")