=====================
Wikilinks for Pelican
=====================

Support Wikilinks when generating Pelican sites.

``Wikilinks`` is a plugin for `Pelican <http://docs.getpelican.com/>`_,
a static site generator written in Python.

.. image:: https://img.shields.io/pypi/v/minchin.pelican.plugins.wikilinks.svg?style=flat
    :target: https://pypi.python.org/pypi/minchin.pelican.plugins.wikilinks
    :alt: PyPI version number

.. image:: https://img.shields.io/badge/-Changelog-success?style=flat
    :target: https://github.com/MinchinWeb/minchin.pelican.plugins.wikilinks/blob/master/CHANGELOG.rst
    :alt: Changelog

.. image:: https://img.shields.io/pypi/pyversions/minchin.pelican.plugins.wikilinks?style=flat
    :target: https://pypi.python.org/pypi/minchin.pelican.plugins.wikilinks/
    :alt: Supported Python version

.. image:: https://img.shields.io/pypi/l/minchin.pelican.plugins.wikilinks.svg?style=flat&color=green
    :target: https://github.com/MinchinWeb/minchin.pelican.plugins.wikilinks/blob/master/LICENSE.txt
    :alt: License

.. image:: https://img.shields.io/pypi/dm/minchin.pelican.plugins.wikilinks.svg?style=flat
    :target: https://pypi.python.org/pypi/minchin.pelican.plugins.wikilinks/
    :alt: Download Count


Installation
============

The easiest way to install ``Wikilinks`` is through the use of pip. This
will also install the required dependencies automatically.

.. code-block:: sh

  pip install minchin.pelican.plugins.wikilinks

Further configuration will depend on the version of Pelican you are running. On
version 4.5 or newer and you haven't defined ``PLUGINS`` in your
``pelicanconf.py``, nothing more in needed. On earlier versions of Pelican, or
if you've defined ``PLUGINS``, you'll need to add the autoloader to your list
of plugins in your ``pelicanconf.py`` file:

.. code-block:: python

  # pelicanconf.py

  PLUGINS = [
      # ...
      'minchin.pelican.plugins.wikilinks',
      # ...
  ]


Usage Notes
===========

In basic usage, this allow links of the form ``[[ my work ]]`` or
``[[ my work | is finished ]]``. Both of these will create a link to a file
named ``my work`` (e.g. ``my work.md``). By default, the name displayed for the
link will be the filename; alternately add a title to the link by using a bar
and anything after the bar will be used as the displayed name 
(e.g. ``| is finished``).

Known Issues
============

The plugin relies on each link target having a unique filename; non-unique
filenames may result in links not going where you were expecting.

Perhaps this should be added as token of a Markdown reader, but the link target
list is only available after all sources have been rendered. Because the plugin
is run after Markdown (or ReStructured) is rendered, there currently isn't a
way to make sure that this isn't run on links within code blocks, etc.

Future To Dos
=============

- support link anchors (e.g. ``my work#heading``)

Prior Art
=========

This plugin relies on much work that has gone before, both explicitly for code
and implicitely for the encouragement of this even being possible. This list is
sadly incomplete, but in particlar:

- Johnathan Sundqvist's `Obisidian Plugin for Pelican
  <https://github.com/jonathan-s/pelican-obsidian>`_ (and forks) -- in
  particular, for providing inspiration on how to deal with Wiki-style links
