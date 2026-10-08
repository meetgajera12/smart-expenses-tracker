import re
from rapidocr_onnxruntime import RapidOCR

# Initialize OCR
ocr = RapidOCR()


def get_lines(result):
    """
    Convert OCR result into ordered text lines with coordinates.
    """
    lines = []
    if not result:
        return lines

    for item in result:
        box = item[0]
        text = item[1].strip()

        # Get vertical (y) and horizontal (x) position
        y = int((box[0][1] + box[2][1]) / 2)
        x = int(box[0][0])

        if text:
            lines.append({
                "text": text,
                "y": y,
                "x": x
            })

    # Sort text from top to bottom
    lines.sort(key=lambda item: item["y"])
    return lines


def extract_numbers_from_line(text):
    """
    Extract all numeric amount candidates from a line of text.
    Handles ₹, Rs, commas, and decimals.
    """
    # Remove commas in numbers like 1,580.00 -> 1580.00
    cleaned = text.replace(",", "")
    
    # Find numbers with optional decimals
    matches = re.findall(r'(?:₹|Rs\.?|INR)?\s*([0-9]+\.?[0-9]*)', cleaned, re.IGNORECASE)
    
    amounts = []
    for m in matches:
        try:
            val = float(m)
            # Skip empty or zero values
            if val > 0:
                amounts.append(val)
        except ValueError:
            pass
    return amounts


def find_date(text):
    """
    Find date from bill text and format as YYYY-MM-DD.
    """
    # Match dates like 19/04/2025, 19-04-2025, 19.04.2025, 19-Jan-2025, etc.
    match = re.search(
        r'(\d{1,2})\s*[-/.]\s*([A-Za-z]+|\d{1,2})\s*[-/.]\s*(\d{2,4})',
        text
    )

    if not match:
        return ""

    day = match.group(1).zfill(2)
    month = match.group(2)
    year = match.group(3)

    months = {
        "jan": "01", "feb": "02", "mar": "03", "apr": "04",
        "may": "05", "jun": "06", "jul": "07", "aug": "08",
        "sep": "09", "oct": "10", "nov": "11", "dec": "12"
    }

    if month.lower() in months:
        month = months[month.lower()]
    else:
        month = month.zfill(2)

    if len(year) == 2:
        year = "20" + year

    return f"{year}-{month}-{day}"


def find_merchant(lines):
    """
    Extract merchant/store name from the top lines of the bill.
    """
    ignore_words = [
        "TAX INVOICE", "CASH MEMO", "INVOICE", "BILL", "RECEIPT",
        "RETAIL INVOICE", "ORIGINAL", "DUPLICATE", "CASH RECEIPT",
        "ESTIMATE", "ORDER", "TABLE NO", "TOKEN"
    ]

    for line in lines[:5]:
        text = line["text"].strip()

        # Skip very short lines or symbols
        if len(text) < 3 or text.startswith("---") or text.startswith("==="):
            continue

        # Skip header labels
        is_ignore = False
        for word in ignore_words:
            if word in text.upper():
                is_ignore = True
                break

        if not is_ignore:
            return text

    # Fallback to first line if nothing found
    if lines:
        return lines[0]["text"].strip()
    return "Store"


def find_total_amount(lines, full_text):
    """
    Accurately find the bill total amount.
    Avoids picking dates (e.g. 2025), phone numbers, or bill numbers.
    """
    # 1. Search for explicit Total lines (e.g. 'Grand Total', 'Total:', 'Net Payable', 'Bill Amount')
    total_keywords = [
        "GRAND TOTAL", "NET AMOUNT", "NET PAYABLE", "BILL TOTAL",
        "AMOUNT DUE", "FINAL AMOUNT", "FOOD TOTAL", "TOTAL AMOUNT",
        "TOTAL", "SUBTOTAL", "SUB TOTAL"
    ]

    for keyword in total_keywords:
        for idx, line in enumerate(lines):
            text_upper = line["text"].upper()

            if keyword in text_upper:
                # Extract numbers from current line
                numbers = extract_numbers_from_line(line["text"])

                # If numbers exist on this line, return the last number (usually total)
                if numbers:
                    return numbers[-1]

                # If number is on the next line (common in multi-column OCR)
                if idx + 1 < len(lines):
                    next_line_numbers = extract_numbers_from_line(lines[idx + 1]["text"])
                    if next_line_numbers:
                        return next_line_numbers[-1]

    # 2. Search for currency symbols (₹, Rs) in text
    currency_matches = re.findall(
        r'(?:₹|Rs\.?|INR)\s*([0-9]+\.?[0-9]*)',
        full_text,
        re.IGNORECASE
    )
    if currency_matches:
        valid_vals = []
        for m in currency_matches:
            try:
                v = float(m)
                # Ignore year-like numbers (e.g. 2024, 2025, 2026) unless they have decimals
                if v not in [2024, 2025, 2026, 2027]:
                    valid_vals.append(v)
            except ValueError:
                pass
        if valid_vals:
            return max(valid_vals)

    # 3. Fallback: extract all numbers with decimal points (like 1864.40, 450.00)
    decimal_matches = re.findall(r'\b([0-9]+\.[0-9]{1,2})\b', full_text)
    if decimal_matches:
        vals = [float(x) for x in decimal_matches]
        return max(vals)

    return 0.0


def find_items(lines):
    """
    Extract item names and amounts from bill tables.
    Handles headers like: Particulars, Item, Description, Menu, Qty, Rate, Amount.
    """
    items = []
    inside_items_section = False

    header_keywords = [
        "PARTICULAR", "ITEM", "DESCRIPTION", "MENU", "PRODUCT",
        "QTY", "RATE", "PRICE", "AMOUNT"
    ]

    stop_keywords = [
        "SUB TOTAL", "SUBTOTAL", "TOTAL", "FOOD TOTAL", "CGST", "SGST",
        "VAT", "SERVICE CHARGE", "TAX", "DISCOUNT", "ROUND OFF",
        "THANK YOU", "VISIT AGAIN", "E.&O.E", "CASH", "UPI", "CARD"
    ]

    for line in lines:
        text = line["text"].strip()
        text_upper = text.upper()

        # Check if table header started
        if not inside_items_section:
            for kw in header_keywords:
                if kw in text_upper:
                    inside_items_section = True
                    break
            continue

        # Check if items section ended (hit subtotal, tax, or total)
        for stop_kw in stop_keywords:
            if stop_kw in text_upper:
                inside_items_section = False
                break

        if not inside_items_section:
            continue

        # Skip separators like ---- or =====
        if text.startswith("---") or text.startswith("===") or len(text) < 2:
            continue

        # An item line typically contains text and at least one number
        # Example: 'HANDI PANEER 2 200 400' or '1 Orange Powder 400' or 'JEERA RICE 110.00'
        
        # Remove item index prefix if present (e.g. '1 Handi Paneer' -> 'Handi Paneer')
        cleaned_text = re.sub(r'^\d+[\s.-]+', '', text).strip()

        # Remove trailing amounts and quantities from the end to get clean item name
        # Removes numbers at the end (e.g., ' 2 200 400' or ' 150.00')
        item_name = re.sub(r'(\s+\d+(?:\.\d+)?)+$', '', cleaned_text).strip()

        # If clean item name has letters, add to items
        if len(item_name) >= 2 and re.search(r'[A-Za-z]', item_name):
            items.append({
                "number": len(items) + 1,
                "name": item_name
            })

    return items


def extract_bill_details(image_path):
    """
    Main function to run OCR and parse merchant, date, amount, and items.
    """
    # 1. Perform RapidOCR
    result, _ = ocr(image_path)
    lines = get_lines(result)

    # Combine all lines into full text
    text_lines = [line["text"] for line in lines]
    full_text = "\n".join(text_lines)

    print("\n========== BILL OCR TEXT ==========")
    print(full_text)
    print("===================================\n")

    # 2. Extract Merchant Name
    merchant = find_merchant(lines)

    # 3. Extract Date
    date = find_date(full_text)

    # 4. Extract Total Amount
    amount = find_total_amount(lines, full_text)

    # 5. Extract Items
    items = find_items(lines)

    return {
        "merchant": merchant,
        "amount": round(amount, 2),
        "date": date,
        "items": items,
        "raw_text": full_text
    }