import simpy
import random
import statistics
import matplotlib.pyplot as plt

# Food Delivery Dispatch Simulation
def delivery_simulation(num_riders=4, sim_time=320, order_interval=5, delivery_mean=10,
                        seed=42, scenario_name="Baseline", cancel_prob=0.0):
    
    # Simulate a food delivery system with multiple riders
    random.seed(seed)
    env = simpy.Environment()
    riders = simpy.Resource(env, capacity=num_riders)
    
    # Initialize metrics and state
    wait_times, delivery_times = [], []
    rider_busy_times = [0] * num_riders
    rider_status = [False] * num_riders
    queue_history, event_log = [], []  # Track queue lengths over time and log events

    # Customer class
    class Customer:
        def __init__(self, cid):
            self.id = cid
            self.delivery_time = 0

    # Process each order
    def process_order(env, customer):
        arrival_time = env.now
        queue_history.append((env.now, len(riders.queue)))
        event_log.append(f"Order {customer.id} arrives at {arrival_time:.2f} minutes")

        with riders.request() as req:   
            yield req   # Wait until a rider is available
            start_service = env.now
            wait = start_service - arrival_time
            wait_times.append(wait)
            event_log.append(f"Order {customer.id} assigned to rider after waiting {wait:.2f} minutes at {start_service:.2f}")

            # Assign the first available rider
            rider_id = next(i for i, status in enumerate(rider_status) if not status)
            rider_status[rider_id] = True
            service_time = random.expovariate(1.0 / delivery_mean)
            rider_busy_times[rider_id] += service_time
            yield env.timeout(service_time)
            rider_status[rider_id] = False

            # Record delivery completion
            customer.delivery_time = wait + service_time # Total time for this order
            delivery_times.append(customer.delivery_time)
            event_log.append(f"Order {customer.id} delivered at {env.now:.2f} minutes")
            queue_history.append((env.now, len(riders.queue)))

    # Generate orders over time
    def order_generator(env):
        cid = 1
        while True:
            inter_arrival = random.expovariate(1.0 / order_interval)  # Time until next order
            yield env.timeout(inter_arrival)  # Wait until next order arrives
            if env.now >= sim_time:   # Stop if simulation time exceeded
                break

            # Random order cancellation
            if random.random() < cancel_prob:
                event_log.append(f"Order {cid} CANCELLED at {env.now:.2f} minutes")
                cid += 1
                continue

            env.process(process_order(env, Customer(cid))) # Start processing this order
            cid += 1

    # Run the simulation
    env.process(order_generator(env))  # Start order generation in the environment
    env.run(until=sim_time)            # Run simulation for specified duration
    while len(riders.queue) > 0 or any(rider_status):  # Continue until all orders completed
        env.step()                     # Advance simulation one step
    
    # Calculate Performance Metrics
    avg_wait = statistics.mean(wait_times) if wait_times else 0           # Average wait time
    avg_delivery = statistics.mean(delivery_times) if delivery_times else 0  # Avg delivery time
    max_queue = max([q for _, q in queue_history]) if queue_history else 0   # Max queue length
    utilization = (sum(rider_busy_times) / (num_riders * sim_time)) * 100    # Rider utilization %
    total_orders = len(wait_times)                                         # Total served orders
    throughput = total_orders / sim_time                                   # Orders per minute
    pct_waited = (sum(1 for w in wait_times if w > 0) / total_orders * 100) if total_orders else 0  # % waited

    return {
        'avg_wait': avg_wait,
        'avg_delivery': avg_delivery,
        'max_queue': max_queue,
        'utilization': min(utilization, 100),
        'throughput': throughput,
        'pct_waited': pct_waited,
        'pct_immediate': 100 - pct_waited,
        'wait_times': wait_times,
        'delivery_times': delivery_times,
        'queue_history': queue_history,
        'event_log': event_log,
        'scenario_name': scenario_name,
        'sim_time': sim_time
    }


# Enhanced Combined Plots for Report
def plot_simplified_results(results_list, baseline_name="Baseline"):
    # 1 & 2: Scenario comparison (avg wait and throughput)
    scenarios = [name for name, _ in results_list]
    avg_waits = [r['avg_wait'] for _, r in results_list]
    throughputs = [r['throughput'] for _, r in results_list]

    # 1. Avg Wait Time by Scenario
    plt.figure(figsize=(8,5))
    plt.bar(scenarios, avg_waits, color='skyblue')
    plt.ylabel('Avg Wait Time (min)')
    plt.title('Average Wait Time by Scenario')
    plt.tight_layout()
    plt.show()

    # 2. Throughput by Scenario
    plt.figure(figsize=(8,5))
    plt.bar(scenarios, throughputs, color='lightgreen')
    plt.ylabel('Throughput (orders/min)')
    plt.title('Throughput by Scenario')
    plt.tight_layout()
    plt.show()

    # Baseline detailed plots only
    baseline_results = next(r for name, r in results_list if name == baseline_name)

    # 3. Wait time distribution (Histogram)
    plt.figure(figsize=(8,5))
    plt.hist(baseline_results['wait_times'], bins=10, edgecolor='black', alpha=0.7, color='teal')
    plt.xlabel('Wait Time (min)')
    plt.ylabel('Frequency')
    plt.title(f'Wait Time Distribution - {baseline_name}')
    plt.grid(axis='y')
    plt.tight_layout()
    plt.show()

    # 4. Queue length over time (Step plot)
    if baseline_results['queue_history']:
        times, queue_lens = zip(*baseline_results['queue_history'])
    else:
        times, queue_lens = ([0],[0])
    plt.figure(figsize=(10,5))
    plt.step(times, queue_lens, where='post', color='blue')
    plt.scatter(times, queue_lens, s=10)
    plt.xlabel('Time (minutes)')
    plt.ylabel('Queue Length')
    plt.title(f'Queue Length Over Time - {baseline_name}')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # 5. Key Metrics (Baseline)
    metrics = ['Avg Wait', 'Throughput', 'Final Queue', '% Waited', 'Utilization']
    values = [baseline_results['avg_wait'], baseline_results['throughput'], 
              baseline_results['queue_history'][-1][1] if baseline_results['queue_history'] else 0,
              baseline_results['pct_waited'], baseline_results['utilization']]
    plt.figure(figsize=(10,5))
    bars = plt.bar(metrics, values, color=['blue','green','orange','red','purple'])
    plt.title(f'Key Metrics - {baseline_name}')
    plt.ylabel('Value')
    for bar in bars:
        h = bar.get_height()
        plt.annotate(f'{h:.2f}', xy=(bar.get_x() + bar.get_width()/2, h),
                     xytext=(0,3), textcoords='offset points', ha='center', va='bottom', fontsize=9)
    plt.tight_layout()
    plt.show()

    # 6. Pie chart: Immediate vs Waited (Baseline)
    total_customers = len(baseline_results['wait_times'])
    waited_count = sum(1 for w in baseline_results['wait_times'] if w > 0)
    immediate_count = total_customers - waited_count

    plt.figure(figsize=(6, 6))
    plt.pie(
        [immediate_count, waited_count],
        labels=['Immediate', 'Waited'],
        autopct='%1.1f%%',
        colors=['green', 'red'],
        startangle=90,
        explode=(0.05, 0.05)
    )
    plt.title(f'Customers Served Immediately vs Waited - {baseline_name}')
    plt.tight_layout()
    plt.show()


# Run Experiments
def run_experiments(base_params):
    scenarios = [
        ("Baseline", base_params),  # keep as is
        ("Limited Rider Availability", {**base_params, 'num_riders': max(1, base_params['num_riders']//2)}),
        ("More Riders", {**base_params, 'num_riders': base_params['num_riders']*2}),  # keep as is
        ("Order Cancellation", {**base_params, 'order_interval': base_params['order_interval']*1.2})
    ]
    
    results_list = []

    for name, params in scenarios:
        results = delivery_simulation(**params, scenario_name=name)
        results_list.append((name, results))

        # Print Event Log
        print(f"\n=== Event Log for {name} Scenario ===")
        for log in results['event_log']:
            print(log)

        # Print Summary Metrics
        print(f"\nSimulation complete (time: {results['sim_time']:.0f} min)")
        print(f"Total customers served: {len(results['wait_times'])}")
        print(f"Average wait time: {results['avg_wait']:.2f} min")
        print(f"Throughput: {results['throughput']:.3f} cust/min")
        print(f"Final queue length: {results['queue_history'][-1][1] if results['queue_history'] else 0}")
        print(f"Percentage of customers who waited: {results['pct_waited']:.2f}%")
        print(f"Percentage of customers served immediately: {results['pct_immediate']:.2f}%")
        print(f"Rider utilization: {results['utilization']:.2f}%")

    # Experiment Summary Table
    print("\n=== Experiment Summary Table ===")
    header = f"{'Scenario':<20}{'Avg Wait':>10}{'Throughput':>12}{'Final Q':>10}{'%Waited':>10}{'Util(%)':>10}"
    print(header)
    print("-" * len(header))

    for name, r in results_list:
        final_queue = r['queue_history'][-1][1] if r['queue_history'] else 0
        print(f"{name:<20}{r['avg_wait']:>10.2f}{r['throughput']:>12.3f}{final_queue:>10}{r['pct_waited']:>10.2f}{r['utilization']:>10.1f}")

    # Comparison with Baseline Scenario
    print("\n=== Comparison with Baseline Scenario ===")
    baseline = results_list[0][1]
    print(f"{'Scenario':<25}{'Avg Wait %chg':>15}{'Throughput %chg':>20}{'Utilization %chg':>20}")
    print("-" * len(header))

    for name, r in results_list[1:]:
        avg_wait_chg = ((r['avg_wait'] - baseline['avg_wait']) / baseline['avg_wait'] * 100) if baseline['avg_wait'] else 0
        throughput_chg = ((r['throughput'] - baseline['throughput']) / baseline['throughput'] * 100) if baseline['throughput'] else 0
        util_chg = r['utilization'] - baseline['utilization']
        print(f"{name:<25}{avg_wait_chg:>15.1f}%{throughput_chg:>20.1f}%{util_chg:>20.1f}%")

    # Plot results
    plot_simplified_results(results_list, baseline_name="Baseline")


# Main Program
if __name__ == "__main__":
    print("=== Welcome to the Food Delivery Simulation ===")
    print("Configure your baseline scenario (press Enter to accept default values):")
    print("Options:")
    print("1. Riders available: 2 to 10")
    print("2. Average time between orders: 1 to 10 minutes")
    print("3. Average delivery duration: 5 to 20 minutes")
    print("4. Total simulation time: 30 to 600 minutes")
    print("-----------------------------------------------")

    num_riders = int(input("Enterumber of riders [default 4]: ") or 4)
    sim_time = float(input("Simulation duration in minutes [default 320]: ") or 320)
    order_interval = float(input("Mean interval between orders [default 5]: ") or 5)
    delivery_mean = float(input("Average delivery time per order [default 10]: ") or 10)

    base_params = {
        'num_riders': num_riders,
        'sim_time': sim_time,
        'order_interval': order_interval,
        'delivery_mean': delivery_mean,
        'seed': 42
    }

    run_experiments(base_params)