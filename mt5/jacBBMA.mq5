//+------------------------------------------------------------------+
//|                                                      jacBBMA.mq5  |
//|   BBMA Oma Ally — Re-Entry robot (jac)  —  v2 (yumshatilgan)      |
//|                                                                  |
//|   ⚠️ FAQAT DEMO. Martingale/averaging — SL yo'q. Xato bo'lsa zarar.|
//|   v2: chart TF'da trend + MA5 teginish -> kiradi.                 |
//|       Multi-TF tasdiq IXTIYORIY (sozlama bilan yoqiladi).         |
//+------------------------------------------------------------------+
#property copyright "jac"
#property version   "2.00"
#property description "BBMA re-entry (MA5 touch), grid scaling, +1% TP / -3% emergency. DEMO!"

#include <Trade/Trade.mqh>
CTrade trade;

//================= SOZLAMALAR =================
input group "--- Asosiy ---"
input ENUM_TIMEFRAMES InpEntryTF = PERIOD_CURRENT; // Kirish TF (grafik TF)
input int    InpBBPeriod = 20;     // Bollinger Band davri
input double InpBBDev    = 2.0;    // Bollinger Band og'ish

input group "--- Multi-TF tasdiq (ixtiyoriy) ---"
input bool   InpUseMidTF = false;  // O'rta TF tasdiqini yoqish
input ENUM_TIMEFRAMES InpMidTF = PERIOD_H1;  // O'rta TF
input bool   InpUseBigTF = false;  // Katta TF tasdiqini yoqish
input ENUM_TIMEFRAMES InpBigTF = PERIOD_H4;  // Katta TF

input group "--- Pul boshqaruvi ---"
input double InpLotPer10k    = 0.1;  // Lot har $10,000 ga
input double InpTargetPct    = 1.0;  // Setup maqsadi: +%
input double InpEmergencyPct = 3.0;  // Favqulodda to'xtash: -%
input int    InpMaxTrades    = 30;   // Setupdagi max bitim
input int    InpMaxSetups    = 3;    // Kuniga max kirish
input int    InpGridStepPts  = 200;  // Grid qadami (punkt)

input group "--- Chiqish ---"
input bool   InpUseM1BBExit     = true;  // M1 BB qarshi chizig'i (foydada)
input bool   InpUseOppositeExit = true;  // Qarshi kuchli sham bo'lsa

input group "--- Boshqa ---"
input long   InpMagic = 20240621;
input bool   InpDebug = true;          // Journalga xabar yozish

//================= GLOBAL =================
ENUM_TIMEFRAMES TFe, TFm, TFb;
int hBBe, hMA5He, hMA5Le, hMA10He, hMA10Le;   // entry TF
int hBBm, hBBb;                                // mid/big TF (bias uchun)
int hBBm1;                                     // M1 chiqish uchun

int    g_setupsToday=0, g_today=-1;
bool   g_blockedToday=false, g_noMoreAdds=false;
double g_lastAddPrice=0, g_basketBalance=0;

//+------------------------------------------------------------------+
int OnInit()
{
   trade.SetExpertMagicNumber(InpMagic);
   TFe = (InpEntryTF==PERIOD_CURRENT)?(ENUM_TIMEFRAMES)Period():InpEntryTF;
   TFm = InpMidTF; TFb = InpBigTF;

   hBBe   = iBands(_Symbol,TFe,InpBBPeriod,0,InpBBDev,PRICE_CLOSE);
   hMA5He = iMA(_Symbol,TFe,5,0,MODE_LWMA,PRICE_HIGH);
   hMA5Le = iMA(_Symbol,TFe,5,0,MODE_LWMA,PRICE_LOW);
   hMA10He= iMA(_Symbol,TFe,10,0,MODE_LWMA,PRICE_HIGH);
   hMA10Le= iMA(_Symbol,TFe,10,0,MODE_LWMA,PRICE_LOW);
   hBBm   = iBands(_Symbol,TFm,InpBBPeriod,0,InpBBDev,PRICE_CLOSE);
   hBBb   = iBands(_Symbol,TFb,InpBBPeriod,0,InpBBDev,PRICE_CLOSE);
   hBBm1  = iBands(_Symbol,PERIOD_M1,InpBBPeriod,0,InpBBDev,PRICE_CLOSE);

   if(hBBe==INVALID_HANDLE||hMA5He==INVALID_HANDLE||hMA5Le==INVALID_HANDLE||
      hMA10He==INVALID_HANDLE||hMA10Le==INVALID_HANDLE||hBBm==INVALID_HANDLE||hBBb==INVALID_HANDLE)
   { Print("Xato: indikator handle"); return INIT_FAILED; }

   Print("jacBBMA v2 ishga tushdi. ⚠️ DEMO! EntryTF=",EnumToString(TFe),
         " MidTF=",(InpUseMidTF?EnumToString(TFm):"off"),
         " BigTF=",(InpUseBigTF?EnumToString(TFb):"off"));
   return INIT_SUCCEEDED;
}
void OnDeinit(const int reason)
{
   IndicatorRelease(hBBe); IndicatorRelease(hMA5He); IndicatorRelease(hMA5Le);
   IndicatorRelease(hMA10He); IndicatorRelease(hMA10Le);
   IndicatorRelease(hBBm); IndicatorRelease(hBBb); IndicatorRelease(hBBm1);
}

//================= YORDAMCHILAR =================
double V(int h,int buf,int sh){ double a[]; if(CopyBuffer(h,buf,sh,1,a)<1) return EMPTY_VALUE; return a[0]; }

// trend bias: close[1] mid BB ustida=+1, ostida=-1
int Bias(int hBB,ENUM_TIMEFRAMES tf)
{
   double mid=V(hBB,0,1); if(mid==EMPTY_VALUE) return 0;
   double c=iClose(_Symbol,tf,1);
   if(c>mid) return +1; if(c<mid) return -1; return 0;
}
// kuchli sham (entry TF): tana MA10 yoki BB ni kessa
int StrongCandle()
{
   double o=iOpen(_Symbol,TFe,1),c=iClose(_Symbol,TFe,1);
   double t=V(hBBe,1,1),l=V(hBBe,2,1),m10h=V(hMA10He,0,1),m10l=V(hMA10Le,0,1);
   if(t==EMPTY_VALUE) return 0;
   if(c>o && (c>m10h||c>t)) return +1;
   if(c<o && (c<m10l||c<l)) return -1;
   return 0;
}

int CountPos(){ int n=0; for(int i=PositionsTotal()-1;i>=0;i--){ ulong tk=PositionGetTicket(i);
   if(PositionSelectByTicket(tk)&&PositionGetInteger(POSITION_MAGIC)==InpMagic&&PositionGetString(POSITION_SYMBOL)==_Symbol)n++;} return n; }
double BasketProfit(){ double p=0; for(int i=PositionsTotal()-1;i>=0;i--){ ulong tk=PositionGetTicket(i);
   if(PositionSelectByTicket(tk)&&PositionGetInteger(POSITION_MAGIC)==InpMagic&&PositionGetString(POSITION_SYMBOL)==_Symbol)
      p+=PositionGetDouble(POSITION_PROFIT)+PositionGetDouble(POSITION_SWAP);} return p; }
int BasketDir(){ for(int i=PositionsTotal()-1;i>=0;i--){ ulong tk=PositionGetTicket(i);
   if(PositionSelectByTicket(tk)&&PositionGetInteger(POSITION_MAGIC)==InpMagic&&PositionGetString(POSITION_SYMBOL)==_Symbol)
      return (PositionGetInteger(POSITION_TYPE)==POSITION_TYPE_BUY)?+1:-1;} return 0; }
void CloseAll(string why){ for(int i=PositionsTotal()-1;i>=0;i--){ ulong tk=PositionGetTicket(i);
   if(PositionSelectByTicket(tk)&&PositionGetInteger(POSITION_MAGIC)==InpMagic&&PositionGetString(POSITION_SYMBOL)==_Symbol)
      trade.PositionClose(tk);} if(InpDebug)Print("Savat yopildi: ",why); }
double AutoLot(){ double bal=AccountInfoDouble(ACCOUNT_BALANCE); double lot=(bal/10000.0)*InpLotPer10k;
   double mn=SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_MIN),mx=SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_MAX),st=SymbolInfoDouble(_Symbol,SYMBOL_VOLUME_STEP);
   if(st>0) lot=MathFloor(lot/st)*st; if(lot<mn)lot=mn; if(lot>mx)lot=mx; return lot; }
void OpenPos(int dir){ double lot=AutoLot();
   if(dir>0) trade.Buy(lot,_Symbol,0,0,0,"jacBBMA"); else trade.Sell(lot,_Symbol,0,0,0,"jacBBMA");
   g_lastAddPrice=(dir>0)?SymbolInfoDouble(_Symbol,SYMBOL_ASK):SymbolInfoDouble(_Symbol,SYMBOL_BID); }

bool IsNewBar(){ static datetime last=0; datetime t=iTime(_Symbol,TFe,0); if(t!=last){last=t;return true;} return false; }

// armed yo'nalish: chart TF bias (+ ixtiyoriy multi-TF tasdiq)
int ArmedDir()
{
   int b=Bias(hBBe,TFe); if(b==0) return 0;
   if(InpUseMidTF && Bias(hBBm,TFm)!=b) return 0;
   if(InpUseBigTF && Bias(hBBb,TFb)!=b) return 0;
   return b;
}

//================= ASOSIY =================
void OnTick()
{
   if(BarsCalculated(hBBe)<InpBBPeriod+5) return;
   MqlDateTime dt; TimeToStruct(TimeCurrent(),dt);
   if(dt.day!=g_today){ g_today=dt.day; g_setupsToday=0; g_blockedToday=false; }

   int pos=CountPos();

   //---------- SAVAT BOSHQARISH ----------
   if(pos>0)
   {
      int dir=BasketDir(); double profit=BasketProfit();
      double target=g_basketBalance*InpTargetPct/100.0;
      double emerg=-g_basketBalance*InpEmergencyPct/100.0;

      if(profit>=target){ CloseAll(StringFormat("TP +%.1f%%",InpTargetPct)); return; }
      if(profit<=emerg){ CloseAll(StringFormat("EMERGENCY -%.1f%%",InpEmergencyPct)); g_blockedToday=true; return; }

      if(InpUseM1BBExit && profit>0){
         double bid=SymbolInfoDouble(_Symbol,SYMBOL_BID),ask=SymbolInfoDouble(_Symbol,SYMBOL_ASK);
         double m1t=V(hBBm1,1,0),m1l=V(hBBm1,2,0);
         if(m1t!=EMPTY_VALUE){
            if(dir>0 && bid>=m1t){ CloseAll("M1 top BB"); return; }
            if(dir<0 && ask<=m1l){ CloseAll("M1 low BB"); return; } }
      }
      if(IsNewBar()){
         int sc=StrongCandle();
         if(dir>0 && (sc<0 || iClose(_Symbol,TFe,1)<V(hMA10Le,0,1))) g_noMoreAdds=true;
         if(dir<0 && (sc>0 || iClose(_Symbol,TFe,1)>V(hMA10He,0,1))) g_noMoreAdds=true;
         if(InpUseOppositeExit){
            if(dir>0 && sc<0){ CloseAll("Qarshi CSM/CSK"); return; }
            if(dir<0 && sc>0){ CloseAll("Qarshi CSM/CSK"); return; } }
      }
      if(!g_noMoreAdds && pos<InpMaxTrades){
         double pt=SymbolInfoDouble(_Symbol,SYMBOL_POINT);
         double bid=SymbolInfoDouble(_Symbol,SYMBOL_BID),ask=SymbolInfoDouble(_Symbol,SYMBOL_ASK);
         if(dir>0 && bid<=g_lastAddPrice-InpGridStepPts*pt){ OpenPos(+1); if(InpDebug)Print("Grid qo'shildi BUY, jami=",pos+1); }
         if(dir<0 && ask>=g_lastAddPrice+InpGridStepPts*pt){ OpenPos(-1); if(InpDebug)Print("Grid qo'shildi SELL, jami=",pos+1); }
      }
      return;
   }

   //---------- YANGI KIRISH ----------
   if(IsNewBar()) g_noMoreAdds=false;
   if(g_blockedToday || g_setupsToday>=InpMaxSetups) return;

   int dir=ArmedDir(); if(dir==0) return;
   double bid=SymbolInfoDouble(_Symbol,SYMBOL_BID),ask=SymbolInfoDouble(_Symbol,SYMBOL_ASK);
   double m5l=V(hMA5Le,0,0),m5h=V(hMA5He,0,0);
   bool entered=false;
   if(dir>0 && m5l!=EMPTY_VALUE && bid<=m5l){ OpenPos(+1); entered=true; }   // pullback MA5 Low -> BUY
   if(dir<0 && m5h!=EMPTY_VALUE && ask>=m5h){ OpenPos(-1); entered=true; }   // pullback MA5 High -> SELL
   if(entered){
      g_basketBalance=AccountInfoDouble(ACCOUNT_BALANCE);
      g_setupsToday++;
      if(InpDebug)Print("KIRISH #",g_setupsToday," ",(dir>0?"BUY":"SELL")," @MA5");
   }
}
//+------------------------------------------------------------------+
