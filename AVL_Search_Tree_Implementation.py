"""
Aidan Butcher
CS 3450 - Algorithms & Data Structures
An AVL search tree implementation in Python.
"""


class Node:
    """Node class with a key, a height, a size, and pointers to its
    parent and children."""
    def __init__(self, key):
        self.key = key
        self.parent = None
        self.left = None
        self.right = None
        self.height = 0
        self.size = 1

    def __str__(self):
        """String representation for print."""
        return str(self.key)

    def is_leaf(self):
        """Checks if node is a leaf."""
        return self.height == 0

    def max_children_height(self):
        """Finds the height of the node's children."""
        if self.left and self.right:
            return max(self.left.height, self.right.height)
        elif self.left:
            return self.left.height
        elif self.right:
            return self.right.height
        else:
            return -1

    def balance(self):
        """Returns the balance of the node."""
        return (self.left.height if self.left else -1) -\
               (self.right.height if self.right else -1)


class AVLTree:
    """AVL Tree implementation that takes in a list of keys and turns it
    into a tree, self-balances according to AVL Tree properties."""
    def __init__(self, h=[]):
        self.root = None
        self.elements_count = 0
        self.rebalance_count = 0
        for el in h:
            self.insert(el)

    def height(self):
        """Returns the height of the tree."""
        if self.root:
            return self.root.height
        return -1

    def find_in_subtree(self, key, node):
        """Searches through a subtree, used in the find() method."""
        if node is None:
            return None
        if key < node.key:
            return self.find_in_subtree(key, node.left)
        elif key > node.key:
            return self.find_in_subtree(key, node.right)
        else:
            return node

    def find(self, key, node=None):
        """Searches from the specified node or root until it finds the given
        key or cannot find it."""
        if node is None:
            node = self.root
        return self.find_in_subtree(key, node)

    def recompute_heights(self, start_node):
        """Recomputes the height of the given node and its children."""
        changed = True
        node = start_node
        while node and changed:
            old_height = node.height
            node.height = (node.max_children_height() + 1
                           if (node.right or node.left) else 0)
            changed = node.height != old_height
            node = node.parent

    def find_biggest(self, start_node):
        """Finds the largest node in the tree."""
        node = start_node
        while node.right:
            node = node.right
        return node

    def find_smallest(self, start_node):
        """Finds the smallest node in the tree."""
        node = start_node
        while node.left:
            node = node.left
        return node

    def as_list(self, type=1):
        """Returns the keys of the tree in a specified order."""
        if not self.root:
            return []
        assert type in [0, 1, 2], 'wrong type value'

        if type == 0:
            return self.preorder(self.root)
        elif type == 1:
            return self.inorder(self.root)
        elif type == 2:
            return self.postorder(self.root)

    def preorder(self, node, retlst=None):
        """Returns the keys in a preorder form."""
        if retlst is None:
            retlst = []
        retlst += [node.key]
        if node.left:
            retlst = self.preorder(node.left, retlst)
        if node.right:
            retlst = self.preorder(node.right, retlst)
        return retlst

    def inorder(self, node, retlst=None):
        """Returns the keys in an inorder form."""
        if retlst is None:
            retlst = []
        if node.left:
            retlst = self.inorder(node.left, retlst)
        retlst += [node.key]
        if node.right:
            retlst = self.inorder(node.right, retlst)
        return retlst

    def postorder(self, node, retlst=None):
        """Returns the keys in the a postorder form."""
        if retlst is None:
            retlst = []
        if node.left:
            retlst = self.postorder(node.left, retlst)
        if node.right:
            retlst = self.postorder(node.right, retlst)
        retlst += [node.key]
        return retlst

    def add_as_child(self, parent_node, child_node):
        """Makes a node a child of another node and rebalances.
        Mainly used in the insert() method."""
        node_to_rebalance = None
        parent_node.size += 1
        if child_node.key < parent_node.key:
            if not parent_node.left:
                parent_node.left = child_node
                child_node.parent = parent_node
                if parent_node.height == 0:
                    node = parent_node
                    while node:
                        node.height = node.max_children_height() + 1
                        if not node.balance() in [-1, 0, 1]:
                            node_to_rebalance = node
                            break
                        node = node.parent
            else:
                self.add_as_child(parent_node.left, child_node)
        else:
            if not parent_node.right:
                parent_node.right = child_node
                child_node.parent = parent_node
                if parent_node.height == 0:
                    node = parent_node
                    while node:
                        node.height = node.max_children_height() + 1
                        if not node.balance() in [-1, 0, 1]:
                            node_to_rebalance = node
                            break
                        node = node.parent
            else:
                self.add_as_child(parent_node.right, child_node)

        if node_to_rebalance:
            self.rebalance(node_to_rebalance)

    def insert(self, key):
        """Inserts a new node and performs rebalancing as needed."""
        new_node = Node(key)
        if not self.root:
            self.root = new_node
            assert self.elements_count==0, 'Wrong elements_count'
            self.elements_count += 1
        else:
            if not self.find(key):
                self.elements_count += 1
                self.add_as_child(self.root, new_node)
        return self

    def remove_branch(self, node):
        """Removes an entire branch of the tree, used in the remove() method."""
        parent = node.parent
        if parent:
            if parent.left == node:
                parent.left = node.right or node.left
            else:
                parent.right = node.right or node.left
            if node.left:
                node.left.parent = parent
            else:
                node.right.parent = parent
            self.recompute_heights(parent)
        del node

        # rebalance
        node = parent
        while node:
            self.resize(node)
            if not node.balance() in [-1, 0, 1]:
                self.rebalance(node)

            node = node.parent

    def remove_leaf(self, node):
        """Used to remove a leaf node, used in the remove() method."""
        parent = node.parent
        if parent:
            if parent.left == node:
                parent.left = None
            else:
                parent.right = None
            self.recompute_heights(parent)
        else:
            self.root = None
        del node

        # rebalance
        node = parent
        while node:
            self.resize(node)
            if not node.balance() in [-1, 0, 1]:
                self.rebalance(node)
            node = node.parent

    def remove(self, key):
        """Using the remove_leaf() and remove_branch() to remove nodes.
        Uses the swap_with_successor_and_remove() method to help rebalance."""
        node = self.find(key)
        if not node is None:
            self.elements_count -= 1
            if node.is_leaf():
                self.remove_leaf(node)
            elif (bool(node.left) ^ bool(node.right)):
                self.remove_branch(node)
            else:
                self.swap_with_successor_and_remove(node)

    def swap_with_successor_and_remove(self, node):
        """Swaps the node with a successor node that is the smallest child of the node.
        Then removes the node after it has been replaced."""
        successor = self.find_smallest(node.right)
        self.swap_nodes(node, successor)
        if node.height == 0:
            self.remove_leaf(node)
        else:
            self.remove_branch(node)

    def swap_nodes(self, node1, node2):
        """Swaps two nodes while maintaining the AVL Tree structure."""
        parent1 = node1.parent
        left1 = node1.left
        right1 = node1.right
        parent2 = node2.parent
        left2 = node2.left
        right2 = node2.right

        tmp = node1.height
        node1.height = node2.height
        node2.height = tmp

        tmp = node1.size
        node1.size = node2.size
        node2.size = tmp

        if parent1:
            if parent1.left == node1:
                parent1.left = node2
            else:
                parent1.right = node2
            node2.parent = parent1
        else:
            self.root = node2
            node2.parent = None

        node2.left = left1
        left1.parent = node2

        node1.left = left2
        node1.right = right2
        if right2:
            right2.parent = node1

        if not (parent2 == node1):
            node2.right = right1
            right1.parent = node2

            parent2.left = node1
            node1.parent = parent2
        else:
            node2.right = node1
            node1.parent = node2

    def resize(self, node):
        """Fixes the size of a node, used in other methods."""
        node.size = 1
        if node.right:
            node.size += node.right.size
        if node.left:
            node.size += node.left.size

    def rebalance(self, node_to_rebalance):
        """Rebalances the tree, used in insertion, deletion, and swaps."""
        self.rebalance_count += 1
        A = node_to_rebalance
        F = A.parent
        if node_to_rebalance.balance() == -2:
            if node_to_rebalance.right.balance() <= 0:
                """Rebalance, case RRC"""
                B = A.right
                C = B.right
                A.right = B.left
                if A.right:
                    A.right.parent = A
                B.left = A
                A.parent = B
                if F is None:
                    self.root = B
                    self.root.parent = None
                else:
                    if F.right == A:
                        F.right = B
                    else:
                        F.left = B
                    B.parent = F
                self.recompute_heights(A)
                self.resize(A)
                self.resize(B)
                self.resize(C)
            else:
                """Rebalance, case RLC"""
                B = A.right
                C = B.left
                B.left = C.right
                if B.left:
                    B.left.parent = B
                A.right = C.left
                if A.right:
                    A.right.parent = A
                C.right = B
                B.parent = C
                C.left = A
                A.parent = C
                if F is None:
                    self.root = C
                    self.root.parent = None
                else:
                    if F.right == A:
                        F.right = C
                    else:
                        F.left = C
                    C.parent = F
                self.recompute_heights(A)
                self.recompute_heights(B)
                self.resize(A)
                self.resize(B)
                self.resize(C)
        else:
            if node_to_rebalance.left.balance() >= 0:
                B = A.left
                C = B.left
                """Rebalance, case LLC"""
                A.left = B.right
                if (A.left):
                    A.left.parent = A
                B.right = A
                A.parent = B
                if F is None:
                    self.root = B
                    self.root.parent = None
                else:
                    if F.right == A:
                        F.right = B
                    else:
                        F.left = B
                    B.parent = F
                self.recompute_heights(A)
                self.resize(A)
                self.resize(B)
                self.resize(C)
            else:
                B = A.left
                C = B.right
                """Rebalance, case LRC"""
                A.left = C.right
                if A.left:
                    A.left.parent = A
                B.right = C.left
                if B.right:
                    B.right.parent = B
                C.left = B
                B.parent = C
                C.right = A
                A.parent = C
                if F is None:
                    self.root = C
                    self.root.parent = None
                else:
                    if F.right == A:
                        F.right = C
                    else:
                        F.right = C
                    C.parent = F
                self.recompute_heights(A)
                self.recompute_heights(B)
                self.resize(A)
                self.resize(B)
                self.resize(C)

    def findkth(self, k, root=None):
        """Finds the kth element from a given node or the base root."""
        if root is None:
            root = self.root
        assert k <= root.size, 'Error, k more than the size of BST'
        leftsize = 0 if root.left is None else root.left.size
        if leftsize >= k:
            return self.findkth(k, root.left)
        elif leftsize == k-1:
            return root.key
        else:
            return self.findkth(k - leftsize - 1, root.right)

    def __str__(self, start_node=None):
        """Overloaded string operator for printing the tree in a fancy way."""
        if start_node is None:
            start_node = self.root
        space_symbol = r" "
        spaces_count = 4 * 2**(self.root.height)
        out_string = r""
        initial_spaces_string = space_symbol * spaces_count + "\n"
        if not start_node:
            return "Tree is empty"
        height = 2**(self.root.height)
        level = [start_node]

        while ((len([i for i in level if (not i is None)])) > 0):
            level_string = initial_spaces_string
            for i in range(len(level)):
                j = int((2 * i + 1) * spaces_count / (2 * len(level)))
                level_string = level_string[:j] + \
                (str(level[i]) if level[i] else space_symbol) + level_string[j + 1:]
            out_string += level_string

            # create next level
            level_next = []
            for i in level:
                level_next += ([i.left, i.right] if i else [None, None])

            # add connection to the next nodes
            for w in range(height-1):
                level_string = initial_spaces_string
                for i in range(len(level)):
                    if not level[i] is None:
                        shift = spaces_count//(2*len(level))
                        j = (2 * i + 1) * shift
                        level_string = level_string[:j - w - 1] + \
                            ('/' if level[i].left else space_symbol) + \
                            level_string[j - w:]
                        level_string = level_string[:j + w + 1] + \
                            ('\\' if level[i].right else space_symbol) + \
                            level_string[j + w:]
                out_string += level_string
            height = height // 2
            level = level_next
        return out_string


if __name__ == '__main__':
    lst = [3, 5, 9, 10, 23, 50, 11, 2]
    tree = AVLTree(lst)
    print(tree)
    tree.insert(16)
    print(tree)
    tree.remove(10)
    print(tree)
    print(tree.as_list())
