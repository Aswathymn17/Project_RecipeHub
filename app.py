from flask import Flask,render_template,request,redirect, session
import mysql.connector
# Establish MySQL connection
connection=mysql.connector.connect(
    host='localhost',
    user='root',
    password='root',
    database='recipehub'
    )
# Create cursor to interact with the database
mycursor=connection.cursor()
#create a flask application
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@app.route("/")
def home():

        try:
            # SQL query to select all records from 'recipes' table
            query = "SELECT * FROM recipes"            
            # Execute the query
            mycursor.execute(query)        
            # Fetch all records from the result set
            data = mycursor.fetchall()
          # Get the username from the session if the user is logged in
            username = session.get('username')
            # Render the home.html template and pass the data to it
            return render_template('home.html', sqldata=data, username=username)       
        except mysql.connector.Error as error:
            # Handle any errors that occur during database operation
            return f"An error occurred: {error}"
   
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        try:
            # SQL query to validate user credentials
            query = "SELECT id FROM users WHERE username = %s AND password = %s"
            mycursor.execute(query, (username, password))
            user_id = mycursor.fetchone()

            if user_id:
                # Store user ID in session to mark user as logged in
                session['user_id'] = user_id[0]
                session['username'] =username # Correctly set the username
                return redirect('/')
            else:
                error_message = "Invalid username or password"
                return render_template('login.html', error=error_message)

        except mysql.connector.Error as error:
            # Handle database errors
            error_message = f"Database error: {error}"
            return render_template('login.html', error=error_message)

    return render_template('login.html')
@app.route("/logout")
def logout():
    # Clear user session to log out user
    session.pop('user_id', None)
    session.pop('username', None) 
    return redirect('/login')

@app.route('/new_recipe')
def newrecepe():
    return render_template('new_recepe.html')

@app.route("/recipe/<int:recipe_id>", methods=['GET', 'POST'])
def recipe_detail(recipe_id):
    try:
        if request.method == 'POST':
            if 'user_id' not in session:
                return redirect('/login')
            comment = request.form['comment']
            user_id = session['user_id']
            try:
                query = "INSERT INTO comments (recipe_id, user_id, comment, date_posted) VALUES (%s, %s, %s, NOW())"
                mycursor.execute(query, (recipe_id, user_id, comment))
                connection.commit()
            except mysql.connector.Error as error:
                return f"Database error: {error}"
        # SQL query to select a specific recipe by ID
        query = "SELECT * FROM recipes WHERE id = %s"
        mycursor.execute(query, (recipe_id,))
        recipe = mycursor.fetchone()

        # SQL query to select comments for the recipe
        comments_query = "SELECT comments.comment, comments.date_posted, users.username FROM comments JOIN users ON comments.user_id = users.id WHERE recipe_id = %s"
        mycursor.execute(comments_query, (recipe_id,))
        comments = mycursor.fetchall()
        
        username = session.get('username')

        if recipe:
            # Render the recipe_detail.html template with the recipe details and comments
            return render_template('recipe_detail.html', recipe={
                'id': recipe[0],
                'name': recipe[1],
                'ingredients': recipe[2],
                'instructions': recipe[3],
                'cooking_time': recipe[4],
                'serving_size': recipe[5]
            }, comments=comments, username=username)
        else:
            return "Recipe not found", 404
    
    except mysql.connector.Error as error:
        # Handle any errors that occur during database operation
        return f"An error occurred: {error}"


@app.route("/search", methods=['GET'])
def search():
    try:
        # Get the search query from the URL parameters
        query = request.args.get('query', '')

        # SQL query to search for recipes by name or ingredients
        sql = "SELECT * FROM recipes WHERE name LIKE %s OR ingredients LIKE %s"
        mycursor.execute(sql, ('%' + query + '%', '%' + query + '%'))

        # Fetch all matching recipes
        search_results = mycursor.fetchall()

        # Render the search_results.html template with the search results
        return render_template('search_results.html', query=query, results=search_results)

    except mysql.connector.Error as error:
        # Handle any errors that occur during database operation
        return f"An error occurred: {error}"

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        print("--------------------------")
        # Check if any field is empty
         # Check if any field is empty
        error_username = None if username else "Username is required."
        error_email = None if email else "Email is required."
        error_password = None if password else "Password is required."

        # If any field is empty, render the registration form with error messages
        if error_username or error_email or error_password:
            return render_template('register.html', error="Please correct the following errors:", 
                                   error_username=error_username, error_email=error_email, error_password=error_password,username=username,email=email)

        try:
            query = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
            mycursor.execute(query, (username, email, password))
            connection.commit()
            return redirect('/login')
        except mysql.connector.Error as error:
            error_message = f"Database error: {error}"
            return render_template('register.html', error=error_message)
    return render_template('register.html')

@app.route("/create_recipe", methods=['POST'])
def create_recipe():
    
        user_id = session['user_id']
        recipe_name = request.form['recipe_name']
        ingredients = request.form['ingredients']
        instructions = request.form['instructions']
        cooking_time = request.form['cooking_time']
        serving_size = request.form['serving_size']
       # Check if any field is empty
        errorrecipe_name = None if recipe_name else "Recipe Name is required."
        erroringredients = None if ingredients else "Ingredients are required."
        errorinstructions = None if instructions else "Instructions are required."
        errorcookingtime = None if cooking_time else "Cooking Time is required."
        errorserving = None if serving_size else "Serving Size is required."

       # If any field is empty, render the form with error messages and previous data
        if errorrecipe_name or erroringredients or errorinstructions or errorcookingtime or errorserving:
            return render_template('new_recepe.html', 
                                   error="Please correct the following errors:", 
                                   errorrecipe_name=errorrecipe_name, 
                                   erroringredients=erroringredients, 
                                   errorinstructions=errorinstructions, 
                                   errorcookingtime=errorcookingtime, 
                                   errorserving=errorserving,
                                   recipe_name=recipe_name, 
                                   ingredients=ingredients, 
                                   instructions=instructions, 
                                   cooking_time=cooking_time, 
                                   serving_size=serving_size)

        try:
            # SQL query to insert new recipe into 'recipes' table
            query = "INSERT INTO recipes (name, ingredients, instructions, cooking_time, serving_size, user_id) VALUES (%s, %s, %s, %s, %s, %s)"
            mycursor.execute(query, (recipe_name, ingredients, instructions, cooking_time, serving_size, user_id))
            connection.commit()  # Commit the transaction
            return redirect('/')
            # Redirect to home page after successful recipe creation
        
       
        except mysql.connector.Error as error:
            # Handle database errors
           
            error_message = f"Database error: {error}"
        return render_template('home.html', error=error_message)
 
   



#run flask application
if __name__ == '__main__':
    app.run(debug = True)

