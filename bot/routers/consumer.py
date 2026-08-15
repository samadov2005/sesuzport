from aiogram import Router, F
from aiogram.types import Message
from bot.keyboards.consumer import consumer_keyboard
from bot.services.user_service import update_user_role

router = Router(name='consumer_router')

@router.message(F.text == "👤 Iste'molchi (Mijoz)")
async def role_consumer(message: Message):
    await update_user_role(message.from_user.id, 'CONSUMER')
    await message.answer(
        "Iste'molchi menyusi. Atrofingizdagi do'konlarni tekshiring, buzilishlar haqida murojaat yuboring va keshbeklaringizni kuzating.",
        reply_markup=consumer_keyboard()
    )
