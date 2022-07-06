from fastapi import FastAPI

def makeServer():
   # app = FastAPI(title='SpeedDB', version='0.0.1b1')
   app = FastAPI()

   @app.get('/')
   def index():
      return {}

   return app