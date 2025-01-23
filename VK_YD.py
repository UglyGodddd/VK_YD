import configparser
import requests
import json
from tqdm import tqdm
import configparser

config = configparser.ConfigParser()
config.read('tokens.ini')

vk_token = config['TOKENS']['vk_token']
yd_token = config['TOKENS']['yd_token']
vk_id = config['ID']['vk_id']

base_vk_url = "https://api.vk.com/method/"
base_yd_url = "https://cloud-api.yandex.net/v1/disk"

class VKYD:
    def __init__(self, vk_token, vk_id, yd_token, version = "5.131"):
        self.token_vk = vk_token
        self.id = vk_id
        self.version = version
        self.token_yd = yd_token
        self.type_size = 's'
        self.headers = {
            "Authorization": f"OAuth {self.token_yd}"
        }
    
    def get_photos(self):
        params = {
            "owner_id": self.id, 
            "album_id":"profile",
            "extended": "1",
            "access_token":self.token_vk,
            "v": self.version,
            }
        url = f'{base_vk_url}/photos.get'
        respone = requests.get(url, params=params)
        data_dict = respone.json()
        photos_url_list = []
        likes_count_list = []
        photos_data = data_dict['response']['items']
        
        for photo_data in photos_data:
            for photo in photo_data['sizes']:
                type_size = photo['type']
                if type_size == self.type_size:
                    likes_count_list.append(photo_data['likes']['count'])
                    photos_url_list.append(photo['url'])
                    continue
        
        base_url_photo = list(zip(likes_count_list, photos_url_list))

        return base_url_photo
        
    def create_folder(self, folder_name):
        base_yd_url = "https://cloud-api.yandex.net/v1/disk"
        url = f'{base_yd_url}/resources'
        params={'path': folder_name}
        response = requests.put(url, headers=self.headers, params=params)
        if response.status_code == 201:
            print(f'Папка с названием - {folder_name} успешно создана')
        elif response.status_code == 409:
            print(f'Папка с данным названием - {folder_name} уже существует ')
        elif response.status_code == 507:
            print(f'Недостаточно свободного места на Я.Диске для создания папки')

    def send_photos(self, photos_list, folder_name, count = 5):
        file_info = []
        photos_list = photos_list[:count]
        url = f'{base_yd_url}/resources/upload'
        with tqdm(total = len(photos_list), desc = 'Загрузка фото', unit='фото') as pbar:
            for like, photo in photos_list:
                file_name = f"{like}.jpg"
                file_path = f'{folder_name}/{file_name}'
                params = {
                    "path": file_path,
                    'url': photo
                    }
                response = requests.post(url, headers=self.headers, params=params)
                if 300 > response.status_code >= 200:  
                    file_info.append({
                        'file_name': file_name,
                        'size': self.type_size
                    })
                else:
                    print(f"Ошибка загрузки {file_name}: {response.status_code}")
                
                pbar.update(1)
        
        with open('photos_info.json', 'w', encoding='utf-8') as json_file:
            json.dump(file_info,json_file)
            print('Информационный файл создан')
        










if __name__ == '__main__':
    folder_name = 'VK_Photos'
    vk_yd = VKYD(vk_token, vk_id, yd_token)
    
    photos_list = vk_yd.get_photos()
    vk_yd.create_folder(folder_name)
    vk_yd.send_photos(photos_list, folder_name)
    
    
