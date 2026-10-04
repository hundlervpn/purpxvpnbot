"""Хендлеры: экраны и навигация повторяют референс @VPN_TelegramBot.

Меню — инлайн-кнопки на стартовом баннере (фото). ВСЯ навигация по кнопкам
перестраивает текущее сообщение на месте (у фото — подпись, у текста — текст),
чтобы не засорять чат новыми сообщениями; новое сообщение отправляется только
если старое отредактировать нельзя (например, старше 48 часов).
Все данные — заглушки из bot.stubs.
"""

import html
import logging

from aiogram import F, Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import CallbackQuery, FSInputFile, Message, ReplyKeyboardRemove

from . import keyboards as kb
from . import stubs

router = Router()
log = logging.getLogger(__name__)

# чаты, где уже убрали старую reply-панель (снятие достаточно одного раза)
kb_cleared: set[int] = set()
# file_id стартового баннера: после первой отправки Telegram отдаёт file_id,
# повторные отправки идут без перезагрузки файла
_photo_file_id: str | None = None


def _name(m: Message) -> str:
    return html.escape(m.from_user.first_name or "друг")


async def _send_menu_photo(message: Message, caption: str) -> Message:
    """Стартовый баннер + подпись + меню на нём."""
    global _photo_file_id
    photo = _photo_file_id or FSInputFile(stubs.START_PHOTO)
    msg = await message.answer_photo(photo, caption=caption, reply_markup=kb.main_menu(stubs.subscriptions_count()))
    if _photo_file_id is None and msg.photo:
        _photo_file_id = msg.photo[-1].file_id
    return msg


async def _edit_menu(message: Message, text: str, markup) -> Message:
    """Перестраивает сообщение на месте: у фото — подпись, у текста — текст.

    Если редактирование невозможно (сообщение старше 48 ч и т.п.) —
    отправляет экран новым сообщением.
    """
    try:
        if message.photo:
            return await message.edit_caption(caption=text, reply_markup=markup)
        return await message.edit_text(text=text, reply_markup=markup)
    except Exception as e:
        if "message is not modified" in str(e):
            return message
        log.info("edit failed (%s), sending new message", e)
    return await message.answer(text, reply_markup=markup)


async def send_menu(message: Message) -> Message:
    """Меню как в референсе; в первый раз заодно снимает залипшую reply-панель."""
    if message.chat.id not in kb_cleared:
        kb_cleared.add(message.chat.id)
        await message.answer(stubs.hello(_name(message)), reply_markup=ReplyKeyboardRemove())
        return await _send_menu_photo(message, stubs.MENU_TITLE)
    return await _send_menu_photo(message, stubs.greeting(_name(message)))


# --- /start и команды (нижняя панель «Меню», как в референсе) ---


@router.message(CommandStart(deep_link=True))
async def start_deeplink(message: Message, command: CommandObject):
    # payload вида ref123456: реферальный учёт подключим позже
    log.info("deep link payload: %s", command.args)
    await start(message)


@router.message(CommandStart())
async def start(message: Message):
    await send_menu(message)


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        stubs.help_text(message.from_user.first_name or "Друг"),
        reply_markup=kb.help_kb(),
    )


@router.message(Command("buy"))
async def cmd_buy(message: Message):
    await message.answer(stubs.BUY_SCREEN, reply_markup=kb.buy_screen(stubs.MY_SUBSCRIPTIONS))


@router.message(Command("offer"))
async def cmd_offer(message: Message):
    await message.answer(stubs.OFFER_TEXT, reply_markup=kb.main_only_kb())


# --- Разделы главного меню: всё перестраивает текущее сообщение ---


@router.callback_query(F.data == "buy")
async def cb_buy(cb: CallbackQuery):
    await _edit_menu(cb.message, stubs.BUY_SCREEN, kb.buy_screen(stubs.MY_SUBSCRIPTIONS))
    await cb.answer()


@router.callback_query(F.data == "subs")
async def cb_subs(cb: CallbackQuery):
    await _edit_menu(
        cb.message,
        f"{stubs.HEART} <b>Мои подписки</b>",
        kb.subs_list(stubs.MY_SUBSCRIPTIONS),
    )
    await cb.answer()


@router.callback_query(F.data == "ref")
async def cb_ref(cb: CallbackQuery):
    link = stubs.ref_link(cb.from_user.id)
    await _edit_menu(cb.message, stubs.REF_TEXT, kb.ref_kb(link))
    await cb.answer()


@router.callback_query(F.data == "help")
async def cb_help(cb: CallbackQuery):
    await _edit_menu(
        cb.message,
        stubs.help_text(cb.from_user.first_name or "Друг"),
        kb.help_kb(),
    )
    await cb.answer()


@router.callback_query(F.data == "no_work")
async def cb_no_work(cb: CallbackQuery):
    await _edit_menu(cb.message, stubs.NOT_WORKING_TEXT, kb.not_working_kb())
    await cb.answer()


@router.callback_query(F.data == "about")
async def cb_about(cb: CallbackQuery):
    await _edit_menu(cb.message, stubs.ABOUT_TEXT, kb.about_kb())
    await cb.answer()


@router.callback_query(F.data == "partner")
async def cb_partner(cb: CallbackQuery):
    await _edit_menu(cb.message, stubs.PARTNER_TEXT, kb.partner_kb())
    await cb.answer()


@router.callback_query(F.data == "partner_link")
async def cb_partner_link(cb: CallbackQuery):
    link = f"https://t.me/{stubs.BOT_USERNAME}?start=p{cb.from_user.id}"
    await _edit_menu(
        cb.message,
        f"{stubs.ce('link', '🔗')} Ваша партнерская ссылка:\n<code>{link}</code>",
        kb.back_and_menu("partner"),
    )
    await cb.answer()


# --- Воронка покупки: тоже на месте ---


@router.callback_query(F.data == "new_key")
async def cb_new_key(cb: CallbackQuery):
    await _edit_menu(
        cb.message,
        f"{stubs.TARIFF_INSTRUCTIONS}\n\n{stubs.TARIFFS_SCREEN}",
        kb.tariffs_kb(),
    )
    await cb.answer()


@router.callback_query(F.data.startswith("tar:"))
async def cb_tariff(cb: CallbackQuery):
    n = int(cb.data.split(":")[1])
    tariff = next(t for t in stubs.TARIFFS if t["n"] == n)
    await _edit_menu(cb.message, stubs.PAYMENT_SCREEN, kb.payment_kb(tariff["n"]))
    await cb.answer()


@router.callback_query(F.data.startswith("pay:"))
async def cb_pay(cb: CallbackQuery):
    _, tar_raw, mid_raw = cb.data.split(":")
    tariff = next(t for t in stubs.TARIFFS if t["n"] == int(tar_raw))
    method = next(m for m in stubs.PAY_METHODS if m["id"] == int(mid_raw))
    sub = stubs.issue_subscription(tariff)  # «оплата» — заглушка
    stubs.MY_SUBSCRIPTIONS.append(sub)
    await _edit_menu(
        cb.message,
        f"{stubs.ce('done', '✅')} <b>Оплата прошла</b> — {method['label']}, {tariff['price']} ₽\n\n"
        + stubs.sub_card(sub),
        kb.after_payment_kb(),
    )
    await cb.answer("Подписка выдана")


# --- Подписки ---


def _find_sub(sid: int):
    return next((s for s in stubs.MY_SUBSCRIPTIONS if s["id"] == sid), None)


@router.callback_query(F.data.startswith("sub:"))
async def cb_sub(cb: CallbackQuery):
    _, sid_raw, action = cb.data.split(":", 2)
    sub = _find_sub(int(sid_raw))
    if sub is None:
        await cb.answer("Подписка не найдена", show_alert=True)
        return
    if action == "open":
        await _edit_menu(cb.message, stubs.sub_card(sub), kb.sub_card_kb(sub))
    elif action == "connect":
        await _edit_menu(
            cb.message,
            f"{stubs.ce('key', '🔑')} Подключение:\n\n"
            f"1️⃣ {stubs.ce('mobile', '📱')} Открой клиент для своей платформы\n"
            f"2️⃣ {stubs.ce('link', '🔗')} Импортируй ссылку подписки:\n<code>{sub['link']}</code>\n"
            f"3️⃣ {stubs.ce('refresh', '🔄')} Нажми «Обновить» в клиенте\n\n"
            f"{stubs.ce('support', '🎧')} Вопросы — {stubs.SUPPORT_HANDLE}",
            kb.back_and_menu(f"sub:{sub['id']}:open"),
        )
    elif action == "devices":
        await _edit_menu(
            cb.message,
            f"{stubs.ce('mobile', '📱')} Устройства подписки №{sub['id']}:\n"
            f"• Активных 0 из {sub['max_devices']}",
            kb.back_and_menu(f"sub:{sub['id']}:open"),
        )
    elif action == "loc":
        await _edit_menu(
            cb.message,
            f"{stubs.ce('servers', '🌍')} Выбери локацию для №{sub['id']}:\n"
            "• 🇳🇱 Нидерланды (текущая)\n• 🇩🇪 Германия\n• 🇫🇮 Финляндия\n• 🇺🇸 США",
            kb.back_and_menu(f"sub:{sub['id']}:open"),
        )
    elif action == "proto":
        await _edit_menu(
            cb.message,
            f"{stubs.ce('shield', '🛡')} Протокол подписки №{sub['id']}: <b>{sub['protocol']}</b>\n"
            "Доступен также VMESS (скоро).",
            kb.back_and_menu(f"sub:{sub['id']}:open"),
        )
    elif action == "extend":
        # продление идёт через ту же воронку тарифов
        await _edit_menu(
            cb.message,
            f"{stubs.TARIFF_INSTRUCTIONS}\n\n{stubs.TARIFFS_SCREEN}",
            kb.tariffs_kb(),
        )
    await cb.answer()


# --- Главное меню ---


@router.callback_query(F.data == "main")
async def cb_main(cb: CallbackQuery):
    await _edit_menu(
        cb.message,
        stubs.greeting(cb.from_user.first_name or "друг"),
        kb.main_menu(stubs.subscriptions_count()),
    )
    await cb.answer()


# --- Fallback ---


@router.message()
async def fallback(message: Message):
    await send_menu(message)
