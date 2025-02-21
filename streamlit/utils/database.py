import sqlite3
import os
import pandas as pd
import streamlit as st

# 데이터베이스 파일 경로
DB_PATH = 'data/brand_manager.db'

def init_database():
    """데이터베이스 초기화 및 필요한 테이블 생성"""
    # 디렉터리가 없으면 생성
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 브랜드 테이블 생성
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS brands (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        contact_person TEXT,
        phone TEXT,
        email TEXT,
        address TEXT,
        registration_number TEXT,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 프로젝트 테이블 생성
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        brand_id INTEGER,
        name TEXT NOT NULL,
        description TEXT,
        start_date TEXT,
        end_date TEXT,
        status TEXT,
        requirements TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (brand_id) REFERENCES brands(id)
    )
    ''')
    
    # 제조사 테이블
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS manufacturers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        contact_person TEXT,
        phone TEXT,
        email TEXT,
        address TEXT,
        capacity TEXT,
        specialties TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 프로젝트-제조사 연결 테이블
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS project_manufacturers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER,
        manufacturer_id INTEGER,
        status TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (project_id) REFERENCES projects(id),
        FOREIGN KEY (manufacturer_id) REFERENCES manufacturers(id)
    )
    ''')
    
    conn.commit()
    conn.close()

@st.cache_resource
def get_connection():
    """SQLite 연결 객체 반환 (캐싱됨)"""
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def execute_query(query, params=(), fetch=False):
    """SQL 쿼리 실행"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    
    if fetch:
        result = cursor.fetchall()
        conn.commit()
        return result
    
    conn.commit()
    return None

def query_to_dataframe(query, params=()):
    """SQL 쿼리 결과를 DataFrame으로 변환"""
    conn = get_connection()
    return pd.read_sql_query(query, conn, params=params)

# 브랜드 관련 함수
def get_brand_by_name(name):
    """브랜드 이름으로 정보 조회"""
    query = "SELECT * FROM brands WHERE name = ?"
    return query_to_dataframe(query, (name,))

def add_brand(name, contact_person, phone, email, address, registration_number, description):
    """새 브랜드 추가"""
    query = """
    INSERT INTO brands (name, contact_person, phone, email, address, registration_number, description)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    try:
        execute_query(query, (name, contact_person, phone, email, address, registration_number, description))
        return True
    except sqlite3.IntegrityError:
        return False

def update_brand(brand_id, contact_person, phone, email, address, registration_number, description):
    """브랜드 정보 업데이트"""
    query = """
    UPDATE brands
    SET contact_person = ?, phone = ?, email = ?, address = ?, registration_number = ?, description = ?
    WHERE id = ?
    """
    execute_query(query, (contact_person, phone, email, address, registration_number, description, brand_id))

def delete_brand(brand_id):
    """브랜드 삭제"""
    query = "DELETE FROM brands WHERE id = ?"
    execute_query(query, (brand_id,))

# 프로젝트 관련 함수
def get_brand_projects(brand_id):
    """브랜드의 모든 프로젝트 조회"""
    query = "SELECT * FROM projects WHERE brand_id = ?"
    return query_to_dataframe(query, (brand_id,))

def add_project(brand_id, name, description, start_date, end_date, status, requirements):
    """새 프로젝트 추가"""
    query = """
    INSERT INTO projects (brand_id, name, description, start_date, end_date, status, requirements)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    execute_query(query, (brand_id, name, description, start_date, end_date, status, requirements))

def update_project(project_id, name, description, start_date, end_date, status, requirements):
    """프로젝트 정보 업데이트"""
    query = """
    UPDATE projects
    SET name = ?, description = ?, start_date = ?, end_date = ?, status = ?, requirements = ?
    WHERE id = ?
    """
    execute_query(query, (name, description, start_date, end_date, status, requirements, project_id))

def delete_project(project_id):
    """프로젝트 삭제"""
    query = "DELETE FROM projects WHERE id = ?"
    execute_query(query, (project_id,))

# 애플리케이션 시작 시 데이터베이스 초기화
init_database()