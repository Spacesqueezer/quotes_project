from django import forms
from .models import Quote


class QuoteForm(forms.ModelForm):
    class Meta:
        # Указываем, что форма связана с моделью Quote
        model = Quote

        # Перечисляем поля модели, которые хотим использовать в форме
        fields = ['text', 'source', 'weight']

        # Устанавливаем подписи для полей формы
        labels = {
            'text': 'Текст цитаты',
            'source': 'Источник',
            'weight': 'Вес цитаты'
        }
