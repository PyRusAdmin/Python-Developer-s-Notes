# -*- coding: utf-8 -*-
from multiprocessing import Process
import time
import os


def eat_ram(mb: int):
    """Потребляет указанное количество МБ памяти без нагрузки на CPU"""
    data = bytearray(mb * 1024 * 1024)  # Выделение памяти
    print(f"PID {os.getpid()}: выделено {mb} МБ RAM")
    time.sleep(3600)  # Удерживаем память 1 час (без нагрузки на CPU)


if __name__ == '__main__':
    processes = []
    mb_per_process = 50  # МБ на процесс
    number_processes = 10  # Количество процессов

    # Запускаем 4 процесса → ~2 ГБ RAM
    for i in range(number_processes):
        p = Process(target=eat_ram, args=(mb_per_process,))
        p.start()
        processes.append(p)

    # Не вызываем join() — процессы работают в фоне
    print(f"\nЗапущено {len(processes)} процессов, удерживающих память...")
    print("Нажмите Ctrl+C для завершения")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nЗавершаем процессы...")
        for p in processes:
            p.terminate()
        for p in processes:
            p.join()
