from flask import Flask, request, render_template, redirect, url_for
import pandas as pd
import os

app = Flask(__name__)

# Veri dosyası
VERI_DOSYASI = 'veri/veri.xlsx'  # Veri dosyasının yolu

@app.route('/')
def index():
    return render_template('veri.html')  # 'veri.html' şablonunu döndür

@app.route('/yükle', methods=['POST'])
def yükle():
    başlık = request.form['Title']  # Başlık verisini al
    açıklama = request.form['Description']  # Açıklama verisini al
    değerler = request.form['Values']  # Değerleri al

    # Eğer dosya yoksa başlık, açıklama ve değer ile yeni DataFrame oluştur
    if not os.path.exists(VERI_DOSYASI):
        df = pd.DataFrame(columns=['Title', 'Description', 'Values'])
    else:
        df = pd.read_excel(VERI_DOSYASI)

    # Yeni satırı oluştur
    yeni_satir = pd.DataFrame({'Title': [başlık], 'Description': [açıklama], 'Values': [değerler]})

    # Eski DataFrame ile yeni satırı birleştir
    df = pd.concat([df, yeni_satir], ignore_index=True)

    # Dosyayı kaydet
    df.to_excel(VERI_DOSYASI, index=False)

    return redirect(url_for('index'))  # Ana sayfaya geri dön

if __name__ == '__main__':
    app.run(debug=True)
