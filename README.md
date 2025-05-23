# Eslatma Bot

**Eslatma Bot** — Bu Telegram bot, foydalanuvchilarga eslatmalar yaratish va ularni kerakli vaqtda eslatib turish
imkonini beradi.

## Loyihaning maqsadi

Eslatma bot foydalanuvchilarga muhim eslatmalarni yaratish va ularni kerakli vaqtlarda xabar yuborish orqali eslatib
turishni ta'minlaydi. Bu bot Telegram orqali ishlaydi va foydalanuvchilar o'z eslatmalarini bot orqali yuborishlari
mumkin.

## O'rnatish

### 1. Klonlash

Loyihani o'zingizning kompyuteringizga klonlash uchun quyidagi buyruqni ishlating:

2. Virtual muhitni yaratish va faollashtirish

Loyihada ishlash uchun virtual muhitni yaratish va uni faollashtirish kerak. Quyidagi buyruqlarni bajarish orqali
virtual muhitni yaratish mumkin:

Windows:

    python -m venv .venv
    .venv\Scripts\activate

Mac/Linux:

    python3 -m venv .venv
    source .venv/bin/activate

3. Kerakli kutubxonalarni o'rnatish

Loyihadagi barcha kerakli kutubxonalarni o'rnatish uchun quyidagi buyruqni bajarish kerak:

    pip install -r requirements.txt

4. Muhit o'zgaruvchilarini sozlash

.env faylini yaratib, unga quyidagi o'zgaruvchilarni qo'shing:

    BOT_API_TOKEN=your_telegram_bot_api_token

Loyihani ishga tushirish

Botni ishga tushurish uchun quyidagi buyruqni bajarishingiz kerak:

    python bot.py

Agar biron bir muammo yuzaga kelsa yoki savollaringiz bo'lsa, quyidagi manzillarga murojaat qiling:

    Email: yaxshioken@gmail.com

    Telegram: @Aziz_555

    GitHub Issues: https://github.com/yaxshioken/eslatma_bot/issues

```bash
git clone https://github.com/yaxshioken/eslatma_bot.git 
