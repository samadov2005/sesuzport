from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from bot.keyboards.common import rights_list_keyboard
from bot.services.user_service import get_user_language
from asgiref.sync import sync_to_async
from apps.rights.models import ConsumerRight

router = Router(name='rights_router')

@router.message(F.text.in_(["⚖️ Huquqlarim", "⚖️ Мои права", "/rights"]))
async def show_rights(message: Message):
    lang = await get_user_language(message.from_user.id)
    
    @sync_to_async
    def get_rights():
        return list(ConsumerRight.objects.filter(is_active=True).order_by('order'))
        
    rights = await get_rights()
    if not rights:
        text = "Hozircha huquqlar haqida ma'lumot yo'q." if lang == 'uz' else "Информация о правах временно отсутствует."
        await message.answer(text)
        return
        
    prompt = "O'zingizni qiziqtirgan qonuniy huquqni tanlang:" if lang == 'uz' else "Выберите интересующую вас статью или право:"
    await message.answer(prompt, reply_markup=rights_list_keyboard(rights))

@router.callback_query(F.data.startswith("right_"))
async def view_right(callback: CallbackQuery):
    lang = await get_user_language(callback.from_user.id)
    right_id = int(callback.data.split('_')[1])
    
    @sync_to_async
    def get_right(rid):
        try:
            return ConsumerRight.objects.get(id=rid)
        except ConsumerRight.DoesNotExist:
            return None
            
    right = await get_right(right_id)
    if not right:
        await callback.answer("Ma'lumot topilmadi." if lang == 'uz' else "Информация не найдена.")
        return
        
    text = f"⚖️ <b>{right.title}</b>\n\n{right.content}"
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()
