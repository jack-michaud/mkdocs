# coding: utf-8

from __future__ import unicode_literals
from datetime import datetime
import io
import logging
import os

from jinja2.exceptions import TemplateNotFound
import jinja2
import json

from mkdocs import nav, search, utils
from mkdocs.utils import filters
from mkdocs.relative_path_ext import RelativePathExtension
import mkdocs

log = logging.getLogger(__name__)


def convert_markdown(markdown_source, config, site_navigation=None):
    """
    Convert the Markdown source file to HTML as per the config and
    site_navigation. Return a tuple of the HTML as a string, the parsed table
    of contents, and a dictionary of any metadata that was specified in the
    Markdown file.
    """

    extensions = [
        RelativePathExtension(site_navigation, config['strict'])
    ] + config['markdown_extensions']

    return utils.convert_markdown(
        markdown_source=markdown_source,
        extensions=extensions,
        extension_configs=config['mdx_configs']
    )


def get_global_context(nav, config):
    """
    Given the SiteNavigation and config, generate the context which is relevant
    to app pages.
    """

    site_name = config['site_name']

    if config['site_favicon']:
        site_favicon = nav.url_context.make_relative('/' + config['site_favicon'])
    else:
        site_favicon = None

    page_description = config['site_description']

    extra_javascript = utils.create_media_urls(nav, config['extra_javascript'])

    extra_css = utils.create_media_urls(nav, config['extra_css'])

    return {
        'site_name': site_name,
        'site_author': config['site_author'],
        'favicon': site_favicon,
        'page_description': page_description,

        # Note that there's intentionally repetition here. Rather than simply
        # provide the config dictionary we instead pass everything explicitly.
        #
        # This helps ensure that we can throughly document the context that
        # gets passed to themes.
        'repo_url': config['repo_url'],
        'repo_name': config['repo_name'],
        'nav': nav,
        'base_url': nav.url_context.make_relative('/'),
        'homepage_url': nav.homepage.url,
        'site_url': config['site_url'],

        'extra_css': extra_css,
        'extra_javascript': extra_javascript,

        'include_nav': config['include_nav'],
        'include_next_prev': config['include_next_prev'],

        'copyright': config['copyright'],
        'google_analytics': config['google_analytics'],

        'mkdocs_version': mkdocs.__version__,
        'build_date_utc': datetime.utcnow(),

        'config': config
    }


def get_page_context(page, content, toc, meta, config):
    """
    Generate the page context by extending the global context and adding page
    specific variables.
    """
    if config['site_url']:
        page.set_canonical_url(config['site_url'])

    page.content = content
    page.toc = toc
    page.meta = meta

    # TODO: remove the rest in version 1.0 as they are deprecated

    if page.is_homepage or page.title is None:
        page_title = None
    else:
        page_title = page.title

    if page.is_homepage:
        page_description = config['site_description']
    else:
        page_description = None

    return {
        'page': page,
        # TODO: remove the rest in version 1.0 as they are deprecated
        'page_title': page_title,
        'page_description': page_description,

        'content': content,
        'toc': toc,
        'meta': meta,

        'canonical_url': page.canonical_url,

        'current_page': page,
        'previous_page': page.previous_page,
        'next_page': page.next_page
    }

def django_convert(content, config):
    from bs4 import BeautifulSoup
    content = "{%" + "load staticfiles" + "%}" + content
    soup = BeautifulSoup(content, 'html.parser')
    for tag in soup.find_all('script'):
        if tag.get('src') is not None:
            if tag['src'][0] == '.':
                tag['src'] = "{% " + "static '{}/{}'".format('docs',tag['src']) + " %}"
    for tag in soup.find_all('link'):
        if tag.get('href') is not None:
            if tag['href'][0] == '.':
                tag['href'] = "{% " + "static '{}/{}'".format('docs',tag['href']) + " %}"
    for tag in soup.find_all('img'):
        if tag.get('src') is not None:
            if tag['src'][0] == '.':
                tag['src'] = "{% " + "static '{}/{}'".format('docs',tag['src']) + " %}"

    # for tag in soup.find_all('a'):
    #     if tag.get('href') is not None:
    #         if tag['href'][0] == '.':
    #             tag['href'] = "{% " + "static '{}/{}'".format('docs',tag['href']) + " %}"

    converted_content = str(soup)
    return converted_content

def build_template(template_name, env, config, site_navigation=None):

    log.debug("Building template: %s", template_name)

    try:
        template = env.get_template(template_name)
    except TemplateNotFound:
        return False

    context = {'page': None}
    if site_navigation is not None:
        context.update(get_global_context(site_navigation, config))

    output_content = template.render(context)
    output_path = os.path.join(config['site_dir'], template_name)
    utils.write_file(output_content.encode('utf-8'), output_path)
    return True


def _build_page(page, config, site_navigation, env, dump_json):

    # Read the input file
    input_path = os.path.join(config['docs_dir'], page.input_path)

    try:
        input_content = io.open(input_path, 'r', encoding='utf-8').read()
    except IOError:
        log.error('file not found: %s', input_path)
        raise

    # Process the markdown text
    html_content, table_of_contents, meta = convert_markdown(
        markdown_source=input_content,
        config=config,
        site_navigation=site_navigation
    )

    context = get_global_context(site_navigation, config)
    context.update(get_page_context(
        page, html_content, table_of_contents, meta, config
    ))

    # Allow 'template:' override in md source files.
    if 'template' in meta:
        template = env.get_template(meta['template'][0])
    else:
        template = env.get_template('base.html')

    # Render the template.
    output_content = template.render(context)

    # Write the output file.
    output_path = os.path.join(config['site_dir'], page.output_path)
    if dump_json:
        json_context = {
            'content': context['content'],
            'title': context['current_page'].title,
            'url': context['current_page'].abs_url,
            'language': 'en',
        }
        json_output = json.dumps(json_context, indent=4).encode('utf-8')
        utils.write_file(json_output, output_path.replace('.html', '.json'))
    else:
        if config['dj_app_name'] is not None:
            content = django_convert(output_content.encode('utf-8'), config)
            utils.write_file(content, output_path)
        else:
            utils.write_file(output_content.encode('utf-8'), output_path)

    return html_content, table_of_contents, meta


def build_extra_templates(extra_templates, config, site_navigation=None):

    log.debug("Building extra_templates page")

    for extra_template in extra_templates:

        input_path = os.path.join(config['docs_dir'], extra_template)

        with io.open(input_path, 'r', encoding='utf-8') as template_file:
            template = jinja2.Template(template_file.read())

        context = {'page': None}
        if site_navigation is not None:
            context.update(get_global_context(site_navigation, config))

        output_content = template.render(context)
        output_path = os.path.join(config['site_dir'], extra_template)
        utils.write_file(output_content.encode('utf-8'), output_path)


def build_pages(config, dump_json=False):
    """
    Builds all the pages and writes them into the build directory.
    """
    site_navigation = nav.SiteNavigation(config['pages'], config['use_directory_urls'])
    loader = jinja2.FileSystemLoader(config['theme_dir'] + [config['mkdocs_templates'], ])
    env = jinja2.Environment(loader=loader)

    # TODO: remove DeprecationContext in v1.0 when all deprecated vars have been removed
    from jinja2.runtime import Context
    deprecated_vars = [
        'page_title',
        'content',
        'toc',
        'meta',
        'current_page',
        'canonical_url',
        'previous_page',
        'next_page'
    ]

    class DeprecationContext(Context):
        def resolve(self, key):
            """ Log a warning when acessing any deprecated variable name. """
            if key in deprecated_vars:
                replacement = "page" if key == 'current_page' else "page.{0}".format(key)
                log.warn(
                    "Template variable warning: '{0}' is being deprecated and will not be "
                    "available in a future version. Use '{1}' instead.".format(key, replacement)
                )
            return super(DeprecationContext, self).resolve(key)

    env.context_class = DeprecationContext
    # TODO: end remove DeprecationContext

    env.filters['tojson'] = filters.tojson
    search_index = search.SearchIndex()

    build_template('404.html', env, config, site_navigation)

    if not build_template('search.html', env, config, site_navigation):
        log.debug("Search is enabled but the theme doesn't contain a "
                  "search.html file. Assuming the theme implements search "
                  "within a modal.")

    build_template('sitemap.xml', env, config, site_navigation)

    build_extra_templates(config['extra_templates'], config, site_navigation)

    for page in site_navigation.walk_pages():

        try:
            log.debug("Building page %s", page.input_path)
            build_result = _build_page(page, config, site_navigation, env,
                                       dump_json)
            html_content, table_of_contents, _ = build_result
            search_index.add_entry_from_context(
                page, html_content, table_of_contents)
        except Exception:
            log.error("Error building page %s", page.input_path)
            raise

    search_index = search_index.generate_search_index()
    json_output_path = os.path.join(config['site_dir'], 'mkdocs', 'search_index.json')    
    utils.write_file(search_index.encode('utf-8'), json_output_path)


def build(config, live_server=False, dump_json=False, clean_site_dir=False):
    """
    Perform a full site build.
    """
    if clean_site_dir:
        log.info("Cleaning site directory")
        utils.clean_directory(config['site_dir'])
    if not live_server:
        log.info("Building documentation to directory: %s", config['site_dir'])
        if not clean_site_dir and site_directory_contains_stale_files(config['site_dir']):
            log.info("The directory contains stale files. Use --clean to remove them.")

    if dump_json:
        build_pages(config, dump_json=True)
        return

    # Reversed as we want to take the media files from the builtin theme
    # and then from the custom theme_dir so that the custom versions take
    # precedence.
    for theme_dir in reversed(config['theme_dir']):
        log.debug("Copying static assets from theme: %s", theme_dir)
        utils.copy_media_files(
            theme_dir, config['site_dir'], exclude=['*.py', '*.pyc', '*.html']
        )

    log.debug("Copying static assets from the docs dir.")
    utils.copy_media_files(config['docs_dir'], config['site_dir'])

    log.debug("Building markdown pages.")
    build_pages(config)


def site_directory_contains_stale_files(site_directory):
    """
    Check if the site directory contains stale files from a previous build.
    Right now the check returns true if the directory is not empty.
    A more sophisticated approach should be found to trigger only if there are
    files that won't be overwritten anyway.
    """
    if os.path.exists(site_directory):
        if os.listdir(site_directory):
            return True
    return False
