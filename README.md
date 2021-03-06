# Synopsis

A caching RSS/Atom proxy server with basic clustering support written in Python. Other data sources can be implemented.

The sources are hosted on [GitHub](https://github.com/rinusser/FeedTrough).

This is a work in progress, upcoming changes are outlined in the repository's [issues](https://github.com/rinusser/FeedTrough/issues).


# General

RSS/Atom feeds frequently don't offer items going back long enough. If you check a feed e.g. once a week but the feed
only lists items from the last 24 hours then you're going to miss items. There are other aggregation services
available, but they either raise privacy concerns or don't provide RSS/Atom feeds to news reader clients.

It's straightforward to implement other data sources like web scrapers, local monitoring etc.


# Requirements

* Python 3.5+ (tested with Python 3.5, 3.6 and 3.7)
* feedparser (tested with 5.2.1)
* PyRSS2Gen (tested with 1.1)


# Installation

Just download the sources and make sure Python, feedparser (`pip install feedparser`) and
PyRSS2Gen (`pip install pyrss2gen`) are installed.


# Usage

Run `run.py`. The command-line interface supports a few arguments: running `run.py -h` will show the help screen.

### Configuration

The list of feeds is read from `sources.txt`. There is an example configuration, along with documentation, in `sources.txt.example`.


# Tests

This application includes a test suite, you can run it with:

    run-tests.py

Tests are written with Python's built-in `unittest` package, there currently are no other dependencies.


# Legal

### Copyright

Copyright (C) 2018 Richard Nusser

### License

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
