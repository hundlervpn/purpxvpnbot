"""Заглушки (моки) данных сервиса.

Всё, что здесь находится — фейковые данные для скелета бота.
При подключении реальной панели (БД, биллинг, VPN-ноды) заменить обращения
к этому модулю на реальные источники данных.

Структура экранов и колбэки повторяют референс @VPN_TelegramBot (снято 03.10.2026).
Брендинг PURPX: фиолетовый, эмодзи — кастомные из пака
https://t.me/addemoji/purpxvpn (Bot API 9.4+: кастомные эмодзи разрешены ботам,
у владельца которых Telegram Premium; у текущего владельца он есть — проверено).
"""

import json
import os
import random
import uuid
from datetime import date, timedelta

BRAND = "PURPX"
BOT_USERNAME = "Purpxvpnbot"  # перезаписывается из get_me() при старте

# --- Кастомные эмодзи пака PURPX -------------------------------------------
# name -> custom_emoji_id (см. emoji/pack/pack_emoji_ids.json).
# Можно выключить: CUSTOM_EMOJI=0 в .env (тогда везде fallback-юникод).
_EMOJI_IDS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "emoji", "pack", "pack_emoji_ids.json",
)
try:
    with open(_EMOJI_IDS_PATH) as _f:
        _PACK_IDS: dict[str, str] = json.load(_f)
except OSError:
    _PACK_IDS = {}

CUSTOM_EMOJI = os.getenv("CUSTOM_EMOJI", "1") == "1" and bool(_PACK_IDS)


def ce(name: str, fallback: str) -> str:
    """Кастомный эмодзи пака в HTML-тексте; без пака/Premium — юникод-fallback."""
    if CUSTOM_EMOJI and name in _PACK_IDS:
        return f'<tg-emoji emoji-id="{_PACK_IDS[name]}">{fallback}</tg-emoji>'
    return fallback


# Фирменный акцент (фиолетовая звезда из пака)
HEART = ce("star", "💜")

# Заглушки ссылок — заменить на реальные
SUPPORT_URL = "https://t.me/purpxsupp"   # служба поддержки
SUPPORT_HANDLE = "@purpxsupp"
DOMAIN = "purpx.example"                      # домен ключей-заглушек

# Тарифы (заглушки): id, название, цена, скидка
TARIFFS = [
    {"n": 1, "label": "1 мес — 199 ₽", "months": 1, "price": 199},
    {"n": 2, "label": "3 мес — 499 ₽ (-16%)", "months": 3, "price": 499},
    {"n": 3, "label": "6 мес — 899 ₽ (-25%)", "months": 6, "price": 899},
    {"n": 4, "label": "12 мес — 1499 ₽ (-37%)", "months": 12, "price": 1499},
]

# Способы оплаты (как в референсе); иконки подставляются в keyboards по id
PAY_METHODS = [
    {"id": 8, "label": "СБП (без автосписания)", "icon": "wallet"},
    {"id": 11, "label": "Оплата картой (без автосписания)", "icon": "buy"},
    {"id": 1, "label": "Telegram Stars", "icon": "star"},
    {"id": 12, "label": "Crypto Pay", "icon": "money"},
]

# Подписки пользователя (заглушка: ровно одна)
_SUB_LINK_HASH = uuid.uuid4().hex
MY_SUBSCRIPTIONS = [
    {
        "id": 229458,
        "protocol": "VLESS",
        "devices": 1,
        "max_devices": 1,
        "expires": date.today() + timedelta(days=1),
        "link": f"https://{DOMAIN}/sub/{_SUB_LINK_HASH}",
        "country": "🇳🇱 Нидерланды",
    },
]


def next_sub_id() -> int:
    return MY_SUBSCRIPTIONS[-1]["id"] + 1 if MY_SUBSCRIPTIONS else 229458


def sub_label(sub: dict) -> str:
    return (f"№{sub['id']} · {sub['protocol']} · до {sub['expires'].strftime('%d.%m')} · "
            f"{sub['devices']}/{sub['max_devices']} устр.")


def sub_card(sub: dict) -> str:
    return (
        f"{ce('info', 'ℹ️')} ID: <b>{sub['id']}</b>\n"
        f"{ce('mobile', '📱')} Устройств: <b>{sub['devices']} / {sub['max_devices']}</b>\n"
        f"{ce('shield', '🛡')} Протокол: <b>{sub['protocol']}</b>\n"
        f"{ce('clock', '🕐')} Подписка до: <b>{sub['expires'].strftime('%d.%m.%Y')}</b>\n\n"
        f"{ce('link', '🔗')} Ссылка для подключения:\n<code>{sub['link']}</code>"
    )


def issue_subscription(tariff: dict) -> dict:
    """«Покупка»: карточка новой подписки (в реальности — запись в панели)."""
    months = tariff["months"]
    sub = {
        "id": next_sub_id(),
        "protocol": "VLESS",
        "devices": 1,
        "max_devices": 1,
        "expires": date.today() + timedelta(days=30 * months),
        "link": f"https://{DOMAIN}/sub/{uuid.uuid4().hex}",
        "country": "🇳🇱 Нидерланды",
    }
    return sub


def subscriptions_count() -> int:
    return len(MY_SUBSCRIPTIONS)


def ref_link(user_id: int) -> str:
    return f"https://t.me/{BOT_USERNAME}?start=ref{user_id}"


def share_url(url: str, text: str = "") -> str:
    from urllib.parse import quote
    q = f"&text={quote(text)}" if text else ""
    return f"https://t.me/share/url?url={quote(url)}{q}"


# Тексты (структура из референса, брендинг PURPX + эмодзи пака)

START_PHOTO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "start_banner.png")


def hello(name: str) -> str:
    return f"Привет, {name} {ce('star', '💜')}"


MENU_TITLE = f"{ce('home', '🏠')} Главное меню"


def greeting(name: str) -> str:
    return f"{hello(name)}\n\n{MENU_TITLE}"


BUY_SCREEN = (
    f"{ce('buy', '💳')} <b>Выберите подписку или ключ для продления.\n"
    "Если у вас ещё нет подписки — создайте новую</b> 👇"
)

TARIFF_INSTRUCTIONS = (
    f"{ce('key', '🔑')} Подключение за 3 шага:\n\n"
    "1️⃣ Выберите необходимый тариф\n"
    "2️⃣ Внесите платеж\n"
    "3️⃣ Получите подписку с простой инструкцией для Вашего устройства\n\n"
    f"{ce('support', '🎧')} Не стесняйтесь обращаться к {SUPPORT_HANDLE} за помощью."
)

TARIFFS_SCREEN = f"{ce('calendar', '📅')} Выберите нужный тариф 👇"

PAYMENT_SCREEN = f"{ce('wallet', '👛')} Выберите способ оплаты 👇"

REF_TEXT = (
    f"{ce('gift', '🎁')} А Вы знали, что VPN можно продлевать бесплатно?\n\n"
    "Приглашайте друзей и получайте <b>+7 дней</b> к подписке за каждого "
    "приглашённого друга.\n\n"
    f"{ce('link', '🔗')} Ваша персональная ссылка — ниже."
)

def help_text(name: str) -> str:
    return f"{name}, выбери необходимый пункт меню 👇"

NOT_WORKING_TEXT = (
    f"{ce('warning', '⚠️')} <b>VPN не работает или интернет не грузит?</b>\n\n"
    f"{ce('refresh', '🔄')} <b>ОБНОВИТЕ ПОДПИСКУ</b> — нажмите на значок обновления в приложении. "
    "VPN должен быть выключен в момент обновления.\n\n"
    f"{ce('bolt', '⚡')} <b>Проверьте ПИНГ</b> — нажмите на значок спидометра. Пинг показывает "
    "задержку соединения в мс. Чем меньше число — тем быстрее отклик VPN.\n\n"
    f"{ce('servers', '🌍')} Если пинга нет или указано «Н/д» — попробуйте другую локацию.\n\n"
    f"{ce('support', '🎧')} <b>Не помогло?</b> Напишите в поддержку: {SUPPORT_HANDLE}"
)

ABOUT_TEXT = (
    f"{HEART} <b>{BRAND}</b> — сервис, который делает интернет свободным: "
    "без границ, слежки и ограничений.\n\n"
    f"{ce('shield', '🛡')} Мы <b>не храним логи</b> и не передаём данные третьим лицам — "
    "твоя активность остаётся только твоей.\n\n"
    f"{ce('bolt', '⚡')} Собственная сеть серверов в нескольких странах с каналами "
    "<b>до 10 Гбит/с</b>: смотри, играй и работай без потери скорости.\n\n"
    f"{ce('mobile', '📱')} Одна подписка — <b>до 3 устройств</b> одновременно: Windows, macOS, "
    "Linux, Android, iOS."
)

OFFER_TEXT = (
    f"{ce('info', 'ℹ️')} <b>Оферта</b>\n\n"
    f"Настоящая оферта описывает условия использования сервиса <b>{BRAND}</b>:\n\n"
    f"{ce('key', '🔑')} Подписка предоставляет доступ к VPN-серверам сервиса на оплаченный срок.\n\n"
    f"{ce('mobile', '📱')} Подписка привязана к аккаунту и используется на указанном числе устройств.\n\n"
    f"{ce('money', '💵')} Возврат средств возможен в течение 7 дней с момента оплаты, "
    "если ключ подключения не был активирован.\n\n"
    f"{ce('disconnect', '🚫')} Сервис не предназначен для противоправной деятельности.\n\n"
    "Полная версия оферты публикуется на сайте проекта."
)

PARTNER_TEXT = (
    f"{ce('money', '💵')} Здравствуйте! Если у Вас есть возможность привлекать клиентов, "
    "мы предлагаем Вам заработать:\n\n"
    f"Нажмите кнопку <b>{ce('link', '🔗')} Создать партнерскую ссылку</b>, и бот создаст "
    "для Вас ссылку для заработка!\n"
    f"{ce('money', '💵')} Мы выплачиваем <b>20% за продажу и продления</b> ключей с выводом "
    "от <b>2500₽</b>!"
)
