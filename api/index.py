import os
import openai
from flask import Flask, render_template, request, jsonify
from scan import scan_and_answer_file
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

api_dir = os.path.abspath(os.path.dirname(__file__))
root_dir = os.path.dirname(api_dir)

app = Flask(__name__, 
            template_folder=os.path.join(root_dir, 'public'),
            static_folder=root_dir,
            static_url_path='')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/clean', methods=['POST'])
def local_clean():
    data = request.get_json()
    text = data.get('text', '')
    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[
                {
                    'role': 'system',
                    'content': 'You clean up raw speech-to-text from a classroom lesson. Add punctuation and capitalization, split into short paragraphs, and fix obvious misheard words using context. Do not add, remove, or summarize content. Return only the cleaned text.'
                },
                {'role': 'user', 'content': text}
            ]
        )
        cleaned_text = response.choices[0].message.content
        return jsonify({'clean': cleaned_text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/scan', methods=['POST'])
def scan_text():
    data = request.get_json()
    transcript_text = data.get('text', '')
    
    if not transcript_text.strip():
        return jsonify({'results': []})
    
    try:
        results = scan_and_answer_file(transcript_text)
        return jsonify({'results': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)