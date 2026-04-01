from flask import Flask, request, render_template_string
import psycopg2

app = Flask(__name__)

# ---------- HTML ----------
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Azure Python 3.11 + PostgreSQL</title>
</head>
<body>
    <h2>Occupancy Prediction</h2>

    <form method="post" action="/predict">
        Temperature: <input name="Temperature" required><br><br>
        Humidity: <input name="Humidity" required><br><br>
        <input type="submit" value="Submit">
    </form>

    <h3>{{ result }}</h3>
</body>
</html>
"""

# ---------- DB CONNECTION ----------
def get_connection():
    return psycopg2.connect(
        dbname="si-database",
        user="nucnfyfjjp",
        password="vHIOdwaLoRHyF$D5",
        host="si-server.postgres.database.azure.com",
        port="5432",
        sslmode="require"
    )

# ---------- CREATE TABLE ----------
def create_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id SERIAL PRIMARY KEY,
            temperature FLOAT,
            humidity FLOAT,
            result TEXT
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

create_table()

# ---------- ROUTES ----------
@app.route('/')
def home():
    return render_template_string(HTML, result="")

@app.route('/predict', methods=['POST'])
def predict():
    try:
        temp = float(request.form['Temperature'])
        humidity = float(request.form['Humidity'])

        if temp > 25 and humidity > 50:
            result = "It is Occupied"
        else:
            result = "It is not Occupied"

        # ✅ STORE DATA IN DB (but DO NOT show it)
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO predictions (temperature, humidity, result) VALUES (%s, %s, %s)",
            (temp, humidity, result)
        )
        conn.commit()
        cur.close()
        conn.close()

        # ✅ Only show result, NOT DB data
        return render_template_string(HTML, result=result)

    except Exception as e:
        return "Something went wrong"

if __name__ == "__main__":
    app.run()
