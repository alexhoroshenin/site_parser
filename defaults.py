import time

SCHEMA = 'https://'

# наш.дом.рф
DOMAIN = 'xn--80az8a.xn--d1aqf.xn--p1ai'

# '/сервисы/каталог-новостроек/список-объектов/список'
CATALOG_PAGE_PATH = \
    '/%D1%81%D0%B5%D1%80%D0%B2%D0%B8%D1%81%D1%8B/' \
    '%D0%BA%D0%B0%D1%82%D0%B0%D0%BB%D0%BE%D0%B3-%D0%BD%D0%BE%D0%B2%D0%BE%D1%81%D1%82%D1%80%D0%BE%D0%B5%D0%BA/' \
    '%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA-%D0%BE%D0%B1%D1%8A%D0%B5%D0%BA%D1%82%D0%BE%D0%B2/' \
    '%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA'

# '/сервисы/каталог-новостроек/объект'
HOUSE_PAGE_PATH = \
    '/%D1%81%D0%B5%D1%80%D0%B2%D0%B8%D1%81%D1%8B/' \
    '%D0%BA%D0%B0%D1%82%D0%B0%D0%BB%D0%BE%D0%B3-%D0%BD%D0%BE%D0%B2%D0%BE%D1%81%D1%82%D1%80%D0%BE%D0%B5%D0%BA/' \
    '%D0%BE%D0%B1%D1%8A%D0%B5%D0%BA%D1%82'

# '/сервисы/проверка_новостроек/'
CHECK_PAGE_PATH = '/%D1%81%D0%B5%D1%80%D0%B2%D0%B8%D1%81%D1%8B/%D0%BF%D1%80%D0%BE%D0%B2%D0%B5%D1%80%D0%BA%D0%B0_%D0%BD%D0%BE%D0%B2%D0%BE%D1%81%D1%82%D1%80%D0%BE%D0%B5%D0%BA/'


# Количество объектов на странице каталога (max - 1000)
CATALOG_PAGE_LIMIT = 100

# Максимальное количестов загружаемых страниц каталога, включая нулевую
CATALOG_PAGE_FETCH_LIMIT = 3


OUTPUT_FILE_NAME = 'result'


COL_NUM = 0
COL_ADDRESS = 1
COL_STATE = 2
COL_FLOOR_COUNT = 3
COL_FLAT_COUNT = 4
COL_SOLD_OUT = 5
COL_AVERAGE_PRICE = 6
COL_GREY_NUMBERS = 7
COL_BUILDER = 8
COL_BUILDER_INN = 9


class _ResultsClass:
    fetched_catalog_pages = 0
    catalog_page_errors = 0
    fetched_house_pages = 0
    house_page_error = 0
    start = time.time()


# Объект для хранения результатов/ошибок/счетчиков
RESULTS = _ResultsClass()
