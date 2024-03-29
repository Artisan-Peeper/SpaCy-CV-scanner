from flask import Flask, render_template, request
import pdfplumber
import spacy

app = Flask(__name__)
nlp = spacy.load("en_core_web_sm")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    if 'file' not in request.files:
        return render_template('index.html', message='No file provided')

    file = request.files['file']
    if file.filename == '':
        return render_template('index.html', message='No file selected')

    keywords = request.form['keywords']
    if not keywords:
        return render_template('index.html', message='No keywords provided')

    if file:
        text = extract_text_from_pdf(file)
        if text:
            if is_resume(text):  # Check if the text resembles a resume
                doc = nlp(text)
                keywords = set([keyword.strip().lower() for keyword in keywords.split(',')])
                entities = set([ent.text for ent in doc.ents if ent.text.lower() in keywords])
                score = evaluate_resume(doc, len(entities))
                normalized_score = normalize_score(score)
                return render_template('result.html', entities=entities, score=normalized_score)
            else:
                return render_template('index.html', message='The uploaded file does not seem to be a resume.')
        else:
            return render_template('index.html', message='Unable to extract text from PDF')

def extract_text_from_pdf(file):
    with pdfplumber.open(file) as pdf:
        text = ''
        for page in pdf.pages:
            text += page.extract_text()
    return text

def is_resume(text):
    # Convert the text to lowercase for case-insensitive matching
    text = text.lower()

    # Define required keywords related to resume sections or headings
    required_keywords = ["education", "experience", "skills", "summary", "achievements"]

    # Define additional indicators commonly found in resumes
    additional_indicators = ["curriculum vitae", "work history", "professional summary", 
                             "job title", "objective", "certifications", "projects", 
                             "publications", "awards", "languages"]

    # Check for the presence of required keywords
    has_required_keywords = all(keyword in text for keyword in required_keywords)

    # Check for the presence of additional indicators
    has_additional_indicators = any(indicator in text for indicator in additional_indicators)

    # Determine if the text resembles a resume based on the presence of required keywords and additional indicators
    is_resembling_resume = has_required_keywords or has_additional_indicators

    return is_resembling_resume

def evaluate_resume(doc, num_keywords):
    num_entities = len(doc.ents)
    max_score = 100
    score = min(num_entities * 10, max_score)
    return score

def normalize_score(score):
    max_score = 100
    normalized_score = (score / max_score) * 100
    return normalized_score

if __name__ == '__main__':
    app.run(debug=True)
