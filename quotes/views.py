import bisect
import random
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .forms import QuoteForm
from .models import Quote


# Функция для получения случайной цитаты
def random_quote(request):
    # Получаем случайную цитату с учетом веса
    quote = get_weighted_random_quote()

    if quote:
        # Увеличиваем количество просмотров цитаты
        quote.views += 1
        quote.save()

        # Проверяем, есть ли у пользователя голос за эту цитату
        liked = request.COOKIES.get(f"quote_{quote.id}_vote")
    else:
        liked = None

    # Возвращаем страницу с цитатой
    return render(request, 'random.html', {
        'quote': quote,
        'form': QuoteForm(),
        'liked': liked
    })


# Функция для получения случайной цитаты с учетом веса
def get_weighted_random_quote():
    # Получаем все цитаты из базы данных
    quotes = Quote.objects.all()

    if not quotes:
        # Если цитат нет, возвращаем None
        return None

    # Создаем список весов цитат
    weights = [q.weight for q in quotes]

    # Создаем список накопленных весов
    cumulative_weights = []
    total = 0
    for i in range(len(weights)):
        total += weights[i]  # добавляем текущий вес к сумме
        cumulative_weights.append(total)  # добавляем накопленную сумму в список

    # Генерируем случайное число от 1 до максимального накопленного веса
    r = random.randint(1, cumulative_weights[-1])

    # Находим индекс цитаты, соответствующий случайному числу
    index = bisect.bisect_left(cumulative_weights, r)

    # Возвращаем цитату с найденным индексом
    return quotes[index]


# Функция для нормализации текста
def normalize_text(text):
    # Удаляем пробелы и приводим текст к нижнему регистру
    return ''.join(text.lower().split())


# Функция для добавления новой цитаты
def add_quote(request):
    # Создаем форму для добавления цитаты
    form = QuoteForm(request.POST or None)

    if form.is_valid():
        # Нормализуем текст цитаты
        normalized_new = normalize_text(form.cleaned_data['text'])

        # Проверяем, есть ли уже такая цитата в базе данных
        if Quote.objects.filter(text__iexact=normalized_new).exists():
            # Если цитата уже существует, возвращаем ошибку
            return render(request, 'add.html', {'form': form, 'error': 'Похожая цитата уже существует.'})
        # Проверяем, есть ли у источника уже 3 цитаты
        source = form.cleaned_data['source']
        if Quote.objects.filter(source=source).count() >= 3:
            # Если у источника уже 3 цитаты, возвращаем ошибку
            return render(request, 'add.html', {'form': form, 'error': 'У этого источника уже 3 цитаты.'})
        # Сохраняем новую цитату
        form.save()
        # Перенаправляем пользователя на страницу случайной цитаты
        return redirect('random_quote')
    # Если форма не валидна, возвращаем страницу с формой
    return render(request, 'add.html', {'form': form})


# Функция для голосования за цитату
def vote_quote(request):
    # Проверяем, является ли запрос POST-запросом
    if request.method != 'POST':
        # Если запрос не POST, возвращаем ошибку
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    # Получаем идентификатор цитаты и действие (лайк или дизлайк)
    quote_id = request.POST.get('id')
    action = request.POST.get('action')
    try:
        # Получаем цитату из базы данных
        quote = Quote.objects.get(id=quote_id)
    except Quote.DoesNotExist:
        # Если цитаты нет, возвращаем ошибку
        return JsonResponse({'success': False, 'error': 'Цитата не найдена'})
    # Получаем ключ куки для голосования
    cookie_key = f"quote_{quote.id}_vote"
    # Получаем предыдущий голос пользователя
    previous = request.COOKIES.get(cookie_key)
    # Обновляем количество лайков и дизлайков
    if previous == 'like':
        quote.likes -= 1
    elif previous == 'dislike':
        quote.dislikes -= 1
    if action == 'like':
        quote.likes += 1
    elif action == 'dislike':
        quote.dislikes += 1
    # Сохраняем изменения в базе данных
    quote.save()
    # Возвращаем ответ с обновленными данными
    resp = JsonResponse({
        'success': True,
        'likes': quote.likes,
        'dislikes': quote.dislikes,
        'action': action
    })
    # Устанавливаем куки для голосования
    resp.set_cookie(cookie_key, action, max_age=31536000)
    return resp
