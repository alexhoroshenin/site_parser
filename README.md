Скрипт получения информации о новостройках

Для запуска нужно
1. Установить зависимости requirements.txt
2. Скачать geckodriver для Mozilla
https://askubuntu.com/questions/870530/how-to-install-geckodriver-in-ubuntu
3. Указать переменную окружения с путем до папки geckodriver
export PATH=$PATH:/path-to-geckodriver-folder/
4. Указать настройки скрипта в файле defaults.py
5. Запустить скрипт 


Страницы каталога сайта реализованы с помощью  JS фрймворка. 
Чтобы получить информацю с таких страниц, используется реальный браузер Mozilla.
