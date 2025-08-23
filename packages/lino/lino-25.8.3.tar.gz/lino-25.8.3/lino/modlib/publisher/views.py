# -*- coding: UTF-8 -*-
# Copyright 2020-2025 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from django import http
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils import translation
from django.views.generic import View
from lino.core.requests import BaseRequest


class Element(View):
    # actor = None
    # publisher_view = None
    table_class = None

    def get(self, request, pk=None):
        # print("20220927 a get()")
        # if pk is None:
        #     return http.HttpResponseNotFound()
        # rnd = settings.SITE.kernel.default_renderer
        rnd = settings.SITE.plugins.publisher.renderer

        # kw = dict(actor=self.publisher_model.get_default_table(),
        #     request=request, renderer=rnd, permalink_uris=True)
        # kw = dict(renderer=rnd)
        # kw = dict(renderer=rnd, permalink_uris=True)
        # if rnd.front_end.media_name == 'react':
        #     kw.update(hash_router=True)

        # kw.update(selected_pks=[pk])
        #
        # try:
        #     ar = self.table_class.create_request(request=request, **kw)
        # except ObjectDoesNotExist as e:
        #     # print("20240911", e)
        #     return http.HttpResponseNotFound(f"No row #{pk} in {self.table_class} ({e})")
        # if len(ar.selected_rows) == 0:
        #     # print(f"20241003 Oops {ar} has no rows")
        #     return http.HttpResponseNotFound(f"20241003 No row #{pk} in {self.table_class}")
        # obj = ar.selected_rows[0]

        m = self.table_class.model
        try:
            obj = m.objects.get(pk=pk)
        except m.DoesNotExist as e:
            return http.HttpResponseNotFound(f"No row #{pk} in {m} ({e})")
        ar = BaseRequest(renderer=rnd, request=request, selected_rows=[obj])
        # ar = BaseRequest(renderer=rnd, request=request)
        return obj.get_publisher_response(ar)


class Index(View):
    def get(self, request, ref=''):
        dv = settings.SITE.models.publisher.Pages
        if len(settings.SITE.languages) == 1:
            # language = settings.SITE.languages[0].django_code
            language = translation.get_language()
        else:
            language = request.LANGUAGE_CODE
        if ref == '':
            ref = 'index'
        try:
            obj = dv.model.objects.get(ref=ref, language=language)
        except dv.model.DoesNotExist:
            return http.HttpResponseNotFound(f"No row {ref} in {dv.model}")

        # print("20231025", index_node)
        rnd = settings.SITE.plugins.publisher.renderer
        ar = dv.create_request(request=request, renderer=rnd,
                               selected_rows=[obj])
        return obj.get_publisher_response(ar)
