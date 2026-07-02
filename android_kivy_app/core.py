import os
import json
from datetime import datetime

# SHAMSI CALENDAR UTILITIES

def gregorian_to_shamsi(year, month, day):
    g_days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
        g_days_in_month[1] = 29

    gy = year - 1600
    gm = month - 1
    gd = day - 1

    g_day_no = 365 * gy + (gy + 3) // 4 - (gy + 99) // 100 + (gy + 399) // 400
    for i in range(gm):
        g_day_no += g_days_in_month[i]
    g_day_no += gd

    j_day_no = g_day_no - 79

    j_np = j_day_no // 12053
    j_day_no %= 12053

    jy = 979 + 33 * j_np + 4 * (j_day_no // 1461)
    j_day_no %= 1461

    if j_day_no >= 366:
        jy += (j_day_no - 1) // 365
        j_day_no = (j_day_no - 1) % 365

    j_days_in_month = [31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 29]
    if (jy % 33) in [1, 5, 9, 13, 17, 22, 26, 30]:
        j_days_in_month[11] = 30

    jm = 0
    while jm < 12 and j_day_no >= j_days_in_month[jm]:
        j_day_no -= j_days_in_month[jm]
        jm += 1

    jd = j_day_no + 1
    return jy, jm + 1, jd


def get_current_shamsi_date():
    now = datetime.now()
    sy, sm, sd = gregorian_to_shamsi(now.year, now.month, now.day)
    return f"{sy:04d}/{sm:02d}/{sd:02d}"


def get_current_shamsi_datetime():
    now = datetime.now()
    sy, sm, sd = gregorian_to_shamsi(now.year, now.month, now.day)
    return f"{sy:04d}/{sm:02d}/{sd:02d} {now.hour:02d}:{now.minute:02d}:{now.second:02d}"


class DatabaseManager:
    def __init__(self, filepath='egg_accounting_db.json'):
        self.filepath = filepath
        self.data = self.load_data()

    def load_data(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return self.get_default_data()

    def get_default_data(self):
        return {
            'customers': {},
            'sellers': {},
            'buy_operations': [],
            'sell_operations': [],
            'settings': {
                'company_name': 'شرکت تخم مرغ عمده فروشی',
                'last_invoice_number': 0
            }
        }

    def save_data(self):
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2, default=str)

    def add_customer(self, customer_id, name, phone, address):
        self.data['customers'][customer_id] = {
            'name': name,
            'phone': phone,
            'address': address,
            'total_debt': 0,
            'total_cheque_paid': 0,
            'total_cash_paid': 0,
            'total_shipping': 0
        }
        self.save_data()

    def add_seller(self, seller_id, name, phone, address=''):
        self.data['sellers'][seller_id] = {
            'name': name,
            'phone': phone,
            'address': address,
            'total_cheque_paid': 0,
            'total_cash_paid': 0,
            'total_debt': 0
        }
        self.save_data()

    def add_buy_operation(self, operation):
        self.data['buy_operations'].append(operation)
        seller_id = operation.get('seller_id')
        if seller_id and seller_id in self.data['sellers']:
            seller = self.data['sellers'][seller_id]
            seller['total_cheque_paid'] += operation.get('cheque_amount', 0)
            seller['total_cash_paid'] += operation.get('cash_amount', 0)
            seller['total_debt'] += operation.get('debt_amount', 0)
        self.save_data()

    def add_sell_operation(self, operation):
        self.data['sell_operations'].append(operation)
        customer_id = operation.get('customer_id')
        if customer_id and customer_id in self.data['customers']:
            customer = self.data['customers'][customer_id]
            customer['total_debt'] += operation.get('debt_amount', 0)
            customer['total_cheque_paid'] += operation.get('cheque_amount', 0)
            customer['total_cash_paid'] += operation.get('cash_amount', 0)
            customer['total_shipping'] += operation.get('total_price', 0)
        self.save_data()

    def get_next_invoice_number(self):
        self.data['settings']['last_invoice_number'] += 1
        self.save_data()
        return self.data['settings']['last_invoice_number']

    def get_all_customers(self):
        return self.data['customers']

    def get_all_sellers(self):
        return self.data['sellers']

    def get_buy_operations(self):
        return self.data['buy_operations']

    def get_sell_operations(self):
        return self.data['sell_operations']


# -----------------------
# Localization helpers
# -----------------------
PERSIAN_DIGITS = {
    '0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴',
    '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹',
    ',': ',', '.': '.'
}

def to_persian_digits(value):
    """Convert a number or string to Persian digits preserving punctuation."""
    s = str(value)
    return ''.join(PERSIAN_DIGITS.get(ch, ch) for ch in s)

def format_currency(value):
    """Format numeric value with thousands separator and Persian digits plus 'تومان'."""
    try:
        # Round to integer for currency display
        v = int(round(float(value)))
        s = f"{v:,}"
        return f"{to_persian_digits(s)} تومان"
    except Exception:
        return to_persian_digits(value)
