class CoffeeMachine:
    def __init__(self, water: int, milk: int, beans: int, cups: int, money: int):
        """
        Simulates interacting with a virtual coffee machine.

        :param water: int - volume of water
        :param milk: int - volume of milk
        :param beans: int - volume of beans
        :param cups: int - volume of cups
        :param money: int - volume of money
        """
        self.action = None
        self.inventory = {"water": water,
                          "milk": milk,
                          "beans": beans,
                          "cups": cups,
                          "money": money}
        while True:
            self.action = input("Write action (buy, fill, take, remaining, exit):\n")
            print()
            if self.action == "take":
                self.take()
            elif self.action == "fill":
                self.fill()
            elif self.action == "buy":
                self.buy()
            elif self.action == "remaining":
                self.print_stats()
            elif self.action == "exit":
                break

    def buy(self):
        """
        Takes input from user and determines what drink a customer wants to buy.
        :return:
        """
        buy_type = input("What do you want to buy? 1 - espresso, 2 - latte, 3 - cappuccino, back - to main menu:\n")
        if buy_type == "1":
            self.buy_espresso()
        elif buy_type == "2":
            self.buy_latte()
        elif buy_type == "3":
            self.buy_cappuccino()
        elif buy_type == "back":
            pass
        else:
            pass

    def buy_generic(self, water_needed: int, milk_needed: int, beans_needed: int, price: int):
        """
        Generic method for buying drinks. Values are provided by drink-specific calling methods.

        :param water_needed: int - volume of water required to create the drink.
        :param milk_needed: int - volume of milk required to create the drink.
        :param beans_needed: int - volume of beans required to create the drink.
        :param price: int - how much money to collect from the customer.
        :return:
        """
        temp_inventory = self.inventory.copy()
        temp_inventory["water"] -= water_needed
        temp_inventory["milk"] -= milk_needed
        temp_inventory["beans"] -= beans_needed
        temp_inventory["cups"] -= 1
        temp_inventory["money"] += price
        missing_items = ""
        # Scan for missing items
        for item in temp_inventory:
            if temp_inventory[item] < 0:
                if missing_items:
                    missing_items += ", " + item
                else:
                    missing_items += item
        if missing_items:
            print(f"Sorry, not enough {missing_items}!")
        else:
            print("I have enough resources, making you a coffee!")
            self.inventory = temp_inventory.copy()
        print()

    def buy_espresso(self):
        self.buy_generic(250, 0, 16, 4)

    def buy_latte(self):
        self.buy_generic(350, 75, 20, 7)

    def buy_cappuccino(self):
        self.buy_generic(200, 100, 12, 6)

    def fill(self):
        self.inventory["water"] += int(input("Write how many ml of water you want to add:\n"))
        self.inventory["milk"] += int(input("Write how many ml of milk you want to add:\n"))
        self.inventory["beans"] += int(input("Write how many grams of coffee beans you want to add:\n"))
        self.inventory["cups"] += int(input("Write how many disposable cups you want to add:\n"))
        print()

    def take(self):
        money = str(self.inventory["money"])
        print(f"I gave you ${money}")
        print()
        self.inventory["money"] = 0

    def print_stats(self):
        print("The coffee machine has:")
        print(f"{self.inventory.get('water')} ml of water")
        print(f"{self.inventory.get('milk')} ml of milk")
        print(f"{self.inventory.get('beans')} g of coffee beans")
        print(f"{self.inventory.get('cups')} disposable cups")
        print(f"${self.inventory.get('money')} of money")
        print()


CoffeeMachine(400, 540, 120, 9, 550)