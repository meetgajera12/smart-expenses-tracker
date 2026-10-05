import re
from rapidocr_onnxruntime import RapidOCR


# Start OCR
ocr = RapidOCR()


def get_lines(result):
    """
    Convert OCR result into simple text lines.
    """

    lines = []

    if not result:
        return lines

    for item in result:
        box = item[0]
        text = item[1]

        # Get the vertical position of the text
        y = int((box[0][1] + box[2][1]) / 2)

        lines.append({
            "text": text.strip(),
            "y": y
        })

    # Sort text from top to bottom
    lines.sort(key=lambda x: x["y"])

    return lines


def find_amount(text):
    """
    Find the last money value in a line.
    """

    numbers = re.findall(
        r'(?:₹|Rs\.?|INR)?\s*([0-9]+(?:\.[0-9]{1,2})?)',
        text,
        re.IGNORECASE
    )

    if numbers:
        return float(numbers[-1])

    return 0


def find_date(text):
    """
    Find date from the bill and convert it to YYYY-MM-DD.
    """

    # Example:
    # 23 - Jan - 2025
    match = re.search(
        r'(\d{1,2})\s*[-/]\s*([A-Za-z]+|\d{1,2})\s*[-/]\s*(\d{2,4})',
        text
    )

    if not match:
        return ""

    day = match.group(1)
    month = match.group(2)
    year = match.group(3)

    months = {
        "jan": "01",
        "feb": "02",
        "mar": "03",
        "apr": "04",
        "may": "05",
        "jun": "06",
        "jul": "07",
        "aug": "08",
        "sep": "09",
        "oct": "10",
        "nov": "11",
        "dec": "12"
    }

    if month.lower() in months:
        month = months[month.lower()]
    else:
        month = month.zfill(2)

    if len(year) == 2:
        year = "20" + year

    return year + "-" + month + "-" + day.zfill(2)


def find_merchant(lines):
    """
    Try to find the shop name.
    """

    for i in range(len(lines)):

        text = lines[i]["text"]

        if "SLEEK BILL" in text.upper():
            return "SLEEK BILL"

    # If SLEEK BILL is not found,
    # use the first useful line.
    for line in lines:

        text = line["text"]

        if len(text) > 3:
            return text

    return ""


def find_items(lines):
    """
    Find simple bill item rows.

    Example:
    1 Orange Powder 1 400.00 448.00
    """

    items = []

    inside_items = False

    for line in lines:

        text = line["text"]

        # Start reading items after the table header
        if "ITEM" in text.upper():
            inside_items = True
            continue

        # Stop when subtotal starts
        if "SUBTOTAL" in text.upper():
            break

        if inside_items:

            # Check if line starts with item number
            match = re.match(r'^(\d+)\s+(.*)', text)

            if match:

                item_number = match.group(1)
                item_text = match.group(2)

                # Remove numbers from the end
                item_text = re.sub(
                    r'\s+\d+(?:\.\d+)?\s+\d+(?:\.\d+)?$',
                    '',
                    item_text
                )

                # Remove quantity and price if OCR kept them
                item_text = item_text.strip()

                if item_text:
                    items.append({
                        "number": int(item_number),
                        "name": item_text
                    })

    return items


def extract_bill_details(image_path):

    # -------------------------
    # OCR
    # -------------------------

    result, _ = ocr(image_path)

    lines = get_lines(result)

    text_lines = []

    for line in lines:
        text_lines.append(line["text"])

    full_text = "\n".join(text_lines)

    print("\n========== BILL OCR ==========")
    print(full_text)
    print("==============================\n")

    # -------------------------
    # Merchant
    # -------------------------

    merchant = find_merchant(lines)

    # -------------------------
    # Date
    # -------------------------

    date = find_date(full_text)

    # -------------------------
    # Total
    # -------------------------

    amount = 0

    for line in lines:

        text = line["text"]

        if re.search(r'\bTOTAL\b', text, re.IGNORECASE):

            value = find_amount(text)

            if value > 0:
                amount = value

    # If TOTAL was not found,
    # try GRAND TOTAL
    if amount == 0:

        for line in lines:

            text = line["text"]

            if "GRAND TOTAL" in text.upper():

                value = find_amount(text)

                if value > 0:
                    amount = value

    # Last backup:
    # use the largest number
    if amount == 0:

        numbers = re.findall(
            r'(?:₹|Rs\.?|INR)?\s*([0-9]+(?:\.[0-9]{1,2})?)',
            full_text,
            re.IGNORECASE
        )

        if numbers:

            values = []

            for number in numbers:
                values.append(float(number))

            amount = max(values)

    # -------------------------
    # Items
    # -------------------------

    items = find_items(lines)

    # -------------------------
    # Return
    # -------------------------

    return {
        "merchant": merchant,
        "amount": amount,
        "date": date,
        "items": items,
        "raw_text": full_text
    }