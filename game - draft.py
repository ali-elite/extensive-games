import networkx as nx
import matplotlib.pyplot as plt


# Define the game tree
def create_game_tree():
    G = nx.DiGraph()

    # Add nodes with format (node, {'player': player_number, 'action': action, 'payoff': (payoff1, payoff2)})
    G.add_node('A', player=1)
    G.add_node('B', player=2)
    G.add_node('C', player=2)
    G.add_node('D', player=3)
    G.add_node('E', player=3)
    G.add_node('F', player=3)
    G.add_node('G', player=3)

    # Add edges with format (parent_node, child_node, {'action': action})
    G.add_edge('A', 'B', action='a1')
    G.add_edge('A', 'C', action='a2')
    G.add_edge('B', 'D', action='b1')
    G.add_edge('B', 'E', action='b2')
    G.add_edge('C', 'F', action='c1')
    G.add_edge('C', 'G', action='c2')

    # Add payoffs at the terminal nodes
    G.nodes['D']['payoff'] = (3, 2, 1)
    G.nodes['E']['payoff'] = (1, 3, 2)
    G.nodes['F']['payoff'] = (0, 0, 3)
    G.nodes['G']['payoff'] = (2, 1, 3)

    return G


# Draw the game tree
def draw_game_tree(G):
    pos = nx.multipartite_layout(G, subset_key="player")
    labels = {node: f"{node}\nP{data['player']}" for node, data in G.nodes(data=True)}
    edge_labels = {(u, v): f"{data['action']}" for u, v, data in G.edges(data=True)}
    nx.draw(G, pos, labels=labels, with_labels=True, node_size=2000, node_color="skyblue")
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    plt.show()


# Find SPNE
def find_spne(G):
    def backward_induction(node):
        if 'payoff' in G.nodes[node]:
            return G.nodes[node]['payoff']

        children = list(G.successors(node))
        if not children:
            return None

        player = G.nodes[node]['player']
        payoffs = []

        for child in children:
            child_payoff = backward_induction(child)
            payoffs.append((child, child_payoff))

        if player == 1:
            best_payoff = max(payoffs, key=lambda x: x[1][0])
        elif player == 2:
            best_payoff = max(payoffs, key=lambda x: x[1][1])
        elif player == 3:
            best_payoff = max(payoffs, key=lambda x: x[1][2])
        else:
            raise ValueError("Player number must be 1, 2, or 3.")

        G.nodes[node]['best_action'] = G.edges[node, best_payoff[0]]['action']
        G.nodes[node]['payoff'] = best_payoff[1]
        return best_payoff[1]

    root = [node for node in G.nodes if G.in_degree(node) == 0][0]
    backward_induction(root)

    spne = {}
    for node in G.nodes:
        if 'best_action' in G.nodes[node]:
            spne[node] = G.nodes[node]['best_action']

    return spne


# Main function
if __name__ == "__main__":
    game_tree = create_game_tree()
    draw_game_tree(game_tree)
    spne = find_spne(game_tree)
    print("Subgame Perfect Nash Equilibrium (SPNE):")
    for node, action in spne.items():
        print(f"At node {node}, choose action {action}")
