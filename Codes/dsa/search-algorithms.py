cards = [13, 12, 11, 7, 4, 2, 1]
query = 7
output = -1

# linear search - bruteforce solution

for card in cards:
    # print(card)
    if card == query:
        output = card

print(output)


# Numbers must be ordered in the list for binary search to work (either descending or ascending)
# descending is worst case, ascending is best case

# Need a program to find the numbers position with least number of lookups to the list


tests = []

# cards.sort()
# print(cards)