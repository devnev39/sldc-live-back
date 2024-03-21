import pytz
from script import getState
from fastapi import FastAPI, HTTPException
from firebase_admin import firestore
from firebase_admin import initialize_app
import datetime

app = FastAPI()

initialize_app()

db = firestore.client()

def delete_collection(name):
    sub_col_ref = db.collection("deploy").document(name).collection(name)
    docs = sub_col_ref.list_documents(page_size = 24)
    for doc in docs:
        doc.delete()
    doc_ref = db.collection("deploy").document(name)
    doc_ref.delete()

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
        dt = datetime.timedelta(days=15)
        past = date - dt
        delete = str(past.date())
        delete_collection(delete)
        print(f'Function executed at {datetime.datetime.now()}')
        return {"data": f"Collected at {datetime.datetime.now(tz=TZ)}!"}
    except Exception as ex:
        print(ex)
        print(f'Function executed at {datetime.datetime.now()} with ERROR !')
        raise HTTPException(500, detail=str(ex))
