import gspread
from google.oauth2 import service_account
import os
import datetime
import json

# Debug line to check correct path
print("Working directory:", os.getcwd())

# Use absolute path for service account file in project root
SERVICE_ACCOUNT_PATH = "pestdt-e9f8a81c8a68.json"
print("Looking for service account at:", SERVICE_ACCOUNT_PATH)

# Define explicit scopes for Google Sheets
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def get_latest_sensor_data():
    try:
        # Debug current time (helps with JWT timestamp issues)
        print("Current UTC time:", datetime.datetime.utcnow())
        
        # Verify service account file exists
        if not os.path.exists(SERVICE_ACCOUNT_PATH):
            print(f"ERROR: Service account file not found at {SERVICE_ACCOUNT_PATH}")
            print("Files in current directory:", os.listdir(os.getcwd()))
            return None
            
        # Print first few characters of service account file to verify content
        with open(SERVICE_ACCOUNT_PATH, 'r') as f:
            sa_content = json.load(f)
            print(f"Service account email: {sa_content.get('client_email')}")
        
        # Create credentials with explicit scopes
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_PATH, scopes=SCOPES
        )
        
        # Connect to Google Sheets with explicit credentials
        gc = gspread.authorize(credentials)
        
        # Open specific sheet by ID - Using your provided ID
        sheet = gc.open_by_key("1fXL0wIxqeHEehuy_NoCpjVjjcvnJNnJk9xULSdZjbKo")
        
        # Get first worksheet (or use a specific name if needed)
        worksheet = sheet.sheet1  # Change to sheet.worksheet("YourSheetName") if needed
        
        # Get all records including headers
        records = worksheet.get_all_records()
        
        if not records:
            print("No records found in the sheet")
            return None
            
        # Debug: print column names
        print("Available columns:", list(records[0].keys()) if records else "No records")
        
        # Get latest row
        latest_row = records[-1]
        print("Latest row data:", latest_row)
        
        # Handle column names (adjust based on your actual sheet columns)
        # Try different variations of column names
        temp_key = next((k for k in latest_row if k.lower().strip() == "temperature"), "Temperature")
        humidity_key = next((k for k in latest_row if k.lower().strip() == "humidity"), "Humidity")
        moisture_key = next((k for k in latest_row if k.lower().strip() == "moisture"), "Moisture")
        gas_key = next((k for k in latest_row if k.lower().strip() in ["gas", "gas'"]), "Gas")
        ir_key = next((k for k in latest_row if k.lower().strip() in ["ir", "ir'"]), "IR")
        pir_key = next((k for k in latest_row if k.lower().strip() in ["pir", "pir'"]), "PIR")
        vibration_key = next((k for k in latest_row if k.lower().strip() == "vibration"), "Vibration")
        
        # Convert categorical values to numeric
        ir_value = str(latest_row.get(ir_key, "")).strip().lower()
        ir = 1 if ir_value == "detected" else 0
        
        pir_value = str(latest_row.get(pir_key, "")).strip().lower()
        pir = 1 if pir_value == "active" else 0
        
        # Prepare feature vector
        features = [
            float(latest_row.get(temp_key, 0)),
            float(latest_row.get(humidity_key, 0)),
            float(latest_row.get(moisture_key, 0)),
            float(latest_row.get(gas_key, 0)),
            ir,
            pir,
            float(latest_row.get(vibration_key, 0))
        ]
        
        print("Processed features:", features)
        return features
        
    except Exception as e:
        print(f"Error reading Google Sheet: {e}")
        import traceback
        traceback.print_exc()
        return None
