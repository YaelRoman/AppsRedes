class Queue:
    def __init__(self):
        self.queue =[]
    
    def enqueue(self, element):
        self.queue.append(element)
    
    def isEmpty(self):
        return len(self.queue) == 0
    
    def dequeue(self):
        if self.isEmpty(): return 'Queue vacia'
        return self.queue.pop(0)
    
    def peek(self):
        if self.isEmpty(): return 'Queue vacia'
        return self.queue[0]
    
    def size(self):
        return len(self.queue)

class Auto:
    def __init__(self, modelo):
        self.modelo = modelo
        self.km = 0

autos = [Auto("Ferrari"),
         Auto("Vocho"),
         Auto("Tsuru"),
         Auto("Sentra"),
         Auto("Camaro")]
        
misAutos = Queue()
print('Autos:', misAutos.queue)
print('Hay', misAutos.size(), 'autos')
print(misAutos.dequeue())

for auto in autos: 
    print('\tEntra', auto.modelo)
    misAutos.enqueue(auto)

print('Autos:\n')
for auto in misAutos.queue: print('\t', auto.modelo)
print('\nHay', misAutos.size(), 'autos')
print('Sale', misAutos.dequeue().modelo)
print('Autos:\n')
for auto in misAutos.queue: print('\t',auto.modelo)
print('\nHay', misAutos.size(), 'autos')

for _ in range(misAutos.size()): 
    print('\tSale', misAutos.dequeue().modelo)
print('Autos:', misAutos.queue)
print('Hay', misAutos.size(), 'autos')




    