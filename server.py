import pytz
from script import getState
from fastapi import FastAPI, HTTPException
from firebase_admin import firestore
from firebase_admin import initialize_app
import datetime

app = FastAPI()

initialize_app()

db = firestore.client()

@app.get("/")
def read_root():
    try:
        TZ = pytz.timezone("Asia/Kolkata")
        date = datetime.datetime.now(tz=TZ)
        today = str(date.date())
        state,stats = getState()
        doc_ref = db.collection('deploy').document(today).collection(today).document()
        doc_ref.set({
            "created_at": firestore.firestore.SERVER_TIMESTAMP,
            "fields": state['fields'],
            "tables": state['tables'],
            "stats": state['stats'],
            "server_stats": stats
        })
        print(f'Function executed at {datetime.datetime.now()}')
        return {"data": f"Collected at {datetime.datetime.now(tz=TZ)}!"}
    except Exception as ex:
        print(ex)
        print(f'Function executed at {datetime.datetime.now()} with ERROR !')
        raise HTTPException(500, detail=str(ex))
