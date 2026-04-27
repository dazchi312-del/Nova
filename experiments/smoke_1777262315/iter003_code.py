import numpy as np
import matplotlib.pyplot as plt

def sine_function(x):
    """
    Calculate the value of the sine function at a given point x.
    
    Parameters:
    x (float): The input to the sine function.
    
    Returns:
    float: The value of the sine function at x.
    """
    return np.sin(x)

def random_walk(n, x_min, x_max):
    """
    Generate n points in a random walk on [x_min, x_max].
    
    Parameters:
    n (int): The number of points to generate.
    x_min (float): The minimum value of the random walk.
    x_max (float): The maximum value of the random walk.
    
    Returns:
    np.ndarray: An array of n evenly spaced values in [x_min, x_max].
    """
    # Generate n evenly spaced values
    x_walk = np.linspace(x_min, x_max, n)
    # Calculate y_walk as a random walk on top of x_walk
    y_walk = np.cumsum(np.random.normal(size=n))
    
    return x_walk, y_walk

def total_variation(y):
    """
    Calculate the total variation of y.
    
    Parameters:
    y (np.ndarray): An array of values for which to calculate the total variation.
    
    Returns:
    float: The total variation of y.
    """
    # Use np.gradient to calculate the gradient of y
    dy = np.gradient(y)
    # Use np.sum to calculate the L1 norm of the gradient
    return np.sum(np.abs(dy))

# Generate 1000 points in a random walk on [0, 4π]
x_walk, y_walk = random_walk(1000, 0, 4 * np.pi)

# Calculate the values of the sine function at the same points
y_sine = sine_function(x_walk)

# Plot both curves
plt.plot(x_walk, y_walk, label='Random Walk')
plt.plot(x_walk, y_sine, label='Sine Function')
plt.legend()
plt.title('Random Walk vs Sine Function')
plt.xlabel('x')
plt.ylabel('y')
plt.savefig('output.png')

print(f'Total variation of random walk: {total_variation(y_walk)}')
print(f'Total variation of sine function: {total_variation(y_sine)}')