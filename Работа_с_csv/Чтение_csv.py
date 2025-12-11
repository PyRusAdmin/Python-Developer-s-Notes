import csv

"""
['Имя', 'Возраст', 'Город']
['Алиса', '30', 'Москва']
['Боб', '25', 'Санкт-Петербург']
"""

with open('file.csv', encoding='utf-8') as f:
    reader = csv.reader(f)
    for row in reader:
        print(row)  # каждая строка — список значений

"""
{'Имя': 'Алиса', 'Возраст': '30', 'Город': 'Москва'}
{'Имя': 'Боб', 'Возраст': '25', 'Город': 'Санкт-Петербург'}
"""
with open('file.csv', encoding=' utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row)  # каждая строка — словарь {заголовок: значение}
