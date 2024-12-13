import mariadb
import pandas as pd
import random
import joblib
from sklearn.feature_extraction.text import CountVectorizer
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import nltk
import string
from dotenv import load_dotenv
import os

load_dotenv()

nltk.download('stopwords')
nltk.download('punkt')

model = joblib.load("modèle_sentiment.pkl")
print("Modèle chargé avec succès.")

cv = joblib.load("count_vectorizer.pkl")
print("Vectorizer chargé avec succès.")

db_host = os.getenv("DB_HOST")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")

connection = mariadb.connect(
    host=db_host,
    user=db_user,
    password=db_password,
    database=db_name
)

query = """
SELECT review_text FROM comments
WHERE review_text IS NOT NULL
ORDER BY RAND()
LIMIT 5
"""

cursor = connection.cursor()
cursor.execute(query)
rows = cursor.fetchall()
connection.close()

if not rows:
    print("Aucun commentaire trouvé dans la base de données.")
    exit()

data = pd.DataFrame(rows, columns=['review_text'])

ps = PorterStemmer()
stop_words = stopwords.words('english')
puncts = string.punctuation

def preprocess_text(text):
    text = text.lower()
    tokens = nltk.word_tokenize(text)
    filtered_tokens = [ps.stem(w) for w in tokens if w not in stop_words and w not in puncts]
    return ' '.join(filtered_tokens)

data['processed_text'] = data['review_text'].apply(preprocess_text)

X = cv.transform(data['processed_text']).toarray()

predictions = model.predict(X)

print("\nRésultats de l'analyse des sentiments:\n")
for i, row in data.iterrows():
    sentiment = "Positive" if predictions[i] == 1 else "Negative"
    print(f"Commentaire : {row['review_text']}")
    print(f"Sentiment prédit : {sentiment}\n")