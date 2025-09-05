from django import forms


class Task1Form(forms.Form):
    probability = forms.FloatField(
        label="Probability P(A)",
        min_value=0,
        max_value=1,
        initial=0.5
    )


class Task2Form(forms.Form):
    probabilities = forms.CharField(
        label="Probabilities (comma-separated)",
        help_text="e.g., 0.3, 0.7",
        initial="0.3, 0.7"
    )


class Task3Form(forms.Form):
    p_a = forms.FloatField(
        label="P(A)",
        min_value=0,
        max_value=1,
        initial=0.6
    )
    p_b_given_a = forms.FloatField(
        label="P(B|A)",
        min_value=0,
        max_value=1,
        initial=0.4
    )


class Task4Form(forms.Form):
    probabilities = forms.CharField(
        label="Probabilities (comma-separated)",
        help_text="e.g., 0.2, 0.3, 0.5",
        initial="0.2, 0.3, 0.5"
    )
