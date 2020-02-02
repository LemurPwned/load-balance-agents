class Coalition():
    def __init__(self, id):
        self.members = []
        self.current_throughput_pool = 0
        self.packets_history = []
        self.membersCountHistory = []
        self.id = id
        self.agents_count = dict()
        self.dropped_packets_history = []
        self.processed_packets_history = []
        self.cost_history = []
        self.throughput_history = []

    def packets_in_previous_turn(self):
        return sum(
            [member.packets_in_previous_turn for member in self.members])

    def _calculate_throughput(self):
        throughput = 0
        for n in self.members:
            throughput += n.throughput
        return throughput

    def recalculate(self):
        self.current_throughput_pool = 0
        for member in self.members:
            self.current_throughput_pool += member.throughput

    def remove_member(self, member):
        self.members.remove(member)
        self.recalculate()

    def join_coalition(self, member):
        if member in self.members:
            pass  # raise ValueError(f"Agent {member.id} already in coalition")
        else:
            self.members.append(member)
            if member.id in self.agents_count.keys():
                self.agents_count[member.id] += 1
            else:
                self.agents_count[member.id] = 1
        self.recalculate()

    def initialize_statistics_for_turn(self, turn_id):
        self.dropped_packets_history.append(0)
        self.processed_packets_history.append(0)
        self.cost_history.append(0)
        self.throughput_history.append(0)

    def update_current_turn_statistics(self, turn_id, agent_cost,
                                       agent_dropped, agent_processed,
                                       agent_throughput):
        self.dropped_packets_history[turn_id] += agent_dropped
        self.processed_packets_history[turn_id] += agent_processed
        self.cost_history[turn_id] += agent_cost
        self.throughput_history[turn_id] += agent_throughput
