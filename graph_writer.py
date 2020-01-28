from Coalition import Coalition

colors = {0:"#FF0000", 1:"#00FF00", 2: "#0000FF", -1: "#FFFFFF", 3:"#ffbb0e"}

def write_graph(agents, coalitions, relations, step):
    graph_id = 0
    for coalition in coalitions:
        coalition.graph_id = graph_id
        graph_id += 1
        coalition.id
        coalition.x = 5
        coalition.y = coalition.id
        coalition.color = colors[coalition.id]
    for agent in agents:
        if (agent.current_coalition is None):
            agent.color = colors[-1]
        else:
            agent.color = agent.current_coalition_ptr.color
        agent.x = 0
        agent.y = agent.id
        agent.graph_id = graph_id
        graph_id += 1

                
    graph_str = "graph G {\n"
    for agent in agents:
        graph_str+='{0}[fillcolor="{3}",style=filled pos="{1},{2}!" label="A"];\n'.format(agent.graph_id,agent.x,agent.y, agent.color)
    for coalition in coalitions:
        graph_str+='{0}[fillcolor="{3}",style=filled pos="{1},{2}!" label="C"];\n'.format(coalition.graph_id,coalition.x,coalition.y, coalition.color)
    for relation in relations:
        graph_str+='{0}--{1};\n'.format(agents[relation[0]].graph_id, coalitions[relation[1]].graph_id)
    graph_str+="}"
    with open("output{0}.dot".format(step),"w+") as f:
        f.write(graph_str)