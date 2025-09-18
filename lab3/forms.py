from django import forms


class Task1Form(forms.Form):
    sample_size = forms.IntegerField(
        label="Sample Size",
        min_value=10,
        max_value=10000,
        initial=1000,
        help_text="Number of (x, y) pairs to generate."
    )

    confidence_level = forms.FloatField(
        label="Confidence Level",
        min_value=0.8,
        max_value=0.99,
        initial=0.95,
        required=False,
        help_text="For confidence intervals (e.g., 0.95 for 95%)."
    )

    include_3d = forms.BooleanField(
        label="Include 3D Histogram",
        required=False,
        initial=False,
        help_text="Check to generate a 3D visualization (⚠️ may take longer)."
    )

    def clean_confidence_level(self):
        cl = self.cleaned_data.get('confidence_level')
        return cl if cl is not None else 0.95


class Task2Form(forms.Form):
    distribution_matrix = forms.CharField(
        label="Distribution Matrix",
        widget=forms.Textarea(attrs={'rows': 6, 'cols': 40}),
        help_text="""
        Enter distribution matrix as rows: x, y, probability.
        Example:
        1,1,0.1
        1,2,0.2
        2,1,0.3
        2,2,0.4
        """,
        initial="1,1,0.1\n1,2,0.2\n2,1,0.3\n2,2,0.4"
    )

    sample_size = forms.IntegerField(
        label="Sample Size",
        min_value=10,
        max_value=10000,
        initial=500
    )

    confidence_level = forms.FloatField(
        label="Confidence Level",
        min_value=0.8,
        max_value=0.99,
        initial=0.95,
        required=False
    )

    include_3d = forms.BooleanField(
        label="Include 3D Histogram",
        required=False,
        initial=False,
        help_text="Check to generate a 3D visualization (⚠️ may take longer)."
    )

    def clean_distribution_matrix(self):
        data = self.cleaned_data['distribution_matrix']
        matrix = {}
        total_prob = 0.0
        lines = data.strip().splitlines()

        if not lines:
            raise forms.ValidationError("Matrix cannot be empty.")

        for i, line in enumerate(lines, 1):
            parts = line.split(',')
            if len(parts) != 3:
                raise forms.ValidationError(f"Line {i}: Expected 3 values (x, y, probability), got {len(parts)}.")

            try:
                x = float(parts[0].strip()) if '.' in parts[0] or 'e' in parts[0].lower() else int(parts[0].strip())
                y = float(parts[1].strip()) if '.' in parts[1] or 'e' in parts[1].lower() else int(parts[1].strip())
                prob = float(parts[2].strip())
            except ValueError as e:
                raise forms.ValidationError(f"Line {i}: Invalid number format. {e}")

            if prob < 0:
                raise forms.ValidationError(f"Line {i}: Probability cannot be negative.")

            key = (x, y)
            if key in matrix:
                raise forms.ValidationError(f"Line {i}: Duplicate key (x={x}, y={y}).")

            matrix[key] = prob
            total_prob += prob

        if abs(total_prob - 1.0) > 1e-6:
            raise forms.ValidationError(f"Sum of probabilities must be 1.0. Current sum is {total_prob:.6f}.")

        return matrix

    def clean_confidence_level(self):
        cl = self.cleaned_data.get('confidence_level')
        return cl if cl is not None else 0.95
