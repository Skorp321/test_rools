import requests

response = requests.get('https://39d33ac4-dd56-435e-9f77-ad8ba6b87376.modelrun.inference.cloud.ru/')

print("Статус ответа:", response)
print("Содержимое ответа (текст):")
print(response.text)