.. include:: ../README.rst

.. _quickstart:

Quickstart
~~~~~~~~~~

1. Make sure you have ``uv`` `installed`__.

   __ https://docs.astral.sh/uv/getting-started/installation/

2. Install ``delineate`` as a tool::

      uv tool install -U delineate

3. Create a Linear API key:

   - Go to Linear's `API settings`__.

     __ https://linear.app/settings/account/security

   - Under `Personal API keys`, click `Create key`, give it a name, and copy the key.

4. Authenticate::

      delineate auth

   Paste your API key when prompted.

5. Export your data::

      delineate export --path ~/linear-backup

Your Linear data is now saved. You can later update your export with::

   delineate export --path ~/linear-backup --update

Full documentation is provided here:

.. toctree::
   :maxdepth: 2

   usage.rst
   changes.rst
   license.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
