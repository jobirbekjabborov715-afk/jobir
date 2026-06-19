# jacEA — MetaTrader 5 robot (o'rganish uchun)

Oddiy **Moving Average crossover** strategiyasidagi Expert Advisor (savdo roboti).
Tez MA sekin MA'ni yuqoriga kesib o'tsa → **sotib oladi**; pastga kessa → **sotadi**.

## ⚠️ MUHIM OGOHLANTIRISH (avval o'qing!)
- Bu robot **o'rganish va tajriba** uchun. **Pul mashinasi EMAS.**
- 📉 **Ko'pchilik trader pul yo'qotadi.** Bu robot ham yo'qotishi mumkin.
- 🎮 **Faqat DEMO hisobda** (soxta pul) sinang.
- 💸 Real pulga o'tsangiz ham — **yo'qota oladigan pulingizdan** ortiq qo'ymang.
- 🚫 "Kafolatlangan foyda" yo'q. Hech kim bozorni aniq bilmaydi.

## O'rnatish (qadamba-qadam)

1. **MetaTrader 5** o'rnating (brokeringizdan yoki metatrader5.com) va **DEMO hisob** oching.
2. MT5'da: yuqori menyu → **Tools → MetaQuotes Language Editor** (yoki F4) — MetaEditor ochiladi.
3. MetaEditor'da: **File → Open** orqali `jacEA.mq5` faylini oching
   (yoki yangi EA yaratib, kodni nusxalab joylashtiring).
4. **Compile** bosing (F7). Xato bo'lmasligi kerak → "0 errors".
5. MT5'ga qayting. **Navigator → Expert Advisors** ichida `jacEA` paydo bo'ladi.
6. Istalgan grafikka (masalan EURUSD, M15) **sudrab tashlang**.
7. Yuqoridagi **AutoTrading** tugmasi **yashil** bo'lsin.

## Avval BACKTEST qiling (tarixda sinash)
1. MT5: **View → Strategy Tester** (Ctrl+R)
2. Expert: `jacEA`, Symbol va davrni tanlang
3. **Start** — robot tarixiy ma'lumotda qanday ishlashini ko'rasiz (pulsiz!)

## Sozlamalar (robotni grafikka qo'yganda chiqadi)
| Sozlama | Ma'nosi |
|---------|---------|
| Lot hajmi | Savdo hajmi — **0.01 dan boshlang** |
| Tez/Sekin MA davri | Strategiya sezgirligi |
| Stop Loss / Take Profit | Zarar/foyda chegaralari (punktda) |
| Maksimal spread | Spread katta bo'lsa savdo qilmaydi |

## Keyingi qadamlar (o'rganib borgan sari)
- Strategiyani o'zgartirish (RSI, MACD qo'shish)
- Risk boshqaruvini yaxshilash (balansga qarab lot hisoblash)
- Trailing stop qo'shish
- Bir nechta strategiyani sinash

Til: **MQL5** (C tiliga o'xshash). Har bir qadamda yordam beraman.
