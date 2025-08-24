from __future__ import annotations

import logging
import re
from http import HTTPStatus
from typing import Any, Mapping, Sequence

from django.conf import settings
from django.db.models import Model
from django.db.models.query import QuerySet
from django.http import HttpRequest, JsonResponse
from django.views.generic import View
from django.views.generic.list import MultipleObjectMixin

from zut import InternalError
from zut.db import Db, ResultManager


class TableDataView(View):
    """
    For Bootstrap Table.

    See https://bootstrap-table.com/docs/api/table-options/#url
    """
    db: Db
    sql: str
    sql_params: Mapping[str,Any]|Sequence[Any]|None = None

    paginate = False

    rows_property = 'rows'
    total_property = 'total'

    def get_sql(self) -> str:
        return self.sql

    def get_sql_params(self) -> Mapping[str,Any]|Sequence[Any]|None:
        return self.sql_params
    
    def get(self, request: HttpRequest, *args, **kwargs):
        sql = self.get_sql()
        params = self.get_sql_params()

        if self.paginate or 'limit' in request.GET or 'offset' in request.GET:
            limit = request.GET.get('limit')
            if not limit:
                return JsonResponse({"error": "Parameter \"limit\" must be set"}, status=HTTPStatus.BAD_REQUEST)
            if not re.match(r'^\d+$', limit):
                return JsonResponse({"error": "Parameter \"limit\" is not an integer"}, status=HTTPStatus.BAD_REQUEST)
            limit = int(limit)

            offset = request.GET.get('offset')
            if not offset:
                return JsonResponse({"error": "Parameter \"offset\" must be set"}, status=HTTPStatus.BAD_REQUEST)
            if not re.match(r'^\d+$', offset):
                return JsonResponse({"error": "Parameter \"offset\" is not an integer"}, status=HTTPStatus.BAD_REQUEST)
            offset = int(offset)

            rows, total = self.db.get_paginated_dicts(sql, params, limit=limit, offset=offset)
            return JsonResponse({self.rows_property: rows, self.total_property: total})

        else:
            rows = self.db.get_dicts(sql, params)
            return JsonResponse({self.rows_property: rows})


class SelectDataView(MultipleObjectMixin, View):
    """
    Generate API data for Select2.

    See https://select2.org/data-sources/ajax
    """
    db: Db
    sql: str
    sql_params: Mapping[str,Any]|Sequence[Any]|None = None

    id_field = 'id'
    text_field = 'name'
    detail_field: str|Sequence[str]|None = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._logger = logging.getLogger(f'{self.__class__.__module__}.{self.__class__.__qualname__}')

    def get_sql(self) -> str:
        return self.sql

    def get_sql_params(self) -> Mapping[str,Any]|Sequence[Any]|None:
        return self.sql_params
    
    def get_values_queryset(self):
        fields = [self.id_field, self.text_field]
        if isinstance(self.detail_field, str):
            fields.append(self.detail_field)
        elif isinstance(self.detail_field, Sequence):
            for detail_field in self.detail_field:
                fields.append(detail_field)
        return self.get_queryset().values(*fields)
    
    def handle_result(self, result: dict):
        if not isinstance(result, dict):
            raise InternalError(f"SelectDataView result is of type {type(result)}, expected dict")
        
        if self.id_field != 'id' and self.id_field in result:
            result['id'] = result[self.id_field]
            del result[self.id_field]
        
        if self.text_field != 'text' and self.text_field in result:
            result['text'] = result[self.text_field]
            del result[self.text_field]
        
        missing_keys = []
        for key in ['id', 'text']:
            if not key in result:
                missing_keys.append(key)
        if missing_keys:
            raise InternalError(f"Missing key(s) {', '.join(missing_keys)} in SelectDataView result")
    
        return result
    
    def get_response_data(self):
        results = []
        pagination_more = False #ROADMAP see issue #14
    
        if hasattr(self, 'sql'):
            sql = self.get_sql()
            params = self.get_sql_params()

            with self.db.execute_result(sql, params) as result:
                for result in result.get_dicts():
                    result = self.handle_result(result)
                    results.append(result)

        else:
            qs = self.get_values_queryset()

            for result in qs:
                result = self.handle_result(result)
                results.append(result)

        return {'results': results, 'pagination': {'more': pagination_more}}
        
    def get(self, request: HttpRequest, *args, **kwargs):
        try:
            data = self.get_response_data()
            return JsonResponse(data)
        except InternalError as err:
            message = str(err)
            self._logger.error(message)
            return JsonResponse({'error': message if settings.DEBUG else "An internal server error occured"}, status=HTTPStatus.INTERNAL_SERVER_ERROR.value)
