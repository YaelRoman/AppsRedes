### Search Binary Tree
class Tree:
    def __init__(self, item):
        self.item = item
        self.left = None
        self.right = None

    def addChild(self, item):
        if item < self.item:
            if self.left == None:
                self.left = Tree(item)
            else:
                self.left.addChild(item)
        else:
            if self.right == None:
                self.right = Tree(item)
            else:
                self.right.addChild(item)
        
    def preOrder(self):
        print(self.item)
        if self.left:
            self.left.preOrder()
        if self.right:
            self.right.preOrder()

    def inOrder(self):
        if self.left:
            self.left.inOrder()
        print(self.item)
        if self.right:
            self.right.inOrder()

    def postOrder(self):
        if self.left:
            self.left.postOrder()
        if self.right:
            self.right.postOrder()
        print(self.item)

### Preorder: 6,4,2,1,3,5,7,9,8
### Inorder : 1,2,3,4,5,6,7,8,9
### Postorder: 1,3,2,5,4,8,9,7,6

abecedario = Tree(6)
abecedario.addChild(4)
abecedario.addChild(2)
abecedario.addChild(1)
abecedario.addChild(3)
abecedario.addChild(5)
abecedario.addChild(7)
abecedario.addChild(9)
abecedario.addChild(8)

print('Preorder')
abecedario.preOrder()
print('Inorder')
abecedario.inOrder()
print('Postorder')
abecedario.postOrder()
