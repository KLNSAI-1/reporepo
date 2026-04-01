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
    <h2>Store Data in PostgreSQL</h2>

    <form method="post" action="/predict">
        Temperature: <input name="Temperature" required><br><br>
        Humidity: <input name="Humidity" required><br><br>
        <input type="submit" value="Submit">
    </form>

    <h3>{{ result }}</h3>

    <br>
    <a href="/data">View Stored Data</a>
</body>
</html>
"""

# ---------- DB CONNECTION (YOUR DETAILS ADDED) ----------
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

# Run once at startup
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

        # Insert into PostgreSQL
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO predictions (temperature, humidity, result) VALUES (%s, %s, %s)",
            (temp, humidity, result)
        )
        conn.commit()
        cur.close()
        conn.close()

        return render_template_string(HTML, result=result)

    except Exception as e:
        return f"Error: {str(e)}"

# ---------- VIEW DATA ----------
@app.route('/data')
def data():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM predictions ORDER BY id DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return str(rows)

if __name__ == "__main__":
    app.run()