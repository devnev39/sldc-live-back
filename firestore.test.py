import datetime
from firebase_admin import initialize_app
from firebase_admin import firestore

app = initialize_app()

db = firestore.client()

def delete_collection(name):
    sub_col_ref = db.collection("test").document(name).collection(name)
    docs = sub_col_ref.list_documents(page_size = 24)
    for doc in docs:
        doc.delete()
    doc_ref = db.collection("test").document(name)
    doc_ref.delete()

td = datetime.datetime.now()
dt = datetime.timedelta(days=15)
past = td - dt
delete_collection(str(past.date()))
print(past.date())
