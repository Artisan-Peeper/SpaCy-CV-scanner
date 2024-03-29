from flask import Flask, request, render_template
import spacy

# Load the English language model in SpaCy
nlp = spacy.load("en_core_web_sm")

app = Flask(__name__)

def process_resume(file):
    # Initialize an empty list to store extracted entities
    entities = []

    # Process the resume file in chunks
    chunk_size = 1024  # Set the chunk size to process
    while True:
        chunk = file.read(chunk_size)
        if not chunk:
            break
        # Process the text chunk using SpaCy
        doc = nlp(chunk.decode('utf-8', errors='ignore'))  # Decode the chunk using 'utf-8' encoding
        # Extract named entities from the chunk
        entities.extend([ent.text for ent in doc.ents])

    return entities

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if file is in the request
        if 'resume' not in request.files:
            return render_template('index.html', error='No file part')

        resume_file = request.files['resume']
        # Check if filename is empty
        if resume_file.filename == '':
            return render_template('index.html', error='No selected file')

        # Process the resume file
        resume_entities = process_resume(resume_file)

        # Render the result template with extracted entities
        return render_template('result.html', entities=resume_entities)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
    