from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure Gemini API
genai.configure(api_key='AIzaSyDREpWFaN2NVS-ICbsOUny3T8dovMf-99Q')
model = genai.GenerativeModel('gemini-2.0-flash')

def extract_article_content(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
            
        # Get text content
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Extract main image
        image_url = None
        # Try to find the main image
        main_image = soup.find('meta', property='og:image')
        if main_image:
            image_url = main_image.get('content')
        else:
            # Try to find the first large image
            images = soup.find_all('img')
            for img in images:
                if img.get('src') and ('jpg' in img.get('src') or 'jpeg' in img.get('src') or 'png' in img.get('src')):
                    image_url = img.get('src')
                    if not image_url.startswith('http'):
                        # Handle relative URLs
                        if image_url.startswith('//'):
                            image_url = 'https:' + image_url
                        else:
                            image_url = url + image_url
                    break
        
        return text, image_url
    except Exception as e:
        return str(e), None

def analyze_news(article_text):
    prompt = f"""
    Etik kurallarına uyarken aşağıdaki bilgileri kullanın:
    Etik Kurallar:
   - Kişisel verileri koru
   - Nefret söylemi ve ayrımcılık içeren içerikleri reddet
   - Telif haklarına saygı göster
   - Gizlilik ve mahremiyeti koru
   
    Lütfen aşağıdaki haber metnini analiz edin ve şu bilgileri verin:
    1. Haberin kısa bir özeti (100 kelime)
    2. Haberin doğruluk oranı (0-100 arası)
    3. Doğruluk değerlendirmesinin nedenleri
    4. Haberin güvenilirliği hakkında genel bir değerlendirme

    Haber metni:
    {article_text}
    """
    
    response = model.generate_content(prompt)
    return response.text

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    url = request.json.get('url')
    if not url:
        return jsonify({'error': 'URL gerekli'}), 400
    
    try:
        article_text, image_url = extract_article_content(url)
        analysis = analyze_news(article_text)
        return jsonify({
            'analysis': analysis,
            'imageUrl': image_url
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 