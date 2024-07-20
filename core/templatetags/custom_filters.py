from django import template

register = template.Library()

@register.filter
def format_duration(duration):
    if duration is None:
        return "Duration not available"
    
    total_seconds = int(duration.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    
    if hours > 0 and minutes > 0:
        return f"{hours} {'hour' if hours == 1 else 'hours'} {minutes} {'minute' if minutes == 1 else 'minutes'}"
    elif hours > 0:
        return f"{hours} {'hour' if hours == 1 else 'hours'}"
    elif minutes > 0:
        return f"{minutes} {'minute' if minutes == 1 else 'minutes'}"
    else:
        return "0 minutes"
    
@register.filter(name='stars_for_rating')
def stars_for_rating(rating):
    full_stars = int(rating)
    half_star = rating - full_stars >= 0.5
    empty_stars = 5 - full_stars - (1 if half_star else 0)
    
    html = ''
    for i in range(full_stars):
        html += '<i class="fa fa-star"></i>'
    if half_star:
        html += '<i class="fa fa-star-half-o"></i>'
    for i in range(empty_stars):
        html += '<i class="fa fa-star-o"></i>'
    
    return html
