import matplotlib.pyplot as plt
import numpy as np

# Hypothesis: Create a simple bar chart with values [1,4,2,5,3]
values = np.array([1, 4, 2, 5, 3])
labels = ['A', 'B', 'C', 'D', 'E']  # assuming labels for each value

# Print input values for verification
print("Input Values:", values)
print("Labels:", labels)

# Create the bar chart
plt.bar(labels, values)
plt.xlabel('Category')
plt.ylabel('Value')
plt.title('Simple Bar Chart')
plt.xticks(labels)  # ensure labels match up with ticks

# Display the plot briefly before saving ( Requirement: visible output )
plt.draw()
plt.pause(2)  # pause for 2 seconds to see the plot

# Save the chart as per goal
plt.savefig('test_chart.png')

# Close the plot after saving
plt.close()

print("Chart Saved as 'test_chart.png'")