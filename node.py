from blockchain import Blockchain
from utility.verification import Verification
from uuid import uuid4
from wallet import Wallet


class Node:
    def __init__(self):
        # self.id = str(uuid4())
        self.wallet = Wallet()
        self.blockchain = Blockchain(self.wallet.public_key)

    def get_transaction_value(self):
        """ Returns the input of the user (a new transaction amount) as a float. """
        recipient = input('Enter the recipient of the transaction: ')
        amount = float(input('Your transaction amount please: '))
        return recipient, amount

    def get_user_choice(self):
        """Prompts the user for its choice and return it."""
        return input('Your choice: ')

    def print_blockchain_elements(self):
        """ Output all blocks of the blockchain. """
        # Output the blockchain list to the console
        for block in self.blockchain.chain:
            print('Outputing Block')
            print(block)
        else:
            print('_' * 20)

    def listen_for_input(self):
        user_choice = None
        # A while loop for the user input interface
        # It's a loop until the user choice is 'q'
        while user_choice != 'q':
            print('Please choose:')
            print('1: Add a new transaction value')
            print('2: Mine a new block')
            print('3: Output the blockchain blocks')
            print('4: Check transaction validity')
            print('5: Create wallet')
            print('6: Load wallet')
            print('q: Quit')
            user_choice = self.get_user_choice()
            if user_choice == '1':
                recipient, amount = self.get_transaction_value()
                # Add the transaction amount to the blockchain
                if self.blockchain.add_transaction(recipient, self.wallet.public_key, amount=amount):
                    print('Added transaction!')
                else:
                    print('Transaction failed!')
                    print(self.blockchain.get_open_transactions())
            elif user_choice == '2':
                self.blockchain.mine_block()
            elif user_choice == '3':
                self.print_blockchain_elements()
            elif user_choice == '4':
                if Verification.verify_transactions(self.blockchain.get_open_transactions(), self.blockchain.get_balance):
                    print('All verified transactions are valid')
                else:
                    print('There are invalid transactions')
            elif user_choice == '5':
                self.wallet.create_keys()
            elif user_choice == '6':
                pass
            elif user_choice == 'q':
                # This will lead to the loop to exist
                break
            else:
                print('Input was invalid, please pick a value from the list!')
            if not Verification.verify_chain(self.blockchain.chain):
                self.print_blockchain_elements()
                print('Invalid blockchain!')
                break
            print(
                f'Balance of {self.wallet}: {self.blockchain.get_balance():6.2f}')
        else:
            print('User left!')
        print('Done')


if __name__ == '__main__':
    node = Node()
    node.listen_for_input()
