import json
from operator import itemgetter

import requests
from django.conf import settings

from .models import (
    ListLanguagesModel,
)

folder_id = settings.TRANSLATE_API_KEYS['folder_id']
yandex_OAuth = settings.TRANSLATE_API_KEYS['yandex_OAuth']


class TranslateFormatEnum:
    PLAIN_TEXT = 'PLAIN_TEXT'
    HTML = 'HTML'


# Время жизни iam токена заметно меньше OAuth
# получаем его при каждм ззапросе
def get_iam_token():
    """
    Получение токена ШФЬ через ЩФгер токен Яндекса
    :return: str IAM token
    """
    iam_request_url = 'https://iam.api.cloud.yandex.net/iam/v1/tokens'
    iam_request_body = {
        'yandexPassportOauthToken': yandex_OAuth,
    }
    response = requests.post(
        url=iam_request_url,
        data=json.dumps(iam_request_body),
    )
    if response.ok:
        iam_token = response.json().get('iamToken')
    else:
        raise requests.HTTPError(
            '\n'.join((
                'Cant get IAM token.',
                response.status_code,
                response.text,
            ))
        )
    return iam_token


def make_import_language_list():
    """
    Выполням запрос списка доступных языков и сохраням в модели
    :return: None
    """
    list_languages_url = 'https://translate.api.cloud.yandex.net/translate/v2/languages'  # noqa
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {get_iam_token()}',
    }
    data = json.dumps(
        {
            'folder_id': folder_id,
        }
    )
    response = requests.post(
        url=list_languages_url,
        data=data,
        headers=headers,
    )

    if response.ok:
        languages_from_request = response.json().get('languages', ())
        for language in languages_from_request:
            ListLanguagesModel.objects.update_or_create(
                code=language['code'],
                defaults={
                    'name': language.get(
                        'name',
                        language['code'],
                    ),
                },
            )
    else:
        raise requests.HTTPError(
            '\n'.join((
                'Cant get languages list',
                response.status_code,
                response.text,
            ))
        )


def translate_text_with_code(
        text,
        lang_code,
        _format=TranslateFormatEnum.PLAIN_TEXT,
):
    """
    Выполням запрос для перевода текста на указанный код языка, возвращаем переведенный текст.
    Можо указать формат твходящего текста
    :param text: str текст для перевода
    :param lang_code: ISO 639-1 код языка 
    :param _format: PLAIN_TEXT OR HTML
    :return: str Переведенный текст
    """
    translate_request_url = 'https://translate.api.cloud.yandex.net/translate/v2/translate'
    header = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {get_iam_token()}',
    }
    translate_request_body = json.dumps(
        {
            'folder_id': folder_id,
            'texts': [text],
            'targetLanguageCode': lang_code,
            'format': _format,
        }
    )
    response = requests.post(
        url=translate_request_url,
        headers=header,
        data=translate_request_body,
    )

    translation = None
    if response.ok:
        translations = response.json().get('translations')
        translation = ''.join(
            map(
                itemgetter('text'),
                translations,
            )
        )
    else:
        raise requests.HTTPError(
            '\n'.join((
                'Cant translate text',
                response.status_code,
                response.text,
            ))
        )
    return translation
