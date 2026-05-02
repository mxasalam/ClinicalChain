import os
import certifi
# Force macOS Python to use certifi's SSL certificates for all outbound requests
os.environ["SSL_CERT_FILE"] = certifi.where()

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from google.cloud import secretmanager
from google.cloud import logging as cloud_logging
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from google.cloud.sql.connector import Connector, IPTypes
import pg8000

# Initialize Cloud Logging
logging_client = cloud_logging.Client()
logger = logging_client.logger("inventory-api")

app = FastAPI(
    title="McKesson Mock Inventory API",
    description="API for checking inventory levels of medications at different warehouses.",
    version="1.0.0"
)

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "clinicalchain")
REGION = "us-central1"
INSTANCE_NAME = "clinicalchain-db"
INSTANCE_CONNECTION_NAME = f"{PROJECT_ID}:{REGION}:{INSTANCE_NAME}"
DB_USER = "postgres"
DB_NAME = "postgres"

def get_db_password():
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{PROJECT_ID}/secrets/inventory-db-password/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

# initialize Cloud SQL Python Connector object
connector = Connector()

def getconn() -> pg8000.dbapi.Connection:
    password = get_db_password()
    conn: pg8000.dbapi.Connection = connector.connect(
        INSTANCE_CONNECTION_NAME,
        "pg8000",
        user=DB_USER,
        password=password,
        db=DB_NAME,
        ip_type=IPTypes.PUBLIC,
    )
    return conn

# Configure SQLAlchemy engine
engine = create_engine(
    "postgresql+pg8000://",
    creator=getconn,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class InventoryItem(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True, index=True)
    warehouse_location = Column(String, index=True)
    medication_name = Column(String, index=True)
    stock_quantity = Column(Integer)
    unit = Column(String)

# Create tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class InventoryCheckRequest(BaseModel):
    warehouse_location: str
    medication_name: str

class InventoryCheckResponse(BaseModel):
    warehouse_location: str
    medication_name: str
    in_stock: bool
    stock_quantity: int
    unit: str

@app.on_event("startup")
def startup_event():
    # Populate the database with mock data if it's empty
    db = SessionLocal()
    if db.query(InventoryItem).count() == 0:
        mock_data = [
            InventoryItem(warehouse_location="richmond", medication_name="insulin", stock_quantity=500, unit="vials"),
            InventoryItem(warehouse_location="richmond", medication_name="amoxicillin", stock_quantity=1200, unit="bottles"),
            InventoryItem(warehouse_location="richmond", medication_name="mrna-vaccine", stock_quantity=50, unit="doses"),
            InventoryItem(warehouse_location="dallas", medication_name="insulin", stock_quantity=0, unit="vials"),
            InventoryItem(warehouse_location="dallas", medication_name="amoxicillin", stock_quantity=800, unit="bottles"),
            InventoryItem(warehouse_location="dallas", medication_name="mrna-vaccine", stock_quantity=200, unit="doses"),
        ]
        db.add_all(mock_data)
        db.commit()
    db.close()
    logger.log_text("Inventory API started successfully.", severity="INFO")

@app.get("/inventory", response_model=InventoryCheckResponse)
def check_inventory(warehouse: str, medication: str, db: Session = Depends(get_db)):
    """
    Check the inventory of a specific medication at a specific warehouse location.
    
    - **warehouse**: The city of the warehouse (e.g., 'richmond', 'dallas').
    - **medication**: The name of the medication (e.g., 'insulin', 'amoxicillin', 'mrna-vaccine').
    """
    wh_key = warehouse.lower()
    med_key = medication.lower()
    
    logger.log_text(f"Checking inventory for {med_key} at {wh_key}.", severity="INFO")

    valid_warehouses = ["richmond", "dallas"]
    if wh_key not in valid_warehouses:
        logger.log_text(f"Warehouse not found: {wh_key}", severity="WARNING")
        raise HTTPException(status_code=404, detail=f"Warehouse '{warehouse}' not found. Valid options: richmond, dallas.")

    item = db.query(InventoryItem).filter(
        InventoryItem.warehouse_location == wh_key,
        InventoryItem.medication_name == med_key
    ).first()
    
    if not item:
        logger.log_text(f"Medication {med_key} not found at {wh_key}.", severity="INFO")
        return InventoryCheckResponse(
            warehouse_location=warehouse,
            medication_name=medication,
            in_stock=False,
            stock_quantity=0,
            unit="unknown"
        )
        
    logger.log_text(f"Found {item.stock_quantity} {item.unit} of {med_key} at {wh_key}.", severity="INFO")
    
    return InventoryCheckResponse(
        warehouse_location=warehouse,
        medication_name=medication,
        in_stock=item.stock_quantity > 0,
        stock_quantity=item.stock_quantity,
        unit=item.unit
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
