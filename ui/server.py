import cherrypy
import sqlite3
import pandas as pd
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('templates'))


class WebServer:
    @cherrypy.expose
    def index(self):
        return open('templates/index.html')

    @cherrypy.expose
    def admin(self):
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        # Retrieve all users from the database
        c.execute("SELECT name, password FROM users")
        users = c.fetchall()
        
        conn.close()

        template = env.get_template('admin.html')
        return template.render(users=users)

    @cherrypy.expose
    def login(self):
        return open('templates/login.html')

    @cherrypy.expose
    def logout(self):
        return open('templates/logout.html')

    @cherrypy.expose
    def registration(self):
        return open('templates/registration.html')

    @cherrypy.expose
    def dashboard(self):
        # Retrieve data from the dashboard_data table (replace with your specific query)
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT data FROM dashboard_data')
        data = c.fetchall()
        conn.close()

        # Return the dashboard HTML page with the retrieved data
        return open('templates/dashboard.html').read().format(data='\n'.join(data))

    # Add methods for handling user creation and deletion
    @cherrypy.expose
    def create_user(self, name, password):
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        # Check if the user already exists
        c.execute("SELECT * FROM users WHERE name = ?", (name,))
        existing_user = c.fetchone()
        
        if existing_user:
            return "User already exists."
        
        # Insert the new user into the database
        c.execute("INSERT INTO users (name, password) VALUES (?, ?)", (name, password))
        conn.commit()
        conn.close()
        
        return "User created successfully."
    
    @cherrypy.expose
    def upload_xlsx(self, file):
        # Save the uploaded file to disk
        upload_path = 'uploads/' + file.filename
        with open(upload_path, 'wb') as f:
            f.write(file.file.read())
        
        # Read the XLSX file data using pandas
        df = pd.read_excel(upload_path, engine='openpyxl')
        # print(df)
        # Store the data in a new table in the database
        conn = sqlite3.connect('dashboard.db')
        df.to_sql('uploaded_data', conn, if_exists='replace', index=False)
        conn.close()
        
        # return "XLSX file uploaded and data stored successfully."
        raise cherrypy.HTTPRedirect("/dashboard_data")


    


    @cherrypy.expose
    def dashboard_data(self):
        # Retrieve data from the dashboard_data table (replace with your specific query)
        conn = sqlite3.connect('dashboard.db')
        c = conn.cursor()
        c.execute('SELECT * FROM uploaded_data')
        data = c.fetchall()
        # print(data)

        # Retrieve the column names from the database table
        c.execute("PRAGMA table_info(uploaded_data)")
        columns = [column[1] for column in c.fetchall()]
        
        conn.close()

        # Generate an HTML table with dropdown lists per column
        table_html = "<table>"
        table_html += "<tr>"
        for column in columns:
            table_html += "<th>" + column + "</th>"
        table_html += "</tr>"
        
        for i in range(len(data)):
            table_html += "<tr>"
            
            for j in range(len(columns)):
                table_html += "<td>"
                table_html += "<select>"
                
                # Populate dropdown options with corresponding values
                for row in data:
                    table_html += "<option>" + str(row[j]) + "</option>"
                
                table_html += "</select>"
                table_html += "</td>"
            
            table_html += "</tr>"
        
        table_html += "</table>"

        template = env.get_template('dashboard_data.html')
        return template.render(data=table_html)



    @cherrypy.expose
    def delete_user(self, name):
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        # Check if the user exists
        c.execute("SELECT * FROM users WHERE name = ?", (name,))
        existing_user = c.fetchone()
        
        if not existing_user:
            return "User does not exist."
        
        # Delete the user from the database
        c.execute("DELETE FROM users WHERE name = ?", (name,))
        conn.commit()
        conn.close()
        
        return "User deleted successfully."
    
    @cherrypy.expose
    def authenticate(self, name, password):
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        # Check if the user exists and the password is correct
        c.execute("SELECT * FROM users WHERE name = ? AND password = ?", (name, password))
        existing_user = c.fetchone()
        
        if not existing_user:
            return "Authentication failed."
        
        # Redirect to the dashboard page upon successful authentication
        raise cherrypy.HTTPRedirect("/dashboard")



        

if __name__ == '__main__':
    cherrypy.quickstart(WebServer(), '/', {
        '/': {
            'tools.sessions.on': True
        },
        '/templates': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'templates'
        }
    })
