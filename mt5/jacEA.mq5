//+------------------------------------------------------------------+
//|                                                        jacEA.mq5  |
//|   Moving Average crossover Expert Advisor — O'RGANISH uchun       |
//|   ⚠️ FAQAT DEMO HISOBDA SINANG. Trading xavfli — pul yo'qotish    |
//|      mumkin. Kafolatlangan foyda YO'Q.                            |
//+------------------------------------------------------------------+
#property copyright "jac"
#property version   "1.00"
#property description "MA crossover EA — demo/o'rganish uchun. Trading xavfli."

#include <Trade/Trade.mqh>
CTrade trade;

//--- Sozlamalar (foydalanuvchi o'zgartira oladi) ---
input long           InpMagic      = 20240619; // Magic raqami (robot identifikatori)
input double         InpLots       = 0.01;     // Lot hajmi (kichikdan boshlang!)
input int            InpFastPeriod = 10;       // Tez MA davri
input int            InpSlowPeriod = 30;       // Sekin MA davri
input ENUM_MA_METHOD InpMethod     = MODE_EMA; // MA turi
input int            InpStopLoss   = 300;      // Stop Loss (punkt, 0=o'chiq)
input int            InpTakeProfit = 600;      // Take Profit (punkt, 0=o'chiq)
input int            InpMaxSpread  = 30;       // Maksimal spread (punkt)

int fastHandle = INVALID_HANDLE;
int slowHandle = INVALID_HANDLE;

//+------------------------------------------------------------------+
int OnInit()
{
   trade.SetExpertMagicNumber(InpMagic);

   fastHandle = iMA(_Symbol, _Period, InpFastPeriod, 0, InpMethod, PRICE_CLOSE);
   slowHandle = iMA(_Symbol, _Period, InpSlowPeriod, 0, InpMethod, PRICE_CLOSE);
   if(fastHandle == INVALID_HANDLE || slowHandle == INVALID_HANDLE)
   {
      Print("Xato: indikator handle yaratilmadi");
      return(INIT_FAILED);
   }
   if(InpFastPeriod >= InpSlowPeriod)
      Print("Ogohlantirish: Tez MA davri Sekin MA dan kichik bo'lishi kerak");

   Print("jacEA ishga tushdi. ⚠️ DEMO hisobda sinang!");
   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   if(fastHandle != INVALID_HANDLE) IndicatorRelease(fastHandle);
   if(slowHandle != INVALID_HANDLE) IndicatorRelease(slowHandle);
}

//--- Yangi shamcha (bar) ochilganini aniqlash ---
bool IsNewBar()
{
   static datetime lastBar = 0;
   datetime cur = iTime(_Symbol, _Period, 0);
   if(cur != lastBar) { lastBar = cur; return true; }
   return false;
}

//+------------------------------------------------------------------+
void OnTick()
{
   if(!IsNewBar()) return;                 // har shamchada bir marta tekshiramiz

   double fast[], slow[];
   ArraySetAsSeries(fast, true);
   ArraySetAsSeries(slow, true);
   if(CopyBuffer(fastHandle, 0, 0, 3, fast) < 3) return;
   if(CopyBuffer(slowHandle, 0, 0, 3, slow) < 3) return;

   // index 1 = oxirgi yopilgan shamcha, index 2 = undan oldingisi
   bool crossUp   = (fast[2] <= slow[2] && fast[1] >  slow[1]);  // tez MA yuqoriga kesib o'tdi → sotib olish
   bool crossDown = (fast[2] >= slow[2] && fast[1] <  slow[1]);  // tez MA pastga kesib o'tdi → sotish

   // spread juda katta bo'lsa — savdo qilmaymiz
   long spread = (long)SymbolInfoInteger(_Symbol, SYMBOL_SPREAD);
   if(spread > InpMaxSpread) return;

   bool hasPos  = PositionSelect(_Symbol);
   long posType = hasPos ? (long)PositionGetInteger(POSITION_TYPE) : -1;

   if(crossUp)
   {
      if(hasPos && posType == POSITION_TYPE_SELL) trade.PositionClose(_Symbol); // qarama-qarshi pozitsiyani yopamiz
      if(!(hasPos && posType == POSITION_TYPE_BUY)) OpenTrade(ORDER_TYPE_BUY);
   }
   else if(crossDown)
   {
      if(hasPos && posType == POSITION_TYPE_BUY) trade.PositionClose(_Symbol);
      if(!(hasPos && posType == POSITION_TYPE_SELL)) OpenTrade(ORDER_TYPE_SELL);
   }
}

//+------------------------------------------------------------------+
void OpenTrade(ENUM_ORDER_TYPE type)
{
   double price = (type == ORDER_TYPE_BUY) ? SymbolInfoDouble(_Symbol, SYMBOL_ASK)
                                           : SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double pt = _Point;
   double sl = 0.0, tp = 0.0;

   if(type == ORDER_TYPE_BUY)
   {
      if(InpStopLoss   > 0) sl = price - InpStopLoss   * pt;
      if(InpTakeProfit > 0) tp = price + InpTakeProfit * pt;
      sl = NormalizeDouble(sl, _Digits);
      tp = NormalizeDouble(tp, _Digits);
      trade.Buy(InpLots, _Symbol, price, sl, tp, "jacEA");
   }
   else
   {
      if(InpStopLoss   > 0) sl = price + InpStopLoss   * pt;
      if(InpTakeProfit > 0) tp = price - InpTakeProfit * pt;
      sl = NormalizeDouble(sl, _Digits);
      tp = NormalizeDouble(tp, _Digits);
      trade.Sell(InpLots, _Symbol, price, sl, tp, "jacEA");
   }
}
//+------------------------------------------------------------------+
