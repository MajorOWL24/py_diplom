
import requests
import json

class VK:
  def __init__(self, token):
    self.token = token
  
  def get_photos(self, id):
    url = "https://api.vk.com/method/photos.get?owner_id=" + id + "&album_id=profile&extended=1&access_token=" + self.token + "&v=5.131"
    r = requests.get(url)
    
    data = {}
    photos_in = r.json()["response"]["items"]
    for photo in photos_in:
      max_size = 0
      url = ""
      size_type = ""
      name = photo["likes"]["count"]
      for size in photo["sizes"]:
        if size["width"] * size["height"] > max_size:
          max_size = size["width"] * size["height"]
          url = size["url"]
          size_type = size["type"]
      if name not in data:
        data[name] = []
      data[name].append({
        "filename": name,
        "size": size_type,
        "type": url.split(".")[-1].split("?")[0],
        "date": photo["date"],
        "url": url
      })
    return data


class Yandex:
  def __init__(self, token):
    self.headers = {
      "Authorization": "OAuth " + token
    }

  def upload(self, folder, name, data):
    url = "https://cloud-api.yandex.net/v1/disk/resources/?path=" + folder
    r = requests.put(url, headers=self.headers)

    url = "https://cloud-api.yandex.net/v1/disk/resources/upload?path=" + folder + "/" + name + "&overwrite=true"
    r = requests.get(url, headers=self.headers).json()
    if "href" in r:
      r = requests.put(r["href"], data=data, headers=self.headers)



vk_id = input('VK id: ')
yandex_token = input('Yandex token: ')
vk_token = '958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008'

vk = VK(vk_token)
ya = Yandex(yandex_token)
photos = vk.get_photos(vk_id)

count = 0
for k in photos:
  count = count + len(photos[k])

print("0/" + str(count))
photos_out = []
i = 1
for likes in photos:
  with_date = False
  if len(photos[likes]) > 1:
    with_date = True
  for photo in photos[likes]:
    name = str(likes)
    if with_date:
      name = name + "_" + str(photo["date"])
    name = name + "." + photo["type"]

    ya.upload("vk", name, requests.get(photo["url"]).content)

    photos_out.append({
      "file_name": name,
      "type": photo["size"]
    })

    print(str(i) + "/" + str(count))
    i = i + 1

f = open("results.json", "w")
f.write(json.dumps(photos_out))
f.close()
