from bs4 import BeautifulSoup
import requests

url = 'https://omgtu.ru/general_information/faculties/'


response = requests.get(url)

soup = BeautifulSoup(response.text, "html.parser")

data = soup.find("div", id="pagecontent")

data2 = data.find("ul").text


with open("file.txt", "w") as file1:
    file1.write(data2)
with open("file.txt", "r") as file1:
    readfile = file1.read()
print(readfile)




