import numpy as np
import matplotlib.pyplot as plt

THROUGHPUT_META_MEAN = 100
THROUGHPUT_META_STD = 10

PACKETS_STD_MEAN = THROUGHPUT_META_STD

ALPHA = 2


class Coalition():
    def __init__(self, id):
        self.members = []
        self.current_throughput_pool = 0
        self.packets_history = []
        self.id = id

    def recalculate(self):
        self.current_throughput_pool = 0
        for member in self.members:
            self.current_throughput_pool += member.throughput

    def remove_member(self, member):
        self.members.remove(member)
        self.recalculate()

    def join_coalition(self, member):
        if member in self.members:
            raise ValueError(f"Agent {member.id} already in coalition")
        else:
            self.members.append(member)
        self.recalculate()


class Node:
    def __init__(self, id=0):
        self.id = id
        self.throughput = np.random.normal(
            loc=THROUGHPUT_META_MEAN, scale=THROUGHPUT_META_STD)

        self.incoming_packets_meta_mean = self.throughput + np.random.normal(
            loc=0, # should be zero mean since 
            scale=PACKETS_STD_MEAN
        )
        """
        either 
        self.incoming_packets_meta_mean = np.random.normal(
            loc=self.throughput,
            scale=THROUGHPUT_META_STD)
        or 
        self.incoming_packets_meta_mean = self.throghput + np.random.normal(
            loc=0,
            scale=PACKETS_STD_MEAN)
        """

        self.cost_history = []
        self.dropped_packets_history = []
        self.processed_packets_history = []
        self.packets_incoming_mean = 0
        self.packets_incoming_std = 0

        self.current_packets = 0
        self.current_coalition = None
        self.saved_best_coal = None

    def make_move(self, coalitions):
        if self.current_coalition:
            if self.saved_best_coal != self.current_coalition:
                coalitions[self.saved_best_coal].join_coalition(self)
                coalitions[self.current_coalition].remove_member(self)
                self.current_coalition = self.saved_best_coal

    def sample_incoming_packets(self):
        self.current_packets = np.random.normal(loc=self.incoming_packets_meta_mean,
                                                scale=THROUGHPUT_META_STD)
        return self.current_packets

    def calculate_cost_function_at_step(self, step):
        cost, dropped, processed = self.calculate_cost_function(
            self.current_packets
        )
        self.dropped_packets_history.append(dropped)
        self.processed_packets_history.append(processed)
        self.cost_history.append(cost)
        return cost

    def calculate_cost_function(self, current_packets):
        dropped = 0
        processed = current_packets
        if self.throughput < current_packets:
            dropped = current_packets - self.throughput
            processed = self.throughput
        return (processed - ALPHA*dropped)/self.throughput, dropped, processed

    def estimate_coalition_values(self, coalitions):
        max_coalition_val, coalition_num = 0, 0
        for coalition in coalitions:
            coalition_packets = self.est_coalition_packets(coalition)
            coalition_val, dropped, processed = self.calculate_cost_function(
                coalition_packets)
            print(
                f"\tAgent {self.id} estimated {coalition_val} for coalition {coalition.id}")
            if coalition_val > max_coalition_val:
                coalition_num = coalition.id
                max_coalition_val = coalition_val
                dropped_val, processed_val = dropped, processed
        print(
            f"Agent {self.id} has calculated the best coalition: {coalition_num} with {coalition_val}")
        decision = 'stay'
        if coalition_num != self.current_coalition:
            decision = 'change'
        self.cost_history.append(coalition_val)
        self.dropped_packets_history.append(dropped_val)
        self.processed_packets_history.append(processed_val)
        print(f"Decision: {decision}")
        return coalition_num

    def est_coalition_packets(self, coalition, fairshare=False):
        if fairshare:
            packet_pool, total_throughput = 0, 0
            for member in coalition.members:
                total_throughput += member.throughput
                packet_pool += member.current_packets
            if self not in coalition.members:
                # if not a member -- value not included
                packet_pool += self.current_packets
                total_throughput += self.throughput
            return (self.throughput*packet_pool)/total_throughput
        else:
            packet_pool = 0
            for member in coalition.members:
                packet_pool += member.current_packets
            if self not in coalition.members:
                # if not a member -- value not included
                packet_pool += self.current_packets
            try:
                return packet_pool / len(coalition.members)
            except ZeroDivisionError:
                return 0

class Game:
    def __init__(self, agents_num=5, coalition_num=3):
        self.agents = [Node(i) for i in range(agents_num)]
        self.coalition_num = coalition_num
        self.coalitions = [Coalition(i) for i in range(self.coalition_num)]

    def play(self, no_steps):

        # randomly assigns routers to coalitions
        for agent in self.agents:
            coal_num = np.random.randint(0, self.coalition_num)
            self.coalitions[coal_num].members.append(agent)
            agent.current_coalition = coal_num

        for i in range(no_steps):
            print(f"\n############ STEP {i} ############\n")

            # sample the packets
            for agent in self.agents:
                agent.sample_incoming_packets()

            # select best coalition
            for agent in self.agents:
                agent.saved_best_coal = agent.estimate_coalition_values(
                    self.coalitions)

            # change coalitions
            for agent in self.agents:
                agent.make_move(self.coalitions)

        # drop packets_history

        fig1, ax1 = plt.subplots()
        fig2, ax2 = plt.subplots()
        for agent in self.agents:
            ax1.plot(agent.dropped_packets_history,
                     '.--', label=f'Agent {agent.id}')
            ax2.plot(agent.cost_history,
                     '.--', label=f'Agent {agent.id}')
        ax1.set_title("dropped_packets_history")
        ax2.set_title("cost history")
        ax1.legend()
        ax2.legend()
        plt.show()
        fig1.savefig(f'dropped_packets_{len(self.agents)}_agents_{self.coalition_num}_coalition_{no_steps}_steps.png')
        fig1.savefig(f'cost_history_{len(self.agents)}_agents_{self.coalition_num}_coalition_{no_steps}_steps.png')


if __name__ == "__main__":
    steps = [15, 50, 150]
    agents = [15, 30, 60]
    coalitions = [3, 5, 7]
    for step in steps:
        for coalition in coalitions:
            for agent in agents:
                g = Game(agent, coalition)
                g.play(step)

