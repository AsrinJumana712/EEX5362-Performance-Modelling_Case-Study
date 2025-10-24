# EEX5362-Performance-Modelling_Case-Study

# 🍔 Food Delivery Dispatch Simulation

This repository contains a Python-based simulation for a food delivery dispatch system, designed to model and analyze the performance of riders under different scenarios. The simulation uses the SimPy library for discrete-event simulation and Matplotlib for visualizing key metrics such as average wait times, throughput, queue lengths, and rider utilization.

## 📘 Overview
The simulation models a food delivery system where orders arrive randomly, are assigned to available riders, and are delivered within a specified time. It allows users to configure parameters such as the number of riders, order arrival intervals, delivery durations, and simulation time. The code generates event logs and performance metrics, visualized through plots, to compare scenarios like Baseline, Limited Rider Availability, More Riders, and Order Cancellation.

- **Language**: Python
- **Libraries**: `simpy`, `random`, `statistics`, `matplotlib`
- **Simulation Time**: Configurable (default 320 minutes)
- **Scenarios**: Baseline, Limited Rider Availability, More Riders, Order Cancellation.

## 🎯 Objectives

- To simulate a real-world food delivery system under different rider conditions.  
- To measure and compare system performance using key metrics.  
- To analyze trade-offs between rider availability and service quality.
- 
## ✨ Features
- **Configurable Parameters**: Adjust the number of riders (2-10), average time between orders (1-10 minutes), average delivery time (5-20 minutes), and total simulation time (30-600 minutes).
- **Performance Metrics**: Calculates average wait time, throughput, maximum queue length, rider utilization, and percentages of customers waited or served immediately.
- **Visualization**: Generates six plots, including average wait time and throughput comparisons across scenarios, wait time distribution, queue length over time, key metrics, and a pie chart of immediate vs. waited customers (focused on the Baseline scenario).
- **Event Logging**: Tracks order arrivals, assignments, and deliveries with timestamps.
- **Scenario Analysis**: Supports four predefined scenarios to study the impact of rider capacity and demand changes.

## Installation
Install my-project with npm

```bash
https://github.com/AsrinJumana712/EEX5362-Performance-Modelling_Case-Study.git
```
Install Dependencies:
Ensure you have Python 3.7+ installed. Install the required libraries using pip:

```bash
pip install simpy matplotlib
```
Verify Installation:
Run a simple Python command to confirm the libraries are installed:
```bash
import simpy
import matplotlib
print("Libraries installed successfully!")
```

## Usage

1. Run the Simulation:
Execute the script directly
```javascript
python s22010084_Case_Study.py
```

2. Configure Parameters:
- The program prompts for input with default values in brackets (e.g., [default 4] for riders).
- Press Enter to accept defaults, or enter custom values within the specified ranges:
    - Riders available: 2 to 10
    - Average time between orders: 1 to 10 minutes
    - Average delivery duration: 5 to 20 minutes
    - Total simulation time: 30 to 600 minutes

3. Output
- Console: Displays event logs for the Baseline scenario and summary metrics (e.g., average wait time, throughput) for all scenarios, plus a summary table and comparison with Baseline.
- Plots: Six matplotlib figures are generated and displayed, showing performance metrics and distributions.

## Example Output
Summary for Baseline Scenario

![1](https://github.com/user-attachments/assets/6d209cf6-77f1-4c78-b76d-a80b9ab4d930)

Experiment Summary Table

![2](https://github.com/user-attachments/assets/4f381013-92a4-43d9-8c70-650053a113fa)

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a new branch `(git checkout -b feature-branch)`.
3. Make your changes and commit them `(git commit -m "Description of changes")`.
4. Push to the branch `(git push origin feature-branch)`.
5. Open a pull request with a description of your changes.

Please ensure code follows PEP 8 style guidelines and includes tests or documentation updates if applicable.
## Acknowledgements

- Inspired by performance modeling case studies for EEX5362.
- Built using SimPy and Matplotlib.

## Author

*AR. Asrin Jumana*  
Undergraduate of Software Engineering (Hons)  
The Open University of Sri Lanka






