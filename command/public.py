# command/public.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Commands: /explore, /locations, /risk, /go [lokasi]
=============================================================================
"""

import logging
import random
from typing import Optional, Dict, List, Any

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from public.locations import PublicLocations
from public.risk import RiskCalculator
from public.thrill import ThrillSystem
from public.auto_select import LocationAutoSelector
from public.events import RandomEvents
from identity.manager import IdentityManager

logger = logging.getLogger(__name__)


async def explore_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler untuk /explore - Cari lokasi random untuk public sex
    """
    user_id = update.effective_user.id
    
    # Cek apakah ada karakter aktif
    current_reg = context.user_data.get('current_registration')
    if not current_reg:
        await update.message.reply_text(
            "❌ **Tidak ada karakter aktif**\n\n"
            "Ketik `/start` untuk memilih karakter.",
            parse_mode='HTML'
        )
        return
    
    locations = PublicLocations()
    risk_calc = RiskCalculator()
    thrill_system = ThrillSystem()
    
    # Ambil lokasi random
    location = locations.get_random_location()
    
    # Hitung risk
    risk_data = await risk_calc.calculate_risk(
        base_risk=location['base_risk'],
        intimacy_level=current_reg.get('level', 1)
    )
    
    # Hitung thrill
    thrill_data = await thrill_system.calculate_thrill(
        base_thrill=location['base_thrill'],
        risk_level=risk_data['final_risk'],
        intimacy_level=current_reg.get('level', 1),
        location_category=location['category']
    )
    
    # Format response
    response = _format_location_explore(location, risk_data, thrill_data)
    
    # Tambah keyboard untuk pindah
    keyboard = [
        [InlineKeyboardButton("📍 Pindah ke sini", callback_data=f"go_{location['id']}"),
         InlineKeyboardButton("🎲 Cari Lain", callback_data="explore_random")],
        [InlineKeyboardButton("⚠️ Cek Risk Detail", callback_data=f"risk_{location['id']}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(response, reply_markup=reply_markup, parse_mode='HTML')


async def locations_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler untuk /locations - Lihat semua kategori lokasi
    """
    locations = PublicLocations()
    stats = locations.get_location_stats()
    
    lines = [
        "📍 **PUBLIC AREAS**\n",
        "**Kategori Lokasi:**",
        f"🏙️ **Urban** - {stats['urban']} lokasi (mall, toilet, parkir, lift)",
        f"🌳 **Nature** - {stats['nature']} lokasi (pantai, hutan, taman, kebun)",
        f"⚡ **Extreme** - {stats['extreme']} lokasi (masjid, gereja, polisi, kuburan)",
        f"🚗 **Transport** - {stats['transport']} lokasi (mobil, kereta, bus, kapal)",
        "",
        f"📊 **Rata-rata Risk:** {stats['avg_risk']:.0f}%",
        f"🎢 **Rata-rata Thrill:** {stats['avg_thrill']:.0f}%",
        "",
        "💡 **Cara pakai:**",
        "• `/explore` - Cari lokasi random",
        "• `/go [nama lokasi]` - Pindah ke lokasi tertentu",
        "• `/risk` - Cek risk lokasi saat ini",
        "",
        "📝 **Contoh:** `/go pantai` atau `/go toilet mall`"
    ]
    
    await update.message.reply_text("\n".join(lines), parse_mode='HTML')


async def risk_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler untuk /risk - Cek risk lokasi saat ini
    """
    user_id = update.effective_user.id
    
    # Cek apakah ada karakter aktif
    current_reg = context.user_data.get('current_registration')
    if not current_reg:
        await update.message.reply_text(
            "❌ **Tidak ada karakter aktif**\n\n"
            "Ketik `/start` untuk memilih karakter.",
            parse_mode='HTML'
        )
        return
    
    registration_id = current_reg.get('id')
    
    identity_manager = IdentityManager()
    state = await identity_manager.get_character_state(registration_id)
    
    if not state or not state.location_bot:
        await update.message.reply_text(
            "📍 **Risk Assessment**\n\n"
            "Mas belum berada di lokasi manapun.\n"
            "Pindah dulu, misal: `/go pantai`",
            parse_mode='HTML'
        )
        return
    
    location_name = state.location_bot
    
    locations = PublicLocations()
    location = locations.get_location_by_name(location_name)
    
    if not location:
        # Gunakan lokasi default
        location = locations.get_random_location()
        location_name = location['name']
    
    risk_calc = RiskCalculator()
    risk_data = await risk_calc.calculate_risk(
        base_risk=location['base_risk'],
        intimacy_level=current_reg.get('level', 1)
    )
    
    response = risk_calc.format_risk_report(risk_data, location_name)
    
    await update.message.reply_text(response, parse_mode='HTML')


async def go_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler untuk /go [lokasi] - Pindah ke lokasi tertentu
    """
    user_id = update.effective_user.id
    args = context.args
    
    if not args:
        await update.message.reply_text(
            "❌ **Cara pakai:** /go [nama lokasi]\n\n"
            "Contoh:\n"
            "• `/go pantai`\n"
            "• `/go toilet mall`\n"
            "• `/go taman kota`\n\n"
            "Gunakan `/locations` untuk lihat semua lokasi.",
            parse_mode='HTML'
        )
        return
    
    # Cek apakah ada karakter aktif
    current_reg = context.user_data.get('current_registration')
    if not current_reg:
        await update.message.reply_text(
            "❌ **Tidak ada karakter aktif**\n\n"
            "Ketik `/start` untuk memilih karakter.",
            parse_mode='HTML'
        )
        return
    
    location_name = ' '.join(args).lower()
    
    locations = PublicLocations()
    location = locations.get_location_by_name(location_name)
    
    if not location:
        await update.message.reply_text(
            f"❌ Lokasi '{location_name}' tidak ditemukan.\n\n"
            f"Gunakan `/locations` untuk melihat daftar lokasi yang tersedia.",
            parse_mode='HTML'
        )
        return
    
    registration_id = current_reg.get('id')
    
    identity_manager = IdentityManager()
    
    # Update lokasi di state
    await identity_manager.update_character_state(
        registration_id,
        {'location_bot': location['name'], 'location_user': location['name']}
    )
    
    # Hitung risk
    risk_calc = RiskCalculator()
    risk_data = await risk_calc.calculate_risk(
        base_risk=location['base_risk'],
        intimacy_level=current_reg.get('level', 1)
    )
    
    # Format response
    response = _format_go_response(location, risk_data)
    
    await update.message.reply_text(response, parse_mode='HTML')


async def explore_random_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback untuk cari lokasi random lagi"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # Cek apakah ada karakter aktif
    current_reg = context.user_data.get('current_registration')
    if not current_reg:
        await query.edit_message_text(
            "❌ **Tidak ada karakter aktif**\n\n"
            "Ketik `/start` untuk memilih karakter.",
            parse_mode='HTML'
        )
        return
    
    locations = PublicLocations()
    risk_calc = RiskCalculator()
    thrill_system = ThrillSystem()
    
    # Ambil lokasi random
    location = locations.get_random_location()
    
    # Hitung risk
    risk_data = await risk_calc.calculate_risk(
        base_risk=location['base_risk'],
        intimacy_level=current_reg.get('level', 1)
    )
    
    # Hitung thrill
    thrill_data = await thrill_system.calculate_thrill(
        base_thrill=location['base_thrill'],
        risk_level=risk_data['final_risk'],
        intimacy_level=current_reg.get('level', 1),
        location_category=location['category']
    )
    
    # Format response
    response = _format_location_explore(location, risk_data, thrill_data)
    
    # Keyboard
    keyboard = [
        [InlineKeyboardButton("📍 Pindah ke sini", callback_data=f"go_{location['id']}"),
         InlineKeyboardButton("🎲 Cari Lain", callback_data="explore_random")],
        [InlineKeyboardButton("⚠️ Cek Risk Detail", callback_data=f"risk_{location['id']}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(response, reply_markup=reply_markup, parse_mode='HTML')


async def go_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback untuk pindah lokasi dari explore"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    data = query.data
    
    location_id = data.replace("go_", "")
    
    # Cek apakah ada karakter aktif
    current_reg = context.user_data.get('current_registration')
    if not current_reg:
        await query.edit_message_text(
            "❌ **Tidak ada karakter aktif**\n\n"
            "Ketik `/start` untuk memilih karakter.",
            parse_mode='HTML'
        )
        return
    
    locations = PublicLocations()
    location = locations.get_location_by_id(location_id)
    
    if not location:
        await query.edit_message_text(
            f"❌ Lokasi tidak ditemukan.",
            parse_mode='HTML'
        )
        return
    
    registration_id = current_reg.get('id')
    
    identity_manager = IdentityManager()
    
    # Update lokasi di state
    await identity_manager.update_character_state(
        registration_id,
        {'location_bot': location['name'], 'location_user': location['name']}
    )
    
    # Hitung risk
    risk_calc = RiskCalculator()
    risk_data = await risk_calc.calculate_risk(
        base_risk=location['base_risk'],
        intimacy_level=current_reg.get('level', 1)
    )
    
    # Format response
    response = _format_go_response(location, risk_data)
    
    await query.edit_message_text(response, parse_mode='HTML')


async def risk_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback untuk cek risk lokasi"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    data = query.data
    
    location_id = data.replace("risk_", "")
    
    locations = PublicLocations()
    location = locations.get_location_by_id(location_id)
    
    if not location:
        await query.edit_message_text(
            f"❌ Lokasi tidak ditemukan.",
            parse_mode='HTML'
        )
        return
    
    # Cek apakah ada karakter aktif
    current_reg = context.user_data.get('current_registration')
    if not current_reg:
        current_level = 7
    else:
        current_level = current_reg.get('level', 7)
    
    risk_calc = RiskCalculator()
    risk_data = await risk_calc.calculate_risk(
        base_risk=location['base_risk'],
        intimacy_level=current_level
    )
    
    response = risk_calc.format_risk_report(risk_data, location['name'])
    
    # Tambah tombol kembali
    keyboard = [[InlineKeyboardButton("🔙 Kembali", callback_data="explore_random")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(response, reply_markup=reply_markup, parse_mode='HTML')


def _format_location_explore(location: Dict, risk_data: Dict, thrill_data: Dict) -> str:
    """Format lokasi untuk explore"""
    
    risk_level = risk_data['risk_level']
    thrill_level = thrill_data['thrill_level'].replace('_', ' ').title()
    
    return (
        f"📍 **{location['name'].title()}**\n"
        f"_{location['description']}_\n\n"
        f"⚠️ **Risk:** {risk_data['final_risk']}% ({risk_level})\n"
        f"🎢 **Thrill:** {thrill_data['final_thrill']}% ({thrill_level})\n"
        f"💡 **Tips:** {location['tips']}\n\n"
        f"_Pilih tindakan di bawah:_"
    )


def _format_go_response(location: Dict, risk_data: Dict) -> str:
    """Format response pindah lokasi"""
    
    risk_level = risk_data['risk_level']
    
    return (
        f"📍 **Pindah ke {location['name'].title()}**\n\n"
        f"{location['description']}\n\n"
        f"⚠️ **Risk Level:** {risk_data['final_risk']}% ({risk_level})\n"
        f"📝 {risk_data['description']}\n\n"
        f"💡 {location['tips']}\n\n"
        f"_Sekarang Mas di {location['name']}._"
    )


__all__ = [
    'explore_command',
    'locations_command',
    'risk_command',
    'go_command',
    'explore_random_callback',
    'go_callback',
    'risk_callback'
]
