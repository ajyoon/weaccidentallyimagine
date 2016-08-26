# we accidentally imagine
*a book of mutable poetry*

This is the complete source code for the website
[weaccidentallyimagine.com](http://weaccidentallyimagine.com).
When readers visit the site, stochastic processes render a unique version
of its 32 poems and deliver them in a single-page website. Users are able
to get permalinks to versions of the book using a random seed that can be
stored in a URL. CSS media queries are used to automatically optimize
the layout and design for printing so that users are free to easily print
the book directly from their browsers.

The code in this repository is configured to run locally using the Django
development server -- only trivial deployment-related differences exist
between the code here and that running live on the website.

## Set up

Running this site locally requires [Python](https://www.python.org/),
[Django](https://www.djangoproject.com/),
and [blur](https://github.com/ajyoon/blur).
While this has only been tested extensively in Python 3.5, it should work
just as well on earlier versions of Python with little to no modification.

Start by cloning this repository to your local machine either using git
or downloading and unpacking a zip of the repository.

If you have Python installed, you can set up the other dependencies
automatically using pip from your system's command line:

    $ cd /path/to/weaccidentallyimagine
    $ pip install -r requirements.txt

Once the dependencies are installed, running the server locally is as
easy as:

    $ cd /path/to/weaccidentallyimagine/weaccidentallyimagine
    $ python manage.py runserver

If all goes correctly, you will see a notification that the development
server has started (likely at port 8000). You can now go to your browser
and view the site at `localhost:8000` (or whatever port the terminal
message indicates)

## Project Overview
```
weaccidentallyimagine/
├── main
│   ├── apps.py
│   ├── engine
│   │   ├── html_utils.py
│   │   ├── __poems_data_builder.py
│   │   ├── __poems_original.py
│   │   ├── poems.py
│   │   ├── soft_poem.py
│   │   └── texts
│   │       └── ...txt
│   ├── static
│   │   └── main
│   │       └── css
│   │           └── main.css
│   ├── templates
│   │   └── main
│   │       └── poem_page.html
│   └── views.py
├── manage.py
├── settings.py
├── urls.py
└── wsgi.py
```
The `weaccidentallyimagine` folder mostly consists of Django boilerplate.
Of note, `urls.py` handles routing both to the main page as well as
the main page with fixed random seeds baked into the URL, acting as a sort
of permalink to a specific version of the book.

Inside `main/` we find a little more boilerplate in `apps.py`, followed by
the real content. `views.py` holds the main request handler for the
site, passing a random seed (or a fixed one if present in the URL) to
the global pseudorandom state of the standard Python `random` module.
(Since `blur` exclusively uses the standard `random` module for its random
number generation, this is enough to guarantee reproducible outcome if a
fixed seed is passed.) The HTML template is then loaded, and the collection
of poem objects is initialized and randomly ordered. The template is then
rendered with the initialized contents and passed to an `HttpResponse`.

The `main/templates/` directory contains just one template, `poem_page.html`,
which facilitates spinning the poems together into a single large page, as
well as containing an info modal and some light javascript to handle it and
force correct browser handling of links.

`main/static/` contains again just one file, `main.css`, which holds
all of the CSS for the site, including media queries for responsive layouts
and optimized printing.

`main/engine/` holds the meat of the poems.
`main/engine/texts/` holds all of the source texts for the 32 poems.
These texts are sometimes used to generate Markov models which drive the text
generation for each poem, and sometimes they appear verbatim in the output.

`main/engine/html_utils.py` contains utilities for manipulating special
markups in the source texts used when rendering the poems to HTML.

`main/engine/poems.py` holds configuration data for each poem which defines
the persistent stochastic behavior of each poem. Much of the data
in the list of poems here was actually generated with the
`__poems_data_builder.py` script, which takes basic classes of poems outlined
in `__poems_original.py` and randomly applies certain parameters to dictate
persistent behavior in each poem. Try running
`$ python __poems_data_builder.py` to make a whole new set of behaviors
for the book!

`engine/soft_poem.py` contains the `SoftPoem` class, which is an elaborate
subclass of the `SoftObject` class from the `blur` package. Instances of this
class represent the poems in the book and contains several parameters
which determine the poem's stochastic behavior.
The `SoftPoem.get()` method spins the poem together, processes specialized
markups in the source texts, and renders the poem as HTML ready to be plugged
into the master template by the main view.
