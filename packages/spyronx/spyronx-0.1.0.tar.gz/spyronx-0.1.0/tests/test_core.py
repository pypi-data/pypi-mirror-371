import spyronx
from spyronx.core import slugify, flatten

def test_import_version():
    assert isinstance(spyronx.__version__, str) and len(spyronx.__version__) > 0

def test_slugify():
    assert slugify("Hello, World!") == "hello-world"
    assert slugify("  Việt Nam ++ 2025  ") == "vi-t-nam-2025"

def test_flatten():
    assert flatten([[1,2],[3]]) == [1,2,3]