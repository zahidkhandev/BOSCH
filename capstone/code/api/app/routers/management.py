from typing import List
from fastapi import APIRouter, Depends, HTTPException
from app import models
from app.database import get_db
import sqlite3

router = APIRouter(
    prefix="/turbines",
    tags=["Turbine Management"]
)

@router.post("/", response_model=models.Turbine, status_code=201, summary="Create a New Turbine")
def create_turbine(turbine: models.TurbineCreate, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO turbine_metadata (location, manufacturer, model) VALUES (?, ?, ?)",
            (turbine.location, turbine.manufacturer, turbine.model)
        )
        db.commit()
        new_turbine_id = cursor.lastrowid
        
        # Retrieve the newly created turbine to return its full details
        cursor.execute("SELECT * FROM turbine_metadata WHERE turbine_id = ?", (new_turbine_id,))
        new_turbine = cursor.fetchone()
        if not new_turbine:
            raise HTTPException(status_code=500, detail="Failed to retrieve new turbine after creation.")
            
        return dict(new_turbine)
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Failed to create turbine: {e}")

@router.get("/", response_model=List[models.Turbine], summary="Get All Turbine Details")
def get_all_turbines(db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM turbine_metadata")
    turbines = cursor.fetchall()
    return [dict(row) for row in turbines]

@router.get("/{turbine_id}", response_model=models.Turbine, summary="Get a Specific Turbine's Details")
def get_turbine(turbine_id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM turbine_metadata WHERE turbine_id = ?", (turbine_id,))
    turbine = cursor.fetchone()
    if not turbine:
        raise HTTPException(status_code=404, detail="Turbine not found.")
    return dict(turbine)

@router.put("/{turbine_id}", response_model=models.Turbine, summary="Update a Turbine's Details")
def update_turbine(turbine_id: int, turbine: models.TurbineUpdate, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    
    # First, check if the turbine exists to provide a clear 404 error
    cursor.execute("SELECT turbine_id FROM turbine_metadata WHERE turbine_id = ?", (turbine_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Turbine not found.")
    
    # If it exists, perform the update
    cursor.execute(
        "UPDATE turbine_metadata SET location=?, manufacturer=?, model=? WHERE turbine_id=?",
        (turbine.location, turbine.manufacturer, turbine.model, turbine_id)
    )
    db.commit()
    
    # Retrieve the updated data to return it
    cursor.execute("SELECT * FROM turbine_metadata WHERE turbine_id = ?", (turbine_id,))
    updated_turbine = cursor.fetchone()
    return dict(updated_turbine)