# coding: utf-8

# django imports
from django import template
try:
    from django.utils.http import urlquote
except ImportError:
    from urllib.parse import quote as urlquote

# filebrowser imports
from filebrowser.settings import SELECT_FORMATS

register = template.Library()




@register.inclusion_tag('filebrowser/include/_response.html', takes_context=True)
def query_string(context, add=None, remove=None):
    """
    Allows the addition and removal of query string parameters.
    
    _response.html is just {{ response }}
    
    Usage:
    http://www.url.com/{% query_string "param_to_add=value, param_to_add=value" "param_to_remove, params_to_remove" %}
    http://www.url.com/{% query_string "" "filter" %}filter={{new_filter}}
    http://www.url.com/{% query_string "sort=value" "sort" %}
    """
    
    # Written as an inclusion tag to simplify getting the context.
    add = string_to_dict(add)
    remove = string_to_list(remove)
    params = context['query'].copy()
    response = get_query_string(params, add, remove)
    return {'response': response }


def query_helper(query, add=None, remove=None):
    """
    Helper Function for use within views.
    """
    
    add = string_to_dict(add)
    remove = string_to_list(remove)
    params = query.copy()
    return get_query_string(params, add, remove)


def get_query_string(p, new_params=None, remove=None):
    """
    Add and remove query parameters. From `django.contrib.admin`.
    @p:type dict
    """
    
    if new_params is None: new_params = {}
    if remove is None: remove = []
    for r in remove:
        if r in p:
            del p[r]

    for k, v in new_params.items():
        if k in p and v is None:
            del p[k]
        elif v is not None:
            p[k] = v
    return '?' + '&'.join([u'%s=%s' % (urlquote(k), urlquote(v)) for k, v in p.items()])


def string_to_dict(string):
    """
    Usage:
        {{ url|thumbnail:"width=10,height=20" }}
        {{ url|thumbnail:"width=10" }}
        {{ url|thumbnail:"height=20" }}
    """
    
    kwargs = {}
    if string:
        string = str(string)
        if ',' not in string:
            # ensure at least one ','
            string += ','
        for arg in string.split(','):
            arg = arg.strip()
            if arg == '': continue
            kw, val = arg.split('=', 1)
            kwargs[kw] = val
    return kwargs


def string_to_list(string):
    """
    Usage:
        {{ url|thumbnail:"width,height" }}
    """
    
    args = []
    if string:
        string = str(string)
        if ',' not in string:
            # ensure at least one ','
            string += ','
        for arg in string.split(','):
            arg = arg.strip()
            if arg == '': continue
            args.append(arg)
    return args


class SelectableNode(template.Node):
    def __init__(self, filetype, format):
        self.filetype = template.Variable(filetype)
        self.format = template.Variable(format)
    
    def render(self, context):
        try:
            filetype = self.filetype.resolve(context)
        except template.VariableDoesNotExist:
            filetype = ''
        try:
            format = self.format.resolve(context)
        except template.VariableDoesNotExist:
            format = ''
        if filetype and format and filetype in SELECT_FORMATS[format]:
            selectable = True
        elif filetype and format and filetype not in SELECT_FORMATS[format]:
            selectable = False
        else:
            selectable = True
        context['selectable'] = selectable
        return ''


def selectable(parser, token):
    
    try:
        tag, filetype, format = token.split_contents()
    except:
        raise template.TemplateSyntaxError("%s tag requires 2 arguments" % token.contents.split()[0])
        
    return SelectableNode(filetype, format)
    
register.tag(selectable)

@register.simple_tag
def custom_admin_media_prefix():
    import django
    if "1.4" in django.get_version():
        from django.conf import settings
        return "".join([settings.STATIC_URL,"admin/"])
    else:
        try:
            from django.contrib.admin.templatetags import admin_media_prefix
        except ImportError:
            from django.contrib.admin.templatetags.adminmedia import admin_media_prefix
        return admin_media_prefix()

