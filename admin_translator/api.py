import json
from functools import lru_cache
from operator import itemgetter
from urllib.error import HTTPError

import requests
from django.contrib import messages

from .models import (
    ListLanguagesModel,
)

folder_id =    '...'
yandex_OAuth = '...'


# Время жизни iam токена заметно меньше OAuth
# получаем его при каждм ззапросе
# @lru_cache()
def get_iam_token():
    iam_request_body = {
        'yandexPassportOauthToken': yandex_OAuth,
    }
    iam_request_url = 'https://iam.api.cloud.yandex.net/iam/v1/tokens'
    response = requests.post(
        url=iam_request_url,
        data=json.dumps(iam_request_body),
    )
    if response.ok:
        iam_token = response.json().get('iamToken')
    else:
        raise HTTPError(
            '\n'.join((
                'Cant get IAM token.',
                f'{response.status_code} code',
                response.text,
            ))
        )
    return iam_token


def make_import_language_list(_request, *args):
    """

    :return:
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
        language_list = []
        for language in languages_from_request:
            language_list.append(
                ListLanguagesModel(
                    code=language['code'],
                    name=language.get('name', language['code']),
                )
            )
        try:
            ListLanguagesModel.objects.bulk_create(language_list)
        except:
            raise
    else:
        messages.error(
            _request,
            'Cant get languages list :(',
        )


def translate(text, lang_code):
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
        translation = ' '.join(
            map(
                itemgetter('text'),
                translations,
            )
        )
    else:
        messages.error(
            '\n'.join((
                'Cant translate ',
                response.status_code,
            ))
        )
    return translation

