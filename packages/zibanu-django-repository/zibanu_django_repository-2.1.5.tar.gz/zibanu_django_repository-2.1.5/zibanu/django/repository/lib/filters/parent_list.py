# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019-2025. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019-2025. Todos los derechos reservados.

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         29/07/25
# Project:      Zibanu Django
# Module Name:  parent_list
# Description:
# ****************************************************************
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from zibanu.django.repository.models import Category

class ParentListFilter(admin.SimpleListFilter):
    """ Filter to show only parents categories. """
    title = _("Category")
    parameter_name = "parent"

    def lookups(self, request, model_admin):
        return Category.objects.get_only_parents_choices(published=True)

    def queryset(self, request, queryset):
        if self.value():
            queryset = queryset.filter(parent=self.value())
        return queryset