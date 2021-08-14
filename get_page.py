import requests
import bs4
from objects import *

url = 'https://xn--80az8a.xn--d1aqf.xn--p1ai/%D1%81%D0%B5%D1%80%D0%B2%D0%B8%D1%81%D1%8B/%D0%BA%D0%B0%D1%82%D0%B0%D0%BB%D0%BE%D0%B3-%D0%BD%D0%BE%D0%B2%D0%BE%D1%81%D1%82%D1%80%D0%BE%D0%B5%D0%BA/%D0%BE%D0%B1%D1%8A%D0%B5%D0%BA%D1%82/30321'

url = 'https://xn--80az8a.xn--d1aqf.xn--p1ai/%D1%81%D0%B5%D1%80%D0%B2%D0%B8%D1%81%D1%8B/%D0%B5%D0%B4%D0%B8%D0%BD%D1%8B%D0%B9-%D1%80%D0%B5%D0%B5%D1%81%D1%82%D1%80-%D0%B7%D0%B0%D1%81%D1%82%D1%80%D0%BE%D0%B9%D1%89%D0%B8%D0%BA%D0%BE%D0%B2/%D0%B7%D0%B0%D1%81%D1%82%D1%80%D0%BE%D0%B9%D1%89%D0%B8%D0%BA/2666'

url = 'https://xn--80az8a.xn--d1aqf.xn--p1ai/%D1%81%D0%B5%D1%80%D0%B2%D0%B8%D1%81%D1%8B/%D0%BF%D1%80%D0%BE%D0%B2%D0%B5%D1%80%D0%BA%D0%B0_%D0%BD%D0%BE%D0%B2%D0%BE%D1%81%D1%82%D1%80%D0%BE%D0%B5%D0%BA/34861'

r = requests.get(url)

print(r.status_code)

obj = CheckPage(html_text=r.text, status_code=r.status_code, url=url)

obj.fetch_house_info()

# h_obj = h.create_house_object()

print(obj)


#
# soup = bs4.BeautifulSoup(r.text)
#
# house_id_element = soup.find("p", {"class": "styles__Id-sc-eng632-2"})
#
# house_id = house_id_element.text
#
#
# state_element = soup.find("label", {"class": "HouseStatus__HouseStatusWrapper-sc-1sb5wh4-0"})
# state = state_element.text
#
# address_element = soup.find("p", {"class": "styles__Address-sc-eng632-8"})
# address = address_element.text
#
# table_elements = soup.find_all("div", {"class": "styles__Row-sc-1fyyfia-6"})
#
#
# floor_count = ''
# flat_count = ''
# for e in table_elements:
#     if e.text.startswith('Количество этажей'):
#         floor_count = e.text.replace('Количество этажей', '')
#
#     if e.text.startswith('Количество квартир'):
#         flat_count = e.text.replace('Количество квартир', '')
#
#
# builder_element = soup.find("a", {"class": "styles__LinkContainer-sc-1u7ca6h-0"})
# builder = builder_element.text
# builder_url = builder_element.attrs.get('href')
# builder_inn = None
#
#
#
#
#
