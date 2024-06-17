import igraph as ig
import plotly.graph_objects as go


class ExtensiveFormGame:
    def __init__(self):
        self.graph = ig.Graph(directed=True)
        self.labels = {}
        self.positions = {}
        self.payoffs = {}

    def add_node(self, node_id, label, pos, payoff=None):
        self.graph.add_vertex(node_id)
        self.labels[node_id] = label
        self.positions[node_id] = pos
        if payoff:
            self.payoffs[node_id] = payoff

    def add_edge(self, from_node, to_node, label):
        self.graph.add_edge(from_node, to_node, label=label, dash=False)

    def add_dashed_edge(self, from_node, to_node, label):
        self.graph.add_edge(from_node, to_node, label=label, dash=True)

    def plot(self):
        nr_vertices = len(self.graph.vs)
        layout = self.graph.layout("rt")

        position = {k: layout[k] for k in range(nr_vertices)}
        Y = [layout[k][1] for k in range(nr_vertices)]
        M = max(Y)

        es = ig.EdgeSeq(self.graph)  # sequence of edges
        E = [e.tuple for e in es]  # list of edges

        L = len(position)
        Xn = [position[k][0] for k in range(L)]
        Yn = [2 * M - position[k][1] for k in range(L)]
        Xe = []
        Ye = []
        for edge in E:
            Xe += [position[edge[0]][0], position[edge[1]][0], None]
            Ye += [2 * M - position[edge[0]][1], 2 * M - position[edge[1]][1], None]

        labels = [self.labels[k] for k in range(L)]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=Xe,
                                 y=Ye,
                                 mode='lines',
                                 line=dict(color='rgb(210,210,210)', width=1),
                                 hoverinfo='none'
                                 ))
        fig.add_trace(go.Scatter(x=Xn,
                                 y=Yn,
                                 mode='markers+text',
                                 text=labels,
                                 textposition='top center',
                                 marker=dict(symbol='circle-dot',
                                             size=18,
                                             color='#6175c1',  # '#DB4551',
                                             line=dict(color='rgb(50,50,50)', width=1)
                                             ),
                                 hoverinfo='text',
                                 opacity=0.8
                                 ))

        def make_annotations(pos, text, font_size=10, font_color='rgb(250,250,250)'):
            L = len(pos)
            if len(text) != L:
                raise ValueError('The lists pos and text must have the same len')
            annotations = []
            for k in range(L):
                annotations.append(
                    dict(
                        text=text[k],  # or replace labels with a different list for the text within the circle
                        x=pos[k][0], y=2 * M - position[k][1],
                        xref='x1', yref='y1',
                        font=dict(color=font_color, size=font_size),
                        showarrow=False)
                )
            return annotations

        axis = dict(showline=False,  # hide axis line, grid, ticklabels and  title
                    zeroline=False,
                    showgrid=False,
                    showticklabels=False,
                    )

        fig.update_layout(title='Extensive Form Game Tree',
                          annotations=make_annotations(position, labels),
                          font_size=12,
                          showlegend=False,
                          xaxis=axis,
                          yaxis=axis,
                          margin=dict(l=40, r=40, b=85, t=100),
                          hovermode='closest',
                          plot_bgcolor='rgb(248,248,248)'
                          )
        fig.show()

    def find_spne(self):
        def backward_induction(node):
            children = self.graph.neighbors(node, mode="out")
            if not children:
                return self.payoffs.get(node)
            payoffs = []
            for child in children:
                payoffs.append((child, backward_induction(child)))
            if payoffs:
                best_payoff = max(payoffs, key=lambda x: x[1][0])
                return best_payoff[1]
            return None

        spne = {}
        for node in reversed(self.graph.topological_sorting()):
            if self.graph.outdegree(node) == 0:
                spne[node] = self.payoffs[node]
            else:
                spne[node] = backward_induction(node)
        print("Subgame Perfect Nash Equilibria:", spne)
        return spne


# Example Usage
if __name__ == "__main__":
    game = ExtensiveFormGame()

    # Add nodes (example based on provided image)
    game.add_node(0, '1', (0, 3))
    game.add_node(1, '2', (-1, 2))
    game.add_node(2, '1', (1, 2))
    game.add_node(3, 'L', (-1.5, 1))
    game.add_node(4, 'R', (-0.5, 1))
    game.add_node(5, 'L', (0.5, 1))
    game.add_node(6, 'R', (1.5, 1))
    game.add_node(7, '(4,3)', (-1.5, 0), payoff=(4, 3))
    game.add_node(8, '(2,4)', (-0.5, 0), payoff=(2, 4))
    game.add_node(9, '(0,1)', (0.5, 0), payoff=(0, 1))
    game.add_node(10, '(2,2)', (1.5, 0), payoff=(2, 2))
    game.add_node(11, '(1,6)', (2, 2), payoff=(1, 6))

    # Add edges
    game.add_edge(0, 1, 'D')
    game.add_edge(0, 11, 'U')
    game.add_edge(1, 3, 'A')
    game.add_edge(1, 4, 'B')
    game.add_edge(3, 7, 'L')
    game.add_edge(3, 8, 'R')
    game.add_edge(4, 9, 'L')
    game.add_edge(4, 10, 'R')
    game.add_dashed_edge(1, 4, '1')

    # Plot the game
    game.plot()

    # Find SPNE
    # game.find_spne()
