# -*- coding: UTF-8 -*-
# Copyright 2012-2025 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from django.db import models

# from django.utils.translation import get_language
# from django.utils.html import format_html

from lino.api import dd, rt, _
from lino.utils.html import E
from lino.core import constants
# from lino.core.renderer import add_user_language
from lino.modlib.office.roles import OfficeUser

from .choicelists import PageFillers, SpecialPages


if dd.is_installed("comments") and dd.is_installed("topics"):
    DISCUSSION_PANEL = """
    topics.TagsByOwner:20 comments.CommentsByRFC:60
    """
else:
    DISCUSSION_PANEL = ""


class PageDetail(dd.DetailLayout):
    main = "general first_panel more"

    first_panel = dd.Panel(
        """
    treeview_panel:20 preview:60
    """,
        label=_("Preview"),
    )

    general = dd.Panel(
        """
    content_panel:60 right_panel:20
    """,
        label=_("General"),
        required_roles=dd.login_required(OfficeUser),
    )

    more = dd.Panel(
        DISCUSSION_PANEL,
        label=_("Discussion"),
        required_roles=dd.login_required(OfficeUser),
    )

    content_panel = """
    title id
    body
    publisher.PagesByParent
    """

    # right_panel = """
    # parent seqno
    # child_node_depth
    # page_type
    # filler
    # """

    right_panel = """
    group language ref
    parent seqno root_page
    child_node_depth main_image
    special_page filler
    publishing_state private
    publisher.TranslationsByPage
    """


class Pages(dd.Table):
    model = "publisher.Page"
    column_names = "ref title #page_type id *"
    detail_layout = "publisher.PageDetail"
    insert_layout = """
    title
    ref
    #page_type filler
    """
    default_display_modes = {None: constants.DISPLAY_MODE_LIST}


class PagesByParent(Pages):
    master_key = "parent"
    label = _("Children")
    # ~ column_names = "title user *"
    order_by = ["seqno"]
    column_names = "seqno title *"
    default_display_modes = {None: constants.DISPLAY_MODE_LIST}


# PublisherViews.add_item_lazy("p", Pages)
# PublisherViews.add_item_lazy("n", Nodes)

# PageTypes.add_item(Pages, 'pages')


class TranslationsByPage(Pages):
    master_key = "translated_from"
    label = _("Translations")
    column_names = "ref title language id *"
    default_display_modes = {None: constants.DISPLAY_MODE_SUMMARY}

    @classmethod
    def row_as_summary(cls, ar, obj, text=None, **kwargs):
        # return format_html("({}) {}", obj.language, obj.as_summary_row(ar, **kwargs))
        return E.span("({}) ".format(obj.language), obj.as_summary_item(ar, text, **kwargs))


class RootPages(Pages):
    label = _("Root pages")
    filter = models.Q(parent__isnull=True, special_page='')
    column_names = "ref title language"
    # default_display_modes = {None: constants.DISPLAY_MODE_LIST}


filler = PageFillers.add_item(RootPages)

SpecialPages.add_item(
    "pages", filler=filler, body=_("List of root pages."),
    title=_("Root pages"),
    parent='home')
