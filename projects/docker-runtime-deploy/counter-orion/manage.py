from app import app, db

# Flask CLI entrypoint:
#   flask --app manage.py db init
#   flask --app manage.py db migrate -m "init users"
#   flask --app manage.py db upgrade

if __name__ == "__main__":
    app.run()
