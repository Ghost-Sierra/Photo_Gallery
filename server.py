from flask import Flask, render_template, request #import modules
import sqlite3

app = Flask(__name__, template_folder='templates')

DATABASE = 'database.db' #name of database to use and create is the database doesn't exsist
# defining continents for drop down and select menu
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


@app.route('/', methods=['GET', 'POST'])
def index():
    create_table()
    message = None
    message_class = None
    results = None  # On reload reset all of the input boxes (Currently broken)

    if request.method == 'POST':
        bird = request.form['bird']
        region = request.form['region']
        date = request.form['date']

        if bird and region and date and region != "Select Region":
            # Convert data to lowercase before inserting
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

#search funciton for accessing the database
@app.route('/search')
def search():
    search_term = request.args.get('search_term')
    results = []

    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        # Use lower case function for case-insensitive search
        cursor.execute("SELECT bird, region, date FROM bird_observations WHERE LOWER(bird) LIKE LOWER(?) OR LOWER(region) LIKE LOWER(?)", ('%' + search_term + '%', '%' + search_term + '%'))
        results = cursor.fetchall()
        conn.close()

    except Exception as e:
        print(f"Error during search: {e}")
        # Error message display for values being entered incorrectly

    #make the results look nice
    results = [{'bird': row[0], 'region': row[1], 'date': row[2]} for row in results]

    return render_template('index.html', results=results, message=None, message_class=None, continents=CONTINENTS)

#transfer to the gallery page of the website
@app.route('/gallery')
def gallery():
    return render_template('gallery.html')


if __name__ == '__main__':
    app.run(debug=True)