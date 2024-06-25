import networkx as nx
import matplotlib.pyplot as plt


class ExtensiveFormGame:
    def __init__(self):
        self.tree = nx.DiGraph()
        self.payoffs = {}
        self.simultaneous_moves = []

    def add_node(self, node, player=None, payoff=None):
        self.tree.add_node(node, player=player, payoff=payoff)
        if payoff:
            self.payoffs[node] = payoff

    def add_edge(self, from_node, to_node, action):
        self.tree.add_edge(from_node, to_node, action=action)

    def add_simultaneous_move(self, node1, node2):
        self.simultaneous_moves.append((node1, node2))

    def hierarchical_pos(self, G, root=None, width=1., vert_gap=0.2, vert_loc=0, xcenter=0.5):
        pos = self._hierarchical_pos(G, root, width, vert_gap, vert_loc, xcenter)
        return pos

    def _hierarchical_pos(self, G, root, width=1., vert_gap=0.2, vert_loc=0, xcenter=0.5, pos=None, parent=None,
                          parsed=[]):
        if pos is None:
            pos = {root: (xcenter, vert_loc)}
        else:
            pos[root] = (xcenter, vert_loc)

        children = list(G.neighbors(root))
        if not isinstance(G, nx.DiGraph) and parent is not None:
            children.remove(parent)

        if len(children) != 0:
            dx = width / len(children)
            nextx = xcenter - width / 2 - dx / 2
            for child in children:
                nextx += dx
                pos = self._hierarchical_pos(G, child, width=dx, vert_gap=vert_gap, vert_loc=vert_loc - vert_gap,
                                             xcenter=nextx, pos=pos, parent=root, parsed=parsed)

        return pos

    def display_tree(self):
        pos = self.hierarchical_pos(self.tree, root='Root')
        labels = {node: (data['payoff'] if data['payoff'] is not None else data['player']) for node, data in
                  self.tree.nodes(data=True)}
        actions = nx.get_edge_attributes(self.tree, 'action')

        plt.figure(figsize=(12, 8))
        nx.draw(self.tree, pos, with_labels=True, labels=labels, node_size=2000, node_color='skyblue', font_size=10,
                font_color='black', font_weight='bold')
        nx.draw_networkx_edge_labels(self.tree, pos, edge_labels=actions, font_color='red')

        for (node1, node2) in self.simultaneous_moves:
            x1, y1 = pos[node1]
            x2, y2 = pos[node2]
            plt.plot([x1 + 0.03, x2 - 0.03], [y1, y2], 'k--')

        plt.show()

    def find_spne(self):
        spne = {}
        for node in reversed(list(nx.topological_sort(self.tree))):
            if node in self.payoffs:
                spne[node] = self.payoffs[node]
            else:
                player = self.tree.nodes[node]['player']
                choices = list(self.tree.successors(node))
                if player and choices:
                    best_choice = max(choices, key=lambda n: spne[n][0] if player == 'P1' else spne[n][1])
                    spne[node] = spne[best_choice]
                    self.tree.nodes[node]['best_choice'] = best_choice

        # Handle simultaneous moves
        for (node1, node2) in self.simultaneous_moves:
            player1 = self.tree.nodes[node1]['player']
            player2 = self.tree.nodes[node2]['player']
            choices1 = list(self.tree.successors(node1))
            choices2 = list(self.tree.successors(node2))

            best_choice1 = max(choices1, key=lambda n: spne[n][0])
            best_choice2 = max(choices2, key=lambda n: spne[n][1])

            spne[node1] = spne[best_choice1]
            spne[node2] = spne[best_choice2]

            self.tree.nodes[node1]['best_choice'] = best_choice1
            self.tree.nodes[node2]['best_choice'] = best_choice2

        return spne

    def display_spne(self):
        spne = self.find_spne()
        print("Subgame Perfect Nash Equilibrium:")
        for node, payoff in spne.items():
            if 'best_choice' in self.tree.nodes[node]:
                print(f"At node {node}, best choice: {self.tree.nodes[node]['best_choice']} with payoff {payoff}")


game = ExtensiveFormGame()

# Add nodes: (node, player, payoff)
game.add_node('Root', player='P1')
game.add_node('A', player='P2')
game.add_node('B', player='P2', payoff=(1, 6))
game.add_node('C',  player='P1')
game.add_node('D',  player='P1')
game.add_node('E', payoff=(4, 3))
game.add_node('F', payoff=(2, 4))
game.add_node('G', payoff=(0, 1))
game.add_node('H', payoff=(2, 2))

# Add edges: (from_node, to_node, action)
game.add_edge('Root', 'A', action='D')
game.add_edge('Root', 'B', action='U')
game.add_edge('A', 'C', action='A')
game.add_edge('A', 'D', action='B')
game.add_edge('C', 'E', action='L')
game.add_edge('C', 'F', action='R')
game.add_edge('D', 'G', action='L')
game.add_edge('D', 'H', action='R')

# Add simultaneous move (dashed line between nodes)
game.add_simultaneous_move('C', 'D')

game.display_tree()
game.display_spne()
