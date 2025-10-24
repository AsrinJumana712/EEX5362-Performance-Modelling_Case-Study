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
    
    class Customer:
        def __init__(self, cid):
            self.id = cid
            self.delivery_time = 0

    def process_order(env, customer):
        arrival_time = env.now
        with riders.request() as request:
            yield request
            wait = env.now - arrival_time
            wait_times.append(wait)
            service_time = random.expovariate(1.0 / delivery_mean)
            yield env.timeout(service_time)
            customer.delivery_time = env.now - arrival_time
            delivery_times.append(customer.delivery_time)
            print(f"Order {customer.id} delivered at {env.now:.2f} min (Waited {wait:.2f} min)")

    def order_generator(env):
        """Generate customers arriving at random intervals."""
        cid = 1
        while True:
            yield env.timeout(random.expovariate(1.0 / order_interval))
            if env.now >= sim_time:
                break
            env.process(process_order(env, Customer(cid)))  # Pass Customer object
            cid += 1

    env.process(order_generator(env))
    env.run(until=sim_time)

    # Calculate average wait time
    avg_wait = sum(wait_times)/len(wait_times) if wait_times else 0

    print(f"\nSimulation complete for {sim_time} minutes")
    print(f"Total orders served: {len(wait_times)}")
    print(f"Average wait time: {avg_wait:.2f} min")

# Run the beginner simulation
if __name__ == "__main__":
    delivery_simulation()
