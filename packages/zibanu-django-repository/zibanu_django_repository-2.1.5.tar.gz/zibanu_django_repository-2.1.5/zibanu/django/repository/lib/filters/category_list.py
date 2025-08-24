# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019-2025. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019-2025. Todos los derechos reservados.

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         29/07/25
# Project:      Zibanu Django
# Module Name:  category_list
# Description:
# ****************************************************************
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from zibanu.django.repository.models import Category

class CategoryAllowedFilesListFilter(admin.SimpleListFilter):
    """ Filter to show only categories with allowed files. """
    title = _("Category")
    parameter_name = "file_extended__category"

    def lookups(self, request, model_admin):
        return Category.objects.get_categories_files_allowed_choices(published=True)

    def queryset(self, request, queryset):
        if self.value():
            queryset = queryset.filter(file_extended__category=self.value())
        return queryset