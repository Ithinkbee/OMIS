import tkinter as tk
from tkinter import ttk, messagebox
from model import Forecast, News, Portfolio, Quote, Recommendation, Report
from typing import List 
import random

class ChartWidget(tk.Canvas):
    def __init__(self, parent, data, width=300, height=150, color="blue"):
        super().__init__(parent, width=width, height=height, bg="white")
        self.data = data
        self.line_color = color
        self.draw()
    
    def draw(self):
        self.delete("all")
        if not self.data:
            self.create_text(int(self['width'])/2, int(self['height'])/2, text="No Data")
            return
        w, h = int(self['width']), int(self['height'])
        max_val, min_val = max(self.data), min(self.data)
        diff = max_val - min_val if max_val != min_val else 1
        
        points = []
        step = w / (len(self.data) - 1) if len(self.data) > 1 else 0
        for i, val in enumerate(self.data):
            x = i * step
            y = h - ((val - min_val) / diff * (h - 20)) - 10
            points.append(x); points.append(y)
        
        if len(points) >= 4:
            self.create_line(points, fill=self.line_color, width=2)

class BaseRepresentation:
    representation_id = None
    def _display(self, data) -> None: 
        print(f"DISPLAY: {data}")
    def _update(self, data) -> None: 
        print(f"UPDATE: {data}")

class IRepresentation(BaseRepresentation):
    def __init__(self, controller):
        self.controller = controller
        self.view_component = None

    def set_view(self, component):
        self.view_component = component

    def displayData(self, data) -> None: 
        self._display(data)
    def updateData(self, data) -> None: 
        self._update(data)

class IReportRepresentation(IRepresentation):
    def showReport(self, report: Report) -> None:
        if self.view_component:
            self.view_component.config(text=report.content)
        messagebox.showinfo(report.title, f"{report.content}\n\nMetrics: {report.metrics}")

    def exportReport(self, report: Report, format: str) -> None:
        messagebox.showinfo("Export", f"Report {report.title} exported to {format}")

class IForecastRepresentation(IRepresentation):
    def showForecasts(self, forecasts: List[Forecast]) -> None:
        msg = "\n".join([f"Target: {f.target_value:.2f}, Horizon: {f.forecast_horizon}" for f in forecasts])
        messagebox.showinfo("Forecast Results", msg)

    def displayTrends(self, data: List) -> None:
        pass

class IRecommendationRepresentation(IRepresentation):
    def displayRecommendations(self, recommendations: List[Recommendation]) -> None:
        pass

    def highlightCriticals(self, recommendations: List[Recommendation]) -> None:
        for r in recommendations:
            if r.rec_value != "hold":
                messagebox.showwarning("Recommendation Signal", f"Signal: {r.rec_value.upper()} for asset {r.asset_id}")

class IDashboardRepresentation(IRepresentation):
    def showCurrentQuotes(self, quotes: List[Quote]) -> None:
        pass
    def showNews(self, news: List[News]) -> None:
        pass

class IPortfolioRepresentation(IRepresentation):
    def showPortfolioContents(self, portfolio: Portfolio) -> None:
        pass
    def showOperationsHistory(self, operations: List) -> None:
        pass

class MainWindow(tk.Tk):
    def __init__(self, controllers, reps):
        super().__init__()
        self.ctrls = controllers
        self.reps = reps
        self.title("Financial Analysis Platform")
        self.geometry("1000x700")
        self.current_user = None
        self.show_login()

    def show_login(self):
        for w in self.winfo_children(): w.destroy()
        frame = tk.Frame(self)
        frame.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(frame, text="Login", font=("Arial", 14)).pack()
        e_user = tk.Entry(frame); e_user.pack(pady=5)
        tk.Label(frame, text="Password").pack()
        e_pass = tk.Entry(frame, show="*"); e_pass.pack(pady=5)
        
        def login():
            u = self.ctrls['auth'].login(e_user.get(), e_pass.get())
            if u:
                self.current_user = u
                self.show_main()
            else:
                messagebox.showerror("Error", "Invalid credentials")
        
        tk.Button(frame, text="Enter", command=login).pack(pady=10)
        tk.Button(frame, text="Register", command=lambda: self.ctrls['auth'].register(e_user.get(), e_pass.get(), "Investor")).pack()

    def show_main(self):
        for w in self.winfo_children(): w.destroy()
        
        self.ctrls['dash'].startMonitoring()
        
        nb = ttk.Notebook(self)
        nb.pack(fill=tk.BOTH, expand=True)
        
        self.tab_dash(nb)
        self.tab_forecast(nb)
        self.tab_report(nb)
        self.tab_auto(nb)

    def tab_dash(self, nb):
        frame = tk.Frame(nb)
        nb.add(frame, text="Dashboard")
        
        data = self.ctrls['dash'].getDashboardData()
        row = tk.Frame(frame)
        row.pack(fill=tk.X, padx=10, pady=10)
        
        for item in data:
            card = tk.Frame(row, bd=2, relief="groove", padx=5, pady=5)
            card.pack(side=tk.LEFT, padx=5)
            tk.Label(card, text=item['ticker'], font="bold").pack()
            tk.Label(card, text=f"{item['price']:.2f} ({item['change']:.2f}%)", fg="green" if item['change']>=0 else "red").pack()
            ChartWidget(card, item['history'], 100, 50).pack()

        tk.Label(frame, text="My Portfolio", font=("Arial", 12, "bold")).pack(pady=10)
        p_frame = tk.Frame(frame)
        p_frame.pack()
        
        def refresh_p():
            for w in p_frame.winfo_children(): w.destroy()
            pf = self.ctrls['port'].getPortfolio(self.current_user.user_id)
            if pf and pf.positions:
                for pos in pf.positions:
                    tk.Label(p_frame, text=f"Asset: {pos.asset_id} | Qty: {pos.quantity}").pack()
            else:
                tk.Label(p_frame, text="Empty").pack()

        refresh_p()
        
        ctrl = tk.Frame(frame)
        ctrl.pack(pady=10)
        e_asset = tk.Entry(ctrl, width=5); e_asset.pack(side=tk.LEFT)
        e_qty = tk.Entry(ctrl, width=5); e_qty.pack(side=tk.LEFT)
        
        def buy():
            from control import BuyAssetCommand
            BuyAssetCommand(self.ctrls['port'], e_asset.get(), float(e_qty.get()), self.current_user.user_id).execute()
            refresh_p()
        
        def sell():
            from control import SellAssetCommand
            SellAssetCommand(self.ctrls['port'], e_asset.get(), float(e_qty.get()), self.current_user.user_id).execute()
            refresh_p()

        tk.Button(ctrl, text="Buy", command=buy).pack(side=tk.LEFT)
        tk.Button(ctrl, text="Sell", command=sell).pack(side=tk.LEFT)

    def tab_forecast(self, nb):
        frame = tk.Frame(nb)
        nb.add(frame, text="Forecast")
        
        tk.Label(frame, text="Analysis Context").pack()
        assets = self.ctrls['forecast'].getAvailableAssets()
        cb = ttk.Combobox(frame, values=[a.ticker for a in assets])
        cb.pack()
        if assets: cb.current(0)
        
        res_lbl = tk.Label(frame, text="...")
        res_lbl.pack(pady=10)
        
        def run():
            from model import AnalysisContext
            asset_obj = next((a for a in assets if a.ticker == cb.get()), assets[0])
            ctx = AnalysisContext(self.current_user.user_id, [asset_obj.asset_id], "1M")
            
            f = self.ctrls['forecast'].createForecast(ctx)
            recs = self.ctrls['rec'].generateRecommendations(ctx)
            
            self.reps['rec'].highlightCriticals(recs)
            self.reps['forecast'].showForecasts([f])
            
            res_lbl.config(text=f"Analyzed {asset_obj.ticker}. Target: {f.target_value:.2f}")

        tk.Button(frame, text="Analyze", command=run).pack()

    def tab_report(self, nb):
        frame = tk.Frame(nb)
        nb.add(frame, text="Reports")
        
        lbl_content = tk.Label(frame, text="", justify=tk.LEFT, bg="#eee", padx=10, pady=10)
        lbl_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.reps['rep'].set_view(lbl_content)
        
        def gen():
            r = self.ctrls['rep'].generateReport("Monthly", self.current_user.user_id)
            self.reps['rep'].showReport(r)
            
        tk.Button(frame, text="Generate Report", command=gen).pack()

    def tab_auto(self, nb):
        frame = tk.Frame(nb)
        nb.add(frame, text="AutoTrading")
        
        tk.Label(frame, text="Bot Manager").pack()
        lst = tk.Listbox(frame)
        lst.pack(fill=tk.BOTH, expand=True)
        
        def refresh():
            lst.delete(0, tk.END)
            bots = self.ctrls['bot'].getUserBots(self.current_user.user_id)
            for b in bots: lst.insert(tk.END, f"{b.name} ({b.strategy})")
            
        def create():
            self.ctrls['bot'].createBot(f"Bot-{random.randint(100,999)}", "Scalping", "AAPL", 0.95, 1.05, 1000, self.current_user.user_id)
            refresh()
            
        def run_cycle():
            res = self.ctrls['bot'].run_bot_cycle(self.current_user.user_id)
            messagebox.showinfo("Bot Cycle", "\n".join(res))
            
        tk.Button(frame, text="Create Random Bot", command=create).pack()
        tk.Button(frame, text="Run Cycle", command=run_cycle).pack()
        refresh()