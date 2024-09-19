from flask import Flask, jsonify, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('template.html')

@app.route('/api/user_data')
def user_data():
    return jsonify({
        'username': 'TestUser',
        'balance': 100.0
    })

if __name__ == "__main__":
    app.run(debug=True)
