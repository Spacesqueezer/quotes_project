import bisect
import random
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .forms import QuoteForm
from .models import Quote


# Отображает случайную цитату на главной странице
def random_quote(request):
    # Получаем случайную цитату с учётом её веса
    quote = get_weighted_random_quote()

    if quote:
        # Увеличиваем счётчик просмотров
        quote.views += 1
        quote.save()

        # Проверяем, голосовал ли пользователь за эту цитату
        liked = request.COOKIES.get(f"quote_{quote.id}_vote")
    else:
        # Если цитаты нет — ничего не выбрано
        liked = None

    # Показываем шаблон с цитатой и формой
    return render(request, 'random.html', {
        'quote': quote,
        'form': QuoteForm(),
        'liked': liked
    })


# Выбирает случайную цитату с учётом "веса"
def get_weighted_random_quote():
    # Загружаем все цитаты
    quotes = Quote.objects.all()

    if not quotes:
        # Если их нет — возвращаем None
        return None

    # Создаём список весов
    weights = [q.weight for q in quotes]

    # Подсчитываем накопленные веса
    cumulative_weights = []
    total = 0
    for i in range(len(weights)):
        total += weights[i]
        cumulative_weights.append(total)

    # Генерируем случайное число от 1 до общего веса
    r = random.randint(1, cumulative_weights[-1])

    # Определяем индекс, подходящий под это число
    index = bisect.bisect_left(cumulative_weights, r)

    # Возвращаем нужную цитату
    return quotes[index]


# Приводит текст к простой форме для сравнения
def normalize_text(text):
    # Удаляем пробелы и делаем все буквы маленькими
    return ''.join(text.lower().split())


# Обрабатывает добавление новой цитаты через форму
def add_quote(request):
    # Создаём экземпляр формы, передаём туда POST-данные
    form = QuoteForm(request.POST or None)

    if form.is_valid():
        # Подготавливаем текст новой цитаты
        normalized_new = normalize_text(form.cleaned_data['text'])

        # Загружаем все существующие цитаты
        existing_quotes = Quote.objects.all()

        # Проверяем, есть ли уже такая (похожая) цитата
        for quote in existing_quotes:
            normalized_existing = normalize_text(quote.text)
            if normalized_existing == normalized_new:
                # Если нашли дубликат — выводим ошибку
                return render(request, 'add.html', {
                    'form': form,
                    'error': 'Похожая цитата уже существует.'
                })

        # Проверяем, не превышен ли лимит в 3 цитаты от одного источника
        source = form.cleaned_data['source']
        if Quote.objects.filter(source=source).count() >= 3:
            return render(request, 'add.html', {
                'form': form,
                'error': 'У этого источника уже 3 цитаты.'
            })

        # Сохраняем цитату
        form.save()

        # Перенаправляем на главную
        return redirect('random_quote')

    # Если форма невалидна — возвращаем её с ошибками
    return render(request, 'add.html', {'form': form})


# Обрабатывает лайки и дизлайки
def vote_quote(request):
    # Проверяем, что запрос POST
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

    # Получаем ID цитаты и действие (лайк или дизлайк)
    quote_id = request.POST.get('id')
    action = request.POST.get('action')

    try:
        # Пытаемся получить нужную цитату
        quote = Quote.objects.get(id=quote_id)
    except Quote.DoesNotExist:
        # Цитата не найдена — ошибка
        return JsonResponse({'success': False, 'error': 'Цитата не найдена'})

    # Получаем предыдущий голос пользователя из куки
    cookie_key = f"quote_{quote.id}_vote"
    previous = request.COOKIES.get(cookie_key)

    # Убираем старый голос
    if previous == 'like':
        quote.likes -= 1
    elif previous == 'dislike':
        quote.dislikes -= 1

    # Добавляем новый голос
    if action == 'like':
        quote.likes += 1
    elif action == 'dislike':
        quote.dislikes += 1

    # Сохраняем изменения
    quote.save()

    # Формируем JSON-ответ
    resp = JsonResponse({
        'success': True,
        'likes': quote.likes,
        'dislikes': quote.dislikes,
        'action': action
    })

    # Сохраняем новое действие в куки
    resp.set_cookie(cookie_key, action, max_age=31536000)
    return resp


# Показывает топ-10 цитат по просмотрам
def top_ten(request):
    quotes = Quote.objects.order_by('-views')[:10]
    return render(request, 'top_ten.html', {'quotes': quotes})


# Показывает топ-10 по просмотрам или весу (выбирается через GET-параметр)
def top_quotes(request):
    sort_by = request.GET.get('sort_by', 'views')
    print("Сортировка по ", request.GET.get('sort_by'))

    if sort_by == 'views':
        quotes = Quote.objects.all().order_by('-views')[:10]
    else:
        quotes = Quote.objects.all().order_by('-weight')[:10]

    return render(request, 'quotes/top_ten.html', {
        'quotes': quotes,
        'sort_by': sort_by
    })
