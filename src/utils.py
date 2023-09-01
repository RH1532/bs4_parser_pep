import logging

from requests import RequestException

from exceptions import ParserFindTagException


REQUEST_EXCEPTION_MESSAGE = 'Возникла ошибка при загрузке страницы {}'


def get_response(session, url, encoding='utf-8'):
    try:
        response = session.get(url)
        response.encoding = encoding
        return response
    except RequestException:
        raise ParserFindTagException(REQUEST_EXCEPTION_MESSAGE).format(url)


def find_tag(soup, tag, attrs=None):
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        error_msg = f'Не найден тег {tag} {attrs}'
        logging.error(error_msg, stack_info=True)
        raise ParserFindTagException(error_msg)
    return searched_tag
