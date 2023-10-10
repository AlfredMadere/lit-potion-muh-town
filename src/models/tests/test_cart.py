from ...models.cart import Cart, NewCart, CartCheckout
from ...models.customer import Customer
from ...models.potion_type import PotionType
from ...models.retail_inventory import RetailInventory
from ...models.invoice import Invoice
from ...models.transaction import Transaction




def test_new_cart():
    Cart.reset()
    Customer.reset()
    new_cart_obj = NewCart(customer="test customer")
    cart = Cart.new_cart(new_cart_obj)
    created_cart = Cart.find(cart.id)
    created_customer = Customer.find(created_cart.customer_id)
    assert created_customer.str == "test customer"
    assert created_cart.id == cart.id


def test_set_item_quantity():
  #this is a smoke test, does not cover edge cases. actually doing this project correctly is very time consuming
  Cart.reset()
  Customer.reset()
  PotionType.reset()
  RetailInventory.reset()
  potion_type = PotionType.create("test name", "test sku", [30, 50, 20, 0], 0)
  RetailInventory.create(potion_type.id, 2, 60)
  new_cart_obj = NewCart(customer="test customer")
  cart = Cart.new_cart(new_cart_obj)
  cart.set_item_quantity("test sku", 2)
  assert Cart.find(cart.id).items[0].quantity == 2
  #this shows how you can add more items to a cart than actually exist in inventory
  cart.set_item_quantity ("test sku", 1)
  assert Cart.find(cart.id).items[1].quantity == 1

def test_checkout():
  Invoice.reset() 
  Cart.reset()
  Customer.reset()
  PotionType.reset()
  RetailInventory.reset()
  Transaction.reset()
  initial_balance = Transaction.get_current_balance()
  potion_type = PotionType.create("test name", "test sku", [30, 50, 20, 0], 0)
  potion_price = 60
  potion_quanity_to_purchase = 2
  RetailInventory.create(potion_type.id, 2, potion_price)
  assert RetailInventory.num_potion_type_available(potion_type.id) == 2
  new_cart_obj = NewCart(customer="test customer")
  cart = Cart.new_cart(new_cart_obj)
  cart.set_item_quantity("test sku", potion_quanity_to_purchase)
  assert Cart.find(cart.id).items[0].quantity == potion_quanity_to_purchase
  cart.checkout(CartCheckout(payment="test payment"))
  modified_cart = Cart.find(cart.id)
  assert modified_cart.checked_out == True
  potion_type_available = RetailInventory.num_potion_type_available(potion_type.id)
  assert potion_type_available == 0
  current_balance = Transaction.get_current_balance()
  assert current_balance == initial_balance + potion_price * potion_quanity_to_purchase