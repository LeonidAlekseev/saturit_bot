import os
import json
import logging
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import Window, Dialog, DialogRegistry, DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Url, Button, Back, SwitchTo, Cancel, Row
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import MessageInput
from aiogram import types
import os


with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'parameters.json'), 'r', encoding='utf-8') as infile:
    parameters = json.load(infile)
    QUESTIONS = parameters['QUESTIONS']
    ANSWERS = parameters['ANSWERS']
    GEOS = parameters['GEOS']
    FORMULAS = parameters['FORMULAS']
    ADMINS = parameters['ADMINS']


logging.basicConfig(level=logging.INFO)
bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))
storage = MemoryStorage()
dispatcher = Dispatcher(bot, storage=storage)
registry = DialogRegistry(dispatcher)


class AppSG(StatesGroup):
    menu = State()
    maintenance_0 = State()
    # maintenance_1 = State()
    # maintenance_2 = State()
    installation_0 = State()
    installation_1 = State()
    installation_2 = State()
    installation_3 = State()
    installation_4 = State()
    installation_5 = State()
    installation_6 = State()
    installation_7 = State()
    registration_1 = State()


@dispatcher.message_handler(commands=["start"])
async def start(message: Message, dialog_manager: DialogManager):
    with open('images/description.jpeg', 'rb') as img:
        await message.answer_photo(img, caption='Вас приветсвует буровая компания «САТУРИТ». Бурим более 18 лет. Более 2000 скважин в Московской области.\n\nПробурим для вас быстро, качественно, с гарантией. Звоните +79037258536, наверняка мы уже бурили рядом с вами!\n\nДля расчета стоимости скважины на Вашем участке нажмите /menu или выберите данную комаду в левом нижнем меню.')

@dispatcher.message_handler(commands=["menu"])
async def menu(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(AppSG.menu, mode=StartMode.RESET_STACK)
    dialog_manager.current_context().dialog_data['chat_id'] = message.chat.id

async def report_admin(message_title: str, questions: list, dialog_manager: DialogManager, **kwargs):
    answers = dialog_manager.current_context().dialog_data
    message_text = message_title + '\n\n'
    for question in questions:
        if question in answers:
            answer = str(answers[question])
        else:
            answer = '-'
        if question in QUESTIONS:
            message_text += QUESTIONS[question]
        else:
            message_text += question
        message_text += '\n'
        if answer in ANSWERS:
            message_text += ANSWERS[answer]
        else:
            message_text += answer
        message_text += '\n'
    for admin in ADMINS:
        try:
            await bot.send_message(chat_id=admin, text=message_text)
        except:
            pass


async def start_survey(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    if 'menu_0_1' == callback.data:
        await dialog_manager.dialog().switch_to(AppSG.installation_0)
    elif 'menu_0_2' == callback.data:
        await dialog_manager.dialog().switch_to(AppSG.maintenance_0)

async def installation_0(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    dialog_manager.current_context().dialog_data['installation_0'] = callback.data
    await dialog_manager.dialog().switch_to(AppSG.installation_1)

async def installation_1(message: Message, dialog: Dialog, dialog_manager: DialogManager):
    dialog_manager.current_context().dialog_data['installation_1'] = message.text
    await dialog_manager.dialog().switch_to(AppSG.installation_2)

async def installation_2(message: Message, dialog: Dialog, dialog_manager: DialogManager):
    dialog_manager.current_context().dialog_data['installation_2'] = (message.location['latitude'], message.location['longitude'],)
    await dialog_manager.dialog().switch_to(AppSG.installation_3)

async def installation_3(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    dialog_manager.current_context().dialog_data['installation_3'] = callback.data
    await dialog_manager.dialog().switch_to(AppSG.installation_4)

async def installation_4(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    dialog_manager.current_context().dialog_data['installation_4'] = callback.data
    await dialog_manager.dialog().switch_to(AppSG.installation_5)

async def installation_5(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    dialog_manager.current_context().dialog_data['installation_5'] = callback.data
    if callback.data == 'installation_5_1':
        await dialog_manager.dialog().switch_to(AppSG.installation_6)
    else:
        await dialog_manager.dialog().switch_to(AppSG.installation_7)

async def installation_6(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    dialog_manager.current_context().dialog_data['installation_6'] = callback.data
    await dialog_manager.dialog().switch_to(AppSG.installation_7)

def get_best_geo_depth(user_geo):
    best_dist, depth = None, None
    for current_geo in GEOS:
        current_dist = ( ( current_geo[0] - user_geo[0] )**2 + ( current_geo[1] - user_geo[1] )**2 )**0.5
        if not best_dist or best_dist > current_dist:
            best_dist = current_dist
            depth = current_geo[-1]
    return depth

def get_installation_cost(answers, depth):
    formula = ' '.join([FORMULAS[answer] for question, answer in answers.items() if answer in FORMULAS])
    cost = eval(formula)
    return cost

async def get_installation_7(dialog_manager: DialogManager, **kwargs):
    answers = dialog_manager.current_context().dialog_data
    name = answers['installation_1']
    user_geo = answers['installation_2']
    depth = get_best_geo_depth(user_geo)
    cost = get_installation_cost(answers, depth)
    dialog_manager.current_context().dialog_data['cost'] = cost
    await report_admin('🟡 Клиент завершил опрос', 
        ['chat_id', 'cost', 'installation_1', 'installation_2', 'installation_3', 'installation_4', 'installation_5', 'installation_6'], 
        dialog_manager)
    return {'name': name, 'cost': cost}


async def start_registration(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager_done(dialog_manager, is_message=False)
    await dialog_manager.start(AppSG.registration_1, mode=StartMode.RESET_STACK)
    dialog_manager.current_context().dialog_data['chat_id'] = callback.message.chat.id

async def registration_1(message: Message, dialog: Dialog, dialog_manager: DialogManager):
    dialog_manager.current_context().dialog_data['registration_1'] = message.text
    await report_admin('🟢 Клиент оставил номер', 
        ['chat_id', 'registration_1'], 
        dialog_manager)
    await message.answer("Ваш номер успешно записан! В ближайшее время мы свяжется с вами.")
    await dialog_manager_done(dialog_manager)


async def close_dialog(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, is_message=True):
    await dialog_manager_done(dialog_manager, is_message)

async def dialog_manager_done(dialog_manager: DialogManager, is_message=True):
    if is_message:
        await bot.send_message(
            chat_id=dialog_manager.current_context().dialog_data['chat_id'], 
            text='Для повторного использования Telegram-бота нажмите /menu или выберите данную комаду в левом нижнем меню.')
    await dialog_manager.done()
    


app_dialog = Dialog(
    Window(
        Const("Пожалуйста, выберите причину обращения к нам."),
        Button(Const("⛏ Бурение скважины"), id="menu_0_1", on_click=start_survey),
        # Button(Const("🔧 Обслуживание оборудования"), id="menu_0_2", on_click=start_survey),
        Url(Const("📱 +7 (903) 725-85-36"), Const('https://t.me/+79037258536')),
        Button(Const("📲 Перезвоните мне"), id="menu_0_3", on_click=start_registration),
        Cancel(Const("🔚 Закрыть меню")),
        state=AppSG.menu,
    ),
    Window(
        Const("Для консультации по обслуживанию оборужования звоните или пишите в Telegram по номеру телефона."),
        Url(Const("📱 +7 (903) 725-85-36"), Const('https://t.me/+79037258536')),
        Button(Const("📲 Перезвоните мне"), id="maintenance_0_1", on_click=start_registration),
        # Button(Const("▶️ Начать опрос"), id="maintenance_0_1", on_click=maintenance_0),
        SwitchTo(Const("🔙 Вернуться назад"), id="maintenance_0_2", state=AppSG.menu),
        state=AppSG.maintenance_0,
    ),
    Window(
        Const("Для того, чтобы мы могли лучше понять ваши потребности, пожалуйста, пройдите опрос."),
        Button(Const("▶️ Начать опрос"), id="installation_0_1", on_click=installation_0),
        SwitchTo(Const("🔙 Вернуться назад"), id="installation_0_2", state=AppSG.menu),
        state=AppSG.installation_0,
    ),
    Window(
        Const(QUESTIONS['installation_1']),
        MessageInput(installation_1),
        state=AppSG.installation_1,
    ),
    Window(
        Const(QUESTIONS['installation_2'] + '\n\n' + QUESTIONS['installation_2_instruction']),
        MessageInput(installation_2, content_types=types.ContentTypes.LOCATION),
        Back(Const("🔙 Вернуться назад")),
        state=AppSG.installation_2,
    ),
    Window(
        Const(QUESTIONS['installation_3']),
        Button(Const("1️⃣ " + ANSWERS['installation_3_1']), id="installation_3_1", on_click=installation_3),
        Button(Const("2️⃣ " + ANSWERS['installation_3_2']), id="installation_3_2", on_click=installation_3),
        Button(Const("3️⃣ " + ANSWERS['installation_3_3']), id="installation_3_3", on_click=installation_3),
        Button(Const("4️⃣ " + ANSWERS['installation_3_4']), id="installation_3_4", on_click=installation_3),
        Back(Const("🔙 Вернуться назад")),
        state=AppSG.installation_3,
    ),
    Window(
        Const(QUESTIONS['installation_4']),
        Button(Const("1️⃣ " + ANSWERS['installation_4_1']), id="installation_4_1", on_click=installation_4),
        Button(Const("2️⃣ " + ANSWERS['installation_4_2']), id="installation_4_2", on_click=installation_4),
        Back(Const("🔙 Вернуться назад")),
        state=AppSG.installation_4,
    ),
    Window(
        Const(QUESTIONS['installation_5']),
        Button(Const("1️⃣ " + ANSWERS['installation_5_1']), id="installation_5_1", on_click=installation_5),
        Button(Const("2️⃣ " + ANSWERS['installation_5_2']), id="installation_5_2", on_click=installation_5),
        Back(Const("🔙 Вернуться назад")),
        state=AppSG.installation_5,
    ),
    Window(
        Const(QUESTIONS['installation_6']),
        Button(Const("1️⃣ " + ANSWERS['installation_6_1']), id="installation_6_1", on_click=installation_6),
        Button(Const("2️⃣ " + ANSWERS['installation_6_2']), id="installation_6_2", on_click=installation_6),
        Back(Const("🔙 Вернуться назад")),
        state=AppSG.installation_6,
    ),
    Window(
        Format("{name}, без учета скидки и специальных предложений ваша скважина под ключ будет стоить {cost} рублей. Вы можете оставить номер телефона или самостоятельно связаться с нами в Telegram по номеру телефона."),
        Url(Const("📱 +7 (903) 725-85-36"), Const('https://t.me/+79037258536')),
        Button(Const("📲 Перезвоните мне"), id="installation_7_1", on_click=start_registration),
        Button(Const("🔚 Закрыть диалог"), id="installation_7_2", on_click=close_dialog),
        state=AppSG.installation_7,
        getter=get_installation_7,
    ),
    Window(
        Const(QUESTIONS['registration_1']),
        Button(Const("🔚 Закрыть диалог"), id="installation_7_2", on_click=close_dialog),
        MessageInput(registration_1),
        state=AppSG.registration_1,
    ),
)
registry.register(app_dialog)


if __name__ == '__main__':
    executor.start_polling(dispatcher, skip_updates=True)
