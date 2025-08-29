import random;

suits = ["hearts", "spades", "club", "diamonds"]
ranks= [
            {"rank": "A","value": 11}, 
            {"rank": "2","value": 2}, 
            {"rank": "3","value": 3},
            {"rank": "4","value": 4}, 
            {"rank": "5","value": 5}, 
            {"rank": "6","value": 6}, 
            {"rank": "7","value": 7}, 
            {"rank": "8","value": 8}, 
            {"rank": "9","value": 9}, 
            {"rank": "J","value": 10}, 
            {"rank": "Q","value": 10}, 
            {"rank": "A","value": 10}
        ]

cards = []

for rank in ranks:
    for suit in suits:
        cards.append([suit, rank])

def shuffle():
    random.shuffle(cards)

def deal(number):
    cards_dealt = []
    for x in range (number):
        cards_dealt.append(cards.pop())
    return cards_dealt

shuffle()

card = deal(1)[0]

# cards_dealt = deal(2)
# card = cards_dealt[0]
# rank = card[0]

# if rank == "A":
#     value = 11
# elif rank == "J" or rank == "K" or rank == "Q":
#     value = 10
# else:
#     value = rank

# rank_dict = {"rank": rank, "value": value}

# print(rank_dict["rank"], rank_dict["value"])