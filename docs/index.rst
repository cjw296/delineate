.. include:: ../README.rst

.. _quickstart:

Quickstart
~~~~~~~~~~

1. Make sure you have ``uv`` `installed`__.

   __ https://docs.astral.sh/uv/getting-started/installation/

2. Install ``delineate`` as a tool:

   .. tabs::

      .. group-tab:: Linux/macOS

         .. code-block:: bash

            uv tool install -U delineate

      .. group-tab:: Windows (PowerShell)

         .. code-block:: powershell

            uv tool install -U delineate

3. Create a Linear API key:

   - Go to Linear's `API settings`__.

     __ https://linear.app/settings/api

   - Click `Create key`, give it a name, and copy the key.

4. Authenticate:

   .. tabs::

      .. group-tab:: Linux/macOS

         .. code-block:: bash

            delineate auth

      .. group-tab:: Windows (PowerShell)

         .. code-block:: powershell

            delineate auth

   Paste your API key when prompted.

5. Export your data:

   .. tabs::

      .. group-tab:: Linux/macOS

         .. code-block:: bash

            delineate export --path ~/linear-backup

      .. group-tab:: Windows (PowerShell)

         .. code-block:: powershell

            delineate export --path $HOME\linear-backup

Your Linear data is now saved. You can later update your export with:

.. tabs::

   .. group-tab:: Linux/macOS

      .. code-block:: bash

         delineate export --path ~/linear-backup --update

   .. group-tab:: Windows (PowerShell)

      .. code-block:: powershell

         delineate export --path $HOME\linear-backup --update

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
