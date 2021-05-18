blockchain = [1]


def add_value():
    blockchain.append([blockchain[0], 5.3])
    print(blockchain)


add_value()
add_value()
add_value()
