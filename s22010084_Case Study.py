import simpy
import random
import statistics

# Simple Food Delivery Simulation (Beginner Version)
def delivery_simulation(num_riders=2, sim_time=100, order_interval=5, delivery_mean=10, seed=1):
    random.seed(seed)
    env = simpy.Environment()
    riders = simpy.Resource(env, capacity=num_riders)

    wait_times = []
    delivery_times = []

    def customer(env, cid):
        """Simple customer process."""
        arrival = env.now
        with riders.request() as req:
            yield req
            start_service = env.now
            wait = start_service - arrival
            wait_times.append(wait)

            service_time = random.expovariate(1.0 / delivery_mean)
            yield env.timeout(service_time)
            delivery_times.append(wait + service_time)

    def order_generator(env):
        """Generate customers arriving at random intervals."""
        cid = 1
        while True:
            yield env.timeout(random.expovariate(1.0 / order_interval))
            if env.now >= sim_time:
                break
            env.process(customer(env, cid))
            cid += 1

    env.process(order_generator(env))
    env.run(until=sim_time)

    # --- Simple metrics ---
    total_orders = len(wait_times)
    avg_wait = statistics.mean(wait_times) if wait_times else 0
    avg_delivery = statistics.mean(delivery_times) if delivery_times else 0
    throughput = total_orders / sim_time  # orders per minute

    print("=== Basic Food Delivery Simulation ===")
    print(f"Total orders served: {total_orders}")
    print(f"Average wait time: {avg_wait:.2f} minutes")
    print(f"Average delivery time: {avg_delivery:.2f} minutes")
    print(f"Throughput: {throughput:.3f} orders/minute")

# Run simulation
if __name__ == "__main__":
    print("Welcome to the Food Delivery Simulation (Basic)")
    riders = int(input("Enter number of riders [default 2]: ") or 2)
    sim_time = float(input("Enter total simulation time [default 100]: ") or 100)
    order_interval = float(input("Enter mean order interval [default 5]: ") or 5)
    delivery_mean = float(input("Enter mean delivery time [default 10]: ") or 10)

    delivery_simulation(
        num_riders=riders,
        sim_time=sim_time,
        order_interval=order_interval,
        delivery_mean=delivery_mean
    )
