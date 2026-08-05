from django.db import models
from datetime import date
# Create your models here.
class TrendingStock(models.Model):
    symbol = models.CharField(max_length=10, unique=True)  # Stock symbol (e.g., AAPL, TSLA)
    search_count = models.IntegerField(default=0)  # Number of times searched

    def __str__(self):
        return f"{self.symbol} - {self.search_count}"

# UserProfile to store Firebase users
class UserProfile(models.Model):
    user_id = models.CharField(max_length=255, unique=True)  # Firebase UID
    email = models.EmailField(unique=True)
    points = models.IntegerField(default=0)  # default 0, update on first login
    last_week_balance = models.DecimalField(max_digits=12, decimal_places=2, default=10000)
    last_month_balance = models.DecimalField(max_digits=12, decimal_places=2, default=10000)
    is_first_login = models.BooleanField(default=True)  # Track first login
    profile_picture = models.ImageField(upload_to='profile_pics', default='default_profile.jpg')

    def __str__(self):
        return self.email


class Portfolio(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    stock_symbol = models.CharField(max_length=20, default='UNKNOWN')
    quantity = models.IntegerField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateField(default=date.today)

    def __str__(self):
        return f"{self.user.email} - {self.stock_symbol}"


class Transaction(models.Model):  # ✅ FIXED: Corrected class name from "Transcation" to "Transaction"
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    stock_name = models.CharField(max_length=100)
    transaction_type = models.CharField(
        max_length=4,
        choices=[('BUY', 'Buy'), ('SELL', 'Sell')]
    )
    price = models.FloatField()
    quantity = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.stock_name} ({self.user.email})"


from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D,LSTM,Dense,Dropout,Flatten

# Create your models here.

def CNN_LSTM(input_shape):
    model = Sequential([
        # CNN Layer
        Conv1D(filters=64, kernel_size=3, activation="relu", input_shape=input_shape),

        # LSTM Layers (No Flatten layer to maintain 3D input)
        LSTM(units=50, return_sequences=True),
        Dropout(0.2),
        LSTM(units=50),

        # Fully Connected Layers
        Dense(units=25, activation="relu"),
        Dense(units=1)  # Output layer (predicts stock price)
    ])

    model.compile(optimizer="adam", loss="mean_squared_error")
    return model