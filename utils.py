from datetime import datetime, date


def format_deadline(deadline_str):
    """Возвращает строку для дедлайна:
       - Сегодня, Завтра, Послезавтра для ближайших дат,
       - иначе полная дата в формате dd MMM yyyy."""
    if not deadline_str:
        return "No deadline"
    try:
        deadline_date = datetime.strptime(deadline_str, "%Y-%m-%d").date()
    except ValueError:
        return deadline_str

    today = date.today()
    delta = (deadline_date - today).days
    if delta < 0:
        return deadline_date.strftime("%d %b %Y")
    elif delta == 0:
        return "Сегодня"
    elif delta == 1:
        return "Завтра"
    elif delta == 2:
        return "Послезавтра"
    else:
        return deadline_date.strftime("%d %b %Y")
