# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019-2025. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019-2025. Todos los derechos reservados.

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         15/02/25
# Project:      Zibanu Django
# Module Name:  category
# Description:  Category manager for Category entity model.
# ****************************************************************
import logging
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import QuerySet, F, ExpressionWrapper
from django.utils.translation import gettext_lazy as _
from zibanu.django.db import models


class CategoryManager(models.Manager):
    """
    Manager class for a Category model
    """
    max_level = settings.ZB_REPOSITORY_MAX_LEVEL_ALLOWED
    multilevel_allowed = settings.ZB_REPOSITORY_MULTILEVEL_FILES_ALLOWED
    mix_files_cats_allowed = settings.ZB_REPOSITORY_MIX_FILES_CATS_ALLOWED

    def __get_choices(self, queryset: QuerySet, insert_none: bool = False):
        """
        Get the sorted choices list from queryset.

        Parameters
        ----------
        queryset: QuerySet
            Queryset to get choices from.
        insert_none: bool
            If True, insert None as the first choice.

        Returns
        -------
        list:
            List of tuples with sorted choices.
        """
        choices =  [(x.id, x.__str__()) for x in sorted(queryset.all(), key=lambda rcq: rcq.__str__())]
        if insert_none:
            choices.insert(0, (0, _("None")))
        return choices

    def get_categories_files_allowed(self, published: bool = True) -> QuerySet:
        """ Get all categories with files allowed."""
        if not self.multilevel_allowed:
            qs = self.get_queryset().filter(level__exact=self.max_level)
        else:
            qs = self.get_queryset().filter(parent_id__isnull=False)
            if not self.mix_files_cats_allowed:
                qs1 = qs.values("parent_id")
                qs = self.get_queryset().exclude(id__in=qs1)
        if published:
                qs = qs.filter(published__exact=True)

        qs = qs.order_by("parent", "name")

        return qs

    def get_categories_files_allowed_choices(self, published: bool = True, insert_none: bool = False) -> list:
        """ Get a sorted choices list from categories with files allowed."""
        qs = self.get_categories_files_allowed(published)
        return self.__get_choices(qs, insert_none=insert_none)

    def get_only_parents(self, published: bool = None) -> QuerySet:
        """
        Method to get all parents categories

        Params
        -------
        enabled: bool
            Flag to force filter by enabled categories.

        Returns
        -------
        Queryset:
            A queryset with all parents categories, filter by published if True unpublished if False and if None, all categories are returned..
        """
        qs = self.filter(level__lt=self.max_level).order_by("name")
        if published is not None :
            qs = qs.filter(published__exact=published)
        return qs

    def get_only_parents_choices(self, published: bool = None, insert_none: bool = False) -> list:
        """ Get a sorted choices list from only parents queryset. """
        qs = self.get_only_parents(published)
        return self.__get_choices(qs, insert_none=insert_none)

    def get_root_categories(self, published: bool = None) -> QuerySet:
        """
        Method to get only root categories.

        Returns
        -------
        Queryset:
            A queryset with only root categories, filter by published if True unpublished if False and if None, all categories are returned..
        """
        qs = self.get_queryset().filter(level__exact=0).order_by("name")
        if published is not None:
            qs = qs.filter(published__exact=published)
        return qs

    def get_root_category(self, category_id: int):
        """
        Get the root category object if it is a child category, otherwise, it returns itself.

        Parameters
        ----------
        category_id: int
            ID of the category to search root

        Returns
        -------
        Category
        """
        try:
            category = self.get_queryset().get(pk=category_id)
            if category.parent is not None:
                category = self.get_root_category(category.parent_id)
        except self.model.DoesNotExist as exc:
            logging.error(str(exc))
            raise ValidationError(_("Category not found."))
        return category


    def get_children(self, category_id: int, published: bool = None) -> QuerySet:
        """
        Method to get all children categories for category id.

        Parameters
        ----------
        category_id: int
            Category id to get children for
        published: bool
            Flag to indicate if only filter published if True, unpublished if False and if None, all categories are returned.

        Returns
        -------
        Queryset
        """
        qs = self.get_queryset().filter(parent__exact=category_id).order_by("name")
        if published is not None:
            qs = qs.filter(published=published, parent__published=published)
        return qs

    def get_children_count(self, category_id: int, published: bool = None) -> int:
        """
        Get count of all children categories for category id.

        Parameters
        ----------
        category_id: int
            Category id to get children count for
        published: bool
            Flag to filter published if True, unpublished if False and if None, all categories are returned.

        Returns
        -------
        integer
            Count of all children categories.
        """
        children_count = 0
        if category_id is not None:
            qs = self.get_children(category_id)
            if published is not None:
                qs = qs.filter(published=published)
            children_count = qs.count()
        return children_count

    def set_children_publish(self, category_id: int, publish: bool) -> None:
        """
        Recursive method to set a publishing flag for children categories.

        Parameters
        ----------
        category_id: int
            Identifier of the category to set children publishes
        publish: bool
            Flag to set publishing for children categories
        Returns
        -------
        None
        """
        with transaction.atomic():
            children_qs = self.get_children(category_id)
            if not publish:
                children_qs.update(published=publish)
                for child in children_qs:
                    self.set_children_publish(child.id, publish)
                    files = child.file_extended.all()
                    files.update(published=publish)
        return None


    def set_children_level(self, category_id: int, level: int):
        with transaction.atomic():
            if level > self.max_level:
                raise ValidationError(_("Maximum level reached."))
            children_qs = self.get_children(category_id)
            children_qs.update(level=level)
            for child in children_qs:
                self.set_children_level(child.id, level + 1)