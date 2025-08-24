# Nanodjango Compose

[![PyPI](https://img.shields.io/pypi/v/nanodjango-compose.svg)](https://pypi.org/project/nanodjango-compose/)

nanodjango-compose is a library of plugins that let you convert your
nanodjango app to a production-ready Django project with maximum flexibility, 
and a minimum of fuss. 

With [Cookiecutter](https://github.com/StuartMacKay/cookiecutter-django-site) 
projects and [repository templates](https://github.com/StuartMacKay/django-project-template)
you can quickly setup a production-ready Django site. However, these can only 
offer either a limited set of choices or predefined configurations. Since every
Django project is different, the minimum set of viable features is often not
sufficient and you then have add various chunks of boilerplate or config files.
Conversely add too many features and you then waste time removing all the 
features you don't need. 

nanodjango delivers rapid prototyping for Django projects. Once you have the 
features you want you can then convert your single page app to a full Django
project. nanodjango-compose takes this a step further. Using nanodjango's 
plugin system, you can control the conversion process to add all the features
you need for a production-ready site.

## Quickstart

Install nanodjango-compose:

```sh
pip install nanodjango-compose
```

Write your nanodjango app in single `.py` file, importing a plugin
for each feature you want to include in the full Django project when
it is converted.

```python
from nanodjango import Django

from compose import postgres, sentry

app = Django()

app.pm.register(postgres)
app.pm.register(sentry)

@app.route("/")
def hello_world(request):
    return "<p>Hello, World!</p>"
```

Save that as `hello_world.py`, then use nanodjango to run it:

```sh
nanodjango run hellow_world.py
```
This will create migrations and a database, and run your project in 
development mode. IMPORTANT: Although the plugins to configure the 
project with PostgreSQL and Sentry, these are only added when the 
project is converted. Right now nanodjango-compose does not change 
nanodjango's`run` command - so it will still initially create an 
SQLite database.

* See [Command usage](https://nanodjango.readthedocs.io/en/latest/usage.html)
  for more options

### Conversion

Once your project has the initial set of features you want, you can convert 
it into a full Django site:

```sh
nanodjango convert hello_world.py path/to/site
```
Now the plugins you included will be used to update Django's settings and 
add any configuration files.

* See
  [Converting to a full Django project](https://nanodjango.readthedocs.io/en/latest/convert.html)
  for more information

## Project Information

* Issues: https://github.com/StuartMacKay/nanodjango-compose/issues
* Repository: https://github.com/StuartMacKay/nanodjango-compose

## License

nanodjango-compose is available under the terms of the [MIT](https://opensource.org/licenses/MIT) licence.
