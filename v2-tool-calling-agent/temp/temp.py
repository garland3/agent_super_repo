import sys
import subprocess

# Install required packages
packages = ['pandas', 'matplotlib']
for package in packages:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

# Now re-run the original code
import pandas as pd
import matplotlib.pyplot as plt

# Download stock data from Yahoo Finance
intel = pd.DataReader('INTC', 'yahoo', start='2022-05-01', end='2023-05-01')  
nvidia = pd.DataReader('NVDA', 'yahoo', start='2022-05-01', end='2023-05-01')

# Plot the adjusted closing prices
plt.figure(figsize=(10, 6))
plt.plot(intel.index, intel['Adj Close'], label='Intel')
plt.plot(nvidia.index, nvidia['Adj Close'], label='NVIDIA')
plt.xlabel('Date')
plt.ylabel('Adjusted Close ($)')
plt.title('Intel vs NVIDIA Stock Prices') 
plt.legend()
plt.show()