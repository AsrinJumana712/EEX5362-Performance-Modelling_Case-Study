import simpy
import random
import statistics
import matplotlib.pyplot as plt

# Intermediate Food Delivery Simulation with Key Metrics and Simplified Graphs
def delivery_simulation(num_riders=2, sim_time=100, order_interval=5, delivery_mean=10, seed=1,
                        scenario_name="Baseline", cancel_prob=0.0):
    random.seed(seed)
    env = simpy.Environment()
    riders = simpy.Resource(env, capacity=num_riders)

    wait_times = []
    delivery_times = []
    queue_history = []
    busy_time = 0  # total time riders are busy

    class Customer:
        def __init__(self, cid):
            self.id = cid
            self.delivery_time = 0

    def process_order(env, customer):
        nonlocal busy_time
        arrival_time = env.now
        queue_history.append((env.now, len(riders.queue)))
        with riders.request() as request:
            yield request
            wait = env.now - arrival_time
            wait_times.append(wait)
            service_time = random.expovariate(1.0 / delivery_mean)
            busy_time += service_time
            yield env.timeout(service_time)
            customer.delivery_time = wait + service_time
            delivery_times.append(customer.delivery_time)
            print(f"[{scenario_name}] Order {customer.id} delivered at {env.now:.2f} min "
                  f"(Waited {wait:.2f} min)")

    def order_generator(env):
        cid = 1
        while True:
            yield env.timeout(random.expovariate(1.0 / order_interval))
            if env.now >= sim_time:
                break
            if random.random() < cancel_prob:
                print(f"[{scenario_name}] Order {cid} CANCELLED at {env.now:.2f} min")
                cid += 1
                continue
            env.process(process_order(env, Customer(cid)))
            cid += 1

    env.process(order_generator(env))
    env.run(until=sim_time)

    avg_wait = statistics.mean(wait_times) if wait_times else 0
    avg_delivery = statistics.mean(delivery_times) if delivery_times else 0
    max_queue = max([q for _, q in queue_history]) if queue_history else 0
    total_orders = len(wait_times)
    throughput = total_orders / sim_time  # orders per minute
    pct_waited = sum(1 for w in wait_times if w > 0) / total_orders * 100 if total_orders > 0 else 0
    utilization = busy_time / (num_riders * sim_time) * 100

    print(f"\n[{scenario_name}] Simulation complete")
    print(f"Total orders served: {total_orders}")
    print(f"Average wait time: {avg_wait:.2f} min")
    print(f"Average delivery time: {avg_delivery:.2f} min")
    print(f"Maximum queue length: {max_queue}")
    print(f"Throughput: {throughput:.3f} orders/min")
    print(f"Percentage waited: {pct_waited:.2f}%")
    print(f"Riders utilization: {utilization:.2f}%")

    return {
        'avg_wait': avg_wait,
        'avg_delivery': avg_delivery,
        'max_queue': max_queue,
        'throughput': throughput,
        'wait_times': wait_times,
        'delivery_times': delivery_times,
        'queue_history': queue_history,
        'pct_waited': pct_waited,
        'utilization': utilization,
        'scenario_name': scenario_name
    }

# Run multiple scenarios
def run_experiments():
    base_params = {
        'num_riders': 2,
        'sim_time': 100,
        'order_interval': 5,
        'delivery_mean': 10,
        'seed': 1
    }

    scenarios = [
        ("Baseline", base_params),
        ("Limited Riders", {**base_params, 'num_riders': 1}),
        ("More Riders", {**base_params, 'num_riders': 4}),
        ("Order Cancellation", {**base_params, 'cancel_prob': 0.3})
    ]

    results_list = []
    for name, params in scenarios:
        results = delivery_simulation(**params, scenario_name=name)
        results_list.append((name, results))

    plot_simplified_results(results_list)

# Simplified plotting function
def plot_simplified_results(results_list, baseline_name="Baseline"):
    # Scenario comparison (avg wait and throughput)
    scenarios = [name for name, _ in results_list]
    avg_waits = [r['avg_wait'] for _, r in results_list]
    throughputs = [r['throughput'] for _, r in results_list]

    # Avg Wait Time by Scenario
    plt.figure(figsize=(8,5))
    plt.bar(scenarios, avg_waits, color='skyblue')
    plt.ylabel('Avg Wait Time (min)')
    plt.title('Average Wait Time by Scenario')
    plt.tight_layout()
    plt.show()

    # Throughput by Scenario
    plt.figure(figsize=(8,5))
    plt.bar(scenarios, throughputs, color='lightgreen')
    plt.ylabel('Throughput (orders/min)')
    plt.title('Throughput by Scenario')
    plt.tight_layout()
    plt.show()

    # Baseline detailed plots
    baseline_results = next(r for name, r in results_list if name == baseline_name)

    # Wait time histogram
    plt.figure(figsize=(8,5))
    plt.hist(baseline_results['wait_times'], bins=10, edgecolor='black', alpha=0.7, color='teal')
    plt.xlabel('Wait Time (min)')
    plt.ylabel('Frequency')
    plt.title(f'Wait Time Distribution - {baseline_name}')
    plt.grid(axis='y')
    plt.tight_layout()
    plt.show()

    # Queue length over time
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

    # Key Metrics Bar Chart
    metrics = ['Avg Wait', 'Throughput', 'Final Queue', '% Waited', 'Utilization']
    values = [
        baseline_results['avg_wait'],
        baseline_results['throughput'],
        baseline_results['queue_history'][-1][1] if baseline_results['queue_history'] else 0,
        baseline_results['pct_waited'],
        baseline_results['utilization']
    ]
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

    # Pie chart: Immediate vs Waited
    total_customers = len(baseline_results['wait_times'])
    waited_count = sum(1 for w in baseline_results['wait_times'] if w > 0)
    immediate_count = total_customers - waited_count
    plt.figure(figsize=(6,6))
    plt.pie([immediate_count, waited_count],
            labels=['Immediate', 'Waited'],
            autopct='%1.1f%%',
            colors=['green','red'],
            startangle=90,
            explode=(0.05,0.05))
    plt.title(f'Customers Served Immediately vs Waited - {baseline_name}')
    plt.tight_layout()
    plt.show()

# Main
if __name__ == "__main__":
    run_experiments()
