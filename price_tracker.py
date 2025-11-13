import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import os
import sys
import json

URL = "https://www.trendyol.com/apple/iphone-13-128-gb-yildiz-isigi-cep-telefonu-apple-turkiye-garantili-p-150059024"

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
TO_EMAIL = os.getenv("TO_EMAIL")

headers = {"User-Agent": "Mozilla/5.0"}

PRICES_FILE = "prices.json"


# ---------------- EMAIL ----------------
def send_email(subject, message):
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD or not TO_EMAIL:
        print("❌ Mail env değişkenleri yok!")
        return

    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = TO_EMAIL

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

    print("📨 Mail gönderildi!")


# ---------------- FETCH PRICE ----------------
def fetch_price(url):
    html = requests.get(url, headers=headers).text
    soup = BeautifulSoup(html, "lxml")

    selectors = [
        ".prc-dsc",
        ".a-price-whole",
        ".price",
        ".product-price",
        "#priceblock_ourprice",
        "#priceblock_dealprice",
    ]

    for sel in selectors:
        el = soup.select_one(sel)
        if el:
            return el.text.strip()

    return None


def normalize_price(text):
    t = (text.replace("TL", "")
             .replace("₺", "")
             .replace(".", "")
             .replace(",", ".")
             .strip())
    try:
        return float(t)
    except:
        return None


# ---------------- PRICE STORAGE ----------------
def load_last_price():
    if not os.path.exists(PRICES_FILE):
        return None

    try:
        with open(PRICES_FILE, "r") as f:
            data = json.load(f)
            return data.get("last_price")
    except:
        return None


def save_last_price(price):
    with open(PRICES_FILE, "w") as f:
        json.dump({"last_price": price}, f)


# ---------------- MAIN ----------------
def main():
    price_text = fetch_price(URL)
    if not price_text:
        print("❌ Fiyat bulunamadı!")
        if "--send-mail" in sys.argv:
            send_email("Fiyat HATASI", f"Fiyat bulunamadı!\n{URL}")
        return

    price = normalize_price(price_text)

    print(f"🔍 Şu anki fiyat: {price} TL")

    last_price = load_last_price()

    # --------- Saatlik rapor maili ---------
    if "--send-mail" in sys.argv:
        send_email(
            "Saatlik Fiyat Raporu",
            f"Anlık fiyat: {price} TL\n\nURL: {URL}"
        )
        save_last_price(price)
        return

    # --------- 15 dakikalık düşüş kontrolü ---------
    if last_price is None:
        print("📁 İlk defa fiyat kaydediliyor.")
        save_last_price(price)
        return

    if price < last_price:
        print(f"🔥 Fiyat düştü! {last_price} → {price}")
        send_email(
            "⚠ Fiyat Düştü!",
            f"Fiyat düştü!\n{last_price} → {price}\n\nURL: {URL}"
        )
    else:
        print("⏳ Fiyat aynı veya daha yüksek → mail yok.")

    save_last_price(price)


if __name__ == "__main__":
    main()
