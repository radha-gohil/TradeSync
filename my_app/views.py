from django.shortcuts import render

# Create your views here.
import pandas as pd
import numpy as np
import yfinance as yf
from django.http import JsonResponse
from django.shortcuts import render,redirect
from django.contrib import messages
import firebase_admin
from firebase_admin import auth,credentials
import requests
from django.core.cache import cache
import pandas_ta as ta
from statsmodels.tsa.stattools import adfuller
from sklearn.metrics import mean_squared_error, r2_score
from statsmodels.tsa.arima.model import ARIMA
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime,timedelta
import plotly.graph_objects as go
import json
import matplotlib.pyplot as plt
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.callbacks import EarlyStopping
import traceback
from sklearn.preprocessing import MinMaxScaler
from django.db.models import Count
from .models import TrendingStock
import talib
from django.core.mail import send_mail
from django.contrib.auth import logout
from .models import UserProfile, Portfolio, Transaction
from .forms import ProfileUpdateForm, PortfolioForm
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date
from django.core.paginator import Paginator
from decimal import Decimal
from django.contrib.auth.models import User
from django.db import transaction
from django.utils.timezone import now, timedelta
import time
# Initialize Firebase only if not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate("")
    firebase_admin.initialize_app(cred)

# Create your views here.

def dashboard(request):
    tickers = ["TSLA","RELIANCE.NS","HDFCBANK.NS","TCS.NS","BHARTIARTL.NS","ICICIBANK.NS","INFY.NS","HINDUNILVR.NS",
               "SBIN.NS","KOTAKBANK.NS","BAJFINANCE.NS","WIPRO.NS","HCLTECH.NS","ASIANPAINT.NS","MARUTI.NS"]	

    data = []
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d")

        if not hist.empty:
            open_price = hist["Open"].iloc[0]
            close_price = hist["Close"].iloc[0]
            change_value = close_price - open_price
            percent_change = (change_value / open_price) * 100
            company_name = stock.info.get("longName", ticker)  # Fetch company name if available

            data.append({
                "ticker": ticker,
                "name": company_name,
                "close": round(close_price, 2),
                "change_value": round(change_value, 2),
                "change": round(percent_change, 2),
            })

    # Sorting
    sorted_data = sorted(data, key=lambda x: x["change"], reverse=True)
    top_gainers = sorted_data[:5]
    top_losers = sorted_data[-5:]

    news=fetch_market_news()
    
    selected_symbols = request.GET.getlist('symbols')  # Get selected stock symbols
    stocks_data = []

    # Stock list for Indian stocks
    stock_list = [
        {"symbol": "RELIANCE.NS", "name": "Reliance Industries"},
        {"symbol": "HDFCBANK.NS", "name": "HDFC Bank"},
        {"symbol": "TCS.NS", "name": "Tata Consultancy Services"},
        {"symbol": "BHARTIARTL.NS", "name": "Bharti Airtel"},
        {"symbol": "ICICIBANK.NS", "name": "ICICI Bank"},
        {"symbol": "INFY.NS", "name": "Infosys"},
        {"symbol": "HINDUNILVR.NS", "name": "Hindustan Unilever"},
        {"symbol": "SBIN.NS", "name": "State Bank of India"},
        {"symbol": "KOTAKBANK.NS", "name": "Kotak Mahindra Bank"},
        {"symbol": "LT.NS", "name": "Larsen & Toubro"},
        {"symbol": "AXISBANK.NS", "name": "Axis Bank"},
        {"symbol": "BAJFINANCE.NS", "name": "Bajaj Finance"},
        {"symbol": "WIPRO.NS", "name": "Wipro"},
        {"symbol": "HCLTECH.NS", "name": "HCL Technologies"},
        {"symbol": "ASIANPAINT.NS", "name": "Asian Paints"},
        {"symbol": "MARUTI.NS", "name": "Maruti Suzuki"},
        {"symbol": "ITC.NS", "name": "ITC Limited"},
        {"symbol": "NESTLEIND.NS", "name": "Nestle India"},
        {"symbol": "M&M.NS", "name": "Mahindra & Mahindra"},
        {"symbol": "ULTRACEMCO.NS", "name": "UltraTech Cement"},
        {"symbol": "SUNPHARMA.NS", "name": "Sun Pharma"},
        {"symbol": "POWERGRID.NS", "name": "Power Grid Corporation"},
        {"symbol": "NTPC.NS", "name": "NTPC Limited"},
        {"symbol": "BAJAJFINSV.NS", "name": "Bajaj Finserv"},
        {"symbol": "TATASTEEL.NS", "name": "Tata Steel"},
        {"symbol": "HDFCLIFE.NS", "name": "HDFC Life"},
        {"symbol": "DIVISLAB.NS", "name": "Divi’s Laboratories"},
        {"symbol": "ADANIGREEN.NS", "name": "Adani Green Energy"},
        {"symbol": "SBILIFE.NS", "name": "SBI Life Insurance"},
        {"symbol": "BRITANNIA.NS", "name": "Britannia Industries"},
        {"symbol": "JSWSTEEL.NS", "name": "JSW Steel"},
        {"symbol": "CIPLA.NS", "name": "Cipla"},
        {"symbol": "TECHM.NS", "name": "Tech Mahindra"},
        {"symbol": "BAJAJ-AUTO.NS", "name": "Bajaj Auto"},
        {"symbol": "GRASIM.NS", "name": "Grasim Industries"},
        {"symbol": "ADANIPORTS.NS", "name": "Adani Ports"},
        {"symbol": "TATAMOTORS.NS", "name": "Tata Motors"},
        {"symbol": "HEROMOTOCO.NS", "name": "Hero MotoCorp"},
        {"symbol": "HINDALCO.NS", "name": "Hindalco Industries"},
        {"symbol": "COALINDIA.NS", "name": "Coal India"},
        {"symbol": "IOC.NS", "name": "Indian Oil Corporation"},
        {"symbol": "SHREECEM.NS", "name": "Shree Cement"},
        {"symbol": "DRREDDY.NS", "name": "Dr. Reddy’s Laboratories"},
        {"symbol": "EICHERMOT.NS", "name": "Eicher Motors"},
        {"symbol": "TATACONSUM.NS", "name": "Tata Consumer Products"},
        {"symbol": "UPL.NS", "name": "UPL Limited"},
        {"symbol": "BPCL.NS", "name": "Bharat Petroleum"},
        {"symbol": "APOLLOHOSP.NS", "name": "Apollo Hospitals"},
        {"symbol": "DLF.NS", "name": "DLF Limited"},
        {"symbol": "SBICARD.NS", "name": "SBI Cards & Payment"},
        {"symbol": "ICICIPRULI.NS", "name": "ICICI Prudential"},
        {"symbol": "INDUSINDBK.NS", "name": "IndusInd Bank"},
    ]

    # If no stocks are selected, show all by default
    if not selected_symbols:
        selected_symbols = [stock["symbol"] for stock in stock_list]  

    for symbol in selected_symbols:
        try:
            stock = yf.Ticker(symbol)
            stock_info = stock.history(period="1d")

            if not stock_info.empty:
                stocks_data.append({
                    "symbol": symbol.upper(),
                    "name": stock.info.get("shortName", "N/A"),
                    "price": round(stock_info['Close'].iloc[-1], 2),
                    "open": round(stock_info['Open'].iloc[-1], 2),
                    "close": round(stock_info['Close'].iloc[-1], 2),
                    "high": round(stock_info['High'].iloc[-1], 2),
                    "low": round(stock_info['Low'].iloc[-1], 2),
                    "volume": stock_info['Volume'].iloc[-1],
                    "change": round(stock_info['Close'].iloc[-1] - stock_info['Open'].iloc[-1], 2),
                })
            else:
                stocks_data.append({"symbol": symbol.upper(), "error": "Stock data not available."})

        except Exception as e:
            stocks_data.append({"symbol": symbol.upper(), "error": f"Error fetching data: {e}"})

    return render(request, "dashboard.html", {"gainers": top_gainers, "losers": top_losers,"news": news,"stocks": stocks_data, "stock_list": stock_list})


def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            # Create user in Firebase
            auth.create_user(uid=username, email=email, password=password)
            messages.success(request, "Account successfully created! Please log in.")
            return redirect("login")  # Redirect to login after successful signup
        except Exception as e:
            messages.error(request, f"Signup failed: {str(e)}")
    
    return render(request, "login_signup.html")  # Render the same page

def login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = auth.get_user_by_email(email)
            request.session["user_id"] = user.uid
            messages.success(request, "Login successful!")
            return redirect("dashboard")  # Redirect to dashboard
        except Exception as e:
            messages.error(request, f"Login failed: {str(e)}")

    return render(request, "login_signup.html")  # Render the same page

def logout(request):
    request.session.flush()  # Clear session
    messages.success(request, "Logged out successfully.")
    return redirect("login")

def dashboard2(request):
    return render(request,"dashboard2.html")

def logo_page(request):
    return render(request,"logo.html")

def searchstock(request):
    query = request.GET.get("q", "").upper()
    stock_data = None
    historical_data = []
    trending_stocks = TrendingStock.objects.order_by('-search_count')[:10]
    upcoming_earnings = []

    # Handle AJAX Live Search Requests
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        if query:
            try:
                stock = yf.Ticker(query)
                info = stock.info
                if "longName" in info and "currentPrice" in info:
                    return JsonResponse({
                        "symbol": query,
                        "name": info["longName"],
                        "price": info["currentPrice"],
                    })
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=500)
        return JsonResponse({"error": "Stock not found"}, status=404)

    if query:
        try:
            stock = yf.Ticker(query)
            info = stock.info

            if "currentPrice" not in info:
                return render(request, "searchstock.html", {
                    "error": "Stock data unavailable.",
                    "trending_stocks": trending_stocks
                })

            # Update Trending Stocks Count
            trending_stock, _ = TrendingStock.objects.get_or_create(symbol=query, defaults={"search_count": 0})
            trending_stock.search_count += 1
            trending_stock.save()

            # Fetch earnings date safely
            earnings_calendar = getattr(stock, "calendar", {})
            earnings_date = list(earnings_calendar.values())[0] if earnings_calendar else "N/A"

            # Stock Data
            stock_data = {
                "symbol": query,
                "name": info.get("longName", "N/A"),
                "current_price": info.get("currentPrice", "N/A"),
                "high": info.get("dayHigh", "N/A"),
                "low": info.get("dayLow", "N/A"),
                "open": info.get("open", "N/A"),  
                "close": info.get("previousClose", "N/A"),  
                "volume": info.get("volume", "N/A"),
                "market_cap": info.get("marketCap", "N/A"),
                "revenue": info.get("totalRevenue", "N/A"),
                "net_income": info.get("netIncome", "N/A"),
                "eps": info.get("trailingEps", "N/A"),
                "dividend_yield": info.get("dividendYield", "N/A"),
                "pe_ratio": info.get("trailingPE", "N/A"),
                "debt_to_equity": info.get("debtToEquity", "N/A"),
                "earnings_date": earnings_date,
                
                "industry": info.get("industry","N/A"),
                "sector": info.get("sector","N/A"),
                "description": info.get("longBusinessSummary","N/A"),
                "headquarters": info.get("city", "") + ", " + info.get("state", ""),
                "ceo": info.get("companyOfficers", [{}])[0].get("name", "N/A"),
                "employees": info.get("fullTimeEmployees","N/A"),
                "website": info.get("website","N/A"),
                "exchange": info.get("exchange","N/A"),
            }

            # Fetch Upcoming Earnings Data
            try:
                earnings = getattr(stock, "earnings_dates", pd.DataFrame())
                if not earnings.empty:
                    for index, row in earnings.iterrows():
                        upcoming_earnings.append({
                            "date": str(index.date()),
                            "eps_estimate": row.get("EPS Estimate", "N/A"),
                            "revenue_estimate": row.get("Revenue Estimate", "N/A")
                        })
            except Exception as e:
                print(f"Earnings Data Fetch Error: {e}")

            # Fetch 30 Days Historical Data
            end_date = datetime.today().date()
            start_date = end_date - timedelta(days=30)
            stock_history = yf.download(query, start=start_date, end=end_date)

            if not stock_history.empty:
                stock_history.reset_index(inplace=True)
                stock_history["Date"] = stock_history["Date"].dt.strftime('%Y-%m-%d')

                # Convert Close Prices to NumPy Array for TA-Lib
                close_prices = stock_history['Close'].to_numpy(dtype=np.float64)

                # Initialize Indicators
                indicators = ["SMA_14", "EMA_14", "RSI_14", "BB_upper", "BB_middle", "BB_lower"]
                for indicator in indicators:
                    stock_history[indicator] = np.nan

                try:
                    stock_history['SMA_14'] = talib.SMA(close_prices, timeperiod=14)
                    stock_history['EMA_14'] = talib.EMA(close_prices, timeperiod=14)
                    stock_history['RSI_14'] = talib.RSI(close_prices, timeperiod=14)

                    bb_upper, bb_middle, bb_lower = talib.BBANDS(close_prices, timeperiod=14)
                    stock_history['BB_upper'] = bb_upper
                    stock_history['BB_middle'] = bb_middle
                    stock_history['BB_lower'] = bb_lower
                except Exception as e:
                    print(f"TA-Lib Error: {e}")

                # Convert NaN values to None (better for JSON)
                stock_history.fillna(value=0, inplace=True)

                # Convert to JSON Format
                historical_data = stock_history[[ 
                    "Date", "Open", "High", "Low", "Close", "Volume",
                    "SMA_14", "EMA_14", "RSI_14", "BB_upper", "BB_middle", "BB_lower"
                ]].to_dict(orient="records")

        except Exception as e:
            return render(request, "searchstock.html", {"error": str(e), "trending_stocks": trending_stocks})
    print("HISTORICAL DATA LENGTH:", len(historical_data))
    return render(request, "searchstock.html", {
        "stock_data": stock_data,
        "historical_data": historical_data,
        "upcoming_earnings": upcoming_earnings,
        "trending_stocks": trending_stocks,
    })
    
def recommandation(request):
    return render(request,'recommandation.html')

def portfolio(request):
    return render(request,'portfolio.html')


def live_stock_prices(request):
    selected_symbols = request.GET.getlist('symbols')  # Get selected stock symbols
    stocks_data = []

    # Stock list for Indian stocks
    stock_list = [
        {"symbol": "RELIANCE.NS", "name": "Reliance Industries"},
        {"symbol": "HDFCBANK.NS", "name": "HDFC Bank"},
        {"symbol": "TCS.NS", "name": "Tata Consultancy Services"},
        {"symbol": "BHARTIARTL.NS", "name": "Bharti Airtel"},
        {"symbol": "ICICIBANK.NS", "name": "ICICI Bank"},
        {"symbol": "INFY.NS", "name": "Infosys"},
        {"symbol": "HINDUNILVR.NS", "name": "Hindustan Unilever"},
        {"symbol": "SBIN.NS", "name": "State Bank of India"},
        {"symbol": "KOTAKBANK.NS", "name": "Kotak Mahindra Bank"},
        {"symbol": "LT.NS", "name": "Larsen & Toubro"},
        {"symbol": "AXISBANK.NS", "name": "Axis Bank"},
        {"symbol": "BAJFINANCE.NS", "name": "Bajaj Finance"},
        {"symbol": "WIPRO.NS", "name": "Wipro"},
        {"symbol": "HCLTECH.NS", "name": "HCL Technologies"},
        {"symbol": "ASIANPAINT.NS", "name": "Asian Paints"},
        {"symbol": "MARUTI.NS", "name": "Maruti Suzuki"},
        {"symbol": "ITC.NS", "name": "ITC Limited"},
        {"symbol": "NESTLEIND.NS", "name": "Nestle India"},
        {"symbol": "M&M.NS", "name": "Mahindra & Mahindra"},
        {"symbol": "ULTRACEMCO.NS", "name": "UltraTech Cement"},
        {"symbol": "SUNPHARMA.NS", "name": "Sun Pharma"},
        {"symbol": "POWERGRID.NS", "name": "Power Grid Corporation"},
        {"symbol": "NTPC.NS", "name": "NTPC Limited"},
        {"symbol": "BAJAJFINSV.NS", "name": "Bajaj Finserv"},
        {"symbol": "TATASTEEL.NS", "name": "Tata Steel"},
        {"symbol": "HDFCLIFE.NS", "name": "HDFC Life"},
        {"symbol": "DIVISLAB.NS", "name": "Divi’s Laboratories"},
        {"symbol": "ADANIGREEN.NS", "name": "Adani Green Energy"},
        {"symbol": "SBILIFE.NS", "name": "SBI Life Insurance"},
        {"symbol": "BRITANNIA.NS", "name": "Britannia Industries"},
        {"symbol": "JSWSTEEL.NS", "name": "JSW Steel"},
        {"symbol": "CIPLA.NS", "name": "Cipla"},
        {"symbol": "TECHM.NS", "name": "Tech Mahindra"},
        {"symbol": "BAJAJ-AUTO.NS", "name": "Bajaj Auto"},
        {"symbol": "GRASIM.NS", "name": "Grasim Industries"},
        {"symbol": "ADANIPORTS.NS", "name": "Adani Ports"},
        {"symbol": "TATAMOTORS.NS", "name": "Tata Motors"},
        {"symbol": "HEROMOTOCO.NS", "name": "Hero MotoCorp"},
        {"symbol": "HINDALCO.NS", "name": "Hindalco Industries"},
        {"symbol": "COALINDIA.NS", "name": "Coal India"},
        {"symbol": "IOC.NS", "name": "Indian Oil Corporation"},
        {"symbol": "SHREECEM.NS", "name": "Shree Cement"},
        {"symbol": "DRREDDY.NS", "name": "Dr. Reddy’s Laboratories"},
        {"symbol": "EICHERMOT.NS", "name": "Eicher Motors"},
        {"symbol": "TATACONSUM.NS", "name": "Tata Consumer Products"},
        {"symbol": "UPL.NS", "name": "UPL Limited"},
        {"symbol": "BPCL.NS", "name": "Bharat Petroleum"},
        {"symbol": "APOLLOHOSP.NS", "name": "Apollo Hospitals"},
        {"symbol": "DLF.NS", "name": "DLF Limited"},
        {"symbol": "SBICARD.NS", "name": "SBI Cards & Payment"},
        {"symbol": "ICICIPRULI.NS", "name": "ICICI Prudential"},
        {"symbol": "INDUSINDBK.NS", "name": "IndusInd Bank"},
    ]

    # If no stocks are selected, show all by default
    if not selected_symbols:
        selected_symbols = [stock["symbol"] for stock in stock_list]  

    for symbol in selected_symbols:
        try:
            stock = yf.Ticker(symbol)
            stock_info = stock.history(period="1d")

            if not stock_info.empty:
                stocks_data.append({
                    "symbol": symbol.upper(),
                    "name": stock.info.get("shortName", "N/A"),
                    "price": round(stock_info['Close'].iloc[-1], 2),
                    "open": round(stock_info['Open'].iloc[-1], 2),
                    "close": round(stock_info['Close'].iloc[-1], 2),
                    "high": round(stock_info['High'].iloc[-1], 2),
                    "low": round(stock_info['Low'].iloc[-1], 2),
                    "volume": stock_info['Volume'].iloc[-1],
                    "change": round(stock_info['Close'].iloc[-1] - stock_info['Open'].iloc[-1], 2),
                })
            else:
                stocks_data.append({"symbol": symbol.upper(), "error": "Stock data not available."})

        except Exception as e:
            stocks_data.append({"symbol": symbol.upper(), "error": f"Error fetching data: {e}"})

    return render(request, "live_stock_prices.html", {"stocks": stocks_data, "stock_list": stock_list})


def marketnews(request):
    """Fetch live market news using Yahoo Finance API from RapidAPI"""
    url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/news/v2/get-details"

    headers = {
        "X-RapidAPI-Key": "f985497e77mshbc191c219c6b102p1fcd30jsn7d87c648d604",  # Replace with your API Key
        "X-RapidAPI-Host": "apidojo-yahoo-finance-v1.p.rapidapi.com"
    }

    querystring = {"uuid": "9800566d-1dd9-3358-a3b1-5a24f2685437"}  # Example query parameter
    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()

    news = []
    for article in data.get("data", {}).get("main", {}).get("stream", []):
        title = article.get("content", {}).get("title", "No Title")
        link = article.get("content", {}).get("clickThroughUrl", {}).get("url", "#")
        news.append({"title": title, "link": link})
    return render(request, "marketnews.html", {"news": news})

def top_movers(request):
    tickers = [
  "RELIANCE.NS", "HDFCBANK.NS", "TCS.NS", "BHARTIARTL.NS", "ICICIBANK.NS",
  "INFY.NS", "HINDUNILVR.NS", "SBIN.NS", "KOTAKBANK.NS", "LT.NS",
  "AXISBANK.NS", "BAJFINANCE.NS", "WIPRO.NS", "HCLTECH.NS", "ASIANPAINT.NS",
  "MARUTI.NS", "ITC.NS", "NESTLEIND.NS", "M&M.NS", "ULTRACEMCO.NS",
  "SUNPHARMA.NS", "POWERGRID.NS", "NTPC.NS", "BAJAJFINSV.NS", "TATASTEEL.NS",
  "HDFCLIFE.NS", "DIVISLAB.NS", "ADANIGREEN.NS", "SBILIFE.NS", "BRITANNIA.NS",
  "JSWSTEEL.NS", "CIPLA.NS", "TECHM.NS", "BAJAJ-AUTO.NS", "GRASIM.NS",
  "ADANIPORTS.NS", "TATAMOTORS.NS", "HEROMOTOCO.NS", "HINDALCO.NS", "COALINDIA.NS",
  "IOC.NS", "SHREECEM.NS", "DRREDDY.NS", "EICHERMOT.NS", "TATACONSUM.NS",
  "UPL.NS", "BPCL.NS", "APOLLOHOSP.NS", "DLF.NS", "SBICARD.NS",
  "ICICIPRULI.NS", "INDUSINDBK.NS"]  # Example tickers

    data = []
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d")  # Get today's data
        if not hist.empty:
            open_price = hist["Open"][0]
            close_price = hist["Close"][0]
            percent_change = ((close_price - open_price) / open_price) * 100
            data.append({"ticker": ticker, "open": open_price, "close": close_price, "change": percent_change})

    # Sort to find top gainers and losers
    sorted_data = sorted(data, key=lambda x: x["change"], reverse=True)
    top_gainers = sorted_data[:3]
    top_losers = sorted_data[-3:]

    return render(request, "top_movers.html", {"gainers": top_gainers, "losers": top_losers})

def fetch_market_news():
    API_KEY = "4102302c15884e00b7fd443e72b48be8"  # Replace with your actual NewsAPI key
    NEWS_URL = f"https://newsapi.org/v2/top-headlines?category=business&language=en&apiKey={API_KEY}"

    try:
        response = requests.get(NEWS_URL)
        news_data = response.json()

        articles = news_data.get("articles", [])[:10]  # Get top 10 news articles
        news_list = []

        for article in articles:
            news_list.append({
                "title": article["title"],
                "description": article["description"],
                "url": article["url"],
                "image": article["urlToImage"] if article["urlToImage"] else "default_image.jpg",
                "source": article["source"]["name"],
            })
        
        return news_list

    except Exception as e:
        print("Error fetching market news:", e)
        return []

def market_news_view(request):
    news = fetch_market_news()
    return render(request, "marketnews.html", {"news": news})

def dashboard_slider(request):
    return render(request,"dashboard_slider.html")

def trading_bot(request):
    return render(request,"trading_bot.html")


# Initialize Firebase only if not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase/apna-college-2b778-d0a7ea9d531a.json")
    firebase_admin.initialize_app(cred)


def psignup(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        try:
            auth.create_user(uid=username, email=email, password=password)
            messages.success(request, "Account is successfully created! Now login through your credentials.")
            return redirect('plogin')
        except Exception as e:
            messages.error(request, f"Error: Sign UP failed {str(e)}")
    return render(request, 'signup.html')


def plogin(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        try:
            user = auth.get_user_by_email(email)
            uid = user.uid
            user_profile, created = UserProfile.objects.get_or_create(user_id=uid, email=email)

            if created or user_profile.is_first_login:
                user_profile.points = 10000  # Assign dummy points
                user_profile.is_first_login = False
                user_profile.save()

                # Send Welcome Email
                send_mail(
                    "Welcome to TradeSync!",
                    f"Hello {email},\n\n🎉 You have received 10,000 dummy points to start trading!\n\n📊 Portfolio Guide:\n- Buy/Sell stocks from your portfolio.\n- Track your profits/losses.\n- View live market data.\n\nHappy Trading!\nTradeSync Team",
                    "noreply@tradesync.com",
                    [email],
                    fail_silently=False,
                )
            messages.success(request, "Account is successfully logged in.")
            request.session["user_id"] = uid
            return redirect('pdashboard')
        except Exception as e:
            messages.error(request, f"Error: login failed {str(e)}")
    return render(request, 'plogin.html')


def user_logout(request):
    logout(request)
    request.session.flush()
    return redirect('plogin')


def pdashboard(request):
    user_id = request.session.get("user_id")

    if not user_id:
        messages.error(request, "You need to login first!")
        return redirect('plogin')

    try:
        user_profile = UserProfile.objects.get(user_id=user_id)
        portfolio = Portfolio.objects.filter(user=user_profile)
        transcations = Transaction.objects.filter(user=user_profile).order_by('-date')[:5]

        total_investment = sum(stock.quantity * stock.purchase_price for stock in portfolio)
        past_transactions = Transaction.objects.filter(user=user_profile, date__gte=now() - timedelta(days=30)).order_by("date")

        portfolio_values = []
        dates = []
        current_value = Decimal('10000')  # Start with initial 10,000 points

        for txn in past_transactions:
            if txn.transaction_type == "Buy":
                current_value -= Decimal(txn.quantity) * Decimal(txn.price)
            elif txn.transaction_type == "Sell":
                current_value += Decimal(txn.quantity) * Decimal(txn.price)

            portfolio_values.append(float(current_value))
            dates.append(txn.date.strftime("%Y-%m-%d"))

        # Convert data to JSON for Chart.js
        portfolio_data = json.dumps({"dates": dates, "values": portfolio_values})

        # Calculate percentage allocation per stock
        investment_allocation = {}
        for stock in portfolio:
            stock_value = stock.quantity * stock.purchase_price
            investment_allocation[stock.stock_symbol] = (stock_value / total_investment) * 100 if total_investment > 0 else 0

        # Convert data to JSON for Chart.js
        investment_chart_data = json.dumps({
            "labels": list(investment_allocation.keys()),  # Stock names
            "data": [float(value) for value in investment_allocation.values()]  # Convert Decimal to float
            })
        
        # Account Growth Calculation
        last_week_balance = user_profile.last_week_balance
        last_month_balance = user_profile.last_month_balance
        current_balance = user_profile.points

        # Growth Percentage Calculation
        weekly_growth = ((current_balance - last_week_balance) / last_week_balance) * 100 if last_week_balance > 0 else 0
        monthly_growth = ((current_balance - last_month_balance) / last_month_balance) * 100 if last_month_balance > 0 else 0

        return render(request, "pdashboard.html", {
            "user_profile": user_profile,
            "profile_image": user_profile.profile_picture.url,
            "portfolio": portfolio,
            "transactions": transcations,
            "total_investment": total_investment,
            "portfolio_data": portfolio_data,
            "investment_chart_data": investment_chart_data,
            "weekly_growth": round(weekly_growth, 2),
            "monthly_growth": round(monthly_growth, 2),
        })
    except UserProfile.DoesNotExist:
        messages.error(request, "User profile not found. Please login again!")
        return redirect("plogin")


def update_profile(request):
    user_id = request.session.get("user_id")

    if not user_id:
        messages.error(request, "You need to login first!")
        return redirect('plogin')

    user_profile = UserProfile.objects.get(user_id=user_id)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('pdashboard')
    else:
        form = ProfileUpdateForm(instance=user_profile)
    return render(request, 'update_profile.html', {'form': form})


def portfolio(request):
    user_id = request.session.get("user_id")

    if not user_id:
        messages.error(request, "You need to login first!")
        return redirect('plogin')

    user_profile = UserProfile.objects.get(user_id=user_id)
    portfolios = Portfolio.objects.filter(user=user_profile)
    
    total_investments = Decimal("0.00")
    current_value = Decimal("0.00")
    holdings = []
    
    for stock in portfolios:
        live_stock = yf.Ticker(stock.stock_symbol)
        history = live_stock.history(period='1d')

        if not history.empty:
            live_price = Decimal(str(history["Close"].iloc[-1]))
        else:
            live_price = stock.purchase_price  # Use purchase price if no data is available

        stock_investment = stock.purchase_price * stock.quantity
        stock_current_value = live_price * stock.quantity
        stock_profit_loss = stock_current_value - stock_investment
        stock_profit_loss_percent = (stock_profit_loss / stock_investment) * 100 if stock_investment else Decimal("0.00")

        total_investments += stock_investment
        current_value += stock_current_value

        holdings.append({
            'id': stock.id,  # Added stock ID for actions
            'symbol': stock.stock_symbol,
            'quantity': stock.quantity,
            'purchase_price': round(stock.purchase_price, 2),
            'purchase_date': stock.purchase_date,
            'current_price': round(live_price, 2),
            'total_value': round(stock_current_value, 2),
            'profit_loss': round(stock_profit_loss, 2),
            'profit_loss_percent': round(stock_profit_loss_percent, 2),
        })        
    
    total_profit_loss = current_value - total_investments
    total_profit_loss_percent = (total_profit_loss / total_investments) * 100 if total_investments else Decimal("0.00")

    context = {
        'holdings': holdings,
        'total_investments': round(total_investments, 2),
        'current_value': round(current_value, 2),
        'total_profit_loss': round(total_profit_loss, 2),
        'profit_loss_percent': round(total_profit_loss_percent, 2),
    }
    return render(request, "portfolio.html", context)


def add_stock(request):
    user_id = request.session.get("user_id")

    if not user_id:
        messages.error(request, "You need to login first!")
        return redirect('plogin')

    user_profile = UserProfile.objects.get(user_id=user_id)

    if request.method == 'POST':
        form = PortfolioForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            purchase_price = form.cleaned_data['purchase_price']
            if quantity <= 0 or purchase_price <= 0:
                messages.error(request, "Quantity and price must be greater than zero.")
            else:
                portfolio = form.save(commit=False)
                portfolio.user = user_profile
                portfolio.save()
                messages.success(request, "Stock added successfully.")
                return redirect('portfolio')
    else:
        form = PortfolioForm()
    return render(request, 'add_stock.html', {'form': form})

def delete_stock(request,stock_id):
    user_id=request.session.get("user_id")
    
    if not user_id:
        messages.error(request,"You need to login first")
        return redirect("plogin")

    stock= get_object_or_404(Portfolio,id=stock_id,user__user_id=user_id)
    stock.delete()
    messages.success(request,"Stock Deleted successfull")
    return redirect("portfolio")

def buy_sell(request):
    stock_data=None
    searched_symbol=None
    if request.method=="POST":
        searched_symbol=request.POST.get('stock_symbol')
        stock_data=get_stock_data(searched_symbol)
        if not stock_data:
            messages.error(request,"Stock not found or invalid symbol")        
    return render(request,"buy_sell.html",{'stock_data':stock_data,'searched_symbol':searched_symbol})

def get_stock_data(symbol):
    stock=yf.Ticker(symbol)
    periods={
        "1d":stock.history(period="1d"),
        "5d":stock.history(period="5d"),
        "10d":stock.history(period="10d"),
        "1y":stock.history(period="1y"),
    }
    
    if all(data.empty for data in periods.values()):
        return None
    
    stock_data={
        "current_price":periods["1d"]["Close"].iloc[-1] if not periods["1d"].empty else None,
        "high_price":periods["1d"]["High"].iloc[-1] if not periods["1d"].empty else None,
        "low_price":periods["1d"]["Low"].iloc[-1] if not periods["1d"].empty else None,
        "history":{}
    }
    for period,data in periods.items():
        if not data.empty:
            stock_data["history"][period]={
                "dates":data.index.strftime('%Y-%m-%d').tolist(),
                "prices":data["Close"].tolist()
            }
    return stock_data
    
def buy_stock(request):
    user_id=request.session.get("user_id")
    if not user_id:
        messages.error(request,"You need to login first!")
        return redirect("plogin")
    
    if request.method=="POST":
        symbol=request.POST.get("stock_symbol")
        quantity=int(request.POST.get("quantity"))
        stock_data=get_stock_data(symbol)
        if not stock_data:
            messages.error(request,"Invalid stock symbol.")
            return redirect("buy_sell")
        
        current_price=stock_data["current_price"]
        total_cost=quantity * current_price
        
        user_profile=UserProfile.objects.get(user_id=user_id)
        
        if quantity>0:
            if user_profile.points >= total_cost:
                portfolio,created=Portfolio.objects.get_or_create(
                    user=user_profile,stock_symbol=symbol,
                    defaults={"quantity":quantity,"purchase_price":current_price}
                )
                if not created:
                    total_quantity=portfolio.quantity + quantity
                    portfolio.purchase_price=((portfolio.purchase_price * portfolio.quantity) +  Decimal(str(current_price)) * quantity) / total_quantity
                    portfolio.quantity=total_quantity
                    portfolio.save()
                else:
                    portfolio.save()
                
                user_profile.points -= total_cost
                user_profile.save()
                
                Transaction.objects.create(
                    user=user_profile,
                    stock_name=symbol,
                    quantity=quantity,
                    price=current_price,
                    transaction_type="BUY"
                )
                messages.success(request,f"Bought {quantity} shares of {symbol} at {current_price}₹ each.")
            else:
                messages.error(request,"Insufficient balance to complete purchase.")
        else:
            messages.error(request,"Quantity must be greater than zero.")
    return redirect("buy_sell")

def sell_stock(request):
    user_id=request.session.get("user_id")
    if not user_id:
        messages.error(request,"You need to login first!")
        return redirect("plogin")
    
    if request.method=="POST":
        symbol=request.POST.get("stock_symbol")
        quantity=int(request.POST.get("quantity"))
        stock_data=get_stock_data(symbol)
        if not stock_data:
            messages.error(request,"Invalid stock symbol.")
            return redirect("buy_sell")
        
        current_price=stock_data["current_price"]
        total_earnings = quantity * current_price
        
        user_profile=UserProfile.objects.get(user_id=user_id)
        
        try:
            portfolio=Portfolio.objects.get(user=user_profile,stock_symbol=symbol)
            if quantity > 0 and portfolio.quantity >= quantity:
                portfolio.quantity -= quantity
                if portfolio.quantity==0:
                    portfolio.delete()
                else:
                    portfolio.save()
                
                user_profile.points += total_earnings
                user_profile.save()
                
                Transaction.objects.create(
                    user=user_profile,
                    stock_name=symbol,
                    quantity=quantity,
                    price=current_price,
                    transaction_type="SELL"
                )
                messages.success(request,f"Sold {quantity} shares of {symbol} at {current_price}₹ each.")
            else:
                messages.error(request, "Invalid quantity. You don't own that many shares.")
        except Portfolio.DoesNotExist:
            messages.error(request, "You do not own this stock.")
    return redirect("buy_sell")

def get_stock_chart_data(request):
    symbol = request.GET.get('symbol')
    range_period = request.GET.get('range', '1d')

    # Correct interval mapping for Yahoo Finance
    period_mapping = {
        '1d': '1d',
        '5d': '5d',
        '10d': '10d',
        '1y': '1y'
    }

    interval_mapping = {
        '1d': '5m',   # 5-minute candles for 1 day
        '5d': '15m',  # 15-minute candles for 5 days
        '10d': '1h',  # 1-hour candles for 10 days
        '1y': '1d'    # 1-day candles for 1 year
    }

    try:
        stock = yf.Ticker(symbol)

        # Fetch stock data with correct interval
        data = stock.history(period=period_mapping.get(range_period, '1d'), interval=interval_mapping.get(range_period, '1d'))

        if data.empty:
            return JsonResponse({"error": f"No data found for {symbol}."}, status=400)

        # Extract OHLC values
        dates = data.index.strftime('%Y-%m-%d %H:%M').tolist()
        open_prices = data['Open'].tolist()
        high_prices = data['High'].tolist()
        low_prices = data['Low'].tolist()
        close_prices = data['Close'].tolist()

        # Get Buy/Sell transaction markers
        user_id = request.session.get("user_id")
        trade_markers = []
        if user_id:
            user_profile = UserProfile.objects.get(user_id=user_id)
            transactions = Transaction.objects.filter(user=user_profile, stock_name=symbol).order_by('date')

            for txn in transactions:
                trade_markers.append({
                    "date": txn.date.strftime('%Y-%m-%d %H:%M'),
                    "price": txn.price,
                    "quantity": txn.quantity,
                    "type": txn.transaction_type
                })

        return JsonResponse({
            "dates": dates,
            "open": open_prices,
            "high": high_prices,
            "low": low_prices,
            "close": close_prices,
            "trade_markers": trade_markers
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
                
                
def transactions_history(request):
    user_id=request.session.get("user_id")
    
    if not user_id:
        messages.error(request,"You need to login first!")
        return redirect('plogin')
    user=UserProfile.objects.get(user_id=user_id)
    transactions = Transaction.objects.filter(user=user).order_by('-date')

    # Filters
    stock_name = request.GET.get('stock_name')
    transaction_type = request.GET.get('transaction_type')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    sort_by=request.session.get('sort_by','date')

    if stock_name:
        transactions = transactions.filter(stock_name__icontains=stock_name)
    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)
    if start_date:
        transactions = transactions.filter(date__date__gte=parse_date(start_date))
    if end_date:
        transactions = transactions.filter(date__date__lte=parse_date(end_date))
        
    #Sorting
    sort_options={
        'date':'-date',
        'price':'-price',
        'quantity':'-quantity',
        'type':'transaction_type',
    }
    transactions=transactions.order_by(sort_options.get(sort_by,'-date'))
    
    # Pagination (Showing 10 transaction per page)
    paginator=Paginator(transactions,10)
    page_number=request.GET.get('page')
    page_obj=paginator.get_page(page_number)
    
    return render(request, 'transactions_history.html', {
        'page_obj': page_obj,
        'stock_name': stock_name,
        'transaction_type': transaction_type,
        'start_date': start_date,
        'end_date': end_date,
        'sort_by': sort_by,
    })

def setting(request):
    user_id = request.session.get("user_id")

    if not user_id:
        messages.error(request, "You need to login first!")
        return redirect('plogin')

    return render(request, "setting.html")

def delete_account(request):
    user_id = request.session.get("user_id")

    if not user_id:
        messages.error(request, "You are not logged in.")
        return redirect("plogin")

    try:
        # Fetch user profile
        user_profile = UserProfile.objects.get(user_id=user_id)

        with transaction.atomic():
            # Delete all related data
            Portfolio.objects.filter(user=user_profile).delete()
            Transaction.objects.filter(user=user_profile).delete()
            user_profile.delete()  # Remove user from PostgreSQL

            # 🔥 Firebase Authentication Deletion (ONLY if user exists)
            try:
                auth.delete_user(user_id)
            except firebase_admin.auth.UserNotFoundError:
                print(f"DEBUG: Firebase user {user_id} not found, skipping deletion.")

        # Clear session
        request.session.flush()

        # Redirect to signup page with success message
        messages.success(request, "Your account has been permanently deleted from the system.")
        return redirect("psignup")

    except UserProfile.DoesNotExist:
        messages.error(request, "User profile not found.")
        return redirect("plogin")

    except Exception as e:
        messages.error(request, f"Error deleting account: {e}")
        return redirect("pdashboard")
    
def porfolio_history(request):
    user_id=request.session.get("user_id")
    
    if not user_id:
        return JsonResponse({"error":"User not logged in"},status=404)
    
    user_profile=UserProfile.objects.get(user_id=user_id)
    portfolios=Portfolio.objects.filter(user=user_profile)
    
    if not user_profile:
        return JsonResponse({"error":"No stock in portfolio"},status=404)
    
    portfolio_history={}
    
    for stock in portfolios:
        ticker=yf.Ticker(stock.stock_symbol)
        history=ticker.history(period='1mo')
        
        if not history.empty:
            for date, row in history.iterrows():
                date_str=date.strftime("%Y-%m-%d")
                price=Decimal(str(row["Close"]))
                stock_value= price * stock.quantity
                
                if date_str in portfolio_history:
                    portfolio_history[date_str]+= stock_value
                else:
                    portfolio_history[date_str] = stock_value
                    
    stored_dates=sorted(portfolio_history.keys())
    sorted_values=[float(portfolio_history[date]) for date in stored_dates]
    
    return JsonResponse({"dates":stored_dates,"values":sorted_values})


from .train_predict import train_and_predict

def stockprediction(request):
    return render(request, "stockprediction.html")

def get_stock_datas(request):
    if request.method == "GET":
        symbol = request.GET.get("symbol", "").upper()  # Get stock symbol from user input
        if not symbol:
            return JsonResponse({"error": "Stock symbol is required"}, status=400)
        
        try:
            # Fetch last 1 year of data (daily interval)
            stock = yf.Ticker(symbol)
            data = stock.history(period="1y", interval="1d")
            
            # Ensure data is not empty
            if data.empty:
                return JsonResponse({"error": "Invalid stock symbol or no data available"}, status=400)
            
            # Reset index to make Date a column
            data.reset_index(inplace=True)
            data["Date"] = data["Date"].dt.strftime("%d-%m-%Y")  # Format date
            
            # Convert DataFrame to JSON
            json_data = data[["Date", "Open", "High", "Low", "Close", "Volume"]].to_dict(orient="records")
            
            return JsonResponse({"stock_data": json_data})
        
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

def predict_stock(request):
    if request.method == "GET":
        symbol = request.GET.get("symbol", "").upper()
        if not symbol:
            return JsonResponse({"error": "Stock symbol is required"}, status=400)

        try:
            result = train_and_predict(symbol)
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
