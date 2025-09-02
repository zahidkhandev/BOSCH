class BankAccount:
    
    def __init__(self, account_number, account_holder, balance, interest_rate):
        self.account_number = account_number
        self.account_holder = account_holder
        self.balance = balance if (balance != 0 or None) else 0
        self.interest_rate = interest_rate

    def deposit(self, amount):
        if (amount < 0):
            print("Deposit failed, please enter a value greater than 0")
            return

        self.balance += amount
        print(f"Deposited of {amount} to {self.account_number} successful. New balance: {self.balance}")

    
    def getBalance(self):
        print(f"Balance of account {self.account_number}: {self.balance}")

    def __str__(self):
        return f"\nAccount Number: {self.account_number}, Account Holder: {self.account_holder}, Account balance: {self.balance}\n"
    

    def applyInterest(self):
        interest_amount = int(self.balance) * int(self.interest_rate) / 100
        self.balance += interest_amount
        print(f"Interest of {interest_amount} has been credited, closing balance: {self.balance}")
    
    
class CurrentAccount(BankAccount):
    
    def __init__(self,account_number, account_holder, balance, interest_rate,overdraft_limit):
        super().__init__(account_number, account_holder, balance, interest_rate)
        self.overdraft_limit = overdraft_limit
    
    
    def withdraw(self, amount):
        if amount < 0:
            print("Widthrawal failed, please enter a value greater than 0")
            return 0
        if self.balance - amount >= -self.overdraft_limit:
            self.balance -= amount
            print(f"Withdrawal of {amount} from {self.account_number} successful. New balance: {self.balance}")
            return 1
        else:
            print("Withdrawal denied. Amount exceeds overdraft limit.")
            return 0

    
    def transfer(self, destination_account, amount):
            print("\nTransfer initiated...")
            if not isinstance(destination_account, BankAccount):
                print("Error: Destination must be a BankAccount object.")
                return False

            if self.withdraw(amount):
                destination_account.deposit(amount)
                print(f"\nTransfer of {amount} from {self.account_number} to {destination_account.account_number} successful.\n")
                return True
            else:
                print(f"Transfer failed: Insufficient funds in account {self.account_number} or invalid amount.")
                return False


person1 = CurrentAccount(account_number="12345", account_holder="John", balance=5000, interest_rate=10, overdraft_limit=1000)

person1.deposit(1000)
person1.withdraw(5000)
person1.getBalance()
person1_bank_info = person1.__str__()
print(person1_bank_info)

person1.applyInterest()
person1.getBalance()

person1.withdraw(3000)
person1.withdraw(1500)
person1.withdraw(-10)
person1.deposit(-10)

print("\n")
person2 = CurrentAccount(account_number="54321", account_holder="Sam", balance=25000, interest_rate=10, overdraft_limit=1000)
person2.getBalance()
person2.transfer(destination_account=person1, amount=10000)

person1.getBalance()
person2.getBalance()