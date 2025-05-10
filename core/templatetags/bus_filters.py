from django import template

register = template.Library()

@register.filter(name='bus_status_color')
def bus_status_color(status):
    """
    Returns Bootstrap color class based on bus status
    """
    status_colors = {
        'active': 'success',
        'in_maintenance': 'warning',
        'out_of_commission': 'danger',
        'delayed': 'info',
        'inactive': 'secondary'
    }
    return status_colors.get(status.lower(), 'primary')

@register.filter(name='route_status_color')
def route_status_color(status):
    """
    Returns color for route based on bus status
    """
    status_colors = {
        'active': '#28a745',
        'in_maintenance': '#ffc107',
        'out_of_commission': '#dc3545',
        'delayed': '#17a2b8',
        'inactive': '#6c757d'
    }
    return status_colors.get(status.lower(), '#007bff')

@register.filter(name='format_timestamp')
def format_timestamp(timestamp):
    """
    Formats timestamp for display
    """
    if not timestamp:
        return "Never updated"
    from django.utils.dateformat import format
    return format(timestamp, "H:i:s")

@register.filter(name='concern_status_color')
def concern_status_color(status):
    status_colors = {
        'open': 'danger',
        'in_progress': 'warning',
        'closed': 'success'
    }
    return status_colors.get(status.lower(), 'secondary')

@register.filter(name='school_status_color')
def school_status_color(is_active):
    return 'success' if is_active else 'secondary'