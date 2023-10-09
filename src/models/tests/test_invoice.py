import logging
from ..transaction import Transaction
from ..invoice import Invoice

Transaction.reset()
def test_create_invoice():
  invoice = Invoice.create(None, None, "test invoice") 
  assert invoice == 2
