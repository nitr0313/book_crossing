from django import forms

from .models import BookInstance


class BookInstanceForm(forms.ModelForm):
    class Meta:
        model = BookInstance
        fields = '__all__'

    def clean(self):
        cd = self.cleaned_data
        status = cd.get('status')
        loaner = cd.get('loaner')
        reserved_time = cd.get('reserved_time')
        if status == 'o' and loaner is None:
            raise forms.ValidationError('Выбран статус В аренде, при этом не указан Заёмщик')
        if status == 'r' and loaner is None:
            raise forms.ValidationError('Выбран статус Зарезервирована, при этом не указан Заёмщик')
        if status in ['m', 'a', 'x'] and loaner is not None:
            cd['loaner'] = None
            # raise forms.ValidationError('При данном статусе заемщика быть не должно!')
        return cd
