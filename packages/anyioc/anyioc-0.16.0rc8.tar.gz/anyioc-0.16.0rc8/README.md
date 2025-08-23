# anyioc

![GitHub](https://img.shields.io/github/license/Cologler/anyioc-python.svg)
[![Testing](https://github.com/Cologler/anyioc-python/actions/workflows/testing.yml/badge.svg)](https://github.com/Cologler/anyioc-python/actions/workflows/testing.yml)
[![PyPI](https://img.shields.io/pypi/v/anyioc.svg)](https://pypi.org/project/anyioc/)
![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/Cologler/anyioc-python)

Another simple ioc framework for python.

## Usage

``` py
from anyioc import ServiceProvider
provider = ServiceProvider()
provider.register_singleton('the key', lambda ioc: 102) # ioc will be a `IServiceProvider`
value = provider.get('the key')
assert value == 102
```

## Register and resolve

By default, you can use following methods to register services:

- `ServiceProvider.register_singleton(key, factory)`
- `ServiceProvider.register_scoped(key, factory)`
- `ServiceProvider.register_transient(key, factory)`
- `ServiceProvider.register(key, factory, lifetime)`
- `ServiceProvider.register_value(key, value)`
- `ServiceProvider.register_group(key, keys)`
- `ServiceProvider.register_bind(new_key, target_key)`

And use following methods to resolve services:

- `ServiceProvider.__getitem__(key)`
- `ServiceProvider.get(key)`
- `ServiceProvider.get_many(key)`

*`get` return `None` if the service was not found, but `__getitem__` will raise a `ServiceNotFoundError`.*

Read full [documentation](https://github.com/Cologler/anyioc-python/wiki).
