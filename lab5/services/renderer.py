import graphviz

from lab5.services.analyzer import PetriNetAnalyzer
from lab5.services.marking import Marking
from lab5.services.petri_net import PetriNet


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

    @staticmethod
    def render_petri_net_with_marking(petri_net: PetriNet, marking: Marking) -> str:
        dot = graphviz.Digraph(comment='Petri Net', format='svg')
        dot.attr(rankdir='LR', nodesep='0.5', ranksep='0.75')
        mark_dict = marking.to_dict()
        for p in petri_net.places:
            tokens = mark_dict.get(p, 0)
            if tokens == "ω":
                label = f"{p}\n∞"
            else:
                if isinstance(tokens, int) and tokens <= 3:
                    dots = "•" * tokens if tokens > 0 else ""
                    label = f"{p}\n{dots}"
                else:
                    label = f"{p}\n{tokens}"
            dot.node(p, label=label, shape='circle', fixedsize='true', width='0.8')
        for t in petri_net.transitions:
            dot.node(t, label=t, shape='box', style='filled', fillcolor='lightgray')
        for t, inputs in petri_net.input_arcs.items():
            for p in inputs:
                dot.edge(p, t)
        for t, outputs in petri_net.output_arcs.items():
            for p in outputs:
                dot.edge(t, p)
        return dot.pipe().decode('utf-8')
