import nicegui as ui
from src.database_query.building_database import insertBuildings

def addBuildings():
    with ui.dialog() as dialog, ui.card():
        buildings_name = ui.input("Buildings")
    
        if ui.button("Chấp nhận"):
            insertBuilding(buildings_name)



