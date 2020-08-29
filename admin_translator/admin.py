from django.contrib import admin

from .api import make_import_language_list
from .models import (
    ListLanguagesModel,
    TranslatedTextModel,
)


class LanguageListAdmin(admin.ModelAdmin):
    actions = [
        make_import_language_list,
    ]

    # def response_add(
    #         self,
    #         request,
    #         obj,
    #         post_url_continue=None,
    # ):
    #     # make_import_language_list()
    #     pass

    def add_view(self, request, form_url='', extra_context=None):
        make_import_language_list(request, form_url, extra_context)
        return super().add_view(request, form_url, extra_context)


class TranslateTextAdmin(admin.ModelAdmin):

    def response_post_save_change(self, request, obj):
        """
        """
        return super().response_post_save_change(request, obj)


admin.site.register(ListLanguagesModel, LanguageListAdmin)
admin.site.register(TranslatedTextModel, TranslateTextAdmin)
