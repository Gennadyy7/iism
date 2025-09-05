from django.core.exceptions import ValidationError


def validate_non_empty_or_spaces(value):
    if not value.strip():
        raise ValidationError("The team name cannot be empty or contain only spaces.")
