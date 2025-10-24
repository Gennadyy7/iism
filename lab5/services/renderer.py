import graphviz

from lab5.services.analyzer import PetriNetAnalyzer


class SVGGraphRenderer:
    @staticmethod
    def render_reachability_graph(analyzer: PetriNetAnalyzer) -> str:
        dot = graphviz.Digraph(comment='Reachability Graph', format='svg')
        dot.attr(rankdir='TB')

        for marking in analyzer.graph:
            label = ", ".join(f"{p}:{v}" for p, v in zip(marking.place_order, marking.values))
            node_id = str(hash(marking))[-8:]
            dot.node(node_id, label=label)

        for src, edges in analyzer.graph.items():
            src_id = str(hash(src))[-8:]
            for transition, dst in edges:
                dst_id = str(hash(dst))[-8:]
                dot.edge(src_id, dst_id, label=str(transition))

        return dot.pipe().decode('utf-8')
