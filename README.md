# Lunera Chatbot

Lunera, hayali bir moda markasıdır. Bu projede Lunera'nın dijital asistanı geliştirildi. Kullanıcılar, ürün bilgilerini sorgulayabilir, beden ve renk filtrelemesi yapabilir, fiyatları öğrenebilir ve sipariş oluşturabilir.

## 🚀 Özellikler

-  Ürün sorgulama (kategori, renk, beden)
-  Doğal dil destekli sohbet
-  Excel tabanlı ürün verisi kullanımı (`product_list.xlsx`)
-  Stok durumu sorgulama
-  Ürün fiyatı gösterimi
-  Sipariş bilgisi alma ve onaylama
-  Desteklenmeyen konularda kibarca geri dönüş
-  CORS destekli FastAPI backend + React frontend


## 🔧 Kurulum

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm start
```

## 📌 Notlar

- `GOOGLE_API_KEY` .env dosyasında tanımlanmalıdır.
- Excel dosyasının adı `product_list.xlsx` olmalıdır ve aynı klasörde yer almalıdır.
- Yalnızca belirli ürün kategorileri, renkler ve bedenler desteklenir.