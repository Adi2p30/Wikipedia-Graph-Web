import random
from pyvis.network import Network

def network_visualise_link(all_paths, source, destination, specific_path, reduction_fraction=0.75):
    net = Network(notebook=True, cdn_resources="remote",
                  bgcolor="#222222", font_color="white",
                  height="750px", width="100%")

    nodes = set()
    edges = []
    node_connections = {}

    # All nodes and edges
    for path in all_paths:
        for i in range(len(path) - 1):
            nodes.add(path[i])
            nodes.add(path[i + 1])
            edges.append((path[i], path[i + 1]))
            node_connections[path[i]] = node_connections.get(path[i], 0) + 1
            node_connections[path[i + 1]] = node_connections.get(path[i + 1], 0) + 1


    important_nodes = set(specific_path)
    important_nodes.add(source)

    # Sample
    non_important_nodes = list(nodes - important_nodes)
    reduced_non_important_nodes = set(random.sample(non_important_nodes, int(len(non_important_nodes) * reduction_fraction)))

    # Opacity
    for node in nodes:
        opacity = min(0.8, 0.1 + 0.9 * (node_connections[node] / max(node_connections.values())))
        color = f'rgba(255, 0, 0, {opacity})' if node == source else f'rgba(0, 255, 0, {opacity})' if node == destination else f'rgba(255, 255, 255, {opacity})'
        if node in important_nodes or node in reduced_non_important_nodes:
            net.add_node(node, color=color)

    for path in all_paths:
        for i in range(len(path) - 1):
            net.add_edge(path[i], path[i + 1])

    for i in range(len(specific_path) - 1):
        net.add_edge(specific_path[i], specific_path[i + 1], color='rgba(0, 255, 255, 0.8)', width=3)

    physics_options = """
       var options = {
           "physics": {
               "enabled": true,
               "barnesHut": {
                   "gravitationalConstant": -6000,
                   "centralGravity": 0.3,
                   "springLength": 95,
                   "springConstant": 0.04,
                   "damping": 0.2,
                   "avoidOverlap": 0.2
               },
               "minVelocity": 0.75
           }
       }
       """

    net.set_options(physics_options)
    net.show("../../cache/graph.html")
