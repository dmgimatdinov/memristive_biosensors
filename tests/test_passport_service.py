# test_passport_service.py

from services.passport_service import PassportService
from domain.models import Analyte, BioRecognitionLayer, ImmobilizationLayer, MemristiveLayer
from db.manager import DatabaseManager

def test_save_valid_passport():
    db = DatabaseManager()
    service = PassportService(db)
    
    analyte = Analyte(
        ta_id="TA_TEST", 
        ta_name="Test Analyte", 
        ph_min=5.0, ph_max=8.0  # Обязательные по SENSORLAYERSCONFIG
    )
    bio = BioRecognitionLayer(
        bre_id="BRE_TEST", 
        bre_name="Test Bio", 
        ph_min=5.0, ph_max=8.0, t_min=20.0, t_max=40.0
    )
    immob = ImmobilizationLayer(im_id="IM_TEST", im_name="Test Immob", ph_min=5.0, ph_max=8.0)
    mem = MemristiveLayer(mem_id="MEM_TEST", mem_name="Test Mem", ph_min=5.0, ph_max=8.0)

    
    ok, msg = service.save_passport(analyte, bio, immob, mem)
    assert ok is True

def test_duplicate_detection():
    db = DatabaseManager()
    service = PassportService(db)
    
    analyte = Analyte(ta_id="TA_DUP", ta_name="Duplicate")
    bio = BioRecognitionLayer(bre_id="BRE_DUP", bre_name="Duplicate")
    immob = ImmobilizationLayer(im_id="IM_TEST", im_name="Duplicate")
    mem = MemristiveLayer(mem_id="MEM_TEST", mem_name="Duplicate")
    
    # Первый раз
    service.save_passport(analyte, bio, immob, mem)
    
    # Второй раз — должен вернуть DUPLICATE
    ok, result = service.save_passport(analyte, bio, immob, mem)
    assert ok is False
    assert result[0] == "DUPLICATE"
