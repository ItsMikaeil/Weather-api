# Limiter خود SlowAPI را وارد می‌کنیم.
from slowapi import Limiter

# این تابع IP واقعی Client را به عنوان کلید Rate Limit برمی‌گرداند.
from slowapi.util import get_remote_address


# برای هر IP یک شمارنده‌ی جداگانه خواهیم داشت.
# مثلاً:
# 192.168.1.10 → محدودیت خودش
# 192.168.1.20 → محدودیت خودش
limiter = Limiter(key_func=get_remote_address)