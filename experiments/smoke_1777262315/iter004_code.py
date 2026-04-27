import numpy as np
import matplotlib.pyplot as plt

# Define a function for generating a random walk
def random_walk(num_points):
    """Generate a random walk with 'num_points' number of points."""
    x = np.cumsum(np.random.normal(size=num_points))
    return x / np.sqrt(num_points)  # Normalize to have unit variance

# Generate the sine curve (smooth function)
x_smooth = np.linspace(0, 4 * np.pi, 10000)
y_smooth = np.sin(x_smooth)

# Generate a random walk
np.random.seed(42)  # For reproducibility
num_points = 10000
x_noisy = random_walk(num_points)

# Calculate total variation (quantify smoothness)
total_variation_smooth = np.sum(np.abs(np.diff(y_smooth)))
total_variation_noisy = np.sum(np.abs(np.diff(x_noisy)))

print(f"Total Variation of the Smooth Curve: {total_variation_smooth}")
print(f"Total Variation of the Noisy Curve: {total_variation_noisy}")

# Plot both curves
plt.figure(figsize=(10, 6))
plt.plot(x_smooth, y_smooth, label='Smooth (sine function)')
plt.plot(np.insert(x_noisy, 0, 0), np.linspace(-1, 1, num_points + 1) * 3, label="Noisy (random walk)")
plt.legend()
plt.xlabel('x')
plt.ylabel('y')
plt.title('Hypothesis Testing: Smoothness of Sine Function vs Random Walk')
plt.savefig('output.png')

print("Plot saved as output.png")