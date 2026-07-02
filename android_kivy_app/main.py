from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.recycleview import RecycleView
from kivy.properties import ObjectProperty
from core import DatabaseManager, get_current_shamsi_datetime, format_currency, to_persian_digits
from kivy.uix.popup import Popup
import os
from kivy.clock import Clock
from kivy.uix.spinner import Spinner
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.scrollview import ScrollView

DATA_FILE = os.path.join(os.path.dirname(__file__), 'egg_accounting_db.json')


class SimpleRV(RecycleView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = []
        # callback for item taps; set by parent
        self.item_callback = None


class HistoryButton(Button):
    callback = ObjectProperty(None)

    def on_release(self):
        if callable(self.callback):
            try:
                self.callback(self.text)
            except Exception:
                pass


class EggAppUI(TabbedPanel):
    db = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DatabaseManager(filepath=DATA_FILE)
        self.do_default_tab = False

        # Customers tab
        self.customers_panel = BoxLayout(orientation='vertical')
        self.customers_form = GridLayout(cols=2, size_hint_y=None, height=200, padding=10, spacing=10)
        self.cust_id = TextInput(multiline=False)
        self.cust_name = TextInput(multiline=False)
        self.cust_phone = TextInput(multiline=False)
        self.cust_address = TextInput(multiline=False)
        self.customers_form.add_widget(Label(text='کد مشتری:'))
        self.customers_form.add_widget(self.cust_id)
        self.customers_form.add_widget(Label(text='نام مشتری:'))
        self.customers_form.add_widget(self.cust_name)
        self.customers_form.add_widget(Label(text='شماره تماس:'))
        self.customers_form.add_widget(self.cust_phone)
        self.customers_form.add_widget(Label(text='آدرس:'))
        self.customers_form.add_widget(self.cust_address)

        add_btn = Button(text='افزودن مشتری')
        add_btn.bind(on_release=self.add_customer)
        add_btn.size_hint = (None, None)
        add_btn.width = 220
        add_btn.height = 44
        add_btn.font_size = '16sp'

        self.customers_list = SimpleRV()
        self.customers_list.item_callback = lambda txt: self.on_history_item(txt, 'customer')

        self.customers_panel.add_widget(self.customers_form)
        self.customers_panel.add_widget(add_btn)
        self.customers_panel.add_widget(self.customers_list)

        self.add_widget(self.customers_panel)
        self.default_tab_text = 'مشتریان'

        # Sellers tab
        self.sellers_panel = BoxLayout(orientation='vertical')
        self.seller_form = GridLayout(cols=2, size_hint_y=None, height=200, padding=10, spacing=10)
        self.seller_id = TextInput(multiline=False)
        self.seller_name = TextInput(multiline=False)
        self.seller_phone = TextInput(multiline=False)
        self.seller_address = TextInput(multiline=False)
        self.seller_form.add_widget(Label(text='کد فروشنده:'))
        self.seller_form.add_widget(self.seller_id)
        self.seller_form.add_widget(Label(text='نام فروشنده:'))
        self.seller_form.add_widget(self.seller_name)
        self.seller_form.add_widget(Label(text='شماره تماس:'))
        self.seller_form.add_widget(self.seller_phone)
        self.seller_form.add_widget(Label(text='آدرس:'))
        self.seller_form.add_widget(self.seller_address)

        add_s_btn = Button(text='افزودن فروشنده')
        add_s_btn.bind(on_release=self.add_seller)
        add_s_btn.size_hint = (None, None)
        add_s_btn.width = 220
        add_s_btn.height = 44
        add_s_btn.font_size = '16sp'

        self.sellers_list = SimpleRV()
        self.sellers_list.item_callback = lambda txt: self.on_history_item(txt, 'seller')

        self.sellers_panel.add_widget(self.seller_form)
        self.sellers_panel.add_widget(add_s_btn)
        self.sellers_panel.add_widget(self.sellers_list)

        self.add_widget(self.sellers_panel)

        # Buy tab
        buy_item = TabbedPanelItem(text='خرید')
        self.buy_panel = BoxLayout(orientation='vertical')
        buy_form = GridLayout(cols=2, size_hint_y=None, height=320, padding=10, spacing=10)
        self.buy_seller = Spinner(text='انتخاب فروشنده', values=[], size_hint=(None, None), size=(240, 44))
        self.buy_weight = TextInput(multiline=False)
        self.buy_price = TextInput(multiline=False)
        self.buy_driver = TextInput(multiline=False)
        self.buy_cheque = TextInput(multiline=False)
        self.buy_cash = TextInput(multiline=False)
        self.buy_debt = TextInput(multiline=False)
        buy_form.add_widget(Label(text='فروشنده:'))
        buy_form.add_widget(self.buy_seller)
        buy_form.add_widget(Label(text='وزن (کیلو):'))
        buy_form.add_widget(self.buy_weight)
        buy_form.add_widget(Label(text='قیمت/کیلو:'))
        buy_form.add_widget(self.buy_price)
        buy_form.add_widget(Label(text='حقوق راننده:'))
        buy_form.add_widget(self.buy_driver)
        buy_form.add_widget(Label(text='مبلغ چک:'))
        buy_form.add_widget(self.buy_cheque)
        buy_form.add_widget(Label(text='مبلغ نقدی:'))
        buy_form.add_widget(self.buy_cash)
        buy_form.add_widget(Label(text='مبلغ بدهکاری:'))
        buy_form.add_widget(self.buy_debt)

        buy_btn = Button(text='ثبت خرید')
        buy_btn.bind(on_release=self.save_buy_operation)
        self.buy_history = SimpleRV()
        self.buy_history.item_callback = lambda txt: self.on_history_item(txt, 'buy')
        self.buy_panel.add_widget(buy_form)
        self.buy_panel.add_widget(buy_btn)
        self.buy_panel.add_widget(Label(text='تاریخچه خریدها:'))
        self.buy_panel.add_widget(self.buy_history)
        buy_item.add_widget(self.buy_panel)
        self.add_widget(buy_item)

        # Sell tab
        sell_item = TabbedPanelItem(text='فروش')
        self.sell_panel = BoxLayout(orientation='vertical')
        sell_form = GridLayout(cols=2, size_hint_y=None, height=300, padding=10, spacing=10)
        self.sell_customer = Spinner(text='انتخاب مشتری', values=[], size_hint=(None, None), size=(240, 44))
        self.sell_weight = TextInput(multiline=False)
        self.sell_price = TextInput(multiline=False)
        self.sell_cheque = TextInput(multiline=False)
        self.sell_cash = TextInput(multiline=False)
        self.sell_debt = TextInput(multiline=False)
        sell_form.add_widget(Label(text='مشتری:'))
        sell_form.add_widget(self.sell_customer)
        sell_form.add_widget(Label(text='وزن (کیلو):'))
        sell_form.add_widget(self.sell_weight)
        sell_form.add_widget(Label(text='قیمت/کیلو:'))
        sell_form.add_widget(self.sell_price)
        sell_form.add_widget(Label(text='مبلغ چک:'))
        sell_form.add_widget(self.sell_cheque)
        sell_form.add_widget(Label(text='مبلغ نقدی:'))
        sell_form.add_widget(self.sell_cash)
        sell_form.add_widget(Label(text='مبلغ بدهکاری:'))
        sell_form.add_widget(self.sell_debt)

        sell_btn = Button(text='ثبت فروش')
        sell_btn.bind(on_release=self.save_sell_operation)
        self.sell_history = SimpleRV()
        self.sell_history.item_callback = lambda txt: self.on_history_item(txt, 'sell')
        self.sell_panel.add_widget(sell_form)
        self.sell_panel.add_widget(sell_btn)
        self.sell_panel.add_widget(Label(text='تاریخچه فروش ها:'))
        self.sell_panel.add_widget(self.sell_history)
        sell_item.add_widget(self.sell_panel)
        self.add_widget(sell_item)

        # Reports tab
        reports_item = TabbedPanelItem(text='گزارشات')
        self.reports_panel = BoxLayout(orientation='vertical')
        rpt_btns = GridLayout(cols=3, size_hint_y=None, height=80, padding=8, spacing=8)
        b1 = Button(text='سود روزانه')
        b1.bind(on_release=lambda x: self.report_daily())
        b2 = Button(text='موجودی')
        b2.bind(on_release=lambda x: self.report_inventory())
        b3 = Button(text='خلاصه کلی')
        b3.bind(on_release=lambda x: self.report_overall())
        rpt_btns.add_widget(b1)
        rpt_btns.add_widget(b2)
        rpt_btns.add_widget(b3)
        self.report_output = TextInput(readonly=True)
        self.reports_panel.add_widget(rpt_btns)
        self.reports_panel.add_widget(self.report_output)
        reports_item.add_widget(self.reports_panel)
        self.add_widget(reports_item)

        # Simple operations tab (buy/sell quick add)
        self.ops_panel = BoxLayout(orientation='vertical')
        self.ops_form = GridLayout(cols=2, size_hint_y=None, height=240, padding=10, spacing=10)
        self.ops_type = TextInput(text='sell', multiline=False)
        self.ops_entity = TextInput(multiline=False)
        self.ops_weight = TextInput(multiline=False)
        self.ops_price = TextInput(multiline=False)
        self.ops_form.add_widget(Label(text='نوع (buy/sell):'))
        self.ops_form.add_widget(self.ops_type)
        self.ops_form.add_widget(Label(text='کد مشتری/فروشنده:'))
        self.ops_form.add_widget(self.ops_entity)
        self.ops_form.add_widget(Label(text='وزن (کیلو):'))
        self.ops_form.add_widget(self.ops_weight)
        self.ops_form.add_widget(Label(text='قیمت/کیلو:'))
        self.ops_form.add_widget(self.ops_price)

        add_op_btn = Button(text='ثبت عملیات')
        add_op_btn.bind(on_release=self.add_operation)
        add_op_btn.size_hint = (None, None)
        add_op_btn.width = 240
        add_op_btn.height = 48
        add_op_btn.font_size = '16sp'

        self.ops_panel.add_widget(self.ops_form)
        self.ops_panel.add_widget(add_op_btn)

        self.add_widget(self.ops_panel)

        # bind Enter navigation
        self._bind_form_focus()

        self.refresh_lists()

    def on_history_item(self, text, typ):
        # text format: "id | date | entity | amount"
        parts = text.split('|')
        try:
            oid = int(parts[0].strip())
        except Exception:
            self.show_popup('خطا', 'شناسه عملیات نامعتبر است')
            return

        op = None
        op_list = None
        if typ == 'buy':
            op_list = self.db.get_buy_operations()
        elif typ == 'sell':
            op_list = self.db.get_sell_operations()
        elif typ == 'customer':
            # show customer details
            cust = self.db.get_all_customers().get(parts[0].strip())
            if cust:
                self.show_popup('مشتری', f"نام: {cust['name']}\nتلفن: {cust['phone']}")
            return
        elif typ == 'seller':
            sel = self.db.get_all_sellers().get(parts[0].strip())
            if sel:
                self.show_popup('فروشنده', f"نام: {sel['name']}\nتلفن: {sel['phone']}")
            return

        if op_list is not None:
            for o in op_list:
                if o.get('id') == oid:
                    op = o
                    break

        if not op:
            self.show_popup('خطا', 'عملیات یافت نشد')
            return

        # show detail popup with Edit/Delete
        content = BoxLayout(orientation='vertical', spacing=8, padding=10)
        content.add_widget(Label(text=f"تاریخ: {op.get('date')}", halign='right'))
        content.add_widget(Label(text=f"مبلغ: {format_currency(op.get('total_price',0))}", halign='right'))
        btns = BoxLayout(size_hint_y=None, height=44, spacing=8)
        edit_btn = Button(text='ویرایش')
        del_btn = Button(text='حذف')
        close_btn = Button(text='بستن')
        btns.add_widget(del_btn)
        btns.add_widget(edit_btn)
        btns.add_widget(close_btn)
        content.add_widget(btns)
        popup = Popup(title='جزئیات عملیات', content=content, size_hint=(0.9, None), height=260)

        def do_delete():
            def _del():
                try:
                    op_list.remove(op)
                    self.db.save_data()
                    self.refresh_lists()
                    self.show_popup('موفق', 'عملیات حذف شد')
                except Exception:
                    self.show_popup('خطا', 'حذف موفقیت‌آمیز نبود')
            popup.dismiss()
            self.show_confirm('تأیید حذف', 'آیا از حذف مطمئن هستید؟', _del)

        def do_edit():
            popup.dismiss()
            self.open_edit_popup(op, typ)

        edit_btn.bind(on_release=lambda *a: do_edit())
        del_btn.bind(on_release=lambda *a: do_delete())
        close_btn.bind(on_release=popup.dismiss)
        popup.open()

    def refresh_lists(self):
        customers = self.db.get_all_customers()
        self.customers_list.data = [{'text': f"{cid} | {c['name']}", 'callback': self.customers_list.item_callback} for cid, c in customers.items()]
        sellers = self.db.get_all_sellers()
        self.sellers_list.data = [{'text': f"{sid} | {s['name']}", 'callback': self.sellers_list.item_callback} for sid, s in sellers.items()]
        # quick counts shown in titles
        try:
            self.default_tab_text = f"مشتریان ({len(customers)})"
        except Exception:
            pass
        # update spinners and histories
        try:
            self.buy_seller.values = [f"{sid}" for sid in sellers.keys()]
            self.sell_customer.values = [f"{cid}" for cid in customers.keys()]
        except Exception:
            pass
        # histories
        self.buy_history.data = [{'text': f"{op['id']} | {op['date']} | {op.get('seller_id','')} | {format_currency(op.get('total_price',0))}", 'callback': self.buy_history.item_callback} for op in self.db.get_buy_operations()]
        self.sell_history.data = [{'text': f"{op['id']} | {op['date']} | {op.get('customer_id','')} | {format_currency(op.get('total_price',0))}", 'callback': self.sell_history.item_callback} for op in self.db.get_sell_operations()]

    # --------------------
    # UI helpers
    # --------------------
    def show_popup(self, title, message):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=message))
        btn = Button(text='باشه', size_hint=(1, None), height=44)
        content.add_widget(btn)
        popup = Popup(title=title, content=content, size_hint=(0.8, None), height=200)
        btn.bind(on_release=popup.dismiss)
        popup.open()

    def show_confirm(self, title, message, on_confirm):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=message))
        btns = BoxLayout(size_hint=(1, None), height=44, spacing=8)
        ok = Button(text='تأیید')
        cancel = Button(text='انصراف')
        btns.add_widget(cancel)
        btns.add_widget(ok)
        content.add_widget(btns)
        popup = Popup(title=title, content=content, size_hint=(0.85, None), height=220)
        ok.bind(on_release=lambda *a: (popup.dismiss(), on_confirm()))
        cancel.bind(on_release=popup.dismiss)
        popup.open()

    def add_customer(self, *args):
        cid = self.cust_id.text.strip()
        name = self.cust_name.text.strip()
        phone = self.cust_phone.text.strip()
        address = self.cust_address.text.strip()
        if not cid or not name:
            return
        self.db.add_customer(cid, name, phone, address)
        self.cust_id.text = self.cust_name.text = self.cust_phone.text = self.cust_address.text = ''
        self.refresh_lists()

        # focus navigation
    def _bind_form_focus(self):
        try:
            self.cust_id.bind(on_text_validate=lambda i: setattr(self.cust_name, 'focus', True))
            self.cust_name.bind(on_text_validate=lambda i: setattr(self.cust_phone, 'focus', True))
            self.cust_phone.bind(on_text_validate=lambda i: setattr(self.cust_address, 'focus', True))

            self.seller_id.bind(on_text_validate=lambda i: setattr(self.seller_name, 'focus', True))
            self.seller_name.bind(on_text_validate=lambda i: setattr(self.seller_phone, 'focus', True))
            self.seller_phone.bind(on_text_validate=lambda i: setattr(self.seller_address, 'focus', True))

            # buy form
            self.buy_seller.bind(on_text_validate=lambda i: setattr(self.buy_weight, 'focus', True))
            self.buy_weight.bind(on_text_validate=lambda i: setattr(self.buy_price, 'focus', True))
            self.buy_price.bind(on_text_validate=lambda i: setattr(self.buy_driver, 'focus', True))
            self.buy_driver.bind(on_text_validate=lambda i: setattr(self.buy_cheque, 'focus', True))
            self.buy_cheque.bind(on_text_validate=lambda i: setattr(self.buy_cash, 'focus', True))
            self.buy_cash.bind(on_text_validate=lambda i: setattr(self.buy_debt, 'focus', True))

            # sell form
            self.sell_customer.bind(on_text_validate=lambda i: setattr(self.sell_weight, 'focus', True))
            self.sell_weight.bind(on_text_validate=lambda i: setattr(self.sell_price, 'focus', True))
            self.sell_price.bind(on_text_validate=lambda i: setattr(self.sell_cheque, 'focus', True))
            self.sell_cheque.bind(on_text_validate=lambda i: setattr(self.sell_cash, 'focus', True))
            self.sell_cash.bind(on_text_validate=lambda i: setattr(self.sell_debt, 'focus', True))
        except Exception:
            pass

    def add_seller(self, *args):
        sid = self.seller_id.text.strip()
        name = self.seller_name.text.strip()
        phone = self.seller_phone.text.strip()
        address = self.seller_address.text.strip()
        if not sid or not name:
            return
        self.db.add_seller(sid, name, phone, address)
        self.seller_id.text = self.seller_name.text = self.seller_phone.text = self.seller_address.text = ''
        self.refresh_lists()

    def add_operation(self, *args):
        typ = self.ops_type.text.strip().lower()
        entity = self.ops_entity.text.strip()
        try:
            weight = float(self.ops_weight.text or 0)
            price = float(self.ops_price.text or 0)
        except Exception:
            return
        total = weight * price
        op = {
            'id': len(self.db.get_buy_operations() if typ=='buy' else self.db.get_sell_operations()) + 1,
            'invoice_number': self.db.get_next_invoice_number() if typ=='sell' else None,
            'date': get_current_shamsi_datetime(),
            'weight': weight,
            'price_per_kg': price,
            'total_price': total,
            'cheque_amount': 0,
            'cash_amount': total,
            'debt_amount': 0,
            'payment_method': 'cash'
        }
        if typ == 'buy':
            op['seller_id'] = entity
            self.db.add_buy_operation(op)
        else:
            op['customer_id'] = entity
            self.db.add_sell_operation(op)
        self.ops_entity.text = self.ops_weight.text = self.ops_price.text = ''
        self.refresh_lists()

    def get_weighted_average_buy_costs(self):
        total_weight = 0
        total_cost = 0
        total_driver = 0
        for op in self.db.get_buy_operations():
            w = op.get('weight', 0)
            total_weight += w
            total_cost += op.get('price_per_kg', 0) * w
            total_driver += op.get('driver_salary', 0)
        avg_price = (total_cost / total_weight) if total_weight > 0 else 0
        avg_driver_per_kg = (total_driver / total_weight) if total_weight > 0 else 0
        return avg_price, avg_driver_per_kg

    def save_buy_operation(self, *args):
        try:
            seller_id = self.buy_seller.text if self.buy_seller.text != 'انتخاب فروشنده' else ''
            weight = float(self.buy_weight.text or 0)
            price = float(self.buy_price.text or 0)
            driver = float(self.buy_driver.text or 0)
            cheque = float(self.buy_cheque.text or 0)
            cash = float(self.buy_cash.text or 0)
            debt = float(self.buy_debt.text or 0)
        except Exception:
            self.show_popup('خطا', 'لطفاً مقادیر عددی معتبر وارد کنید')
            return

        total = weight * price
        if abs((cheque + cash + debt) - total) > 1:
            self.show_popup('خطا', f"جمع پرداخت‌ها با قیمت کل همخوانی ندارد ({format_currency(cheque+cash+debt)} ≠ {format_currency(total)})")
            return

        def _do_save():
            op = {
                'id': len(self.db.get_buy_operations()) + 1,
                'date': get_current_shamsi_datetime(),
                'seller_id': seller_id,
                'weight': weight,
                'price_per_kg': price,
                'total_price': total,
                'cheque_amount': cheque,
                'cash_amount': cash,
                'debt_amount': debt,
                'driver_salary': driver,
                'payment_method': 'mixed'
            }
            self.db.add_buy_operation(op)
            self.buy_weight.text = self.buy_price.text = self.buy_driver.text = ''
            self.buy_cheque.text = self.buy_cash.text = self.buy_debt.text = ''
            self.refresh_lists()
            self.show_popup('موفق', f"خرید با مبلغ {format_currency(total)} ثبت شد")

        # confirm
        self.show_confirm('تأیید ثبت خرید', f"آیا مایل به ثبت خرید به مبلغ {format_currency(total)} هستید؟", _do_save)

    def save_sell_operation(self, *args):
        try:
            customer_id = self.sell_customer.text if self.sell_customer.text != 'انتخاب مشتری' else ''
            weight = float(self.sell_weight.text or 0)
            price = float(self.sell_price.text or 0)
            cheque = float(self.sell_cheque.text or 0)
            cash = float(self.sell_cash.text or 0)
            debt = float(self.sell_debt.text or 0)
        except Exception:
            self.show_popup('خطا', 'لطفاً مقادیر عددی معتبر وارد کنید')
            return

        total = weight * price
        if abs((cheque + cash + debt) - total) > 1:
            self.show_popup('خطا', f"جمع پرداخت‌ها با قیمت کل همخوانی ندارد ({format_currency(cheque+cash+debt)} ≠ {format_currency(total)})")
            return

        avg_buy, avg_driver = self.get_weighted_average_buy_costs()
        cost_per_kg = avg_buy + avg_driver
        cost_total = cost_per_kg * weight
        pure_profit = (price - cost_per_kg) * weight

        def _do_save():
            op = {
                'id': len(self.db.get_sell_operations()) + 1,
                'invoice_number': self.db.get_next_invoice_number(),
                'date': get_current_shamsi_datetime(),
                'customer_id': customer_id,
                'weight': weight,
                'price_per_kg': price,
                'total_price': total,
                'cheque_amount': cheque,
                'cash_amount': cash,
                'debt_amount': debt,
                'payment_method': 'mixed',
                'cost_price_per_kg': cost_per_kg,
                'cost_total': cost_total,
                'pure_profit': pure_profit
            }
            self.db.add_sell_operation(op)
            self.sell_weight.text = self.sell_price.text = ''
            self.sell_cheque.text = self.sell_cash.text = self.sell_debt.text = ''
            self.refresh_lists()
            self.show_popup('موفق', f"فاکتور شماره {to_persian_digits(op['invoice_number'])} صادر شد — مبلغ {format_currency(total)}")

        self.show_confirm('تأیید صدور فاکتور', f"آیا مایل به صدور فاکتور به مبلغ {format_currency(total)} هستید؟", _do_save)

    def report_daily(self):
        profit = 0
        today = get_current_shamsi_datetime().split(' ')[0]
        for op in self.db.get_sell_operations():
            if op.get('date','').split(' ')[0] == today:
                profit += op.get('pure_profit', 0)
        self.report_output.text = f"سود خالص امروز: {format_currency(profit)}"

    def report_inventory(self):
        total_bought = sum(op.get('weight',0) for op in self.db.get_buy_operations())
        total_sold = sum(op.get('weight',0) for op in self.db.get_sell_operations())
        remaining = total_bought - total_sold
        # use Persian formatting for numbers
        self.report_output.text = f"موجودی فعلی: {to_persian_digits(f'{remaining:,.1f}')} کیلوگرم"

    def report_overall(self):
        total_buy = sum(op.get('total_price',0) for op in self.db.get_buy_operations())
        total_sell = sum(op.get('total_price',0) for op in self.db.get_sell_operations())
        self.report_output.text = f"مجموع خرید: {format_currency(total_buy)}\nمجموع فروش: {format_currency(total_sell)}\nسود تخمینی: {format_currency(total_sell-total_buy)}"

    def open_edit_popup(self, op, typ):
        # generic edit popup for buy/sell
        win = BoxLayout(orientation='vertical', spacing=8, padding=10)
        form = GridLayout(cols=2, size_hint_y=None, height=260)
        w_in = TextInput(text=str(op.get('weight',0)), multiline=False)
        p_in = TextInput(text=str(op.get('price_per_kg',0)), multiline=False)
        c_in = TextInput(text=str(op.get('cheque_amount',0)), multiline=False)
        cash_in = TextInput(text=str(op.get('cash_amount',0)), multiline=False)
        d_in = TextInput(text=str(op.get('debt_amount',0)), multiline=False)
        form.add_widget(Label(text='وزن (کیلو):'))
        form.add_widget(w_in)
        form.add_widget(Label(text='قیمت/کیلو:'))
        form.add_widget(p_in)
        form.add_widget(Label(text='مبلغ چک:'))
        form.add_widget(c_in)
        form.add_widget(Label(text='مبلغ نقدی:'))
        form.add_widget(cash_in)
        form.add_widget(Label(text='مبلغ بدهکاری:'))
        form.add_widget(d_in)
        win.add_widget(form)
        btns = BoxLayout(size_hint_y=None, height=44, spacing=8)
        saveb = Button(text='ذخیره')
        cancelb = Button(text='انصراف')
        btns.add_widget(cancelb)
        btns.add_widget(saveb)
        win.add_widget(btns)
        popup = Popup(title='ویرایش عملیات', content=win, size_hint=(0.95, None), height=420)

        def do_save(*a):
            try:
                weight = float(w_in.text or 0)
                price = float(p_in.text or 0)
                cheque = float(c_in.text or 0)
                cash = float(cash_in.text or 0)
                debt = float(d_in.text or 0)
            except Exception:
                self.show_popup('خطا', 'لطفاً مقادیر عددی معتبر وارد کنید')
                return
            total = weight * price
            if abs((cheque + cash + debt) - total) > 1:
                self.show_popup('خطا', 'جمع پرداخت‌ها با قیمت کل همخوانی ندارد')
                return
            op['weight'] = weight
            op['price_per_kg'] = price
            op['total_price'] = total
            op['cheque_amount'] = cheque
            op['cash_amount'] = cash
            op['debt_amount'] = debt
            # update driver if present
            if 'driver_salary' in op:
                # keep existing driver or 0
                pass
            try:
                self.db.save_data()
            except Exception:
                pass
            popup.dismiss()
            self.refresh_lists()
            self.show_popup('موفق', 'ویرایش با موفقیت انجام شد')

        saveb.bind(on_release=do_save)
        cancelb.bind(on_release=popup.dismiss)
        popup.open()


class EggApp(App):
    def build(self):
        root = BoxLayout(orientation='vertical')
        # header with current shamsi datetime
        self.header = Label(text=get_current_shamsi_datetime(), size_hint_y=None, height=48,
                            halign='right', valign='middle', font_size='18sp')
        # ensure right alignment
        self.header.bind(size=lambda w, h: setattr(self.header, 'text_size', (self.header.width - 20, None)))
        Clock.schedule_interval(self._update_header, 1)
        root.add_widget(self.header)

        self.ui = EggAppUI()
        root.add_widget(self.ui)
        return root

    def _update_header(self, dt):
        try:
            self.header.text = get_current_shamsi_datetime()
        except Exception:
            pass


if __name__ == '__main__':
    EggApp().run()
