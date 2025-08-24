# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019-2025. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019-2025. Todos los derechos reservados.

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         18/02/25
# Project:      Zibanu Django
# Module Name:  admin_categories_view
# Description:
# ****************************************************************
import logging
from django import forms
from django.apps import apps
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from zibanu.django.lib.utils import object_to_list
from zibanu.django.repository.lib.filters import ParentListFilter
from zibanu.django.repository.models import Category

class CategoriesAdminView(admin.ModelAdmin):
    """ Category Model class."""
    list_display = ("name", "parent", "published", "level")
    fieldsets = (
        (None, {"fields": ("name", "parent")}),
        (_("Features"), {
            "fields": ["gen_thumb", "gen_ml", "extract_metadata", "extract_tables", "file_types", ("sort_by", "sort_type")],
            "classes": ["collapse"],
        }),
        (_("Status"), {"fields": ("published", )})
    )
    actions = ["publish_categories", "unpublish_categories"]
    list_filter = [ParentListFilter, "level"]
    sortable_by = ["name", "parent", "published", "level"]
    search_fields = ["name", "parent__name", "parent__parent__name"]
    list_select_related = ["parent"]
    list_per_page = 20

    @staticmethod
    def __get_category_choices() -> list:
        """
        Method to load a sorted choices list from the Category model manager.

        Returns
        -------
        list:
            List of tuples with the sorted choices.
        """
        app = apps.get_app_config("zb_repository")
        choices = []
        if app.is_ready:
            choices = Category.objects.get_only_parents_choices(published=True, insert_none=True)
        return choices


    @admin.action(description=_("Publish the selected categories."))
    def publish_categories(self, request: HttpRequest, queryset: QuerySet) -> None:
        """
        Method to publish selected categories and their children.
        Parameters
        ----------
        request:
            HTTP request object

        queryset:
            Set of selected categories to do the action on.

        Returns
        -------
        None
        """
        try:
            queryset = queryset.order_by("level")
            for category in queryset:
                category.refresh_from_db(fields=["parent"])
                if category.parent is not None:
                    category.parent.refresh_from_db(
                        fields=["published"]
                    )
                category.published = True
                category.save()
        except ValidationError as exc:
            if len(exc.messages) > 0:
                messages.error(request, exc.messages[0])
            else:
                messages.error(request, _("Error publishing the category or categories."))


    @admin.action(description=_("Unpublish the selected categories."))
    def unpublish_categories(self, request: HttpRequest, queryset: QuerySet) -> None:
        """
        Method to unpublish selected categories and their children categories and files.
        Parameters
        ----------
        request:
            HTTP request object
        queryset:
            Set of selected categories to do the action on.

        Returns
        -------
        None
        """
        try:
            with transaction.atomic():
                for child in queryset:
                    child.published = False
                    child.save()
        except ValidationError as exc:
            messages.error(request, _("Error unpublishing the category or categories."))

    def get_form(self, request, obj: Category = None, **kwargs):
        # *****************************************************************************
        # COMMENT: Override clean method to replace factory clean method.
        # Modified by: macercha
        # Modified at: 2025-05-14, 11:39
        # *****************************************************************************
        def override_clean(target_form):
            """ Override method to clean the form before saving it. """
            if "parent" not in target_form.cleaned_data.keys():
                target_form.cleaned_data["parent"] = None
                raise ValidationError(_("Parent category is not published."))

            if target_form.cleaned_data.get("parent", None) is not None:
                if target_form.cleaned_data["parent"] == 0:
                    target_form.cleaned_data["parent"] = None
                else:
                    target_form.cleaned_data["parent"] = Category.objects.get(id=target_form.cleaned_data["parent"])
            return target_form.cleaned_data

        # Get form object and replace the parent field.
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["parent"] = forms.TypedChoiceField(choices=self.__get_category_choices(), coerce=int)
        clean_method = getattr(form, "clean", None)

        # Set the override clean method.
        if callable(clean_method):
            setattr(form, "clean", override_clean)

        # Validate parent publish status.
        if obj is not None and obj.parent is not None and not obj.parent.published:
            messages.error(request, _("The parent category is not published. Changes not allowed."))
            for key in form.base_fields.keys():
                form.base_fields[key].disabled = True

        return form


    def save_model(self, request: HttpRequest, obj, form, change):
        """ Override save model method. """
        try:
            super().save_model(request, obj, form, change)
        except ValidationError as exc:
            error_list = object_to_list(exc.messages)
            if len(error_list) > 0:
                for message_error in error_list:
                    messages.error(request, message_error)
                    logging.error(message_error)
        except Exception as exc:
            messages.error(request, str(exc))
            logging.error(str(exc))
