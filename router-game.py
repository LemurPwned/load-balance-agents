import numpy as np
import matplotlib.pyplot as plt

THROUGHPUT_META_MEAN = 100
THROUGHPUT_META_STD = 10

PACKETS_STD_MEAN = THROUGHPUT_META_STD

ALPHA = 2
BETA = 0.1

class Coalition():
    def __init__(self, id):
        self.members = []
        self.current_throughput_pool = 0
        self.packets_history = []
        self.id = id
        self.agentsCount = dict()

    def recalculate(self):
        self.current_throughput_pool = 0
        for member in self.members:
            self.current_throughput_pool += member.throughput

    def remove_member(self, member):
        self.members.remove(member)
        self.recalculate()

    def join_coalition(self, member):
        if member in self.members:
            pass# raise ValueError(f"Agent {member.id} already in coalition")
        else:
            self.members.append(member)
            if member.id in self.agentsCount:
                self.agentsCount[member.id] += 1
            else:
                self.agentsCount[member.id] = 1
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
        self.current_coalition_ptr = None
        self.saved_best_coal = None

        self.neighbour_coalitions = []

    def register_coalition(self, coalition):
        self.neighbour_coalitions.append(coalition)

    def make_move(self):
        if self.current_coalition and len(self.neighbour_coalitions)>0:
            if self.saved_best_coal != self.current_coalition:
                self.neighbour_coalitions[self.saved_best_coal].join_coalition(self)
                self.neighbour_coalitions[self.current_coalition].remove_member(self)
                self.current_coalition = self.saved_best_coal
                self.current_coalition_ptr = self.neighbour_coalitions[self.current_coalition]

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
        penalty = 0
        if self.current_coalition_ptr is not None:
                penalty += BETA * len(self.current_coalition_ptr.members) - 1
        if self.throughput < current_packets:
            dropped = current_packets - self.throughput
            processed = self.throughput
        return (processed - ALPHA*dropped)/self.throughput - penalty, dropped, processed


    def estimate_coalition_values(self):
        coalitions = self.neighbour_coalitions
        dropped_val, processed_val = 0.0, 0.0
        max_coalition_val, coalition_num = 0, 0
        for i, coalition in enumerate(coalitions):
            coalition_packets = self.est_coalition_packets(coalition)
            coalition_val, dropped, processed = self.calculate_cost_function(
                coalition_packets)
            print(
                f"\tAgent {self.id} estimated {coalition_val} for coalition {coalition.id}")
            if coalition_val > max_coalition_val:
                coalition_num = i
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
    def __init__(self, agents_num=5, coalition_num=3, relations=[]):
        self.agents = [Node(i) for i in range(agents_num)]
        self.coalition_num = coalition_num
        self.coalitions = [Coalition(i) for i in range(self.coalition_num)]
        self.relations = relations

    def play(self, no_steps):
        # register coalitions to routers

        for relation in self.relations:
            self.agents[relation[0]].register_coalition(self.coalitions[relation[1]]);

        # randomly assigns routers to coalitions
        for agent in self.agents:
            coal_num = np.random.randint(0, len(agent.neighbour_coalitions))
            agent.neighbour_coalitions[coal_num].members.append(agent)
            agent.current_coalition = coal_num
            agent.current_coalition_ptr = agent.neighbour_coalitions[coal_num]

        for i in range(no_steps):
            print(f"\n############ STEP {i} ############\n")

            # sample the packets
            for agent in self.agents:
                agent.sample_incoming_packets()

            # select best coalition
            for agent in self.agents:
                agent.saved_best_coal = agent.estimate_coalition_values()

            # change coalitions
            for agent in self.agents:
                agent.make_move()

        # drop packets_history

        fig1, ax1 = plt.subplots()
        fig2, ax2 = plt.subplots()
        fig3, ax3 = plt.subplots()
        #fig1.figsize(100,100)
        for agent in self.agents:
            ax1.plot(agent.dropped_packets_history)
            ax2.plot(agent.cost_history)
        coalitionsCount = dict()

        for coalition in self.coalitions:
            values = list(coalition.agentsCount.values())
            coalitionsCount[int(coalition.id + 1)] = int(len(values))

        width = 0.35
        vals = list(coalitionsCount.values())
        ks = list(coalitionsCount.keys())
        my_colors = 'rgbkymc'
        colors = list()
        for i in range(len(vals)):
            colors.append(my_colors[i])

        ax3.bar(ks, vals, width, color=colors)

        ax1.set_title(f'dropped packets: {len(self.agents)} agents, {self.coalition_num} coalitions')
        ax2.set_title(f'cost history: {len(self.agents)} agents, {self.coalition_num} coalitions')
        ax3.set_title(f'Total number of agents in coalition during game: {len(self.agents)} agents, {self.coalition_num} coalitions')
        ax3.set_ylim([min(vals), max(vals)+3])

        ax1.set_ylabel("dropped_packets")
        ax1.set_xlabel("iterations")


        ax2.set_ylabel("cost")
        ax2.set_xlabel("iterations")

        ax3.set_ylabel("number of agents")
        ax3.set_xlabel("coalitions")
        ax3.set_xticklabels([])

        rects = ax3.patches
        for rect, label in zip(rects, ks):
            height = rect.get_height()
            ax3.text(rect.get_x() + rect.get_width() / 2, height+0.3, label,
                    ha='center', va='bottom')

        plt.show()
        #fig1.savefig(f'images/dropped_packets_{len(self.agents)}_agents_{self.coalition_num}_coalition_{no_steps}_steps.png')
        #fig2.savefig(f'images/cost_history_{len(self.agents)}_agents_{self.coalition_num}_coalition_{no_steps}_steps.png')


if __name__ == "__main__":
    steps = [50]
    agents = [15]
    coalitions = [3]
    relations = [[[0,0],[1,0],[2,0],[3,0],[4,0],[5,0],[6,1],[7,1],[8,1],[9,1],[10,1],[11,1],[12,1],[13,1],[14,1],[0,2],[1,2],[6,2],[7,2],[8,2],[9,2],[3,2],[4,2]]]  
    for step in steps:
        for coalition in coalitions:
            for agent in agents:
                g = Game(agent, coalition,relations[0])
                g.play(step)

