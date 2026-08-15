from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from bot.keyboards.common import rights_list_keyboard
from asgiref.sync import sync_to_async
from apps.rights.models import ConsumerRight

router = Router(name='rights_router')

@router.message(F.text == "⚖️ Huquqlarim")
async def show_rights(message: Message):
    @sync_to_async
    def get_rights():
        return list(ConsumerRight.objects.filter(is_active=True).order_by('order'))
        
    rights = await get_rights()
    if not rights:
        await message.answer("Hozircha huquqlar haqida ma'lumot yo'q.")
        return
        
    await message.answer("O'zingizni qiziqtirgan huquqni tanlang:", reply_markup=rights_list_keyboard(rights))

@router.callback_query(F.data.startswith("right_"))
async def view_right(callback: CallbackQuery):
    right_id = int(callback.data.split('_')[1])
    
    @sync_to_async
    def get_right(rid):
        try:
            return ConsumerRight.objects.get(id=rid)
        except ConsumerRight.DoesNotExist:
            return None
            
    right = await get_right(right_id)
    if not right:
        await callback.answer("Ma'lumot topilmadi.")
        return
        
    text = f"⚖️ {right.title}\n\n{right.content}"
    await callback.message.answer(text)
    await callback.answer()
