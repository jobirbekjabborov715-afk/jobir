//+------------------------------------------------------------------+
//|                                                    jacAutoEA.mq5  |
//|   AVTOMATIK robot — tez-tez bitimga kiradi (EMA yo'nalishi bo'yicha)|
//|   ⚠️ FAQAT DEMO. Tez savdo = tez xarajat/yo'qotish bo'lishi mumkin.|
//+------------------------------------------------------------------+
#property copyright "jac"
#property version   "1.00"
#property description "Avtomatik tez-tez kiradigan EA — demo/o'rganish. Trading xavfli."

#include <Trade/Trade.mqh>
CTrade trade;

//--- Sozlamalar ---
input long   InpMagic           = 20240620; // Magic raqami
input double InpLots            = 0.01;     // Lot hajmi (kichik!)
input int    InpEMA             = 20;       // Yo'nalish EMA davri (kichik = tez-tez)
input int    InpStopLoss        = 200;      // Stop Loss (punkt, 0=o'chiq)
input int    InpTakeProfit      = 300;      // Take Profit (punkt, 0=o'chiq)
input int    InpMaxSpread       = 30;       // Maksimal spread (punkt)
input bool   InpReverseOnFlip   = true;     // Yo'nalish o'zgarsa pozitsiyani teskari qil
input int    InpCooldownBars    = 1;        // Bitimlar orasidagi minimal shamcha
input int    InpMaxTradesPerDay = 30;       // Kunlik bitim limiti (overtrading himoyasi)

int      emaHandle   = INVALID_HANDLE;
datetime lastTradeBar = 0;
int      tradesToday = 0;
int      curDay      = -1;

//+------------------------------------------------------------------+
int OnInit()
{
   trade.SetExpertMagicNumber(InpMagic);
   emaHandle = iMA(_Symbol, _Period, InpEMA, 0, MODE_EMA, PRICE_CLOSE);
   if(emaHandle == INVALID_HANDLE)
   {
      Print("Xato: EMA handle yaratilmadi");
      return(INIT_FAILED);
   }
   Print("jacAutoEA ishga tushdi. ⚠️ DEMO hisobda sinang!");
   return(INIT_SUCCEEDED);
}

void OnDeinit(const int reason)
{
   if(emaHandle != INVALID_HANDLE) IndicatorRelease(emaHandle);
}

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
   if(!IsNewBar()) return;                 // har shamchada tekshiramiz → tez-tez imkoniyat

   // kunlik limitni nollash (yangi kun)
   MqlDateTime dt; TimeToStruct(TimeCurrent(), dt);
   if(dt.day != curDay) { curDay = dt.day; tradesToday = 0; }

   double ema[];
   ArraySetAsSeries(ema, true);
   if(CopyBuffer(emaHandle, 0, 0, 3, ema) < 3) return;

   double closePrev = iClose(_Symbol, _Period, 1);   // oxirgi yopilgan shamcha narxi
   bool bull = (closePrev > ema[1]);                 // narx EMA ustida → yuqori yo'nalish
   bool bear = (closePrev < ema[1]);                 // narx EMA ostida → quyi yo'nalish

   bool hasPos  = PositionSelect(_Symbol);
   long posType = hasPos ? (long)PositionGetInteger(POSITION_TYPE) : -1;

   // yo'nalish o'zgarsa — pozitsiyani yopamiz (keyin teskari kiradi)
   if(hasPos && InpReverseOnFlip)
   {
      if(posType == POSITION_TYPE_BUY && bear)  { trade.PositionClose(_Symbol); hasPos = false; }
      else if(posType == POSITION_TYPE_SELL && bull) { trade.PositionClose(_Symbol); hasPos = false; }
   }

   if(hasPos) return;                      // bir vaqtda bitta pozitsiya (xavfsizlik)

   // --- kirish shartlari (himoya) ---
   long spread = (long)SymbolInfoInteger(_Symbol, SYMBOL_SPREAD);
   if(spread > InpMaxSpread) return;
   if(tradesToday >= InpMaxTradesPerDay) return;
   if(lastTradeBar != 0)
   {
      int barsPassed = iBarShift(_Symbol, _Period, lastTradeBar);
      if(barsPassed < InpCooldownBars) return;
   }

   if(bull)      { if(OpenTrade(ORDER_TYPE_BUY))  RegisterTrade(); }
   else if(bear) { if(OpenTrade(ORDER_TYPE_SELL)) RegisterTrade(); }
}

void RegisterTrade()
{
   lastTradeBar = iTime(_Symbol, _Period, 0);
   tradesToday++;
}

//+------------------------------------------------------------------+
bool OpenTrade(ENUM_ORDER_TYPE type)
{
   double price = (type == ORDER_TYPE_BUY) ? SymbolInfoDouble(_Symbol, SYMBOL_ASK)
                                           : SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double pt = _Point;
   double sl = 0.0, tp = 0.0;

   if(type == ORDER_TYPE_BUY)
   {
      if(InpStopLoss   > 0) sl = NormalizeDouble(price - InpStopLoss   * pt, _Digits);
      if(InpTakeProfit > 0) tp = NormalizeDouble(price + InpTakeProfit * pt, _Digits);
      return trade.Buy(InpLots, _Symbol, price, sl, tp, "jacAutoEA");
   }
   else
   {
      if(InpStopLoss   > 0) sl = NormalizeDouble(price + InpStopLoss   * pt, _Digits);
      if(InpTakeProfit > 0) tp = NormalizeDouble(price - InpTakeProfit * pt, _Digits);
      return trade.Sell(InpLots, _Symbol, price, sl, tp, "jacAutoEA");
   }
}
//+------------------------------------------------------------------+
