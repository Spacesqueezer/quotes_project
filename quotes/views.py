import bisect
import random
from django.shortcuts import render, redirect
from .forms import QuoteForm
from .models import Quote


def random_quote(request):
    quote = get_weighted_random_quote()
    if not quote:
        return render(request, 'random.html', {'quote': None})

    # увеличиваем счетчик просмотров
    quote.views += 1
    quote.save()

    # передаём цитату в шаблон
    return render(request, 'random.html', {'quote': quote})


def get_weighted_random_quote():
    quotes = list(Quote.objects.all())
    if not quotes:
        return None
    weights = [q.weight for q in quotes]
    cumulative_weights = []
    total = 0
    for w in weights:
        total += w
        cumulative_weights.append(total)
    r = random.randint(1, total)
    index = bisect.bisect_left(cumulative_weights, r)
    return quotes[index]


def normalize_text(text):
    return ''.join(text.lower().split())


def add_quote(request):
    form = QuoteForm(request.POST or None)
    error = ''
    if request.method == 'POST' and form.is_valid():
        normalized_new = normalize_text(form.cleaned_data['text'])
        existing = Quote.objects.all()
        for q in existing:
            if normalize_text(q.text) == normalized_new:
                error = 'Похожая цитата уже существует.'
                break
        else:
            source = form.cleaned_data['source']
            if Quote.objects.filter(source=source).count() >= 3:
                error = 'У этого источника уже 3 цитаты.'
            else:
                form.save()
                return redirect('random_quote')
    return render(request, 'add.html', {'form': form, 'error': error})
