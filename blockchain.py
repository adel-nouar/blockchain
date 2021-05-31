from functools import reduce
import hashlib as hl

import json
import pickle

# Import two functions from our hash_util.py file. Omit the ".py" in the import
from hash_util import hash_block, hash_string_256
from block import Block
from transaction import Transaction

# The reward we give to miners (for creating a new bloc)
MINING_REWARD = 10

# Initializing our (empty) blockchain list
blockchain = []
# Unhandled transactions
open_transactions = []
# We are the owner of this blockchain node, hence this is our identifier (e.g. for sending coins)
owner = 'Someone'


def load_data():
    """Initialize blockchain + open transactions data from a file."""
    global blockchain
    global open_transactions
    try:
        with open('blockchain.json', mode='r') as f:
            # file_content = pickle.loads(f.read())
            file_content = f.readlines()
            # blockchain = file_content['chain']
            # open_transactions = file_content['ot']
            blockchain = json.loads(file_content[0][:-1])
            # We need to convert  the loaded data because Transactions should use OrderedDict
            updated_blockchain = []
            for block in blockchain:
                converted_tx = [Transaction(
                    tx['sender'], tx['recipient'], tx['amount']) for tx in block['transactions']]
                # converted_tx = [OrderedDict(
                #     [('sender', tx['sender']), ('recipient', tx['recipient']), ('amount', tx['amount'])])
                #     for tx in block['transactions']]
                updated_block = Block(
                    block['index'], block['previous_hash'], converted_tx, block['proof'], block['timestamp'])
                # updated_block = {
                #     'previous_hash': block['previous_hash'],
                #     'index': block['index'],
                #     'proof': block['proof'],
                #     'transactions': [OrderedDict(
                #         [('sender', tx['sender']), ('recipient', tx['recipient']), ('amount', tx['amount'])])
                #         for tx in block['transactions']]
                # }
                updated_blockchain.append(updated_block)
            blockchain = updated_blockchain
            open_transactions = json.loads(file_content[1])
            # We need to convert  the loaded data because Transactions should use OrderedDict
            updated_transactions = []
            for tx in open_transactions:
                updated_transaction = Transaction(
                    tx['sender'], tx['recipient'], tx['amount'])
                # updated_transaction = OrderedDict(
                #     [('sender', tx['sender']), ('recipient', tx['recipient']), ('amount', tx['amount'])])
                updated_transactions.append(updated_transaction)
            open_transactions = updated_transactions
    except (IOError, IndexError):
        # Our starting block for the blockchain
        genesis_block = Block(0, '', [], 100, 0)
        # genesis_block = {
        #     'previous_hash': '',
        #     'index': 0,
        #     'transactions': [],
        #     'proof': 100
        # }
        # Initializing our (empty) blockchain list
        blockchain = [genesis_block]
        # Unhandled transactions
        open_transactions = []
    finally:
        print('Cleanup!')


load_data()


def save_data():
    """Save blockchain + open transactions snapshot to a file."""
    try:
        with open('blockchain.json', mode='w') as f:
            saveable_chain = [block.__dict__ for block in [Block(block_el.index, block_el.previous_hash, [
                                                                 tx.__dict__ for tx in block_el.transactions], block_el.proof, block_el.timestamp) for block_el in blockchain]]
            # f.write(json.dumps(blockchain))
            f.write(json.dumps(saveable_chain))
            f.write('\n')
            saveable_tx = [tx.__dict__ for tx in open_transactions]
            f.write(json.dumps(saveable_tx))
            # save_data = {
            #     'chain': blockchain,
            #     'ot': open_transactions
            # }
            # f.write(pickle.dumps(save_data))
    except IOError:
        print('Saving failed!')


def valid_proof(transactions, last_hash, proof):
    """Validate a proof of work number and see if it solves the puzzle algorithm (two leading 0s)

    Arguments:
          :transactions: The transactions of the block for which the proof is created.
          :last_hash: The previous block's hash which will be stored in the current block.
          :proof: The proof number we're testing.
    """
    # Create a string with all the hash inputs
    guess = (str([tx.to_ordered_dict() for tx in transactions]) +
             str(last_hash) + str(proof)).encode()
    # Hash the string
    # IMPORTANT: This is NOT the same hash as will be stored in the previous_hash. It's a not a block's hash. It'    s only used for the proof-of-work algorithm.
    guess_hash = hash_string_256(guess)
    # Only a hash (which is based on the above inputs) which starts with two 0s is treated as valid
    # This condition is of course defined by you. You could also require 10 leading 0s - this would take significantly longer (and this allows you to control the speed at which new blocks can be added)
    return guess_hash[0:2] == '00'


def proof_of_work():
    """Generate a proof of work for the open transactions, the hash of the previous block and a random number (wh    ich is guessed until it fits)."""
    last_block = blockchain[-1]
    last_hash = hash_block(last_block)
    proof = 0
    # Try different PoW numbers and return the first valid one
    while not valid_proof(open_transactions, last_hash, proof):
        proof += 1
    return proof


def get_balance(participant):
    """Calculate and return the balance for a participant.

    Arguments:
        :participant: The person for whom to calculate the balance.
    """
    # Fetch a list of all sent coin amounts for the given person (empty lists are returned if the person was NOT     the sender)
    # This fetches sent amounts of transactions that were already included in blocks of the blockchain
    tx_sender = [[tx.amount for tx in block.transactions
                  if tx.sender == participant] for block in blockchain]

    # Fetch a list of all sent coin amounts for the given person (empty lists are returned if the person was NOT     the sender)
    # This fetches sent amounts of open transactions (to avoid double spending)
    open_tx_sender = [tx.amount
                      for tx in open_transactions if tx.sender in participant]
    tx_sender.append(open_tx_sender)
    amount_sent = reduce(
        lambda tx_sum, tx_amt: tx_sum +
        sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_sender, 0
    )
    # amount_sent = 0
    # for tx in tx_sender:
    #     if len(tx) > 0:
    #         amount_sent += tx[0]

    # This fetches received coin amounts of transactions that were already included in blocks of the blockchain
    # We ignore open transactions here because you shouldn't be able to spend coins before the transaction was confirmed + included in a block
    tx_recipient = [[tx.amount for tx in block.transactions
                     if tx.recipient == participant] for block in blockchain]
    amount_received = reduce(
        lambda tx_sum, tx_amt: tx_sum +
        sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_recipient, 0
    )
    # amount_received = 0
    # for tx in tx_recipient:
    #     if len(tx) > 0:
    #         amount_received += tx[0]

    # Return the total balance
    return amount_received - amount_sent


def get_last_blockchain_value():
    """ Returns the last value of the current blockchain. """
    if len(blockchain) < 1:
        return None
    return blockchain[-1]


def verify_transaction(transaction):
    """Verify a transaction by checking whether the sender has sufficient coins.

    Arguments:
        :transaction: The transaction that should be verified.
    """
    sender_balance = get_balance(transaction.sender)
    return sender_balance >= transaction.amount

# This function accpets two arguments.
# One required (transition_amount) and one optional (last_transaction)
# The optional one is optional because it has a default value => [1]


def add_transaction(recipient, sender=owner, amount=1.0):
    """ Append a new value as well as the last blockchain value to the blockchain.

    Arguments:
        :sender: The sender of the coins.
        :recipient: The recipient of the coins.
        :amount: The amount of coins sent with the transaction(default = 1.0)
    """
    # transaction = {
    #     'sender': sender,
    #     'recipient': recipient,
    #     'amount': amount
    # }
    transaction = Transaction(sender, recipient, amount)
    # transaction = OrderedDict(
    #     [('sender', sender), ('recipient', recipient), ('amount', amount)])
    if verify_transaction(transaction):
        open_transactions.append(transaction)
        # participants.add(sender)
        # participants.add(recipient)
        save_data()
        return True
    return False


def mine_block():
    """Create a new block and add open transactions to it."""
    # Fetch the currently last block of the blockchain
    last_block = blockchain[-1]
    # Hash the last block (=> to be able to compare it to the stored hash value)
    hashed_block = hash_block(last_block)
    proof = proof_of_work()
    # Miners should be rewarded, so let's create a reward transaction
    # reward_transaction = {
    #     'sender': 'MINING',
    #     'recipient': owner,
    #     'amount': MINING_REWARD
    # }
    reward_transaction = Transaction('MINING', owner, MINING_REWARD)
    # reward_transaction = OrderedDict(
    #     [('sender', 'MINING'), ('recipient', owner), ('amount', MINING_REWARD)])
    # Copy transaction instead of manipulating the original open_transactions list
    # This ensures that if for some reason the mining should fail, we don't have the reward transaction stored in the open transactions
    copied_transaction = open_transactions.copy()
    copied_transaction.append(reward_transaction)
    block = Block(len(blockchain), hashed_block, copied_transaction, proof)
    # block = {
    #     'previous_hash': hashed_block,
    #     'index': len(blockchain),
    #     'transactions': copied_transaction,
    #     'proof': proof
    # }
    blockchain.append(block)
    return True


def get_transaction_value():
    """ Returns the input of the user (a new transaction amount) as a float. """
    recipient = input('Enter the recipient of the transaction: ')
    amount = float(input('Your transaction amount please: '))
    return recipient, amount


def get_user_choice():
    """Prompts the user for its choice and return it."""
    return input('Your choice: ')


def print_blockchain_elements():
    """ Output all blocks of the blockchain. """
    # Output the blockchain list to the console
    for block in blockchain:
        print('Outputing Block')
        print(block)
    else:
        print('_' * 20)


def verify_chain():
    """ Verify the current blockchain and return True if it's valid, False otherwise. """
    for (index, block) in enumerate(blockchain):
        if index == 0:
            continue
        if block.previous_hash != hash_block(blockchain[index - 1]):
            return False
        if not valid_proof(block.transactions[:-1], block.previous_hash, block.proof):
            print('Proof of work is invalid')
            return False
    return True


def verify_transactions():
    """Verifies all open transactions."""
    return all([verify_transaction(tx) for tx in open_transactions])
    # is_valid = True
    # for tx in open_transactions:
    #     if verify_transaction(tx):
    #         is_valid = True
    #     else:
    #         is_valid = False
    # return is_valid


user_choice = None

# A while loop for the user input interface
# It's a loop until the user choice is 'q'
while user_choice != 'q':
    print('Please choose:')
    print('1: Add a new transaction value')
    print('2: Mine a new block')
    print('3: Output the blockchain blocks')
    # print('4: Output participants')
    print('4: Check transaction validity')
    # print('h: Manipulate the chain')
    print('q: Quit')
    user_choice = get_user_choice()
    if user_choice == '1':
        recipient, amount = get_transaction_value()
        # Add the transaction amount to the blockchain
        if add_transaction(recipient, amount=amount):
            print('Added transaction!')
        else:
            print('Transaction failed!')
    elif user_choice == '2':
        if mine_block():
            open_transactions = []
            save_data()
    elif user_choice == '3':
        print_blockchain_elements()
    # elif user_choice == '4':
    #     print(participants)
    elif user_choice == '4':
        if verify_transactions():
            print('All verified transactions are valid')
        else:
            print('There are invalid transactions')
    # elif user_choice == 'h':
    #     # Make sure that you don't try to "hack" the blockchain if it's empty
    #     if len(blockchain) >= 1:
    #         blockchain[0] = {
    #             'previous_hash': '',
    #             'index': 0,
    #             'transactions': [{'sender': 'Chris', 'recipient': 'Max', 'amount': 100.0}]
    #         }

    elif user_choice == 'q':
        # This will lead to the loop to exist
        break
    else:
        print('Input was invalid, please pick a value from the list!')
    if not verify_chain():
        print_blockchain_elements()
        print('Invalid blockchain!')
        break
    print(f'Balance of {owner}: {get_balance(owner):6.2f}')
else:
    print('User left!')
print('Done')
