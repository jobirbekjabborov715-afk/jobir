//+------------------------------------------------------------------+
//|                                                      jacBBMA.mq5  |
//|   BBMA Oma Ally — Multi-Timeframe Re-Entry robot (jac)            |
//|                                                                  |
//|   ⚠️ FAQAT DEMO HISOBDA SINANG. Bu martingale/averaging usuli —   |
//|      SL yo'q, ko'p bitim. Xato bo'lsa katta zarar mumkin.         |
//|      v1: birinchi versiya — demo'da test qilib birga sozlaymiz.   |
//+------------------------------------------------------------------+
#property copyright "jac"
#property version   "1.00"
#property description "BBMA multi-TF re-entry, grid scaling, +1% TP / -3% emergency. DEMO only!"

#include <Trade/Trade.mqh>
CTrade trade;

//================= SOZLAMALAR =================
input group "--- Timeframe triplet (katta/o'rta/kichik) ---"
input ENUM_TIMEFRAMES InpBigTF   = PERIOD_H4;   // Katta TF (asosiy = Re-Entry)
input ENUM_TIMEFRAMES InpMidTF   = PERIOD_H1;   // O'rta TF (Re-entry/Extreme)
input ENUM_TIMEFRAMES InpSmallTF = PERIOD_M15;  // Kichik TF (Extreme/MHV) — kirish shu yerda

input group "--- Indikator sozlamalari (BBMA standart) ---"
input int    InpBBPeriod = 20;     // Bollinger Band davri
input double InpBBDev    = 2.0;    // Bollinger Band og'ish (deviation)

input group "--- Pul boshqaruvi ---"
input double InpLotPer10k   = 0.1;   // Lot har $10,000 ga (avto-moslashadi)
input double InpTargetPct   = 1.0;   // Setup maqsadi: +% (savat yopiladi)
input double InpEmergencyPct= 3.0;   // Favqulodda to'xtash: -% (prop himoyasi)
input int    InpMaxTrades   = 30;    // Bitta setupdagi maksimal bitim
input int    InpMaxSetups   = 3;     // Kuniga maksimal kirish (setup)
input int    InpGridStepPts = 200;   // Grid qadami (punkt) — qarshi ketganda qo'shish

input group "--- Chiqish usullari ---"
input bool   InpUseM1BBExit   = true;  // M1 BB qarshi chizig'iga tegsa (foydada) chiqish
input bool   InpUseOppositeExit = true;// Qarshi kuchli sham (CSM/CSK) bo'lsa chiqish

input group "--- Boshqa ---"
input long   InpMagic = 20240621;      // Magic raqami

//================= GLOBAL =================
ENUM_TIMEFRAMES TF[3];
int hBB[3], hEMA[3], hMA5H[3], hMA5L[3], hMA10H[3], hMA10L[3];
int hBBm1 = INVALID_HANDLE;

int      g_armedDir   = 0;       // tayyor yo'nalish (+1 buy / -1 sell / 0)
bool     g_noMoreAdds = false;   // grid qo'shish to'xtatilgan
double   g_lastAddPrice = 0;     // oxirgi qo'shilgan bitim narxi
int      g_setupsToday = 0;
int      g_today = -1;
bool     g_blockedToday = false; // favqulodda to'xtashdan keyin kun bloklanadi
double   g_basketBalance = 0;    // setup boshlangandagi balans

//+------------------------------------------------------------------+
int OnInit()
{
   trade.SetExpertMagicNumber(InpMagic);
   TF[0]=InpBigTF; TF[1]=InpMidTF; TF[2]=InpSmallTF;
   for(int i=0;i<3;i++)
   {
      hBB[i]   = iBands(_Symbol, TF[i], InpBBPeriod, 0, InpBBDev, PRICE_CLOSE);
      hEMA[i]  = iMA(_Symbol, TF[i], 50, 0, MODE_EMA,  PRICE_CLOSE);
      hMA5H[i] = iMA(_Symbol, TF[i], 5,  0, MODE_LWMA, PRICE_HIGH);
      hMA5L[i] = iMA(_Symbol, TF[i], 5,  0, MODE_LWMA, PRICE_LOW);
      hMA10H[i]= iMA(_Symbol, TF[i], 10, 0, MODE_LWMA, PRICE_HIGH);
      hMA10L[i]= iMA(_Symbol, TF[i], 10, 0, MODE_LWMA, PRICE_LOW);
      if(hBB[i]==INVALID_HANDLE||hEMA[i]==INVALID_HANDLE||hMA5H[i]==INVALID_HANDLE||
         hMA5L[i]==INVALID_HANDLE||hMA10H[i]==INVALID_HANDLE||hMA10L[i]==INVALID_HANDLE)
      { Print("Xato: indikator handle yaratilmadi (TF index ",i,")"); return INIT_FAILED; }
   }
   hBBm1 = iBands(_Symbol, PERIOD_M1, InpBBPeriod, 0, InpBBDev, PRICE_CLOSE);
   Print("jacBBMA ishga tushdi. ⚠️ FAQAT DEMO! Triplet: ",
         EnumToString(TF[0])," / ",EnumToString(TF[1])," / ",EnumToString(TF[2]));
   return INIT_SUCCEEDED;
}

void OnDeinit(const int reason)
{
   for(int i=0;i<3;i++){
      IndicatorRelease(hBB[i]); IndicatorRelease(hEMA[i]);
      IndicatorRelease(hMA5H[i]); IndicatorRelease(hMA5L[i]);
      IndicatorRelease(hMA10H[i]); IndicatorRelease(hMA10L[i]);
   }
   if(hBBm1!=INVALID_HANDLE) IndicatorRelease(hBBm1);
}

//================= INDIKATOR O'QISH =================
double V(int handle,int buf,int shift)
{
   double a[]; if(CopyBuffer(handle,buf,shift,1,a)<1) return EMPTY_VALUE;
   return a[0];
}
double BBtop(int i,int s){ return V(hBB[i],1,s); }
double BBlow(int i,int s){ return V(hBB[i],2,s); }
double BBmid(int i,int s){ return V(hBB[i],0,s); }
double MA5H(int i,int s){ return V(hMA5H[i],0,s); }
double MA5L(int i,int s){ return V(hMA5L[i],0,s); }
double MA10H(int i,int s){ return V(hMA10H[i],0,s); }
double MA10L(int i,int s){ return V(hMA10L[i],0,s); }
double C(int i,int s){ return iClose(_Symbol,TF[i],s); }
double O(int i,int s){ return iOpen(_Symbol,TF[i],s); }
double Hi(int i,int s){ return iHigh(_Symbol,TF[i],s); }
double Lo(int i,int s){ return iLow(_Symbol,TF[i],s); }

//================= BBMA ELEMENT ANIQLASH =================
// Extreme: MA5 BB tashqarisida.  +1 = buy (MA5L<lowBB), -1 = sell (MA5H>topBB)
int Extreme(int i,int s=1)
{
   double t=BBtop(i,s),l=BBlow(i,s),m5h=MA5H(i,s),m5l=MA5L(i,s);
   if(t==EMPTY_VALUE||l==EMPTY_VALUE) return 0;
   if(m5l<l) return +1;
   if(m5h>t) return -1;
   return 0;
}
// MHV: extreme'dan keyin shamcha (tana+soya) to'liq BB ichida
int MHV(int i)
{
   int exDir=0;
   for(int s=1;s<=6;s++){ int e=Extreme(i,s); if(e!=0){exDir=e;break;} }
   if(exDir==0) return 0;
   double t1=BBtop(i,1),l1=BBlow(i,1);
   if(t1==EMPTY_VALUE) return 0;
   if(Hi(i,1)<=t1 && Lo(i,1)>=l1) return exDir;  // soya ham chiqmagan
   return 0;
}
// Re-entry: trend (mid BB) + narx MA5/10 ga qaytadi, MA dan tashqariga yopilmaydi
int ReEntry(int i)
{
   double c1=C(i,1),mid=BBmid(i,1);
   if(mid==EMPTY_VALUE) return 0;
   double m5l=MA5L(i,1),m10l=MA10L(i,1),m5h=MA5H(i,1),m10h=MA10H(i,1);
   if(c1>mid && Lo(i,1)<=m5l && c1>m10l) return +1; // uptrend, pastga MA5L ga qaytdi
   if(c1<mid && Hi(i,1)>=m5h && c1<m10h) return -1; // downtrend, yuqoriga MA5H ga qaytdi
   return 0;
}
// Kuchli tanali sham: tana MA5/10 ni YOKI BB ni kessa
int StrongCandle(int i)
{
   double o1=O(i,1),c1=C(i,1),t1=BBtop(i,1),l1=BBlow(i,1),m10h=MA10H(i,1),m10l=MA10L(i,1);
   if(t1==EMPTY_VALUE) return 0;
   if(c1>o1 && (c1>m10h || c1>t1)) return +1;
   if(c1<o1 && (c1<m10l || c1<l1)) return -1;
   return 0;
}

// Multi-TF moslik: katta=ReEntry, o'rta=ReEntry|Extreme, kichik=Extreme|MHV — bir yo'nalish
int SetupDirection()
{
   int d0=ReEntry(0);                 if(d0==0) return 0;        // katta TF re-entry shart
   int d1=ReEntry(1); if(d1==0) d1=Extreme(1);
   int d2=Extreme(2); if(d2==0) d2=MHV(2);
   if(d1==d0 && d2==d0) return d0;
   return 0;
}

//================= POZITSIYA YORDAMCHILARI =================
int CountPos()
{
   int n=0;
   for(int i=PositionsTotal()-1;i>=0;i--){ ulong tk=PositionGetTicket(i);
      if(PositionSelectByTicket(tk) && PositionGetInteger(POSITION_MAGIC)==InpMagic
         && PositionGetString(POSITION_SYMBOL)==_Symbol) n++; }
   return n;
}
double BasketProfit()
{
   double p=0;
   for(int i=PositionsTotal()-1;i>=0;i--){ ulong tk=PositionGetTicket(i);
      if(PositionSelectByTicket(tk) && PositionGetInteger(POSITION_MAGIC)==InpMagic
         && PositionGetString(POSITION_SYMBOL)==_Symbol)
         p += PositionGetDouble(POSITION_PROFIT)+PositionGetDouble(POSITION_SWAP); }
   return p;
}
int BasketDir()  // +1 buy, -1 sell, 0 yo'q
{
   for(int i=PositionsTotal()-1;i>=0;i--){ ulong tk=PositionGetTicket(i);
      if(PositionSelectByTicket(tk) && PositionGetInteger(POSITION_MAGIC)==InpMagic
         && PositionGetString(POSITION_SYMBOL)==_Symbol)
         return (PositionGetInteger(POSITION_TYPE)==POSITION_TYPE_BUY)?+1:-1; }
   return 0;
}
void CloseAll(string why)
{
   for(int i=PositionsTotal()-1;i>=0;i--){ ulong tk=PositionGetTicket(i);
      if(PositionSelectByTicket(tk) && PositionGetInteger(POSITION_MAGIC)==InpMagic
         && PositionGetString(POSITION_SYMBOL)==_Symbol)
         trade.PositionClose(tk); }
   Print("Savat yopildi: ",why);
}
double AutoLot()
{
   double bal=AccountInfoDouble(ACCOUNT_BALANCE);
   double lot=(bal/10000.0)*InpLotPer10k;
   double mn=SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_MIN);
   double mx=SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_MAX);
   double st=SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_STEP);
   if(st>0) lot=MathFloor(lot/st)*st;
   if(lot<mn) lot=mn; if(lot>mx) lot=mx;
   return lot;
}
void OpenPos(int dir)
{
   double lot=AutoLot();
   if(dir>0) trade.Buy(lot,_Symbol,0,0,0,"jacBBMA");
   else      trade.Sell(lot,_Symbol,0,0,0,"jacBBMA");
   g_lastAddPrice = (dir>0)?SymbolInfoDouble(_Symbol,SYMBOL_ASK):SymbolInfoDouble(_Symbol,SYMBOL_BID);
}

//================= ASOSIY =================
bool IsNewSmallBar()
{
   static datetime last=0; datetime t=iTime(_Symbol,TF[2],0);
   if(t!=last){ last=t; return true; }
   return false;
}

void OnTick()
{
   // tayyorlik
   if(BarsCalculated(hBB[2])<InpBBPeriod+5) return;

   // kunlik nollash
   MqlDateTime dt; TimeToStruct(TimeCurrent(),dt);
   if(dt.day!=g_today){ g_today=dt.day; g_setupsToday=0; g_blockedToday=false; }

   int pos=CountPos();

   //---------- 1) SAVATNI BOSHQARISH (pozitsiya bor) ----------
   if(pos>0)
   {
      int dir=BasketDir();
      double profit=BasketProfit();
      double target =  g_basketBalance*InpTargetPct/100.0;
      double emerg  = -g_basketBalance*InpEmergencyPct/100.0;

      // (1) +1% maqsad
      if(profit>=target){ CloseAll("TP +"+DoubleToString(InpTargetPct,1)+"%"); return; }
      // (2) -3% favqulodda
      if(profit<=emerg){ CloseAll("Emergency -"+DoubleToString(InpEmergencyPct,1)+"%"); g_blockedToday=true; return; }

      // (3) M1 BB qarshi chizig'i (faqat foydada)
      if(InpUseM1BBExit && profit>0)
      {
         double bid=SymbolInfoDouble(_Symbol,SYMBOL_BID), ask=SymbolInfoDouble(_Symbol,SYMBOL_ASK);
         double m1t=V(hBBm1,1,0), m1l=V(hBBm1,2,0);
         if(m1t!=EMPTY_VALUE){
            if(dir>0 && bid>=m1t){ CloseAll("M1 top BB (foydada)"); return; }
            if(dir<0 && ask<=m1l){ CloseAll("M1 low BB (foydada)"); return; }
         }
      }

      // yangi shamchada: grid to'xtatish + qarshi chiqish
      if(IsNewSmallBar())
      {
         int sc=StrongCandle(2);
         // grid to'xtash: kuchli sham MA10 ni qarshi tomonga buzsa
         if(dir>0 && (sc<0 || C(2,1)<MA10L(2,1))) g_noMoreAdds=true;
         if(dir<0 && (sc>0 || C(2,1)>MA10H(2,1))) g_noMoreAdds=true;
         // (4) qarshi kuchli sham (CSM/CSK) -> chiqish
         if(InpUseOppositeExit){
            if(dir>0 && sc<0){ CloseAll("Qarshi CSM/CSK"); return; }
            if(dir<0 && sc>0){ CloseAll("Qarshi CSM/CSK"); return; }
         }
      }

      // (scaling) qarshi ketganda grid bitim qo'shish
      if(!g_noMoreAdds && pos<InpMaxTrades)
      {
         double pt=SymbolInfoDouble(_Symbol,SYMBOL_POINT);
         double bid=SymbolInfoDouble(_Symbol,SYMBOL_BID), ask=SymbolInfoDouble(_Symbol,SYMBOL_ASK);
         if(dir>0 && bid <= g_lastAddPrice - InpGridStepPts*pt) OpenPos(+1); // narx tushdi -> buy qo'sh
         if(dir<0 && ask >= g_lastAddPrice + InpGridStepPts*pt) OpenPos(-1); // narx ko'tarildi -> sell qo'sh
      }
      return;
   }

   //---------- 2) YANGI KIRISH IZLASH (pozitsiya yo'q) ----------
   if(IsNewSmallBar())
   {
      g_noMoreAdds=false;
      if(!g_blockedToday && g_setupsToday<InpMaxSetups)
         g_armedDir = SetupDirection();   // triplet mosligi
      else
         g_armedDir = 0;
   }

   if(g_armedDir!=0 && !g_blockedToday && g_setupsToday<InpMaxSetups)
   {
      double bid=SymbolInfoDouble(_Symbol,SYMBOL_BID), ask=SymbolInfoDouble(_Symbol,SYMBOL_ASK);
      double m5l=MA5L(2,0), m5h=MA5H(2,0);   // kichik TF MA5 (hozirgi)
      bool entered=false;
      if(g_armedDir>0 && m5l!=EMPTY_VALUE && bid<=m5l){ OpenPos(+1); entered=true; } // MA5 ga teginish
      if(g_armedDir<0 && m5h!=EMPTY_VALUE && ask>=m5h){ OpenPos(-1); entered=true; }
      if(entered){
         g_basketBalance=AccountInfoDouble(ACCOUNT_BALANCE);
         g_setupsToday++;
         g_armedDir=0;
         Print("Yangi kirish #",g_setupsToday," yo'nalish=",(BasketDir()>0?"BUY":"SELL"));
      }
   }
}
//+------------------------------------------------------------------+
