from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__, template_folder='templates')

DATABASE = 'database.db'

CONTINENTS = [
    "Africa",
    "Antarctica",
    "Asia",
    "Europe",
    "North America",
    "Oceania",
    "South America"
]


def create_table():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bird_observations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bird TEXT NOT NULL,
            region TEXT NOT NULL,
            date TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


@app.route('/', methods=['GET', 'POST'])  # Corrected to handle initial form display
def index():
    create_table()
    message = None
    message_class = None
    results = None  # On reload reset all of the input boxes (Fixed)

    if request.method == 'POST':
        bird = request.form['bird']
        region = request.form['region']
        date = request.form['date']

        if bird and region and date and region != "Select Region":
            bird = bird.lower()
            region = region.lower()

            try:
                conn = sqlite3.connect(DATABASE)
                cursor = conn.cursor()
                cursor.execute("INSERT INTO bird_observations (bird, region, date) VALUES (?, ?, ?)", (bird, region, date))
                conn.commit()
                conn.close()
                message = "Observation successfully added!"
                message_class = "success"
            except Exception as e:
                message = f"Error adding observation: {str(e)}"
                message_class = "error"
        else:
            message = "Please fill in all fields."
            message_class = "error"

    return render_template('index.html', message=message, message_class=message_class, results=results, continents=CONTINENTS)



@app.route('/search')
def search():
    search_term = request.args.get('search_term')
    results = []
    message = None  # Initialize message
    message_class = None  # Initialize message_class

    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        if search_term:
            query = "SELECT bird, region, date FROM bird_observations WHERE LOWER(bird) LIKE ? OR LOWER(region) LIKE ?"
            search_pattern = f"%{search_term.lower()}%"
            cursor.execute(query, (search_pattern, search_pattern))
            #results = cursor.fetchall()
            #results = [{'bird': row[0], 'region': row[1], 'date': row[2]} for row in results]  # Format here
            results = [dict(zip(['bird', 'region', 'date'], row)) for row in cursor.fetchall()] # Fixed Line

        conn.close()

    except Exception as e:
        message = f"Error during search: {str(e)}"
        message_class = "error"
        results = []  # Ensure results is always defined


    return render_template('index.html', results=results, message=message, message_class=message_class, continents=CONTINENTS)

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

@app.route('/observations')  # Added observations Route
def observations():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, bird, region, date FROM bird_observations") # changed to include id
    observations = [dict(zip(['id', 'bird', 'region', 'date'], row)) for row in cursor.fetchall()] # added id to the zip
    conn.close()
    return render_template('observations.html', observations=observations)

@app.route('/delete/<int:id>', methods=['POST']) # Added Delete Function
def delete_observation(id):
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM bird_observations WHERE id = ?", (id,))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error deleting observation: {e}")  # Log the error
        # Optionally, you could set a message and redirect back to the observations page with an error message.

    return redirect(url_for('observations'))  # Redirect back to observations page

@app.route('/edit/<int:id>')
def edit_observation(id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, bird, region, date FROM bird_observations WHERE id = ?", (id,))
    observation = dict(zip(['id', 'bird', 'region', 'date'], cursor.fetchone()))
    conn.close()
    return render_template('edit_observation.html', observation=observation, continents=CONTINENTS) #Passing Continents

@app.route('/update/<int:id>', methods=['POST'])
def update_observation(id):
    bird = request.form['bird']
    region = request.form['region']
    date = request.form['date']

    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("UPDATE bird_observations SET bird=?, region=?, date=? WHERE id=?", (bird, region, date, id))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error updating observation: {e}")
        # Optionally handle the error and display a message

    return redirect(url_for('observations'))  # Redirect back to observations page

if __name__ == '__main__':
    app.run(debug=True)