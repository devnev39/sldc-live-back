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
    """
    Deletes a collection and its associated documents in the database.

    Args:
        name (str): The name of the collection to delete.

    Returns:
        None
    """
    sub_col_ref = db.collection("deploy").document(name).collection(name)
    docs = sub_col_ref.list_documents(page_size = 32)
    for doc in docs:
        doc.delete()
    doc_ref = db.collection("deploy").document(name)
    doc_ref.delete()

def filterDoc(docs: list, key: str, value: str):
    docs = [d for d in docs if d[key] == value]
    return docs[0]

def toNumber(inp: str):
    try:
        return float(inp)
    except Exception as ex:
        print(ex)
        return None
    

@app.get("/")
def read_root():
    """
    Retrieves data from the image with OCR and stores it in the 'deploy' and 'processed' collections.
    Deletes documents from the 'deploy' collection that are older than 16 days.
    Deletes documents from the 'processed' collection that are older than 90 days.
    Returns a dictionary containing the collected data and a timestamp.
    Raises an HTTPException with a status code of 500 and a detailed error message if an exception occurs.
    """
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

        dt = datetime.timedelta(days=16)
        past = date - dt

        delete = str(past.date())
        delete_collection(delete)

        # Store processed data in processed collection

        doc_ref = db.collection('parsed').document(date.strftime("%Y-%m-%d"))
        doc_ref.set({f'{date.strftime("%H:%M:%S")}':{
            "created_at": firestore.firestore.SERVER_TIMESTAMP,
            "frequency": toNumber(state['fields']['frequency']),
            "state_gen": toNumber(filterDoc(state['stats'], "name", "STATE GEN")['value']),
            "state_demand": toNumber(filterDoc(state['stats'], "name", "STATE DEMAND")['value'])
        }}, merge=True)

        # Get last 91st day to delete the data from processed collection
        past = date - datetime.timedelta(days=300)

        db.collection("parsed").document(str(past.date())).delete()


        # get id of the docs
        # docs = db.collection(f'processed').order_by("created_at", direction=firestore.Query.ASCENDING).limit(24).stream()
        
        # docs = [doc.id for doc in docs]

        # ids = []

        # for doc in docs:
        #     if (doc.create_time < past):
        #         ids.append(doc.id)

        # delete the docs
        # for id in ids:
        #     db.collection("processed").document(id).delete()

        print(f'Function executed at {datetime.datetime.now()}')
        return {"data": f"Collected at {datetime.datetime.now(tz=TZ)}!"}
    except Exception as ex:
        print(ex)
        print(f'Function executed at {datetime.datetime.now()} with ERROR !')
        raise HTTPException(500, detail=str(ex))
