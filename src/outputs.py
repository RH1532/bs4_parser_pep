import csv
import datetime as dt
import logging

from prettytable import PrettyTable

from constants import BASE_DIR, DATETIME_FORMAT


FILE_SAVED_MESSAGE = 'Файл с результатами был сохранён: {}'


def control_output(results, cli_args):
    output_functions = {
        'pretty': pretty_output,
        'file': file_output,
    }
    selected_output = cli_args.output
    output_function = output_functions.get(selected_output, default_output)
    output_function(results, cli_args)


def default_output(results, cli_args):
    for row in results:
        print(*row)


def pretty_output(results, cli_args):
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)


def file_output(results, cli_args):
    results_dir = BASE_DIR / 'results'
    results_dir.mkdir(exist_ok=True)
    parser_mode = cli_args.mode
    now = dt.datetime.now()
    file_name = f'{parser_mode}_{now.strftime(DATETIME_FORMAT)}.csv'
    file_path = results_dir / file_name
    with open(file_path, 'w', encoding='utf-8') as f:
        csv.writer(f, dialect=csv.unix_dialect).writerows(results)
    logging.info(FILE_SAVED_MESSAGE.format(file_path))
