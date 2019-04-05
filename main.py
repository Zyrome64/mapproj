import pygame
import requests
import sys
import os
import math

# Ищем город Якутск, ответ просим выдать в формате json.



# Определяем функцию, считающую расстояние между двумя точками, заданными координатами
def lonlat_distance(a, b):

    degree_to_meters_factor = 111 * 1000 # 111 километров в метрах
    a_lon, a_lat = map(float, a.split(','))
    b_lon, b_lat = map(float, b.split(','))

    # Берем среднюю по широте точку и считаем коэффициент для нее.
    radians_lattitude = math.radians((a_lat + b_lat) / 2.)
    lat_lon_factor = math.cos(radians_lattitude)

    # Вычисляем смещения в метрах по вертикали и горизонтали.
    dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
    dy = abs(a_lat - b_lat) * degree_to_meters_factor

    # Вычисляем расстояние между точками.
    distance = round(math.sqrt(dx * dx + dy * dy), 1)

    return int(distance) if distance % 1 == 0 else distance



def get_inf(obj):
    geocoder_request = "http://geocode-maps.yandex.ru/1.x/?geocode={}&format=json".format(obj)
    
    # Выполняем запрос.
    response = None
    try:
        response = requests.get(geocoder_request)
        if response:
            # Преобразуем ответ в json-объект
            json_response = response.json()
    ##        print(json_response["response"]['GeoObjectCollection']['featureMember'][0]['GeoObject'].keys())
            # Получаем первый топоним из ответа геокодера.
            # Согласно описанию ответа, он находится по следующему пути:
            toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
            # Печатаем извлечённые из ответа поля:
            return toponym['metaDataProperty']['GeocoderMetaData']['Address']['postal_code']
    ##        print(toponym_address, "имеет координаты:", toponym_coodrinates)
        else:
            print("Ошибка выполнения запроса:")
            print(geocoder_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
    except:
        print("Запрос не удалось выполнить. Проверьте подключение к сети Интернет.")


def get_south(objs):
    ms = None
    for obj in objs:
        geocoder_request = "http://geocode-maps.yandex.ru/1.x/?geocode={}&format=json".format(obj)
        response = None
        try:
            response = requests.get(geocoder_request)
            if response:
                json_response = response.json()
                toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
                if ms is None:
                    ms = [obj, toponym['Point']['pos']]
##                else:
##                    print( ms[1].split()[1], toponym['Point']['pos'].split()[1])
                elif float(ms[1].split()[1]) > float(toponym['Point']['pos'].split()[1]):
                    ms = [obj, toponym['Point']['pos']]
            else:
                print("Ошибка выполнения запроса:")
                print(geocoder_request)
                print("Http статус:", response.status_code, "(", response.reason, ")")
                return
        except:
            print("Запрос не удалось выполнить. Проверьте подключение к сети Интернет.")
            return
    if ms is not None:
        return ms[0]


def pic(coords, spn, type_, arg=None):
    response = None
    try:
## 55.817844, 37.440578 спартак, 55.791703, 37.560535 динамо, 55.715955, 37.553651 лужники
        if arg is None:
            map_request = "http://static-maps.yandex.ru/1.x/?ll={}&spn={}&l={}".format(coords, spn, type_)
        else:
            map_request = "http://static-maps.yandex.ru/1.x/?ll={}&spn={}&l={}&{}".format(coords, spn, type_, arg)
        response = requests.get(map_request)
    
        if not response:
##            print("Ошибка выполнения запроса:")
##            print(geocoder_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)
    except:
        print("Запрос не удалось выполнить. Проверьте наличие сети Интернет.")
        sys.exit(1)

     
    # Запишем полученное изображение в файл.
    map_file = "map.png"
    try:
        with open(map_file, "wb") as file:
            file.write(response.content)
    except IOError as ex:
        print("Ошибка записи временного файла:", ex)
        sys.exit(2)

     
    # Инициализируем pygame
    pygame.init()
    screen = pygame.display.set_mode((600, 450))
    # Рисуем картинку, загружаемую из только что созданного файла.
    screen.blit(pygame.image.load(map_file), (0, 0))
    # Переключаем экран и ждем закрытия окна.
    pygame.display.flip()
    while pygame.event.wait().type != pygame.QUIT:
        pass
    pygame.quit()


    # Удаляем за собой файл с изображением.
    os.remove(map_file)


def slideshow(coords_list):
    for i, tup in enumerate(coords_list):
        coords, spn = tup
        response = None
        try:
    ## 55.817844, 37.440578 спартак, 55.791703, 37.560535 динамо, 55.715955, 37.553651 лужники
            map_request = "http://static-maps.yandex.ru/1.x/?ll={}&spn={}&l=sat".format(coords, spn)
            response = requests.get(map_request)
            if not response:
    ##            print("Ошибка выполнения запроса:")
    ##            print(geocoder_request)
                print("Http статус:", response.status_code, "(", response.reason, ")")
                sys.exit(1)
        except:
            print("Запрос не удалось выполнить. Проверьте наличие сети Интернет.")
            sys.exit(1)

         
        # Запишем полученное изображение в файл.
        map_file = "{}.png".format(str(i))
        try:
            with open(map_file, "wb") as file:
                file.write(response.content)
        except IOError as ex:
            print("Ошибка записи временного файла:", ex)
            sys.exit(2)

     
    # Инициализируем pygame
    pygame.init()
    screen = pygame.display.set_mode((600, 450))
    cur_im = 0
    screen.blit(pygame.image.load('{}.png'.format(str(cur_im))), (0, 0))
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                break
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                cur_im += 1
                if cur_im >= len(coords_list):
                    cur_im = 0
                screen.blit(pygame.image.load('{}.png'.format(str(cur_im))), (0, 0))
                # Переключаем экран и ждем закрытия окна.
                pygame.display.flip()
        else:
            continue
        break
    pygame.quit()


    # Удаляем за собой файл с изображением.
    for i in range(len(coords_list)):
        os.remove(str(i) + '.png')

##for loc in ['петровка 38']:
##    print(loc, '\t', get_inf(loc))
##path = ['30.312300,59.941372', '30.313533,59.944456', '30.311844,59.946254', '30.294017,59.946655', '30.270461,59.953577', '30.264769,59.956766', '30.257398,59.957523', '30.212623,59.966225', '29.913233,59.891882']
##print(lonlat_distance(input('Введите долготу и широту первой точки через запятую - '), input('Введите долготу и широту второй точки через запятую - ')), 'м')
##pic('30.119060,59.932104', '0.2,0.2', 'map', 'pl=' + ','.join(path))
# slideshow([('-52.837122,47.191585', '0.001,0.001'), ('46.061245,51.529056', '0.001,0.001'), ('68.775195,38.564725', '0.05,0.05')])











def sputnik_im(coord, spn, type, markers, lines):
    response = None
    try:
        host = "http://static-maps.yandex.ru/1.x/?ll={}&spn={}&l={}".format(coord, spn, type)
        if markers:
            host += '&pt='
            for i in range(len(markers)):
                if i < len(markers) - 1:
                    host += markers[i] + ',pm2rdm~'
                else:
                    host += markers[i] + ',pm2rdm'
        if lines:
            host += '&pl=c:ec473fFF,f:00FF00A0, w:7'
            for x in lines:
                host += ',' + x
        map_request = host  # 0.002
        # "http://static-maps.yandex.ru/1.x/?ll={}&spn={}&l={}&pt={},pm2rdm~{},pm2rdm~{},pm2rdm&pl=c:ec473fFF,f:00FF00A0, w:7,30.015249,59.865990,30.114517,59.946595,30.191421,59.970402,30.273819,59.952891,30.310705,59.945413"
        response = requests.get(map_request)

        if not response:
            print("Ошибка выполнения запроса:")
            print(geocoder_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)
    except:
        print("Запрос не удалось выполнить. Проверьте наличие сети Интернет.")
        sys.exit(1)

    # Запишем полученное изображение в файл.
    map_file = "map.png"
    try:
        with open(map_file, "wb") as file:
            file.write(response.content)
    except IOError as ex:
        print("Ошибка записи временного файла:", ex)
        sys.exit(2)

    # Инициализируем pygame
    pygame.init()
    screen = pygame.display.set_mode((600, 450))
    # Рисуем картинку, загружаемую из только что созданного файла.
    screen.blit(pygame.image.load(map_file), (0, 0))
    # Переключаем экран и ждем закрытия окна.
    pygame.display.flip()
    while pygame.event.wait().type != pygame.QUIT:
        pass
    pygame.quit()

    # Удаляем за собой файл с изображением.
    os.remove(map_file)



class list_of_sputniks:
    def __init__(self):
        self.data = []
        self.dat = []
        self.index = 0
    def appen(self, coord, spn, type):
        self.coord = coord
        self.spn = spn
        self.type = type
        response = None
        try:
            self.host = 'http://static-maps.yandex.ru/1.x/?ll={}&spn={}&l={}'.format(self.coord, self.spn, self.type)
            map_request = self.host  # 0.002
            response = requests.get(map_request)

            if not response:
                print("Ошибка выполнения запроса:")
                print(geocoder_request)
                print("Http статус:", response.status_code, "(", response.reason, ")")
                sys.exit(1)
        except:
            print("Запрос не удалось выполнить. Проверьте наличие сети Интернет.")
            sys.exit(1)

        # Запишем полученное изображение в файл.
        map_file = "map.png"
        try:
            with open(map_file, "wb") as file:
                file.write(response.content)
        except IOError as ex:
            print("Ошибка записи временного файла:", ex)
            sys.exit(2)
        self.data.append(map_file)
        self.dat.append(pygame.image.load(map_file))


    def pg_updn(self, minusBool):
        spn = [str(float(x) - 0.05) if minusBool else str(float(x) + 0.05) for x in self.spn.split(',')]
        self.spn = ','.join(spn)
        print(self.spn)

    def move(self, x, y):
        coor = [float(i) for i in self.coord.split(',')]
        coor[0] += x
        coor[1] += y
        self.coord = coor




# Инициализируем pygame
pygame.init()
h = list_of_sputniks()
coordin = input()
spns = input()
# '29.962672,59.943050'    '0.3,0.3'
coordin = '29.962672,59.943050'
spns = '0.3,0.3'
h.appen(coordin, spns, 'sat')
h.appen(coordin, spns, 'map')
h.appen(coordin, spns, 'sat,skl')
screen = pygame.display.set_mode((600, 450))
flag = True
while flag:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            flag = False
            pygame.quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                h.index -= 1
                if h.index < 0:
                    h.index = len(h.dat) - 1
            elif event.key == pygame.K_d:
                h.index += 1
                if h.index > len(h.dat) - 1:
                    h.index = 0
            elif event.key == pygame.K_PAGEUP:
                h.pg_updn(False)
            elif event.key == pygame.K_PAGEDOWN:
                h.pg_updn(True)
            elif event.key == pygame.K_LEFT:
                h.move(0.01, 0)
            elif event.key == pygame.K_RIGHT:
                h.move(-0.01, 0)
            elif event.key == pygame.K_UP:
                h.move(0, 0.01)
            elif event.key == pygame.K_DOWN:
                h.move(0, -0.01)
    screen.blit(h.dat[h.index], (0, 0))
    # Переключаем экран и ждем закрытия окна.
    pygame.display.flip()
pygame.quit()
# Рисуем картинку, загружаемую из только что созданного файла.



# sputnik_im('29.962672,59.943050', '0.3,0.3', 'map',
#            ['37.439944,55.817950', '37.560154,55.791408', '37.554787,55.715562'],
#            ['30.015249,59.865990', '30.114517,59.946595', '30.191421,59.970402', '30.273819,59.952891',
#             '30.310705,59.945413'])



