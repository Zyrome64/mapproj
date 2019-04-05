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
slideshow([('-52.837122,47.191585', '0.001,0.001'), ('46.061245,51.529056', '0.001,0.001'), ('68.775195,38.564725', '0.05,0.05')])
