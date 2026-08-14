import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

load_dotenv()

# ================= BASE DIR =================
BASE_DIR = Path(__file__).resolve().parent.parent

# ================= SECURITY =================
# SECRET_KEY = "django-insecure-change-this-secret-key"
# DEBUG = True
# ALLOWED_HOSTS = ["127.0.0.1", "localhost", "192.168.29.249"]


SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-local-development-key-change-this"
)

DEBUG = os.environ.get("DEBUG", "True") == "True"

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get(
        "ALLOWED_HOSTS",
        "127.0.0.1,localhost"
    ).split(",")
    if host.strip()
]

# ================= INSTALLED APPS =================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core",             # ✅ MUST BE ACTIVE
    "franchise",        # Handles the 'Wall' logic
    "portal",
    "management_portal.apps.ManagementPortalConfig", # Your revived business logic
    "student_portal.apps.StudentPortalConfig",
    "website_portal.apps.WebsitePortalConfig",
    'simple_history',
    'corsheaders',
]
STATIC_URL = '/static/'
# ================= MIDDLEWARE =================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    'corsheaders.middleware.CorsMiddleware',
    # 1. Multi-tenant logic first
    "core.middleware.TenantMiddleware", 
    
    # 2. History logic LAST (to capture the authenticated user)
    'simple_history.middleware.HistoryRequestMiddleware',
    "management_portal.middleware.NoticeSchedulerMiddleware",
]

# ================= URL CONFIG =================
ROOT_URLCONF = "institute.urls"

# ================= TEMPLATES =================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ================= WSGI =================
WSGI_APPLICATION = "institute.wsgi.application"



DATABASES = {
    "default": dj_database_url.parse(
        os.environ.get("DATABASE_URL", "sqlite:///db.sqlite3")
    )
}



# ================= PASSWORD VALIDATION =================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ================= LANGUAGE & TIMEZONE =================
LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Kolkata"

USE_I18N = True
USE_TZ = True

# ================= STATIC FILES =================
STATIC_URL = "/static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
# ================= MEDIA FILES =================
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ================= DEFAULT AUTO FIELD =================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# # ================= TWILIO =================
# TWILIO_ACCOUNT_SID = "ACxxxxxxxxxxxxxxxxxxxx"
# TWILIO_AUTH_TOKEN = "your_auth_token"
# TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"   # NO COMMA

# ================= EMAIL (FOR OTP) =================
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# Gmail App Password


EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")


# DEFAULT_FROM_EMAIL = EMAIL_HOST_USER   # 🔥 add this
DEFAULT_FROM_EMAIL = "Smart Computer Institute (No Reply) <smartcomputerins2022@gmail.com>"
EMAIL_TIMEOUT = 30  # Stop waiting after 10 seconds
EMAIL_USE_SSL = False # Use TLS (already set to True)

# ================= LOGIN SETTINGS =================
LOGIN_URL = '/admin/login/'
LOGIN_REDIRECT_URL = '/admin/'
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
]