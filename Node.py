import numpy as np
from Coalition import Coalition

THROUGHPUT_META_MEAN = 100
THROUGHPUT_META_STD = 10
MAX_PERSISTENCE = 7
MIN_PERSISTENCE = 1

PACKETS_STD_MEAN = THROUGHPUT_META_STD
MARIAN_CONSTANT = 3.0
ALPHA = 2
BETA = 0.01


def cost_fun(load, throughput):
    return (min(load, throughput) - max(0, load - throughput)) / throughput


class Node:
    def __init__(self, id=0):
        self.id = id
        self.throughput = np.random.normal(loc=THROUGHPUT_META_MEAN,
                                           scale=THROUGHPUT_META_STD)

        self.incoming_packets_meta_mean = self.throughput + np.random.normal(
            loc=0,  # should be zero mean since 
            scale=PACKETS_STD_MEAN)
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
        self.current_coalition_ptr: Coalition = None
        self.saved_best_coal = None
        """
        Coalition persistence states how reluctant the node is to 
        join coaltion in this turn 
        """
        self.coalition_persistence = np.random.randint(MIN_PERSISTENCE,
                                                       MAX_PERSISTENCE)
        self.coalition_persistence_counter = 0
        self.neighbour_coalitions = []

    def register_coalition(self, coalition):
        self.neighbour_coalitions.append(coalition)

    def make_move(self):
        self.coalition_persistence_counter += 1
        if self.coalition_persistence:
            if self.coalition_persistence_counter < self.coalition_persistence:
                self.saved_best_coal = None
            else:
                self.coalition_persistence_counter = 0
        if self.saved_best_coal is None:
            if (self.current_coalition is not None):
                self.neighbour_coalitions[
                    self.current_coalition].remove_member(self)
            self.current_coalition = None
            self.current_coalition_ptr = None
            return
        if len(self.neighbour_coalitions) > 0:
            if self.saved_best_coal != self.current_coalition:
                if (self.current_coalition is not None):
                    self.neighbour_coalitions[
                        self.current_coalition].remove_member(self)
                self.neighbour_coalitions[self.saved_best_coal].join_coalition(
                    self)
                self.current_coalition = self.saved_best_coal
                self.current_coalition_ptr = self.neighbour_coalitions[
                    self.current_coalition]

    def sample_incoming_packets(self):
        self.current_packets = np.random.normal(
            loc=self.incoming_packets_meta_mean, scale=THROUGHPUT_META_STD)
        self.expected_incoming_packets = (self.packets_in_previous_turn +
                                          self.current_packets) / 2
        self.packets_in_previous_turn = self.current_packets
        return self.current_packets

    def calculate_cost_function(self, current_packets):
        dropped = 0
        processed = current_packets
        penalty = 0
        if self.current_coalition_ptr is not None:
            penalty += BETA * len(self.current_coalition_ptr.members) - 1
        if self.throughput < current_packets:
            dropped = current_packets - self.throughput
            processed = self.throughput
        return (processed - ALPHA *
                dropped) / self.throughput - penalty, dropped, processed

    def estimate_coalition_values(self):
        coalitions = self.neighbour_coalitions
        dropped_val, processed_val = 0.0, 0.0
        dropped, processed = 0, 0
        max_coalition_val, coalition_num = cost_fun(
            self.expected_incoming_packets,
            self.throughput) / MARIAN_CONSTANT, None
        for i, coalition in enumerate(coalitions):
            coalition_val = self.est_coalition_packets(coalition)
            #coalition_val, dropped, processed = self.calculate_cost_function(coalition_packets)
            print(
                f"\tAgent {self.id} estimated {coalition_val} for coalition {coalition.id}"
            )
            if coalition_val >= max_coalition_val:
                coalition_num = i
                max_coalition_val = coalition_val
                # extra packets
                coal_contr = self.expected_incoming_packets + coalition.packets_in_previous_turn(
                )

        print(
            f"Agent {self.id} has calculated the best coalition: {coalition_num} with {coalition_val}"
        )
        decision = 'stay'
        if coalition_num != self.current_coalition:
            decision = 'change'

        print(f"Decision: {decision}")
        return coalition_num

    def est_coalition_packets(self, coalition):
        coal_contr = self.expected_incoming_packets + coalition.packets_in_previous_turn(
        )
        predicted_load = (coal_contr) / (len(coalition.members) + 1)
        return (min(predicted_load, self.throughput) -
                max(0, predicted_load - self.throughput)
                ) / self.throughput - BETA * len(coalition.members)

    def post_turn_calculate_cost_functions(self, turn):
        if self.current_coalition_ptr:
            agent_packets_load = self.current_coalition_ptr.packets_in_previous_turn(
            ) / len(self.current_coalition_ptr.members)
        else:
            agent_packets_load = self.current_packets

        cost_val, _, _ = self.calculate_cost_function(agent_packets_load)
        dropped = max(0, agent_packets_load - self.throughput)
        processed = min(agent_packets_load, self.throughput)
        self.cost_history.append(cost_val)
        self.dropped_packets_history.append(dropped)
        self.processed_packets_history.append(processed)

        if self.current_coalition_ptr:
            self.current_coalition_ptr.update_current_turn_statistics(
                turn, cost_val, dropped, processed, self.throughput)
