import logging
import re
from collections import defaultdict
from urllib.parse import urljoin

import requests_cache
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, DOWNLOADS, MAIN_DOC_URL, MAIN_PEP_URL
from exceptions import VersionListNotFoundException
from outputs import control_output
from utils import find_tag, get_soup


ERROR_GETTING_SOUP_URL = "Ошибка при получении супа для URL: {}"
ARCHIVE_DOWNLOADED = 'Архив был загружен и сохранён: {}'
PARSER_STARTED = 'Парсер запущен!'
COMMAND_LINE_ARGS = 'Аргументы командной строки: {}'
PARSER_COMPLETED = 'Парсер завершил работу.'
ERROR_MESSAGE = 'Произошла ошибка: {}'
VERSION_LIST_NOT_FOUND_MESSAGE = 'Не найден список c версиями Python'
ERROR_MESSAGE = 'Произошла ошибка: {}'


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    soup = get_soup(session, whats_new_url)
    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_with_ul.find_all('li',
                                              attrs={'class': 'toctree-l1'})
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    logs = []
    for section in tqdm(sections_by_python):
        version_a_tag = section.find('a')
        version_link = urljoin(whats_new_url, version_a_tag['href'])
        try:
            soup = get_soup(session, version_link)
            results.append((version_link,
                            find_tag(soup, 'h1').text,
                            find_tag(soup, 'dl').text.replace('\n', ' ')))
        except ConnectionError:
            logs.append(ERROR_GETTING_SOUP_URL.format(version_link))
    list(map(logging.error, logs))
    return results


def latest_versions(session):
    soup = get_soup(session, MAIN_DOC_URL)
    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise VersionListNotFoundException(VERSION_LIST_NOT_FOUND_MESSAGE)
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append(
            (a_tag['href'], version, status)
        )
    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    soup = get_soup(session, downloads_url)
    main_tag = find_tag(soup, 'div', attrs={'role': 'main'})
    table_tag = find_tag(main_tag, 'table', attrs={'class': 'docutils'})
    pdf_a4_tag = table_tag.find('a', {'href': re.compile(r'.+pdf-a4\.zip$')})
    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)
    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / DOWNLOADS
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    response = session.get(archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(ARCHIVE_DOWNLOADED.format(archive_path))


def pep(session):
    soup = get_soup(session, MAIN_PEP_URL)
    num_index = find_tag(soup, 'section', {'id': 'numerical-index'})
    rows = num_index.find_all('tr')
    pep_count = defaultdict(int)
    logs = []
    for row in tqdm(rows[1:]):
        a_tag = find_tag(row, 'a')
        href = a_tag['href']
        pep_link = urljoin(MAIN_PEP_URL, href)
        try:
            soup = get_soup(session, pep_link)
            dl = find_tag(soup, 'dl')
            dt_tags = dl.find_all('dt')
            for dt in dt_tags:
                if dt.text == 'Status:':
                    dt_status = dt
                    break
            pep_status = dt_status.find_next_sibling('dd').string
            pep_count[pep_status] += 1
        except ConnectionError:
            logs.append(ERROR_GETTING_SOUP_URL.format(pep_link))
    list(map(logging.error, logs))
    return [
        ('Статус', 'Количество'),
        *pep_count.items(),
        ('Всего', sum(pep_count.values())),
    ]


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    try:
        configure_logging()
        logging.info(PARSER_STARTED)

        arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
        args = arg_parser.parse_args()
        logging.info(COMMAND_LINE_ARGS.format(args))

        session = requests_cache.CachedSession()
        if args.clear_cache:
            session.cache.clear()

        parser_mode = args.mode
        results = MODE_TO_FUNCTION[parser_mode](session)

        if results is not None:
            control_output(results, args)
        logging.info(PARSER_COMPLETED)
    except Exception as e:
        logging.error(ERROR_MESSAGE.format(str(e)))


if __name__ == '__main__':
    main()
