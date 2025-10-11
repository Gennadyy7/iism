from django import forms


class PriorityQueueForm(forms.Form):
    queue_length = forms.IntegerField(
        label="Queue length (R)",
        min_value=0,
        initial=2,
        help_text="Number of places in the queue (excluding the service channel)."
    )
    lambda1 = forms.FloatField(
        label="λ₁ (Arrival rate of Type I)",
        min_value=0.0001,
        initial=1.0,
        help_text="Arrival rate for high-priority requests."
    )
    lambda2 = forms.FloatField(
        label="λ₂ (Arrival rate of Type II)",
        min_value=0.0001,
        initial=1.0,
        help_text="Arrival rate for low-priority requests."
    )
    mu1 = forms.FloatField(
        label="μ₁ (Service rate for Type I)",
        min_value=0.0001,
        initial=2.0,
        help_text="Service rate for high-priority requests."
    )
    mu2 = forms.FloatField(
        label="μ₂ (Service rate for Type II)",
        min_value=0.0001,
        initial=1.5,
        help_text="Service rate for low-priority requests."
    )
