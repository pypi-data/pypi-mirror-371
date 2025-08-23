## Typing stubs for setuptools

This is a [type stub package](https://typing.python.org/en/latest/tutorials/external_libraries.html)
for the [`setuptools`](https://github.com/pypa/setuptools) package. It can be used by type checkers
to check code that uses `setuptools`. This version of
`types-setuptools` aims to provide accurate annotations for
`setuptools==80.9.*`.

Given that `pkg_resources` is typed since `setuptools >= 71.1`, it is no longer included with `types-setuptools`.

This package is part of the [typeshed project](https://github.com/python/typeshed).
All fixes for types and metadata should be contributed there.
See [the README](https://github.com/python/typeshed/blob/main/README.md)
for more details. The source for this package can be found in the
[`stubs/setuptools`](https://github.com/python/typeshed/tree/main/stubs/setuptools)
directory.

This package was tested with the following type checkers:
* [mypy](https://github.com/python/mypy/) 1.17.1
* [pyright](https://github.com/microsoft/pyright) 1.1.404

It was generated from typeshed commit
[`ca44e4c45dc40fb47602dc79a3145ba61879add8`](https://github.com/python/typeshed/commit/ca44e4c45dc40fb47602dc79a3145ba61879add8).