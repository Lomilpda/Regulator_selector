import numpy as np
import random
import pickle
from math import *
import sqlite3
import re
import add_function as af
import math
from functools import reduce
#Грузим значения пользователя. Для удобства раскидываем данные по тематическим кортежам
out_userdata = open('user_data.pkl', 'rb')
data = pickle.load(out_userdata)
out_userdata.close()
flow_rate=data[0]
enviroment = data[1]
pressure = data[2]
temperature = data[3]
scheme = data[4]
material_pipe = data[5] # костыль, material pipe нужен при любом расчете
scheme_before = data[6]
# Подключаем БД
if __name__ == '__main__': # Для удобства. Если скрипт вызван как модуль, то в нем будут только обработанные заданые значения
    #Начинаем расчет. 3.1
    def delta_P_change (x, y):
        '''
        x,y - виды давлений, выбранные из условия
        :param x:
        :param y:
        :return:
        '''
        p_po = x-y
        return p_po
    if pressure[2] and pressure[6] != 0:  # считается примерное значение, гидравлический расчет все равно делать надо
        difference_pressure=delta_P_change(pressure[2], pressure[6])
    elif pressure[0] and pressure[1] != 0:    # если есть P1 и P2
        difference_pressure=delta_P_change(pressure[0], pressure[1])
    else:
        print("Не хватает данных для расчета дельта_P_PO")
    print('дельта_P_PO', difference_pressure)
    #Выбираем P_y
    pressure_nominal = af.extract(data[3][0], data[2][0], data[5])
    '''
    Проводим предварительный выбор конструктивного типа РО
    '''
    possible_types = []
    possible_types = af.prior_choice(data[3][0], pressure_nominal, difference_pressure) # список всех возможных типов РО
    match_types=af.ouput_dict(possible_types, True)
    print('Индексы', possible_types)
    '''
    Гидравлический расчет трубопроводной системы.
    '''
    if (pressure[3] and pressure[4]) == 0:
        speed_flow=af.awerage_speed_flow(flow_rate[0],  scheme[0], enviroment[3], enviroment[2]) # средняя скорость потока 4.4-4.5
        reynolds = af.reynolds_k(scheme[1], speed_flow, scheme[0], enviroment[0]) # критерий рейнольдса 4.8
        relativ_roughnes=af.relatively_roughness(scheme[4][4], scheme[0]) # относительная шероховатость
        friction = af.hydravlic_friction(reynolds, relativ_roughnes)
        if scheme[3] == True:   #True - пользователь ввел ручками сумму гидравлических сопротивлений, False - выбрал из списков
            losses_local=af.losses_local_res(scheme[5], enviroment[2], speed_flow)
        else:
            all_res = af.all_resistances(scheme[4][1][1], scheme[4][3][1], scheme[4][6][1],
                                      scheme[4][7][1], scheme[4][8][1], scheme[4][9][1],
                                      scheme[4][10][1], scheme[4][11][1])
            losses_local= af.losses_local_res(all_res, enviroment[2], speed_flow)
        losses_straight=af.losses_straight_lines(friction, enviroment[2], scheme[5], speed_flow, scheme[0])
        pressure_loss = lambda x,y: x+y # давненько не брал я в руки лямбд
        pressure_loss=pressure_loss(losses_local, losses_straight)
    else:
        pressure_loss=pressure[3]+pressure[4]
    print('Потери давления в линии (дельта P_л)', pressure_loss)
    '''
    Гидравлический расчет трубопроводной сис-мы до РО (P1)
    '''
    resistances_before = af.all_resistances(scheme_before[1][1], scheme_before[3][1], scheme_before[6][1],
                                      scheme_before[7][1], scheme_before[8][1], scheme_before[9][1],
                                      scheme_before[10][1], scheme_before[11][1])
    losses_local_before = af.losses_local_res(resistances_before, enviroment[2], speed_flow)
    before_hydrostat=[]       #список гидростатических давлений
    before_hydrostat=af.hydrostatic_pressure(scheme_before[5][2], enviroment[2], scheme_before[5][3], scheme_before[1])
    if enviroment[3] == 1 or enviroment[3] == 3:  # если среда - газ/пар
        final_hydro_before=0
    else:
         final_hydro_before=reduce(af.summ_list, before_hydrostat) # его сумма
    print('Гидростатическое давление перед РО ', before_hydrostat)

    before_ro = pressure[0]-final_hydro_before-losses_local_before
    print('Давление перед РО  (P1)', before_ro)
    ''' Определяем максимальный перепад давления на РО '''
    if pressure[3] and pressure[6] != 0:    # если есть P1 и P2
        difference_pressure_max=difference_pressure
    else:
        list_hydrostat=[]       #список гидростатических давлений
        list_hydrostat=af.hydrostatic_pressure(scheme[4][5][2], enviroment[2], scheme[4][5][3], scheme[4][5][1])
        if scheme[4][5][0] == False:  # если не указанны изгибы трубы
            final_hydrostate_pressure=0
            print('Гидростатическое давление не расчитано')
        elif enviroment[3] == 1 or enviroment[3] == 3: # если среда - газ/пар, расчетом можно пренебречь
            final_hydrostate_pressure=0
        else:
            final_hydrostate_pressure=reduce(af.summ_list, list_hydrostat) # общая сумма списка. не забываем про перевод
        total_overfall = pressure[0]-pressure[1]+final_hydrostate_pressure
        difference_pressure_max=lambda x,y : x-y
        difference_pressure_max=difference_pressure_max(total_overfall,losses_local)
    '''Расчет максимальной пропускной способности. Все посчитанные ранее значения пишем в БД
    '''
    type(pressure_nominal)
    con = sqlite3.connect('database_all.db')
    cur = con.cursor()
    # data [(ID, NAME, CALCULATE) для таблицы CALCULATE_VALUES]
    data = [
        (1, 'pressure_nominal_(P_y)', pressure_nominal),
        (2, 'possible_types', str(possible_types)),
        (3, 'speed_flow(w)', speed_flow),
        (4, 'reynolds', int(reynolds)),
        (5, 'relativ_roughnes', relativ_roughnes),
        (6, 'losses_straight', losses_straight),
        (7, 'losses_local', losses_local),
        (8, 'pressure_loss', pressure_loss),
        (9, 'losses_local_before', losses_local_before),
        (10, 'final_hydro_before', final_hydro_before),
        (11, 'before_ro', before_ro),
        (12, 'difference_pressure_max', difference_pressure_max)
    ]
    sql_request = "INSERT OR IGNORE INTO CALCULATE_VALUES (ID, NAME, CALCULATE) VALUES (?, ?, ?)"
    try:
        cur.executemany(sql_request, data)
    except sqlite3.DatabaseError as error:
        print('Не удалось внести данные в БД')
    con.commit()

    '''
    Закоментированный фрагмент нужен только для тестирования, выбор типа РО и условного диаметра
    происходит вручную из каталогов производителя
    '''
    if (flow_rate[4]) in possible_types:    #проверка на совпадение желаемого РО в списке возможных
        i = 0
        while i < len(possible_types):
            if flow_rate[4] == possible_types[i]:
                defined_type = possible_types[i]
            i +=1
        print('Доступен выбор предпочитаемого РО. Тип предпочитаемого РО:', af.ouput_dict(defined_type, False))
    else:
        defined_type = possible_types[0] # 1-ый тип РО в списке допустимых
        print('Не доступен выбор предпочитаемого РО. Рекомендуемый тип РО:', af.ouput_dict(defined_type, False))
    if (5 in possible_types) == False: #если не допустимо использование шлангового РО
        capacity_m=af.capacity_max(enviroment[3], flow_rate[0], difference_pressure_max, enviroment[2], temperature[0])
        print('Максимальная пропускная способность (К_v)', capacity_m)
    else:
        print('Шланговые РО будут добавленны после тестирования ') #когда я разберусь с типами среды и мне не будет лень
    '''
    Выбираем условную пропускную способность и условный проход РО
    '''
    capacity_nominal = lambda x: x*1.2  #условная пропускная способность, именно по ней и идет дальнейший выбор условного диаметра
    capacity_nominal = capacity_nominal (capacity_m)
    print('Условная максимальная пропускная способность (K_v_y)', capacity_nominal)
    #diametr_nominal = af.diametr_nominal_type(defined_type, pressure_nominal, capacity_nominal) # выбор условного диаметра по таблицам, только для тестирования!
    add_data =[
        (13, 'capacity_max', capacity_m),
        (14, ' capacity_nominal',  capacity_nominal)
    ]
    try:
        cur.executemany(sql_request, add_data)
    except sqlite3.DatabaseError as error:
        print('Не удалось внести данные в БД')
    con.commit()
    con.close()

