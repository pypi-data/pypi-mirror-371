from .node import TreeNode
from .binary_search_tree import BinarySearchTree
from enum import Enum

"""
1. The color of a node is either red or black.
2. The color of the root node is always black.
3. All leaf nodes are black.
4. Every red node has both the children colored in black.
5. Every simple path from a given node to any of its leaf nodes has an equal number of black nodes.
"""

class Color(Enum):
    RED     = "red"
    BLACK   = "black"


class RBTreeNode(TreeNode):

    def __init__(self, value, left_child=None, right_child=None, color=Color.RED, parent=None, nil_node=None):
        super().__init__(value, left_child, right_child, parent)
        self._color = color
        self.NIL = nil_node
        
    @property
    def color(self):
        return self._color
    
    @color.setter
    def color(self, color):
        if not isinstance(color, Color):
            raise Exception("Wrong type of color. Set either Color.RED or Color.BLACK")
        self._color = color
    
    @property
    def is_red(self):
        return self._color == Color.RED

    @property
    def is_black(self):
        return self._color == Color.BLACK
    
    @property
    def grandparent(self):
        if self.parent is self.NIL or self.parent.parent is self.NIL:
            return self.NIL
        return self.parent.parent
    
    @property
    def uncle(self):
        grand_parent = self.grandparent
        if grand_parent is self.NIL:
            return self.NIL
        elif grand_parent.left_child == self.parent:
            return grand_parent.right_child
        else:
            return grand_parent.left_child
    
    def is_left_child(self):
        return self.parent != self.NIL and self.parent.left_child == self
    
    def is_right_child(self):
        return self.parent != self.NIL and self.parent.right_child == self

class RedBlackTree(BinarySearchTree):
    def __init__(self, value=None, node=RBTreeNode):
        super().__init__(value, node)
        self._Node = node
        self.NIL = self._Node(None, color=Color.BLACK)
        self.NIL._left_child = self.NIL
        self.NIL._right_child = self.NIL
        self.NIL.parent = self.NIL
        
        if value is None:
            self._root = self.NIL
            self._size = 0
        else:
            self._root = self._Node(value, color=Color.BLACK, parent=self.NIL,
                                    left_child=self.NIL, right_child=self.NIL)
            self._size = 1
    
    def __iter__(self):
        for node in self._inorder(self.root):
            yield node
    
    def _inorder(self, node):
        if node is self.NIL:
            return
        yield from self._inorder(node.left_child)
        yield node
        yield from self._inorder(node.right_child)
    
    def _preorder(self, node):
        if node is self.NIL:
            return
        yield node
        yield from self._preorder(node.left_child)
        yield from self._preorder(node.right_child)
        
    def _postorder(self, node):
        if node is self.NIL:
            return
        yield from self._postorder(node.left_child)
        yield from self._postorder(node.right_child)
        yield node
    
    def insert(self, data):
        node = self._insert_iterative(data)
        if self.root is node:
            node.color = Color.BLACK
        self._fix_insertion(node)
    
    def _insert_iterative(self, data):
        if not isinstance(data, self._Node):
            new_node = self._Node(data, left_child=self.NIL, right_child=self.NIL, parent=self.NIL, nil_node=self.NIL)
        else:
            new_node = data
        
        if self.root is self.NIL:
            self.root = new_node
            self._size += 1
            return new_node
        else:
            current_node = self.root
        while True:
            if new_node.value >= current_node.value:
                if current_node.right_child is self.NIL:
                    current_node.right_child = new_node
                    new_node.parent = current_node
                    self._size += 1
                    return new_node
                current_node = current_node.right_child
            elif new_node.value < current_node.value:
                if current_node.left_child is self.NIL:
                    current_node.left_child = new_node
                    new_node.parent = current_node
                    self._size += 1
                    return new_node
                current_node = current_node.left_child

    def _fix_insertion(self, node):
        while node.parent.is_red:
            if node.parent.is_left_child():
                if node.uncle.color == Color.RED:
                    node.parent.color = Color.BLACK
                    node.uncle.color = Color.BLACK
                    node.grandparent.color = Color.RED
                    node = node.grandparent
                else: # if node.uncle.color == Color.BLACK or node.uncle is None
                    if node.is_right_child():
                        node = node.parent
                        self._rotate_left(node)
                    node.parent.color = Color.BLACK
                    node.grandparent.color = Color.RED
                    self._rotate_right(node.grandparent)
            else: # node.parent.is_right_child()
                if node.uncle.color == Color.RED:
                    node.parent.color = Color.BLACK
                    node.uncle.color = Color.BLACK
                    node.grandparent.color = Color.RED
                    node = node.grandparent
                else: # if node.uncle.color == Color.BLACK or node.uncle is None
                    if node.is_left_child():
                        node = node.parent
                        self._rotate_right(node)
                    node.parent.color = Color.BLACK
                    node.grandparent.color = Color.RED
                    self._rotate_left(node.grandparent)
        
        self.root.color = Color.BLACK
                
    def _rotate_right(self, node):
        target_node = node.left_child
        if node.parent is not self.NIL:
            if node.parent.left_child == node:
                node.parent.left_child = target_node
            elif node.parent.right_child == node:
                node.parent.right_child = target_node
        else:
            self.root = target_node
            self.root.parent = self.NIL
        
        node.left_child = target_node.right_child
        if target_node.right_child is not self.NIL:
            target_node.right_child.parent = node
        
        target_node.right_child = node
        temp = node.parent
        target_node.parent = temp
        node.parent = target_node
    
    def _rotate_left(self, node):
        target_node = node.right_child
        if node.parent is not self.NIL:
            if node.parent.left_child == node:
                node.parent.left_child = target_node
            elif node.parent.right_child == node:
                node.parent.right_child = target_node
        else:
            self.root = target_node
            self.root.parent = self.NIL
        
        node.right_child = target_node.left_child
        if target_node.left_child is not self.NIL:
            target_node.left_child.parent = node
            
        target_node.left_child = node
        temp = node.parent
        target_node.parent = temp
        node.parent = target_node
    
    def delete(self, node):
        deleted_node = self.search_iterative(node, self.NIL)
        node_color = deleted_node.color
        if deleted_node.left_child is self.NIL:
            node = deleted_node.right_child
            self._transplant(deleted_node, deleted_node.right_child)
        elif deleted_node.right_child is self.NIL:
            node = deleted_node.left_child
            self._transplant(deleted_node, deleted_node.left_child)
        else: # node has both children
            successor = self.find_min(deleted_node.right_child, none_value=self.NIL)
            node_color = successor.color
            node = successor.right_child
            
            if successor.parent != deleted_node:
                self._transplant(successor, successor.right_child)
                successor.right_child = deleted_node.right_child
                successor.right_child.parent = successor

            self._transplant(deleted_node, successor)
            successor.left_child = deleted_node.left_child
            successor.left_child.parent = successor
            successor.color = deleted_node.color

        if node_color == Color.BLACK:
            self._fix_deletion(node)
            
            
    def _transplant(self, u, v):
        """Replaces subtree rooted at u with subtree rooted at v."""
        if u.parent == self.NIL:
            self.root = v
        elif u == u.parent.left_child:
            u.parent.left_child = v
        else:
            u.parent.right_child = v
        v.parent = u.parent

    def _fix_deletion(self, node):
        while node != self.root and node.color == Color.BLACK:
            if node.is_left_child():
                sibling_node = node.parent.right_child
                if sibling_node.color == Color.RED:
                    sibling_node.color = Color.BLACK
                    sibling_node.parent.color = Color.RED
                    self._rotate_left(sibling_node.parent)
                    sibling_node = node.parent.right_child
                elif sibling_node.is_black and sibling_node.left_child.is_black and sibling_node.right_child.is_black:
                    sibling_node.color = Color.RED
                    node = node.parent
                elif sibling_node.is_black and sibling_node.left_child.is_red and sibling_node.right_child.is_black:
                    sibling_node.left_child.color = Color.BLACK
                    sibling_node.color = Color.RED
                    self._rotate_right(sibling_node)
                    sibling_node = node.parent.right_child
                else: # sibling_node.is_black and sibling_node.right_child.is_red
                    sibling_node.color = sibling_node.parent.color
                    sibling_node.parent.color = Color.BLACK
                    sibling_node.right_child.color = Color.BLACK
                    self._rotate_left(sibling_node.parent)
                    node = self.root
            else:
                sibling_node = node.parent.left_child
                if sibling_node.is_red:
                    sibling_node.color = Color.BLACK
                    sibling_node.parent.color = Color.RED
                    self._rotate_right(sibling_node.parent)
                    sibling_node = node.parent.left_child
                elif sibling_node.is_black and sibling_node.left_child.is_black and sibling_node.right_child.is_black:
                    sibling_node.color = Color.RED
                    node = node.parent
                elif sibling_node.is_black and sibling_node.right_child.is_red and sibling_node.left_child.is_black:
                    sibling_node.right_child.color = Color.BLACK
                    sibling_node.color = Color.RED
                    self._rotate_left(sibling_node)
                    sibling_node = node.parent.left_child
                else: # sibling_node.is_black and sibling_node.left_child.is_red
                    sibling_node.color = sibling_node.parent.color
                    sibling_node.parent.color = Color.BLACK
                    sibling_node.left_child.color = Color.BLACK
                    self._rotate_right(sibling_node.parent)
                    node = self.root
        
        if node:
            node.color = Color.BLACK
        self.root.color = Color.BLACK
