# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019-2025. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019-2025. Todos los derechos reservados.

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         4/02/23 15:45
# Project:      Zibanu Django Project
# Module Name:  document
# Description:
# ****************************************************************
from zibanu.django.db import models


class File(models.Manager):
    """
    Manager class for the Document model
    """
    def get_by_uuid(self, uuid: str) -> models.QuerySet:
        """
        Get a document queryset from the uuid value
        Parameters
        ----------
        uuid: String with uuid value

        Returns
        -------
        qs: Queryset with filter by uuid value
        """
        return self.filter(uuid__exact=uuid)

    def get_by_code(self, code: str) -> models.QuerySet:
        """
        Get a document queryset from the code value.

        Parameters
        ----------
        code: String with code value

        Returns
        -------
        qs: Queryset with filter by code value.
        """
        return self.filter(code__exact=code)

    def get_by_category(self, category_id: int, published: bool = True) -> models.QuerySet:
        """
        Get a document queryset from the category value.

        Parameters
        ----------
        category_id: int
            Category id to get files
        published: bool
            Flag to indicate if only filter published if True, unpublished if False and if None, all files are returned.

        Returns
        -------
        Queryset:
            Queryset with filter by category value.
        """
        # *****************************************************************************
        # COMMENT: Change import statement to avoid circularity bug.
        # Modified by: macercha
        # Modified at: 2025-04-12, 17:03
        # *****************************************************************************
        from zibanu.django.repository.models.category import Category
        list_sort_by = ["file_extended__title", "generated_at", "id"]
        list_sort_type = ["", "-"]
        category = Category.objects.get(pk=category_id)
        sort_by = category.sort_by
        sort_type = category.sort_type
        # *****************************************************************************
        # COMMENT: Add sort statement to do compatible with new features
        # Modified by: macercha
        # Modified at: 2025-04-12, 17:04
        # *****************************************************************************
        qs = self.filter(file_extended__category_id__exact=category_id)
        if published is not None:
            qs = qs.filter(file_extended__published__exact=published)
        qs = qs.order_by(list_sort_type[sort_type] + list_sort_by[sort_by])
        return qs

    def get_count_by_category(self, category_id: int, published: bool = True) -> int:
        """
        Get the number of files for a category.

        Parameters
        ----------
        category_id: int
            Id of category to get the number of files for a specific category
        published: bool
            Flag to indicate if only filter published if True, unpublished if False and if None, all files are returned.

        Returns
        -------
        int:
            Number of files for a specific category
        """
        files_count = 0

        if category_id is not None:
            qs = self.get_by_category(category_id, published)
            files_count = qs.count()
        return files_count

