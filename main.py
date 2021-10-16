import json

import requests

import time

from tqdm import tqdm


token_vk = '958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008'
token_yd = ''


class VkUser:
    url = 'https://api.vk.com/method/'

    def __init__(self, token):
        self.params = {
            'access_token': token,
            'v': '5.131'
        }

    def get_info(self, user_id):
        info_url = self.url + 'users.get'
        info_params = {
            'user_id': user_id,
        }
        res = requests.get(url=info_url, params={**self.params, **info_params}).json()
        return res

    def get_photo(self, user_id):
        photo_url = self.url + 'photos.get'
        photo_params = {
            'extended': 1,
            'photo_sizes': 1,
            'album_id': 'profile',
            'owner_id': user_id
        }
        res = requests.get(url=photo_url, params={**self.params, **photo_params}).json()
        info_about_photo = {}
        id = 0
        all_likes = []
        for item in res['response']['items']:
            likes = item['likes']['count']
            all_likes.append(likes)
        for item in res['response']['items']:
            id += 1
            likes = item['likes']['count']
            photo = item['sizes'][-1]['url']
            date = item['date']

            for sizes in item['sizes']:
                size = sizes['type']
                info_about_photo[id] = [photo, likes, size, date]
        id = 0
        for like in all_likes:
            id += 1
            if all_likes.count(like) == 1:
                photo_name = like
                info_about_photo[id].append(photo_name)
            else:
                photo_name = f'{like}_{info_about_photo.get(id)[3]}'
                info_about_photo[id].append(photo_name)
        return info_about_photo


class YandexDisk:

    def __init__(self, token):
        self.token = token

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token)
        }

    def get_folder(self, name):
        url = 'https://cloud-api.yandex.net/v1/disk/resources/'
        headers = self.get_headers()
        params = {
            'path': name
        }
        response = requests.put(url=url, headers=headers, params=params)
        return response.json()

    def download_by_link(self, link, photo_name):
        upload_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        headers = self.get_headers()
        params = {'path': f"{name}/{photo_name}", 'url': link}
        response = requests.post(url=upload_url, params=params, headers=headers)
        return response.json()


if __name__ == '__main__':
    id_user_vk = input('Введите ID пользоввателя vk.com: ')
    if id_user_vk.isdigit() is True:
        user = VkUser(token_vk)
        for item in user.get_info(id_user_vk)['response']:
            name = f"Фото профиля vk.com {item['first_name']} {item['last_name']} (id {item['id']})"
            print(name)
        all_photos = user.get_photo(id_user_vk)
        yandex = YandexDisk(token_yd)
        yandex.get_folder(name)
        photos_list = []
        for keys, values in tqdm(all_photos.items()):
            yandex.download_by_link(values[0], values[4])
            photo_vk = {'file_name': f"{values[4]}.jpg", 'size': f"{values[2]}"}
            photos_list.append(photo_vk)
            time.sleep(1)
        print(f'{len(all_photos.items())} фотографий успешно загружены на Яндекс.Диск')
        with open('photo_vk.json', 'w') as f:
            json.dump(photos_list, f, ensure_ascii=False, indent=2)
    else:
        print('ID пользователя введен неверно')
        