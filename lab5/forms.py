from django import forms


class PetriNetForm(forms.Form):
    num_places = forms.IntegerField(
        label="Number of places",
        min_value=1,
        max_value=20,
        initial=5,
        help_text="Total number of places (e.g., p1, p2, ..., pn)."
    )
    num_transitions = forms.IntegerField(
        label="Number of transitions",
        min_value=1,
        max_value=20,
        initial=4,
        help_text="Total number of transitions (e.g., t1, t2, ..., tm)."
    )
    initial_marking = forms.CharField(
        label="Initial marking",
        help_text="Comma-separated integers in order of p1, p2, ..., pn. Example: 0,0,1,1,0",
        initial="0,0,1,1,0"
    )
    target_marking = forms.CharField(
        label="Target marking (for reachability check)",
        help_text="Comma-separated integers. Leave empty to skip reachability analysis.",
        required=False,
        initial="1,1,0,0,1"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        num_transitions = self._get_num_transitions_from_data(*args, **kwargs)
        for i in range(1, num_transitions + 1):
            self.fields[f'transition_{i}_input'] = forms.CharField(
                label=f"Input places for t{i}",
                help_text=f"Comma-separated place indices (1-based). Example: 3,4 → uses p3 and p4 as input.",
                initial="3" if i == 1 else ""
            )
            self.fields[f'transition_{i}_output'] = forms.CharField(
                label=f"Output places for t{i}",
                help_text=f"Comma-separated place indices (1-based). Example: 1,4 → adds tokens to p1 and p4.",
                initial="1,4" if i == 1 else ""
            )

    @staticmethod
    def _get_num_transitions_from_data(*args, **kwargs) -> int:
        if args and args[0]:
            try:
                return int(args[0].get('num_transitions', 4))
            except (TypeError, ValueError):
                pass
        return kwargs.get('initial', {}).get('num_transitions', 4)

    def clean_initial_marking(self) -> list[int]:
        data = self.cleaned_data['initial_marking']
        return self._parse_marking(data, 'Initial marking')

    def clean_target_marking(self) -> list[int] | None:
        data = self.cleaned_data.get('target_marking')
        if not data:
            return None
        return self._parse_marking(data, 'Target marking')

    def _parse_marking(self, data: str, field_name: str) -> list[int]:
        try:
            parts = [p.strip() for p in data.split(',')]
            marking = [int(x) for x in parts]
        except ValueError:
            raise forms.ValidationError(f"{field_name} must contain integers separated by commas.")
        num_places = self.cleaned_data.get('num_places')
        if num_places is not None and len(marking) != num_places:
            raise forms.ValidationError(
                f"{field_name} must have exactly {num_places} values (one per place)."
            )
        if any(x < 0 for x in marking):
            raise forms.ValidationError(f"{field_name} cannot contain negative values.")
        return marking

    def clean(self) -> dict:
        cleaned_data = super().clean()
        num_places = cleaned_data.get('num_places')
        num_transitions = cleaned_data.get('num_transitions')

        if not num_places or not num_transitions:
            return cleaned_data

        input_arcs = {}
        output_arcs = {}

        for i in range(1, num_transitions + 1):
            in_key = f'transition_{i}_input'
            out_key = f'transition_{i}_output'

            in_val = self.cleaned_data.get(in_key, "").strip()
            out_val = self.cleaned_data.get(out_key, "").strip()

            if in_val:
                try:
                    in_places = [int(x.strip()) for x in in_val.split(',')]
                except ValueError:
                    raise forms.ValidationError(f"Invalid input places for t{i}. Use comma-separated integers.")
                for p in in_places:
                    if p < 1 or p > num_places:
                        raise forms.ValidationError(f"Input place {p} for t{i} is out of range (1–{num_places}).")
                input_arcs[f"t{i}"] = [f"p{p}" for p in in_places]
            else:
                input_arcs[f"t{i}"] = []

            if out_val:
                try:
                    out_places = [int(x.strip()) for x in out_val.split(',')]
                except ValueError:
                    raise forms.ValidationError(f"Invalid output places for t{i}. Use comma-separated integers.")
                for p in out_places:
                    if p < 1 or p > num_places:
                        raise forms.ValidationError(f"Output place {p} for t{i} is out of range (1–{num_places}).")
                output_arcs[f"t{i}"] = [f"p{p}" for p in out_places]
            else:
                output_arcs[f"t{i}"] = []

        cleaned_data['input_arcs'] = input_arcs
        cleaned_data['output_arcs'] = output_arcs

        cleaned_data['places'] = tuple(f"p{i}" for i in range(1, num_places + 1))
        cleaned_data['transitions'] = tuple(f"t{i}" for i in range(1, num_transitions + 1))

        return cleaned_data
