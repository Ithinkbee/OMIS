import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from model import Forecast, News, Portfolio, Quote, Recommendation, Report, AnalysisContext
from typing import List 
from control import BuyAssetCommand, SellAssetCommand

class ModernChartWidget(tk.Canvas):
    def __init__(self, parent, data, width=500, height=250, title="Price History"):
        super().__init__(parent, width=width, height=height, bg="white", highlightthickness=0)
        self.data = data
        self.title = title
        self.draw()
    
    def draw(self):
        self.delete("all")
        w, h = int(self['width']), int(self['height'])
        pad = 30
        
        self.create_text(w/2, 15, text=self.title, font=("Arial", 10, "bold"), fill="#333")
        self.create_line(pad, h-pad, w-pad, h-pad, fill="#ccc")
        self.create_line(pad, pad, pad, h-pad, fill="#ccc")
        
        if not self.data or len(self.data) < 2:
            self.create_text(w/2, h/2, text="No Data Available", fill="#999")
            return
            
        max_val, min_val = max(self.data), min(self.data)
        rng = max_val - min_val if max_val != min_val else 1
        
        points = []
        step = (w - 2*pad) / (len(self.data) - 1)
        
        for i, val in enumerate(self.data):
            x = pad + i * step
            y = (h - pad) - ((val - min_val) / rng * (h - 2*pad))
            points.append(x)
            points.append(y)
            
        color = "#2ecc71" if self.data[-1] >= self.data[0] else "#e74c3c"
        if len(points) >= 4:
            self.create_line(points, fill=color, width=2, smooth=True)
            
        self.create_text(pad-15, pad, text=f"{max_val:.1f}", font=("Arial", 8), fill="#555")
        self.create_text(pad-15, h-pad, text=f"{min_val:.1f}", font=("Arial", 8), fill="#555")

class BaseRepresentation:
    def _display(self, data) -> None: 
        print(f"[UI LOG] Displaying data: {data}")
    def _update(self, data) -> None: 
        print(f"[UI LOG] Updating data: {data}")

class IRepresentation(BaseRepresentation):
    def __init__(self, controller):
        self.controller = controller

class IReportRepresentation(IRepresentation):
    def showReport(self, report: Report) -> None:
        messagebox.showinfo(report.title, f"{report.content}\n\nMetrics: {report.metrics}")
    def exportReport(self, report: Report, format: str) -> None:
        messagebox.showinfo("Export", f"Report exported to {format}")

class IForecastRepresentation(IRepresentation):
    def showForecasts(self, forecasts: List[Forecast]) -> None: 
        print(f"Forecasts ready: {len(forecasts)}")

class IRecommendationRepresentation(IRepresentation):
    def displayRecommendations(self, recommendations: List[Recommendation]) -> None:
        print(f"Recommendations: {recommendations}")

class IDashboardRepresentation(IRepresentation):
    def showCurrentQuotes(self, quotes: List[Quote]) -> None:
        print("Quotes updated on dashboard")

class IPortfolioRepresentation(IRepresentation):
    def showPortfolioContents(self, portfolio: Portfolio) -> None:
        print(f"Portfolio: {portfolio.title}")

class LoginWindow(tk.Toplevel):
    def __init__(self, root, auth_controller, on_success):
        super().__init__(root)
        self.title("Financial Platform - Login")
        self.geometry("400x550")
        self.auth = auth_controller
        self.on_success = on_success
        self.protocol("WM_DELETE_WINDOW", root.destroy)
        self.configure(bg="#f0f2f5")
        self.setup_ui()
        
    def setup_ui(self):
        style = ttk.Style()
        style.configure("TLabel", background="#f0f2f5", font=("Segoe UI", 10))
        
        tk.Label(self, text="Welcome Back", font=("Segoe UI", 20, "bold"), bg="#f0f2f5", fg="#2c3e50").pack(pady=30)
        
        nb = ttk.Notebook(self)
        nb.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        f_login = tk.Frame(nb, bg="white")
        tk.Label(f_login, text="Username", bg="white").pack(pady=(20,5))
        e_user = ttk.Entry(f_login)
        e_user.pack(fill=tk.X, padx=20)
        
        tk.Label(f_login, text="Password", bg="white").pack(pady=(10,5))
        e_pass = ttk.Entry(f_login, show="*")
        e_pass.pack(fill=tk.X, padx=20)
        
        def do_login():
            user = self.auth.login(e_user.get(), e_pass.get())
            if user:
                self.on_success(user)
                self.destroy()
            else:
                messagebox.showerror("Error", "Invalid credentials")
                
        ttk.Button(f_login, text="Login", command=do_login).pack(pady=30)
        nb.add(f_login, text="Sign In")
        
        f_reg = tk.Frame(nb, bg="white")
        tk.Label(f_reg, text="New Username", bg="white").pack(pady=(20,5))
        r_user = ttk.Entry(f_reg)
        r_user.pack(fill=tk.X, padx=20)
        
        tk.Label(f_reg, text="Password", bg="white").pack(pady=(10,5))
        r_pass = ttk.Entry(f_reg, show="*")
        r_pass.pack(fill=tk.X, padx=20)
        
        tk.Label(f_reg, text="Goal (Role)", bg="white").pack(pady=(10,5))
        r_role = ttk.Combobox(f_reg, values=["Investor", "Analyst"], state="readonly")
        r_role.current(0)
        r_role.pack(fill=tk.X, padx=20)
        
        def do_reg():
            user = self.auth.register(r_user.get(), r_pass.get(), r_role.get())
            if user:
                messagebox.showinfo("Success", "Registered! Logging in...")
                self.on_success(user)
                self.destroy()
            else:
                messagebox.showerror("Error", "Registration failed")
        
        ttk.Button(f_reg, text="Register", command=do_reg).pack(pady=30)
        nb.add(f_reg, text="Create Account")

class MainWindow(tk.Tk):
    def __init__(self, controllers, reps):
        super().__init__()
        self.withdraw()
        self.ctrls = controllers
        self.reps = reps
        self.title("Financial Analysis Platform")
        self.geometry("1200x850")
        self.current_user = None
        
        LoginWindow(self, self.ctrls['auth'], self.start_session)

    def start_session(self, user):
        self.current_user = user
        self.deiconify()
        self.ctrls['dash'].startMonitoring()
        self.setup_main_ui()

    def setup_main_ui(self):
        header = tk.Frame(self, bg="#2c3e50", height=60)
        header.pack(fill=tk.X)
        tk.Label(header, text=f"Financial Platform | {self.current_user.login} ({self.current_user.role})", 
                 bg="#2c3e50", fg="white", font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT, padx=20, pady=15)
        
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.create_dashboard()
        
        if self.current_user.role in ["Analyst", "Manager"]:
            self.create_forecasting()
            
        if self.current_user.role in ["Investor", "Manager"]:
            self.create_reports()
            self.create_autotrading()

    def create_dashboard(self):
        tab = tk.Frame(self.nb)
        self.nb.add(tab, text="Dashboard")
        
        f_top = tk.LabelFrame(tab, text="Market Monitoring", font=("Segoe UI", 10, "bold"))
        f_top.pack(fill=tk.X, padx=10, pady=5)
        
        market_data = self.ctrls['dash'].getMarketData()
        
        f_charts = tk.Frame(f_top)
        f_charts.pack(fill=tk.X, padx=5, pady=5)
        
        for item in market_data[:3]:
            f_card = tk.Frame(f_charts, bd=1, relief="solid", bg="white")
            f_card.pack(side=tk.LEFT, padx=10, fill=tk.Y)
            
            color = "#2ecc71" if item['change'] >= 0 else "#e74c3c"
            sign = "+" if item['change'] >= 0 else ""
            
            tk.Label(f_card, text=item['ticker'], font=("Segoe UI", 12, "bold"), bg="white").pack()
            tk.Label(f_card, text=f"{item['price']:.2f}", font=("Segoe UI", 14), bg="white").pack()
            tk.Label(f_card, text=f"{sign}{item['change']:.2f}%", fg=color, font=("Segoe UI", 10), bg="white").pack()
            ModernChartWidget(f_card, item['history'], width=150, height=80, title="").pack()

            if self.current_user.role in ["Investor", "Manager"]:
                btn_f = tk.Frame(f_card, bg="white")
                btn_f.pack(fill=tk.X, pady=5)
                tk.Button(btn_f, text="Buy", bg="#2ecc71", fg="white", 
                          command=lambda i=item['id']: self.prompt_trade("buy", i)).pack(side=tk.LEFT, padx=5)
                tk.Button(btn_f, text="Sell", bg="#e74c3c", fg="white", 
                          command=lambda i=item['id']: self.prompt_trade("sell", i)).pack(side=tk.RIGHT, padx=5)
            
        f_bot = tk.LabelFrame(tab, text="My Favorites / Wallet", font=("Segoe UI", 10, "bold"))
        f_bot.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        cols = ("Asset", "Quantity", "Current Value ($)", "Change Since Purchase")
        self.tree_pf = ttk.Treeview(f_bot, columns=cols, show="headings")
        for c in cols: self.tree_pf.heading(c, text=c)
        self.tree_pf.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.refresh_portfolio_view()

    def prompt_trade(self, action, asset_id):
        qty = simpledialog.askfloat(action.title(), f"Amount to {action}:")
        if qty:
            cmd = None
            if action == "buy":
                cmd = BuyAssetCommand(self.ctrls['port'], asset_id, qty, self.current_user.user_id)
            else:
                cmd = SellAssetCommand(self.ctrls['port'], asset_id, qty, self.current_user.user_id)
            
            cmd.execute()
            self.refresh_portfolio_view()
            messagebox.showinfo("Success", f"Order Executed: {action.upper()} {qty}")

    def refresh_portfolio_view(self):
        for i in self.tree_pf.get_children(): self.tree_pf.delete(i)
        pf_data = self.ctrls['dash'].getPortfolioSummary(self.current_user.user_id)
        if pf_data:
            for item in pf_data:
                self.tree_pf.insert("", tk.END, values=(item['ticker'], item['qty'], f"{item['value']:.2f}", f"{item['change']:.2f}%"))
        else:
            self.tree_pf.insert("", tk.END, values=("No assets", "-", "-", "-"))

    def create_forecasting(self):
        tab = tk.Frame(self.nb)
        self.nb.add(tab, text="Forecasting")
        
        paned = ttk.PanedWindow(tab, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        f_left = tk.Frame(paned, width=300, bg="#f9f9f9")
        f_right = tk.Frame(paned, bg="white")
        paned.add(f_left)
        paned.add(f_right)
        
        tk.Label(f_left, text="Configuration", font=("Segoe UI", 12, "bold"), bg="#f9f9f9").pack(pady=20)
        
        assets = self.ctrls['forecast'].getAvailableAssets()
        tk.Label(f_left, text="Select Asset:", bg="#f9f9f9").pack(anchor="w", padx=20)
        cb_asset = ttk.Combobox(f_left, values=[a.ticker for a in assets], state="readonly")
        cb_asset.pack(fill=tk.X, padx=20, pady=5)
        if assets: cb_asset.current(0)
        
        tk.Label(f_left, text="Model:", bg="#f9f9f9").pack(anchor="w", padx=20)
        cb_model = ttk.Combobox(f_left, values=["ARIMA", "LSTM", "Random Forest"], state="readonly")
        cb_model.current(0)
        cb_model.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(f_left, text="Period:", bg="#f9f9f9").pack(anchor="w", padx=20)
        cb_period = ttk.Combobox(f_left, values=["1W", "1M"], state="readonly")
        cb_period.current(1)
        cb_period.pack(fill=tk.X, padx=20, pady=5)
        
        lbl_res = tk.Label(f_left, text="", bg="#f9f9f9", justify=tk.LEFT)
        lbl_res.pack(pady=20, padx=20)
        
        chart_container = tk.Frame(f_right, bg="white")
        chart_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        def run_forecast():
            ticker = cb_asset.get()
            asset_obj = next((a for a in assets if a.ticker == ticker), None)
            ctx = AnalysisContext(self.current_user.user_id, [asset_obj.asset_id], cb_period.get())
            
            rec_text = self.ctrls['analysis'].analyseData(asset_obj.asset_id)
            f = self.ctrls['forecast'].createForecast(ctx, cb_model.get())
            
            recs = self.ctrls['rec'].generateRecommendations(ctx, rec_text)
            final_rec = recs[0].rec_value.upper()
            
            res_txt = (f"Target Price: {f.target_value:.2f}\n"
                       f"Confidence Interval: [{f.conf_interval[0]:.2f}, {f.conf_interval[1]:.2f}]\n"
                       f"Volatility: {f.volatility*100:.1f}%\n"
                       f"Recommendation: {final_rec}")
            
            lbl_res.config(text=res_txt, font=("Segoe UI", 11), fg="#2980b9")
            
            for w in chart_container.winfo_children(): w.destroy()
            hist_data = self.ctrls['dash'].getMarketData()
            asset_hist = next((h['history'] for h in hist_data if h['ticker'] == ticker), [])
            
            full_data = asset_hist + [f.target_value]
            ModernChartWidget(chart_container, full_data, width=700, height=400, title=f"{ticker} Forecast Analysis").pack()

        ttk.Button(f_left, text="Generate Forecast", command=run_forecast).pack(fill=tk.X, padx=20, pady=10)

        if self.current_user.role == "Analyst":
            tk.Label(f_left, text="--- Model Management ---", bg="#f9f9f9").pack(pady=10)
            def train_model_ui():
                name = simpledialog.askstring("New Model", "Model Name:")
                if name:
                    m = self.ctrls['forecast'].train_new_model(name, {"epoch": 100, "layers": 5})
                    messagebox.showinfo("Model Training", f"Model '{m.name}' Status: {m.status}\nAccuracy: {m.accuracy:.2f}")
            
            ttk.Button(f_left, text="Train New Model", command=train_model_ui).pack(fill=tk.X, padx=20, pady=5)

    def create_reports(self):
        tab = tk.Frame(self.nb)
        self.nb.add(tab, text="Reports")
        
        f_metrics = tk.Frame(tab)
        f_metrics.pack(fill=tk.X, padx=20, pady=20)
        
        self.metric_labels = {}
        metrics_keys = ["Yield", "Volatility", "Benchmark (S&P500)", "VaR (95%)", "Stress Test (-20%)"]
        
        for k in metrics_keys:
            f_m = tk.Frame(f_metrics, bg="white", bd=1, relief="ridge", width=150, height=80)
            f_m.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)
            f_m.pack_propagate(False)
            tk.Label(f_m, text=k, bg="white", fg="#777").pack(pady=(10,5))
            l = tk.Label(f_m, text="-", bg="white", font=("Segoe UI", 14, "bold"))
            l.pack()
            self.metric_labels[k] = l

        f_content = tk.Frame(tab)
        f_content.pack(fill=tk.BOTH, expand=True, padx=20)
        
        lbl_details = tk.Label(f_content, text="Generate a report to see details.", justify=tk.LEFT, font=("Consolas", 10))
        lbl_details.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        chart_frame = tk.Frame(f_content, bg="white")
        chart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        def gen_report():
            rep = self.ctrls['rep'].generateReport("YTD", self.current_user.user_id)
            lbl_details.config(text=rep.content)
            
            for k, v in rep.metrics.items():
                if k in self.metric_labels:
                    self.metric_labels[k].config(text=v)
            
            for w in chart_frame.winfo_children(): w.destroy()
            import random
            dummy_yield = [100 + i + random.uniform(-2, 3) for i in range(50)]
            ModernChartWidget(chart_frame, dummy_yield, width=500, height=300, title="Portfolio Performance (YTD)").pack()
            
        ttk.Button(tab, text="Run Analytics", command=gen_report).pack(pady=10)

    def create_autotrading(self):
        tab = tk.Frame(self.nb)
        self.nb.add(tab, text="AutoTrading")
        
        f_form = tk.LabelFrame(tab, text="Create Trading Bot", padx=10, pady=10)
        f_form.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, pady=10, expand=False, width=300)
        
        tk.Label(f_form, text="Bot Name").pack(anchor="w")
        e_name = ttk.Entry(f_form); e_name.pack(fill=tk.X, pady=5)
        
        tk.Label(f_form, text="Strategy").pack(anchor="w")
        c_strat = ttk.Combobox(f_form, values=["Moving Average", "RSI Scalp", "Mean Reversion"])
        c_strat.pack(fill=tk.X, pady=5)
        
        tk.Label(f_form, text="Asset (Ticker)").pack(anchor="w")
        assets = self.ctrls['dash'].getMarketData()
        c_asset = ttk.Combobox(f_form, values=[a['ticker'] for a in assets])
        c_asset.pack(fill=tk.X, pady=5)
        
        tk.Label(f_form, text="Stop Loss (%)").pack(anchor="w")
        e_sl = ttk.Entry(f_form); e_sl.pack(fill=tk.X, pady=5)
        
        tk.Label(f_form, text="Take Profit (%)").pack(anchor="w")
        e_tp = ttk.Entry(f_form); e_tp.pack(fill=tk.X, pady=5)
        
        tk.Label(f_form, text="Max Position Size ($)").pack(anchor="w")
        e_max = ttk.Entry(f_form); e_max.pack(fill=tk.X, pady=5)
        
        f_list = tk.LabelFrame(tab, text="Active Bots", padx=10, pady=10)
        f_list.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        cols = ("Name", "Strategy", "Asset", "SL/TP")
        tree = ttk.Treeview(f_list, columns=cols, show="headings")
        for c in cols: tree.heading(c, text=c)
        tree.pack(fill=tk.BOTH, expand=True)
        
        def refresh_bots():
            for i in tree.get_children(): tree.delete(i)
            bots = self.ctrls['bot'].getUserBots(self.current_user.user_id)
            for b in bots:
                tree.insert("", tk.END, values=(b.name, b.strategy, b.assets, f"{b.stop_loss}% / {b.take_profit}%"))
        
        def run_execution_cycle():
            logs = self.ctrls['bot'].run_bot_cycle(self.current_user.user_id)
            for l in logs: print(f"[BOT LOG] {l}")
            messagebox.showinfo("Bot Execution", f"Cycle completed. Checked {len(logs)} bots.")

        def add_bot():
            try:
                self.ctrls['bot'].createBot(
                    e_name.get(), c_strat.get(), c_asset.get(),
                    float(e_sl.get()), float(e_tp.get()), float(e_max.get()),
                    self.current_user.user_id
                )
                refresh_bots()
                messagebox.showinfo("Success", "Bot Deployed")
            except ValueError:
                messagebox.showerror("Error", "Please check numeric fields")
                
        ttk.Button(f_form, text="Deploy Bot", command=add_bot).pack(pady=20, fill=tk.X)
        ttk.Button(f_list, text="Run Execution Cycle", command=run_execution_cycle).pack(fill=tk.X)
        refresh_bots()