import bisect
import random

from django.http import request, JsonResponse
from django.shortcuts import render, redirect
from .forms import QuoteForm
from .models import Quote


def random_quote(request):
    quote = get_weighted_random_quote()
    form = QuoteForm()
    liked = None

    if quote:
        quote.views += 1
        quote.save()

        cookie_key = f"quote_{quote.id}_vote"
        liked = request.COOKIES.get(cookie_key)

    return render(request, 'random.html', {
        'quote': quote,
        'form': form,
        'liked': liked
    })


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


def vote_quote(request):
    if request.method == 'POST':
        quote_id = request.POST.get('id')
        action = request.POST.get('action')

        try:
            quote = Quote.objects.get(id=quote_id)
        except Quote.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Цитата не найдена'})

        if action == 'like':
            quote.likes += 1
        elif action == 'dislike':
            quote.dislikes += 1

        quote.save()

    resp = JsonResponse({
        'success': True,
        'likes': quote.likes,
        'dislikes': quote.dislikes,
        'action': action
    })
    # resp.set_cookie(cookie_key, action, max_age=60 * 60 * 24 * 365)
    return resp
