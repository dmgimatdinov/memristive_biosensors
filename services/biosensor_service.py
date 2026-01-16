# services/biosensor_service.py
from db.manager import DatabaseManager
from domain.models import Analyte, BioRecognitionLayer
from domain.config import FIELD_CONSTRAINTS
from typing import Dict, Any, Optional

class BiosensorService:
    """Бизнес-логика для работы с биосенсорами (без Streamlit)."""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def validate_field(self, entity_type: str, field_name: str, value: float) -> bool:
        """Валидация поля по ограничениям"""
        if entity_type not in FIELD_CONSTRAINTS:
            return True
        if field_name not in FIELD_CONSTRAINTS[entity_type]:
            return True
        
        constraint = FIELD_CONSTRAINTS[entity_type][field_name]
        return constraint['min'] <= value <= constraint['max']
    
    def validate_analyte(self, data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Валидация данных аналита"""
        if not data.get('ta_id'):
            return False, "ID аналита обязателен"
        if not data.get('ta_name'):
            return False, "Название обязательно"
        
        # Проверка типов и диапазонов
        for field, value in data.items():
            if value is not None and field in FIELD_CONSTRAINTS['analyte']:
                if not self.validate_field('analyte', field, value):
                    constraint = FIELD_CONSTRAINTS['analyte'][field]
                    return False, f"{field}: значение вне диапазона {constraint['min']}-{constraint['max']}"
        
        return True, None
    
    def save_analyte(self, data: Dict[str, Any]) -> tuple[bool, str]:
        """Сохранение аналита (с валидацией)"""
        is_valid, error_msg = self.validate_analyte(data)
        if not is_valid:
            return False, error_msg
        
        result = self.db.insert_analyte(data)
        if result is True:
            return True, f"Аналит {data['ta_id']} сохранён"
        elif result == "DUPLICATE":
            return False, f"Аналит {data['ta_id']} уже существует"
        else:
            return False, "Ошибка при сохранении"
    
    def get_all_analytes(self, limit: int = 50, offset: int = 0) -> list[Dict]:
        """Получение аналитов с пагинацией"""
        return self.db.list_all_analytes_paginated(limit, offset)
