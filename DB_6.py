import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import re
from typing import Dict, Any, List
import json
from functools import lru_cache
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, filename='biosensor.log',
                    format='%(asctime)s - %(levelname)s - %(message)s')

class DatabaseManager:
    """Класс для управления операциями с базой данных SQLite для приложения BiosensorGUI."""
    def __init__(self, db_name="memristive_biosensor.db"):
        self.db_name = db_name
        self.logger = logging.getLogger(__name__)  # Инициализируем логгер ПЕРВЫМ
        self.conn = sqlite3.connect(db_name)
        self.conn.execute("PRAGMA foreign_keys = ON")  # Включение поддержки внешних ключей
        self.create_tables()

    def create_tables(self):
        """Создание таблиц базы данных, если они не существуют."""
        tables = [
            """
            CREATE TABLE IF NOT EXISTS Analytes (
                TA_ID VARCHAR PRIMARY KEY,
                TA_Name VARCHAR NOT NULL,
                PH_Min REAL,
                PH_Max REAL,
                T_Max REAL,
                ST REAL,
                HL REAL,
                PC REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS BioRecognitionLayers (
                BRE_ID VARCHAR PRIMARY KEY,
                BRE_Name VARCHAR NOT NULL,
                PH_Min REAL,
                PH_Max REAL,
                T_Min REAL,
                T_Max REAL,
                SN REAL,
                DR_Min REAL,
                DR_Max REAL,
                RP REAL,
                TR REAL,
                ST REAL,
                LOD REAL,
                HL REAL,
                PC REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS ImmobilizationLayers (
                IM_ID VARCHAR PRIMARY KEY,
                IM_Name VARCHAR NOT NULL,
                PH_Min REAL,
                PH_Max REAL,
                T_Min REAL,
                T_Max REAL,
                MP REAL,
                Adh VARCHAR,
                Sol VARCHAR,
                K_IM REAL,
                RP REAL,
                TR REAL,
                ST REAL,
                HL REAL,
                PC REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS MemristiveLayers (
                MEM_ID VARCHAR PRIMARY KEY,
                MEM_Name VARCHAR NOT NULL,
                PH_Min REAL,
                PH_Max REAL,
                T_Min REAL,
                T_Max REAL,
                MP REAL,
                SN REAL,
                DR_Min REAL,
                DR_Max REAL,
                RP REAL,
                TR REAL,
                ST REAL,
                LOD REAL,
                HL REAL,
                PC REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS SensorCombinations (
                Combo_ID VARCHAR PRIMARY KEY,
                TA_ID VARCHAR NOT NULL,
                BRE_ID VARCHAR NOT NULL,
                IM_ID VARCHAR NOT NULL,
                MEM_ID VARCHAR NOT NULL,
                SN_total REAL,
                TR_total REAL,
                ST_total REAL,
                RP_total REAL,
                LOD_total REAL,
                DR_total VARCHAR,
                HL_total REAL,
                PC_total REAL,
                Score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (TA_ID) REFERENCES Analytes (TA_ID),
                FOREIGN KEY (BRE_ID) REFERENCES BioRecognitionLayers (BRE_ID),
                FOREIGN KEY (IM_ID) REFERENCES ImmobilizationLayers (IM_ID),
                FOREIGN KEY (MEM_ID) REFERENCES MemristiveLayers (MEM_ID)
            );
            """
        ]
        try:
            cursor = self.conn.cursor()
            for table in tables:
                cursor.execute(table)
            self.conn.commit()
            self.logger.info("Таблицы успешно созданы")
        except sqlite3.Error as e:
            self.logger.error(f"Ошибка создания таблиц: {e}")

    def insert_analyte(self, data: Dict[str, Any]) -> bool:
        """Вставка или замена аналита с проверкой дубликатов."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT TA_ID FROM Analytes WHERE TA_ID = ?", (data['TA_ID'],))
        if cursor.fetchone():
            if not messagebox.askyesno("Подтверждение перезаписи", f"Аналит {data['TA_ID']} уже существует. Перезаписать?"):
                return False
        query = """
        INSERT OR REPLACE INTO Analytes (TA_ID, TA_Name, PH_Min, PH_Max, T_Max, ST, HL, PC)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        try:
            cursor.execute(query, (
                data['TA_ID'], data['TA_Name'], data.get('PH_Min'),
                data.get('PH_Max'), data.get('T_Max'), data.get('ST'),
                data.get('HL'), data.get('PC')
            ))
            self.conn.commit()
            self.clear_cache()
            self.logger.info(f"Аналит {data['TA_ID']} успешно вставлен")
            return True
        except sqlite3.Error as e:
            self.logger.error(f"Ошибка вставки аналита: {e}")
            return False

    def insert_bio_recognition_layer(self, data: Dict[str, Any]) -> bool:
        """Вставка или замена биораспознающего слоя с проверкой дубликатов."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT BRE_ID FROM BioRecognitionLayers WHERE BRE_ID = ?", (data['BRE_ID'],))
        if cursor.fetchone():
            if not messagebox.askyesno("Подтверждение перезаписи", f"Биослой {data['BRE_ID']} уже существует. Перезаписать?"):
                return False
        query = """
        INSERT OR REPLACE INTO BioRecognitionLayers 
        (BRE_ID, BRE_Name, PH_Min, PH_Max, T_Min, T_Max, SN, DR_Min, DR_Max, RP, TR, ST, LOD, HL, PC)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        try:
            cursor.execute(query, (
                data['BRE_ID'], data['BRE_Name'], data.get('PH_Min'), data.get('PH_Max'),
                data.get('T_Min'), data.get('T_Max'), data.get('SN'), data.get('DR_Min'),
                data.get('DR_Max'), data.get('RP'), data.get('TR'), data.get('ST'),
                data.get('LOD'), data.get('HL'), data.get('PC')
            ))
            self.conn.commit()
            self.clear_cache()
            self.logger.info(f"Биослой {data['BRE_ID']} успешно вставлен")
            return True
        except sqlite3.Error as e:
            self.logger.error(f"Ошибка вставки биослоя: {e}")
            return False

    def insert_immobilization_layer(self, data: Dict[str, Any]) -> bool:
        """Вставка или замена иммобилизационного слоя с проверкой дубликатов."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT IM_ID FROM ImmobilizationLayers WHERE IM_ID = ?", (data['IM_ID'],))
        if cursor.fetchone():
            if not messagebox.askyesno("Подтверждение перезаписи", f"Иммобилизационный слой {data['IM_ID']} уже существует. Перезаписать?"):
                return False
        query = """
        INSERT OR REPLACE INTO ImmobilizationLayers 
        (IM_ID, IM_Name, PH_Min, PH_Max, T_Min, T_Max, MP, Adh, Sol, K_IM, RP, TR, ST, HL, PC)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        try:
            cursor.execute(query, (
                data['IM_ID'], data['IM_Name'], data.get('PH_Min'), data.get('PH_Max'),
                data.get('T_Min'), data.get('T_Max'), data.get('MP'), data.get('Adh'),
                data.get('Sol'), data.get('K_IM'), data.get('RP'), data.get('TR'),
                data.get('ST'), data.get('HL'), data.get('PC')
            ))
            self.conn.commit()
            self.clear_cache()
            self.logger.info(f"Иммобилизационный слой {data['IM_ID']} успешно вставлен")
            return True
        except sqlite3.Error as e:
            self.logger.error(f"Ошибка вставки иммобилизационного слоя: {e}")
            return False

    def insert_memristive_layer(self, data: Dict[str, Any]) -> bool:
        """Вставка или замена мемристивного слоя с проверкой дубликатов."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT MEM_ID FROM MemristiveLayers WHERE MEM_ID = ?", (data['MEM_ID'],))
        if cursor.fetchone():
            if not messagebox.askyesno("Подтверждение перезаписи", f"Мемристивный слой {data['MEM_ID']} уже существует. Перезаписать?"):
                return False
        query = """
        INSERT OR REPLACE INTO MemristiveLayers 
        (MEM_ID, MEM_Name, PH_Min, PH_Max, T_Min, T_Max, MP, SN, DR_Min, DR_Max, RP, TR, ST, LOD, HL, PC)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        try:
            cursor.execute(query, (
                data['MEM_ID'], data['MEM_Name'], data.get('PH_Min'), data.get('PH_Max'),
                data.get('T_Min'), data.get('T_Max'), data.get('MP'), data.get('SN'),
                data.get('DR_Min'), data.get('DR_Max'), data.get('RP'), data.get('TR'),
                data.get('ST'), data.get('LOD'), data.get('HL'), data.get('PC')
            ))
            self.conn.commit()
            self.clear_cache()
            self.logger.info(f"Мемристивный слой {data['MEM_ID']} успешно вставлен")
            return True
        except sqlite3.Error as e:
            self.logger.error(f"Ошибка вставки мемристивного слоя: {e}")
            return False
        
    def insert_sensor_combination(self, data: Dict[str, Any]) -> bool:
        """Вставка или замена комбинации сенсора с проверкой дубликатов."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT Combo_ID FROM SensorCombinations WHERE Combo_ID = ?", (data['Combo_ID'],))
        if cursor.fetchone():
            if not messagebox.askyesno("Подтверждение перезаписи", f"Комбинация {data['Combo_ID']} уже существует. Перезаписать?"):
                return False
        query = """
        INSERT OR REPLACE INTO SensorCombinations 
        (Combo_ID, TA_ID, BRE_ID, IM_ID, MEM_ID, SN_total, TR_total, ST_total, RP_total, LOD_total, DR_total, HL_total, PC_total, Score, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        try:
            cursor.execute(query, (
                data['Combo_ID'], data.get('TA_ID'), data.get('BRE_ID'), data.get('IM_ID'),
                data.get('MEM_ID'), data.get('SN_total'), data.get('TR_total'), data.get('ST_total'),
                data.get('RP_total'), data.get('LOD_total'), data.get('DR_total'), data.get('HL_total'),
                data.get('PC_total'), data.get('Score'), data.get('created_at')
            ))
            self.conn.commit()
            self.clear_cache()
            self.logger.info(f"Комбинация сенсора {data['Combo_ID']} успешно вставлена")
            return True
        except sqlite3.Error as e:
            self.logger.error(f"Ошибка вставки комбинации сенсора: {e}")
            return False

    @lru_cache(maxsize=32)
    def list_all_analytes(self) -> List[Dict[str, Any]]:
        """Получение всех аналитов с выбором конкретных столбцов."""
        query = """
        SELECT TA_ID, TA_Name, PH_Min, PH_Max, T_Max, ST
        FROM Analytes
        ORDER BY TA_Name
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            columns = [description[0] for description in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            self.logger.info(f"Получено {len(results)} аналитов")
            return results
        except sqlite3.Error as e:
            self.logger.error(f"Ошибка получения аналитов: {e}")
            return []

    @lru_cache(maxsize=32)
    def list_all_bio_recognition_layers(self) -> List[Dict[str, Any]]:
        """Получение всех биораспознающих слоев."""
        query = """
        SELECT BRE_ID, BRE_Name, PH_Min, PH_Max, T_Min, T_Max, SN
        FROM BioRecognitionLayers
        ORDER BY BRE_Name
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            columns = [description[0] for description in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            self.logger.info(f"Получено {len(results)} биослоев")
            return results
        except sqlite3.Error as e:
            self.logger.error(f"Ошибка получения биослоев: {e}")
            return []

    @lru_cache(maxsize=32)
    def list_all_immobilization_layers(self) -> List[Dict[str, Any]]:
        """Получение всех иммобилизационных слоев."""
        query = """
        SELECT IM_ID, IM_Name, PH_Min, PH_Max, T_Min, T_Max, MP
        FROM ImmobilizationLayers
        ORDER BY IM_Name
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            columns = [description[0] for description in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            self.logger.info(f"Получено {len(results)} иммобилизационных слоев")
            return results
        except sqlite3.Error as e:
            self.logger.error(f"Ошибка получения иммобилизационных слоев: {e}")
            return []

    @lru_cache(maxsize=32)
    def list_all_memristive_layers(self) -> List[Dict[str, Any]]:
        """Получение всех мемристивных слоев."""
        query = """
        SELECT MEM_ID, MEM_Name, PH_Min, PH_Max, T_Min, T_Max, SN
        FROM MemristiveLayers
        ORDER BY MEM_Name
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            columns = [description[0] for description in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            self.logger.info(f"Получено {len(results)} мемристивных слоев")
            return results
        except sqlite3.Error as e:
            self.logger.error(f"Ошибка получения мемристивных слоев: {e}")
            return []
        
    @lru_cache(maxsize=32)
    def list_all_sensor_combinations(self) -> List[Dict[str, Any]]:
        """Получение всех комбинаций сенсоров."""
        query = """
        SELECT Combo_ID, TA_ID, BRE_ID, IM_ID, MEM_ID, Score
        FROM SensorCombinations
        ORDER BY Combo_ID
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            columns = [description[0] for description in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            self.logger.info(f"Получено {len(results)} комбинаций сенсоров")
            return results
        except sqlite3.Error as e:
            self.logger.error(f"Ошибка получения комбинаций сенсоров: {e}")
            return []

    def list_all_analytes_paginated(self, limit: int, offset: int) -> List[Dict[str, Any]]:
        """Получение аналитов с пагинацией."""
        query = """
        SELECT TA_ID, TA_Name, PH_Min, PH_Max, T_Max, ST
        FROM Analytes
        ORDER BY TA_Name
        LIMIT ? OFFSET ?
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, (limit, offset))
            columns = [description[0] for description in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            self.logger.info(f"Получено {len(results)} аналитов (страница)")
            return results
        except sqlite3.Error as e:
            self.logger.error(f"Ошибка получения аналитов с пагинацией: {e}")
            return []

    def list_all_bio_recognition_layers_paginated(self, limit: int, offset: int) -> List[Dict[str, Any]]:
        """Получение биослоев с пагинацией."""
        query = """
        SELECT BRE_ID, BRE_Name, PH_Min, PH_Max, T_Min, T_Max, SN
        FROM BioRecognitionLayers
        ORDER BY BRE_Name
        LIMIT ? OFFSET ?
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, (limit, offset))
            columns = [description[0] for description in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            self.logger.info(f"Получено {len(results)} биослоев (страница)")
            return results
        except sqlite3.Error as e:
            self.logger.error(f"Ошибка получения биослоев с пагинацией: {e}")
            return []

    def list_all_immobilization_layers_paginated(self, limit: int, offset: int) -> List[Dict[str, Any]]:
        """Получение иммобилизационных слоев с пагинацией."""
        query = """
        SELECT IM_ID, IM_Name, PH_Min, PH_Max, T_Min, T_Max, MP
        FROM ImmobilizationLayers
        ORDER BY IM_Name
        LIMIT ? OFFSET ?
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, (limit, offset))
            columns = [description[0] for description in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            self.logger.info(f"Получено {len(results)} иммобилизационных слоев (страница)")
            return results
        except sqlite3.Error as e:
            self.logger.error(f"Ошибка получения иммобилизационных слоев с пагинацией: {e}")
            return []

    def list_all_memristive_layers_paginated(self, limit: int, offset: int) -> List[Dict[str, Any]]:
        """Получение мемристивных слоев с пагинацией."""
        query = """
        SELECT MEM_ID, MEM_Name, PH_Min, PH_Max, T_Min, T_Max, SN
        FROM MemristiveLayers
        ORDER BY MEM_Name
        LIMIT ? OFFSET ?
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, (limit, offset))
            columns = [description[0] for description in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            self.logger.info(f"Получено {len(results)} мемристивных слоев (страница)")
            return results
        except sqlite3.Error as e:
            self.logger.error(f"Ошибка получения мемристивных слоев с пагинацией: {e}")
            return []
    
    def list_all_sensor_combinations_paginated(self, limit: int, offset: int) -> List[Dict[str, Any]]:
        """Получение всех комбинаций сенсоров."""
        query = """
        SELECT Combo_ID, TA_ID, BRE_ID, IM_ID, MEM_ID, Score
        FROM SensorCombinations
        ORDER BY Combo_ID
        LIMIT ? OFFSET ?
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, (limit, offset))
            columns = [description[0] for description in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            self.logger.info(f"Получено {len(results)} комбинаций сенсоров (страница)")
            return results
        except sqlite3.Error as e:
            self.logger.error(f"Ошибка получения комбинаций сенсоров с пагинацией: {e}")
            return []

    def get_analyte_by_id(self, ta_id: str) -> Dict[str, Any]:
        """Получение аналита по ID."""
        query = """
        SELECT TA_ID, TA_Name, PH_Min, PH_Max, T_Max, ST, HL, PC
        FROM Analytes
        WHERE TA_ID = ?
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, (ta_id,))
            result = cursor.fetchone()
            if result:
                columns = [description[0] for description in cursor.description]
                self.logger.info(f"Получен аналит {ta_id}")
                return dict(zip(columns, result))
            return None
        except sqlite3.Error as e:
            self.logger.error(f"Ошибка получения аналита {ta_id}: {e}")
            return None

    def get_bio_recognition_layer_by_id(self, bre_id: str) -> Dict[str, Any]:
        """Получение биораспознающего слоя по ID."""
        query = """
        SELECT BRE_ID, BRE_Name, PH_Min, PH_Max, T_Min, T_Max, SN, DR_Min, DR_Max, RP, TR, ST, LOD, HL, PC
        FROM BioRecognitionLayers
        WHERE BRE_ID = ?
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, (bre_id,))
            result = cursor.fetchone()
            if result:
                columns = [description[0] for description in cursor.description]
                self.logger.info(f"Получен биослой {bre_id}")
                return dict(zip(columns, result))
            return None
        except sqlite3.Error as e:
            self.logger.error(f"Ошибка получения биослоя {bre_id}: {e}")
            return None

    def get_immobilization_layer_by_id(self, im_id: str) -> Dict[str, Any]:
        """Получение иммобилизационного слоя по ID."""
        query = """
        SELECT IM_ID, IM_Name, PH_Min, PH_Max, T_Min, T_Max, MP, Adh, Sol, K_IM, RP, TR, ST, HL, PC
        FROM ImmobilizationLayers
        WHERE IM_ID = ?
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, (im_id,))
            result = cursor.fetchone()
            if result:
                columns = [description[0] for description in cursor.description]
                self.logger.info(f"Получен иммобилизационный слой {im_id}")
                return dict(zip(columns, result))
            return None
        except sqlite3.Error as e:
            self.logger.error(f"Ошибка получения иммобилизационного слоя {im_id}: {e}")
            return None

    def get_memristive_layer_by_id(self, mem_id: str) -> Dict[str, Any]:
        """Получение мемристивного слоя по ID."""
        query = """
        SELECT MEM_ID, MEM_Name, PH_Min, PH_Max, T_Min, T_Max, MP, SN, DR_Min, DR_Max, RP, TR, ST, LOD, HL, PC
        FROM MemristiveLayers
        WHERE MEM_ID = ?
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, (mem_id,))
            result = cursor.fetchone()
            if result:
                columns = [description[0] for description in cursor.description]
                self.logger.info(f"Получен мемристивный слой {mem_id}")
                return dict(zip(columns, result))
            return None
        except sqlite3.Error as e:
            self.logger.error(f"Ошибка получения мемристивного слоя {mem_id}: {e}")
            return None

    def clear_cache(self):
        """Очистка кэша результатов запросов."""
        self.list_all_analytes.cache_clear()
        self.list_all_bio_recognition_layers.cache_clear()
        self.list_all_immobilization_layers.cache_clear()
        self.list_all_memristive_layers.cache_clear()
        self.list_all_sensor_combinations.cache_clear()
        self.logger.info("Кэш очищен")

    def close(self):
        """Закрытие соединения с базой данных."""
        self.conn.close()
        self.logger.info("Соединение с базой данных закрыто")

class Section:
    """Базовый класс для секций ввода в GUI."""
    def __init__(self, parent, title: str, color: str, fields: List[Dict]):
        self.frame = tk.LabelFrame(parent, text=title, font=('Arial', 12, 'bold'), fg=color, padx=10, pady=10)
        self.vars = {}
        self.create_fields(fields)

    def create_fields(self, fields):
        """Создание полей ввода на основе конфигурации."""
        for i, field in enumerate(fields):
            if field.get('type') == 'range':
                # Создание двух полей для диапазона
                tk.Label(self.frame, text=field['label'], anchor='w').grid(row=i, column=0, sticky='w', pady=2)
                
                # Фрейм для двух полей диапазона
                range_frame = tk.Frame(self.frame)
                range_frame.grid(row=i, column=1, padx=5, pady=2, sticky='ew')
                
                # Минимальное значение
                min_var = tk.StringVar()
                self.vars[field['min_var']] = min_var
                min_entry = tk.Entry(range_frame, textvariable=min_var, width=15)
                min_entry.pack(side='left', padx=(0, 2))
                self.setup_copy_paste(min_entry)  # Добавляем copy-paste
                
                # Разделитель
                tk.Label(range_frame, text="—").pack(side='left', padx=2)
                
                # Максимальное значение
                max_var = tk.StringVar()
                self.vars[field['max_var']] = max_var
                max_entry = tk.Entry(range_frame, textvariable=max_var, width=15)
                max_entry.pack(side='left', padx=(2, 0))
                self.setup_copy_paste(max_entry)  # Добавляем copy-paste
                
                if field.get('hint'):
                    tk.Label(self.frame, text=field['hint'], fg='gray', font=('Arial', 8)).grid(row=i, column=2, padx=5, sticky='w')
            else:
                # Обычное поле
                tk.Label(self.frame, text=field['label'], anchor='w').grid(row=i, column=0, sticky='w', pady=2)
                var = tk.StringVar()
                self.vars[field['var_name']] = var
                entry = tk.Entry(self.frame, textvariable=var, width=35)
                entry.grid(row=i, column=1, padx=5, pady=2, sticky='ew')
                self.setup_copy_paste(entry)  # Добавляем copy-paste
                if field.get('hint'):
                    tk.Label(self.frame, text=field['hint'], fg='gray', font=('Arial', 8)).grid(row=i, column=2, padx=5, sticky='w')
            
            self.frame.columnconfigure(1, weight=1)

    def setup_copy_paste(self, entry):
        """Настройка copy-paste для поля ввода."""
        def copy_text(event):
            try:
                entry.clipboard_clear()
                text = entry.selection_get()
                entry.clipboard_append(text)
            except tk.TclError:
                pass
        
        def paste_text(event):
            try:
                text = entry.clipboard_get()
                entry.insert(tk.INSERT, text)
            except tk.TclError:
                pass
        
        def cut_text(event):
            try:
                copy_text(event)
                entry.delete(tk.SEL_FIRST, tk.SEL_LAST)
            except tk.TclError:
                pass
        
        def select_all(event):
            entry.select_range(0, tk.END)
            return 'break'
        
        # Привязка клавиш
        # entry.bind('<Control-c>', copy_text) # already implemented
        # entry.bind('<Control-C>', copy_text) # already implemented
        # entry.bind('<Control-v>', paste_text) # already implemented
        # entry.bind('<Control-V>', paste_text) # already implemented
        entry.bind('<Control-x>', cut_text)
        entry.bind('<Control-X>', cut_text)
        entry.bind('<Control-a>', select_all)
        entry.bind('<Control-A>', select_all)
        
        # Привязка правой кнопки мыши для контекстного меню
        def show_context_menu(event):
            context_menu = tk.Menu(entry, tearoff=0)
            context_menu.add_command(label="Копировать", command=lambda: copy_text(None))
            context_menu.add_command(label="Вставить", command=lambda: paste_text(None))
            context_menu.add_command(label="Вырезать", command=lambda: cut_text(None))
            context_menu.add_separator()
            context_menu.add_command(label="Выделить все", command=lambda: select_all(None))
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
        
        entry.bind('<Button-3>', show_context_menu)  # Правая кнопка мыши
    def get_vars(self):
        """Возвращает переменные секции."""
        return self.vars

class AnalyteSection(Section):
    """Секция для ввода данных аналита."""
    def __init__(self, parent, fields):
        super().__init__(parent, "🎯 Целевой аналит (TA)", '#2196F3', fields)

class BioRecognitionSection(Section):
    """Секция для ввода данных биораспознающего слоя."""
    def __init__(self, parent, fields):
        super().__init__(parent, "🔴 Биораспознающий слой (BRE)", '#f44336', fields)

class ImmobilizationSection(Section):
    """Секция для ввода данных иммобилизационного слоя."""
    def __init__(self, parent, fields):
        super().__init__(parent, "🟡 Иммобилизационный слой (IM)", '#ff9800', fields)

class MemristiveSection(Section):
    """Секция для ввода данных мемристивного слоя."""
    def __init__(self, parent, fields):
        super().__init__(parent, "🟣 Мемристивный слой (MEM)", '#9c27b0', fields)

class BiosensorGUI:
    """GUI-приложение для управления паспортами мемристивных биосенсоров."""
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.root = tk.Tk()
        self.root.title("Паспорта мемристивных биосенсоров v2.0")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')

        # Инициализация базы данных
        self.db_manager = DatabaseManager()

        # Настройки пагинации
        self.page_size = 50
        self.current_page = 0
        self.current_data_type = 'analytes'  # Для отслеживания текущего типа данных в Treeview

        # Загрузка конфигурации или создание значений по умолчанию
        self.config = self.get_default_config()

        # Ограничения для валидации полей
        self.field_constraints = {
            'analyte': {
                'ph_min': {'min': 2.0, 'max': 10.0},  # Расширили диапазон
                'ph_max': {'min': 2.0, 'max': 10.0},  # Расширили диапазон
                't_max': {'min': 0, 'max': 180},
                'stability': {'min': 0, 'max': 365},
                'half_life': {'min': 0, 'max': 8760},
                'power_consumption': {'min': 0, 'max': 1000}
            },
            'bio_recognition': {
                'ph_min': {'min': 2.0, 'max': 10.0},  # Расширили диапазон
                'ph_max': {'min': 2.0, 'max': 10.0},  # Расширили диапазон
                't_min': {'min': 4, 'max': 120},
                't_max': {'min': 4, 'max': 120},
                'dr_min': {'min': 0.1, 'max': 1000000000000},
                'dr_max': {'min': 0.1, 'max': 1000000000000},
                'sensitivity': {'min': 0, 'max': 20000},
                'reproducibility': {'min': 0, 'max': 100},
                'response_time': {'min': 0, 'max': 3600},
                'stability': {'min': 0, 'max': 365},
                'lod': {'min': 0, 'max': 50000},
                'durability': {'min': 0, 'max': 8760},
                'power_consumption': {'min': 0, 'max': 1000}
            },
            'immobilization': {
                'ph_min': {'min': 2.0, 'max': 10.0},  # Расширили диапазон
                'ph_max': {'min': 2.0, 'max': 10.0},  # Расширили диапазон
                't_min': {'min': 4, 'max': 120},
                't_max': {'min': 4, 'max': 120},
                'young_modulus': {'min': 0, 'max': 1000},
                # 'adhesion': {'min': 0, 'max': 100}, # замена на строчный тип
                # 'solubility': {'min': 0, 'max': 100}, # замена на строчный тип
                'loss_coefficient': {'min': 0, 'max': 1},
                'reproducibility': {'min': 0, 'max': 100},
                'response_time': {'min': 0, 'max': 3600},
                'stability': {'min': 0, 'max': 365},
                'durability': {'min': 0, 'max': 8760},
                'power_consumption': {'min': 0, 'max': 1000}
            },
            'memristive': {
                'ph_min': {'min': 2.0, 'max': 10.0},
                'ph_max': {'min': 2.0, 'max': 10.0},
                't_min': {'min': 5, 'max': 120},
                't_max': {'min': 5, 'max': 120},
                'dr_min': {'min': 0.0000001, 'max': 100000000000},
                'dr_max': {'min': 0.0000001, 'max': 100000000000},
                'young_modulus': {'min': 0, 'max': 1000},
                'sensitivity': {'min': 0, 'max': 1000},
                'reproducibility': {'min': 0, 'max': 100},
                'response_time': {'min': 0, 'max': 3600},
                'stability': {'min': 0, 'max': 365},
                'lod': {'min': 0, 'max': 100000},
                'durability': {'min': 0, 'max': 100000},
                'power_consumption': {'min': 0, 'max': 1000}
            }
        }

        # Создание интерфейса
        self.sections = {}
        self.create_menu()
        self.create_notebook()
        self.create_data_entry_tab()
        self.create_database_tab()
        self.create_analysis_tab()

    def get_default_config(self):
        """Возвращает конфигурацию по умолчанию для полей."""
        return {
            'analyte': [
                {'label': 'ID аналита:', 'var_name': 'ta_id', 'hint': 'Например: TA001'},
                {'label': 'Название:', 'var_name': 'ta_name', 'hint': 'Полное название аналита'},
                {'label': 'pH диапазон:', 'type': 'range', 'min_var': 'ph_min', 'max_var': 'ph_max', 'hint': '2.0 — 10.0'},
                {'label': 'Макс. температура (°C):', 'var_name': 't_max', 'hint': '0-180'},
                {'label': 'Стабильность (дни):', 'var_name': 'stability', 'hint': '0-365'},
                {'label': 'Период полураспада (ч):', 'var_name': 'half_life', 'hint': '0-8760'},
                {'label': 'Энергопотребление (мВт):', 'var_name': 'power_consumption', 'hint': '0-1000'}
            ],
            'bio_recognition': [
                {'label': 'ID биослоя:', 'var_name': 'bre_id', 'hint': 'Например: BRE001'},
                {'label': 'Название:', 'var_name': 'bre_name', 'hint': 'Тип биослоя'},
                {'label': 'pH диапазон:', 'type': 'range', 'min_var': 'ph_min', 'max_var': 'ph_max', 'hint': '2.0 — 10.0'},
                {'label': 'Температурный диапазон (°C):', 'type': 'range', 'min_var': 't_min', 'max_var': 't_max', 'hint': '2 — 120'},
                {'label': 'Диапазон измерений (пМ):', 'type': 'range', 'min_var': 'dr_min', 'max_var': 'dr_max', 'hint': '0.1 — 1*10^12'},
                {'label': 'Чувствительность (мкА/(мкМ*см^2)):', 'var_name': 'sensitivity', 'hint': '0.01 — 1000'},
                {'label': 'Воспроизводимость (%):', 'var_name': 'reproducibility', 'hint': '0-100'},
                {'label': 'Время отклика (с):', 'var_name': 'response_time', 'hint': '0-3600'},
                {'label': 'Стабильность (дни):', 'var_name': 'stability', 'hint': '0-365'},
                {'label': 'Предел обнаружения (нМ):', 'var_name': 'lod', 'hint': '0-100000'},
                {'label': 'Долговечность (ч):', 'var_name': 'durability', 'hint': '0-100000'},
                {'label': 'Энергопотребление (мВт):', 'var_name': 'power_consumption', 'hint': '0-1000'}
            ],
            'immobilization': [
                {'label': 'ID иммобилизации:', 'var_name': 'im_id', 'hint': 'Например: IM001'},
                {'label': 'Название:', 'var_name': 'im_name', 'hint': 'Тип иммобилизации'},
                {'label': 'pH диапазон:', 'type': 'range', 'min_var': 'ph_min', 'max_var': 'ph_max', 'hint': '2.0 — 10.0'},
                {'label': 'Температурный диапазон (°C):', 'type': 'range', 'min_var': 't_min', 'max_var': 't_max', 'hint': '4 — 95'},
                {'label': 'Модуль Юнга (ГПа):', 'var_name': 'young_modulus', 'hint': '0-1000'},
                {'label': 'Адгезия (%):', 'var_name': 'adhesion', 'hint': 'Например: высокая'},
                {'label': 'Растворимость (%):', 'var_name': 'solubility', 'hint': 'Например: средняя'},
                {'label': 'Коэффициент потерь:', 'var_name': 'loss_coefficient', 'hint': '0-1'},
                {'label': 'Воспроизводимость (%):', 'var_name': 'reproducibility', 'hint': '0-100'},
                {'label': 'Время отклика (с):', 'var_name': 'response_time', 'hint': '0-3600'},
                {'label': 'Стабильность (дни):', 'var_name': 'stability', 'hint': '0-365'},
                {'label': 'Долговечность (ч):', 'var_name': 'durability', 'hint': '0-8760'},
                {'label': 'Энергопотребление (мВт):', 'var_name': 'power_consumption', 'hint': '0-1000'}
            ],
            'memristive': [
                {'label': 'ID мемристора:', 'var_name': 'mem_id', 'hint': 'Например: MEM001'},
                {'label': 'Название:', 'var_name': 'mem_name', 'hint': 'Тип мемристора'},
                {'label': 'pH диапазон:', 'type': 'range', 'min_var': 'ph_min', 'max_var': 'ph_max', 'hint': '2.0 — 10.0'},
                {'label': 'Температурный диапазон (°C):', 'type': 'range', 'min_var': 't_min', 'max_var': 't_max', 'hint': '5 — 100'},
                {'label': 'Диапазон измерений (пМ):', 'type': 'range', 'min_var': 'dr_min', 'max_var': 'dr_max', 'hint': '0.0000001 — 0-1*10^11'},
                {'label': 'Модуль Юнга (ГПа):', 'var_name': 'young_modulus', 'hint': '0-1000'},
                {'label': 'Чувствительность (мВ/dec):', 'var_name': 'sensitivity', 'hint': '0-1000'},
                {'label': 'Воспроизводимость (%):', 'var_name': 'reproducibility', 'hint': '0-100'},
                {'label': 'Время отклика (с):', 'var_name': 'response_time', 'hint': '0-3600'},
                {'label': 'Стабильность (дни):', 'var_name': 'stability', 'hint': '0-365'},
                {'label': 'Предел обнаружения (нМ):', 'var_name': 'lod', 'hint': '0-1*10^5'},
                {'label': 'Долговечность (ч):', 'var_name': 'durability', 'hint': '0-8760'},
                {'label': 'Энергопотребление (мВт):', 'var_name': 'power_consumption', 'hint': '0-1000'}
            ]
        }

    def create_menu(self):
        """Создание меню приложения."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Сохранить паспорт", command=self.save_passport)
        file_menu.add_command(label="Загрузить паспорт", command=self.load_passport)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Инструменты", menu=tools_menu)
        tools_menu.add_command(label="Очистить форму", command=self.clear_form)
        tools_menu.add_command(label="Экспорт данных", command=self.export_data)
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label="О программе", command=self.about)

    def create_notebook(self):
        """Создание вкладок интерфейса."""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        style = ttk.Style()
        style.configure('TNotebook.Tab', padding=[20, 8])

    def create_data_entry_tab(self):
        """Создание вкладки ввода паспортов."""
        self.entry_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.entry_frame, text="🔬 Ввод паспортов")
        title_label = tk.Label(self.entry_frame, text="🔬 Ввод паспорта биосенсора v2.0",
                              font=('Arial', 16, 'bold'), bg='#e8f4fd', pady=10)
        title_label.pack(fill='x', padx=5, pady=5)
        canvas = tk.Canvas(self.entry_frame, bg='#f0f0f0')
        scrollbar = ttk.Scrollbar(self.entry_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        self.create_sections()
        self.create_control_buttons()
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

    def create_sections(self):
        """Создание секций ввода из конфигурации."""
        self.sections['analyte'] = AnalyteSection(self.scrollable_frame, self.config['analyte'])
        self.sections['analyte'].frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        self.sections['bio_recognition'] = BioRecognitionSection(self.scrollable_frame, self.config['bio_recognition'])
        self.sections['bio_recognition'].frame.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')
        self.sections['immobilization'] = ImmobilizationSection(self.scrollable_frame, self.config['immobilization'])
        self.sections['immobilization'].frame.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')
        self.sections['memristive'] = MemristiveSection(self.scrollable_frame, self.config['memristive'])
        self.sections['memristive'].frame.grid(row=1, column=1, padx=10, pady=10, sticky='nsew')

    def create_control_buttons(self):
        """Создание кнопок управления."""
        button_frame = tk.Frame(self.scrollable_frame, bg='#f0f0f0')
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        tk.Button(button_frame, text="💾 Сохранить паспорт", command=self.save_passport_to_db,
                  bg='#4CAF50', fg='white', font=('Arial', 12, 'bold'), padx=20, pady=10).pack(side='left', padx=10)
        tk.Button(button_frame, text="🗑️ Очистить форму", command=self.clear_form,
                  bg='#f44336', fg='white', font=('Arial', 12, 'bold'), padx=20, pady=10).pack(side='left', padx=10)
        tk.Button(button_frame, text="📁 Загрузить паспорт", command=self.load_passport_from_db,
                  bg='#2196F3', fg='white', font=('Arial', 12, 'bold'), padx=20, pady=10).pack(side='left', padx=10)

    def create_database_tab(self):
        """Создание вкладки базы данных."""
        self.db_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.db_frame, text="📊 База данных")
        title_label = tk.Label(self.db_frame, text="📊 База данных биосенсоров",
                              font=('Arial', 16, 'bold'), bg='#e8f4fd', pady=10)
        title_label.pack(fill='x', padx=5, pady=5)
        btn_frame = tk.Frame(self.db_frame)
        btn_frame.pack(fill='x', padx=10, pady=5)
        tk.Button(btn_frame, text="TA (аналиты)", command=self.show_analytes,
                  bg='#2196F3', fg='white', padx=10).pack(side='left', padx=5)
        tk.Button(btn_frame, text="BRE (биослои)", command=self.show_bio_layers,
                  bg='#f44336', fg='white', padx=10).pack(side='left', padx=5)
        tk.Button(btn_frame, text="IM (иммобилизация)", command=self.show_immobilization_layers,
                  bg='#ff9800', fg='white', padx=10).pack(side='left', padx=5)
        tk.Button(btn_frame, text="MEM (мемристоры)", command=self.show_memristive_layers,
                  bg='#9c27b0', fg='white', padx=10).pack(side='left', padx=5)
        tk.Button(btn_frame, text="Обновить", command=self.refresh_data,
                  bg='#607d8b', fg='white', padx=10).pack(side='left', padx=5)
        self.tree = ttk.Treeview(self.db_frame)
        self.tree.pack(fill='both', expand=True, padx=10, pady=10)
        scrollbar_tree = ttk.Scrollbar(self.db_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar_tree.set)
        scrollbar_tree.pack(side='right', fill='y')

    def create_analysis_tab(self):
        """Создание вкладки анализа."""
        self.analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.analysis_frame, text="📈 Анализ")
        title_label = tk.Label(self.analysis_frame, text="📈 Анализ характеристик",
                              font=('Arial', 16, 'bold'), bg='#e8f4fd', pady=10)
        title_label.pack(fill='x', padx=5, pady=5)
        analysis_btn_frame = tk.Frame(self.analysis_frame)
        analysis_btn_frame.pack(fill='x', padx=10, pady=5)
        tk.Button(analysis_btn_frame, text="Лучшие комбинации", command=self.show_best_combinations,
                  bg='#4CAF50', fg='white', padx=15).pack(side='left', padx=5)
        tk.Button(analysis_btn_frame, text="Сравнительный анализ", command=self.comparative_analysis,
                  bg='#2196F3', fg='white', padx=15).pack(side='left', padx=5)
        tk.Button(analysis_btn_frame, text="Статистика", command=self.show_statistics,
                  bg='#ff9800', fg='white', padx=15).pack(side='left', padx=5)
        self.analysis_text = tk.Text(self.analysis_frame, height=20, font=('Courier', 10))
        self.analysis_text.pack(fill='both', expand=True, padx=10, pady=10)
        scrollbar_analysis = ttk.Scrollbar(self.analysis_frame, orient='vertical',
                                          command=self.analysis_text.yview)
        self.analysis_text.configure(yscrollcommand=scrollbar_analysis.set)
        scrollbar_analysis.pack(side='right', fill='y')

    def save_passport_to_db(self):
        """Сохранение всех паспортов в базу данных."""
        try:
            # Сохранение аналита
            analyte_vars = self.sections['analyte'].get_vars()
            if analyte_vars['ta_id'].get():
                analyte_data = {
                    'TA_ID': analyte_vars['ta_id'].get(),
                    'TA_Name': analyte_vars['ta_name'].get(),
                    'PH_Min': self.safe_float_convert(analyte_vars['ph_min'].get(), 'ph_min', 'analyte'),
                    'PH_Max': self.safe_float_convert(analyte_vars['ph_max'].get(), 'ph_max', 'analyte'),
                    'T_Max': self.safe_float_convert(analyte_vars['t_max'].get(), 't_max', 'analyte'),
                    'ST': self.safe_float_convert(analyte_vars['stability'].get(), 'stability', 'analyte'),
                    'HL': self.safe_float_convert(analyte_vars['half_life'].get(), 'half_life', 'analyte'),
                    'PC': self.safe_float_convert(analyte_vars['power_consumption'].get(), 'power_consumption', 'analyte')
                }
                if None in analyte_data.values():
                    return
                # Проверка диапазона pH
                if analyte_data['PH_Min'] > analyte_data['PH_Max']:
                    messagebox.showerror("Ошибка", "pH минимум не может быть больше pH максимума")
                    return
                if self.db_manager.insert_analyte(analyte_data):
                    self.logger.info(f"Аналит {analyte_data['TA_ID']} успешно сохранен")

            # Сохранение биораспознающего слоя
            bio_vars = self.sections['bio_recognition'].get_vars()
            if bio_vars['bre_id'].get():
                bio_data = {
                    'BRE_ID': bio_vars['bre_id'].get(),
                    'BRE_Name': bio_vars['bre_name'].get(),
                    'PH_Min': self.safe_float_convert(bio_vars['ph_min'].get(), 'ph_min', 'bio_recognition'),
                    'PH_Max': self.safe_float_convert(bio_vars['ph_max'].get(), 'ph_max', 'bio_recognition'),
                    'T_Min': self.safe_float_convert(bio_vars['t_min'].get(), 't_min', 'bio_recognition'),
                    'T_Max': self.safe_float_convert(bio_vars['t_max'].get(), 't_max', 'bio_recognition'),
                    'SN': self.safe_float_convert(bio_vars['sensitivity'].get(), 'sensitivity', 'bio_recognition'),
                    'DR_Min': self.safe_float_convert(bio_vars['dr_min'].get(), 'dr_min', 'bio_recognition'),
                    'DR_Max': self.safe_float_convert(bio_vars['dr_max'].get(), 'dr_max', 'bio_recognition'),
                    'RP': self.safe_float_convert(bio_vars['reproducibility'].get(), 'reproducibility', 'bio_recognition'),
                    'TR': self.safe_float_convert(bio_vars['response_time'].get(), 'response_time', 'bio_recognition'),
                    'ST': self.safe_float_convert(bio_vars['stability'].get(), 'stability', 'bio_recognition'),
                    'LOD': self.safe_float_convert(bio_vars['lod'].get(), 'lod', 'bio_recognition'),
                    'HL': self.safe_float_convert(bio_vars['durability'].get(), 'durability', 'bio_recognition'),
                    'PC': self.safe_float_convert(bio_vars['power_consumption'].get(), 'power_consumption', 'bio_recognition')
                }
                if None in bio_data.values():
                    return
                # Проверка диапазонов
                if bio_data['PH_Min'] > bio_data['PH_Max']:
                    messagebox.showerror("Ошибка", "pH минимум не может быть больше pH максимума")
                    return
                if bio_data['T_Min'] > bio_data['T_Max']:
                    messagebox.showerror("Ошибка", "Температура минимум не может быть больше температуры максимума")
                    return
                if bio_data['DR_Min'] > bio_data['DR_Max']:
                    messagebox.showerror("Ошибка", "Диапазон измерений: минимум не может быть больше максимума")
                    return
                if self.db_manager.insert_bio_recognition_layer(bio_data):
                    self.logger.info(f"Биослой {bio_data['BRE_ID']} успешно сохранен")

            # Сохранение иммобилизационного слоя
            immob_vars = self.sections['immobilization'].get_vars()
            if immob_vars['im_id'].get():
                immob_data = {
                    'IM_ID': immob_vars['im_id'].get(),
                    'IM_Name': immob_vars['im_name'].get(),
                    'PH_Min': self.safe_float_convert(immob_vars['ph_min'].get(), 'ph_min', 'immobilization'),
                    'PH_Max': self.safe_float_convert(immob_vars['ph_max'].get(), 'ph_max', 'immobilization'),
                    'T_Min': self.safe_float_convert(immob_vars['t_min'].get(), 't_min', 'immobilization'),
                    'T_Max': self.safe_float_convert(immob_vars['t_max'].get(), 't_max', 'immobilization'),
                    'MP': self.safe_float_convert(immob_vars['young_modulus'].get(), 'young_modulus', 'immobilization'),
                    'Adh': immob_vars['adhesion'].get(), # смена типа на строчный
                    'Sol': immob_vars['solubility'].get(), # замена на строчный тип
                    'K_IM': self.safe_float_convert(immob_vars['loss_coefficient'].get(), 'loss_coefficient', 'immobilization'),
                    'RP': self.safe_float_convert(immob_vars['reproducibility'].get(), 'reproducibility', 'immobilization'),
                    'TR': self.safe_float_convert(immob_vars['response_time'].get(), 'response_time', 'immobilization'),
                    'ST': self.safe_float_convert(immob_vars['stability'].get(), 'stability', 'immobilization'),
                    'HL': self.safe_float_convert(immob_vars['durability'].get(), 'durability', 'immobilization'),
                    'PC': self.safe_float_convert(immob_vars['power_consumption'].get(), 'power_consumption', 'immobilization')
                }
                if None in immob_data.values():
                    return
                # Проверка диапазонов
                if immob_data['PH_Min'] > immob_data['PH_Max']:
                    messagebox.showerror("Ошибка", "pH минимум не может быть больше pH максимума")
                    return
                if immob_data['T_Min'] > immob_data['T_Max']:
                    messagebox.showerror("Ошибка", "Температура минимум не может быть больше температуры максимума")
                    return
                if self.db_manager.insert_immobilization_layer(immob_data):
                    self.logger.info(f"Иммобилизационный слой {immob_data['IM_ID']} успешно сохранен")

            # Сохранение мемристивного слоя
            mem_vars = self.sections['memristive'].get_vars()
            if mem_vars['mem_id'].get():
                mem_data = {
                    'MEM_ID': mem_vars['mem_id'].get(),
                    'MEM_Name': mem_vars['mem_name'].get(),
                    'PH_Min': self.safe_float_convert(mem_vars['ph_min'].get(), 'ph_min', 'memristive'),
                    'PH_Max': self.safe_float_convert(mem_vars['ph_max'].get(), 'ph_max', 'memristive'),
                    'T_Min': self.safe_float_convert(mem_vars['t_min'].get(), 't_min', 'memristive'),
                    'T_Max': self.safe_float_convert(mem_vars['t_max'].get(), 't_max', 'memristive'),
                    'MP': self.safe_float_convert(mem_vars['young_modulus'].get(), 'young_modulus', 'memristive'),
                    'SN': self.safe_float_convert(mem_vars['sensitivity'].get(), 'sensitivity', 'memristive'),
                    'DR_Min': self.safe_float_convert(mem_vars['dr_min'].get(), 'dr_min', 'memristive'),
                    'DR_Max': self.safe_float_convert(mem_vars['dr_max'].get(), 'dr_max', 'memristive'),
                    'RP': self.safe_float_convert(mem_vars['reproducibility'].get(), 'reproducibility', 'memristive'),
                    'TR': self.safe_float_convert(mem_vars['response_time'].get(), 'response_time', 'memristive'),
                    'ST': self.safe_float_convert(mem_vars['stability'].get(), 'stability', 'memristive'),
                    'LOD': self.safe_float_convert(mem_vars['lod'].get(), 'lod', 'memristive'),
                    'HL': self.safe_float_convert(mem_vars['durability'].get(), 'durability', 'memristive'),
                    'PC': self.safe_float_convert(mem_vars['power_consumption'].get(), 'power_consumption', 'memristive')
                }
                if None in mem_data.values():
                    return
                # Проверка диапазонов
                if mem_data['PH_Min'] > mem_data['PH_Max']:
                    messagebox.showerror("Ошибка", "pH минимум не может быть больше pH максимума")
                    return
                if mem_data['T_Min'] > mem_data['T_Max']:
                    messagebox.showerror("Ошибка", "Температура минимум не может быть больше температуры максимума")
                    return
                if mem_data['DR_Min'] > mem_data['DR_Max']:
                    messagebox.showerror("Ошибка", "Диапазон измерений: минимум не может быть больше максимума")
                    return
                if self.db_manager.insert_memristive_layer(mem_data):
                    self.logger.info(f"Мемристивный слой {mem_data['MEM_ID']} успешно сохранен")

            messagebox.showinfo("Успех", "Паспорт успешно сохранен!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения: {str(e)}\nПроверьте данные.")
            self.logger.error(f"Ошибка сохранения: {e}")
            
    def save_sensor_combinations_to_db(self):
        
        return 0

    def safe_float_convert(self, value_str: str, field_name: str, section: str) -> float:
        """Преобразование строки в float с валидацией."""
        if not value_str or value_str.strip() == "":
            messagebox.showerror("Неверный ввод", f"Пустое значение для {field_name}")
            return None
        try:
            value = float(value_str.strip())
            constraints = self.field_constraints.get(section, {}).get(field_name, {})
            if constraints:
                if not (constraints['min'] <= value <= constraints['max']):
                    raise ValueError(f"Значение вне диапазона: {constraints['min']}-{constraints['max']}")
            return value
        except ValueError as e:
            messagebox.showerror("Неверный ввод", f"Ошибка в {field_name}: {str(e)}")
            self.logger.error(f"Ошибка преобразования числа для {field_name}: {e}")
            return None

    def clear_form(self):
        """Очистка всех форм ввода."""
        for section in self.sections.values():
            for var in section.get_vars().values():
                var.set("")
        messagebox.showinfo("Очистка", "Форма очищена!")

    def save_passport(self):
        """Сохранение паспорта в JSON-файл."""
        data = {name: {k: v.get() for k, v in section.get_vars().items()} for name, section in self.sections.items()}
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Сохранение", f"Паспорт сохранен в {filename}")
            self.logger.info(f"Паспорт сохранен в {filename}")

    def load_passport(self):
        """Загрузка паспорта из JSON-файла."""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                for section_name, section_data in data.items():
                    if section_name in self.sections:
                        for k, v in section_data.items():
                            if k in self.sections[section_name].get_vars():
                                self.sections[section_name].get_vars()[k].set(v)
                messagebox.showinfo("Загрузка", "Паспорт загружен!")
                self.logger.info(f"Паспорт загружен из {filename}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка загрузки: {str(e)}")
                self.logger.error(f"Ошибка загрузки: {e}")

    def load_passport_from_db(self):
        """Загрузка паспорта из базы данных для выбранного типа данных."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Выбор паспорта")
        dialog.geometry("300x200")
        
        # Выбор типа данных
        tk.Label(dialog, text="Выберите тип данных:").pack(pady=10)
        data_type_var = tk.StringVar(value="analyte")
        data_types = [
            ("Аналит (TA)", "analyte"),
            ("Биораспознающий слой (BRE)", "bio_recognition"),
            ("Иммобилизационный слой (IM)", "immobilization"),
            ("Мемристивный слой (MEM)", "memristive")
        ]
        combobox = ttk.Combobox(dialog, textvariable=data_type_var, 
                               values=[dt[1] for dt in data_types], state="readonly")
        combobox.pack(pady=5)
        
        # Ввод ID
        tk.Label(dialog, text="Введите ID:").pack(pady=10)
        id_var = tk.StringVar()
        tk.Entry(dialog, textvariable=id_var, width=20).pack(pady=5)
        
        def load_selected():
            data_type = data_type_var.get()
            layer_id = id_var.get()
            if not layer_id:
                messagebox.showerror("Ошибка", "Введите ID!")
                return

            # Очистка формы перед загрузкой
            self.clear_form()

            # Загрузка данных в зависимости от типа
            if data_type == "analyte":
                data = self.db_manager.get_analyte_by_id(layer_id)
                if data:
                    vars_dict = self.sections['analyte'].get_vars()
                    vars_dict['ta_id'].set(data['TA_ID'])
                    vars_dict['ta_name'].set(data['TA_Name'] or '')
                    vars_dict['ph_min'].set(str(data['PH_Min']) if data['PH_Min'] is not None else '')
                    vars_dict['ph_max'].set(str(data['PH_Max']) if data['PH_Max'] is not None else '')
                    vars_dict['t_max'].set(str(data['T_Max']) if data['T_Max'] is not None else '')
                    vars_dict['stability'].set(str(data['ST']) if data['ST'] is not None else '')
                    vars_dict['half_life'].set(str(data['HL']) if data['HL'] is not None else '')
                    vars_dict['power_consumption'].set(str(data['PC']) if data['PC'] is not None else '')
                    messagebox.showinfo("Загрузка", "Паспорт аналита загружен из базы данных!")
                else:
                    messagebox.showerror("Ошибка", "Аналит не найден!")
            elif data_type == "bio_recognition":
                data = self.db_manager.get_bio_recognition_layer_by_id(layer_id)
                if data:
                    vars_dict = self.sections['bio_recognition'].get_vars()
                    vars_dict['bre_id'].set(data['BRE_ID'])
                    vars_dict['bre_name'].set(data['BRE_Name'] or '')
                    vars_dict['ph_min'].set(str(data['PH_Min']) if data['PH_Min'] is not None else '')
                    vars_dict['ph_max'].set(str(data['PH_Max']) if data['PH_Max'] is not None else '')
                    vars_dict['t_min'].set(str(data['T_Min']) if data['T_Min'] is not None else '')
                    vars_dict['t_max'].set(str(data['T_Max']) if data['T_Max'] is not None else '')
                    vars_dict['dr_min'].set(str(data['DR_Min']) if data['DR_Min'] is not None else '')
                    vars_dict['dr_max'].set(str(data['DR_Max']) if data['DR_Max'] is not None else '')
                    vars_dict['sensitivity'].set(str(data['SN']) if data['SN'] is not None else '')
                    vars_dict['reproducibility'].set(str(data['RP']) if data['RP'] is not None else '')
                    vars_dict['response_time'].set(str(data['TR']) if data['TR'] is not None else '')
                    vars_dict['stability'].set(str(data['ST']) if data['ST'] is not None else '')
                    vars_dict['lod'].set(str(data['LOD']) if data['LOD'] is not None else '')
                    vars_dict['durability'].set(str(data['HL']) if data['HL'] is not None else '')
                    vars_dict['power_consumption'].set(str(data['PC']) if data['PC'] is not None else '')
                    messagebox.showinfo("Загрузка", "Паспорт биослоя загружен из базы данных!")
                else:
                    messagebox.showerror("Ошибка", "Биослой не найден!")
            elif data_type == "immobilization":
                data = self.db_manager.get_immobilization_layer_by_id(layer_id)
                if data:
                    vars_dict = self.sections['immobilization'].get_vars()
                    vars_dict['im_id'].set(data['IM_ID'])
                    vars_dict['im_name'].set(data['IM_Name'] or '')
                    vars_dict['ph_min'].set(str(data['PH_Min']) if data['PH_Min'] is not None else '')
                    vars_dict['ph_max'].set(str(data['PH_Max']) if data['PH_Max'] is not None else '')
                    vars_dict['t_min'].set(str(data['T_Min']) if data['T_Min'] is not None else '')
                    vars_dict['t_max'].set(str(data['T_Max']) if data['T_Max'] is not None else '')
                    vars_dict['young_modulus'].set(str(data['MP']) if data['MP'] is not None else '')
                    vars_dict['adhesion'].set(str(data['Adh']) if data['Adh'] is not None else '')
                    vars_dict['solubility'].set(str(data['Sol']) if data['Sol'] is not None else '')
                    vars_dict['loss_coefficient'].set(str(data['K_IM']) if data['K_IM'] is not None else '')
                    vars_dict['reproducibility'].set(str(data['RP']) if data['RP'] is not None else '')
                    vars_dict['response_time'].set(str(data['TR']) if data['TR'] is not None else '')
                    vars_dict['stability'].set(str(data['ST']) if data['ST'] is not None else '')
                    vars_dict['durability'].set(str(data['HL']) if data['HL'] is not None else '')
                    vars_dict['power_consumption'].set(str(data['PC']) if data['PC'] is not None else '')
                    messagebox.showinfo("Загрузка", "Паспорт иммобилизационного слоя загружен из базы данных!")
                else:
                    messagebox.showerror("Ошибка", "Иммобилизационный слой не найден!")
            elif data_type == "memristive":
                data = self.db_manager.get_memristive_layer_by_id(layer_id)
                if data:
                    vars_dict = self.sections['memristive'].get_vars()
                    vars_dict['mem_id'].set(data['MEM_ID'])
                    vars_dict['mem_name'].set(data['MEM_Name'] or '')
                    vars_dict['ph_min'].set(str(data['PH_Min']) if data['PH_Min'] is not None else '')
                    vars_dict['ph_max'].set(str(data['PH_Max']) if data['PH_Max'] is not None else '')
                    vars_dict['t_min'].set(str(data['T_Min']) if data['T_Min'] is not None else '')
                    vars_dict['t_max'].set(str(data['T_Max']) if data['T_Max'] is not None else '')
                    vars_dict['dr_min'].set(str(data['DR_Min']) if data['DR_Min'] is not None else '')
                    vars_dict['dr_max'].set(str(data['DR_Max']) if data['DR_Max'] is not None else '')
                    vars_dict['young_modulus'].set(str(data['MP']) if data['MP'] is not None else '')
                    vars_dict['sensitivity'].set(str(data['SN']) if data['SN'] is not None else '')
                    vars_dict['reproducibility'].set(str(data['RP']) if data['RP'] is not None else '')
                    vars_dict['response_time'].set(str(data['TR']) if data['TR'] is not None else '')
                    vars_dict['stability'].set(str(data['ST']) if data['ST'] is not None else '')
                    vars_dict['lod'].set(str(data['LOD']) if data['LOD'] is not None else '')
                    vars_dict['durability'].set(str(data['HL']) if data['HL'] is not None else '')
                    vars_dict['power_consumption'].set(str(data['PC']) if data['PC'] is not None else '')
                    messagebox.showinfo("Загрузка", "Паспорт мемристивного слоя загружен из базы данных!")
                else:
                    messagebox.showerror("Ошибка", "Мемристивный слой не найден!")
            dialog.destroy()

        tk.Button(dialog, text="Загрузить", command=load_selected).pack(pady=10)

    def show_analytes(self):
        """Отображение аналитов с пагинацией."""
        self.current_data_type = 'analytes'
        self.current_page = 0  # Сброс на первую страницу
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = ("TA_ID", "Название", "pH_Min", "pH_Max", "T_Max", "Стабильность")
        self.tree["show"] = "headings"
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        offset = self.current_page * self.page_size
        analytes = self.db_manager.list_all_analytes_paginated(self.page_size, offset)
        for analyte in analytes:
            self.tree.insert("", "end", values=(
                analyte.get('TA_ID', ''),
                analyte.get('TA_Name', ''),
                analyte.get('PH_Min', ''),
                analyte.get('PH_Max', ''),
                analyte.get('T_Max', ''),
                analyte.get('ST', '')
            ))
        self.update_pagination_buttons()

    def show_bio_layers(self):
        """Отображение биораспознающих слоев с пагинацией."""
        self.current_data_type = 'bio_layers'
        self.current_page = 0  # Сброс на первую страницу
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = ("BRE_ID", "Название", "pH_Min", "pH_Max", "T_Min", "T_Max", "Чувствительность")
        self.tree["show"] = "headings"
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        offset = self.current_page * self.page_size
        bio_layers = self.db_manager.list_all_bio_recognition_layers_paginated(self.page_size, offset)
        for layer in bio_layers:
            self.tree.insert("", "end", values=(
                layer.get('BRE_ID', ''),
                layer.get('BRE_Name', ''),
                layer.get('PH_Min', ''),
                layer.get('PH_Max', ''),
                layer.get('T_Min', ''),
                layer.get('T_Max', ''),
                layer.get('SN', '')
            ))
        self.update_pagination_buttons()

    def show_immobilization_layers(self):
        """Отображение иммобилизационных слоев с пагинацией."""
        self.current_data_type = 'immobilization_layers'
        self.current_page = 0  # Сброс на первую страницу
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = ("IM_ID", "Название", "pH_Min", "pH_Max", "T_Min", "T_Max", "MP")
        self.tree["show"] = "headings"
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        offset = self.current_page * self.page_size
        im_layers = self.db_manager.list_all_immobilization_layers_paginated(self.page_size, offset)
        for layer in im_layers:
            self.tree.insert("", "end", values=(
                layer.get('IM_ID', ''),
                layer.get('IM_Name', ''),
                layer.get('PH_Min', ''),
                layer.get('PH_Max', ''),
                layer.get('T_Min', ''),
                layer.get('T_Max', ''),
                layer.get('MP', '')
            ))
        self.update_pagination_buttons()

    def show_memristive_layers(self):
        """Отображение мемристивных слоев с пагинацией."""
        self.current_data_type = 'memristive_layers'
        self.current_page = 0  # Сброс на первую страницу
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = ("MEM_ID", "Название", "pH_Min", "pH_Max", "T_Min", "T_Max", "Чувствительность")
        self.tree["show"] = "headings"
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        offset = self.current_page * self.page_size
        mem_layers = self.db_manager.list_all_memristive_layers_paginated(self.page_size, offset)
        for layer in mem_layers:
            self.tree.insert("", "end", values=(
                layer.get('MEM_ID', ''),
                layer.get('MEM_Name', ''),
                layer.get('PH_Min', ''),
                layer.get('PH_Max', ''),
                layer.get('T_Min', ''),
                layer.get('T_Max', ''),
                layer.get('SN', '')
            ))
        self.update_pagination_buttons()
    
    """    
    def show_sensor_combination(self):
        Отображение комбинаций сенсоров с пагинацией.
        self.current_data_type = 'sensor_combinations'
        self.current_page = 0  # Сброс на первую страницу
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = ("Combo_ID", "TA_ID", "BRE_ID", "IM_ID", "MEM_ID", "Score")
        self.tree["show"] = "headings"
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        offset = self.current_page * self.page_size
        sensor_combinations = self.db_manager.list_all_sensor_combinations(self.page_size, offset)
        for layer in sensor_combinations:
            self.tree.insert("", "end", values=(
                layer.get('Combo_ID', ''),
                layer.get('TA_ID', ''),
                layer.get('BRE_ID', ''),
                layer.get('IM_ID', ''),
                layer.get('MEM_ID', ''),
                layer.get('Score', '')
            ))
        self.update_pagination_buttons()
    """

    def refresh_data(self):
        """Обновление данных в зависимости от текущего типа."""
        if self.current_data_type == 'analytes':
            self.show_analytes()
        elif self.current_data_type == 'bio_layers':
            self.show_bio_layers()
        elif self.current_data_type == 'immobilization_layers':
            self.show_immobilization_layers()
        elif self.current_data_type == 'memristive_layers':
            self.show_memristive_layers()

    def update_pagination_buttons(self):
        """Обновление кнопок пагинации."""
        if hasattr(self, 'pagination_frame'):
            self.pagination_frame.destroy()
        self.pagination_frame = tk.Frame(self.db_frame)
        self.pagination_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Button(self.pagination_frame, text="◀ Предыдущая", command=self.prev_page,
                  state='normal' if self.current_page > 0 else 'disabled').pack(side='left', padx=5)
        
        # Показать текущую страницу
        page_label = tk.Label(self.pagination_frame, text=f"Страница {self.current_page + 1}")
        page_label.pack(side='left', padx=10)
        
        tk.Button(self.pagination_frame, text="Следующая ▶", command=self.next_page).pack(side='left', padx=5)

    def prev_page(self):
        """Переход на предыдущую страницу."""
        if self.current_page > 0:
            self.current_page -= 1
            self.refresh_data()

    def next_page(self):
        """Переход на следующую страницу."""
        self.current_page += 1
        self.refresh_data()
        
    def computing_combinations(self):
        """рассчет и сохранение комбинаций сенсоров"""
        analytes = self.db_manager.list_all_analytes()
        bio_layers = self.db_manager.list_all_bio_recognition_layers()
        im_layers = self.db_manager.list_all_immobilization_layers()
        mem_layers = self.db_manager.list_all_memristive_layers()
        
        

    def show_best_combinations(self):
        """Отображение комбинаций сенсоров с пагинацией."""
        self.current_data_type = 'sensor_combinations'
        self.current_page = 0  # Сброс на первую страницу
        # рассчет и сохранение комбинаций
        
        # self.tree.delete(*self.tree.get_children())
        # self.tree["columns"] = ("Combo_ID", "TA_ID", "BRE_ID", "IM_ID", "MEM_ID", "Score")
        # self.tree["show"] = "headings"
        # for col in self.tree["columns"]:
        #    self.tree.heading(col, text=col)
        #    self.tree.column(col, width=120)
        offset = self.current_page * self.page_size
        sensor_combinations = self.db_manager.list_all_sensor_combinations_paginated(self.page_size, offset)
        self.update_pagination_buttons()
        """Отображение лучших комбинаций сенсоров."""
        self.analysis_text.delete(1.0, tk.END)
        self.analysis_text.insert(tk.END, "=== ЛУЧШИЕ КОМБИНАЦИИ БИОСЕНСОРОВ ===\n\n")
        for layer in sensor_combinations:
            self.analysis_text.insert(tk.END, list(
                layer.get('Combo_ID', ''),
                layer.get('TA_ID', ''),
                layer.get('BRE_ID', ''),
                layer.get('IM_ID', ''),
                layer.get('MEM_ID', ''),
                layer.get('Score', '')
            ))
        """self.analysis_text.insert(tk.END, "Функция в разработке...\n")"""
        
    def comparative_analysis(self):
        """Выполнение сравнительного анализа."""
        self.analysis_text.delete(1.0, tk.END)
        self.analysis_text.insert(tk.END, "=== СРАВНИТЕЛЬНЫЙ АНАЛИЗ ===\n\n")
        self.analysis_text.insert(tk.END, "Функция в разработке...\n")

    def show_statistics(self):
        """Отображение статистики базы данных."""
        self.analysis_text.delete(1.0, tk.END)
        self.analysis_text.insert(tk.END, "=== СТАТИСТИКА БАЗЫ ДАННЫХ ===\n\n")
        try:
            cursor = self.db_manager.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Analytes")
            analytes_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM BioRecognitionLayers")
            bio_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM ImmobilizationLayers")
            immob_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM MemristiveLayers")
            mem_count = cursor.fetchone()[0]
            stats = f"""Количество записей в базе данных:
            
📋 Аналиты: {analytes_count}
🔴 Слои биораспознавания: {bio_count}
🟡 Слои иммобилизации: {immob_count}
🟣 Мемристивные слои: {mem_count}
"""
            self.analysis_text.insert(tk.END, stats)
        except Exception as e:
            self.analysis_text.insert(tk.END, f"Ошибка получения статистики: {str(e)}")

    def export_data(self):
        """Экспорт данных в файл."""
        messagebox.showinfo("Экспорт", "Функция в разработке")

    def about(self):
        """Отображение информации о программе."""
        messagebox.showinfo("О программе", "Паспорта мемристивных биосенсоров v2.0\n\n© 2025")

    def run(self):
        """Запуск приложения."""
        self.root.mainloop()
        self.db_manager.close()

if __name__ == "__main__":
    app = BiosensorGUI()
    app.run()