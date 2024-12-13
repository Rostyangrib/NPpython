from flask import Flask, render_template, request, jsonify
from database import get_filtered_films
from Scrap import scrape_films

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/filter', methods=['GET'])
def filter_films():

    keyword = request.args.get('keyword', '')
    min_time = request.args.get('min_time')
    max_time = request.args.get('max_time')

    results = get_filtered_films(keyword, min_time, max_time)

    return jsonify(results)

@app.route('/scrape', methods=['POST'])
def scrape_and_save():
    scrape_films()
    return jsonify({"message": "Данные успешно спарсены и сохранены!"})

if __name__ == '__main__':
    app.run(debug=True)
