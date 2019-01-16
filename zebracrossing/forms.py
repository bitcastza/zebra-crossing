from django import forms

class CalendarWidget(forms.DateInput):
    def __init__(self, attrs=None, format=None):
        default_attrs = {
            'class': 'date-input',
            'width': 276
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

    class Media:
        css = {
            'screen': ('vendor/gijgo/css/gijgo.min.css',)
        }
        js = ( 'vendor/gijgo/js/gijgo.min.js',
              'js/use_datetimepicker.js',)

class FileWidget(forms.FileInput):
    def __init__(self, attrs=None, format=None):
        default_attrs = {
            'class': 'custom-file',
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

    class Media:
        js = ( 'vendor/bs-custom-file-input/bs-custom-file-input.min.js',
              'js/use_bs_file_input.js',)

