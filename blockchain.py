# Initializing our blockchain list
genesis_block = {
    'previous_hash': '',
    'index': 0,
    'transactions': []
}
blockchain = [genesis_block]
open_transaction = []
owner = 'Someone'


def get_last_blockchain_value():
    """ Returns the last value of the current blockchain. """
    if len(blockchain) < 1:
        return None
    return blockchain[-1]


def add_transaction(recipient, sender=owner, amount=1.0):
    """ Append a new value as well as the last blockchain value to the blockchain.

    Arguments:
        :sender: The sender of the coins.
        :recipient: The recipient of the coins.
        :amount: The amount of coins sent with the transaction(default = 1.0)
    """
    transaction = {
        'sender': sender,
        'recipient': recipient,
        'amount': amount}
    open_transaction.append(transaction)


def mine_block():
    last_block = blockchain[-1]
    hashed_block = ''.join(str([last_block[key]) for key in last_block])
    for key in last_block:
        value = last_block[key]
        hashed_block = hashed_block + str(value)
    block = {
        'previous_hash': hashed_block,
        'index': len(blockchain),
        'transactions': open_transaction
    }
    blockchain.append(block)


def get_transaction_value():
    """ Returns the input of the user (a new transaction amount) as a float. """
    recipient = input('Enter the recipient of the transaction: ')
    amount = float(input('Your transaction amount please: '))
    return recipient, amount


def get_user_choice():
    return input('Your choice: ')


def print_blockchain_elements():
    # Output the blockchain list to the console
    for block in blockchain:
        print('Outputing Block')
        print(block)
    else:
        print('_' * 20)


def verify_chain():
    block_index = 0
    is_valid = True
    for block_index in range(len(blockchain)):
        if block_index == 0:
            continue
        elif blockchain[block_index][0] == blockchain[block_index - 1]:
            is_valid = True
        else:
            is_valid = False
            break
    # for block in blockchain:
    #     if block_index == 0:
    #         block_index += 1
    #         continue
    #     elif block[0] == blockchain[block_index - 1]:
    #         is_valid = True
    #     else:
    #         is_valid = False
    #         break
    #     block_index += 1
    return is_valid


user_choice = None
while user_choice != 'q':
    print('Please choose:')
    print('1: Add a new transaction value')
    print('2: Mine a new block')
    print('3: Output the blockchain blocks')
    print('h: Manipulate the chain')
    print('q: Quit')
    user_choice = get_user_choice()
    if user_choice == '1':
        recipient, amount = get_transaction_value()
        add_transaction(recipient, amount=amount)
    elif user_choice == '2':
        mine_block()
    elif user_choice == '3':
        print_blockchain_elements()
    elif user_choice == 'h':
        if len(blockchain) >= 1:
            blockchain[0] = [2]
    elif user_choice == 'q':
        break
    else:
        print('Input was invalid, please pick a value from the list!')
    # if not verify_chain():
    #     print('Invalid blockchain!')
    #     break
else:
    print('User left!')
print('Done')
