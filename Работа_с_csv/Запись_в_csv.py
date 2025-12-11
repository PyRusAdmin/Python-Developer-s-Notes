import csv

data = [
    ['Имя', 'Возраст', 'Город'],
    ['Алиса', 30, 'Москва'],
    ['Боб', 25, 'Санкт-Петербург']
]

with open('file.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerows(data)