import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Campaign, Donation, CATEGORIES

app = FastAPI(title="FundRise API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "FundRise backend is running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": "❌ Not Set",
        "database_name": "❌ Not Set",
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"

    return response

# Utility to convert ObjectId to str in documents

def _serialize(doc):
    if not doc:
        return doc
    doc = dict(doc)
    if "_id" in doc:
        doc["_id"] = str(doc["_id"]) if isinstance(doc["_id"], ObjectId) else doc["_id"]
    return doc

# Categories
@app.get("/categories", response_model=List[str])
def get_categories():
    return CATEGORIES

# Campaigns
@app.post("/campaigns")
def create_campaign(campaign: Campaign):
    if campaign.category not in CATEGORIES:
        raise HTTPException(status_code=400, detail="Invalid category")
    inserted_id = create_document("campaign", campaign)
    # Return created document
    created = db["campaign"].find_one({"_id": ObjectId(inserted_id)})
    return _serialize(created)

@app.get("/campaigns")
def list_campaigns(trending: Optional[bool] = Query(default=None)):
    filter_query = {}
    if trending is True:
        filter_query["is_trending"] = True
    docs = get_documents("campaign", filter_query, limit=10 if trending else None)
    return [_serialize(d) for d in docs]

@app.get("/campaigns/{campaign_id}")
def get_campaign(campaign_id: str):
    try:
        oid = ObjectId(campaign_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid campaign id")
    doc = db["campaign"].find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return _serialize(doc)

# Donations
@app.post("/donations")
def create_donation(donation: Donation):
    # Basic validation: campaign exists
    try:
        oid = ObjectId(donation.campaign_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid campaign id")
    campaign = db["campaign"].find_one({"_id": oid})
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    # Insert donation
    inserted_id = create_document("donation", donation)
    created = db["donation"].find_one({"_id": ObjectId(inserted_id)})
    # Update campaign raised amount (simple increment)
    amount = donation.amount
    db["campaign"].update_one({"_id": oid}, {"$inc": {"raised": amount}})
    return _serialize(created)

@app.get("/donations")
def list_donations(campaign_id: Optional[str] = None):
    filter_query = {}
    if campaign_id:
        try:
            oid = ObjectId(campaign_id)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid campaign id")
        filter_query["campaign_id"] = campaign_id
    docs = get_documents("donation", filter_query)
    return [_serialize(d) for d in docs]

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
