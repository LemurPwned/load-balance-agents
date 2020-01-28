import numpy as np
import graph_writer
import matplotlib.pyplot as plt
from Node import Node
from Coalition import Coalition

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

        index = 0
        # randomly assigns routers to coalitions
        for agent in self.agents:
            coal_num = np.random.randint(0, len(agent.neighbour_coalitions))
            agent.neighbour_coalitions[coal_num].join_coalition(agent)
            agent.current_coalition = coal_num
            if coal_num in self.coalitions:
                self.coalitions[agent.neighbour_coalitions[coal_num].id].agents_count[agent.id] += 1
            else:
                self.coalitions[agent.neighbour_coalitions[coal_num].id].agents_count[agent.id] = 1

            agent.current_coalition_ptr = agent.neighbour_coalitions[coal_num]
            index +=1

        for i in range(no_steps):
            print(f"\n############ STEP {i} ############\n")
            graph_writer.write_graph(self.agents, self.coalitions, self.relations, i)
            
            print([agent.current_coalition_ptr.id for agent in self.agents if agent.current_coalition_ptr is not None])

            for coalition in self.coalitions:
                coalition.membersCountHistory.append(len(coalition.members))

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
        fig4, ax4 = plt.subplots()
        fig5, ax5 = plt.subplots()

        #fig1.figsize(100,100)
        for agent in self.agents:
            ax1.plot(agent.dropped_packets_history)
            ax2.plot(agent.cost_history)
        coalitionsCount = dict()

        for coalition in self.coalitions:
            values = list(coalition.agents_count.values())
            coalitionsCount[int(coalition.id + 1)] = int(len(values))
            ax4.plot(coalition.membersCountHistory, label=f'CoalitionId: {coalition.id}')

        ax4.legend()
        width = 0.35
        vals = list(coalitionsCount.values())
        ks = list(coalitionsCount.keys())
        my_colors = 'rgbkymc'
        colors = list()
        for i in range(len(vals)):
            colors.append(my_colors[i])

        ax3.bar(ks, vals, width, color=colors, label=[i for i in range(len(ks))])

        ax1.set_title(f'dropped packets: {len(self.agents)} agents, {self.coalition_num} coalitions')
        ax1.set_ylabel("dropped_packets")
        ax1.set_xlabel("iterations")

        ax2.set_title(f'cost history: {len(self.agents)} agents, {self.coalition_num} coalitions')
        ax2.set_ylabel("cost")
        ax2.set_xlabel("iterations")

        ax3.set_title(f'Total number of agents in coalition during game: {len(self.agents)} agents, {self.coalition_num} coalitions')
        ax3.set_ylim([0, max(vals)+3])
        ax3.set_ylabel("number of agents")
        ax3.set_xlabel("coalitions")
        ax3.set_xticklabels([])

        for agent in self.agents:
            ax1.plot(agent.dropped_packets_history)
            ax2.plot(agent.cost_history)

        ax4.set_title(f'number of agents in coalition per iteration')
        ax4.set_ylabel("number of agents in coalition")
        ax4.set_xlabel("iterations")

        cost_histories_sum = []
        idies = []
        for agent in self.agents:
            cost_histories_sum.append(sum(agent.cost_history))
            idies.append(int(agent.id))

        ax5.bar(idies, cost_histories_sum, width, label=[i for i in range(len(idies))])

        ax5.set_title(f'Function Value -> ')
        ax5.set_ylabel("sum of values")
        ax5.set_xlabel("agents")
        ax5.set_ylim([min(cost_histories_sum)-0.5, max(cost_histories_sum)+0.5])

        rects = ax3.patches
        for rect, label in zip(rects, ks):
            height = rect.get_height()
            ax3.text(rect.get_x() + rect.get_width() / 2, height+0.3, label,
                    ha='center', va='bottom')

        plt.show()
        #fig1.savefig(f'images/dropped_packets_{len(self.agents)}_agents_{self.coalition_num}_coalition_{no_steps}_steps.png')
        #fig2.savefig(f'images/cost_history_{len(self.agents)}_agents_{self.coalition_num}_coalition_{no_steps}_steps.png')
