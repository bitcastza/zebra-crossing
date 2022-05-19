from django import forms

class CalendarWidget(forms.DateInput):
    def __init__(self, attrs=None, format=None):
        default_attrs = {
            'type': 'date',
            'width': 276
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)
