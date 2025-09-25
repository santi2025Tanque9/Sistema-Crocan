from django import forms

class AddToCartForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        label="Cantidad",
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )
    note = forms.CharField(
        required=False,
        label="Nota",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 2,
                "placeholder": "Ej: sin cebolla, extra queso..."
            }
        )
    )
    override_quantity = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.HiddenInput #lo vamos a usar únicamente en los formularios de actualización (en cart_detail.html).
    )