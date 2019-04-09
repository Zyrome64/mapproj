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
        self.types = []
        self.speed = [0, 200, 90, 60, 20, 10, 8, 6, 4, 2, 1.5, 1.2, 1, 0.8, 0.7, 0.4, 0.15, 0.06, 0.02, 0.01, 0.005]
        self.index = 0


    def appen(self, coord, spn, type):
        self.coord = coord
        self.spn = spn
        self.type = type
        self.b = int(17 * (0.9 ** (int(self.spn) - 1)))
        self.types.append(type)
        response = None
        try:
            self.host = 'http://static-maps.yandex.ru/1.x/?ll={}&z={}&l={}'.format(self.coord, self.spn, self.type)
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

        if minusBool:
            spn = int(self.spn) - 1
        else:
            spn = int(self.spn) + 1
        if float(spn) < 20 and float(spn) > 0:
            self.spn = str(spn)
            print(self.spn)



    def move(self, x, y):
        coor = [float(i) for i in self.coord.split(',')]
        x, y = x * self.speed[int(self.spn)], y * self.speed[int(self.spn)]
        coor[0] += x
        coor[1] += y
        print(','.join(map(str, coor)))
        self.coord = ','.join(map(str, coor))


    def update(self, i):
        try:
            self.host = 'http://static-maps.yandex.ru/1.x/?ll={}&z={}&l={}'.format(self.coord, self.spn, self.types[i])
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
        self.data[i] = map_file
        self.dat[i] = pygame.image.load(map_file)



# Инициализируем pygame
pygame.init()
h = list_of_sputniks()
# coordin = input()
# spns = input()
# '29.962672,59.943050'    '0.3,0.3'
coordin = '144.33067200000022,43.94305'
spns = '1'

size = (640, 480)
screen = pygame.display.set_mode(size)
font = pygame.font.Font(None, 32)
clock = pygame.time.Clock()
input_box = pygame.Rect(int(size[0] - 250), 5, 140, 32)
back_text = pygame.Rect(0, 0, size[0], 42)
info_text = pygame.Rect(5, 50, 140, 32)
color_inactive = pygame.Color('lightskyblue3')
color_active = pygame.Color('dodgerblue2')
color = color_inactive
active = False
text = ''
done = False


h.appen(coordin, spns, 'sat')
h.appen(coordin, spns, 'map')
h.appen(coordin, spns, 'sat,skl')
screen = pygame.display.set_mode((600, 450))
shift = (0, 0)
flag = True
while flag:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            flag = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if input_box.collidepoint(event.pos):
                active = not active
            else:
                active = False

            color = color_active if active else color_inactive


        if event.type == pygame.KEYDOWN:
            if not active:
                if event.key == pygame.K_a:
                    h.index -= 1
                    if h.index < 0:
                        h.index = len(h.dat) - 1
                elif event.key == pygame.K_d:
                    h.index += 1
                    if h.index > len(h.dat) - 1:
                        h.index = 0
            else:
                if event.key == pygame.K_RETURN:
                    print(text)
                    text = ''
                    active = False
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    text += event.unicode
            if event.key == pygame.K_PAGEUP:
                h.pg_updn(False)
            elif event.key == pygame.K_PAGEDOWN:
                h.pg_updn(True)
            elif event.key == pygame.K_RIGHT:
                shift = (0.01, 0)
            elif event.key == pygame.K_LEFT:
                shift = (-0.01, 0)
            elif event.key == pygame.K_UP:
                shift = (0, 0.01)
            elif event.key == pygame.K_DOWN:
                shift = (0, -0.01)
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT or event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    shift = (0, 0)
    if shift != (0, 0):
        h.move(shift[0], shift[1])
            

    screen.fill((30, 30, 30))
    h.update(h.index)
    screen.blit(h.dat[h.index], (0, 0))
    pygame.draw.rect(screen,  (25, 25, 25, 1), back_text, 0)
    txt_surface = font.render(text, True, color)
    width = max(200, txt_surface.get_width() + 10)
    input_box.w = width
    input_box.x = int(size[0] - input_box.w - 50)
    screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
    # Blit the input_box rect.
    pygame.draw.rect(screen, color, input_box, 2)
    # Переключаем экран и ждем закрытия окна.
    pygame.display.flip()
pygame.quit()
# Рисуем картинку, загружаемую из только что созданного файла.



# sputnik_im('29.962672,59.943050', '0.3,0.3', 'map',
#            ['37.439944,55.817950', '37.560154,55.791408', '37.554787,55.715562'],
#            ['30.015249,59.865990', '30.114517,59.946595', '30.191421,59.970402', '30.273819,59.952891',
#             '30.310705,59.945413'])








# import pygame as pg
#
#
# def main():
#     screen = pg.display.set_mode((640, 480))
#     font = pg.font.Font(None, 32)
#     clock = pg.time.Clock()
#     input_box = pg.Rect(100, 100, 140, 32)
#     color_inactive = pg.Color('lightskyblue3')
#     color_active = pg.Color('dodgerblue2')
#     color = color_inactive
#     active = False
#     text = ''
#     done = False
#
#     while not done:
#         for event in pg.event.get():
#             if event.type == pg.QUIT:
#                 done = True
#             if event.type == pg.MOUSEBUTTONDOWN:
#                 # If the user clicked on the input_box rect.
#                 if input_box.collidepoint(event.pos):
#                     # Toggle the active variable.
#                     active = not active
#                 else:
#                     active = False
#                 # Change the current color of the input box.
#                 color = color_active if active else color_inactive
#             if event.type == pg.KEYDOWN:
#                 if active:
#                     if event.key == pg.K_RETURN:
#                         print(text)
#                         text = ''
#                     elif event.key == pg.K_BACKSPACE:
#                         text = text[:-1]
#                     else:
#                         text += event.unicode
#
#         screen.fill((30, 30, 30))
#         # Render the current text.
#         txt_surface = font.render(text, True, color)
#         # Resize the box if the text is too long.
#         width = max(200, txt_surface.get_width()+10)
#         input_box.w = width
#         # Blit the text.
#         screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
#         # Blit the input_box rect.
#         pg.draw.rect(screen, color, input_box, 2)
#
#         pg.display.flip()
#         clock.tick(30)
#
#
# if __name__ == '__main__':
#     pg.init()
#     main()
#     pg.quit()

