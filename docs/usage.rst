Usage
=====

The best place to start is the :any:`quickstart`.

Available Commands
------------------

``delineate`` provides several commands:

* ``delineate auth`` - Authenticate with Linear
* ``delineate whoami`` - Show the authenticated user
* ``delineate export`` - Export data from Linear
* ``delineate version`` - Show the version

For help with any command, use:

.. tabs::

   .. group-tab:: Linux/macOS

      .. code-block:: bash

         delineate {COMMAND} --help

   .. group-tab:: Windows (PowerShell)

      .. code-block:: powershell

         delineate {COMMAND} --help

Export File Structure
---------------------

When you export data, delineate creates this folder structure:

.. code-block:: text

    export-folder/
    ├── latest.json              # Export tracking for incremental updates
    ├── issues/
    │   └── {prefix}/{uuid}.json
    ├── comments/
    │   └── {prefix}/{uuid}.json
    ├── projects/
    │   └── {prefix}/{uuid}.json
    ├── teams/
    │   └── {prefix}/{uuid}.json
    ├── users/
    │   └── {prefix}/{uuid}.json
    ├── initiatives/
    │   └── {prefix}/{uuid}.json
    ├── cycles/
    │   └── {prefix}/{uuid}.json
    ├── documents/
    │   └── {prefix}/{uuid}.json
    ├── workflow_states/
    │   └── {prefix}/{uuid}.json
    ├── issue_labels/
    │   └── {prefix}/{uuid}.json
    ├── attachments/
    │   └── {prefix}/{uuid}.json
    ├── project_milestones/
    │   └── {prefix}/{uuid}.json
    └── files/
        ├── manifest.jsonl       # URL to filename mapping
        └── {prefix}/{uuid}/
            └── {original_filename}

Entity files are organized into prefix directories using the first 4 characters
of the UUID to avoid filesystem issues with large numbers of files.

Basic Usage Examples
--------------------

**Export all data:**

.. tabs::

   .. group-tab:: Linux/macOS

      .. code-block:: bash

         delineate export --path ~/linear-backup

   .. group-tab:: Windows (PowerShell)

      .. code-block:: powershell

         delineate export --path $HOME\linear-backup

**Export specific entity types:**

.. tabs::

   .. group-tab:: Linux/macOS

      .. code-block:: bash

         delineate export --path ~/linear-backup issues comments

   .. group-tab:: Windows (PowerShell)

      .. code-block:: powershell

         delineate export --path $HOME\linear-backup issues comments

**Incremental update:**

After an initial export, use ``--update`` to only fetch entities that have
changed since the last export:

.. tabs::

   .. group-tab:: Linux/macOS

      .. code-block:: bash

         delineate export --path ~/linear-backup --update

   .. group-tab:: Windows (PowerShell)

      .. code-block:: powershell

         delineate export --path $HOME\linear-backup --update

This uses timestamps stored in ``latest.json`` to filter the API queries,
making subsequent exports much faster.

File Downloads
--------------

Delineate automatically downloads files referenced in issue descriptions,
comments, and other markdown content. These are stored in the ``files/``
directory with their original filenames, organized by UUID prefix.

The ``manifest.jsonl`` file maps original Linear URLs to local filenames,
enabling resumable downloads across export runs.
