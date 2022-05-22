from collections import Counter
import datetime as dt

import pandas as pd

from ini_res import Ini
from lic_res import Lic
from dbf_res import Dbf
import os

from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from tkcalendar import DateEntry, Calendar

INI = Ini()
LIC = Lic()
DBF = Dbf()

COLOR1 = "#D3D3D3"
COLOR2 = "#F5F5DC"
COLOR3 = "#FFBCD1"

LOG_NAME = 'AlohaSh5.log'
INI_NAME = 'AlohaSh5.ini'
# OUT_NAME = 'SHOut'
RES_FILE_NAME = 'res.dat'
# LIC RES
NTP_URL = INI.get(log=LOG_NAME, ini=INI_NAME, section='NTP', param='url')
LICENSE = LIC.check(log_file_name=LOG_NAME, res_file_name=RES_FILE_NAME, ntp_url=NTP_URL)
# INI PATHS
DICTS_PATH = INI.get(log=LOG_NAME, ini=INI_NAME, section='PATHS', param='dicts')
SHIFTS_PATH = INI.get(log=LOG_NAME, ini=INI_NAME, section='PATHS', param='shifts')
# INI GROUP PARAMS
GROUPS = INI.get(log=LOG_NAME, ini=INI_NAME, section='EXP', param='groups')
TOTALS = INI.get(log=LOG_NAME, ini=INI_NAME, section='EXP', param='totals')
TABLES = INI.get(log=LOG_NAME, ini=INI_NAME, section='EXP', param='tables')
# DICTS
TDR_NAME = 'TDR.DBF'
CMP_NAME = 'CMP.DBF'
RSN_NAME = 'RSN.DBF'
CAT_NAME = 'CAT.DBF'
CIT_NAME = 'CIT.DBF'
ITM_NAME = 'ITM.DBF'
# SHIFTS
GNDITEM_NAME = 'GNDITEM.DBF'
GNDTNDR_NAME = 'GNDTNDR.DBF'
GNDVOID_NAME = 'GNDVOID.DBF'
# EXPCATEG CODE RATES
PAY_RATE = 10000
CUR_RATE = 20000
RSN_RATE = 30000
# EXP
EXP_NAME = 'exp.dbf'
EXPCATEG_NAME = 'Expcateg.dbf'
GTREE_NAME = 'GTree.dbf'
GOODS_NAME = 'Goods.dbf'
CATEG_NAME = 'Categ.dbf'
SUNITS_NAME = 'sunits.dbf'
# DATA PERIODS
NOW = dt.datetime.now()
START = INI.get(log=LOG_NAME, ini=INI_NAME, section='EXP', param='start')
STOP = INI.get(log=LOG_NAME, ini=INI_NAME, section='EXP', param='stop')
# SH5 API
HOST = INI.get(log=LOG_NAME, ini=INI_NAME, section='MAIN', param='host')
PORT = INI.get(log=LOG_NAME, ini=INI_NAME, section='MAIN', param='port')
USER_NAME = INI.get(log=LOG_NAME, ini=INI_NAME, section='MAIN', param='user')
USER_PSW = INI.get(log=LOG_NAME, ini=INI_NAME, section='MAIN', param='psw')
EXEC = 'sh5exec'  # выполнить процедуру


def get_data(name: str):

    # SH4 ----------------------------

    def expcateg(param: str):
        """ param: 'expcateg' or 'ptree';\n
        Возвращает expcateg_tl или ptree """

        # ---------------------- PAYS & PTREE -------------------------------------------------------- #
        section = 'PTREE'
        names = INI.get(log=LOG_NAME, ini=INI_NAME, section=section, param='names').split(", ")
        codes = INI.get(log=LOG_NAME, ini=INI_NAME, section=section, param='codes').split(", ")

        ptree_l = []  # список валют из ини с привязкой к типам оплат
        pay_tl = []  # корневой уровень PTREE типы оплат
        for i in range(len(codes)):
            extcode = str(int(codes[i]) + PAY_RATE)
            name = f"pay:{names[i]}"
            deleted = '0'
            subs = INI.get(log=LOG_NAME, ini=INI_NAME, section=section, param=f"{'subs'}{codes[i]}").split(", ")
            t = (extcode, name, deleted)
            pay_tl.append(t)  # [('20098', 'CASH', '0') ...
            ptree_l.append([extcode, name] + subs)  # ... ['20096', 'OTHERS', '24', '14', '11', '18']]

        # ---------------------------- CURRENCIES & DISCS ------------------------------------------------------ #
        tdr = DBF.read_dbf(log=LOG_NAME, file_path=DICTS_PATH, file_name=TDR_NAME)
        cmp = DBF.read_dbf(log=LOG_NAME, file_path=DICTS_PATH, file_name=CMP_NAME)
        cur_tl = []
        for l in tdr:
            extcode = str(l[0] + CUR_RATE)
            name = f"cur:{l[1]}"
            deleted = '0'
            t = (extcode, name, deleted)
            cur_tl.append(t)  # [('10020', 'cur:Кред.Карта', '0'), ('10001', 'cur:РУБЛИ', '0'),
        cmp_tl = []
        for l in cmp:
            extcode = str(l[0] + CUR_RATE)
            name = f"cur:{l[1]}"
            deleted = '0'
            t = (extcode, name, deleted)
            cmp_tl.append(t)  #
    # ------------------ DEL REASONS ----------------------------------------------------------- #
        rsn = DBF.read_dbf(log=LOG_NAME, file_path=DICTS_PATH, file_name=RSN_NAME)
        rsn_tl = []
        for l in rsn:
            extcode = str(l[0] + RSN_RATE)
            name = f"rsn:{l[1]}"
            deleted = '0'
            t = (extcode, name, deleted)
            rsn_tl.append(t)  #

        expcateg_tl = pay_tl + cur_tl + cmp_tl + rsn_tl
        # [('10098', 'pay:CASH', '0'), ... ('20020', 'cur:Кред.Карта', '0'), ... ('30006', 'rsn:Б/С Менеджер', '0')]

        if param == 'ptree':
            return ptree_l
        else:
            return expcateg_tl

    def gtree(param: str):
        """ param: 'gtree1' or 'gtree2';\n
        Возвращает gtree_tl или gtree1 / 2 """

        ini_names = INI.get(log=LOG_NAME, ini=INI_NAME, section='GTREE', param='names').split(", ")  # list
        ini_codes = INI.get(log=LOG_NAME, ini=INI_NAME, section='GTREE', param='codes').split(", ")  # list

        gtree1 = []  # [[root_cat_code: num, root_cat_name: str, cat_codes], ...
        tl1 = []  # корневой уровень каталогов / категорий товаров
        for i in range(len(ini_codes)):
            extcode = int(ini_codes[i])
            parent = None
            name = ini_names[i]
            abbr = str(extcode)
            subs = INI.get(log=LOG_NAME, ini=INI_NAME, section='GTREE', param=f"{'subs'}{ini_codes[i]}").split(", ")
            t = (extcode, parent, name, abbr)

            tl1.append(t)  # [(61, None, 'Алкоголь', '61'), (62, None, 'Еда', '62')]
            gtree1.append([extcode, name] + subs)  # [['61', 'Бар', '1', '3'], ...

        cats = DBF.read_dbf(log=LOG_NAME, file_path=DICTS_PATH, file_name=CAT_NAME)  # [[2, 'Бар'], [1, 'Кухня']]

        gtree2 = []
        for l1 in cats:
            ccode = str(l1[0])  # : str
            cname = str(l1[1])  # : str
            for l2 in gtree1:
                subs = l2[2:]  # срез начиная со 2-го индекса: str
                gcode = l2[0]  # int
                gname = l2[1]  # str
                if ccode in subs:
                    gtree2.append([int(ccode), cname, gcode, gname])  # [[2, 'Бар', 62, 'KUH'], ...
        # подкорневой уровень каталогов (категорий)
        tl2 = [(x[0], x[2], x[1], str(x[0])) for x in gtree2]  # (extcode, parent, name, abbr)
        # result
        gtree_tl = tl1 + tl2  # [(61, None, 'BAR', '61'), (62, None, 'KUH', '62'), (2, 62, 'Бар', '2'), (1, 61, ...

        if param == 'gtree1': return gtree1
        elif param == 'gtree2': return gtree2
        elif param == 'tl1': return tl1
        else: return gtree_tl

    def goods(param: str):
        """ param option: 'goods2' """

        itm = DBF.read_dbf(log=LOG_NAME, file_path=DICTS_PATH, file_name=ITM_NAME)  # [[1802, 'Чизкейк', 210.0], ...
        cat = [x[0] for x in DBF.read_dbf(log=LOG_NAME, file_path=DICTS_PATH, file_name=CAT_NAME)]  # [[2], [1]]
        cit = [x for x in DBF.read_dbf(log=LOG_NAME, file_path=DICTS_PATH, file_name=CIT_NAME) if x[0] in cat]
        items = []
        for l1 in cit:
            for l2 in itm:
                if l2[0] == l1[1]:
                    items.append([l1[1], l1[0], l2[1], l2[2]])
                    # [code, parent, name, price] .. [[1802, 1, 'Чизкейк', 210.0], ...
        # (extcode, parent, name, abbr_text, abbr_num, categ_ref, outtax1, outtax2, outprice, deleted, used, barcode)
        goods_tl = [(x[0], x[1], x[2], "", x[0], x[1], None, None, x[3], 0, None, "") for x in items]  # блюда
        # [(1802, 1, 'Чизкейк', '', 1802, 1, None, None, 210.0, 0, None, '') ...

        goods1 = [[x[0], x[1], x[2], x[3]] for x in items]  # [[1802, 1, 'Чизкейк', 210.0], ...
        gtree1 = gtree(param='gtree1')  # [[61, 'BAR', '1', '22'], [62, 'KUH', '2']]

        # # goods2 with sunit_ref
        goods2 = []
        for l in goods1:
            gcode = str(l[1])
            for l2 in gtree1:
                sunit = l2[0]
                if gcode in l2:
                    l.append(sunit)  #
                    goods2.append(l)  #
        # result
        if param == 'goods2': return goods2
        elif param == 'goods': return goods_tl
        else: pass

    def categ():

        gtree2 = gtree(param='gtree2')  # [[2, 'Бар', 62, 'KUH'], ...
        categ_tl = [(x[0], x[1], None, 0) for x in gtree2]  # extcode, name, extoptions, deleted
        # [(2, 'Бар', None, 0), (1, 'Кухня', None, 0)]
        return categ_tl

    def sunits():

        tl1 = gtree(param='tl1')  # [(61, None, 'BAR', '61'), (62, None, 'KUH', '62')]
        sunits_tl = [(str(x[0]), x[2], 0) for x in tl1]  # (code, name, deleted)
        # print(sunits_tl)  # [('61', 'BAR', 0), ('62', 'KUH', 0)]
        return sunits_tl

    def shifts(start: str, stop: str, param: str):

        """ Создание листов смен из aloha shift (GND) dbf файлов.\n
         Ожидает параметры: 'gnditem', 'gndtndr', 'gndvoid'. params start/stop: 'YYYYMMDD'. """

        shifts_path = INI.get(log=LOG_NAME, ini=INI_NAME, section='PATHS', param='shifts')

        shift_dirs = []  # лист всех каталогов смен
        for root, dirs, files in os.walk(shifts_path):
            for d in dirs:
                if len(d) == 8 and d.isdigit() == True:  # проверка длины каталога и на цифровое название
                    shift_dirs.append(d)  # лист каталогов: ['20211212', '20211213']
                else: pass

        if len(shift_dirs) != 0:
            shift_dirs2 = []  # лист смен после фильтрации
            # старт/стоп директории вне списка
            if start not in shift_dirs and stop not in shift_dirs:
                shift_dirs2 = shift_dirs  # срез старт-стоп диапазона
            # старт вне списка / стоп в списке
            elif start not in shift_dirs and stop in shift_dirs:
                shift_dirs2 = shift_dirs[: shift_dirs.index(stop) + 1]
            # старт в списке / стоп вне списка
            elif start in shift_dirs and stop not in shift_dirs:
                shift_dirs2 = shift_dirs[shift_dirs.index(start):]
            # старт/стоп в списке
            elif start in shift_dirs and stop in shift_dirs:
                shift_dirs2 = shift_dirs[shift_dirs.index(start): shift_dirs.index(stop) + 1]

            items = []
            tndrs = []
            voids = []
            for shift_dir in shift_dirs2:
                items.extend(DBF.read_dbf(log=LOG_NAME, file_path=f"{SHIFTS_PATH}/{shift_dir}", file_name=f"{GNDITEM_NAME}"))
                tndrs.extend(DBF.read_dbf(log=LOG_NAME, file_path=f"{SHIFTS_PATH}/{shift_dir}", file_name=f"{GNDTNDR_NAME}"))
                voids.extend(DBF.read_dbf(log=LOG_NAME, file_path=f"{SHIFTS_PATH}/{shift_dir}", file_name=f"{GNDVOID_NAME}"))

        if param == GNDITEM_NAME: return items
        elif param == GNDTNDR_NAME: return tndrs
        elif param == GNDVOID_NAME: return voids
        else: return []

    def exp():
        """ params: '1' - by cur's, '2' - by pay types, '3' - by del reasons """

        START = INI.get(log=LOG_NAME, ini=INI_NAME, section='EXP', param='start')
        STOP = INI.get(log=LOG_NAME, ini=INI_NAME, section='EXP', param='stop')

        GROUPS = INI.get(ini=INI_NAME, log=LOG_NAME, section='EXP', param='groups')
        TOTALS = INI.get(ini=INI_NAME, log=LOG_NAME, section='EXP', param='totals')
        # TABLES = INI.get(ini=INI_NAME, log=LOG_NAME, section='EXP', param='tables')

        items = shifts(start=START, stop=STOP, param=GNDITEM_NAME)  # [[20001, datetime.date(2022, 4, 5), 2900, 1.0, 380.0, 380.0, 1], .. categ]
        tndrs = shifts(start=START, stop=STOP, param=GNDTNDR_NAME)  # [[20001, 1, 20], ... check, pay_id, cur

        goods2 = goods('goods2')  # [[1802, 1, 'Чизкейк', 210.0, 61], ...
        ptree = expcateg('ptree')  # ... ['10096', 'pay:OTHERS', '24', '14', '11', '18']]

        # ----------------------------------- GND ITEMS FULL LIST ---------------------------------------------- #
        items2 = []
        for l in items:
            check = l[0]
            item = l[2]
            for l2 in tndrs:
                check2 = l2[0]
                cur = l2[2]
                if check == check2 and len(l) < 8:
                    l.append(cur)  # [20001, datetime.date(2022, 4, 5), 2900, 1.0, 380.0, 380.0, 1, 20]
                    # [check, date, item, quantity, price, discprice, categ, cur]
            for l3 in goods2:
                item2 = l3[0]
                sunit = l3[4]
                name = l3[2]
                if item == item2:
                    l.append(sunit)  # ... , 220.0, 10001, 62]  # ... cur, sunit]
                    l.append(name)  # ... curr, sunit, item_name]
                     # [20001, datetime.date(2022, 4, 5), 2900, 1.0, 380.0, 380.0, 1, 20, 61, 'Ролл с лососем 200 гр'] ...
            for l4 in ptree:  # ... ['10096', 'pay:OTHERS', '24', '14', '11', '18']]
                pay = int(l4[0])  # 10096
                curs = l4[2:]  # ['24', '14', '11', '18'] ..
                if str(l[7]) in curs:
                    l.append(pay)
                    items2.append(l)
        # print(items2)
        # [[20001, datetime.date(2022, 4, 5), 2900, 1.0, 380.0, 380.0, 1, 20, 61, 'Ролл с лососем 200 гр', 10099],
        # ------------------------------------ EXP ITEMS TL ------------------------------------- #
        # # [check, date, item, quantity, price, discprice, categ, cur, sunit, name, pay_type]
        tl1 = []
        for l in items2:
            logicdate = l[1]
            sunits_ref = str(l[8])
            goods_ref = l[2]
            pgoods_ref = None

            if GROUPS == '2': ecateg_ref = l[7] + CUR_RATE  # by currs
            elif GROUPS == '1': ecateg_ref = l[-1]  # by pay types
            elif GROUPS == '3': ecateg_ref = INI.get(log=LOG_NAME, ini=INI_NAME, section='RSN', param='default_guid')  # by del reasons
            else: ecateg_ref = INI.get(log=LOG_NAME, ini=INI_NAME, section='RSN', param='default_guid')  # by del reasons

            ecaption_ref = None
            qnt = l[3]
            if TOTALS == '1': total0 = l[5]  # with discs / markups
            elif TOTALS == '2': total0 = l[6]  # without
            else: total0 = l[5]  # with

            # обработка отрицательной цены (при возвратах)
            if total0 < 0:
                total = 0
            else:
                total = total0

            gabbr_text = ""
            gabbr_num = str(l[2])
            gname = l[9]
            t = (logicdate, sunits_ref, goods_ref, pgoods_ref, ecateg_ref, ecaption_ref, qnt, total,
                 gabbr_text, gabbr_num, gname)
            tl1.append(t)
            # [(datetime.date(2022, 4, 5), '61', 2900, None, 20020, None, 1.0, 380.0, '', '2900', 'Ролл с лососем 200
        # ------------------------------------- VOIDS TL  ------------------------------------------- #
        voids = shifts(start=START, stop=STOP, param=GNDVOID_NAME)
        # [[20604, datetime.date(2022, 4, 5), 1806, 130.0, 5], ... reason]
        # Передается в TL, если код причины удаления есть в [RSN]reasons
        voids2 = []
        for l in voids:
            code = l[2]
            for l2 in goods2:  # [[1802, 1, 'Чизкейк', 210.0, 61], ...
                code2 = l2[0]
                name = l2[2]
                sunit = l2[4]
                if code == code2:
                    l.append(name)  # ... , 'Хот-Дог']
                    l.append(sunit)  # ... -Дог', 61]
                    voids2.append(l)  # [[20604, datetime.date(2022, 4, 5), 1806, 130.0, 5, 'Круассан с шоколадом', 61],
        ini_reasons = INI.get(log=LOG_NAME, ini=INI_NAME, section='RSN', param='reasons').split(", ")
        del_reasons = [int(x) for x in ini_reasons]

        tl2 = []
        for l in voids2:  # [[20604, datetime.date(2022, 4, 5), 1806, 130.0, 5, 'Круассан с шоколадом', 61],
            if l[4] in del_reasons:
                logicdate = l[1]
                sunits_ref = str(l[6])
                goods_ref = l[2]
                pgoods_ref = None
                if GROUPS == '3':
                    ecateg_ref = num_to_guid(str(l[4] + RSN_RATE))
                else:
                    ecateg_ref = l[4] + RSN_RATE
                ecaption_ref = None
                qnt = 1.0
                total = l[3]
                gabbr_text = ""
                gabbr_num = str(l[2])
                gname = l[5]
                t = (logicdate, sunits_ref, goods_ref, pgoods_ref, ecateg_ref, ecaption_ref, qnt, total,
                     gabbr_text, gabbr_num, gname)
                tl2.append(t)  #

        tl = tl1 + tl2
        # Получение конечного RES_TL (ITEMS + VOIDS) просуммированного по кол-ву

        c = Counter(tl)
        exp_dict = c

        logicdate_l = []
        sunits_ref_l = []  # str,2
        goods_ref_l = []
        pgoods_ref_l = []
        ecateg_ref_l = []  # int,15
        ecaption_ref_l = []
        qnt_l = []
        total_l = []
        gabbr_text_l = []
        gabbr_num_l = []
        gname_l = []  # str,47

        for k in exp_dict:
            # print(k[2], exp_dict[k])
            logicdate_l.append(k[0])
            sunits_ref_l.append(k[1])
            goods_ref_l.append(k[2])
            pgoods_ref_l.append(k[3])
            ecateg_ref_l.append(k[4])
            ecaption_ref_l.append(k[5])
            qnt_l.append(float(exp_dict[k]))
            total_l.append(k[7] * exp_dict[k])
            gabbr_text_l.append(k[8])
            gabbr_num_l.append(k[9])
            gname_l.append(k[10])

        res_tl = list(zip(logicdate_l, sunits_ref_l, goods_ref_l, pgoods_ref_l, ecateg_ref_l, ecaption_ref_l, qnt_l,
                      total_l, gabbr_text_l, gabbr_num_l, gname_l))

        return res_tl

    # SH5 ---------------------------

    def num_to_guid(num: str):
        """ Convert any number to guid """
        zero_add = ''
        guid_mask = '{00000000-0000-0000-0000-'
        postfix = '}'
        if len(num) < 12:
            diff = 12 - len(num)  # 6
            for _ in range(diff):
                zero_add += '0'
                code = zero_add + num
        elif len(num) > 12:
            diff = len(num) - 12
            code = num[diff:]
        else:
            code = num

        guid = guid_mask + code + postfix
        return guid  # make

    def sh5_corrs():
        """ Returns spec_corrs.json """

        # ---------------------- PAYS & PTREE -------------------------------------------------------- #
        section = 'PTREE'
        names = INI.get(log=LOG_NAME, ini=INI_NAME, section=section, param='names').split(", ")
        codes = INI.get(log=LOG_NAME, ini=INI_NAME, section=section, param='codes').split(", ")

        guid = []
        name = []
        type = []

        for i in range(len(codes)):
            extcode = str(int(codes[i]) + PAY_RATE)
            guid.append(num_to_guid(extcode))
            name.append(f"pay:{names[i]}")
            type.append(2)
        # ---------------------------- CURRENCIES & DISCS ------------------------------------------------------ #
        tdr = DBF.read_dbf(log=LOG_NAME, file_path=DICTS_PATH, file_name=TDR_NAME)
        cmp = DBF.read_dbf(log=LOG_NAME, file_path=DICTS_PATH, file_name=CMP_NAME)

        for l in tdr:
            extcode = str(l[0] + CUR_RATE)
            guid.append(num_to_guid(extcode))
            name.append(f"cur:{l[1]}")
            type.append(2)

        for l in cmp:
            extcode = str(l[0] + CUR_RATE)
            guid.append(num_to_guid(extcode))
            name.append(f"cur:{l[1]}")
            type.append(2)

        # ------------------ DEL REASONS ----------------------------------------------------------- #
        rsn = DBF.read_dbf(log=LOG_NAME, file_path=DICTS_PATH, file_name=RSN_NAME)

        for l in rsn:
            extcode = str(l[0] + RSN_RATE)
            guid.append(num_to_guid(extcode))
            name.append(f"rsn:{l[1]}")

        corrs_json = {
            "UserName": USER_NAME,
            "Password": USER_PSW,
            "ProcName": 'ReplCorrs',
            "Input": [
                {
                    "Head": "107",
                    "Original": ['4', '3', '32'],
                    "Values": [guid, name, type]
                }
            ]
        }

        return corrs_json

    def sh5_ggroups():
        """ Returns ggroups.json """

        ini_names = INI.get(log=LOG_NAME, ini=INI_NAME, section='GTREE', param='names').split(", ")  # list
        ini_codes = INI.get(log=LOG_NAME, ini=INI_NAME, section='GTREE', param='codes').split(", ")  # list
        ini_root_guid = INI.get(log=LOG_NAME, ini=INI_NAME, section='GTREE', param='root_guid')

        guid = []
        parent = []
        name = []

        gtree1 = []
        for i in range(len(ini_codes)):
            extcode = ini_codes[i]
            guid.append(num_to_guid(extcode))
            parent.append(ini_root_guid)
            name.append(ini_names[i])

            subs = INI.get(log=LOG_NAME, ini=INI_NAME, section='GTREE', param=f"{'subs'}{ini_codes[i]}").split(", ")
            gtree1.append([extcode, name] + subs)  # [['61', 'Бар', '1', '3'], ...

        cats = DBF.read_dbf(log=LOG_NAME, file_path=DICTS_PATH, file_name=CAT_NAME)  # [[2, 'Бар'], [1, 'Кухня']]

        gtree2 = []
        for l1 in cats:
            ccode = str(l1[0])  # : str
            cname = str(l1[1])  # : str
            for l2 in gtree1:
                subs = l2[2:]  # срез начиная со 2-го индекса: str
                gcode = l2[0]  # int
                gname = l2[1]  # str
                if ccode in subs:
                    gtree2.append([ccode, cname, gcode, gname])  # [[2, 'Бар', 62, 'KUH'], ...

        # подкорневой уровень каталогов (категорий)
        for l in gtree2:
            extcode = l[0]
            guid.append(num_to_guid(extcode))
            parent.append(num_to_guid(l[2]))
            name.append(l[1])

        ggroups_json = {
            "UserName": USER_NAME,
            "Password": USER_PSW,
            "ProcName": 'ReplGGroups',
            "Input": [
                {
                    "Head": "209#2",
                    "Original": ['209#3\\4', '4', '3'],
                    "Values": [parent, guid, name]
                }
            ]
        }

        return ggroups_json

    def sh5_goods():
        """ Returns goods.json """

        itm = DBF.read_dbf(log=LOG_NAME, file_path=DICTS_PATH, file_name=ITM_NAME)  # [[1802, 'Чизкейк', 210.0], ...
        cat = [x[0] for x in DBF.read_dbf(log=LOG_NAME, file_path=DICTS_PATH, file_name=CAT_NAME)]  # [[2], [1]]
        cit = [x for x in DBF.read_dbf(log=LOG_NAME, file_path=DICTS_PATH, file_name=CIT_NAME) if x[0] in cat]

        guid = []
        parent = []
        name = []
        price = []
        rkcode = []

        for l1 in cit:
            for l2 in itm:
                if l2[0] == l1[1]:
                    # items.append([str(l1[1]), str(l1[0]), l2[1], l2[2]])
                    # [code, parent, name, price] .. [[1802, 1, 'Чизкейк', 210.0], ...
                    guid.append(num_to_guid(str(l1[1])))
                    parent.append(num_to_guid(str(l1[0])))
                    name.append(l2[1])
                    price.append(l2[2])
                    rkcode.append(str(l1[1]))

        goods_json = {
            "UserName": USER_NAME,
            "Password": USER_PSW,
            "ProcName": 'ReplGoods',
            "Input": [
                {
                    "Head": "210",
                    "Original": ['209\\4', '4', '3', '56', '241'],
                    "Values": [parent, guid, name, price, rkcode]
                }
            ]
        }

        return goods_json

    def sh5_sunits():

        tl1 = gtree(param='tl1')  # [(61, None, 'BAR', '61'), (62, None, 'KUH', '62')]

        guid = []
        name = []

        for l in tl1:
            guid.append(num_to_guid(str(l[0])))
            name.append(l[2])

        sunits_json = {
            "UserName": USER_NAME,
            "Password": USER_PSW,
            "ProcName": 'ReplSUnits',
            "Input": [
                {
                    "Head": "226",
                    "Original": ['4', '3'],
                    "Values": [guid, name]
                }
            ]
        }

        return sunits_json

    def sh5_odocs():
        """ Returns odocs.json """

        exp_tl = exp()
        # [(datetime.date(2022, 4, 6), '61', 1200, None, 10099, None, 1.0, 144.0, '', '1200', 'Американо 0,3 с собой'),

        date = []
        sunit_guid = []
        corr_guid = []
        good_guid = []
        good_qnt = []
        good_total = []
        spec = []

        for t in exp_tl:
            date.append(str(t[0]))
            sunit_guid.append(num_to_guid(t[1]))
            if GROUPS != '3':
                corr_guid.append(num_to_guid(str(t[4])))
            else:
                corr_guid.append(INI.get(log=LOG_NAME, ini=INI_NAME, section='RSN', param='default_guid'))

            good_guid.append(num_to_guid(str(t[9])))
            good_qnt.append(t[6])
            good_total.append(t[7])
            spec.append(0)

        odoc_json = {
            "UserName": USER_NAME,
            "Password": USER_PSW,
            "ProcName": 'ReplODocs',
            "Input": [
                {
                    "Head": "222",
                    "Original": ['221\\31', '221\\226\\4', '221\\107\\4', '210\\4', '9', '55', '42'],
                    "Values": [date, sunit_guid, corr_guid, good_guid, good_qnt, good_total, spec]
                }
            ]
        }

        return odoc_json

    if name == 'expcateg': return expcateg(param='expcateg')
    elif name == 'ptree': return expcateg(param='ptree')
    elif name == 'tl1': return gtree(param='tl1')
    elif name == 'gtree': return gtree(param='gtree')
    elif name == 'gtree1': return gtree(param='gtree1')
    elif name == 'gtree2': return gtree(param='gtree2')
    elif name == 'goods': return goods(param='goods')
    elif name == 'goods2': return goods(param='goods2')
    elif name == 'categ': return categ()
    elif name == 'sunits': return sunits()
    elif name == 'exp': return exp()
    # sh 5
    elif name == 'sh5_corrs': return sh5_corrs()
    elif name == 'sh5_ggroups': return sh5_ggroups()
    elif name == 'sh5_goods': return sh5_goods()
    elif name == 'sh5_sunits': return sh5_sunits()
    elif name == 'sh5_odocs': return sh5_odocs()
    else: pass


def api_request(host, port, proc):

    import requests
    request = requests.post(url=f'http://{host}:{port}/api/sh5exec', json=proc)
    request.raise_for_status()
    data = request.json()
    return data


def gui():

    # MENU FILE -------------------------------- #

    def gui_menu_file_start():

        # in group params
        tables = INI.get(ini=INI_NAME, log=LOG_NAME, section='EXP', param='tables')
        # Dicts
        corrs = get_data('sh5_spec_corrs')
        ggroups = get_data('sh5_ggroups')
        goods = get_data('sh5_goods')
        sunits = get_data('sh5_sunits')
        # Expenditure
        odocs = get_data('sh5_odocs')

        tables = [corrs, ggroups, goods, sunits, odocs]

        # write to sh5
        if tables == '1':  # Dicts + Exp
            for i in range(len(tables)):
                with open(LOG_NAME, "a") as log_file:
                    log_file.write(f"{NOW} : Start creating {tables[i]} ...\n")
                api_request(host=HOST, port=PORT, proc=tables[i])
                with open(LOG_NAME, "a") as log_file:
                    log_file.write(f"{NOW} : {tables[i]} Ok!\n")

        if tables == '2':  # Dicts only
            for i in range(len(tables[:4])):
                with open(LOG_NAME, "a") as log_file:
                    log_file.write(f"{NOW} : Start creating {tables[i]} ...\n")
                api_request(host=HOST, port=PORT, proc=tables[i])
                with open(LOG_NAME, "a") as log_file:
                    log_file.write(f"{NOW} : {tables[i]} Ok!\n")

        if tables == '3':  # Exp only
            with open(LOG_NAME, "a") as log_file:
                log_file.write(f"{NOW} : Start creating {tables[-1]} ...\n")
            api_request(host=HOST, port=PORT, proc=tables[-1])

        # Done! message
        with open(LOG_NAME, "a") as log_file:
            log_file.write(f"{NOW} : Exit.\n")
        # Done! message
        messagebox.showinfo(title='Convert', message='Done!')

        root.destroy()

    # MENU SETTINGS --------------------------- #

    def gui_menu_settings_paths():

        def button_save_paths():
            # menu settings entries enabled
            settings.entryconfigure(0, state='normal')
            settings.entryconfigure(1, state='normal')
            settings.entryconfigure(2, state='normal')
            # write paths from entries to ini
            INI.set(log=LOG_NAME, ini=INI_NAME, section='PATHS', param='dicts', data=entry_dicts.get())
            INI.set(log=LOG_NAME, ini=INI_NAME, section='PATHS', param='shifts', data=entry_shifts.get())
            # destroy
            button_save.destroy()
            entry_dicts.destroy()
            entry_shifts.destroy()
            # entry_result.destroy()
            label_paths.destroy()
            # resize back main window
            root.maxsize(width=245, height=250)

        # GUI MENU SETTINGS PATHS ---------------------------------------- #

        # menu settings entries disabled
        settings.entryconfigure(0, state='disabled')
        settings.entryconfigure(1, state='disabled')
        settings.entryconfigure(2, state='disabled')
        # root window extend
        root.maxsize(width=245, height=400)
        # Paths
        label_paths = Label(text="Paths - aloha dicts / shifts", width=22)
        label_paths.grid(column=0, row=7, sticky=NW)
        # Путь к справочникам
        entry_dicts = Entry(width=28, relief="sunken", bg=COLOR2)
        entry_dicts.insert(0, INI.get(log=LOG_NAME, ini=INI_NAME, section='PATHS', param='dicts'))
        entry_dicts.grid(column=0, row=8, padx=3, pady=5, sticky=NW)
        # Путь к сменам
        entry_shifts = Entry(width=28, relief="sunken", bg=COLOR2)
        entry_shifts.insert(0, INI.get(log=LOG_NAME, ini=INI_NAME, section='PATHS', param='shifts'))
        entry_shifts.grid(column=0, row=9, padx=3, pady=5, sticky=NW)
        # Save
        button_save = Button(text="Save", width=5, height=1, bg=COLOR3, command=button_save_paths)
        button_save.grid(column=0, row=11, padx=3, pady=5, sticky=SE)

    def gui_menu_settings_links():

        def unlinked_gtree_codes():
            cat = DBF.read_dbf(log=LOG_NAME, file_path=DICTS_PATH, file_name=CAT_NAME)  # [[2, 'Бар'], [1, 'Кухня']]
            linked_codes = [x[0] for x in get_data('gtree2')]  # [2]
            unlinked = [f' {x[0]}: {x[1]}->UNLINKED!' for x in cat if x[0] not in linked_codes]
            unlinked.sort()
            linked = [f' {x[0]}: {x[1]}->{x[2]}: {x[3]}' for x in get_data('gtree2')]
            linked.sort()
            result = unlinked + linked
            return result

        def unlinked_ptree_codes():
            tdr = DBF.read_dbf(log=LOG_NAME, file_path=DICTS_PATH, file_name=TDR_NAME)  # [[20, 'Кред.Карта'], ...
            linked_codes = [x[2:] for x in get_data('ptree') if x[2] != '']
            linked_codes2 = [item for sublist in linked_codes for item in sublist]
            unlinked = [f" {x[0]}: {x[1]}->UNLINKED!" for x in tdr if str(x[0]) not in linked_codes2]
            linked = []
            for x in tdr:
                code = str(x[0])
                name = x[1]
                for y in get_data('ptree'):
                    code_l = y[2:]
                    if code in code_l:
                        l = f" {code}: {name}->{int(y[0]) - PAY_RATE}: {y[1].lstrip('pay:')}"
                        linked.append(l)
            unlinked.sort()
            linked.sort()
            return unlinked + linked

        def unlinked_rsn_codes():

            rsn = DBF.read_dbf(log=LOG_NAME, file_path=DICTS_PATH, file_name=RSN_NAME)  # [[1, 'Ошибка официант'], ..
            linked_codes = INI.get(log=LOG_NAME, ini=INI_NAME, section='RSN', param='reasons').split(', ')
            linked = [f'{x[0]}: {x[1]}->linked OK!' for x in rsn if str(x[0]) in linked_codes]
            unlinked = [f'{x[0]}: {x[1]}->UNLINKED!' for x in rsn if str(x[0]) not in linked_codes]
            linked.sort()
            unlinked.sort()

            return unlinked + linked

        def button_close_links():

            # menu settings entries enabled
            settings.entryconfigure(0, state='normal')
            settings.entryconfigure(1, state='normal')
            settings.entryconfigure(2, state='normal')
            # destroy
            gtree_label.destroy()
            gtree_listbox.destroy()
            ptree_label.destroy()
            ptree_listbox.destroy()
            rsn_label.destroy()
            rsn_listbox.destroy()
            button_close.destroy()
            button_update.destroy()
            # resize back main window
            # root.minsize(width=245, height=250)
            root.maxsize(width=245, height=250)

        def button_update_lists():
            # clear listboxes
            gtree_listbox.delete(0, END)
            ptree_listbox.delete(0, END)
            rsn_listbox.delete(0, END)

            # fill gtree listbox
            unlinked_gtree = unlinked_gtree_codes()
            if len(unlinked_gtree) > 0:
                for item in unlinked_gtree:
                    gtree_listbox.insert(unlinked_gtree.index(item), item)

            # fill ptree listbox
            unlinked_ptree = unlinked_ptree_codes()
            for item in unlinked_ptree:
                ptree_listbox.insert(unlinked_ptree.index(item), item)

            # fill rsn listbox
            unlinked_rsn = unlinked_rsn_codes()
            for item in unlinked_rsn:
                rsn_listbox.insert(unlinked_rsn.index(item), item)

        # GUI LINKS -------------------------------------------------------------------- #

        # menu settings entries disabled
        settings.entryconfigure(0, state='disabled')
        settings.entryconfigure(1, state='disabled')
        settings.entryconfigure(2, state='disabled')
        # root window extend
        # root.minsize(width=480, height=490)
        root.maxsize(width=480, height=490)
        # GTREE ----------------------------------------------------------- #
        # Unlinked Categ's Label
        gtree_label = Label(text="Unlinked [GTREE] codes", width=21)
        gtree_label.grid(column=0, row=7, padx=3, sticky=NW)

        # Unlinked Categ's Listbox
        gtree_listbox = Listbox(height=10, width=28, exportselection="false", bg=COLOR2)
        unlinked_gtree = unlinked_gtree_codes()
        if len(unlinked_gtree) > 0:
            for item in unlinked_gtree:
                gtree_listbox.insert(unlinked_gtree.index(item), item)
        gtree_listbox.bind("<<ListboxSelect>>", None)
        gtree_listbox.grid(column=0, row=8, padx=3, pady=3, sticky=NW, rowspan=2)
        # PTREE ------------------------------------------------------------- #
        # Unlinked Currs's Label
        ptree_label = Label(text="Unlinked [PTREE] codes", width=21)
        ptree_label.grid(column=1, row=0, padx=3, sticky=NW)
        # Unlinked curr's Listbox
        ptree_listbox = Listbox(height=9, width=28, exportselection="false", bg=COLOR2)
        unlinked_ptree = unlinked_ptree_codes()
        for item in unlinked_ptree:
            ptree_listbox.insert(unlinked_ptree.index(item), item)
        ptree_listbox.bind("<<ListboxSelect>>", None)
        ptree_listbox.grid(column=1, row=1, padx=3, pady=3, sticky=NW, rowspan=6)

        # RSN ------------------------------------------------------------- #
        # Unlinked RSN's Label
        rsn_label = Label(text="Unlinked [RSN] codes", width=20)
        rsn_label.grid(column=1, row=7, padx=3, sticky=NW)
        # Unlinked RSN's Listbox
        rsn_listbox = Listbox(height=8, width=28, exportselection="false", bg=COLOR2)
        unlinked_rsn = unlinked_rsn_codes()
        for item in unlinked_rsn:
            rsn_listbox.insert(unlinked_rsn.index(item), item)
        rsn_listbox.bind("<<ListboxSelect>>", None)
        rsn_listbox.grid(column=1, row=8, padx=3, pady=3, sticky=NW)
        # Save button
        button_close = Button(text="Close", width=6, height=1, bg=COLOR3, command=button_close_links)
        button_close.grid(column=1, row=9, padx=3, pady=5, sticky=SE)
        # update button
        button_update = Button(text='Update lists \u27F3', width=13, height=1, bg=COLOR3, command=button_update_lists)
        button_update.grid(column=1, row=9, padx=3, pady=5, sticky=SW)

    def gui_menu_settings_impRK():

        def button_save_imprk():
            # menu settings entries enabled
            settings.entryconfigure(0, state='normal')
            settings.entryconfigure(1, state='normal')
            settings.entryconfigure(2, state='normal')
            # write paths from entries to ini
            INI.set(log=LOG_NAME, ini=INI_NAME, section='MAIN', param='host', data=entry_host.get())
            INI.set(log=LOG_NAME, ini=INI_NAME, section='MAIN', param='port', data=entry_port.get())
            INI.set(log=LOG_NAME, ini=INI_NAME, section='MAIN', param='user', data=entry_user.get())
            INI.set(log=LOG_NAME, ini=INI_NAME, section='MAIN', param='psw', data=entry_psw.get())
            # destroy
            label_host.destroy()
            entry_host.destroy()
            label_port.destroy()
            entry_port.destroy()
            label_user.destroy()
            entry_user.destroy()
            label_psw.destroy()
            entry_psw.destroy()

            button_apisave.destroy()
            # resize back main window
            root.maxsize(width=245, height=250)

        # GUI MENU SETTINGS ImpRK ---------------------------------------- #

        # menu settings entries disabled
        settings.entryconfigure(0, state='disabled')
        settings.entryconfigure(1, state='disabled')
        settings.entryconfigure(2, state='disabled')
        # root window extend
        root.maxsize(width=245, height=400)

        label_host = Label(text="Host", width=5)
        label_host.grid(column=0, row=7, sticky=NW)

        entry_host = Entry(width=13, relief="sunken", bg=COLOR2)
        entry_host.insert(0, INI.get(log=LOG_NAME, ini=INI_NAME, section='MAIN', param='host'))
        entry_host.grid(column=0, row=8, padx=3, pady=3, sticky=NW)

        label_port = Label(text="Port", width=5)
        label_port.grid(column=1, row=7, sticky=NW)

        entry_port = Entry(width=13, relief="sunken", bg=COLOR2)
        entry_port.insert(0, INI.get(log=LOG_NAME, ini=INI_NAME, section='MAIN', param='port'))
        entry_port.grid(column=1, row=8, padx=3, pady=3, sticky=NW)

        label_user = Label(text="User", width=5)
        label_user.grid(column=0, row=9, sticky=NW)

        entry_user = Entry(width=13, relief="sunken", bg=COLOR2)
        entry_user.insert(0, INI.get(log=LOG_NAME, ini=INI_NAME, section='MAIN', param='user'))
        entry_user.grid(column=0, row=10, padx=3, pady=3, sticky=NW)

        label_psw = Label(text="Psw", width=5)
        label_psw.grid(column=1, row=9, sticky=NW)

        entry_psw = Entry(width=13, relief="sunken", bg=COLOR2)
        entry_psw.insert(0, INI.get(log=LOG_NAME, ini=INI_NAME, section='MAIN', param='psw'))
        entry_psw.grid(column=1, row=10, padx=3, pady=5, sticky=NW)

        # ImpRK Save
        button_apisave = Button(text="Save", width=5, height=1, bg=COLOR3, command=button_save_imprk)
        button_apisave.grid(column=1, row=11, padx=3, pady=5, sticky=SE)


    # MENU HELP ------------------------------- #

    def menu_hlp_about():
        messagebox.showinfo(title="About", message="Aloha POS to SH5 Data Converter. Shareware. Version 5.1 release\n"
                                                   "Created by Dmitry R. Support: everycas@gmail.com.\n\n"
                                                   "Installation and user manual please see in docs folder.")

    def menu_hlp_license():
        messagebox.showinfo(title='License', message=f"Valid license: {LICENSE}.")

    # MAIN ------------------------------ #

    def pick_start(event):
        date = str(picker_start.get_date())
        start_date = ''.join(date.split('-'))  # str : 20220401
        INI.set(log=LOG_NAME, ini=INI_NAME, section='EXP', param='start', data=start_date)

    def pick_stop(event):
        date = str(picker_stop.get_date())
        stop_date = ''.join(date.split('-'))  # str : 20220401
        INI.set(log=LOG_NAME, ini=INI_NAME, section='EXP', param='stop', data=stop_date)

    def cbox_groups_set(event):
        num = str(int(cbox_groups['values'].index(cbox_groups.get())) + 1)
        INI.set(log=LOG_NAME, ini=INI_NAME, section='EXP', param='groups', data=num)

    def cbox_totals_set(event):
        num = str(int(cbox_totals['values'].index(cbox_totals.get())) + 1)
        INI.set(log=LOG_NAME, ini=INI_NAME, section='EXP', param='totals', data=num)

    def cbox_tables_set(event):
        num = str(int(cbox_tables['values'].index(cbox_tables.get())) + 1)
        INI.set(log=LOG_NAME, ini=INI_NAME, section='EXP', param='tables', data=num)

    # GUI MAIN WINDOW -------------------------------- #

    root = Tk()
    root.iconbitmap('logo.ico')
    root.title("AlohaSH")
    root.config(padx=5, pady=5)
    # root.minsize(width=245, height=250)
    root.maxsize(width=245, height=250)
    root.resizable(False, False)

    # FILE MENU ---------------------------------------- #

    main = Menu(root)
    root.config(menu=main)
    # File
    file = Menu(main, tearoff=0)
    file.add_command(label="Start", command=gui_menu_file_start)
    file.add_separator()
    file.add_command(label="Exit", command=root.destroy)
    # Settings
    settings = Menu(main, tearoff=0)
    settings.add_command(label="Set data paths", command=gui_menu_settings_paths)
    settings.add_command(label="Show unlinked codes", command=gui_menu_settings_links)
    settings.add_command(label="Set SH5 web api", command=gui_menu_settings_impRK)
    # Help
    hlp = Menu(main, tearoff=0)
    hlp.add_command(label="About", command=menu_hlp_about)
    hlp.add_command(label="License", command=menu_hlp_license)
    # Root menu level
    main.add_cascade(label="File", menu=file)
    main.add_cascade(label="Settings", menu=settings)
    main.add_cascade(label="Help", menu=hlp)

    # DATE / CALENDAR PICKERS ---------------------------- #
    # Label start
    date_label = Label(text="Start - stop data period", width=20)
    date_label.grid(column=0, row=0, padx=3, sticky=NW, columnspan=2)
    # Start picker
    picker_start = DateEntry(selectmode='day', year=NOW.year, month=NOW.month, day=NOW.day - 1, locale='ENG')
    picker_start.config(width=25)
    picker_start.bind("<<DateEntrySelected>>", pick_start)
    picker_start.grid(column=0, row=1, pady=3, padx=3, sticky=NW, columnspan=2)
    # Stop picker
    picker_stop = DateEntry(selectmode='day', year=NOW.year, month=NOW.month, day=NOW.day, locale='ENG')
    picker_stop.config(width=25)
    picker_stop.bind("<<DateEntrySelected>>", pick_stop)
    picker_stop.grid(column=0, row=2, pady=3, padx=3, sticky=NW, columnspan=2)

    # COMBO_BOXES -------------------------------------- #
    label_group = Label(text="Group EXP doc's", width=13)
    label_group.grid(column=0, row=3, padx=3, sticky=NW, columnspan=2)
    # 1
    n = StringVar()
    cbox_groups = ttk.Combobox(root, width=25, textvariable=n, state="readonly")
    cbox_groups['values'] = ('1) By pay types', '2) By currencies', '3) By del reasons')
    cbox_groups.bind("<<ComboboxSelected>>", cbox_groups_set)
    cbox_groups.grid(column=0, row=4, pady=3, padx=3, sticky=NW, columnspan=2)
    cbox_groups.current(int(INI.get(log=LOG_NAME, ini=INI_NAME, section='EXP', param='groups')) - 1)
    # 2
    n2 = StringVar()
    cbox_totals = ttk.Combobox(root, width=25, textvariable=n2, state="readonly")
    cbox_totals['values'] = ("1) With disc's / markups", "2) Without disc's / markups")
    cbox_totals.bind("<<ComboboxSelected>>", cbox_totals_set)
    cbox_totals.grid(column=0, row=5, pady=3, padx=3, sticky=NW, columnspan=2)
    cbox_totals.current(int(INI.get(log=LOG_NAME, ini=INI_NAME, section='EXP', param='totals')) - 1)
    # 3
    n3 = StringVar()
    cbox_tables = ttk.Combobox(root, width=25, textvariable=n3, state="readonly")
    cbox_tables['values'] = ("1) Dict's + Exp's", "2) Dict's only", "3) Exp's only")
    cbox_tables.bind("<<ComboboxSelected>>", cbox_tables_set)
    cbox_tables.grid(column=0, row=6, pady=3, padx=3, sticky=NW, columnspan=2)
    cbox_tables.current(int(INI.get(log=LOG_NAME, ini=INI_NAME, section='EXP', param='tables')) - 1)

    root.mainloop()


def auto():

    global START, STOP
    # date
    today = str(NOW.date())
    # чистка от символов
    date = int(today.replace("-", ''))  # : int 20220421
    start_date = str(date - 1)
    # запись старт-стоп даты в ини
    START = INI.set(log=LOG_NAME, ini=INI_NAME, section='EXP', param='start', data=start_date)
    STOP = INI.set(log=LOG_NAME, ini=INI_NAME, section='EXP', param='stop', data=str(date))

    # in group params
    tables = INI.get(ini=INI_NAME, log=LOG_NAME, section='EXP', param='tables')
    # Dicts
    corrs = get_data('sh5_spec_corrs')
    ggroups = get_data('sh5_ggroups')
    goods = get_data('sh5_goods')
    sunits = get_data('sh5_sunits')
    # Expenditure
    odocs = get_data('sh5_odocs')

    tables = [corrs, ggroups, goods, sunits, odocs]

    # write to sh5
    if tables == '1':  # Dicts + Exp
        for i in range(len(tables)):
            with open(LOG_NAME, "a") as log_file:
                log_file.write(f"{NOW} : Start creating {tables[i]} ...\n")
            api_request(host=HOST, port=PORT, proc=tables[i])
            with open(LOG_NAME, "a") as log_file:
                log_file.write(f"{NOW} : {tables[i]} Ok!\n")

    if tables == '2':  # Dicts only
        for i in range(len(tables[:4])):
            with open(LOG_NAME, "a") as log_file:
                log_file.write(f"{NOW} : Start creating {tables[i]} ...\n")
            api_request(host=HOST, port=PORT, proc=tables[i])
            with open(LOG_NAME, "a") as log_file:
                log_file.write(f"{NOW} : {tables[i]} Ok!\n")

    else:  # Exp only
        with open(LOG_NAME, "a") as log_file:
            log_file.write(f"{NOW} : Start creating {tables[-1]} ...\n")
        api_request(host=HOST, port=PORT, proc=tables[-1])
    # Done! message
    with open(LOG_NAME, "a") as log_file:
        log_file.write(f"{NOW} : Exit.\n")


def run():
    with open(LOG_NAME, "w") as log_file:
        log_file.write(f"{NOW} : Start.\n")

    # GUI
    if LICENSE:
        if INI.get(log=LOG_NAME, ini=INI_NAME, section='MAIN', param='gui') == '1':
            gui()
        else:
            auto()
    else:
        messagebox.showerror(title="License error", message=f'Valid license: {LICENSE}.\n\n'
                                                            'For new license and support contact to:\n'
                                                            'everycas@gmail.com')


run()

# odocs = get_data('sh5_odocs')
# print(odocs)
# api_request(host=HOST, port=PORT, proc=odocs)
# get_data('exp')