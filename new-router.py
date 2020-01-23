ALPHA = 0.1
BETA = 0.1
THROUGHPUT_META_STD = 20
PACKETS_STD_MEAN = 10


class Node:
    def __init__(self, incoming_packets, coalition_ability, throughput):
        self.expected_incoming_packets = incoming_packets

        self.throughput = np.random.normal(loc=throughput,
                                           scale=THROUGHPUT_META_STD)

        self.incoming_packets_meta_mean = self.throughput + np.random.normal(
            loc=0,  # should be zero mean since 
            scale=PACKETS_STD_MEAN)

        self.coalition_ability = coalition_ability

        self.current_packets = 0

    def calculate_cost_function(self):
        pass

    def process_packages(self):
        self.current_packets = np.random.normal(
            loc=self.incoming_packets_meta_mean,
            scale=int(PACKETS_STD_MEAN / 2))
        return self.current_packets

    def delegate_packages(self, other_node: Node, packets_ratio: float):
        """
        Share packets with other agent
        """
        other_node.current_packets = int(self.current_packets * packets_ratio)
        self.current_packets = int(self.current_packets * (1 - packets_ratio))

    def join_coalition(self, coalition):
        if coalition.add_node_coalition(self):
            print(f"Agent succeded in joining coaliton {coalition.name}")
            return True 
        else: 
            print(f"Agent failed to join the coaliton {coalition.name}")
            return False

    def leave_coalition(self, coalition):
        coalition.remove_node_from_coalition(self)

    def estimate_coalition_value(self, coalition):
        total_throughput = coalition.throughput + self.throughput
        own_contr = (self.packets_in_previous_turn +
                     self.expected_incoming_packets)
        coal_contr = ALPHA * (max(
            0, self.packets_in_previous_turn - total_throughput))
        return (own_contr - coal_contr) / total_throughput - BETA * len(
            self.coalition.nodes)


class Coalition:
    def __init__(self, name, max_capacity):
        self.max_capacity = max_capacity
        self.nodes = []
        self.throughput = 0
        self.current_packets = 0
        self.name = name

    def _calculate_throughput(self):
        self.throughput = 0
        for n in self.nodes:
            self.throughput += n.throughput

    def consider_node(self, node):
        if node in self.nodes:
            raise ValueError(f"Node already in coaltion {self.name}!")
        if len(self.nodes) >= self.max_capacity:
            return False
        else:
            return True

    def add_node_coalition(self, node):
        if self.consider_node(node)
            self.nodes.append(node)
            return True
        else:
            return False

    def remove_node_from_coalition(self, node):
        self.nodes.remove(node)