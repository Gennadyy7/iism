from django import forms
from scipy import stats


class Task1Form(forms.Form):
    DISTRIBUTION_CHOICES = [
        ('norm', 'Normal (Gaussian)'),
        ('expon', 'Exponential'),
        ('uniform', 'Uniform'),
        ('gamma', 'Gamma'),
    ]

    distribution = forms.ChoiceField(
        label="Distribution Type",
        choices=DISTRIBUTION_CHOICES,
        initial='norm'
    )

    param1 = forms.FloatField(
        label="Parameter 1 (e.g., mean 'loc' for Normal, 'scale' for Exponential)",
        initial=0.0
    )
    param2 = forms.FloatField(
        label="Parameter 2 (e.g., std 'scale' for Normal, 'scale' for Uniform is b-a)",
        initial=1.0,
        required=False
    )

    sample_size = forms.IntegerField(
        label="Sample Size",
        min_value=10,
        initial=1000
    )

    def clean(self):
        cleaned_data = super().clean()
        dist_type = cleaned_data.get('distribution')
        p1 = cleaned_data.get('param1')
        p2 = cleaned_data.get('param2')

        errors = {}
        if dist_type == 'norm':
            if p2 is None or p2 <= 0:
                errors['param2'] = "Standard deviation (scale) must be positive for Normal distribution."
        elif dist_type == 'expon':
            # param1 -> loc, param2 -> scale
            if p2 is None or p2 <= 0:
                errors['param2'] = "Scale must be positive for Exponential distribution."
        elif dist_type == 'uniform':
            # param1 -> loc (a), param2 -> scale (b-a). Then b = loc + scale.
            if p2 is None or p2 <= 0:
                errors['param2'] = "Scale (b-a) must be positive for Uniform distribution."
        elif dist_type == 'gamma':
            # param1 -> a (shape), param2 -> scale
            if p1 is None or p1 <= 0:
                errors['param1'] = "Shape parameter 'a' must be positive for Gamma distribution."
            if p2 is None or p2 <= 0:
                errors['param2'] = "Scale parameter must be positive for Gamma distribution."

        if errors:
            raise forms.ValidationError(errors)
        return cleaned_data

    def get_scipy_distribution(self):
        cleaned_data = self.cleaned_data
        dist_type = cleaned_data['distribution']
        p1 = cleaned_data['param1']
        p2 = cleaned_data['param2']

        if dist_type == 'norm':
            return stats.norm(loc=p1, scale=p2)
        elif dist_type == 'expon':
            return stats.expon(loc=p1, scale=p2)
        elif dist_type == 'uniform':
            return stats.uniform(loc=p1, scale=p2)
        elif dist_type == 'gamma':
            return stats.gamma(a=p1, loc=0, scale=p2)
        else:
            raise ValueError(f"Unsupported distribution type: {dist_type}")


class Task2Form(forms.Form):
    values = forms.CharField(
        label="Values (comma-separated)",
        help_text="e.g., 1, 2, 3 or A, B, C",
        initial="1, 2, 3"
    )

    probabilities = forms.CharField(
        label="Probabilities (comma-separated)",
        help_text="e.g., 0.2, 0.5, 0.3 (must sum to 1.0)",
        initial="0.2, 0.5, 0.3"
    )

    sample_size = forms.IntegerField(
        label="Sample Size",
        min_value=10,
        initial=500
    )

    def clean_values(self):
        data = self.cleaned_data['values']
        try:
            values_list = [x.strip() for x in data.split(',')]
            converted_values = []
            for v in values_list:
                try:
                    converted_values.append(int(v))
                except ValueError:
                    try:
                        converted_values.append(float(v))
                    except ValueError:
                        converted_values.append(v)
            return converted_values
        except Exception:
            raise forms.ValidationError("Invalid format for values. Use comma-separated list.")

    def clean_probabilities(self):
        data = self.cleaned_data['probabilities']
        try:
            probs_list = [float(x.strip()) for x in data.split(',')]
            if not probs_list:
                raise forms.ValidationError("At least one probability is required.")
            return probs_list
        except ValueError:
            raise forms.ValidationError("Invalid format for probabilities. Use comma-separated numbers.")

    def clean(self):
        cleaned_data = super().clean()
        values = cleaned_data.get('values')
        probabilities = cleaned_data.get('probabilities')

        if values is not None and probabilities is not None:
            if len(values) != len(probabilities):
                raise forms.ValidationError("The number of values must match the number of probabilities.")

            total_prob = sum(probabilities)
            if abs(total_prob - 1.0) > 1e-6:
                raise forms.ValidationError(f"The sum of probabilities must be 1.0. Current sum is {total_prob:.6f}.")

        return cleaned_data

    def get_simulation_params(self):
        return self.cleaned_data['values'], self.cleaned_data['probabilities']
