# domain/config.py
from domain.models import FieldConfig

FIELD_CONSTRAINTS = {
    'analyte': {
        'ph_min': {'min': 2.0, 'max': 10.0},
        'ph_max': {'min': 2.0, 'max': 10.0},
        't_max': {'min': 0, 'max': 180},
        'stability': {'min': 0, 'max': 365},
        'half_life': {'min': 0, 'max': 8760},
        'power_consumption': {'min': 0, 'max': 1000}
    },
    'bio_recognition': {
        'ph_min': {'min': 2.0, 'max': 10.0},
        'ph_max': {'min': 2.0, 'max': 10.0},
        't_min': {'min': 4, 'max': 120},
        't_max': {'min': 4, 'max': 120},
        'sensitivity': {'min': 0, 'max': 20000},
        'reproducibility': {'min': 0, 'max': 100},
        'response_time': {'min': 0, 'max': 3600},
        'stability': {'min': 0, 'max': 365},
        'lod': {'min': 0, 'max': 50000},
        'durability': {'min': 0, 'max': 8760},
        'power_consumption': {'min': 0, 'max': 1000},
        'dr_min': {'min': 0.1, 'max': 1000000000000},
        'dr_max': {'min': 0.1, 'max': 1000000000000}
    },
    # ... и т.д. ...
}

FORMS_CONFIG = {
    'analyte': [
        FieldConfig(label='ID аналита:', var_name='ta_id', hint='Например: TA001'),
        FieldConfig(label='Название:', var_name='ta_name', hint='Полное название аналита'),
        FieldConfig(label='pH диапазон:', type='range', min_var='ph_min', max_var='ph_max', hint='2.0 — 10.0'),
        FieldConfig(label='Макс. температура (°C):', var_name='t_max', hint='0-180'),
        FieldConfig(label='Стабильность (дни):', var_name='stability', hint='0-365'),
        FieldConfig(label='Период полураспада (ч):', var_name='half_life', hint='0-8760'),
        FieldConfig(label='Энергопотребление (мВт):', var_name='power_consumption', hint='0-1000')
    ],
    'bio_recognition': [
        FieldConfig(label='ID биослоя:', var_name='bre_id', hint='Например: BRE001'),
        FieldConfig(label='Название:', var_name='bre_name', hint='Тип биослоя'),
        FieldConfig(label='pH диапазон:', type='range', min_var='ph_min', max_var='ph_max', hint='2.0 — 10.0'),
        FieldConfig(label='Температурный диапазон (°C):', type='range', min_var='t_min', max_var='t_max', hint='2 — 120'),
        FieldConfig(label='Диапазон измерений (пМ):', type='range', min_var='dr_min', max_var='dr_max', hint='0.1 — 1*10^12'),
        FieldConfig(label='Чувствительность (мкА/(мкМ*см^2)):', var_name='sensitivity', hint='0.01 — 1000'),
        FieldConfig(label='Воспроизводимость (%):', var_name='reproducibility', hint='0-100'),
        FieldConfig(label='Время отклика (с):', var_name='response_time', hint='0-3600'),
        FieldConfig(label='Стабильность (дни):', var_name='stability', hint='0-365'),
        FieldConfig(label='Предел обнаружения (нМ):', var_name='lod', hint='0-100000'),
        FieldConfig(label='Долговечность (ч):', var_name='durability', hint='0-100000'),
        FieldConfig(label='Энергопотребление (мВт):', var_name='power_consumption', hint='0-1000')
    ],
    # ... и т.д. ...
}
