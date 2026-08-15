from flask import Flask, render_template, request, redirect, url_for
# TODO: добавить нужные импорты (flask_sqlalchemy, flask_login, и т.д.)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'TODO-change-this-secret'
# TODO: app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'


# TODO: инициализировать расширения (db = SQLAlchemy(app), login_manager = ...)


# ─── Маршруты ───────────────────────────────────────────────────────────────

@app.route('/')
def index():
    # TODO: передать данные из БД в шаблон
    return render_template('index.html')


# TODO: добавить остальные маршруты


# ────────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    app.run(debug=True)
