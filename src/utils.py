from bs4 import BeautifulSoup
from requests import RequestException
from exceptions import ParserFindTagException


REQUEST_EXCEPTION_MESSAGE = 'Возникла ошибка при загрузке страницы {}\n{}'
TAG_NOT_FOUND_MESSAGE = 'Не найден тег {} {}'


def get_response(session, url, encoding='utf-8'):
    try:
        response = session.get(url)
        response.encoding = encoding
        return response
    except RequestException as e:
        error_message = REQUEST_EXCEPTION_MESSAGE.format(url, str(e))
        raise RequestException(error_message) from e


def find_tag(soup, tag, attrs=None):
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        raise ParserFindTagException(TAG_NOT_FOUND_MESSAGE.format(tag, attrs))
    return searched_tag


def get_soup(session, url, parser='lxml'):
    response = get_response(session, url)
    return BeautifulSoup(response.text, parser)
