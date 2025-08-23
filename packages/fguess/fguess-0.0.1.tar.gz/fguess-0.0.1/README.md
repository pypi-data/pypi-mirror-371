# fguess

[![PyPI - Version](https://img.shields.io/pypi/v/fguess.svg)](https://pypi.org/project/fguess)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/fguess.svg)](https://pypi.org/project/fguess)

-----

Like https://pym.dev/format but in your terminal


## Installation

You install `fguess` with `pip`:

```console
pip install fguess
```

Or if you have [uv](https://docs.astral.sh/uv/) installed:

```console
uvx fguess
```


## Testing

This project uses [hatch](https://hatch.pypa.io).

To run the tests:

```console
hatch test
```

To see code coverage:

```console
hatch test --cover
hatch run cov-html
open htmlcov/index.html
```

To run the auto-formatter:

```console
hatch fmt
```


## License

`fguess` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
