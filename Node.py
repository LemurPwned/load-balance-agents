import numpy as np

THROUGHPUT_META_MEAN = 100
THROUGHPUT_META_STD = 10

PACKETS_STD_MEAN = THROUGHPUT_META_STD

ALPHA = 2
BETA = 0.01

def cost_fun(load, throughput):
    return (min(load, throughput) - max(0, load - throughput))/throughput


class Node:
    def __init__(self, id=0):
        self.id = id
        self.throughput = np.random.normal(
            loc=THROUGHPUT_META_MEAN, scale=THROUGHPUT_META_STD)

        self.incoming_packets_meta_mean = self.throughput + np.random.normal(
            loc=0, # should be zero mean since 
            scale=PACKETS_STD_MEAN
        )
        self.packets_in_previous_turn = 0
        self.expected_incoming_packets = 0
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
        if self.saved_best_coal is None:
            if(self.current_coalition is not None): 
                self.neighbour_coalitions[self.current_coalition].remove_member(self)
            self.current_coalition = None
            self.current_coalition_ptr = None
            return
        if len(self.neighbour_coalitions)>0:
            if self.saved_best_coal != self.current_coalition:
                if(self.current_coalition is not None): 
                    self.neighbour_coalitions[self.current_coalition].remove_member(self)
                self.neighbour_coalitions[self.saved_best_coal].join_coalition(self)
                self.current_coalition = self.saved_best_coal
                self.current_coalition_ptr = self.neighbour_coalitions[self.current_coalition]

    def sample_incoming_packets(self):
        self.current_packets = np.random.normal(loc=self.incoming_packets_meta_mean,
                                                scale=THROUGHPUT_META_STD)
        self.expected_incoming_packets = (self.packets_in_previous_turn + self.current_packets)/2
        self.packets_in_previous_turn = self.current_packets
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
        return (processed - ALPHA * dropped)/self.throughput - penalty, dropped, processed


    def estimate_coalition_values(self):
        coalitions = self.neighbour_coalitions
        dropped_val, processed_val = 0.0, 0.0
        dropped, processed = 0,0
        max_coalition_val, coalition_num = cost_fun(self.expected_incoming_packets, self.throughput)/2.0 , None
        for i, coalition in enumerate(coalitions):
            coalition_val = self.est_coalition_packets(coalition)
            #coalition_val, dropped, processed = self.calculate_cost_function(coalition_packets)
            print(
                f"\tAgent {self.id} estimated {coalition_val} for coalition {coalition.id}")
            if coalition_val >= max_coalition_val:
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

    def est_coalition_packets(self, coalition):
        coal_contr =  self.expected_incoming_packets + coalition.packets_in_previous_turn()
        predicted_load = (coal_contr) / (len(coalition.members)+1)
        return (min(predicted_load, self.throughput) - max(0, predicted_load - self.throughput))/self.throughput - BETA * len(
            coalition.members)
