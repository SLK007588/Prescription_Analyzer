from flask import Flask, render_template, request
import pandas as pd
from fuzzywuzzy import fuzz, process
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import io
import openai
import os

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

client = openai.OpenAI(api_key=OPENROUTER_API_KEY, base_url="https://openrouter.ai/api/v1")

app = Flask(__name__)

def get_medicine_info_from_gpt(medicine_name, price):
    prompt = f"""
    Provide a clean, realistic bullet-point summary for this medicine:
    Medicine: {medicine_name}
    Price per tablet: INR {price}
    Include sections:
    - DOSAGE
    - COMPOSITION
    - MAX USAGE
    - SIDE EFFECTS
    - WARNINGS & AGE RESTRICTIONS
    - PRICE: INR {price}
    """
    try:
        r = client.chat.completions.create(
            model="openai/gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=500
        )
        return r.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

@app.route('/')
def home():
    return render_template('index.html', title='Medical Prescription Analyzer')

@app.route('/disease-predict', methods=['POST'])
def disease_predict():
    file = request.files.get('file')
    if not file:
        return "No file uploaded"
    df = pd.read_csv('medicine_data.csv')
    mock_predictions = df.sample(3)['medicine_names'].tolist()
    results = []
    for med in mock_predictions:
        row = df[df['medicine_names'] == med].iloc[0]
        price = row['price']
        summary = get_medicine_info_from_gpt(med, price)
        results.append({
            "medicine_name": med,
            "price": price,
            "summary": summary
        })
    return render_template('disease-result.html', results=results)

def handler(event, context):
    return app(event, context)
