from __future__ import annotations

import inspect
import logging
import os
import re
from pathlib import Path

from zut import skip_utf8_bom
from zut.db import get_sql_create_names

from django.conf import settings
from django.db.migrations import RunSQL
from django.db.migrations.operations.base import Operation

_logger = logging.getLogger(__name__)


def get_sql_migration_operations(path: str|os.PathLike|None = None, vars: dict|None = None) -> list[Operation]:
    def get_ordered_files(directory: str|os.PathLike, *, ext: str|None = None, recursive: bool = False) -> list[Path]:
        if not isinstance(directory, Path):
            directory = Path(directory)

        if ext and not ext.startswith('.'):
            ext = f'.{ext}'

        def generate(directory: Path):
            for path in sorted(directory.iterdir(), key=lambda entry: (0 if entry.is_dir() else 1, entry.name)):
                if path.is_dir():
                    if recursive:
                        yield from generate(path)
                elif not ext or path.name.lower().endswith(ext):
                    yield path

        return [ path for path in generate(directory) ]

    def get_sql_and_reverse_sql(file: str|os.PathLike):
        sql = None
        reverse_sql = None

        with open(file, 'r', encoding='utf-8') as fp:
            skip_utf8_bom(fp)

            while True:
                line = fp.readline()
                if not line:
                    break
                if vars:
                    for name, value in vars.items():
                        line = line.replace("{"+name+"}", value)

                if reverse_sql is None:
                    # search !reverse mark
                    stripped_line = line = line.strip()
                    if stripped_line.startswith('--') and stripped_line.lstrip(' -\t').startswith('!reverse'):
                        reverse_sql = line
                    else:
                        sql = (sql + '\n' if sql else '') + line
                else:
                    reverse_sql += '\n' + line

        return sql, reverse_sql

    if path is None:
        calling_module = inspect.getmodule(inspect.stack()[1][0])
        if not calling_module:
            raise ValueError("Cannot find calling module")
        if not calling_module.__file__:
            raise ValueError("Calling module has not __file__: %s" % (calling_module,))
        calling_file = Path(calling_module.__file__)
        path = calling_file.parent.joinpath(calling_file.stem).with_suffix('.sql')
        if not path.exists():
            path = calling_file.parent.joinpath(calling_file.stem).with_suffix('')
    elif not isinstance(path, Path):
        path = Path(path)

    if path.is_file():
        sql, reverse_sql = get_sql_and_reverse_sql(path)
        return [RunSQL(sql, reverse_sql)]
    elif path.is_dir():
        operations = []

        for path in get_ordered_files(path, ext='.sql', recursive=True):
            sql, reverse_sql = get_sql_and_reverse_sql(path)
            operations.append(RunSQL(sql, reverse_sql))

        return operations
    else:
        raise ValueError(f"Migration path not found: {path}")


def check_migration_sql_file_names():
    def check_file(path: Path):
        _logger.debug("Check migration SQL file name: %s", path)

        m = re.match(r'^[0-9]+\-(.+)$', path.stem)
        if m:
            expected_name = m[1].lower()
        else:
            expected_name = path.stem.lower()

        names = get_sql_create_names(path, lower_names=True)
        if not expected_name in names:
            suffix = ''
            if names:
                suffix = " (founnd creation of " + ', '.join(f'"{name}"' for name in names) + ")"
            _logger.warning(f"No creation of \"{expected_name}\" found in SQL migration file {path}" + suffix)
            return

    path: Path
    for path in settings.BASE_DIR.glob('**/migrations/**/*.sql'):
        if re.match(r'^[0-9]{4}_', path.name) or any(not re.match(r'^[a-zA-Z0-9_\.]+$', part) for part in path.relative_to(settings.BASE_DIR).with_suffix('').parts):
            continue

        with open(path, 'r', encoding='utf-8') as fp:
            for line in fp:
                if 'check_migration_sql_file_names:skip' in line:
                    return

        check_file(path)
