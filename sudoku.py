import os
from collections import Counter
from time import sleep
from random import shuffle, randint
from copy import deepcopy
import pickle


class Grid:
    """Класс, описывающий сетку игрового поля"""
    def __init__(self, start_grid=None, num_drop_cells=46):
        """
        :param start_grid: list - готовое игровое поле
        :num_drop_cells: количество клеток, которые будут пустыми
        """
        if start_grid is None:
            self._playing_field = [
                [(x + 3 * t + t // 3) % 9 + 1 for x in range(9)]
                for t in range(9)
            ]
            self._shuffle_grid()
            self._drop_cells(num_drop_cells)
        else:
            self._playing_field = deepcopy(start_grid)
        self._set_delay = True
        self._delay = 10**-2
        self._grid_mask = [
            [x != 0 for x in row] for row in self._playing_field
            ]
        self._colorize = True

    @property
    def grid(self):
        return self._playing_field

    @property
    def colorize(self):
        return self._colorize

    @colorize.setter
    def colorize(self, val):
        if (type(val) == bool):
            self._colorize = val
        else:
            raise TypeError

    def _transpose(self):
        """Функция транспонирования сетки"""
        self._playing_field = [*map(list, zip(*self._playing_field))]

    def _swap_rows_area(self):
        """
        Функция перестановка двух зон, состоящих из 3 строк.
        В сетке 3 таких зоны: 1-3, 4-6, 7-9 строки включительно.
        """
        indx = [*range(0, 3)]
        array_slices = [
            self._playing_field[3 * i: 3 * (i + 1)] for i in range(3)
        ]
        self._playing_field = []

        shuffle(indx)
        for i in range(3):
            self._playing_field += array_slices[indx[i]]

    def _swap_cols_area(self):
        """
        Функция перестановки двух зон, состоящих из 3 столбцоа.
        В сетке 3 таких зоны: 1-3, 4-6, 7-9 столбцы включительно.
        """
        self._transpose()
        self._swap_rows_area()
        self._transpose()

    def _swap_rows(self):
        """Функция перестановки 2 случайных строк"""
        area = randint(0, 2)
        indx = [*range(3)]
        shuffle(indx)

        array_slices = [
            self._playing_field[3 * i: 3 * (i + 1)] for i in range(3)
        ]

        arr = []
        for i in range(3):
            arr += [array_slices[area][indx[i]]]

        array_slices[area] = arr
        self._playing_field = []
        for i in range(3):
            self._playing_field += array_slices[i]

    def _swap_cols(self):
        """Функция перестановки 2 случайных столбцов"""
        self._transpose()
        self._swap_rows()
        self._transpose()

    def _shuffle_grid(self, iter_num=15):
        """
        Функция для случайного перемешивания строк, стобцов и зон
        :param iter_num: количество итераций перемешивания
        """
        func = [
            self._transpose,
            self._swap_rows,
            self._swap_rows_area,
            self._swap_cols,
            self._swap_cols_area
        ]

        for i in range(iter_num):
            func[randint(0, len(func) - 1)]()

    def _drop_cells(self, n):
        """
        Функция для удаления клеток
        :param n: количество клеток, которые будут удалены
        """
        if (n > 66):
            raise ValueError('Слишком мало заполненных клеток!')
        if (n < 1):
            raise ValueError('Все клетки заполнены!')
        solver = SudokuSolver()

        num_drop_cells = 0
        while (num_drop_cells < n):
            i, j = randint(0, 8), randint(0, 8)
            if (self._playing_field[i][j] == 0):
                continue

            t = self._playing_field[i][j]
            self._playing_field[i][j] = 0

            if not solver.get_solution(Grid(self._playing_field)):
                self._playing_field[i][j] = t
            else:
                num_drop_cells += 1

    @property
    def delay(self):
        return self._delay

    @delay.setter
    def delay(self, value):
        if (type(value) == str):
            if value in set(('1', '2', '3')):
                if (value == '1'):
                    self._delay = 10**-3
                elif (value == '2'):
                    self._delay = 10**-2
                else:
                    self._delay = 10**-1
            else:
                raise ValueError
        else:
            raise TypeError

    @property
    def set_delay(self):
        return self._set_delay

    @set_delay.setter
    def set_delay(self, value):
        if (type(value) == bool):
            self._set_delay = value
        else:
            raise TypeError

    @staticmethod
    def _cls():
        "Функция очистки консоли"
        os.system('cls' if os.name == 'nt' else 'clear')

    def show(self, clr_screen=True):
        """
        Функция, которая выводит сетку в консоль
        :param clr_screen: bool - показывает, необходимо ли очищать экран
        """
        if self._set_delay:
            sleep(self._delay)

        if clr_screen:
            Grid._cls()

        for i in range(len(self._playing_field)):
            if (i % 3 == 0):
                print('=' * 41)
            else:
                print('-' * 41)

            st = '|'
            for j in range(9):
                if (j % 3 == 0):
                    st += '|'

                # когда элемент в ячейке отсутствует
                if (self._playing_field[i][j] == 0):
                    st += '   |'
                else:
                    if (self._colorize and self._grid_mask[i][j]):
                        st += f' \033[31m{self._playing_field[i][j]}\033[0m |'
                    else:
                        st += f' {self._playing_field[i][j]} |'
            st += '|'

            print(st)
        print('=' * 41)

    @staticmethod
    def _check(counter):
        """
        Функция, которая проверяет условие:
        каждое число должно появиться не более одного раза
        :param counter: Counter - счетчик поличества появлений каждой цифры
        :return: True - если условие выполняется, иначе False
        """
        if not all([counter[key] == 1 for key in counter.keys()]):
            return False
        return True

    @staticmethod
    def _get_num_of_square(i, j):
        """"
        Функция, которая вычисляет номер квадрата 3х3
        (слева направо сверху вниз 9 квадратов 3х3)
        по значению строки и столбца
        :param i: номер строки
        :param j: номер столбца
        """
        return (i // 3) * 3 + j // 3

    def _check_row(self, i):
        """
        Функция, которая проверяет условие:
        в строке каждая цифра может появляться не более одного раза
        :param i: номер строки
        :return: bool - True, если условие выполняется, иначе False
        """
        counter = Counter(self._playing_field[i])
        del counter[0]
        if not Grid._check(counter):
            return False
        return True

    def _check_col(self, j):
        """
        Функция, которая проверяет условие:
        в столбце каждая цифра может появляться не более одного раза
        :param j: номер строки
        :return: bool - True, если условие выполняется, иначе False
        """
        counter = Counter([
            val for val in map(
                lambda x: x[j],
                self._playing_field
                )
            ])
        del counter[0]
        if not Grid._check(counter):
            return False
        return True

    def _check_square(self, num):
        """
        Функция, которая проверяет условие:
        в квадрате 3х3 каждая цифра может появляться не более одного раза
        :param num: номер квадрата (слева направо сверху вниз 9 квадратов 3х3)
        :return: bool - True, если условие выполняется, иначе False
        """
        val = (3 * (num + 1))
        ind_right = val % 9 if val % 9 != 0 else val
        counter = Counter(sum([x for x in map(
            lambda x: x[(3 * num) % 9: ind_right],
            self._playing_field[3 * (num // 3):3 + 3 * (num // 3)]
        )], []))
        del counter[0]
        if not Grid._check(counter):
            return False
        return True

    def check_grid(self):
        """
        Функция, которая проверяет все правила игры:
        1. В каждой строке каждая цифра встречается не более одного раза
        2. В каждом столбце каждая цифра встречается не более одного раза
        3. В каждом квадрате каждая цифра встречается не более одного раза
           (слева направо сверху вниз 9 квадратов 3х3)
        4. Отсутствуют незаполненные клетки (отсутствуют нули в сетке)
        """
        set_of_num = set()

        for i in range(9):
            # проверка строк
            if not self._check_row(i):
                return False

            # проверка столбцов
            if not self._check_col(i):
                return False

            # проверка квадратов 3х3
            if not self._check_square(i):
                return False

            set_of_num |= set(self._playing_field[i])

        # проверка на наличие нулей
        if 0 in set_of_num:
            return False

        return True

    def fill_cell(self, i, j, number):
        """
        Функция, которая заполняет ячейку,
        если значение удовлетворяет всем правилам игры
        :param i: номер строки
        :param j: номер столбца
        :param number: значение, которым может быть
        заполнена ячейка (цифра от 1 до 9)
        :return: bool - True, если number соответствовало правилам
        и было присовено ячейке, иначе False
        """
        if (self._grid_mask[i][j]):
            return False

        t = self._playing_field[i][j]
        self._playing_field[i][j] = number
        if all((self._check_row(i),
                self._check_col(j),
                self._check_square(Grid._get_num_of_square(i, j)))):
            return True
        else:
            self._playing_field[i][j] = t
            return False


class SudokuSolver:
    """Клас для поиска решения Судоку компьютером методом грубой силы"""
    def __init__(self):
        self._print_steps = False

    def _set_print_steps(self, val):
        if (type(val) == bool):
            self._print_steps = val
        else:
            raise TypeError

    print_steps = property(fset=_set_print_steps)
    del _set_print_steps

    @staticmethod
    def _get_zero_index(grid):
        """
        Функция поиска первого нулевого элемента (незаполненной ячейки)
        :param grid: Grid - сетка игрового поля
        return: индекс строки и стобца первого нулевого элемента
        (слева направо сверху вниз), или (-1, -1) если нулевых элементов нет
        """
        for i in range(len(grid.grid)):
            for j in range(len(grid.grid[i])):
                if (grid.grid[i][j] == 0):
                    return i, j
        return -1, -1

    def get_solution(self, grid):
        """
        Функция рекурсивного поиска решения Судоку
        :param grid: Grid - сетка игрового поля
        :return: bool - True, если решение найдено, иначе False
        """
        zero = SudokuSolver._get_zero_index(grid)
        if (zero == (-1, -1)):
            if grid.check_grid():
                return True
            else:
                return False

        for number in range(1, 10):
            if grid.fill_cell(zero[0], zero[1], number):
                if self._print_steps:
                    grid.show()
                    print(f'\n({zero[0] + 1}, {zero[1] + 1}, {number})')

                if self.get_solution(grid):
                    return True
        grid.grid[zero[0]][zero[1]] = 0
        return False


class SudokuGame:
    """Класс, описывающий процесс игры в Судоку"""
    def start_game(self):
        """Функция запуска игры"""

        SudokuGame._cls()
        print('Добро пожаловаь в Судоку!')
        SudokuGame._print_rules()
        if (SudokuGame._game_menu(['Начать игру', 'Выйти']) == '1'):
            game_mode = SudokuGame._game_menu([
                'Режим игры для пользователя',
                'Режим игры для компьютера'
            ])
            if (game_mode == '1'):
                self._user_game_mode()
            else:
                SudokuGame._computer_game_mode()

    @staticmethod
    def _game_menu(menu_items):
        """
        Функция, которая выводит меню
        :param menu_items: list - элементы меню
        """
        print('\nМеню:')
        for i in range(len(menu_items)):
            print(str(i + 1) + '. ' + menu_items[i] + '')
        while True:
            answ = input('(Выберите пункт меню - цифра ' +
                         f'от 1 до {len(menu_items)})\n')
            if answ in set(map(str, range(1, len(menu_items) + 1))):
                return answ
            else:
                print('Введено некорректное значение!')

    @staticmethod
    def _print_rules():
        """Функция, которая выводит правила игры"""
        print()
        print('\n'.join([
            'Краткое напоминание основных правил игры:',
            '1. Цифра может появиться только один раз в каждой строчке',
            '2. Цифра может появиться только один раз в каждом столбике',
            '3. Цифра может появиться только один раз в каждом квадрате',
            '(Квадрат со сторонами 3х3, на игровом поле',
            'выделяется широкой границей)'
        ]))

    @staticmethod
    def _cls():
        """Функция очистки консоли"""
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def _save_game(grid):
        """
        Функция для сохранения игры
        :param grid: Grid - сетка игрового поля
        """
        with open('game.pkl', 'wb+') as file:
            pickle.dump(grid, file)

    @staticmethod
    def _load_game():
        """
        Функция для загрузки последнего сохранения
        :return: Grid - сохраненная сетка игрового поля
        """
        try:
            with open('game.pkl', 'rb') as file:
                return pickle.load(file)
        except FileNotFoundError:
            return None

    def _user_game_mode(self):
        """Функция, реализующая режим игры для пользователя"""

        SudokuGame._cls()

        print('Режим игры для пользователя')
        if (SudokuGame._game_menu([
            'Начать новую игру',
            'Загрузить последнюю игру'
        ]) == '1'):
            grid = Grid(num_drop_cells=81 - SudokuGame._get_num_of_cells())
            grid.show()
        else:
            grid = self._load_game()
            if not grid:
                print('Нет сохраненной игры! Начата новая игра!')
                grid = Grid(num_drop_cells=81 - SudokuGame._get_num_of_cells())
            grid.show()

        while not grid.check_grid():
            answ = input("\nВведите 3 цифры от 1 до 9 через пробел: "
                         "Строка, Колонка, Число\n"
                         "(Чтобы открыть меню, введите 'menu')\n")
            if(answ.isalpha() and len(answ) == 4):
                if (answ == 'menu'):
                    menu_item = SudokuGame._game_menu([
                        'Продолжить',
                        'Правила',
                        'Сохранить игру',
                        'Включить/Выключить раскраску исходных элементов',
                        'Выйти'
                    ])

                    if (menu_item == '1'):
                        continue
                    elif(menu_item == '2'):
                        SudokuGame._print_rules()
                    elif (menu_item == '3'):
                        SudokuGame._save_game(grid)
                        print('Игра сохранена!')
                    elif (menu_item == '4'):
                        grid.colorize = not grid.colorize
                        grid.show()
                    else:
                        break

                    continue

            answ = answ.split()
            if (len(answ) != 3 or not all(map(str.isdigit, answ))):
                print('Введите 3 ЦИФРЫ!')
                continue
            else:
                answ = [*map(int, answ)]

                if not all(map(lambda x: 1 <= x <= 9, answ)):
                    print('Введите 3 цифры от 1 до 9!')
                    continue

                answ[0] -= 1
                answ[1] -= 1

            if not grid.fill_cell(*answ):
                print(
                    'Введенные данные не соответствуют правилам игры!\n'
                    'Попробуйте еще раз.'
                )
                continue

            grid.show()
        else:
            print('Победа!')

    @staticmethod
    def _computer_game_mode():
        """Функция, реализующая режим игры для компьютера"""

        def configure_print(grid):
            """
            Функция настройки вывода сетки игрового поля
            :param grid: Grid - сетка игрового поля
            """

            def check_answer(question):
                """
                Функция получения ответа от пользователя
                :param quetion: str - вопрос для пользователя
                return: bool - True, если ответ "Да", иначе False
                """
                for i in range(3):
                    answ = str.lower(input(question + '(Y/n)\n'))
                    if (answ == 'y') or (answ == 'n'):
                        break
                    print('Введено некорректное значение! '
                          'Введите "Y" или "n".')
                else:
                    return False

                if (answ == 'y'):
                    return True
                else:
                    return False

            if check_answer('Установить задержку отображения игрового поля?'):
                grid.set_delay = True
            else:
                grid.set_delay = False

            if grid.set_delay:
                if check_answer('Изменить величину задержки?'):
                    for i in range(3):
                        answ = input('Выберите величину задержки(от 1 до 3): '
                                     '1 - min, 2 - mean, 3 - max\n')
                        if (answ in set(('1', '2', '3'))):
                            grid.delay = answ
                            break
                        else:
                            print('Введено некорректное значение! '
                                  'Введите цифру от 1 до 3.')
                    else:
                        grid.delay = '1'

        SudokuGame._cls()
        print('Режим игры для компьютера')

        solver = SudokuSolver()
        solver.print_steps = True
        grid = Grid(num_drop_cells=81 - SudokuGame._get_num_of_cells())
        configure_print(grid)
        solver.get_solution(grid)

    @staticmethod
    def _get_num_of_cells():
        """
        Функция, которая получает от пользователя количество
        изначально заполненных клеточек
        :return: количество введенных пользователем клеточек,
        или 35 (по умолчанию), если пользователь ввел 3 раза
        некорректное значение
        """
        for i in range(3):
            answ = input('Введите количество заполненных '
                         'клеток на игровом поле (15 < n < 81):\n')
            if (answ.isdigit()):
                if (15 < int(answ) < 81):
                    return int(answ)
                else:
                    print('Введено некорректное число!')
            else:
                print('Введите число!')
        return 35


game = SudokuGame()
game.start_game()
