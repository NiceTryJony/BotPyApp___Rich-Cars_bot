from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from database import get_car, add_purchase
import asyncio
from dotenv import load_dotenv
import os

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')  # Не забудьте сменить на настоящий ключ!


@app.route('/')
def index():
    return render_template('template.html')


@app.route('/purchase', methods=['POST'])
async def purchase():
    user_id = request.form.get('user_id')  # Предполагаем, что user_id доступен
    car_id = request.form.get('car_id')

    car_info = await get_car(car_id)
    if car_info:
        car_name, car_power, car_price = car_info
        # Здесь вы можете добавить логику для проверки баланса и добавления покупки
        await add_purchase(user_id, car_id)  # Добавление покупки в БД
        return jsonify({
            'success': True,
            'car_name': car_name,
            'car_power': car_power,
            'car_price': car_price
        })
    return jsonify({'success': False, 'message': 'Car not found'})


if __name__ == '__main__':
    app.run(debug=True)







# )from flask import Flask, jsonify, render_template

# )app = Flask(__name__, template_folder='templates')

# )@app.route('/')
# def index():
#     return render_template('template.html')

# )@app.route('/api/user_data')
# def user_data():
#     return jsonify({
#         'username': 'TestUser',
#         'balance': 100.0
#     })

# )if __name__ == "__main__":
#     app.run(debug=True, port=8080)
