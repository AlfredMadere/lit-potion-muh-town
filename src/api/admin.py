from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
from ..models.global_inventory import GlobalInventory, PotionInventory
from ..models.cart import Cart
from ..models.retail_inventory import RetailInventory
from ..models.transaction import Transaction
from ..models.cart import Cart
from ..models.wholesale_inventory import WholesaleInventory
from ..models.customer import Customer
from ..models.invoice import Invoice
from ..models.cart_item import CartItemM



router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.post("/reset")
def reset():
    """
    Reset the game state. Gold goes to 100, all potions are removed from
    inventory, and all barrels are removed from inventory. Carts are all reset.
    """
    Cart.reset()
    Customer.reset()
    Invoice.reset()
    WholesaleInventory.reset()
    RetailInventory.reset() 
    Transaction.reset()

    return "OK"


@router.get("/shop_info/")
def get_shop_info():
    #TODO: implement get_shop_info
    """ """

    # TODO: Change me!
    return {
        "shop_name": "Lit Potion Muh Town",
        "shop_owner": "Potion King of Muh Town (Alfred)",
    }

