import logging
from functools import wraps
from django.shortcuts import render
import re


def handle_lab_exceptions(func):
    @wraps(func)
    def wrapper(view_instance, request, *args, **kwargs):
        view_class_name = view_instance.__class__.__name__
        lab_number = "unknown"
        try:
            match = re.search(r'Lab(\d+)', view_class_name)
            if match:
                lab_number = match.group(1)
        except (AttributeError, TypeError, re.error):
            lab_number = "unknown"

        try:
            return func(view_instance, request, *args, **kwargs)
        except ValueError as e:
            error_message = f"Lab {lab_number}: {str(e)}"
        except Exception as e:
            logging.error(f"Lab {lab_number} error: {str(e)}", exc_info=True)
            error_message = f"Lab {lab_number}: An unexpected error occurred. Please check your input and try again."

        context = view_instance.get_context_data()
        context[f'lab_error'] = error_message
        return render(request, view_instance.template_name, context)
    return wrapper
