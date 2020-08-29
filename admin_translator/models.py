from django.db import models
from ckeditor.fields import RichTextField


class ListLanguagesModel(models.Model):
    name = models.CharField(
        'Название языка',
        max_length=100,
    )
    code = models.CharField(
        'Код языка (ISO 639-1)',
        max_length=10,
    )

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'list_languages'
        unique_together = (
            'name',
            'code',
        )


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
    )

    class Meta:
        db_table = 'translated_text'
