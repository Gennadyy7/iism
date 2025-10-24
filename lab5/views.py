from django.shortcuts import render
from django.views.generic import TemplateView

from iism.utils import handle_lab_exceptions
from lab5.forms import PetriNetForm
from lab5.services.analyzer import PetriNetAnalyzer
from lab5.services.marking import Marking
from lab5.services.petri_net import PetriNet
from lab5.services.renderer import SVGGraphRenderer


class Lab5View(TemplateView):
    template_name = 'lab5/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PetriNetForm()
        return context

    @handle_lab_exceptions
    def post(self, request):
        context = self.get_context_data()
        form = PetriNetForm(request.POST)

        if form.is_valid():
            try:
                places = form.cleaned_data['places']
                transitions = form.cleaned_data['transitions']
                input_arcs = form.cleaned_data['input_arcs']
                output_arcs = form.cleaned_data['output_arcs']
                initial_marking_list = form.cleaned_data['initial_marking']
                target_marking_list = form.cleaned_data['target_marking']

                initial_marking_dict = {
                    p: v for p, v in zip(places, initial_marking_list)
                }
                initial_marking = Marking.from_dict(initial_marking_dict, places)

                petri_net = PetriNet(
                    places=places,
                    transitions=transitions,
                    input_arcs=input_arcs,
                    output_arcs=output_arcs,
                    initial_marking=initial_marking
                )

                analyzer = PetriNetAnalyzer(petri_net)

                target_reachable = None
                if target_marking_list is not None:
                    target_marking_dict = {
                        p: v for p, v in zip(places, target_marking_list)
                    }
                    target_marking = Marking.from_dict(target_marking_dict, places)
                    target_reachable = analyzer.is_reachable(target_marking)

                try:
                    svg_diagram = SVGGraphRenderer.render_reachability_graph(analyzer)
                except Exception as e:
                    svg_diagram = f"<!-- SVG rendering failed: {e} -->"

                classification = analyzer.classify()

                context['result'] = {
                    'network': {
                        'places': list(places),
                        'transitions': list(transitions),
                        'input_arcs': input_arcs,
                        'output_arcs': output_arcs,
                        'initial_marking': initial_marking_list,
                        'target_marking': target_marking_list,
                    },
                    'analysis': {
                        'is_bounded': analyzer.is_bounded(),
                        'is_safe': analyzer.is_safe(),
                        'is_conservative': analyzer.is_conservative(),
                        'is_liveness': analyzer.is_liveness(),
                        'has_parallel_firing': analyzer.has_parallel_firing(),
                        'reachable': target_reachable,
                    },
                    'classification': {
                        'automaton': classification['automaton'],
                        'marked_graph': classification['marked_graph'],
                        'free_choice': classification['free_choice'],
                    },
                    'svg_diagram': svg_diagram,
                    'all_markings': [
                        [v if v != "ω" else "∞" for v in m.values]
                        for m in analyzer.all_markings
                    ],
                }

            except Exception as e:
                form.add_error(None, f"Error during Petri net analysis: {e}")
                context['form'] = form
        else:
            context['form'] = form

        return render(request, self.template_name, context)
