# Проект парсинга pep
### Автор 
- [Ильин Данила](https://github.com/RH1532)
### Техно-стек 
Python, BeautifulSoup, argparse, requests, prettytable
### Команды развертывания
Клонировать репозиторий и перейти в директорию проекта:
```bash
git clone https://github.com/RH1532/bs4_parser_pep.git
```
Cоздать и активировать виртуальное окружение:
```bash
python -m venv venv
```
```bash
source venv/Scripts/activate
```
Установить зависимости из файла requirements.txt:
```bash
pip install -r requirements.txt
```
### Команды запуска
- whats-new   
```
python main.py whats-new
```
- latest_versions
```
python main.py latest-versions
```
- download   
```
python main.py download
```
- pep
```
python main.py pep
```
### Доступ к справке
Список комманд
```
python main.py -h
```