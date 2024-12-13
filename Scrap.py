from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from flask import Flask, jsonify
import mysql.connector
import json

app = Flask(__name__)

DB_CONFIG = {
    'host': 'db',
    'user': 'root',
    'password': '123',
    'database': 'Films',
    'charset': 'utf8mb4'
}

@app.route('/')
def index():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

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
                title = film.find('div', class_='releases-item-description').find(
                    'div', class_='releases-item-description__title text text--size-24').text

                disc = film.find('div', class_='releases-item-description').find(
                    'div', class_='releases-item-description__badge text text--size-12')
                spans = disc.find_all('span')
                span_texts = [span.text.strip() for span in spans]

                time_sel = film.find('div', class_='releases-item-schedule').find(
                    'div', class_='seance-item').find(
                    'div', class_='seance-item__container').find(
                    'div', class_='seance-item__item').find(
                    'div', class_='seance-item__time text text--size-18')
                time_txt = time_sel.text.strip()

                result.append({
                    "title": title,
                    "description": span_texts,
                    "time": time_txt
                })

                # Сохранение в базу данных
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO films (title, description, time) 
                    VALUES (%s, %s, %s)
                """, (
                    title, json.dumps(span_texts), json.dumps([time_txt])
                ))
                conn.commit()
                cursor.close()
                conn.close()

            except AttributeError:
                continue

        return jsonify({"status": "Данные успешно добавлены в базу данных", "data": result})

    finally:
        driver.quit()

if __name__ == '__main__':
    app.run(debug=True)
