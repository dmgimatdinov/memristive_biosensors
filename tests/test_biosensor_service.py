# test_biosensor_service.py
from services.biosensor_service import BiosensorService
from db.manager import DatabaseManager

def test_validate_analyte():
    db = DatabaseManager()
    service = BiosensorService(db)
    
    # Валидные данные
    data = {"ta_id": "TA001", "ta_name": "Glucose", "t_max": 50.0}
    is_valid, msg = service.validate_analyte(data)
    assert is_valid is True
    
    # Невалидные данные
    data = {"ta_id": "TA001", "ta_name": "Glucose", "t_max": 500.0}  # вне диапазона
    is_valid, msg = service.validate_analyte(data)
    assert is_valid is False
