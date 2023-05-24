from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Получаем данные из формы
        file = request.files['file']
        # Считываем содержимое файла
        text = file.read().decode('utf-8')
        # Удаляем все знаки препинания
        text = ''.join(c if c.isalnum() or c.isspace() else ' ' for c in text)
        # Разбиваем текст на слова
        words = text.split()
        # Находим самое частое слово
        stats = {}
        for word in words:
            stats[word] = stats.get(word, 0) + 1
        if len(stats) > 0:
            most_frequent_word = max(stats, key=stats.get)
        else:
            most_frequent_word = None

        return render_template('result.html', most_frequent_word=most_frequent_word)

    # Если метод GET, выводим форму
    return render_template('index.html')

#if __name__ == '__main__':
def run():
    app.run()