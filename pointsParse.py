import requests
import json
from bs4 import BeautifulSoup
from userData import users_info
    
HOST = 'https://urfu.ru'
HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'}
FILE_URL = 'https://urfu.ru/api/ratings/info/'
MAIN = '55/'
ORIG = '56/'


# DATABASE FUNCTIONS
async def convert_data(state):
    async with state.proxy() as data:
        if data.state is not None:
            state_name = data.state.split(':')[-1]
        else:
            state_name = 'none'

        converted_data = json.dumps(data.as_dict(), ensure_ascii=False)

        return state_name, converted_data


async def update_userdata(user, state):
    try:
        state_name, converted_data = await convert_data(state)
        await users_info.update_userdata(user, state_name, converted_data)
    except:
        print('update_userdata error')


async def get_userdata(user):
    try:
        return await users_info.get_userdata(user.id)
    except:
        print('get_userdata error')
        return {}


# PARSING
def get_file_names(ident):
    r1 = requests.get(FILE_URL + MAIN + ident[0], headers=HEADERS).json()
    r2 = requests.get(FILE_URL + ORIG + ident[1], headers=HEADERS).json()
    return [r1['url'], r2['url']]


def get_pages(fileNames):
    page1 = requests.get(HOST + fileNames[0], headers=HEADERS)
    page2 = requests.get(HOST + fileNames[1], headers=HEADERS)
    page1.encoding = 'utf-8'
    page2.encoding = 'utf-8'
    return [page1.text, page2.text]


def get_tables(pages, direction):
    try:
        tables = ['', '']
        budgetPlaces = ['error', 'error']

        for i in range(2):
            soup_main = BeautifulSoup(pages[i], 'lxml')
            pointers = soup_main.find_all('div', class_='etableTitle')
            for pointer in pointers:
                direction_name = pointer.find_previous('table').find_previous('table').find_all('tr')[1].find('b').get_text()
                if 'основные места' in pointer.get_text().lower() and direction in direction_name:
                    budgetPlaces[i] = pointer.get_text().lower().split()[-1]
                    tables[i] = str(pointer.find_next())

        return tables, budgetPlaces
    except:
        print(direction, pages, 'error')

    
# POSITION CALCULATIONS
def get_points_position(rows_main, rows_orig, userData):
    points = []
    for row in rows_main:
        try:
            soup = BeautifulSoup(str(row), 'lxml')
            point = soup.find_all('td', class_='td-center')[-2].get_text()
            if int(point) < 30:
                points.append(400)
            else:
                points.append(int(point))
        except:
            points.append(400)

    position = 1
    for point in points:
        if point >= userData:
            position += 1

    potentialPosition = 1
    if rows_orig != []:
        for row in rows_orig:
            try:
                soup = BeautifulSoup(str(row), 'lxml')
                columns = soup.find_all('td', class_='td-center')
                if int(columns[-2].get_text()) > 50 and int(columns[-2].get_text()) >= userData:
                    potentialPosition = rows_orig.index(row) + 2
            except:
                potentialPosition = rows_orig.index(row) + 2

    return position, potentialPosition


def get_number_position(rows_main, rows_orig, user_data, direction):
    in_rating = False
    potential = True
    for row in rows_orig:
        try:
            soup = BeautifulSoup(str(row), 'lxml')
            columns = soup.find_all('td', class_='td-center')
            position = columns[0].get_text()
            number = columns[1].get_text()
            if number == user_data:
                try:
                    if int(columns[-2].get_text()) < 30:
                        user_points = 400
                    else:
                        user_points = int(columns[-2].get_text())
                except:
                    user_points = 400

                in_rating = True
                potential = False
                break
        except:
            print('rating error', direction)

    in_list = True
    if not in_rating:
        in_list = False
        for row in rows_main:
            try:
                soup = BeautifulSoup(str(row), 'lxml')
                columns = soup.find_all('td', class_='td-center')
                position = columns[0].get_text()
                number = columns[1].get_text()
                if number == user_data:
                    try:
                        if int(columns[-2].get_text()) < 30:
                            user_points = 400
                        else:
                            user_points = int(columns[-2].get_text())
                    except:
                        user_points = 400
                        
                    in_list = True
                    break
            except:
                print('list error', direction)
    
    if in_list:
        potential = False
        potentialPosition = 1
        if (not in_rating) and (rows_orig != []):
            potential = True
            for row in rows_orig:
                try:
                    soup = BeautifulSoup(str(row), 'lxml')
                    rating_points = int(soup.find_all('td', class_='td-center')[-2].get_text())
                    if rating_points >= user_points:
                        potentialPosition += 1
                except:
                    potentialPosition += 1
        elif rows_orig == []:
            potential = True

        return position, potentialPosition, potential, in_rating
    else:
        return 'тебя нет в списке :(', 0, False, False


# HANDLING FUNCTIONS
def get_info(tables, budgetPlaces, user_data, choseNumber, direction):
    if budgetPlaces[1] != 'error':
        soup_main = BeautifulSoup(tables[0], 'lxml')
        soup_orig = BeautifulSoup(tables[1], 'lxml')
        rows_main = soup_main.find_all('tr')[2:]
        rows_orig = soup_orig.find_all('tr')[2:]

        info = {}

        if choseNumber:
            position, potentialPosition, potential, in_rating = get_number_position(rows_main, rows_orig, user_data, direction)
        else:
            position, potentialPosition = get_points_position(rows_main, rows_orig, user_data)
            potential = True
            in_rating = False

        if potential:
            if potentialPosition <= int(budgetPlaces[1]):
                potentialPosition = str(potentialPosition) + ' ✅'
            else:
                potentialPosition = str(potentialPosition) + ' 🥲'

        if in_rating:
            if int(position) <= int(budgetPlaces[1]):
                position = position + ' ✅'
            else:
                position = position + ' 🥲'

        info['potential'] = potential
        info['potentialPosition'] = potentialPosition
        info['position'] = position
        info['abiturients'] = len(rows_main)
        info['budgetPlaces'] = budgetPlaces[1]
    else:
        info = {}
        info['potential'] = False
        info['potentialPosition'] = 'error'
        info['position'] = 'error'
        info['abiturients'] = 'error'
        info['budgetPlaces'] = 'error'

    return info


def send_info(ident, user_data, direction, choseNumber):
    fileNames = get_file_names(ident)
    pages = get_pages(fileNames)
    tables, budgetPlaces = get_tables(pages, direction)
    
    info = get_info(tables, budgetPlaces, user_data, choseNumber, direction)
    
    return info