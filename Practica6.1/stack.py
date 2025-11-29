class Stack:
    def __init__(self):
        self.stack = []

    def isEmpty(self):
        return len(self.stack) == 0
    
    def push(self, item):
        self.stack.append(item)

    def pop(self):
        if self.isEmpty(): return "Stack vacio"
        return self.stack.pop()

    def peek(self):
        if self.isEmpty(): return "Stack vacio"
        return self.stack[-1]
    
    def size(self):
        return len(self.stack)

# Inicializar e intentar retirar elemento    
miStack = Stack()
print(miStack.pop())

# Insertar 10 números
for i in range(10): miStack.push(i)
print(miStack.stack)
print('Hay', miStack.size(), 'numeros')
print('Top: ', miStack.peek())

# Remover un elemento
print('Removido: ', miStack.pop())
print('Hay', miStack.size(), 'numeros')
print(miStack.stack)
# Remover todos los elementos
for _ in range(miStack.size()): print('Removido', miStack.pop())
print('Hay', miStack.size(), 'numeros')
print(miStack.pop())
