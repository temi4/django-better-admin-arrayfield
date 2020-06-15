from django import forms


class DynamicArrayWidget(forms.TextInput):

    template_name = "django_better_admin_arrayfield/forms/widgets/dynamic_array.html"
    
    delimiter = ','

    @property
    def media(self):
        js = (
            "js/min/django_better_admin_arrayfield.min.js",
        )
        css = {"all": (
            "css/min/django_better_admin_arrayfield.min.css",
        )}

        return forms.Media(js=js, css=css)

    def get_context(self, name, value, attrs):
        context_value = value or [""]
        context = super().get_context(name, context_value, attrs)
        final_attrs = context["widget"]["attrs"]
        id_ = context["widget"]["attrs"].get("id")
        context["widget"]["is_none"] = value is None

        subwidgets = []
        for index, item in enumerate(context["widget"]["value"]):
            widget_attrs = final_attrs.copy()
            if id_:
                widget_attrs["id"] = "{id_}_{index}".format(id_=id_, index=index)
            widget = forms.TextInput()
            widget.is_required = self.is_required
            subwidgets.append(widget.get_context(name, item, widget_attrs)["widget"])

        context["widget"]["subwidgets"] = subwidgets
        context["widget"]["null_widget"] = forms.HiddenInput().get_context(name, '', final_attrs.copy())["widget"]
        return context

    def value_from_datadict(self, data, files, name):
        try:
            getter = data.getlist
            return [value for value in getter(name) if value]
        except AttributeError:
            return data.get(name)

    def format_value(self, value):
        pre_comma = 0
        values = []
        if value:
            for comma_index in re.finditer(self.delimiter, value):
                comma_index = comma_index.start()
                if value[comma_index:comma_index + 2] != f'{self.delimiter} ':
                    values.append(value[pre_comma:comma_index])
                    pre_comma = comma_index + 1

            values.append(value[pre_comma:len(value)])
        return values
