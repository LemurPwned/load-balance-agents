class Coalition():
    def __init__(self, id):
        self.members = []
        self.current_throughput_pool = 0
        self.packets_history = []
        self.membersCountHistory = []
        self.id = id
        self.agents_count = dict()
        
    def packets_in_previous_turn(self):
        return sum([member.packets_in_previous_turn for member in self.members])

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
            pass# raise ValueError(f"Agent {member.id} already in coalition")
        else:
            self.members.append(member)
            if member.id in self.agents_count.keys():
                self.agents_count[member.id] += 1
            else:
                self.agents_count[member.id] = 1
        self.recalculate()

