from bs4 import BeautifulSoup
import urllib
import requests
from defaults import *
from urllib.parse import urlparse, parse_qs
import validators
import asyncio
import aiohttp


class UrlFetcher:

    def __init__(self, urls, objects_class):
        self.urls = urls
        self.objects_class = objects_class
        self.html_pages = {}

    async def _fetch_url(self, session, url):

        if not validators.url(url):
            url = self.create_full_url(url)

        try:
            async with session.get(url, timeout=20) as response:
                if response.status == 200:
                    html_text = await response.text()
                    self.html_pages[url] = self.objects_class(url=url, html_text=html_text, status_code=response.status)

        except Exception as e:
            self.html_pages[url] = self.objects_class(url=url, connect_exception=e)

    async def _fetch_all(self, session, urls):
        tasks = []
        for url in urls:
            task = asyncio.create_task(self._fetch_url(session, url))
            tasks.append(task)
        await asyncio.gather(*tasks)

    async def start_fetching(self):
        async with aiohttp.ClientSession() as session:
            await self._fetch_all(session, self.urls)

    def create_full_url(self, url):
        if SCHEMA not in url and DOMAIN not in url:
            return SCHEMA + DOMAIN + url
        return url


class AbstractHtmlPage:

    def __init__(self, **kwargs):
        self.url = kwargs.get('url')
        self.status_code = kwargs.get('status_code')
        self.html_text = kwargs.get('html_text')
        self.connect_exception = kwargs.get('connect_exception')
        self.soup = None

    def _get_soup(self):
        if (self.status_code != 200) or (not self.html_text) or self.connect_exception:
            return

        if not self.soup:
            self.soup = BeautifulSoup(self.html_text, 'html.parser')


class HousePage(AbstractHtmlPage):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def create_house_object(self):
        self._get_soup()
        if self.soup:
            house_id_element = self.soup.find("p", {"class": "styles__Id-sc-eng632-2"})
            house_id_text = house_id_element.text
            if house_id_text:
                house_id = house_id_text.split(': ')[1]
            else:
                house_id = ''

            state_element = self.soup.find("label", {"class": "HouseStatus__HouseStatusWrapper-sc-1sb5wh4-0"})
            state = state_element.text

            address_element = self.soup.find("p", {"class": "styles__Address-sc-eng632-11"})
            if address_element:
                address_string = address_element.text
                address = address_string.replace('Адрес: ', '')

            table_elements = self.soup.find_all("div", {"class": "styles__Row-sc-1fyyfia-6"})
            if table_elements:
                floor_count = ''
                flat_count = ''

                for e in table_elements:
                    if e.text.startswith('Количество этажей'):
                        floor_count = e.text.replace('Количество этажей', '')

                    if e.text.startswith('Количество квартир'):
                        flat_count = e.text.replace('Количество квартир', '')

            builder_element = self.soup.find("a", {"class": "styles__LinkContainer-sc-1u7ca6h-0"})
            if builder_element:
                builder_name = builder_element.text

                builder_url = builder_element.attrs.get('href')

            return House(address=address,
                         house_id=house_id,
                         state=state,
                         flat_count=flat_count,
                         floor_count=floor_count,
                         builder_name=builder_name,
                         builder_url=builder_url
                         )


class BuilderPage(AbstractHtmlPage):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.builder_name = kwargs.get('builder_name')
        self.builder_inn = kwargs.get('builder_inn')

    def fetch_builder_info(self):
        self._get_soup()
        if not self.soup:
            return

        h1_element = self.soup.find("h1")
        self.builder_name = h1_element.text

        blocks_with_inn = self.soup.find_all("div", {"class": 'styles__BuilderCardRequisitesBlock-sc-p65t3v-4'})
        for div in blocks_with_inn:
            p_elements = div.find_all("p", {"class": "styles__TypographyP-sc-1txyxb-4"})

            for p in p_elements:
                if p.text == 'ИНН':
                    # Значит в этом div есть данные об ИНН
                    for target_p in p_elements:
                        if target_p.text != 'ИНН':
                            self.builder_inn = target_p.text


class CatalogPage(AbstractHtmlPage):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pagination_links = set()
        self.house_urls = set()

    def _get_soup(self):
        if not self.html_text or self.connect_exception:
            return

        if not self.soup:
            self.soup = BeautifulSoup(self.html_text, 'html.parser')

    def fetch_html_text_without_js(self):
        response = requests.get(self.url)
        self.status_code = response.status_code
        self.html_text = response.text

    def get_links_for_house_pages_from_soup(self):
        self._get_soup()
        if not self.soup:
            return set()
        a_elements = self.soup.find_all("a")
        for a in a_elements:
            href = a.get('href')
            if href and (HOUSE_PAGE_PATH in href):
                self.house_urls.add(href)

        return self.house_urls

    def get_links_for_other_catalog_pages_with_houses(self):
        self._get_soup()

        if self.soup:
            self._get_links_for_catalog_pages_from_soup()

        return self.pagination_links

    def _get_links_for_catalog_pages_from_soup(self):
        ul_pagination_block = self.soup.find("ul", {"class": "pagination"})
        a_pagination_links = ul_pagination_block.find_all('a')
        for link in a_pagination_links:
            try:
                self.pagination_links.add(link['href'])
            except:
                pass

    def get_max_pagination_page_number(self):
        self.get_links_for_other_catalog_pages_with_houses()

        pagination_pages = []
        for pagination_link in self.pagination_links:
            parsed_url = urlparse(pagination_link)
            params = parse_qs(parsed_url.query)
            page_param = params.get('page')
            if page_param:
                pagination_pages.append(int(page_param[0]))

        try:
            max_page = max(pagination_pages)
        except:
            max_page = None

        return max_page


class CheckPage(AbstractHtmlPage):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.average_price = kwargs.get('price_for_meter')
        self.grey_numbers = kwargs.get('grey_numbers')
        self.sold_out = kwargs.get('sold_out')

    def fetch_house_info(self):
        self._get_soup()
        if not self.soup:
            return

        # Чтобы определить цену за квадрат и распроданность, Ищем DIV с классом "styles__Flex-sc-1fvbtz4-2"
        div_elements_with_block_title = self.soup.find_all("div", {"class": "styles__Flex-sc-1fvbtz4-2"})

        for div_with_block_title in div_elements_with_block_title:
            if 'Распроданность квартир' in div_with_block_title.text:
                # Среди соседних DIV нужно найти такой, у которого нет класса. В этом блоке будет нужное значение
                neighbour_div_element = div_with_block_title.parent.find("div", {"class": ""})
                if neighbour_div_element:
                    self.sold_out = neighbour_div_element.text

            elif 'Средняя цена' in div_with_block_title.text:
                # Среди соседних DIV нужно найти такой, у которого нет класса. В этом блоке будет нужное значение
                neighbour_div_element = div_with_block_title.parent.find("div", {"class": ""})
                if neighbour_div_element:
                    self.average_price = neighbour_div_element.text

        # Кадастровые номера
        div_elements_with_grey_numbers = self.soup.find_all("div", {"class": ["styles__Label-sc-16mifxz-0", 'kFAJIQ']})
        for e in div_elements_with_grey_numbers:
            if 'Кадастров' in e.text:
                self.grey_numbers = [div.text for div in e.parent.find_all("div", {"class": ""})]

class House:

    def __init__(self, **kwargs):

        self.house_id = kwargs.get('house_id', '')
        self.address = kwargs.get('address', '')
        self.state = kwargs.get('state', '')
        self.flat_count = kwargs.get('flat_count', '')
        self.floor_count = kwargs.get('floor_count', '')
        self.builder_name = kwargs.get('builder_name', '')
        self.builder_url = kwargs.get('builder_url', '')
        self.check_page_url = kwargs.get('price_for_meter', '')

    def get_check_page_url(self):
        if self.house_id:
            self.check_page_url = SCHEMA + DOMAIN + CHECK_PAGE_PATH + self.house_id
        return self.check_page_url

    def __repr__(self):
        return f'{self.house_id}, {self.address}, {self.state}'

