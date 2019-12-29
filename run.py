from ez_script_center import app, db

if __name__ == "__main__":
    db.create_all()
    app.run(ssl_context="adhoc", host='0.0.0.0')
