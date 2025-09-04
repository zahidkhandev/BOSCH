class HashMap:
    def __init__(self, size=10):
        self.size = size
        self.table = [[] for _ in range(self.size)]

    def _hash(self, key):
        return hash(key) % self.size

    def put(self, key, value):
        index = self._hash(key)
        found = False
        for i, (k, v) in enumerate(self.table[index]):
            if k == key:
                self.table[index][i] = (key, value)
                found = True
                break
        if not found:
            self.table[index].append((key, value))

    def get(self, key):
        index = self._hash(key)
        for k, v in self.table[index]:
            if k == key:
                return v
        return None

    def remove(self, key):
        index = self._hash(key)
        for i, (k, v) in enumerate(self.table[index]):
            if k == key:
                self.table[index].pop(i)
                return

hm = HashMap()

hm.put("apple", 1)
hm.put("banana", 2)
hm.put("cherry", 3)
hm.put("date", 4)
hm.put("berry", 5)
print(hm.get("apple"))
print(hm.get("banana"))
print(hm.get("grape"))
hm.put("orange", 10)
print(hm.get("apple"))
print(hm.get("orange"))
print(hm.table)
hm.remove("banana")
print(hm.get("banana"))
print(hm.table)