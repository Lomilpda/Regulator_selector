import sqlite3
import re
import numpy as np
import core_script as cs
from math import pi, log, sqrt
'''
Здесь находятся все ф-ци используемые в сore_script
'''
def prepare_list(pure_list):
    '''
    Убирает лишние символы, разбирает на отдельные элементы и трансформирует из <str> в <float>
    :param pure_list:
    :return: final_list
    '''
    pure_list= pure_list[2:] #убираем ('
    pure_list= pure_list[:-3] # убираем ',)
    pure_list=re.split(' ', pure_list)
    i=0
    final_list=[a*0 for a in range(0, len(pure_list))]
    while i < len(pure_list):
        final_list[i]=float(pure_list[i])
        i += 1
    return final_list
def ouput_dict(possible_types, key=0):
    '''
    Выводит в читаемом виде все виды возможных РО
    :param possible_types:
    :param key: True - работа в обычном режиме, False - вывод одного значения РО
    :return:
    '''
    types_po = {0:'специальный', 1 :'односедельный', 2 :'двухседельный', 3 :'заслонковый', 4:'диафрагмовый',
              5 :'шланговый', 6:'триходовой'}
    if key == True:
        match_types = possible_types & types_po.keys() #
        print('Возможные виды РО :')
        i = 0
        for i in match_types:
            print(types_po[i]+';')
            i += 1
    else:
        match_types = types_po[possible_types]
        print('Тип РО: ', match_types)
    return match_types
def all_resistances(number_diafragmas=0,number_bends=0, number_turns=0,
                    number_chokers=0, number_valve_n=0, number_valve_d=0,
                    number_extensions=0, number_narrowing=0,
                    input_r=0, output_r=0, diafragma=0,
                    pipe_bend=0, turn=0, choker=0,
                    valve_normal=0, valve_direct=0, extension=0, narrowing=0 ):
    '''
    Считает сумму всех сопротивлений, далеко не все могут быть заданы,
    так что по умолчанию все они равны 0
    аргументы number_<some_name> указывают на кол-во <some_name> в системе.
    :param input_r: вход в трубу
    :param output_r: выход из трубы
    :param diafragma: диафрагма в прямой трубе
    :param pipe_bend: колено
    :param turn: поворот трубы, плавный
    :param choker: заслонка
    :param valve_normal: вентиль нормальный
    :param valve_direct: вентиль прямоточный
    :param extension: внезапное расширение
    :param narrowing: внезапное сужение
    :return: сумма всех сопротивлений
    '''
    if cs.scheme[4][0] == True:
        input_r=0.5
    if cs.scheme[4][12] == True:
        output_r=0.2
    '''Все вложенные ф-ции должны выполнятся без участия пользователя, так что аргумен'''
    def sum_diafragm():
        diafragm_dict = {0: 7000, 1: 1670, 2: 730, 3: 400,
                         4: 245, 5: 165, 6: 32, 7: 22.3, 8: 13.1,
                         9: 4, 10: 0.97, 11: 0.13}
        values = np.array([0.02, 0.04, 0.06, 0.08, 0.1, 0.12, 0.24, 0.28, 0.34, 0.5, 0.7, 0.9])
        print( cs.scheme[4][1])
        if  cs.scheme[4][1] != 0:
            number = np.searchsorted(values,  cs.scheme[4][1][2], side='right')-1
            value = diafragm_dict[number]
            print('Сопротивление диафрагмы: ', value)
        return value
    ''' Пока что D_y=D_т. Если D_y не задан расчет не выполняется'''
    if  cs.scheme[0] != 0:
        diametr= cs.scheme[0]*1000 #переводим из метров в мм
        print(diametr)
        def sum_bends():
            dict_bends={0:2.2, 1:2, 2:1.6, 3:1.1}
            values=np.array([12.5, 25, 37, 50])
            number=np.searchsorted(values, diametr, side='right')-1
            value=dict_bends[number]
            print('Сопротивление колен(а): ',value)
            return value
        if  cs.scheme[6] !=0:
            def sum_turns():
                dict_turns={0:1.1, 1:0.7, 2:0.63, 3:0.63}
                values=np.array([1, 2, 4, 7])
                number=np.searchsorted(values, (scheme[6]*1000)/diametr, side='right')-1
                value=dict_turns[number]
                print('Сопротивление плавного поворота(ов): ',value)
                return value
                sum_turn = sum_turns()
        else:
            print('Радиус поворота трубы не указан')
        def sum_choker():
            dict_turns={0:0.5, 1:0.25, 2:0.15}
            values=np.array([15, 175, 300])
            number=np.searchsorted(values, diametr, side='right')-1
            value=dict_turns[number]
            print('Сопротивление заслонки(ок)): ',value)
            return value
        def sum_valves_normal():
            dict_turns={0:8, 1:4.9, 2:4, 3:4.1, 4:4.7, 5:5.1, 6:5.5}
            values=np.array([20, 40, 80, 100, 200, 250, 350])
            number=np.searchsorted(values, diametr, side='right')-1
            value=dict_turns[number]
            print('Сопротивление нормального вентиля(ей): ',value)
            return value
        def sum_valves_direct():
            dict_turns={0:1.04, 1:0.79, 2:0.5, 3:0.42, 4:0.36, 5:0.32}
            values=np.array([25, 50, 100, 150, 200, 250])
            number=np.searchsorted(values, diametr, side='right')-1
            value=dict_turns[number]
            print('Сопротивление прямоточного вентиля(ей)',value)
            return value
    else: print('Не указан условный проход D_y')
    sum_ext = 0 # промежуточные переменные, на случай отсутствия нужных значений
    sum_nar = 0
    sum_turn = 0
    if  cs.scheme[4][10][2] and  cs.scheme [4][11][2] !=0:
        def sum_extensions():
            value=( cs.scheme[4][10][2]/(( cs.scheme[4][11][2])-1))**2
            print('Сопротивление внезапного расширения): ',value)
            return value
        def sum_narrowing():
            value=0.5*((1- cs.scheme[4][10][2]/( cs.scheme[4][11][2]))**2)
            print('Сопротивление внезапного сужения): ',value)
            return value
        sum_ext = sum_extensions()
        sum_nar = sum_narrowing()
    else:
        print('Внезапное расширение и сужение отсутствуют')

    #просто суммируем все что есть
    total_sum=number_diafragmas*sum_diafragm()+number_bends*sum_bends()+sum_turn*turn+\
              number_chokers*sum_choker()+number_valve_n*sum_valves_normal()+number_valve_d*sum_valves_direct()+\
              number_extensions*sum_ext+number_narrowing*sum_nar+input_r+output_r
    print(total_sum)
    return total_sum
def prior_choice(temperature, pressure_nominal, delta_p_po):
        possible_types=[] #список, в котором пишутся все возможные типы РО
        if temperature<= -225 or temperature >= 600:
            possible_types.append(0)
        elif pressure_nominal>160:
            possible_types.append(1)
        elif temperature<= 40 and temperature <=80 and pressure_nominal <= 16:
            possible_types.extend([2, 1, 4, 3, 5])
        elif temperature <=150 and pressure_nominal <= 16:
            possible_types.extend([2, 1, 4, 3])
        elif not pressure_nominal > 40:
            if delta_p_po > 16 and temperature <= -50:
                possible_types.extend([2, 1, 3])
            else:
                possible_types.extend([1, 3])
        elif not pressure_nominal > 64:
            possible_types.extend([2, 1])
        elif not delta_p_po > 25:
            possible_types.append(2)
        else:
            possible_types.extend([1, 2, 3, 4, 5, 6])
        return possible_types
def awerage_speed_flow(consumption, diametr, envi, density):
        '''

       :param consumption: максимальный расход, Q_max
        :param diametr: условный диаметр прямых участков, м
        :param enviroment: среда.
        :return: speed: средняя скорость потока
        '''
        print(envi)
        if envi == 0 or envi == 2 or envi == 4: #среда не газ или газ/твердое вещ-во
            speed=(4*consumption)/(pi*(diametr**2)*3600)
        else:
            speed=(4*consumption)/(pi*(diametr**2)*density*3600)
        print('Средняя скорость потока ', speed, ' м/с')
        return speed
def reynolds_k(pipe_form, speed_flow, diametr, cinematic_density):
        '''

        :param pipe_form: форма трубы. True - круглые, False - некруглые
        :param speed_flow: средняя скорость потока
        :param diametr:
        :param cinematic_density: кинематическая вязкость
        :return:
        '''
        if pipe_form == True:
            reynolds = (speed_flow*100*diametr*100)/cinematic_density
        else:
            #De=4F/P и где его брать?
            DE=2 # для проверки
            reynolds =(speed_flow*100*DE*100)/cinematic_density
        print('Критерий Рейнольдса ', reynolds)
        return reynolds
def relatively_roughness (pipe_type, diametr):
        '''
        Расчет относительной шероховатости (4.6)
        :param pipe_type: тип трубы (1-7)
        :param diametr:
        :return:
        '''
        types={0: 0.2, 1: 1.4, 2: 0.2, 3: 0.5, 4: 1, 5: 0.8, 6: 0.1, 7: 0.67}
        roughnes=types[pipe_type]
        print('Шероховатость стенок труб ',roughnes)
        relativ_r=roughnes/(1000*diametr)
        print('Относительная шероховатость', relativ_r)
        return  relativ_r
def hydravlic_friction(reynolds, roughness):
        '''
        :param reynolds:
        :param roughness: относительная шероховатость
        :return:
        '''
        if reynolds>2320:
            friction = (1/(-2*log((roughness/3.7+((6.81/reynolds)**0.9)), 10)))**2
        else:
            friction = 64/ reynolds
        print('Коэффициент гидравлического сопротивления', friction)
        return friction
def losses_straight_lines(friction, density, lenght, speed, diametr):
        '''
        Считает для 1-го участка
        :param friction:
        :param density:
        :param lenght: длина прямых участков трубопровода
        :param speed:
        :param diametr:
        :return:
        '''
        losses=friction*1000*density*((lenght*speed**2)/(2*diametr))
        print('Потери на прямых участках трубопровода, (дельта_P_пр)', losses)
        return losses
def losses_local_res(summ_local_res, density, speed):
        '''

        :param summ_local_res:  общая сумма местных сопротивлений, надо будет посчитать где-то отдельно
        :param density:
        :param speed:
        :return:
        '''
        losses_local = summ_local_res*density*1000*speed**2/2*10**(-6)
        print('Потери в местных сопротивлениях (дельта Р_м)', losses_local)
        print(summ_local_res)
        return losses_local
def extract(temperature, pressure_basic, material): # выбираем P_y
        '''

        :param temperature: data[3][0]
        :param pressure_basic: data[2][0]
        :param material: 1 - steel, 2 - cast_iron
        :return:
        '''
        con = sqlite3.connect('database_all.db')
        '''
        Крайне странное поведение numpy. Вместо списка, np.searchsorted возвращает int64, который SQL упорно не хочет воспринимать
        Пока конвертируем полученное значение в  int, там посмотрим.
        '''
        cur = con.cursor()
        if material == 1:
            power_list = np.array([-70, 200, 300, 400, 480, 520, 600])
            number_row = np.searchsorted(power_list, temperature, side='right') - 1
            number_row = int(number_row)
            cur.execute("SELECT VARIANTS from P_steel_3_2 WHERE ID=?", (number_row,))
            print('Выбор данных из таблицы 3.2')
        elif material == 2:
            power_list = np.array([-30, 120, 200, 300, 350, 400])
            number_row = np.searchsorted(power_list, temperature, side='right')-1
            number_row = int(number_row)
            cur.execute("SELECT VARIANTS from P_max_cast_iron_3_1 WHERE ID=?", (number_row,))
            print('Выбор данных из таблицы 3.1')
        else:
            print("Материал трубы не найден")
        print('Столбец ', number_row+1) # считаем то с 0
        unpacked = (str(cur.fetchone()))
        cur.close()
        unpacked = prepare_list(unpacked)
        print('Значения P_y в столбце ',unpacked)
        column_list=np.array(unpacked)
        column_number=np.searchsorted(column_list, pressure_basic, side='right')
        print('Строка ', column_number+1) # считаем то с 0
        pressure_nominal = unpacked[column_number]
        print('Выбранное P_y', pressure_nominal)
        return pressure_nominal
def hydrostatic_pressure(altitude, density, number_stages, direction):
        i=0
        hydro_pressure = [i*0 for i in range(0, len(direction))] #cоздание списка длиной в кол-во направлений поворотов
        print(number_stages)
        while i < number_stages:
            if direction[i] == True:    # направление вверх от РО
                hydro_pressure[i]=density*altitude[i]*9.8*10**(-6) # 9.8 - g, константа
            else:
                hydro_pressure[i]=-1*density*altitude[i]*9.8*10**(-6) # вниз от РО
            i +=1
        print('Список гидравлических давлений в сис-ме', hydro_pressure)
        return hydro_pressure
def summ_list(first_values, next_values):
            '''
            с помощью reduce считает сумму значений в списке
            :param first_values: начальное значение списка (0, изначальн)
            :param next_values: следующее за ним значение списка
            :return:
            '''
            total_sum=first_values+next_values
            return total_sum
def capacity_max(type_enviroment, discharge_max, difference_pressure_max ,density=0,temperature=0):
    '''
    Для всех типов РО кроме шланговых
    :param type_enviroment: тип среды (0-5)
    :param discharge_max: максимальный расход  Q_max
    :param difference_pressure_max: дельта P_PO
    :param density: плотность
    :param temperature: температура, К
    :return:
    '''
    con = sqlite3.connect('database_all.db')
    cur = con.cursor()
    cur.execute("SELECT CALCULATE FROM CALCULATE_VALUES WHERE NAME='before_ro'")
    before_ro=cur.fetchone()
    cur.execute("SELECT CALCULATE FROM CALCULATE_VALUES WHERE NAME='difference_pressure_max'")
    dif_pres=cur.fetchone()
    cur.close()
    def pressure_after():   #P2
        pressure_aft = cs.pressure[0]-dif_pres[0]
        print('P2', pressure_aft)
        return pressure_aft
    pressure_aft=pressure_after()
    def compression_coefficient():  #коэффициент сжатости K`
        if ((before_ro[0]-pressure_aft)/ before_ro[0]) < 0.08:
            coefficient = 1
        else:
            coefficient = 1 - ((0.46*( before_ro[0]-pressure_aft))/ before_ro[0])
        print ('k сжатости ', coefficient)
        return coefficient
    print(difference_pressure_max,'pressure_max_dif')
    print(0.5*before_ro[0], 'esy')
    if difference_pressure_max < (0.5*before_ro[0]): #описываем расчеты при докритическом режиме
        print('Докритический режим')
        if  cs.flow_rate[3] == True: # проверка на единицы измерения, True - Q_max, m^3/ч, False - G_max, кг/ч
            if type_enviroment == 0:  # жидкость
                capacity = discharge_max*sqrt(density/(difference_pressure_max*10**(-5)))
            elif type_enviroment == 1:  #газ
                capacity = (discharge_max/5.35)*sqrt((density*temperature*compression_coefficient())/(difference_pressure_max)*pressure_after())
            elif type_enviroment == 2: # твердое вещество
                capacity = 0 # пока так, нужно уточнить
        else:   # G_max, кг/ч
            if type_enviroment == 0:
                 capacity = discharge_max/(sqrt(density*difference_pressure_max*10**(-5)))
            elif type_enviroment == 1:
                capacity = (discharge_max/5.35)*sqrt((temperature*compression_coefficient())/(density*difference_pressure_max()*pressure_after()))
            elif type_enviroment == 2: # твердое вещество
                capacity = 0 # пока так, нужно уточнить
            elif type_enviroment == 3: # водяной пар
                capacity = 10*(discharge_max/sqrt(cs.pressure[6]*difference_pressure_max))
    else:   #при критическом режиме
        print('Критический режим работы')
        if type_enviroment !=0: # для жидкости нет другой ф-лы
            if cs.flow_rate[3] == True: # проверка на единицы измерения, True - Q_max, m^3/ч, False - G_max, кг/ч
                if type_enviroment == 1:  #газ
                    capacity = (discharge_max/(2680*before_ro[0]))*sqrt(density*temperature*compression_coefficient())
                elif type_enviroment == 2: # твердое вещество
                    capacity = 0 # пока так, нужно уточнить
                else:
                    print("Невозможно посчитать значение расхода")
            else:   # G_max, кг/ч
                if type_enviroment == 1:
                    capacity = (discharge_max/(2680*before_ro))*sqrt((temperature*compression_coefficient())/density)
                elif type_enviroment == 2: # твердое вещество
                    capacity = 0 # пока так, нужно уточнить
                elif type_enviroment == 3: # водяной пар
                    capacity = discharge_max/((sqrt( cs.pressure[5]*difference_pressure_max))*74)
                else:
                    print("Невозможно посчитать значение расхода")
        else:
            if cs.flow_rate[3] == True:
                capacity = discharge_max*sqrt(density/(difference_pressure_max*10**(-5)))
            else:
                capacity = discharge_max/(sqrt(density*difference_pressure_max*10**(-5)))
    capacity=capacity*0.001 #костыль, пока не выясню что за цирк с конями написан в методе
    return capacity
def diametr_nominal_type(type_ro, pressure_nominal, capacity_nominal):
    '''
    Выбор условного диаметра (D_y)
    :param type_ro: тип РО, выбранный изначально
    :param pressure_nominal: условное давление
    :param capacity_nominal: условный расход
    :return:
    '''
    diametr_nominal_list = [15, 20, 25, 40, 50, 65, 80, 100, 125, 150, 200, 250,
                                     300, 400, 500, 600, 700, 800, 900, 1000]
    con = sqlite3.connect('database_all.db')
    cur = con.cursor()
    sql = "SELECT DATA FROM ? WHERE P_y =?"
    dict_associate = {1:'SINGLE_SEATED', 2:'TWO_SEATED', 3:'CHOKER',
                      4: 'DIAFRAFM', 5:'HOSE', 6:'THREE_WAY'}
    number_type=dict_associate[type_ro]
    try:
        cur.execute(sql, number_type, pressure_nominal)
    except sqlite3.DatabaseError as error:
        print('Не удалось взять данные из БД ', error)
    list_capacitys = cur.fetchone()
    def number_r(list_capacitys):
        list = prepare_list(list_capacitys)
        list_capacitys = np.array([list])
        number_row = np.searchsorted(list_capacitys, capacity_nominal, side='right')
        print(number_row)
        return number_row
    number_row=number_r(list_capacitys)
    if type_ro == 3:    # choker
        number_row = number_row+4
    diametr_nominal = diametr_nominal_list[number_row]
    condition = ((cs.scheme[0]*0.25) <= diametr_nominal and diametr_nominal <= cs.scheme[0])  #заданное условие
    if condition != True:
        while condition != True:
            i=1
            try:
                cur.execute(sql, dict_associate[type_ro+i], pressure_nominal)
            except sqlite3.DatabaseError as error:
                print('Не удалось взять данные из БД ', error)
            list_capacitys = cur.fetchone()
            number_row=number_r(list_capacitys)
            i+=1
        diametr_nominal = diametr_nominal_list[number_row]
    print('Предварительно выбранный номинальный диаметр ', diametr_nominal)
    return diametr_nominal


