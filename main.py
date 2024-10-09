from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from PIL import Image, ImageDraw, ImageFont

bot = Bot(token='7484796265:AAE1aos40kjJkpZqp1BOaHSXolgzDNncDio')

# Створення диспетчера з використанням пам'яті для збереження станів
dp = Dispatcher(bot, storage=MemoryStorage())

# Обробник для команди /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer('Hallo,\n ich bin ein Bot zum Erstellen von Bildern.\n Um mit der Arbeit zu beginnen, sende mir bitte ein Bild.')

@dp.message_handler(content_types=[types.ContentType.PHOTO])
async def handle_photo(message: types.Message, state: FSMContext):
    # Завантаження останньої фотографії
    await message.photo[-1].download(destination_file='photo.jpg')
    await message.answer('Foto erfolgreich gespeichert\n Schreib den Text, den du dem Foto hinzufügen möchtest.')
    await state.set_state('set_photo_text')

@dp.message_handler(state='set_photo_text')
async def set_photo_text(message: types.Message, state: FSMContext):
    # Визначення функції для обчислення розміру тексту
    def draw_text_size(text, font):
        temp_image = Image.new('RGB', (1000, 1000))  # Велике зображення для перевірки розміру
        draw = ImageDraw.Draw(temp_image)
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        return text_width, text_height

    # Відкриваємо основне зображення
    image = Image.open('photo.jpg')
    draw = ImageDraw.Draw(image)

    # Завантаження шрифту (переконайтесь, що шрифт доступний)
    try:
        font = ImageFont.truetype('Impact.ttf', 50)  # Замініть 'arial.ttf' на шлях до доступного шрифту
    except IOError:
        font = ImageFont.load_default()

    text = message.text

    # Визначення розміру тексту та позиції
    text_width, text_height = draw_text_size(text, font)
    x = (image.width - text_width) / 2
    #y = image.height - text_height - 40 текст буде внизу
    y = 40

    # Малюємо білу тінь для тексту
    shadow_offset = 3  # Відступ для тіні
    draw.text((x + shadow_offset, y + shadow_offset), text.upper(), font=font, fill=(255, 255, 255))  # Біла тінь

    # Малюємо чорний текст на зображенні
    draw.text((x, y), text.upper(), font=font, fill=(0, 0, 0))  # Чорний текст
    image.save('photo_mem.jpg')

    # Відправка зображення з текстом
    await message.answer('Toll!\nHier ist dein Mem:')

    with open('photo_mem.jpg', 'rb') as photo:
        await bot.send_photo(message.from_user.id, photo)

    await state.finish()

# Запуск довготривалого опитування (polling)
if __name__ == '__main__':
    executor.start_polling(dp)



