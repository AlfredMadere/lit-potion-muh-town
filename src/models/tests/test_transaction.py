import logging
from ..transaction import Transaction
from ..invoice import Invoice

Transaction.reset()
Invoice.reset()
def test_get_current_balance():
  current_balance = Transaction.get_current_balance()
  assert current_balance == 100

def test_create():
  invoice_id = Invoice.create(None, None, "test invoice")
  result = Transaction.create(100, invoice_id)
  assert result == "OK"
  current_balance = Transaction.get_current_balance()
  assert current_balance == 200