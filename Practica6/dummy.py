### Queue
class Queue:
    def __init__(self):
        self.items = []
        self.n = 0
    
    def is_empty(self):
        if self.n == 0:
            return True
        return False
    
    def count(self):
        return self.n
    
    def enqueue(self, item):
        self.items.append(item)
        self.n += 1
        return item

    def dequeue(self):
        if self.is_empty():
            print("Cola vacía")
            return None
        item = self.items.pop(0)
        self.n -= 1
        return item
    
### Stack    
class Stack:
    def __init__(self):
        self.items = []
        self.n = 0

    def is_empty(self):
        if self.n == 0:
            return True
        return False

    def count(self):
        return self.n

    def push(self, item):
        self.items.append(item)
        self.n += 1
        return item

    def pop(self):
        if self.is_empty():
            print("Pila vacía")
            return None
        item = self.items.pop()
        self.n -= 1
        return item
    
frutas = Stack()

print('Hay ', frutas.count(), 'frutas')  
print('Hay frutas?', 'Si' if not frutas.is_empty() else 'No')

frutas.push('Manzana')
frutas.push('Banana')
frutas.push('Cereza')

print('Hay ', frutas.count(), 'frutas')
print('Hay frutas?', 'Si' if not frutas.is_empty() else 'No')

print('Sacando frutas...')
print(frutas.pop())
print(frutas.pop())
print(frutas.pop())

print('Hay frutas?', 'Si' if not frutas.is_empty() else 'No')

verduras = Queue()
print('Hay ', verduras.count(), 'verduras')
print('Hay verduras?', 'Sí' if not verduras.is_empty() else 'No')

print('Metiendo verduras...')
print(verduras.enqueue('Zanahoria'))
print(verduras.enqueue('Lechuga'))
print(verduras.enqueue('Pepino'))

print('Hay ', verduras.count(), 'verduras')
print('Hay verduras?', 'Sí' if not verduras.is_empty() else 'No')
print('Lista de verduras:', verduras.items)
print('Sacando verduras...')
while not verduras.is_empty():
    verdura = verduras.items[0]
    verduras.dequeue()
    print('Adios',verdura)
    
print('Hay ', verduras.count(), 'verduras')
print('Hay verduras?', 'Sí' if not verduras.is_empty() else 'No')