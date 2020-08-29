from django.db import models
from ckeditor.fields import RichTextField


class ListLanguagesModel(models.Model):
    name = models.CharField(
        'Название языка',
        max_length=100,
        blank=True,
    )
    code = models.CharField(
        'Код языка (ISO 639-1)',
        max_length=10,
        unique=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'list_languages'
        verbose_name = 'Досутпные языки для первода'


class TranslatedTextModel(models.Model):
    input_text = RichTextField(
        'Текст для перевода',
    )
    language = models.ForeignKey(
        ListLanguagesModel,
        on_delete=models.PROTECT,
    )
    output_text = RichTextField(
        'Переведенный текст',
        blank=True,
    )

    def translate_text_with_html(self):
        """
        Выполняетя перевод текста записи и сохраняетс
        :param self: TranslatedTextModel record
        :return: None
        """
        # cross import fix
        from .api import (
            translate_text_with_code,
            TranslateFormatEnum,
        )
        translate = translate_text_with_code(
            self.input_text,
            self.language.code,
            _format=TranslateFormatEnum.HTML,
        )
        self.output_text = translate
        self.save()

    def __str__(self):
        result = ' - '.join((
            self.input_text[:30],
            self.language.code,
            str(self.output_text),
        ))
        return result

    class Meta:
        db_table = 'translated_text'
        verbose_name = 'Текст до перевода и после'
