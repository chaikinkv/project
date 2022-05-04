import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import pandas as pd
import numpy as np
from os.path import abspath


def get_data(login, password, url, school, driver_src = abspath('chromedriver')):
    """
    на вход получает логин, пароль, название школы
    возвращает DataFrame
    """


    options = webdriver.ChromeOptions()
    options.headless = True

    driver = webdriver.Chrome(driver_src, options=options)

    try:
        driver.get(url=url)

        time.sleep(2)
        sft = Select(driver.find_element(By.NAME, 'sft'))
        sft.select_by_visible_text('Общеобразовательная')

        scid = Select(driver.find_element(By.NAME, 'scid'))
        scid.select_by_visible_text(school)

        driver.find_element(By.NAME, 'UN').send_keys(login)
        driver.find_element(By.NAME, 'PW').send_keys(password)

        driver.find_element(By.CLASS_NAME, 'button-login-title').click()

        time.sleep(2)

        if driver.current_url == 'https://net-school.cap.ru/asp/SecurityWarning.asp':
            driver.execute_script('if(isButtonsLock()) {return;}doContinue();;return false;')

        time.sleep(1)
        driver.find_element(By.LINK_TEXT, 'Отчеты').click()
        time.sleep(1)
        driver.find_element(By.LINK_TEXT, 'Отчет об успеваемости и посещаемости ученика').click()
        time.sleep(1)
        driver.find_element(By.XPATH, '//*[@id="buttonPanel"]/div/button[1]').click()
        time.sleep(5)

        df = pd.DataFrame(pd.read_html(driver.page_source, decimal=',')[1])
        # df.to_csv('TEST1.csv')
        return df
    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()


def prepare_data_from_csv(data):
    """
    получает на вход файл .csv и возвращает словарь с оценками
    """
    list_ = []
    marks = {}

    for j in range(1, data.shape[0]):
        list_ = []
        for i in data.iloc[j][1:-1]:

            try:
                int(i)
                list_.append(int(i))
            except:
                pass

            if '\xa0' in str(i):
                if '.' in str(i):
                    list_.append(int(i.split()[0])) if str(i)[0] != '.' else list_.append(int(i.split()[1]))
                else:

                    list_.append(int(i.split()[0]))
                    list_.append(int(i.split()[1]))

            elif i == '.':
                list_.append(2)

        list_.append(round(np.array(list_).mean(), 2)) if list_ != [] else list_.append(0)
        marks[data.iloc[j][1]] = list_

    return marks

def prepare_data_from_site(data):
    """
    получает на вход pd.DataFrame полученный с помощью йункции get_data() файл и возвращает словарь с оценками
    """
    list_ = []
    marks = {}

    for j in range(1, data.shape[0]):
        list_ = []
        for i in data.iloc[j][1:-1]:

            try:
                int(i)
                list_.append(int(i))
            except:
                pass

            if '\xa0' in str(i):
                if '.' in str(i):
                    list_.append(int(i.split()[0])) if str(i)[0] != '.' else list_.append(int(i.split()[1]))
                else:

                    list_.append(int(i.split()[0]))
                    list_.append(int(i.split()[1]))

            elif i == '.':
                list_.append(2)

        list_.append(round(np.array(list_).mean(), 2)) if list_ != [] else list_.append(0)
        marks[data.iloc[j][0]] = list_

    return marks

def choose_subj(marks):
    for i, j in enumerate(marks):
        print(i, j, '-', marks[j][-1])
    print('-----------------------------------------------------------')
    subj_num = int(input('Выберите предмет (номер предмета): '))
    print('-----------------------------------------------------------')
    return subj_num

def do_somthing_with_marks(marks, subj_num):
    """
    получает на вход словарь с оценками и номер выбранного предмета
    """
    current_marks = []

    print('Предмет', list(marks.keys())[subj_num])
    print('Оценки', list(marks.values())[subj_num][:-1])
    print('Средняя оценка', list(marks.values())[subj_num][-1])
    current_marks = list(marks.values())[subj_num][:-1]
    print('-----------------------------------------------------------')
    new_marks = input('Какую оценки хотите добавить (перечислите в строчку через прбел): ')
    current_marks += list(map(int, new_marks.split()))
    print(round(np.array(current_marks).mean(), 2))
    while True:
        cont = input('Хотите добавить еще оценок? (y/n)')

        if cont == 'y':
            new_marks = input('Какую оценки хотите добавить (перечислите в строчку через прбел): ')
            current_marks += list(map(int, new_marks.split()))
            print(round(np.array(current_marks).mean(), 2))
        else:
            yn = input('Хотите  выбрать другой предмет ? (y/n)')

            if yn == 'y':
                do_somthing_with_marks(marks, choose_subj(marks))
            else:
                break
            break


# do_somthing_with_marks(ma, choose_subj(ma))

a = pd.read_csv('TEST1.csv')
def main():

    bl = input('есть ли у вас уже .csv с вашими оценками ? (y/n): ')
    if bl == 'y':
        name_of_csv = input('Название scv:' )
        try:
            data = pd.read_csv(name_of_csv.strip() + '.csv')
            marks = prepare_data_from_csv(data)
        except Exception as ex:
            print(ex)
    else:

        datas = open('data.txt', 'r').readlines()
        lg, psw, sch = datas[0].split(':')[-1].strip(), datas[1].split(':')[-1].strip(), datas[2].split(':')[-1].strip()
        data = get_data(login= lg, password=psw, url='https://net-school.cap.ru/', school=sch)
        marks = prepare_data_from_site(data)

    subj_num = choose_subj(marks)
    do_somthing_with_marks(marks, subj_num)


if __name__ == '__main__':
     main()
