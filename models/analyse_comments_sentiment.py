import mariadb
import pandas as pd
import nltk
import seaborn as sns
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from nltk.corpus import stopwords
import string
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB, MultinomialNB, BernoulliNB
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import joblib
import time
import os
from dotenv import load_dotenv

load_dotenv()

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
SELECT id,game_name,review_text,review_score FROM comments
"""
df = pd.read_sql_query(query, connection)
connection.close()

df['review_score'] = pd.to_numeric(df['review_score'], errors='coerce')
df.dropna(subset=['review_score', 'review_text'], inplace=True)

revs = df[['review_score', 'review_text']]
new_df = revs.sample(n=50000, random_state=1) if revs.shape[0] > 50000 else revs.copy()
new_df.drop_duplicates(inplace=True)
new_df.rename(columns={'review_score': 'target', 'review_text': 'text'}, inplace=True)

nltk.download('punkt')
nltk.download('stopwords')
ps = PorterStemmer()
stop_words = stopwords.words('english')
puncts = string.punctuation


def convert_text(text):
    text = text.lower()
    tokens = nltk.word_tokenize(text)
    filtered_tokens = [ps.stem(w) for w in tokens if w not in stop_words and w not in puncts]
    return ' '.join(filtered_tokens)


new_df['converted_text'] = new_df['text'].apply(convert_text)

cv = CountVectorizer(max_features=3000)
X = cv.fit_transform(new_df['converted_text']).toarray()
y = new_df['target'].values
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=34)

models = {
    "GaussianNB": GaussianNB(),
    "MultinomialNB": MultinomialNB(),
    "BernoulliNB": BernoulliNB()
}

results = []
best_model = None
best_score = 0

for model_name, model in models.items():
    start_time = time.time()
    model.fit(X_train, y_train)
    train_time = time.time() - start_time

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    precision_ = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    conf_matrix = confusion_matrix(y_test, y_pred)

    results.append({
        "model": model_name,
        "accuracy": acc,
        "precision": precision_,
        "recall": recall,
        "f1_score": f1,
        "training_time": train_time
    })

    if acc > best_score:
        best_score = acc
        best_model = model
        best_model_name = model_name

    print(f"{model_name}:")
    print(f"Accuracy: {acc:.4f}, Precision: {precision_:.4f}, Recall: {recall:.4f}, F1-Score: {f1:.4f}")
    print(f"Confusion Matrix:\n{conf_matrix}\n")

joblib.dump(best_model, "modèle_sentiment.pkl")
joblib.dump(cv, "count_vectorizer.pkl")
print(f"Meilleur modèle sauvegardé : {best_model_name}")

connection = mariadb.connect(
    host=db_host,
    user=db_user,
    password=db_password,
    database=db_name
)
cursor = connection.cursor()

insert_query = """
INSERT INTO model_stats (model_name, accuracy, precision_, recall, f1_score, training_time)
VALUES (?, ?, ?, ?, ?, ?)
"""
for result in results:
    cursor.execute(insert_query, (
        result["model"],
        result["accuracy"],
        result["precision"],
        result["recall"],
        result["f1_score"],
        result["training_time"]
    ))

connection.commit()
connection.close()

df_results = pd.DataFrame(results)
sns.barplot(x="model", y="accuracy", data=df_results)
plt.title("Performance des modèles (Accuracy)")
plt.show()

sns.barplot(x="model", y="f1_score", data=df_results)
plt.title("Performance des modèles (F1-Score)")
plt.show()

wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white')

pos_wc = wc.generate(new_df[new_df['target'] == 1]['converted_text'].str.cat(sep=" "))
plt.figure(figsize=(8, 8))
plt.imshow(pos_wc)
plt.axis("off")
plt.title("WordCloud des Reviews Positives", fontsize=16)
plt.show()

neg_wc = wc.generate(new_df[new_df['target'] == -1]['converted_text'].str.cat(sep=" "))
plt.figure(figsize=(8, 8))
plt.imshow(neg_wc)
plt.axis("off")
plt.title("WordCloud des Reviews Négatives", fontsize=16)
plt.show()