import csv
import requests
import time
import re
from django.db import transaction
from ctm_app.models.carta import Carta
from ctm_app.models.edicion import Edicion
from ctm_app.models.item_lista import ItemLista

def import_list_from_file(file_content_str, lista, format_choice, limit=None):
    """
    Parses a CSV/TXT string from Manabox or Moxfield, and creates ItemLista objects.
    Fetches missing cards from Scryfall lazily.
    """
    lines = file_content_str.splitlines()
    if not lines:
        return False, "El archivo está vacío."

    success_count = 0
    errors = []

    with transaction.atomic():
        if format_choice == 'manabox_txt':
            # regex: Qty Name (SetCode) CollectorNum
            pattern = re.compile(r'^(\d+)\s+(.+?)\s+\((.+?)\)\s+(\d+.*?)$')
            count = 0
            for i, line in enumerate(lines):
                if limit is not None and count >= limit:
                    break
                line = line.strip()
                if not line:
                    continue
                match = pattern.match(line)
                if not match:
                    errors.append(f"Fila {i+1}: Formato no reconocido '{line}'")
                    continue
                qty_str, name, set_code, collector_number = match.groups()
                qty = int(qty_str)
                name = name.strip()
                set_code = set_code.lower().strip()
                
                success = _process_card(lista, qty, name, set_code, 'NM', 'en', False, collector_number, i+1, errors)
                if success:
                    success_count += 1
                    count += 1
        else:
            reader = csv.DictReader(lines)
            headers = reader.fieldnames
            if not headers:
                return False, "Formato CSV inválido."
                
            count = 0
            for i, row in enumerate(reader):
                if limit is not None and count >= limit:
                    break
                try:
                    if format_choice == 'moxfield_csv':
                        qty = int(row.get('Count', row.get('Tradelist Count', 1)))
                        name = row.get('Name', '').strip()
                        set_code = row.get('Edition', '').lower().strip()
                        condition = row.get('Condition', 'NM')
                        language = row.get('Language', 'en')
                        is_foil = str(row.get('Foil', '')).lower() == 'true'
                        collector_number = row.get('Collector Number', '')
                    elif format_choice == 'manabox_csv':
                        qty = int(row.get('Quantity', 1))
                        name = row.get('Name', '').strip()
                        set_code = row.get('Set code', row.get('Set', '')).lower().strip()
                        condition = row.get('Condition', 'NM')
                        language = row.get('Language', 'en')
                        is_foil = str(row.get('Foil', '')).lower() in ['foil', 'true', 'yes']
                        collector_number = row.get('Collector number', '')
                    else:
                        continue
                        
                    if not name or not set_code:
                        continue
                    
                    success = _process_card(lista, qty, name, set_code, condition, language, is_foil, collector_number, i+2, errors)
                    if success:
                        success_count += 1
                        count += 1
                except Exception as e:
                    errors.append(f"Fila {i+2}: Error procesando '{row.get('Name', 'Desconocido')}' - {str(e)}")
                
    return True, {"success_count": success_count, "errors": errors}

def _process_card(lista, qty, name, set_code, condition, language, is_foil, collector_number, row_num, errors):
    # Fetch or create edition
    edicion, _ = Edicion.objects.get_or_create(set_code=set_code, defaults={'nombre': set_code.upper()})
    
    # Search local Carta
    qs = Carta.objects.filter(nombre__iexact=name, Edicion=edicion)
    if collector_number:
        qs = qs.filter(number_collector_txt=collector_number)
    carta = qs.first()

    if not carta:
        if collector_number:
            scryfall_url = f"https://api.scryfall.com/cards/{set_code}/{collector_number}"
            params = {}
        else:
            scryfall_url = "https://api.scryfall.com/cards/named"
            params = {'exact': name, 'set': set_code}
            
        resp = requests.get(scryfall_url, params=params)
        time.sleep(0.1)
        
        # Fallback si el collector number falla (a veces Scryfall requiere formatos específicos)
        if resp.status_code != 200 and collector_number:
            scryfall_url = "https://api.scryfall.com/cards/named"
            params = {'exact': name, 'set': set_code}
            resp = requests.get(scryfall_url, params=params)
            time.sleep(0.1)

        if resp.status_code == 200:
            data = resp.json()
            carta = Carta.objects.create(
                nombre=data.get('name', name),
                Edicion=edicion,
                number_collector=0, 
                number_collector_txt=data.get('collector_number', collector_number)[:10],
                small_image=data.get('image_uris', {}).get('small', ''),
                scryfall_id=data.get('id'),
                mana_cost=data.get('mana_cost', ''),
                type_line=data.get('type_line', '')[:100],
                oracle_text=data.get('oracle_text', '')
            )
        else:
            errors.append(f"Fila {row_num}: No se encontró la carta '{name}' ({set_code.upper()} #{collector_number}) en Scryfall.")
            return False
            
    cond_map = {
        'NM': 'NM', 'Near Mint': 'NM',
        'LP': 'LP', 'Lightly Played': 'LP', 'Slightly Played': 'LP',
        'MP': 'MP', 'Moderately Played': 'MP',
        'HP': 'HP', 'Heavily Played': 'HP',
        'DMG': 'DMG', 'Damaged': 'DMG', 'Poor': 'DMG',
    }
    mapped_cond = cond_map.get(condition, 'NM')

    lang_map = {
        'en': 'EN', 'English': 'EN',
        'es': 'ES', 'Spanish': 'ES',
        'ja': 'JP', 'Japanese': 'JP',
        'fr': 'FR', 'French': 'FR',
        'de': 'DE', 'German': 'DE',
        'it': 'IT', 'Italian': 'IT',
        'pt': 'PT', 'Portuguese': 'PT',
        'ru': 'RU', 'Russian': 'RU',
        'ko': 'KO', 'Korean': 'KO',
        'zh': 'ZH', 'Chinese': 'ZH',
        'zhs': 'ZH', 'zht': 'ZH',
    }
    mapped_lang = lang_map.get(language.lower(), 'EN')

    ItemLista.objects.create(
        carta=carta,
        cantidad=qty,
        precio=0,
        lista=lista,
        idioma=mapped_lang,
        estado_fisico=mapped_cond,
        es_foil=is_foil
    )
    return True
