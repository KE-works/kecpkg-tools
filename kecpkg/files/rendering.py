import os

from jinja2 import Environment, FileSystemLoader

from kecpkg.utils import create_file

__environment = None


def get_environment():
    """Retrieve the jinja 2 environment as this is a singleton."""
    global __environment
    if not __environment:
        __environment = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))
    return __environment


def get_template(template):
    """
    From the rendering environment, retrieve the template.

    :param template: template name
    :return: Template
    """
    return get_environment().get_template(template)


def render_to_template(template, content):
    """
    Render content (dict) to the template.

    :param template: name of the jinja2 template file
    :param content: dictionary with content to render
    :return: rendered template (as string)
    """
    return get_template(template).render(content)


def render_to_file(filename, content, target_dir=None, template=None):
    """
    Render content to a template file in a target_dir.

    :param filename: filename (basename) to render to
    :param content: dictionary to render in the template
    :param target_dir: (optional) subdirectory or fullpath where to create the file
    :param template: (optional) template name (if not provided will be `<filename>.template`
    :return: None
    """
    # alias for render_to_template
    template = template or '{}.template'.format(filename)
    target_dir = target_dir or os.getcwd()
    filepath = os.path.join(target_dir, filename)

    filecontents = render_to_template(template=template, content=content)
    create_file(filepath=filepath, content=filecontents)
