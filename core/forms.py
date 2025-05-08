# core/forms.py
from django import forms
from .models import Concern, Bus

class ConcernForm(forms.ModelForm):
    # You might want to limit the buses shown based on user's role (e.g., only assigned bus for driver)
    # For simplicity, showing all buses here.
    bus = forms.ModelChoiceField(queryset=Bus.objects.all(), required=False, help_text="Optional: Select the bus related to your concern.")

    class Meta:
        model = Concern
        fields = ['bus', 'subject', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to form fields
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.widgets.TextInput) or \
                isinstance(field.widget, forms.widgets.Textarea) or \
                isinstance(field.widget, forms.widgets.Select):
                field.widget.attrs['class'] = 'form-control'
            if isinstance(field.widget, forms.widgets.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            if isinstance(field.widget, forms.widgets.ClearableFileInput):
                field.widget.attrs['class'] = 'form-control-file'