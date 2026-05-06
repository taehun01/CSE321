class Node:
    def __init__(self):
        self.parent :Node = None
        self.keys :list[tuple] = [] #d-1
        self.pointers :list[Node] = [] #d
    
    def key_count(self):
        return len(self.keys)

    def set_keys(self, keys :list):
        self.keys = keys
    
    def set_parent(self, parent):
        self.parent = parent

    def set_pointers(self, pointers :list):
        self.pointers = pointers

    def add_child(self, child):
        self.pointers.append(child)
        self.pointers.sort(key=lambda x: x.keys[0][0])
        child.set_parent(self)
    

class Btree:
    def __init__(self, d=4):
        self.root = None
        self.d = d # Order of b-tree. d > 1
        self.split_count = 0

    
    def search(self, key, start=None, search_only_leaf=False) -> Node:
        if self.root == None:
            return None
        if start is None:
            searching_node = self.root
        else:
            searching_node = start
        while searching_node.pointers:
            temp_count = searching_node.key_count()
            for i in range(temp_count):
                if key == searching_node.keys[i][0] and search_only_leaf == False:
                    return searching_node
                elif key < searching_node.keys[i][0]:
                    searching_node = searching_node.pointers[i]
                    break
                if i == temp_count-1:
                    searching_node = searching_node.pointers[i+1]
        return searching_node


    def insert(self, key, rid):
        if self.root == None:
            self.root = Node()
            self.add_key(self.root, key, rid)
            return
        
        searched_leaf = self.search(key, search_only_leaf=True)
        self.add_key(searched_leaf, key, rid)

    
    def remove(self, key):
        searched_Node = self.search(key)
        if not searched_Node.pointers: #leaf
            self.remove_key(searched_Node, key)
        else: #internal
            index = -1
            for i, key_ in enumerate(searched_Node.keys):
                if key_[0] == key:
                    index = i
                    break
            if index == -1: return
            searched_leaf_Node = self.search(key, start=searched_Node.pointers[index+1] ,search_only_leaf=True)
            switching_key = searched_leaf_Node.keys[0]
            target_tuple = searched_Node.keys[index] 
            searched_Node.keys[index] = switching_key
            searched_leaf_Node.keys[0] = target_tuple
            self.remove_key(searched_leaf_Node, key)
            

    def add_key(self, current_Node :Node, key, rid):
        current_Node.keys.append((key, rid))
        current_Node.keys.sort(key=lambda x: x[0])
        if current_Node.key_count() >= self.d:
            self.split(current_Node)

    
    def remove_key(self, current_Node :Node, key):
        removed = False
        for key_ in current_Node.keys:
            if key_[0] == key:
                current_Node.keys.remove(key_)
                removed = True
                break
        if removed == False: # 값이 없을때 
            return
        if current_Node.key_count() < -(-self.d//2) - 1:
            self.merge(current_Node)


    def merge(self, current_Node :Node):
        if current_Node.key_count() >= -(-self.d//2) - 1 or current_Node is self.root:
            return
        
        parent = current_Node.parent
        index = -1
        left_sibling = None
        right_sibling = None

        if current_Node in parent.pointers:
            index = parent.pointers.index(current_Node)
        if index-1 >= 0 and index != -1:
            left_sibling = parent.pointers[index-1]
        if parent.key_count() > index and index != -1:
            right_sibling = parent.pointers[index+1]

        if left_sibling is not None and left_sibling.key_count() > -(-self.d//2) - 1:
            borrowing_key = left_sibling.keys.pop()
            parent_key = parent.keys.pop(index-1)
            parent.keys.insert(index-1, borrowing_key)
            current_Node.keys.insert(0, parent_key)
            if left_sibling.pointers:
                left_sibling_child = left_sibling.pointers.pop()
                current_Node.add_child(left_sibling_child)
            return
                
        elif right_sibling is not None and right_sibling.key_count() > -(-self.d//2) - 1:
            borrowing_key = right_sibling.keys.pop(0)
            parent_key = parent.keys.pop(index)
            parent.keys.insert(index, borrowing_key) 
            current_Node.keys.append(parent_key)
            if right_sibling.pointers:
                right_sibling_child = right_sibling.pointers.pop(0)
                current_Node.add_child(right_sibling_child)
            return

        #merge
        if left_sibling is not None:
            for key in left_sibling.keys:
                current_Node.keys.append(key)
            parent_key = parent.keys.pop(index-1)
            current_Node.keys.append(parent_key)
            current_Node.keys.sort(key=lambda x: x[0])
            parent.pointers.remove(left_sibling)
            for child in left_sibling.pointers:
                current_Node.add_child(child)

        elif right_sibling is not None:
            for key in right_sibling.keys:
                current_Node.keys.append(key)
            parent_key = parent.keys.pop(index)
            current_Node.keys.append(parent_key)
            current_Node.keys.sort(key=lambda x: x[0])
            parent.pointers.remove(right_sibling)
            for child in right_sibling.pointers:
                current_Node.add_child(child)
        
        if parent.key_count() == 0 and parent.parent is None:
            self.root = current_Node
            current_Node.parent = None
        
        self.merge(parent)


    def split(self, current_Node :Node):
        self.split_count += 1
        parent = current_Node.parent
        pivot = -(-current_Node.key_count()//2) - 1 #1
        middle = current_Node.keys[pivot]
        # 0 1 2 3   key
        #0 1 2 3 4  pointer
        left_Node = Node() 
        left_Node.set_keys(current_Node.keys[:pivot])
        left_Node.set_pointers(current_Node.pointers[:pivot+1])
        for child in current_Node.pointers[:pivot+1]:
            child.set_parent(left_Node)

        right_Node = Node()
        right_Node.set_keys(current_Node.keys[pivot+1:])
        right_Node.set_pointers(current_Node.pointers[pivot+1:])
        for child in current_Node.pointers[pivot+1:]:
            child.set_parent(right_Node)
        
        if parent is None:
            parent = Node()
            self.root = parent
            parent.keys.append(middle)
            parent.add_child(left_Node)
            parent.add_child(right_Node)
        else:
            parent.pointers.remove(current_Node)
            parent.add_child(left_Node)
            parent.add_child(right_Node)
            key_, rid_ = middle
            self.add_key(parent, key_, rid_)
    

    def print_tree(self, current_Node: Node, level=0, prefix="Root: "):
        if current_Node is not None:
            indent = "    " * level
            print(f"{indent}{prefix}{current_Node.keys}")
            
            if current_Node.pointers:
                for i, child in enumerate(current_Node.pointers):
                    new_prefix = f"Child[{i}]: "
                    self.print_tree(child, level + 1, new_prefix)