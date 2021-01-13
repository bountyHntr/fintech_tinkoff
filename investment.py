import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from copy import deepcopy


df = pd.read_csv('data.csv')
df.drop(columns=df.columns[0], inplace=True)

# логарифмируем цену, чтобы изменение цены вычислять в процентах
# df.price[y] / df.price[x] = np.exp(log_price[y] - log_price[x])
log_price = np.log(df.price)

# находим точки максимума и минимума
x_min = []
x_max = []
x = []
N = 4000
for i in range(len(df.price) // N):
    x_max.append(N * i + log_price[N * i:N * (i + 1)].argmax())
    x_min.append(N * i + log_price[N * i:N * (i + 1)].argmin())
    for k in sorted([x_max[-1], x_min[-1]]):
        x.append(k)

# выбираем среди подряд идущих максимумов (минимумов)
# одну максимальную (минимальную)
for i in range(len(x) - 1):
    if (x[i] in x_max and x[i + 1] in x_max):
        if (log_price[x[i]] < log_price[x[i + 1]]):
            x_max.remove(x[i])
        else:
            x_max.remove(x[i + 1])

    if (x[i] in x_min and x[i + 1] in x_min):
        if (log_price[x[i]] < log_price[x[i + 1]]):
            x_min.remove(x[i + 1])
        else:
            x_min.remove(x[i])

x_min = x_min[:min(len(x_min), len(x_max))]
x_max = x_max[:min(len(x_min), len(x_max))]

X_min = deepcopy(x_min)
X_max = deepcopy(x_max)


def get_min_dif(price=log_price, x_max=X_max, x_min=X_min):
    """
    Функция, которая находит пару (максимум; минимум) с наимаеньшей
    разностью цен покупки и продажи
    :param price: pd.Series - массив логарифма цен на акцию за все время
    :param x_max: list - массив точек максимума
    :param x_min: list - массив точек минимума
    :return: int, int - индекс для пары точек, с наимаеньшей разностью
    между максимумом и минимумом, количество оставшихся точек
    """
    dif = []

    for i in range(len(x_max)):
        dif.append([log_price[x_max[i]] - log_price[x_min[i]], i])

    return min(dif, key=lambda x: x[0])[1], len(dif)


def get_nearest(price, x_min, i):
    """
    Функция, которая находит ближайшую по точке
    минимума пару (максимум; минимум)
    :param price: pd.Series - массив логарифма цен на акцию за все время
    :param x_min: list - массив точек минимума
    :param i:int - индекс текущей точки
    :return: индекс ближайшей точки
    """
    # выбираем ближайшее по x_min и штрафуем за изменение высоты
    dist_right = abs(x_min[i] - x_min[i + 1])
    dist_right += 10**5 * abs(price[x_min[i]] - price[x_min[i + 1]])
    dist_left = abs(x_min[i] - x_min[i - 1])
    dist_left += 10**5 * abs(price[x_min[i]] - price[x_min[i - 1]])

    if dist_right < dist_left:
        return i + 1
    else:
        return i - 1


def get_best(x, i, i_alt, func):
    """
    Функция, которая выбирает лучшую из двух точек
    :param x: list - массив, точки которого сравниваются
    :param i: int индекс текущей точки
    :param i_alt: индекс (альтернативной) точки, с которой сравниваем текущую
    :param func: int, int -> bool функция, сравнивающая 2 точки
    :return: индекс лучшей точки
    """
    if func(x[i], x[i_alt]):
        return i
    else:
        return i_alt


while True:
    k = input('Введите количество транзакций! (k > 0)\n')
    if k.isdigit():
        k = int(k)
        if (k > 0):
            break
        else:
            print('Введите число > 0')
    else:
        print('Введите ЧИСЛО!')

diff = get_min_dif()

while diff[1] > k:

    indx = diff[0]

    # выбираем ближайшую точку, обрабатываем крайние точки
    if (indx == 0):
        x_nearest = indx + 1
    elif(indx == len(X_max) - 1):
        x_nearest = indx - 1
    else:
        x_nearest = get_nearest(log_price, X_min, indx)

    ind_min_best = get_best(
        X_min, indx, x_nearest,
        lambda x, x_alt: log_price[x] < log_price[x_alt]
    )
    x_min_best = X_min[ind_min_best]

    # удаляем худшую из 2 точек: текущей и альтернативной ближайшей
    if (x_nearest < indx and ind_min_best == indx):
        X_min.pop(indx)
        X_max.pop(indx)
    else:
        if (ind_min_best == indx):
            X_min.pop(x_nearest)
        else:
            X_min.pop(indx)

        if (X_max[indx] > x_min_best and X_max[x_nearest] > x_min_best):

            if (indx == get_best(
                    X_max, indx, x_nearest,
                    lambda x, x_alt: log_price[x] > log_price[x_alt])):
                X_max.pop(x_nearest)
            else:
                X_max.pop(indx)
        elif (X_max[x_nearest] > x_min_best):
            X_max.pop(indx)
        else:
            X_max.pop(x_nearest)

    diff = get_min_dif()

while True:
    capital = input('Введите размер капитала (>=2000)\n')
    if capital.isdigit():
        capital = int(capital)
        if (capital >= 2000):
            break
        else:
            print('Капитал слишком маленький! Введите число больше 2000!')
    else:
        print('Введите ЧИСЛО!')


def get_date_time(int_date_time):
    """
    Функция, которая преобразует дату в формат DD.MM.YYYY
    или время в формат HH.MM.SS
    """
    return ("{:02}".format(int_date_time // 10**4) + "."
            + "{:02}".format(int_date_time // 100 % 100) + "."
            + "{:02}".format(int_date_time % 100))


def join_date_time(ind):
    "Функция, которая объединяет дату и время в одну строку"
    return get_date_time(df.date[ind]) + " " + get_date_time(df.time[ind])


for i in range(k):
    num_stock = capital // df.price[X_min[i]]

    print('Покупка акций '
          + join_date_time(X_min[i]) + " "
          + f'в количестве {num_stock}.')
    print('Стоимость акций в портфеле: '
          f'{round(num_stock * df.price[X_min[i]], 2)}')

    # выводим промежуточные состояния портфеля
    for j in range(X_min[i] + 1, X_max[i]):
        print('Стоимость акций в портфеле '
              + join_date_time(j) + ": "
              f'{round(num_stock * df.price[j], 2)}')

    print('Продажа акций '
          + join_date_time(X_max[i]) + " "
          + f'в количестве {num_stock}.')

    capital = round(capital - num_stock * df.price[X_min[i]]
                    + num_stock * df.price[X_max[i]], 2)
    print(f'Капитал: {capital}')

print(f'Итоговый размер капитала: {capital}')
