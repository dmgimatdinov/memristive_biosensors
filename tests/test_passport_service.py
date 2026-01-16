# test_passport_service.py

from services.passport_service import PassportService
from domain.models import Analyte, BioRecognitionLayer
from db.manager import DatabaseManager

def test_save_valid_passport():
    db = DatabaseManager()
    service = PassportService(db)
    
    analyte = Analyte(ta_id="TA_TEST", ta_name="Test Analyte", t_max=50.0)
    bio = BioRecognitionLayer(bre_id="BRE_TEST", bre_name="Test Bio")
    # ... и т.д.
    
    ok, msg = service.save_passport(analyte, bio, ...)
    assert ok is True

def test_duplicate_detection():
    db = DatabaseManager()
    service = PassportService(db)
    
    analyte = Analyte(ta_id="TA_DUP", ta_name="Duplicate")
    bio = BioRecognitionLayer(bre_id="BRE_DUP", bre_name="Duplicate")
    
    # Первый раз
    service.save_passport(analyte, bio, ...)
    
    # Второй раз — должен вернуть DUPLICATE
    ok, result = service.save_passport(analyte, bio, ...)
    assert ok is False
    assert result[0] == "DUPLICATE"
