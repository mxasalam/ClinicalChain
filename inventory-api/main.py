from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI(
    title="McKesson Mock Inventory API",
    description="API for checking mock inventory levels of medications at different warehouses.",
    version="1.0.0"
)

# Mock database
mock_db = {
    "richmond": {
        "insulin": {"stock": 500, "unit": "vials"},
        "amoxicillin": {"stock": 1200, "unit": "bottles"},
        "mrna-vaccine": {"stock": 50, "unit": "doses"},
    },
    "dallas": {
        "insulin": {"stock": 0, "unit": "vials"},
        "amoxicillin": {"stock": 800, "unit": "bottles"},
        "mrna-vaccine": {"stock": 200, "unit": "doses"},
    }
}

class InventoryCheckRequest(BaseModel):
    warehouse_location: str
    medication_name: str

class InventoryCheckResponse(BaseModel):
    warehouse_location: str
    medication_name: str
    in_stock: bool
    stock_quantity: int
    unit: str

@app.get("/inventory", response_model=InventoryCheckResponse)
def check_inventory(warehouse: str, medication: str):
    """
    Check the inventory of a specific medication at a specific warehouse location.
    
    - **warehouse**: The city of the warehouse (e.g., 'richmond', 'dallas').
    - **medication**: The name of the medication (e.g., 'insulin', 'amoxicillin', 'mrna-vaccine').
    """
    wh_key = warehouse.lower()
    med_key = medication.lower()

    if wh_key not in mock_db:
        raise HTTPException(status_code=404, detail=f"Warehouse '{warehouse}' not found. Valid options: richmond, dallas.")

    warehouse_data = mock_db[wh_key]
    
    if med_key not in warehouse_data:
        # If medication is valid but not in this warehouse, return 0 stock
        return InventoryCheckResponse(
            warehouse_location=warehouse,
            medication_name=medication,
            in_stock=False,
            stock_quantity=0,
            unit="unknown"
        )
        
    item = warehouse_data[med_key]
    
    return InventoryCheckResponse(
        warehouse_location=warehouse,
        medication_name=medication,
        in_stock=item["stock"] > 0,
        stock_quantity=item["stock"],
        unit=item["unit"]
    )

if __name__ == "__main__":
    import uvicorn
    # Cloud Run requires listening on 0.0.0.0 and PORT env var, or 8080 default
    import os
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
