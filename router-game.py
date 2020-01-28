import numpy as np
from Game import Game
import osbrain

def relation_generator(num_of_agents, num_of_coalitions, length):
    result = []

    index = 0
    for agent_id in range(num_of_agents):
        coalition = np.random.randint(0, num_of_coalitions)
        l = [agent_id, coalition]
        result.append(l)
        index += 1

    if index < length:
        while(index < length):

            agent_id = np.random.randint(0, num_of_agents)
            coalition = np.random.randint(0, num_of_coalitions)
            l = [agent_id, coalition]
            if not result.count(l):
                result.append(l)
            index += 1

    return result

if __name__ == "__main__":
    agents = [20]
    coalitions = [4]
    steps = [15]
    costs = []
    retries = 1
    server = osbrain.run_nameserver()
    relations = [[0,0],[1,0],[2,0],[3,0],[4,0],[5,0],[6,1],[7,1],[8,1],[9,1],[10,1],[11,1],[12,1],[13,1],[14,1],[0,2],[1,2],[6,2],[7,2],[8,2],[9,2],[3,2],[4,2]]
    r = relation_generator(agents[0], coalitions[0], 35)
    for index in range(retries):
        for step in steps:
            for coalition in coalitions:
                for agent in agents:
                    g = Game(agent, coalition, r)
                    cost = g.play(step)
                    costs.append(cost)
    print(sum(costs)/retries)
    print(f'Total relations:{relations.__len__()}')
