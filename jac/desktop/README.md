# jac — desktop hamroh (suzuvchi 3D robot)

Noutbuk ekranida o'zi suzib yuradigan, doim ustda turadigan 3D robot.
Ishingizga xalaqit bermaydi: sichqoncha bosishlari ostidan o'tib ketadi,
faqat robot ustiga borganda uni ushlash mumkin (sudrab ko'chirasiz).

## Kerak (bir martalik)
- **Node.js** o'rnatilgan bo'lsin → https://nodejs.org (LTS versiyasi)

## Ishga tushirish
Shu (`jac/desktop`) papkada terminal ochib:
```
npm install      # bir marta — Electron yuklab oladi
npm start        # robotni ishga tushiradi
```

## Foydalanish
- Robot ekran bo'ylab **o'zi suzib yuradi** (goh suzadi, goh aylanadi, goh atrofni kuzatadi).
- Sichqonchani kuzatadi; ko'zlari rang o'zgartiradi (🔵🟢🟡🔴).
- Robot **ustiga** borib **ushlab sudrasangiz** — uni xohlagan joyga qo'yasiz.
- Boshqa joyda sichqoncha oddiy ishlayveradi (robot xalaqit bermaydi).
- **Yashirish/chiqish:** ekran burchagidagi tray (kichik ikonka) → menyu.

## Eslatma
- Hozircha robot harakatini **o'zi** boshqaradi (harakat miyyasi).
- Keyingi bosqichlarda: ovoz, ekranni ko'rish, va haqiqiy AI miyya (Claude) ulanadi —
  o'shanda robot gapiradi va maqsadli harakatlanadi.

Texnologiya: Electron + Three.js (vendored).
