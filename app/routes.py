from app import create_app

app = create_app()
print("from module",app.mongo_db)