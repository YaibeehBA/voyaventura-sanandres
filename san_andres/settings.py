

from pathlib import Path
import os




# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

import environ

env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', default=False)

ALLOWED_HOSTS = [
    'voyaventura-san-andres.up.railway.app',
    'localhost',
    '127.0.0.1',
    '2015-186-42-22-126.ngrok-free.app',
    
]

CSRF_TRUSTED_ORIGINS = [
    'https://voyaventura-san-andres.up.railway.app',
    
]

# Application definition

INSTALLED_APPS = [
    'jazzmin',
    
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    # whitnoise añadido
    "whitenoise.runserver_nostatic",
    'django.contrib.staticfiles',
    # Aplicaciones personalizadas
    'alojamiento',
    'guias',
    'userauths',
    'user_dashboard',
    'reservacion',
  
    #aplicaciones de tercero
    'import_export',
    'crispy_forms',
    'ckeditor_uploader',
    'django_ckeditor_5',
    
   
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    
]


ROOT_URLCONF = 'san_andres.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'san_andres.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# if DEBUG:
#     DATABASES = {
#         'default': {
#             'ENGINE': 'django.db.backends.sqlite3',
#             'NAME': BASE_DIR / 'db.sqlite3',
#         }
#     }
# else:
DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': env("DB_NAME"),
            'USER': env("DB_USER"),
            'PASSWORD': env("DB_PASSWORD"),
            'HOST': env("DB_HOST"),
            'PORT': env("DB_PORT")
        }
    }

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'es-Es'

TIME_ZONE =  'America/Bogota'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)


STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR,'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR,'media')


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = "userauths.Usuario"



# platilla del administrador 

JAZZMIN_SETTINGS = {
    'site_header': "GAD SAN ANDRES",
    'site_brand': "Administrador",
    'site_logo': "logo.png",
    "logout_template_message": "Gracias por utilizar nuestro sitio web. ¡Esperamos verte de nuevo pronto!",
   
    
   
    'copyright':  "All Right Reserved 2023",
    "welcome_sign": "Bienvenido.",
    
    # "custom_links": {
    #     "apps": [
    #         {
    #             "name": "Dashboard",
    #             "url": "/admin/dashboard/",  # Cambia esto a una URL absoluta
    #             "icon": "fas fa-chart-line",
    #         },
    #     ]
    # },
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Dashboard", "url": "/admin/dashboard/", "permissions": ["auth.view_user"]},  # URL absoluta aquí también
       
    ],
        
    "order_with_respect_to": [
        
        

        
        "alojamiento",
        "alojamiento.Alojamiento",
        "alojamiento.GaleriaAlojamiento",
        "alojamiento.TipoAlojamiento",
        "alojamiento.Habitacion",
        "alojamiento.Reservacion",
       
       
        "guias.GuiaTuristico",
        "guias.Ruta",
        "guias.ReservacionRuta",
        
        
    ],
    
    "icons": {
        "admin.LogEntry": "fas fa-file",

        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",

        "userauths.Usuario": "fas fa-users",
        "userauths.MensajeUsuario":"fas fa-envelope",

        "alojamiento.Alojamiento": "fas fa-th",
        "alojamiento.GaleriaAlojamiento":"fas fa-calendar-week",
        "alojamiento.Reservacion":"fas fa-calendar-alt",
       
        "alojamiento.Habitacion":"fas fa-bed",
        "alojamiento.TipoAlojamiento":"fas fa-warehouse",
       
        "guias.GuiaTuristico":" fas fa-regular fa-id-card",
        "guias.Ruta":"fas fa-map",
        "guias.GuiaRuta":"fas  fa-mountain",
        "guias.ReservacionGuia":"fas fa-calendar-alt",

        
    },
    

    "show_ui_builder" : True,
   "custom_links": {
        "books": [{
            "name": "Dashboard Personalizado", 
            "url": "/admin/dashboard/", 
            "icon": "fas fa-tachometer-alt",
        }]
    },
}


JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": True,
    "brand_small_text": False,
    "brand_colour": "navbar-indigo",
    "accent": "accent-olive",
    "navbar": "navbar-indigo navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": False,
    "sidebar": "sidebar-dark-indigo",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "cyborg",
    "dark_mode_theme": "cyborg",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}




#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'# usar en desarrollo
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend' 
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')
EMAIL_SUBJECT_PREFIX = "Recuperación de contraseña"

# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp-mail.outlook.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'gadsanandres2024@outlook.es'
# EMAIL_HOST_PASSWORD = 'admin2024'
# EMAIL_SUBJECT_PREFIX = "Recuperación de contraseña"


# Stripe settings
STRIPE_PUBLIC_KEY = env('STRIPE_PUBLIC_KEY')
STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY')
DOMAIN = env('DOMAIN')



OPENAI_API_KEY = env('OPENAI_API_KEY')