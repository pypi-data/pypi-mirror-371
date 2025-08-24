"""
Write and read using JSON format.
"""
from __future__ import annotations

from importlib import import_module
from io import BytesIO, StringIO
import json
import os
import re
import sys
from contextlib import AbstractContextManager, contextmanager
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from enum import Enum, Flag
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING, IO, Any, Callable, Sequence, TypeVar
from uuid import UUID

from zut import skip_utf8_bom
from zut.polyfills import ZipPath

if TYPE_CHECKING:
    from typing import Literal


#region Write JSON

class ExtendedJSONEncoder(json.JSONEncoder):
    """
    Adapted from: django.core.serializers.json.DjangoJSONEncoder
    
    Usage example: json.dumps(data, indent=4, cls=ExtendedJSONEncoder)
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def default(self, o):
        if isinstance(o, datetime):
            r = o.isoformat()
            if o.microsecond and o.microsecond % 1000 == 0:
                r = r[:23] + r[26:]
            if r.endswith("+00:00"):
                r = r[:-6] + "Z"
            return r
        elif isinstance(o, date):
            return o.isoformat()
        elif isinstance(o, time):
            if o.tzinfo is not None:
                raise ValueError("JSON can't represent timezone-aware times.")
            r = o.isoformat()
            if o.microsecond and o.microsecond % 1000 == 0:
                r = r[:12]
            return f'T{r}'
        elif isinstance(o, timedelta):
            from zut.convert import get_duration_str
            return get_duration_str(o)
        elif isinstance(o, (Decimal, UUID)):
            return str(o)
        else:
            try:
                from django.utils.functional import \
                    Promise  # type: ignore (optional dependency)
                if isinstance(o, Promise):
                    return str(o)
            except ModuleNotFoundError:
                pass

            if isinstance(o, (Enum,Flag)):
                return o.value
            elif isinstance(o, bytes):
                return str(o)
            elif not isinstance(o, type) and hasattr(o, 'to_jsondict'):
                result = o.to_jsondict() # pyright: ignore[reportAttributeAccessIssue]
                if not isinstance(result, dict):
                    raise TypeError(f"{type(o).__name__}.to_jsondict() method returned {type(result).__name__}, expected dict")
                return result
            else:
                return super().default(o)


def to_jsondict(obj: object, attributes: Sequence[str]|Literal['*']):
    try:
        if '__cls__' in obj.__dict__:
            raise ValueError(f"Cannot create JSON dict for {type(obj)}: there is already a __cls__ attribute")
    except AttributeError:
            raise ValueError(f"Cannot create JSON dict for {type(obj)}: no __dict__ attribute") from None

    result = {'__cls__': type(obj).__module__ + ':' + type(obj).__qualname__}
    for key, value in obj.__dict__.items():
        if attributes == '*' or key in attributes:
            result[key] = value
    return result


class JsonWriter:
    default_indent: int|None = 2
    default_encoder: type[json.JSONEncoder] = ExtendedJSONEncoder


def dump_json(data: Any, file: str|os.PathLike|IO[str], *, indent: int|None = None, sort_keys = False, ensure_ascii = False, cls: type[json.JSONEncoder]|None = None, encoding = 'utf-8', archivate: bool|str|os.PathLike|ZipPath|None = None):
    if indent is None:
        indent = JsonWriter.default_indent
    if cls is None:
        cls = JsonWriter.default_encoder

    _file_manager: AbstractContextManager[IO[str]]|None
    _file: IO[str]
    if isinstance(file, (str, os.PathLike)):
        from zut import files
        if archivate:
            files.archivate(file, archivate, missing_ok=True)
        _file_manager = files.open(file, 'w', encoding=encoding, mkdir=True)
        _file = _file_manager.__enter__()
    else:
        _file_manager = None # managed externally
        _file = file

    try:
        json.dump(data, _file, ensure_ascii=ensure_ascii, indent=None if indent == 0 else indent, sort_keys=sort_keys, cls=cls)
        if _file == sys.stdout or _file == sys.stderr:
            _file.write('\n')
    finally:
        if _file_manager:
            _file_manager.__exit__(None, None, None)


@contextmanager
def dump_json_temp(data: Any, *, encoding = 'utf-8', indent: int|None = None, sort_keys = False, ensure_ascii = False, cls: type[json.JSONEncoder]|None = None):
    temp = None
    try:
        with NamedTemporaryFile('w', encoding=encoding, suffix='.json', delete=False) as temp:
            dump_json(data, temp.file, ensure_ascii=ensure_ascii, indent=indent, sort_keys=sort_keys, cls=cls)
 
        yield temp.name
    finally:
        if temp is not None:
            os.unlink(temp.name)


def dumps_json(data: Any, *, indent: int|None = None, sort_keys = False, ensure_ascii = False, cls: type[json.JSONEncoder]|None = None) -> str:
    with StringIO() as fp:
        dump_json(data, fp, indent=indent, sort_keys=sort_keys, ensure_ascii=ensure_ascii, cls=cls)
        return fp.getvalue()


def dumps_json_noindent(data: Any, *, sort_keys = False, ensure_ascii = False, cls: type[json.JSONEncoder]|None = None) -> str:
    with StringIO() as fp:
        dump_json(data, fp, indent=0, sort_keys=sort_keys, ensure_ascii=ensure_ascii, cls=cls)
        return fp.getvalue()

#endregion


#region Read JSON

class ExtendedJSONDecoder(json.JSONDecoder):
    def __init__(self, *, object_hook = None, **options):
        super().__init__(object_hook=object_hook or self._object_hook, **options)

    def _object_hook(self, data: dict):
        cls_spec = data.get('__cls__')
        if isinstance(cls_spec, str):
            return from_jsondict(data, '*', use_constructor=False)
        
        for key, value in data.items():
            if isinstance(value, str):
                from zut.convert import recognize_datetime
                value = recognize_datetime(value)
                if isinstance(value, datetime):
                    data[key] = value
        
        return data


def from_jsondict(data: dict, attributes: str|Sequence[str]|Literal['*'], *, use_constructor: bool|None = None) -> object:
    try:
        cls_spec = data.pop('__cls__')
    except KeyError:
        raise ValueError(f"Cannot create object from JSON dict: no __cls__ key") from None

    cls: type
    if isinstance(cls_spec, type):
        cls = cls_spec
    elif isinstance(cls_spec, str):
        m = re.match(r'^([a-z0-9_\.]+):([a-z0-9_\.]+)$', cls_spec, re.IGNORECASE)
        if not m:
            raise ValueError(f"Cannot create object from JSON dict: __cls__ '{cls_spec}' does not match module:Class pattern")

        modulename: str = m[1]
        qualname: str = m[2]
        try:
            module = import_module(modulename)
        except Exception as err:
            raise ValueError(f"Cannot create '{cls_spec}' object from JSON dict: {err}") from None
        try:
            cls = getattr(module, qualname)
        except AttributeError:
            raise ValueError(f"Cannot create '{cls_spec}' object from JSON dict: attribute '{qualname}' not found in module '{modulename}'") from None
    else:
        raise ValueError(f"Cannot create object from JSON dict: __cls__ is of type {type(cls_spec).__name__}, expected str")
    
    if attributes != '*':
        filtered_data = {}
        for key, value in data.items():
            if key in attributes:
                filtered_data[key] = value
        data = filtered_data
    
    cls_method = None
    if not use_constructor:
        try:
            cls_method = getattr(cls, 'from_jsondict')
        except AttributeError:
            if use_constructor is False:
                raise ValueError(f"Cannot create '{cls_spec}' object from JSON dict: class method 'from_jsondict' not found") from None

    if cls_method:
        return cls_method(data)
    else:    
        return cls(**data)


class JsonLoader:
    default_decoder: type[json.JSONDecoder] = ExtendedJSONDecoder


def load_json(file: str|os.PathLike|IO, *, encoding = 'utf-8', cls: type[json.JSONDecoder]|None = None) -> Any:
    if cls is None:
        cls = JsonLoader.default_decoder
    
    _file_manager: AbstractContextManager[IO]|None
    _file: IO
    if isinstance(file, (str, os.PathLike)):
        from zut import files
        _file_manager = files.open(file, 'r', encoding=encoding)
        _file = _file_manager.__enter__()
    else:
        _file_manager = None # managed externally
        _file = file

    try:
        skip_utf8_bom(_file)
        return json.load(_file, cls=cls)
    finally:
        if _file_manager:
            _file_manager.__exit__(None, None, None)


def loads_json(data: str|bytes, *, cls: type[json.JSONDecoder]|None = None) -> Any:
    with StringIO(data) if isinstance(data, str) else BytesIO(data) as fp:
        return load_json(fp, cls=cls)

#endregion


#region JSON utility decorator

T_Obj = TypeVar('T_Obj', bound=object)

def jsondict(attributes: str|Sequence[str]|Literal['*']) -> Callable[[type[T_Obj]], type[T_Obj]]:
    if isinstance(attributes, str) and attributes != '*':
        attributes = [attributes]
    
    def decorator(cls: type):
        if hasattr(cls, 'to_jsondict'):
            raise ValueError(f"{cls}.to_jsondict is already defined")
        cls.to_jsondict = lambda self: to_jsondict(self, attributes)
        
        if hasattr(cls, 'from_jsondict'):
            raise ValueError(f"{cls}.from_jsondict is already defined")
        cls.from_jsondict = lambda data: from_jsondict({'__cls__': cls, **data}, attributes, use_constructor=True)

        return cls

    # this decorator can only be used with arguments
    return decorator

#endregion
