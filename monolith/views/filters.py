import flask 

filters = flask.Blueprint('filters', __name__)

@filters.app_template_filter()
def datetime_format(value, format="%d/%m/%Y"):
    """
        filter used to properly format date of birth in html templates
    """
    return value.strftime(format)

@filters.app_template_filter()
def delivery_datetime_format(value, format="%H:%M %d/%m/%Y"):
    """
        filter used to properly format delivery date in html templates
    """
    return value.strftime(format) if value != None else ""

filters.add_app_template_filter(datetime_format)
filters.add_app_template_filter(delivery_datetime_format)
