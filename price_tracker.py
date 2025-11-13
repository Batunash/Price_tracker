import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import os
import sys

# Buraya ürün linki gelecek (sonradan değiştiririz)
URL = "https://www.trendyol.com/apple/iphone-13-128-gb-yildiz-isigi-cep-telefonu-apple-turkiye-garantili-p-150059024?boutiqueId=61&merchantId=107870"

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
TO_EMAIL = os.getenv("TO_EMAIL")

headers = {"User-Agent": "Mozilla/5.0"}

def send_email(subject, message):
    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = TO_EMAIL

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

    print("📨 Mail gönderildi!")

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
    t = text.replace("TL","").replace("₺","").replace(".", "").replace(",", ".").strip()
    try:
        return float(t)
    except:
        return None

def main():
    price_text = fetch_price(URL)
    if not price_text:
        print("❌ Fiyat bulunamadı!")
        if "--send-mail" in sys.argv:
            send_email("Fiyat HATASI", f"Fiyat bulunamadı!\n{URL}")
        return

    price = normalize_price(price_text)
    print(f"🔍 Fiyat: {price}")

    if "--send-mail" in sys.argv:
        send_email("Güncel Fiyat", f"Anlık fiyat: {price} TL\n\n{URL}")

if __name__ == "__main__":
    main()
