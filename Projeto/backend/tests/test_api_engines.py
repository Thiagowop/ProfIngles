#!/usr/bin/env python3
"""
Test TTS engines endpoint
"""
import requests
import json

try:
    # Test the endpoint directly
    response = requests.get('http://localhost:8000/tts/engines')
    if response.status_code == 200:
        data = response.json()
        print('=== TTS ENGINES ENDPOINT RESPONSE ===')
        print(f'Status: {response.status_code}')
        print(f'Current engine: {data.get("current_engine", "N/A")}')
        print(f'Available engines count: {len(data.get("available_engines", {}))}')
        print('')
        print('=== ENGINES LIST ===')
        for name, info in data.get('available_engines', {}).items():
            print(f'{name}: {info.get("name", "Unknown")}')
    else:
        print(f'Error: {response.status_code} - {response.text}')
except Exception as e:
    print(f'Connection error: {e}')
    print('Make sure the backend server is running on localhost:8000')
