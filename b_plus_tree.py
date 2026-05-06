import b_tree

class Bplustree(b_tree.Btree):
    def __init__(self, d=4):
        super().__init__(d)
        self.split_count = 0
        
    def search(self, key, start=None):
        if self.root == None:
            return None
        if start is None:
            searching_node = self.root
        else:
            searching_node = start
        while searching_node.pointers:
            temp_count = searching_node.key_count()
            for i in range(temp_count):
                if key < searching_node.keys[i][0]:
                    searching_node = searching_node.pointers[i]
                    break
                if i == temp_count - 1:
                    searching_node = searching_node.pointers[i+1]
        return searching_node


    def insert(self, key, rid):
        if self.root == None:
            self.root = b_tree.Node()
            self.add_key(self.root, key, rid)
            return
        
        searched_leaf = self.search(key)
        self.add_key(searched_leaf, key, rid)


    def remove(self, key):
        searched_leaf = self.search(key)
        if searched_leaf is None: 
            return
        self.remove_key(searched_leaf, key)


    def merge(self, current_Node: b_tree.Node):
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

        is_leaf = not bool(current_Node.pointers)

        # redistribution
        if left_sibling is not None and left_sibling.key_count() > -(-self.d//2) - 1:
            if is_leaf:
                borrowing_key = left_sibling.keys.pop()
                current_Node.keys.insert(0, borrowing_key)
                parent.keys[index-1] = (current_Node.keys[0][0], None) 
            else:
                borrowing_key = left_sibling.keys.pop()
                parent_key = parent.keys.pop(index-1)
                parent.keys.insert(index-1, (borrowing_key[0], None))
                current_Node.keys.insert(0, parent_key)
                if left_sibling.pointers:
                    left_sibling_child = left_sibling.pointers.pop()
                    current_Node.add_child(left_sibling_child)
            return
                
        elif right_sibling is not None and right_sibling.key_count() > -(-self.d//2) - 1:
            if is_leaf:
                borrowing_key = right_sibling.keys.pop(0)
                current_Node.keys.append(borrowing_key)
                parent.keys[index] = (right_sibling.keys[0][0], None)
            else:
                borrowing_key = right_sibling.keys.pop(0)
                parent_key = parent.keys.pop(index)
                parent.keys.insert(index, (borrowing_key[0], None)) 
                current_Node.keys.append(parent_key)
                if right_sibling.pointers:
                    right_sibling_child = right_sibling.pointers.pop(0)
                    current_Node.add_child(right_sibling_child)
            return

        # merge
        if left_sibling is not None:
            if is_leaf:
                for key in current_Node.keys:
                    left_sibling.keys.append(key)
                left_sibling.next = getattr(current_Node, 'next', None)
                parent.keys.pop(index-1)
                parent.pointers.remove(current_Node)
            else:
                parent_key = parent.keys.pop(index-1)
                left_sibling.keys.append(parent_key)
                for key in current_Node.keys:
                    left_sibling.keys.append(key)
                for child in current_Node.pointers:
                    left_sibling.add_child(child)
                parent.pointers.remove(current_Node)

        elif right_sibling is not None:
            if is_leaf:
                for key in right_sibling.keys:
                    current_Node.keys.append(key)
                current_Node.next = getattr(right_sibling, 'next', None)
                parent.keys.pop(index)
                parent.pointers.remove(right_sibling)
            else:
                parent_key = parent.keys.pop(index)
                current_Node.keys.append(parent_key)
                for key in right_sibling.keys:
                    current_Node.keys.append(key)
                for child in right_sibling.pointers:
                    current_Node.add_child(child)
                parent.pointers.remove(right_sibling)
        
        if parent.key_count() == 0 and parent.parent is None:
            if left_sibling is not None:
                self.root = left_sibling
                left_sibling.parent = None
            elif right_sibling is not None:
                self.root = current_Node
                current_Node.parent = None
        
        if parent.parent is not None or parent.key_count() < -(-self.d//2) - 1:
            self.merge(parent)


    def split(self, current_Node: b_tree.Node):
        parent = current_Node.parent
        pivot = -(-current_Node.key_count() // 2) - 1

        is_leaf = not bool(current_Node.pointers)
        if is_leaf:
            self.split_count += 1
            right_Node = b_tree.Node()
            all_keys = current_Node.keys
            current_Node.set_keys(all_keys[:pivot])
            right_Node.set_keys(all_keys[pivot:])
            right_Node.next = getattr(current_Node, 'next', None)
            current_Node.next = right_Node
            sending_middle = (right_Node.keys[0][0], None)
            
            if parent is None:
                parent = b_tree.Node()
                self.root = parent
                parent.add_child(current_Node)
                parent.add_child(right_Node)
                parent.keys.append(sending_middle)
            else:
                parent.add_child(right_Node)
                parent.keys.append(sending_middle)
                parent.keys.sort(key=lambda x: x[0])
                if parent.key_count() >= self.d:
                    self.split(parent)
        else:
            super().split(current_Node)

    def range_query(self, start_key, end_key):
        result = []
        if self.root is None:
            return result
        
        current_node = self.search(start_key)
        while current_node is not None:
            for key, rid in current_node.keys:
                if start_key <= key <= end_key:
                    result.append((key, rid))
                elif key > end_key:
                    return result
            current_node = getattr(current_node, 'next', None)
        return result