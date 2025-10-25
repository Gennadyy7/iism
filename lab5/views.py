from django.shortcuts import render
from django.views.generic import TemplateView

from iism.utils import handle_lab_exceptions
from lab5.forms import PetriNetForm
from lab5.services.analyzer import PetriNetAnalyzer
from lab5.services.graph_builder import ReachabilityGraphBuilder
from lab5.services.marking import Marking
from lab5.services.petri_net import PetriNet
from lab5.services.renderer import SVGGraphRenderer
from lab5.services.simulator import PetriNetSimulator


class Lab5View(TemplateView):
    template_name = 'lab5/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = PetriNetForm()

        num_transitions = form.fields['num_transitions'].initial or 4

        transition_fields = []
        for i in range(1, num_transitions + 1):
            try:
                input_field = form[f"transition_{i}_input"]
                output_field = form[f"transition_{i}_output"]
                transition_fields.append({
                    'index': i,
                    'input': input_field,
                    'output': output_field,
                })
            except KeyError:
                break

        context['form'] = form
        context['transition_fields'] = transition_fields
        return context

    @handle_lab_exceptions
    def post(self, request):
        num_transitions_raw = request.POST.get('num_transitions', 4)
        try:
            num_transitions = int(num_transitions_raw)
            if not (1 <= num_transitions <= 20):
                num_transitions = 4
        except (TypeError, ValueError):
            num_transitions = 4

        form = PetriNetForm(request.POST, initial={'num_transitions': num_transitions})

        transition_fields = []
        for i in range(1, num_transitions + 1):
            try:
                input_field = form[f"transition_{i}_input"]
                output_field = form[f"transition_{i}_output"]
                transition_fields.append({
                    'index': i,
                    'input': input_field,
                    'output': output_field,
                })
            except KeyError:
                break

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

                simulator = PetriNetSimulator()
                simulation_path, is_cyclic = simulator.simulate_one_path(
                    petri_net,
                    max_steps=ReachabilityGraphBuilder.MAX_MARKINGS,
                )
                slide_svgs = []
                for mark in simulation_path:
                    try:
                        svg = SVGGraphRenderer.render_petri_net_with_marking(petri_net, mark)
                        slide_svgs.append(svg)
                    except Exception as e:
                        slide_svgs.append(f"<!-- Slide rendering failed: {e} -->")

                context = {
                    'form': form,
                    'transition_fields': transition_fields,
                    'result': {
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
                        'simulation_slides': slide_svgs,
                        'is_cyclic_simulation': is_cyclic,
                        'total_simulation_steps': len(slide_svgs),
                    },
                }
                return render(request, self.template_name, context)

            except Exception as e:
                form.add_error(None, f"Error during Petri net analysis: {e}")

        context = {
            'form': form,
            'transition_fields': transition_fields,
        }
        return render(request, self.template_name, context)
