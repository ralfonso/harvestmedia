.. _quickstart:

Quick Start
===========

You should already have your Harvest Media API key before attempting to connect!

Here's the quick and dirty way to get your libraries and some albums::

    from harvestmedia.api.client import Client
    from harvestmedia.api.library import Library
    client = Client(api_key)

    # static methods need a client instance passed to them
    # the convention for this is _client
    libraries = Library.query.get_libraries(_client=client)
    for library in libraries:
        library_albums = library.get_albums()

More in the :ref:`api` docs!
