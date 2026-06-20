# jacBBMA — BBMA Oma Ally Multi-Timeframe Re-Entry robot

BBMA strategiyasini avtomatlashtirilgan ko'rinishi: ko'p-timeframe (triplet) re-entry,
grid scaling, +1% maqsad / −3% himoya.

## ⚠️ JIDDIY OGOHLANTIRISH
- Bu **martingale/averaging** usuli: **stop loss yo'q**, bitta setupда **30 tagacha** bitim.
- Trend uzoq qarshi ketsa — **katta zarar / akkaunt yonishi** mumkin.
- **−3% favqulodda to'xtash** himoya qiladi, lekin kafolat emas (gap/slippage bo'lishi mumkin).
- **FAQAT DEMO HISOBDA** uzoq sinang. Real pul — faqat o'zingiz to'liq ishonganda.
- Bu **v1** — birinchi versiya. Demo natijasiga qarab birga sozlaymiz.

## Strategiya mantiqi (spec)
**Element aniqlash (har TF):**
- **Kuchli sham (yo'nalish):** tana MA5/10 ni yoki BB ni kessa
- **Extreme:** MA5 BB tashqarisida (MA5L<lowBB=buy, MA5H>topBB=sell)
- **MHV:** extreme'dan keyin shamcha (tana+soya) to'liq BB ichida
- **Re-entry:** trend yo'nalishida narx MA5/10 ga qaytadi

**Multi-TF triplet (sozlanadi):** katta=Re-entry, o'rta=Re-entry/Extreme, kichik=Extreme/MHV — bir yo'nalishda mos kelsa kiradi.
- Standart: **H4 / H1 / M15**
- Boshqalari: D1/H4/H1 · H1/M15/M5 · M15/M5/M1

**Kirish:** kichik TF'da narx **MA5 ga teginganda** → 1-bitim.
**Scaling:** narx qarshi ketganда grid bitim qo'shiladi (teng lot), **max 30**; kuchli sham MA10 ni buzsa → to'xtaydi.
**Lot:** $10,000 ga 0.1 (avto: 0.01/$1000).
**Maqsad:** har setup **+1%** → savat yopiladi. **Kuniga max 3 setup.**
**Chiqish:** +1% / −3% / M1 BB qarshi chizig'i (foydada) / qarshi kuchli sham.

## O'rnatish
1. MT5 + **DEMO hisob** oching.
2. F4 (MetaEditor) → `jacBBMA.mq5` ni oching → **F7 (Compile)** → "0 errors".
3. MT5'da robotni **kichik TF grafikка** (masalan M15) tashlang.
4. **AutoTrading** yashil bo'lsin.
5. Avval **Strategy Tester (Ctrl+R)** da tarixda sinang!

## Asosiy sozlamalar
| Sozlama | Tavsif |
|---------|--------|
| InpBigTF / InpMidTF / InpSmallTF | Triplet TF'lari (standart H4/H1/M15) |
| InpLotPer10k | Lot har $10k ga (0.1) |
| InpTargetPct | Maqsad +% (1.0) |
| InpEmergencyPct | Favqulodda −% (3.0) |
| InpMaxTrades | Setupdagi max bitim (30) |
| InpMaxSetups | Kuniga max kirish (3) |
| InpGridStepPts | Grid qadami punktda (200) |
| InpUseM1BBExit / InpUseOppositeExit | Qo'shimcha chiqish usullari |

## v1 dagi soddalashtirishlar (birga sozlaymiz)
- Scaling qo'shish **grid qadami (punkt)** bilan amalga oshiriladi — bu MA10/MA50 masofasini taxminan ifodalaydi. Test paytida `InpGridStepPts` ni sozlaymiz.
- "Vaziyatga qarab" diskretsion qismlar aniq shartga aylantirildi.
- Re-entry/MHV aniqlash soddalashtirilgan — backtest natijasiga qarab aniqlik kiritamiz.

## Birinchi qadam: BACKTEST
Strategy Tester'da EURUSD M15, oxirgi 1-3 oy, "Every tick based on real ticks" rejimida sinang.
Natijani ko'rib — `InpGridStepPts`, TF triplet, maqsad %larni birga sozlaymiz.
