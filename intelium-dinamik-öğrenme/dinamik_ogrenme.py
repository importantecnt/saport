import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from flask import Flask, render_template, request
import os
from sklearn.ensemble import RandomForestClassifier

# Global değişkenler
VERI_DOSYASI = 'veri/veri.xlsx'

# Eğer dosya yoksa, boş bir DataFrame oluştur ve kaydet
if not os.path.exists(VERI_DOSYASI):
    df = pd.DataFrame(columns=['Title', 'Description', 'Values'])
    df.to_excel(VERI_DOSYASI, index=False)

# Etiketler
label_name = {
    0: "Report a BUG",
    1: "Suggest a new feature",
    2: "Suggest improvement",
    3: "Technical support"
}

# Flask uygulaması oluştur
app = Flask(__name__)

# Model ve vektörleştirici
model = None
vectorizer = CountVectorizer()

def verileri_yukle():
    """Excel dosyasından verileri yükle."""
    if os.path.exists(VERI_DOSYASI):
        df = pd.read_excel(VERI_DOSYASI)
        return df['Title'].tolist(), df['Description'].tolist(), df['Values'].astype(int).tolist()
    return [], [], []

def modeli_tasarla(X, y):
    """Modeli oluştur ve eğit."""
    global model, vectorizer
    # Başlık ve açıklamayı birleştir
    X_combined = ["{} {}".format(title, description) for title, description in zip(*X)]
    X_vect = vectorizer.fit_transform(X_combined)  # Metinleri vektörleştir

    # Random Forest modelini oluştur
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_vect, y)  # Modeli eğit

def yeni_veri_ekle(title, description):
    """Yeni bir veri ekle ve modeli güncelle."""
    # Mevcut verileri yükle
    X_titles, X_descriptions, y = verileri_yukle()

    # Yeni veriyi ekle
    X_titles.append(title)
    X_descriptions.append(description)
    y.append(len(y) % len(label_name))  # Varsayılan değer ile ekle

    df = pd.DataFrame({'Title': X_titles, 'Description': X_descriptions, 'Values': y})
    df.to_excel(VERI_DOSYASI, index=False)  # Verileri Excel dosyasına yaz

    # Modeli yeniden oluştur
    modeli_tasarla((X_titles, X_descriptions), y)

def metne_gore_tahmin_yap(title, description):
    """Verilen başlık ve açıklamaya göre etiket tahmini yap."""
    combined_input = "{} {}".format(title, description)  # Başlık ve açıklamayı birleştir
    combined_vect = vectorizer.transform([combined_input])  # Metni vektörleştir
    prediction = model.predict(combined_vect)  # Tahmin yap
    return prediction[0]

@app.route('/', methods=['GET'])
def form():
    return render_template('form.html')  # form.html dosyası oluşturulmalı

@app.route('/predict', methods=['POST'])
def predict():
    title = request.form['title']
    description = request.form['description']

    # Mevcut verileri yükle ve modeli oluştur
    X_titles, X_descriptions, y = verileri_yukle()

    if X_titles and X_descriptions and y:  # Eğer veri varsa
        # Yeni veriyi ekle ve modeli güncelle
        yeni_veri_ekle(title, description)

        # Tahmin yap
        tahmin = metne_gore_tahmin_yap(title, description)

        # Tahmin edilen etiket
        tahmin_edilen_etiket = label_name[tahmin]

        return render_template('form.html', prediction=tahmin_edilen_etiket)
    else:
        return "Excel dosyasında yeterli veri bulunamadı.", 400

if __name__ == '__main__':
    # Mevcut verileri yükle ve modeli oluştur
    X_titles, X_descriptions, y = verileri_yukle()

    if X_titles and X_descriptions and y:  # Eğer veri varsa
        modeli_tasarla((X_titles, X_descriptions), y)
    else:
         print("Excel dosyasında yeterli veri bulunamadı.")

app.run(debug=True)
