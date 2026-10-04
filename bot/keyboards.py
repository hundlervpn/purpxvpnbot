"""Клавиатуры — ряды повторяют референс @VPN_TelegramBot (снято 03.10.2026).

Брендинг PURPX: на каждой кнопке кастомная фиолетовая иконка из пака
https://t.me/addemoji/purpxvpn (Bot API 9.4+ `icon_custom_emoji_id`, работает,
когда у владельца бота Telegram Premium). В тексте кнопки эмодзи не дублируем —
иконка рисуется слева от надписи клиентом. Стиль style='primary' красит кнопку
в акцентный цвет темы клиента, 'success' — зелёный.

Колбэки: buy | subs | sub:<id>:open|extend|connect|devices|loc|proto |
new_key | tar:<n> | pay:<tar>:<mid> | ref | help | no_work | about |
partner | partner_link | main
"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from . import stubs

PRIMARY = "primary"    # акцентный (фиолетовый при фиолетовой теме клиента)
SUCCESS = "success"    # подтверждение действия


def btn(text: str, icon: str | None = None, **kwargs) -> InlineKeyboardButton:
    """Кнопка с иконкой из пака PURPX (если ID доступен)."""
    return InlineKeyboardButton(
        text=text,
        icon_custom_emoji_id=stubs._PACK_IDS.get(icon) if icon else None,
        **kwargs,
    )


def main_menu(subs_count: int) -> InlineKeyboardMarkup:
    rows = [
        [btn("Купить подписку", "buy", callback_data="buy", style=PRIMARY)],
        [btn(f"Мои подписки ({subs_count})", "key", callback_data="subs")],
        [
            btn("Пригласить", "referral", callback_data="ref"),
            btn("Помощь", "question", callback_data="help"),
        ],
        [
            btn(f"Всё о {stubs.BRAND}", "info", callback_data="about"),
            btn("Поддержка", "support", url=stubs.SUPPORT_URL),
        ],
        [btn("Партнерская программа", "money", callback_data="partner")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def buy_screen(subs: list[dict]) -> InlineKeyboardMarkup:
    rows = [
        [btn(stubs.sub_label(s), "key", callback_data=f"sub:{s['id']}:extend")]
        for s in subs
    ]
    rows.append([btn("Создать новую подписку", "plus", callback_data="new_key", style=PRIMARY)])
    rows.append([btn("Главное меню", "home", callback_data="main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def tariffs_kb() -> InlineKeyboardMarkup:
    rows = [
        [btn(t["label"], "calendar", callback_data=f"tar:{t['n']}")]
        for t in stubs.TARIFFS
    ]
    rows.append([btn("Назад", "back", callback_data="buy")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def payment_kb(tariff_n: int) -> InlineKeyboardMarkup:
    rows = [
        [btn(m["label"], m.get("icon"), callback_data=f"pay:{tariff_n}:{m['id']}", style=PRIMARY)]
        for m in stubs.PAY_METHODS
    ]
    rows.append([btn("Назад", "back", callback_data="buy")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def subs_list(subs: list[dict]) -> InlineKeyboardMarkup:
    rows = [
        [btn(stubs.sub_label(s), "key", callback_data=f"sub:{s['id']}:open")]
        for s in subs
    ]
    rows.append([btn("Купить ещё", "buy", callback_data="buy")])
    rows.append([btn("Главное меню", "home", callback_data="main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def sub_card_kb(sub: dict) -> InlineKeyboardMarkup:
    sid = sub["id"]
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn("Подключить", "connect", callback_data=f"sub:{sid}:connect", style=SUCCESS)],
        [
            btn("Мои устройства", "mobile", callback_data=f"sub:{sid}:devices"),
            btn("Продлить", "refresh", callback_data=f"sub:{sid}:extend", style=PRIMARY),
        ],
        [
            btn("Добавить локацию", "servers", callback_data=f"sub:{sid}:loc"),
            btn("Изменить протокол", "settings", callback_data=f"sub:{sid}:proto"),
        ],
        [btn("Поделиться", "share", url=stubs.share_url(sub["link"]))],
        [btn("Назад", "back", callback_data="subs")],
    ])


def ref_kb(link: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn("Поделиться", "share", url=stubs.share_url(link), style=PRIMARY)],
        [btn("Главное меню", "home", callback_data="main")],
    ])


def help_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn("Не работает VPN", "warning", callback_data="no_work")],
        [btn("Связаться с поддержкой", "support", url=stubs.SUPPORT_URL)],
        [btn("Главное меню", "home", callback_data="main")],
    ])


def not_working_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn("Связаться с поддержкой", "support", url=stubs.SUPPORT_URL)],
        [btn("Главное меню", "home", callback_data="main")],
    ])


def about_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn("Купить подписку", "buy", callback_data="buy", style=PRIMARY)],
        [btn("Главное меню", "home", callback_data="main")],
    ])


def partner_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn("Создать партнерскую ссылку", "link", callback_data="partner_link", style=PRIMARY)],
        [btn("Главное меню", "home", callback_data="main")],
    ])


def after_payment_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn("Мои подписки", "key", callback_data="subs")],
        [btn("Главное меню", "home", callback_data="main")],
    ])


def back_and_menu(back_cb: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn("Назад", "back", callback_data=back_cb)],
        [btn("Главное меню", "home", callback_data="main")],
    ])


def main_only_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn("Главное меню", "home", callback_data="main")],
    ])
