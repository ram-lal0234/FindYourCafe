from flask import Flask, render_template,request,redirect
import pickle
import psycopg2


cafes = pickle.load(open('model/cafe_list.pkl','rb'))
similarity= pickle.load(open('model/similarity.pkl','rb'))

# PostgreSQL Configuration
postgresql_host = 'localhost'
postgresql_port = '3000'
postgresql_user = 'postgres'
postgresql_password = '0234'
postgresql_database = 'cafe'

conn = psycopg2.connect(
    host=postgresql_host,
    port=postgresql_port,
    user=postgresql_user,
    password=postgresql_password,
    database=postgresql_database
)
cursor = conn.cursor()

app = Flask(__name__)

# conatct form
@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']

    # Insert form submission into the database
    insert_query = "INSERT INTO contact (name, email, message) VALUES (%s, %s, %s)"
    cursor.execute(insert_query, (name, email, message))
    conn.commit()

    # Add your logic here (e.g., sending emails, redirecting, etc.)
    return redirect('/')

# suggest your cafe 
@app.route('/submit-suggest', methods=['POST'])
def submit_form():
    first_name = request.form.get('first-name')
    last_name = request.form.get('last-name')
    email = request.form.get('email')
    phone_number = request.form.get('phone-number')
    food_item = request.form.get('food-item')
    cafe_name = request.form.get('cafe-name')
    location = request.form.get('location')

    # Insert the form data into the PostgreSQL database
    query = "INSERT INTO suggest_cafe (first_name, last_name, email, phone_number, food_item, cafe_name, location) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    values = (first_name, last_name, email, phone_number, food_item, cafe_name, location)
    cursor.execute(query, values)
    conn.commit()

    return "Form submitted successfully"

def recommend(cafe):
    index = -1
    try:
        index = cafes[cafes['Best Indian Food Item'] == cafe].index[0]
    except IndexError:
        print(f"Error: cafe '{cafe}' not found in dataset")
    if index == -1:
        return []
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_cafe_name = []
    recommended_cafe_location=[]
    recommended_cafe_map=[]

    for i in distances[1:6]:
        recommended_cafe_name.append(cafes.iloc[i[0]]['Restaurant Name'])
        recommended_cafe_location.append(cafes.iloc[i[0]]['Location'])
        recommended_cafe_map.append(cafes.iloc[i[0]]['Link'])

    return recommended_cafe_name,recommended_cafe_location,recommended_cafe_map




# Create navbar and footer routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/suggestcafe')
def suggestcafe():
    return render_template('suggestcafe.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/searchcafe',methods=['GET','POST'])
def searchcafe():

    cafe_list = cafes['Best Indian Food Item'].values
    print(cafe_list)
    status= False

    if request.method =="POST":
        try:
            if request.form['cafes']:
                cafe_name=request.form['cafes']
                print(cafe_name)
                recommended_cafe_name,recommended_cafe_location,recommended_cafe_map=recommend(cafe_name)
                status=True
                
                return render_template('searchcafe.html',cafe_name=recommended_cafe_name, location=recommended_cafe_location,map=recommended_cafe_map,cafe_list=cafe_list,status=status)
        
        except Exception as e:
            error={'error':e}
            return render_template('searchcafe.html',error=error,cafe_list=cafe_list,status=status)
    else:
        return render_template('searchcafe.html',cafe_list=cafe_list,status=status)                   
    


if __name__ == '__main__':
    app.run(debug=True)
