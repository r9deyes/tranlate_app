from django.contrib import admin, messages
from django.db import IntegrityError
from requests import HTTPError

from .api import (
    make_import_language_list,
)
from .models import (
    ListLanguagesModel,
    TranslatedTextModel,
)


class LanguageListAdmin(admin.ModelAdmin):
    list_display = [
        'code',
        'name',
    ]
    actions = [
        'make_import',
    ]

    def make_import(self, request, queryset):
        try:
            make_import_language_list()
        except IntegrityError:
            messages.error(
                request,
                'Произошла ошибка при запись в БД',
            )
        except HTTPError as ex:
            messages.error(
                request,
                str(ex),
            )
    make_import.short_description = 'Выполнить импорт списка доступных языков'

    # Импорт выполняется при вызове шаблона добавления новой записи
    def add_view(self, request, form_url='', extra_context=None):
        self.make_import(
            request=request,
            queryset=None,
        )
        messages.info(
            request,
            'Импорт записей был успешно выполнен'
        )
        # Показываем списочный шаблон вместо показа формы добавления
        return super().changelist_view(
            request=request,
            extra_context=extra_context,
        )


class TranslateTextAdmin(admin.ModelAdmin):
    list_display = [
        'input_text',
        'language',
        'output_text',
    ]
    # Выполнить перевод из списочного вида
    actions = [
        'translate_text_in_queryset',
    ]

    def translate_text_in_queryset(self, request, queryset):
        queryset = queryset.select_related(
            'language',
        )
        try:
            for obj in queryset:
                obj.translate_text_with_html()
        except HTTPError as ex:
            messages.error(
                request,
                str(ex),
            )
    translate_text_in_queryset.short_description = 'Выполнить перевод'

    # Перевод выполняется при сохранении записи модели
    def response_post_save_change(self, request, obj):
        try:
            obj.translate_text_with_html()
        except HTTPError as ex:
            messages.error(
                request,
                str(ex),
            )
        return super().response_post_save_change(request, obj)


admin.site.register(ListLanguagesModel, LanguageListAdmin)
admin.site.register(TranslatedTextModel, TranslateTextAdmin)
