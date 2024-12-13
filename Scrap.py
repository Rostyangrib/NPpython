from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from flask import Flask, jsonify
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import mysql.connector
import json

app = Flask(__name__)

def create_database():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='123'
        )
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS Films")
        print("База данных Films создана или уже существует")
        cursor.close()
        connection.close()
    except mysql.connector.Error as e:
        print(f"Ошибка при создании базы данных: {e}")


def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host='http://localhost:8080/',
            user='root',
            password='123',
            database='Films'
        )
        if connection.is_connected():
            print("Подключение к базе данных успешно")
        return connection
    except mysql.connector.Error as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return None


def create_table():
    connection = connect_to_db()
    if connection:
        try:
            cursor = connection.cursor()
            query = """
                CREATE TABLE IF NOT EXISTS films (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    description JSON NOT NULL,
                    show_times JSON NOT NULL
                )
            """
            cursor.execute(query)
            print("Таблица films создана или уже существует")
            cursor.close()
        except mysql.connector.Error as e:
            print(f"Ошибка при создании таблицы: {e}")
        finally:
            connection.close()


def insert_data_to_db(connection, data):
    try:
        cursor = connection.cursor()
        query = """
            INSERT INTO films (title, description, show_times)
            VALUES (%s, %s, %s)
        """
        for film in data:
            cursor.execute(query, (
                film["title"],
                json.dumps(film["description"]),
                json.dumps(film["time"])
            ))
        connection.commit()
        print("Данные успешно добавлены в базу данных")
    except mysql.connector.Error as e:
        print(f"Ошибка добавления данных: {e}")
    finally:
        cursor.close()

@app.route('/')
def index():
    create_database()
    create_table()

    options = Options()
    options.add_argument("--headless")  # Режим без графического интерфейса
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    chromedriver_path = 'C:/Users/Rostislav/PycharmProjects/Flask/.venv/chromedriver_win32 (1)/chromedriver.exe'

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get('https://newcinema38.ru/')

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "releases-item"))
        )

        html = driver.page_source

        soup = BeautifulSoup(html, 'html.parser')

        films = soup.find_all('div', class_='releases-item__info')

        result = []

        for film in films:
            try:
                title = film.find('div', class_='releases-item-description').find('div',
                                                                                  class_='releases-item-description__title text text--size-24').text

                disc = film.find('div', class_='releases-item-description').find('div',
                                                                                 class_='releases-item-description__badge text text--size-12')
                spans = disc.find_all('span')
                span_texts = [span.text.strip() for span in spans]

                time_sel = film.find('div', class_='releases-item-schedule').find('div', class_='seance-item').find(
                    'div', class_='seance-item__container').find('div', class_='seance-item__item').find('div',
                                                                                                         class_='seance-item__time text text--size-18')
                time_txt = [t.text.strip() for t in time_sel]

                result.append({
                    "title": title,
                    "description": span_texts,
                    "time": time_txt
                })

            except AttributeError:
                continue

        connection = connect_to_db()
        if connection:
            insert_data_to_db(connection, result)
            connection.close()

        return jsonify({"status": "Данные успешно добавлены в базу данных", "data": result})

    finally:
        driver.quit()


if __name__ == '__main__':
    app.run(debug=True)
