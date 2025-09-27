Library Service (Django REST)

Онлайн-сервіс для керування бібліотекою: книги, користувачі, позики (borrowings), платежі (Stripe), прострочки та (опційно) нотифікації в Telegram. API самодокументований (Swagger), підтримує JWT-автентифікацію та фільтри.

🚀 Функціонал

Users: реєстрація, JWT токени, профіль /me

Books: CRUD із правами доступу (лише адмін може створювати/редагувати/видаляти)

Borrowings: створення позики (зменшує інвентар), список/деталі з фільтрами, повернення (збільшує інвентар, нарахування штрафу при прострочці)

Payments (Stripe): створення сесії оплати при позичанні, success/cancel ендпоїнти, список/деталі платежів

Fines: штраф за прострочку = days_overdue * daily_fee * FINE_MULTIPLIER

Docs: OpenAPI/Swagger за адресою /api/docs/

(Опційно): Нотифікації в Telegram про нові позики / прострочки

🧱 Технології

Backend: Django 5, DRF, django-filter, SimpleJWT, drf-spectacular

Payments: Stripe (test mode)

Infra (опц.): Docker, docker-compose, Postgres

Інше: python-dotenv, requests (Telegram)

📦 Структура
library_service/
├─ .env.sample
├─ requirements.txt
├─ docker-compose.yml
└─ backend/
   ├─ manage.py
   ├─ library/         # settings/urls/asgi/wsgi
   ├─ users/           # кастомний User + auth
   ├─ books/           # моделі/серіали/в’ю/urls
   ├─ borrowings/      # моделі/серіали/фільтри/в’ю/urls
   └─ payments/        # моделі/stripe utils/views/urls

⚙️ Встановлення та запуск (локально)

Python env

python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt


Сконфігуруй .env (скопіюй із .env.sample)

DJANGO_SECRET_KEY=change-me
DJANGO_DEBUG=1
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
# SQLite за замовчуванням (залиши DB_HOST порожнім)
# Для Postgres через Docker — заповни DB_HOST, DB_NAME, DB_USER, DB_PASSWORD

ACCESS_MINUTES=60
REFRESH_DAYS=1

API_TITLE=Library API
API_VERSION=1.0.0

# Stripe (TEST)
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_PUBLISHABLE_KEY=pk_test_xxx
FRONTEND_SUCCESS_URL=http://localhost:8000/api/payments/success/
FRONTEND_CANCEL_URL=http://localhost:8000/api/payments/cancel/

FINE_MULTIPLIER=2


Міграції та суперкористувач

cd backend
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser


Запуск

python manage.py runserver 0.0.0.0:8000


Swagger: http://localhost:8000/api/docs/

Schema (json): http://localhost:8000/api/schema/

🐳 Запуск у Docker (опціонально, Postgres)
docker compose up --build


API: http://localhost:8000/api/

Перевір або онови змінні БД у .env:

DB_NAME=library
DB_USER=library
DB_PASSWORD=library
DB_HOST=db
DB_PORT=5432

🔐 Автентифікація (JWT)

Реєстрація: POST /api/users/

{ "email": "a@a.com", "password": "12345", "first_name":"A", "last_name":"A" }


Отримати токени: POST /api/users/token/

{ "email": "a@a.com", "password": "12345" }


Відповідь: { "access": "...", "refresh": "..." }

Оновити: POST /api/users/token/refresh/

Мій профіль: GET/PUT/PATCH /api/users/me/

У приватні запити додавати заголовок:

Authorization: Bearer <ACCESS_TOKEN>

📚 Ендпоїнти
Users

POST /api/users/ — реєстрація

POST /api/users/token/ — отримати JWT

POST /api/users/token/refresh/ — оновити JWT

GET/PUT/PATCH /api/users/me/ — профіль поточного користувача

Books

GET /api/books/ — список (доступний усім, навіть без JWT)

GET /api/books/{id}/ — деталі (усім)

POST /api/books/ — створити (лише staff)

PUT/PATCH/DELETE /api/books/{id}/ — змінити/видалити (лише staff)

Borrowings

GET /api/borrowings/ — список

Не-адмін бачить лише свої

Параметри:

is_active=true|false

user_id=<id> (лише staff)

GET /api/borrowings/{id}/ — деталі

POST /api/borrowings/ — створити позику

Валідація: book.inventory > 0

Логіка: inventory -= 1, створюється Payment (PAYMENT) + Stripe Session

POST /api/borrowings/{id}/return/ — повернути

Заборонено повертати двічі

Логіка: inventory += 1

Якщо прострочено → створюється Payment (FINE) + Stripe Session

Payments

GET /api/payments/ — список платежів

Не-адмін бачить лише свої

GET /api/payments/{id}/ — деталі платежу

GET /api/payments/success/?session_id=... — відзначити як PAID (Stripe перенаправляє сюди)

GET /api/payments/cancel/ — інформує, що можна оплатити пізніше (сесія ~24h)

💳 Потік оплати (Stripe, TEST)

Користувач створює Borrowing → бекенд рахує ціну за дні (days * daily_fee) та створює Stripe Checkout Session.

У відповідь Borrowing “пов’язаний” із Payment (type=PAYMENT) і має session_url.

Користувач переходить за session_url, проводить тестову оплату карткою (наприклад, 4242 4242 4242 4242).

Після оплати Stripe перенаправить на /api/payments/success/?session_id=... → бекенд відмітить PAID.

При поверненні простроченої позики створюється Payment type=FINE з сумою:

money_to_pay = overdue_days * daily_fee * FINE_MULTIPLIER

🧪 Приклади curl
# Реєстрація
curl -X POST http://localhost:8000/api/users/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"12345"}'

# Токен
curl -X POST http://localhost:8000/api/users/token/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"12345"}'

# Книги (список)
curl http://localhost:8000/api/books/

# Створити позику (потрібен токен)
curl -X POST http://localhost:8000/api/borrowings/ \
  -H "Authorization: Bearer <ACCESS>" \
  -H "Content-Type: application/json" \
  -d '{"book": 1, "expected_return_date": "2025-10-05"}'

# Повернути позику
curl -X POST http://localhost:8000/api/borrowings/1/return/ \
  -H "Authorization: Bearer <ACCESS>"

🧰 Ролі та доступ

Anonymous:

GET /api/books/, GET /api/books/{id}/

Swagger / schema

User (JWT):

Свої Borrowings/Payments

Створення Borrowing

Повернення власних Borrowings

Staff:

CRUD Books

Перегляд Borrowings/Payments будь-якого користувача (user_id фільтр)

📝 Документація

Swagger UI: /api/docs/

OpenAPI schema: /api/schema/

Під час зміни/додавання ендпоїнтів — стеж, щоб схему можна було побудувати без помилок.

🧪 Тестування (рекомендації)

Набір інструментів у requirements.txt: pytest, pytest-django, pytest-cov

Ціль покриття для кастомної логіки: 60%+

Рекомендовані кейси:

Users: register/token/me

Books: list (public), create/update (staff only)

Borrowings:

create: inventory зменшується; заборона при inventory=0

list: user бачить лише свої; admin — усіх; фільтри is_active, user_id

return: захист від повторного; inventory збільшується; FINE при прострочці

Payments: list/detail власних платежів; success змінює статус на PAID

Запуск:

pytest --cov=backend --cov-report=term-missing

🔔 Telegram (опційно)

Заповни у .env:

TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...


І викликай хелпер notifications.telegram.send_message("text") з потрібних місць (створення Borrowing, успішний Payment, щоденна перевірка прострочених — якщо додаси Celery/Django-Q).

🧭 Workflows (рекомендації під завдання)

Гілка/PR на кожну задачу, осмислені назви гілок і комітів.

Для командної роботи увімкни обовʼязкові ревʼю перед мерджем (2 approvals).

Не зберігай секрети в гіті. Додай .env.sample і користуйся .env локально/на сервері.

📜 Ліцензія

MIT (або інша, за потреби проєкту).

Notes

Stripe використовуй лише в тестовому режимі.

Для продакшену додай Reverse Proxy (Nginx), HTTPS, безпечні кукі тощо.

Якщо підключатимеш фронтенд — увімкни CORS у settings.py (вже додано) та додай CSRF_TRUSTED_ORIGINS за потреби.
