from Game import Game





if __name__ == "__main__":
    agents = [15]
    coalitions = [3]
    steps = [30]
    relations = [[[0,0],[1,0],[2,0],[3,0],[4,0],[5,0],[6,1],[7,1],[8,1],[9,1],[10,1],[11,1],[12,1],[13,1],[14,1],[0,2],[1,2],[6,2],[7,2],[8,2],[9,2],[3,2],[4,2]]]  
    for step in steps:
        for coalition in coalitions:
            for agent in agents:
                g = Game(agent, coalition, relations[0])
                g.play(step)

