import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.orm import Session
from database import SessionLocal
from models import ProductDB

router = Router()

# მომხმარებლების კალათები მეხსიერებაში: {user_id: {product_id: quantity}}
user_carts = {}

@router.message(F.text == "/start")
async def cmd_start(message: Message):
    await message.answer(
        "გამარჯობა! მე ვარ GeoMobile-ის ოფიციალური ასისტენტი.\n\n"
        "🔍 პროდუქტების მოსაძებნად გამოიყენეთ ბრძანება:\n"
        "`/search ბრენდი` (მაგ: `/search iPhone`)\n\n"
        "🛒 კალათის სანახავად ჩაწერეთ: `/cart`"
    )

@router.message(F.text.startswith("/search"))
async def search_products(message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("გთხოვ მიუთითო საძიებო სიტყვა, მაგალითად: `/search Samsung`")
        return
    
    keyword = args[1].strip()
    db: Session = SessionLocal()
    try:
        products = db.query(ProductDB).filter(ProductDB.name.ilike(f"%{keyword}%")).limit(5).all()
        if not products:
            await message.answer(f"'{keyword}' დასახელებით პროდუქტი ვერ მოიძებნა.")
            return
        
        for p in products:
            # ინლაინ ღილაკი თითოეული პროდუქტისთვის
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🛒 კალათაში დამატება", callback_data=f"add_{p.id}")]
            ])
            
            text = (
                f"📱 **{p.name}**\n"
                f"📂 კატეგორია: {p.category}\n"
                f"💰 ფასი: {p.price} ₾\n"
                f"📦 მარაგშია: {p.stock} ცალი"
            )
            await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")
    finally:
        db.close()

# კალათაში დამატება ღილაკით
@router.callback_query(F.data.startswith("add_"))
async def add_to_cart_callback(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id
    
    db: Session = SessionLocal()
    try:
        product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
        if not product:
            await callback.answer("პროდუქტი ვერ მოიძებნა!", show_alert=True)
            return
        
        if product.stock <= 0:
            await callback.answer("პროდუქტი ამოიწურა მარაგში!", show_alert=True)
            return
        
        if user_id not in user_carts:
            user_carts[user_id] = {}
        
        current_qty = user_carts[user_id].get(product_id, 0)
        if current_qty >= product.stock:
            await callback.answer("მეტი რაოდენობა მარაგში არ არის!", show_alert=True)
            return
        
        user_carts[user_id][product_id] = current_qty + 1
        await callback.answer(f"✅ '{product.name}' დაემატა კალათაში!")
    finally:
        db.close()

# კალათის ნახვა
@router.message(F.text == "/cart")
async def show_cart(message: Message):
    user_id = message.from_user.id
    if user_id not in user_carts or not user_carts[user_id]:
        await message.answer("🛒 თქვენი კალათა ცარიელია.")
        return
    
    db: Session = SessionLocal()
    try:
        text = "🛒 **თქვენი კალათა:**\n\n"
        total_price = 0
        
        for product_id, qty in user_carts[user_id].items():
            product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
            if product:
                subtotal = product.price * qty
                total_price += subtotal
                text += f"📱 **{product.name}**\n   რაოდენობა: {qty} ცალი | ფასი: {subtotal} ₾\n\n"
        
        text += f"💰 **სულ გადასახდელია: {total_price} ₾**"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ შეკვეთის გაფორმება", callback_data="checkout")],
            [InlineKeyboardButton(text="🗑 კალათის გასუფთავება", callback_data="clear_cart")]
        ])
        
        await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")
    finally:
        db.close()

# კალათის გასუფთავება
@router.callback_query(F.data == "clear_cart")
async def clear_cart(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id in user_carts:
        user_carts[user_id] = {}
    await callback.message.edit_text("🗑 კალათა გასუფთავებულია.")
    await callback.answer()

# შეკვეთის გაფორმება (მარაგის შემცირება ბაზაში)
@router.callback_query(F.data == "checkout")
async def checkout(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in user_carts or not user_carts[user_id]:
        await callback.answer("კალათა ცარიელია!", show_alert=True)
        return
    
    db: Session = SessionLocal()
    try:
        for product_id, qty in user_carts[user_id].items():
            product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
            if product:
                if product.stock < qty:
                    await callback.message.answer(f"⚠️ ბოდიში, პროდუქტი '{product.name}' აღარ არის საკმარისი მარაგი.")
                    db.rollback()
                    return
                product.stock -= qty
        
        db.commit()
        user_carts[user_id] = {}  # გასუფთავება ყიდვის შემდეგ
        await callback.message.edit_text("🎉 **შეკვეთა წარმატებით გაფორმდა!** მადლობა რომ სარგებლობთ GeoMobile-ით.")
        await callback.answer()
    except Exception as e:
        db.rollback()
        await callback.answer("შეცდომა შეკვეთის დამუშავებისას.", show_alert=True)
    finally:
        db.close()
