import time
from browser import Browser
from objects import *
import xlsxwriter
from loguru import logger


def replace_url_param(url, param, new_value):
    parsed = urllib.parse.urlsplit(url)
    query_dict = parse_qs(parsed.query)
    query_dict[param][0] = str(new_value)
    query_new = urllib.parse.urlencode(query_dict, doseq=True)
    parsed = parsed._replace(query=query_new)
    return parsed.geturl()


def get_catalog_page_urls(start_catalog_url, max_catalog_page):
    catalog_page_urls = set([start_catalog_url])

    for i in range(max_catalog_page + 1):
        catalog_page_urls.add(replace_url_param(start_catalog_url, 'page', i))

    return catalog_page_urls


def fetch_catalog_pages_with_browser(urls):
    """Получение HTML страниц каталога и извлечение ссылок на новостройки"""
    browser = Browser(headless=True)
    browser.create_browser()
    wait_class_name = 'House'
    catalog_pages = []

    for url in catalog_page_urls:
        html = browser.get_page(url=url, wait_class_name=wait_class_name, delay=80)
        if isinstance(html, Exception):
            RESULTS.catalog_page_errors += 1
        else:
            RESULTS.fetched_catalog_pages += 1
            page = CatalogPage(html_text=html)
            catalog_pages.append(page)

    browser.close_browser()
    return catalog_pages


def get_houses_links_from_catalog_pages(catalog_pages):
    """Возвращает список URL новостроек со страниц каталога"""
    urls_to_houses = set()

    for page in catalog_pages:
        links_for_house_pages = page.get_links_for_house_pages_from_soup()
        urls_to_houses = urls_to_houses | links_for_house_pages

    return urls_to_houses


def fetch_urls_asynchronously(urls, batch_size, objects_class):
    result = {}
    for part in split_iterable_by_batches(list(urls), batch_size=batch_size):
        fetcher = UrlFetcher(part, objects_class=objects_class)
        asyncio.run(fetcher.start_fetching())
        result.update(fetcher.html_pages)

    return result


def create_houses(house_pages):
    """Вернет список созданных объектов домов"""
    houses = {}
    for house_url, house_page in house_pages.items():
        house = house_page.create_house_object()
        if house:
            houses[house_url] = house
            RESULTS.fetched_house_pages += 1
        else:
            RESULTS.house_page_error += 1

    return houses


def get_builders_urls_from_houses(houses):
    builders_urls = set()
    for house_url, house in houses.items():
        if house.builder_url:
            builders_urls.add(house.builder_url)

    return builders_urls


def fetch_builders_info(builders_urls):

    builder_pages = fetch_urls_asynchronously(urls=builders_urls, batch_size=BATCH_SIZE, objects_class=BuilderPage)

    for builder_page in builder_pages.values():
        builder_page.fetch_builder_info()

    return builder_pages

def fetch_informationn_from_check_pages(houses):

    check_page_urls = set()
    for house in houses.values():
        check_page_url = house.get_check_page_url()
        check_page_urls.add(check_page_url)

    check_pages = fetch_urls_asynchronously(urls=check_page_urls, batch_size=BATCH_SIZE, objects_class=CheckPage)

    for check_page in check_pages.values():
        check_page.fetch_house_info()

    return check_pages


def split_iterable_by_batches(iterable, batch_size):
    for i in range(0, len(iterable) + 1, batch_size):
        yield iterable[i: i + batch_size]


def write_xlsx(houses, builders, check_pages):
    workbook = xlsxwriter.Workbook(f'{OUTPUT_FILE_NAME}.xlsx')
    worksheet = workbook.add_worksheet()
    paste_title_into_worksheet(worksheet)

    for num, house in enumerate(houses.values(), start=1):
        builder = builder_pages.get(house.builder_url)
        check_page = check_pages.get(house.check_page_url)

        worksheet.write(num, COL_NUM, num)
        worksheet.write(num, COL_ADDRESS, house.address)
        worksheet.write(num, COL_FLAT_COUNT, house.flat_count)
        worksheet.write(num, COL_FLOOR_COUNT, house.floor_count)
        worksheet.write(num, COL_STATE, house.state)

        if builder:
            worksheet.write(num, COL_BUILDER_INN, builder.builder_inn)
            worksheet.write(num, COL_BUILDER, builder.builder_name)

        if check_page:
            worksheet.write(num, COL_SOLD_OUT, check_page.sold_out)
            worksheet.write(num, COL_AVERAGE_PRICE, check_page.average_price)
            worksheet.write(num, COL_GREY_NUMBERS, ', '.join(check_page.grey_numbers))

    workbook.close()


def paste_title_into_worksheet(worksheet):
    worksheet.write(0, COL_NUM, 'Номер')
    worksheet.write(0, COL_ADDRESS, 'Адрес')
    worksheet.write(0, COL_STATE, 'Статус')
    worksheet.write(0, COL_FLOOR_COUNT, 'Количество квартир')
    worksheet.write(0, COL_FLAT_COUNT, 'Количество этажей')
    worksheet.write(0, COL_SOLD_OUT, 'Распроданность квартир')
    worksheet.write(0, COL_AVERAGE_PRICE, 'Средняя цена за 1 м²')
    worksheet.write(0, COL_GREY_NUMBERS, 'Кадастровые номера земельного участка')
    worksheet.write(0, COL_BUILDER, 'Застройщик')
    worksheet.write(0, COL_BUILDER_INN, 'ИНН застройщика')


def print_results():

    logger.info(f'Загружено страниц каталога {RESULTS.fetched_catalog_pages}')
    logger.info(f'Ошибки при загрузке страниц каталога {RESULTS.catalog_page_errors}')
    logger.info(f'Загружено страниц новостроек {RESULTS.fetched_house_pages}')
    logger.info(f'Ошибки при загрузке страниц новостроек {RESULTS.house_page_error}')
    logger.info(f'Время работы скрипта {int(time.time() - RESULTS.start)} сек')


if __name__ == '__main__':

    logger.info('Начало работы скрипта')
    logger.info('Загрузка первой страницы каталога')
    start_catalog_url = SCHEMA + DOMAIN + CATALOG_PAGE_PATH + f'?limit={CATALOG_PAGE_LIMIT}&page=0'
    first_catalog_page = CatalogPage(url=start_catalog_url)
    first_catalog_page.fetch_html_text_without_js()

    # Получение номера последней страницы каталога
    max_catalog_page = first_catalog_page.get_max_pagination_page_number()

    # Генерация url-ов всех страниц каталога
    catalog_page_urls = get_catalog_page_urls(start_catalog_url, max_catalog_page)

    logger.info(f'Загрузка страниц каталога. Будет загружено {CATALOG_PAGE_FETCH_LIMIT} страниц(ы).')
    catalog_page_urls = list(catalog_page_urls)[0:CATALOG_PAGE_FETCH_LIMIT]

    # Получение HTML страниц каталога и извлечение ссылок на новостройки
    catalog_pages = fetch_catalog_pages_with_browser(catalog_page_urls)

    logger.info('Получение со страниц каталога ссылок на новостройки.')
    houses_urls = get_houses_links_from_catalog_pages(catalog_pages)

    logger.info('Загрузка страниц новостроек.')
    house_pages = fetch_urls_asynchronously(urls=houses_urls, batch_size=BATCH_SIZE, objects_class=HousePage)

    logger.info('Получение искомых элементов на страницах новостроек и создание объектов домов.')
    houses = create_houses(house_pages)

    logger.info('Создание списка застройщиков.')
    builders_urls = get_builders_urls_from_houses(houses)

    logger.info('Получение ИНН со страниц застройщиков.')
    builder_pages = fetch_builders_info(builders_urls)

    logger.info('Получение информации со страниц проверки новостройки.')
    check_pages = fetch_informationn_from_check_pages(houses)

    logger.info(f'Запись информации в файл {OUTPUT_FILE_NAME}.')
    write_xlsx(houses=houses, builders=builder_pages, check_pages=check_pages)
    logger.info(f'Файл записан, работа завершена. Результаты:')

    print_results()
