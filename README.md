# MkDocs

Project documentation with Markdown.

#### To download and install, use the method detailed [here](http://www.mkdocs.org/about/contributing/#installing-for-development). Remember to clone this repo!
You can use my version the same way you can the original mkdocs...
The difference is you can specify your Django app name in the mkdocs.yml as such:
```yaml
site_name: Foobar
pages: 
- Home: index.md
- About: about.md
theme: readthedocs
dj_app_name: my_django_app_name <--

```

All static file references in img, link, and script tags are turned to Django {% static '...' %} tags and {% load staticfiles %} is inserted at the beginning of the file. 

Here's an example of how you can use this mkdocs in Django.

```bash

django-admin startproject testproj && cd testproj
python manage.py startapp docs && cd docs
mkdir static && cd static    
mkdir docs 

# Here's our folder structure:
#    ├── docs
#    │   ├── __init__.py
#    │   ├── admin.py
#    │   ├── apps.py
#    │   ├── migrations
#    │   │   └── __init__.py
#    │   ├── models.py
#    │   ├── static         #/static/ is where staticfiles are found by default (see testproj/settings.py)
#    │   │   └── docs
#    │   ├── tests.py
#    │   └── views.py
#    ├── manage.py
#    └── testproj
#        ├── __init__.py
#        ├── __init__.pyc
#        ├── settings.py
#        ├── settings.pyc
#        ├── urls.py
#        └── wsgi.py

cd ..
mkdir templates && cd templates
mkdir docs



```

Generate your mkdocs (see [MkDocs documentation][mkdocs])...
Drag all the HTML files into the /templates/docs folder and the css, fonts, js, and img folders into the /static/docs folder.

```

docs 
├── static
│   └── docs
│       ├── css
│       │   ├── highlight.css
│       │   ├── theme.css
│       │   └── theme_extra.css
│       ├── fonts
│       │   ├── fontawesome-webfont.eot
│       │   ├── fontawesome-webfont.svg
│       │   ├── fontawesome-webfont.ttf
│       │   └── fontawesome-webfont.woff
│       ├── img
│       │   └── favicon.ico
│       └── js
│           ├── highlight.pack.js
│           ├── jquery-2.1.1.min.js
│           ├── modernizr-2.8.3.min.js
│           └── theme.js
└── templates
    └── docs
        └── index.html

```

Set up the views, urls, and apps as per usual; see the [Django documentation](https://docs.djangoproject.com/en/1.9/intro/). 
Remember, you have to set up a view for each HTML file you drag in from the generated site from mkdocs.

```python

#### /docs/views.py

from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'docs/index.html', {})

#### /testproj/urls.py

from django.conf.urls import url
from django.contrib import admin
import docs.views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', docs.views.index),
]

```


---

[![PyPI Downloads][pypi-dl-image]][pypi-dl-link]
[![PyPI Version][pypi-v-image]][pypi-v-link]
[![Build Status][travis-image]][travis-link]
[![Windows Build Status][appveyor-image]][appveyor-link]
[![Coverage Status][codecov-image]][codecov-link]
[![Landscale Code Health][landscape-image]][landscape-link]

- View the [MkDocs documentation][mkdocs].
- Project [release notes][release-notes].
- Visit the [MkDocs wiki](https://github.com/mkdocs/mkdocs/wiki) for community
  resources, including third party themes and a list of MkDocs users.
- IRC channel: `#mkdocs` on freenode.
- Discussions and support: <https://groups.google.com/forum/#!forum/mkdocs>

[appveyor-image]: https://img.shields.io/appveyor/ci/d0ugal/mkdocs/master.png
[appveyor-link]: https://ci.appveyor.com/project/d0ugal/mkdocs
[codecov-image]: http://codecov.io/github/mkdocs/mkdocs/coverage.svg?branch=master
[codecov-link]: http://codecov.io/github/mkdocs/mkdocs?branch=master
[landscape-image]: https://landscape.io/github/mkdocs/mkdocs/master/landscape.svg?style=flat-square
[landscape-link]: https://landscape.io/github/mkdocs/mkdocs/master
[pypi-dl-image]: https://img.shields.io/pypi/dm/mkdocs.png
[pypi-dl-link]: https://pypi.python.org/pypi/mkdocs
[pypi-v-image]: https://img.shields.io/pypi/v/mkdocs.png
[pypi-v-link]: https://pypi.python.org/pypi/mkdocs
[travis-image]: https://img.shields.io/travis/mkdocs/mkdocs/master.png
[travis-link]: https://travis-ci.org/mkdocs/mkdocs

[mkdocs]: http://www.mkdocs.org
[release-notes]: http://www.mkdocs.org/about/release-notes/
