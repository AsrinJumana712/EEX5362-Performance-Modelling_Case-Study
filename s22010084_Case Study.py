import simpy
import random
import statistics
import matplotlib.pyplot as plt

# Intermediate Food Delivery Simulation with Key Metrics and Graphs
def delivery_simulation(num_riders=2, sim_time=100, order_interval=5, delivery_mean=10, seed=1, scenario_name="Baseline", cancel_prob=0.0):
    random.seed(seed)
    env = simpy.Environment()
    riders = simpy.Resource(env, capacity=num_riders)

    wait_times = []
    delivery_times = []
    queue_history = []

    class Customer:
        def __init__(self, cid):
            self.id = cid
            self.delivery_time = 0

    def process_order(env, customer):
        arrival_time = env.now
        queue_history.append((env.now, len(riders.queue)))
        with riders.request() as request:
            yield request
            wait = env.now - arrival_time
            wait_times.append(wait)
            service_time = random.expovariate(1.0 / delivery_mean)
            yield env.timeout(service_time)
            customer.delivery_time = wait + service_time
            delivery_times.append(customer.delivery_time)
            print(f"[{scenario_name}] Order {customer.id} delivered at {env.now:.2f} min (Waited {wait:.2f} min)")

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

    print(f"\n[{scenario_name}] Simulation complete")
    print(f"Total orders served: {total_orders}")
    print(f"Average wait time: {avg_wait:.2f} min")
    print(f"Average delivery time: {avg_delivery:.2f} min")
    print(f"Maximum queue length: {max_queue}")
    print(f"Throughput: {throughput:.3f} orders/min")

    return {
        'avg_wait': avg_wait,
        'avg_delivery': avg_delivery,
        'max_queue': max_queue,
        'throughput': throughput,
        'wait_times': wait_times,
        'delivery_times': delivery_times,
        'queue_history': queue_history,
        'scenario_name': scenario_name
    }

# Run multiple scenarios and plot results
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
        results_list.append(results)

    # =======================
    # All Graphs in One Section
    # =======================

    scenario_names = [r['scenario_name'] for r in results_list]

    # 1. Avg Wait Time by Scenario
    plt.figure(figsize=(8,5))
    plt.bar(scenario_names, [r['avg_wait'] for r in results_list], color='skyblue')
    plt.ylabel('Average Wait Time (min)')
    plt.title('Average Wait Time by Scenario')
    plt.tight_layout()
    plt.show()

    # 2. Throughput by Scenario
    plt.figure(figsize=(8,5))
    plt.bar(scenario_names, [r['throughput'] for r in results_list], color='lightgreen')
    plt.ylabel('Throughput (orders/min)')
    plt.title('Throughput by Scenario')
    plt.tight_layout()
    plt.show()

    # 3. Pie Chart: Immediate vs Waited (last scenario)
    last_result = results_list[-1]
    total_customers = len(last_result['wait_times'])
    waited_count = sum(1 for w in last_result['wait_times'] if w > 0)
    immediate_count = total_customers - waited_count

    plt.figure(figsize=(6,6))
    plt.pie(
        [immediate_count, waited_count],
        labels=['Immediate', 'Waited'],
        autopct='%1.1f%%',
        colors=['green', 'red'],
        startangle=90,
        explode=(0.05, 0.05)
    )
    plt.title(f'Customers Served Immediately vs Waited - {last_result["scenario_name"]}')
    plt.tight_layout()
    plt.show()

    # 4. Queue Length Over Time (last scenario)
    if last_result['queue_history']:
        times, queue_lengths = zip(*last_result['queue_history'])
    else:
        times, queue_lengths = ([0], [0])

    plt.figure(figsize=(8,5))
    plt.step(times, queue_lengths, where='post', color='blue')
    plt.xlabel('Time (min)')
    plt.ylabel('Queue Length')
    plt.title(f'Queue Length Over Time - {last_result["scenario_name"]}')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # 5. Key Metrics Bar Chart for All Scenarios
    metrics = ['avg_wait', 'throughput', 'max_queue']
    metric_names = ['Average Wait (min)', 'Throughput (orders/min)', 'Max Queue']
    colors = ['skyblue', 'lightgreen', 'orange', 'pink']

    for i, metric in enumerate(metrics):
        plt.figure(figsize=(8,5))
        plt.bar(scenario_names, [r[metric] for r in results_list], color=colors)
        plt.ylabel(metric_names[i])
        plt.title(f'{metric_names[i]} by Scenario')
        plt.tight_layout()
        plt.show()

# Main
if __name__ == "__main__":
    run_experiments()
