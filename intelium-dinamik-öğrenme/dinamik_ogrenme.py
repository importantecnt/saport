import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from flask import Flask, render_template, request
import os

# Global değişkenler
VERI_DOSYASI = 'veri/veri.xlsx'
TEST_VERI_DOSYASI = 'veri/model_test_verileri.xlsx'
model_accuracy = None  # Doğruluk oranı için global değişken

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

def verileri_yukle(dosya_yolu):
    """Excel dosyasından verileri yükle."""
    if os.path.exists(dosya_yolu):
        df = pd.read_excel(dosya_yolu)
        return df['Description'].tolist(), df['Values'].astype(int).tolist()  # Sadece Description ve Values döndür
    return [], []

def modeli_tasarla(X, y):
    """Modeli oluştur ve eğit."""
    global model, vectorizer, model_accuracy
    # Sadece açıklamayı kullan
    X_vect = vectorizer.fit_transform(X)  # Metinleri vektörleştir

    # Random Forest modelini oluştur
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_vect, y)  # Modeli eğit

    # Test verilerini yükle ve doğruluk oranını hesapla
    X_test_descriptions, y_test = verileri_yukle(TEST_VERI_DOSYASI)
    if X_test_descriptions and y_test:
        X_test_vect = vectorizer.transform(X_test_descriptions)
        predictions = model.predict(X_test_vect)
        model_accuracy = accuracy_score(y_test, predictions) * 100
        print(f"Model test doğruluğu: {model_accuracy:.2f}%")
    else:
        print("Test verisi yüklenemedi veya eksik.")

def metne_gore_tahmin_yap(description):
    """Verilen açıklamaya göre etiket tahmini yap."""
    combined_vect = vectorizer.transform([description])  # Metni vektörleştir
    prediction = model.predict(combined_vect)  # Tahmin yap
    return prediction[0]

@app.route('/', methods=['GET'])
def form():
    return render_template('form.html', accuracy=model_accuracy)  # Doğruluk oranını gönder

@app.route('/predict', methods=['POST'])
def predict():
    description = request.form['description']

    # Mevcut verileri yükle ve modeli oluştur
    X_descriptions, y = verileri_yukle(VERI_DOSYASI)

    if X_descriptions and y:  # Eğer veri varsa
        # Tahmin yap
        tahmin = metne_gore_tahmin_yap(description)

        # Tahmin edilen etiket
        tahmin_edilen_etiket = label_name[tahmin]

        return render_template('form.html', prediction=tahmin_edilen_etiket, accuracy=model_accuracy)
    else:
        return "Excel dosyasında yeterli veri bulunamadı.", 400

if __name__ == '__main__':
    # Mevcut verileri yükle ve modeli oluştur
    X_descriptions, y = verileri_yukle(VERI_DOSYASI)

    if X_descriptions and y:  # Eğer veri varsa
        modeli_tasarla(X_descriptions, y)
    else:
        print("Excel dosyasında yeterli veri bulunamadı.")

app.run(debug=True)
