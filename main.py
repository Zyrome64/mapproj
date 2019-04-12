import pygame
import requests
import sys
import os
import math
import pygame as pg




pg.init()
class Checkbox:
    def __init__(self, surface, x, y, color=(230, 230, 230), caption="", outline_color=(0, 0, 0),
                 check_color=(0, 0, 0), font_size=22, font_color=(0, 0, 0), text_offset=(28, 1)):
        self.surface = surface
        self.x = x
        self.y = y
        self.color = color
        self.caption = caption
        self.oc = outline_color
        self.cc = check_color
        self.fs = font_size
        self.fc = font_color
        self.to = text_offset
        # checkbox object
        self.checkbox_obj = pg.Rect(self.x, self.y, 12, 12)
        self.checkbox_outline = self.checkbox_obj.copy()
        # variables to test the different states of the checkbox
        self.checked = False
        self.active = False
        self.unchecked = True
        self.click = False

    def _draw_button_text(self):
        self.font = pg.font.Font(None, self.fs)
        self.font_surf = self.font.render(self.caption, True, self.fc)
        w, h = self.font.size(self.caption)
        self.font_pos = (self.x + 12 / 2 - w / 2 + self.to[0], self.y + 12 / 2 - h / 2 + self.to[1])
        self.surface.blit(self.font_surf, self.font_pos)

    def render_checkbox(self):
        if self.checked:
            pg.draw.rect(self.surface, self.color, self.checkbox_obj)
            pg.draw.rect(self.surface, self.oc, self.checkbox_outline, 1)
            pg.draw.circle(self.surface, self.cc, (self.x + 6, self.y + 6), 4)

        elif self.unchecked:
            pg.draw.rect(self.surface, self.color, self.checkbox_obj)
            pg.draw.rect(self.surface, self.oc, self.checkbox_outline, 1)
        self._draw_button_text()

    def _update(self, event_object):
        x, y = pg.mouse.get_pos()
        px, py, w, h = self.checkbox_obj
        if px < x < px + w and py < y < py + w:
            if self.checked:
                self.checked = False
            else:
                self.checked = True
            print(str(self.caption) + ' toggle ' + str(self.checked))

    def _mouse_up(self):
            if self.active and not self.checked and self.click:
                    self.checked = True
            elif self.checked:
                self.checked = False
                self.unchecked = True

            if self.click is True and self.active is False:
                if self.checked:
                    self.checked = True
                if self.unchecked:
                    self.unchecked = True
                self.active = False

    def update_checkbox(self, event_object):
        self.click = True
        self._update(event_object)

    def is_checked(self):
        if self.checked is True:
            return True
        else:
            return False

    def is_unchecked(self):
        if self.checked is False:
            return True
        else:
            return False



# Ищем город Якутск, ответ просим выдать в формате json.

FPS = 60

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


def address_full(str_):
    geocoder_request = "http://geocode-maps.yandex.ru/1.x/?geocode={}&format=json".format(str_)
    response = None
    try:
        response = requests.get(geocoder_request)
        if response:
            # Преобразуем ответ в json-объект
            json_response = response.json()
            data = {}
            # Получаем первый топоним из ответа геокодера.
            # Согласно описанию ответа, он находится по следующему пути:
            toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
            # Полный адрес топонима:

            try:
                toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
                data["adress"] = toponym_address
            except:
                pass

            try:
                toponym_address1 = toponym["metaDataProperty"]["GeocoderMetaData"]["Address"]["Components"][1]["name"]
                data["okrug"] = toponym_address1
            except:
                pass

            try:
                toponym_address2 = toponym["metaDataProperty"]["GeocoderMetaData"]["Address"]["Components"][2]["name"]
                data["oblast"] = toponym_address2
            except:
                pass

            try:
                toponym_address3 = \
                    toponym["metaDataProperty"]["GeocoderMetaData"]["AddressDetails"]["Country"]["AdministrativeArea"][
                        "Locality"]["Thoroughfare"]["Premise"]["PostalCode"]["PostalCodeNumber"]
                data["postal code"] = toponym_address3
            except:
                pass

            # Координаты центра топонима:
            try:
                toponym_coodrinates = toponym["Point"]["pos"]
                data["pos"] = toponym_coodrinates
            except:
                pass

            # Печатаем извлечённые из ответа поля:
            return (data)
        else:
            print("Ошибка выполнения запроса:")
            print(geocoder_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
    except:
        print("Запрос не удалось выполнить. Проверьте подключение к сети Интернет.")



class list_of_sputniks:
    def __init__(self):
        self.data = []
        self.dat = []
        self.types = ['sat', 'map', 'sat,skl']
        self.markers = []
        self.lines = []
        self.speed = [0, 300, 90, 60, 20, 10, 8, 6, 4, 2, 1.5, 1.2, 1, 0.8, 0.7, 0.4, 0.15, 0.06, 0.02, 0.01, 0.005]
        self.index = 0


    def appen(self, coord, spn, type, markers, lines):
        self.coord = coord
        self.spn = spn
        self.b = int(17 * (0.9 ** (int(self.spn) - 1)))
        self.markers += markers
        self.lines = lines
        response = None
        try:
            self.host = 'http://static-maps.yandex.ru/1.x/?ll={}&z={}&l={}'.format(self.coord, self.spn, self.types[self.index])
            if markers:
                self.host += '&pt='
                for i in range(len(markers)):
                    if i < len(markers) - 1:
                        self.host += markers[i] + ',pm2rdm~'
                    else:
                        self.host += markers[i] + ',pm2rdm'
            if lines:
                self.host += '&pl=c:ec473fFF,f:00FF00A0, w:7'
                for x in lines:
                    self.host += ',' + x
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
        if float(spn) < 19 and float(spn) > 0:
            self.spn = str(spn)
            print(self.spn)



    def move(self, x, y):
        coor = [float(i) for i in self.coord.split(',')]
        x, y = x * self.speed[int(self.spn)], y * self.speed[int(self.spn)]
        coor[0] += x
        coor[1] += y
        print(','.join(map(str, coor)))
        if coor[0] > 175:
            coor[0] = 175
        elif coor[0] < -175:
            coor[0] = -175
        if coor[1] < -85:
            coor[1] = -85
        elif coor[1] > 85:
            coor[1] = 85
        self.coord = ','.join(map(str, coor))

    def add_mark(self, coor):
        self.markers.append(coor)

    def remove_marker(self):
        if self.markers:
            self.markers.pop(0)

    def update(self):
        try:
            self.host = 'http://static-maps.yandex.ru/1.x/?ll={}&z={}&l={}'.format(self.coord, self.spn, self.types[self.index])
            if self.markers:
                self.host += '&pt='
                for i in range(len(self.markers)):
                    if i < len(self.markers) - 1:
                        self.host += self.markers[i] + ',pm2rdm~'
                    else:
                        self.host += self.markers[i] + ',pm2rdm'
            if self.lines:
                self.host += '&pl=c:ec473fFF,f:00FF00A0, w:7'
                for x in self.lines:
                    self.host += ',' + x

            map_request = self.host  # 0.002
            response = requests.get(map_request)

            if not response:
##                print("Ошибка выполнения запроса:")
##                print(geocoder_request)
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
        self.data[self.index] = map_file
        self.dat[self.index] = pygame.image.load(map_file)



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
info_font = pygame.font.Font(None, 20)
infocoor_font = pygame.font.Font(None, 13)

clock = pygame.time.Clock()
input_box = pygame.Rect(int(size[0] - 250), 5, 140, 32)
back_text = pygame.Rect(0, 0, size[0], 42)
info_rect = pygame.Rect(5, 47, 150, 200)
chkbox = Checkbox(screen, info_rect.left + 10, info_rect.bottom - 50)
color_inactive = pygame.Color('lightskyblue3')
color_active = pygame.Color('dodgerblue2')
color = color_inactive
active = False
text = ''
info_text = ''
coor_text = ''
postal_code = ''
city = ''
done = False
btn_rect = pygame.Rect(info_rect.left + 5, info_rect.bottom - 30, info_rect.width - 10, 25)

clock = pygame.time.Clock()
h.appen(coordin, spns, 'sat', [], [])
h.appen(coordin, spns, 'map', [], [])
h.appen(coordin, spns, 'sat,skl', [], [])
screen = pygame.display.set_mode((600, 450))
arrow_keys_pressed = {'up': False, 'down': False, 'right': False, 'left': False}
##shift = [0, 0]
flag = True
do = True
while flag:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            flag = False


        if event.type == pygame.MOUSEBUTTONDOWN:
            if btn_rect.collidepoint(event.pos):
                print('!!!!!!!')
                info_text = ''
                coor_text = ''
                postal_code = ''
                h.markers = []
                do = True
            if input_box.collidepoint(event.pos):
                active = not active
            else:
                active = False

            chkbox.update_checkbox(event)
            if chkbox.is_checked():
                try:
                    postal_code = address_full(city)['postal code']
                except Exception as a:
                    postal_code = 'No PCode'
            else:
                postal_code = ''

            color = color_active if active else color_inactive


        if event.type == pygame.KEYDOWN:
            if not active:
                if event.key == pygame.K_a:
                    h.index -= 1
                    if h.index < 0:
                        h.index = len(h.dat) - 1
                    do = True
                elif event.key == pygame.K_d:
                    h.index += 1
                    if h.index > len(h.dat) - 1:
                        h.index = 0
                    do = True

            else:
                if event.key == pygame.K_RETURN:
                    print(text)
                    try:
                        try:
                            float(text.split(',')[0])
                            info_text = address_full(text)['adress']
                        except:
                            try:
                                print(address_full(text)['pos'])
                                info_text = address_full(text)['adress']
                            except Exception:
                                pass
                            do = True
                        coor_text = address_full(text)['pos']
                        h.coord = ','.join(address_full(text)['pos'].split())
                        h.markers = [','.join(address_full(text)['pos'].split())]
                        if chkbox.is_checked():
                            try:
                                postal_code = address_full(text)['postal code']
                            except Exception as a:
                                postal_code = 'No PCode'
                        else:
                            postal_code = ''
                        h.spn = '8'
                        city = text
                        text = ''
                        active = False
                    except  Exception as a:
                        print(a)
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    text += event.unicode

            if event.key == pygame.K_PAGEUP:
                h.pg_updn(False)
                do = True
            elif event.key == pygame.K_PAGEDOWN:
                h.pg_updn(True)
                do = True

            elif event.key == pygame.K_RIGHT:
                arrow_keys_pressed['right'] = True
                arrow_keys_pressed['left'] = False
##                shift[0] = 0.01
            elif event.key == pygame.K_LEFT:
                arrow_keys_pressed['left'] = True
                arrow_keys_pressed['right'] = False
##                shift[0] = -0.01
            elif event.key == pygame.K_UP:
                arrow_keys_pressed['up'] = True
                arrow_keys_pressed['down'] = False
##                shift[1] = 0.01
            elif event.key == pygame.K_DOWN:
                arrow_keys_pressed['down'] = True
                arrow_keys_pressed['up'] = False
##                shift[1] = -0.01
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT:
                arrow_keys_pressed['right'] = False
            elif event.key == pygame.K_LEFT:
                arrow_keys_pressed['left'] = False
            elif event.key == pygame.K_UP:
                arrow_keys_pressed['up'] = False
            elif event.key == pygame.K_DOWN:
                arrow_keys_pressed['down'] = False
    if arrow_keys_pressed['right']:
        h.move(0.01, 0)
        do = True
    elif arrow_keys_pressed['left']:
        h.move(-0.01, 0)
        do = True
    if arrow_keys_pressed['up']:
        h.move(0, 0.01)
        do = True
    elif arrow_keys_pressed['down']:
        h.move(0, -0.01)
        do = True
        

    screen.fill((30, 30, 30))

    if do:
        h.update()
        do = False

    screen.blit(h.dat[h.index], (0, 0))

    pygame.draw.rect(screen,  (40, 40, 40, 1), back_text)
    pygame.draw.rect(screen, (40, 40, 40, 1), info_rect)

    txt_surface = font.render(text, True, color)
    adr_surface = info_font.render(info_text, True, color_inactive)
    coor_surface = infocoor_font.render(coor_text, True, color_inactive)
    postal_surface = font.render(postal_code, True, color_inactive)
    chkbox_text = pygame.font.Font(None, 15).render('Почтовый индекс', True, color_inactive)
    btn_text = pygame.font.Font(None, 17).render('Сбросить результаты', True, (0, 255, 255))

    width = max(200, txt_surface.get_width() + 10)
    input_box.w = width
    input_box.x = int(size[0] - input_box.w - 50)

    pygame.draw.rect(screen, color, input_box, 2)
    pygame.draw.rect(screen, (255, 0, 0), btn_rect)
    screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
    screen.blit(adr_surface, (info_rect.x + 5, info_rect.y + 5))
    screen.blit(coor_surface, (info_rect.x + 5, info_rect.y + 25))
    screen.blit(postal_surface, (info_rect.x + 5, info_rect.y + 45))

    width2 = max(150, adr_surface.get_width() + 5)
    info_rect.w = width2
    btn_rect = pygame.Rect(info_rect.left + 5, info_rect.bottom - 30, info_rect.width - 10, 25)

    pygame.draw.rect(screen, color, input_box, 2)
    screen.blit(chkbox_text, (15 + chkbox.x, chkbox.y + 1))
    screen.blit(btn_text, (btn_rect.x + (btn_rect.w // 2) - 65, btn_rect.y + 7))


    chkbox.render_checkbox()


    # Переключаем экран и ждем закрытия окна.
    pygame.display.flip()
    clock.tick(FPS)
pygame.quit()