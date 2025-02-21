import requests
import streamlit as st

API_URL = "http://localhost:8000"

def get_brands():
    response = requests.get(f"{API_URL}/brands/")
    return response.json()

def get_brand_by_id(brand_id):
    response = requests.get(f"{API_URL}/brands/{brand_id}")
    return response.json()

def get_brand_by_name(name):
    response = requests.get(f"{API_URL}/brands/by-name/{name}")
    if response.status_code == 404:
        return None
    return response.json()

def create_brand(brand_data):
    response = requests.post(f"{API_URL}/brands/", json=brand_data)
    if response.status_code == 400:
        return False, response.json()["detail"]
    return True, response.json()

def update_brand(brand_id, brand_data):
    response = requests.put(f"{API_URL}/brands/{brand_id}", json=brand_data)
    return response.json()

def delete_brand(brand_id):
    response = requests.delete(f"{API_URL}/brands/{brand_id}")
    return response.json()

# 프로젝트, 제조사에 대한 API 함수도 비슷하게 구현