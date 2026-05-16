import nicegui as ui
from src.database_query.building_database import insertBuildings
def addRooms():
    with ui.dialog() as dialog, ui.card():
    rooms_name = ui.input("Rooms")
    
    if ui.button("Submit"):
        insertRooms(rooms_name)
