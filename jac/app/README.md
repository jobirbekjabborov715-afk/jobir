# jac — 3D robot (real-time, WebGL)

Bu haqiqiy 3D robot: aylanadi, harakatlanadi, ko'zlari yonib rang o'zgartiradi.
Brauzerda ko'rish uchun kichik lokal server kerak (ES modullar `file://` da ishlamaydi).

## Ishga tushirish (eng oson yo'l)

Shu papkada terminal ochib, quyidagilardan birini bajaring:

**Python bo'lsa:**
```
python -m http.server 8000
```
keyin brauzerda oching: http://localhost:8000

**Node bo'lsa:**
```
npx serve .
```

Yoki VS Code'da "Live Server" kengaytmasi bilan `index.html` ni oching.

## Boshqarish
- Sichqoncha bilan ushlab **aylantiring** (haqiqiy 3D).
- Pastdagi tugmalar: holatni o'zgartiring (Salom / Tayyor / O'ylayapman / Xato / Avto).
- Ko'zlar holatga qarab rang o'zgartiradi: 🔵 Salom · 🟢 Tayyor · 🟡 O'ylayapti · 🔴 Xato.

Texnologiya: Three.js (vendored — internetsiz ham ishlaydi).
