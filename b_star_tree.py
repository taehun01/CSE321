import b_tree

class Bstartree(b_tree.Btree):
    def __init__(self, d=4):
        super().__init__(d)

    def split(self, current_Node :b_tree.Node):
        if current_Node.key_count() < self.d:
            return
        if current_Node is self.root and current_Node.parent is None:
            super().split(current_Node)
            return

        parent = current_Node.parent
        index = -1
        left_sibling = None
        right_sibling = None

        if current_Node in parent.pointers:
            index = parent.pointers.index(current_Node)
        else:
            return
        if index-1 >= 0 and index != -1:
            left_sibling = parent.pointers[index-1]
        if parent.key_count() > index and index != -1:
            right_sibling = parent.pointers[index+1]

        # redistribution
        if left_sibling is not None and left_sibling.key_count() < self.d - 1:
            sending_key = current_Node.keys.pop(0)
            parent_key = parent.keys.pop(index-1)
            parent.keys.insert(index-1, sending_key)
            left_sibling.keys.append(parent_key)
            if current_Node.pointers:
                current_Node_child = current_Node.pointers.pop(0)
                left_sibling.add_child(current_Node_child)
            return
        elif right_sibling is not None and right_sibling.key_count() < self.d - 1:
            sending_key = current_Node.keys.pop()
            parent_key = parent.keys.pop(index)
            parent.keys.insert(index, sending_key) 
            right_sibling.keys.insert(0, parent_key)
            if current_Node.pointers:
                current_Node_child = current_Node.pointers.pop()
                right_sibling.add_child(current_Node_child)
            return
       
        # 0 1 2 3   key
        #0 1 2 3 4  pointer      
        #  
        #                                                1     0
        # 0 1     0 1+n        0 1 p 0 1 n -> 2*d      0   p 1   n
        #0 1 2   0 1 2        0 1 2 0 1 2             0 1 2 0 1 2

        self.split_count += 1
        #2-to-3
        if left_sibling is not None:
            parent_separator = parent.keys[index-1]
            parent.keys.pop(index-1)
            merging_keys = left_sibling.keys + [parent_separator] + current_Node.keys
            merging_pointers = left_sibling.pointers + current_Node.pointers

            separator_index_1 = len(merging_keys)//3
            separator_index_2 = len(merging_keys)*2//3
            
            separator_new_1 = merging_keys[separator_index_1]
            separator_new_2 = merging_keys[separator_index_2]
            parent.keys.append(separator_new_1)
            parent.keys.append(separator_new_2)
            parent.keys.sort(key=lambda x: x[0])
            
            Node_1 = b_tree.Node()
            Node_2 = b_tree.Node()
            Node_3 = b_tree.Node()

            node_1_keys = merging_keys[:separator_index_1]
            Node_1.set_keys(node_1_keys)
            node_2_keys = merging_keys[separator_index_1+1:separator_index_2]
            Node_2.set_keys(node_2_keys)
            node_3_keys = merging_keys[separator_index_2+1:]
            Node_3.set_keys(node_3_keys)

            node_1_pointers = merging_pointers[:separator_index_1+1]
            Node_1.set_pointers(node_1_pointers)
            for child in node_1_pointers:
                child.set_parent(Node_1)
            node_2_pointers = merging_pointers[separator_index_1+1:separator_index_2+1]
            Node_2.set_pointers(node_2_pointers)
            for child in node_2_pointers:
                child.set_parent(Node_2)
            node_3_pointers = merging_pointers[separator_index_2+1:]
            Node_3.set_pointers(node_3_pointers)
            for child in node_3_pointers:
                child.set_parent(Node_3)

            Node_1.set_parent(parent)
            Node_2.set_parent(parent)
            Node_3.set_parent(parent)

            parent.pointers.remove(current_Node)
            parent.pointers.remove(left_sibling)
            parent.add_child(Node_1)
            parent.add_child(Node_2)
            parent.add_child(Node_3)

            self.split(parent)

        elif right_sibling is not None:
            parent_separator = parent.keys[index]
            parent.keys.pop(index)
            merging_keys = current_Node.keys + [parent_separator] + right_sibling.keys
            merging_pointers = current_Node.pointers + right_sibling.pointers

            separator_index_1 = len(merging_keys)//3
            separator_index_2 = len(merging_keys)*2//3
            
            separator_new_1 = merging_keys[separator_index_1]
            separator_new_2 = merging_keys[separator_index_2]
            parent.keys.append(separator_new_1)
            parent.keys.append(separator_new_2)
            parent.keys.sort(key=lambda x: x[0])
            
            Node_1 = b_tree.Node()
            Node_2 = b_tree.Node()
            Node_3 = b_tree.Node()

            node_1_keys = merging_keys[:separator_index_1]
            Node_1.set_keys(node_1_keys)
            node_2_keys = merging_keys[separator_index_1+1:separator_index_2]
            Node_2.set_keys(node_2_keys)
            node_3_keys = merging_keys[separator_index_2+1:]
            Node_3.set_keys(node_3_keys)

            node_1_pointers = merging_pointers[:separator_index_1+1]
            Node_1.set_pointers(node_1_pointers)
            for child in node_1_pointers:
                child.set_parent(Node_1)
            node_2_pointers = merging_pointers[separator_index_1+1:separator_index_2+1]
            Node_2.set_pointers(node_2_pointers)
            for child in node_2_pointers:
                child.set_parent(Node_2)
            node_3_pointers = merging_pointers[separator_index_2+1:]
            Node_3.set_pointers(node_3_pointers)
            for child in node_3_pointers:
                child.set_parent(Node_3)

            Node_1.set_parent(parent)
            Node_2.set_parent(parent)
            Node_3.set_parent(parent)

            parent.pointers.remove(current_Node)
            parent.pointers.remove(right_sibling)
            parent.add_child(Node_1)
            parent.add_child(Node_2)
            parent.add_child(Node_3)

            self.split(parent)
        else:
            super().split(current_Node)
    
    def remove_key(self, current_Node :b_tree.Node, key):
        removed = False
        for key_ in current_Node.keys:
            if key_[0] == key:
                current_Node.keys.remove(key_)
                removed = True
                break
        if removed == False: # 값이 없을때 
            return
        if current_Node.key_count() < (self.d*2-1)//3:
            self.merge(current_Node)
    

    def merge(self, current_Node :b_tree.Node):
        if current_Node.key_count() >= (self.d*2-1)//3:
            return
        if current_Node is self.root:
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
        
        # redistribution
        if left_sibling is not None and left_sibling.key_count() > (self.d*2-1)//3:
            borrowing_key = left_sibling.keys.pop()
            parent_key = parent.keys.pop(index-1)
            parent.keys.insert(index-1, borrowing_key)
            current_Node.keys.insert(0, parent_key)
            if left_sibling.pointers:
                left_sibling_child = left_sibling.pointers.pop()
                current_Node.add_child(left_sibling_child)
            return
                
        elif right_sibling is not None and right_sibling.key_count() > (self.d*2-1)//3:
            borrowing_key = right_sibling.keys.pop(0)
            parent_key = parent.keys.pop(index)
            parent.keys.insert(index, borrowing_key) 
            current_Node.keys.append(parent_key)
            if right_sibling.pointers:
                right_sibling_child = right_sibling.pointers.pop(0)
                current_Node.add_child(right_sibling_child)
            return
        
        # 3->2 merge 
        if left_sibling is not None and left_sibling.key_count() == (self.d*2-1)//3 and right_sibling is not None and right_sibling.key_count() == (self.d*2-1)//3:
            left_separator = parent.keys[index-1]
            right_separator = parent.keys[index]
            merging_keys = left_sibling.keys + [left_separator] + current_Node.keys + [right_separator] + right_sibling.keys
            new_separator = merging_keys[len(merging_keys)//2 - 1]
            merging_keys.pop(len(merging_keys)//2 - 1)
            parent.keys.pop(index)
            parent.keys.pop(index-1)
            parent.keys.insert(index-1, new_separator)
            merging_pointers = left_sibling.pointers + current_Node.pointers + right_sibling.pointers
            pivot = len(merging_keys)//2

            left_Node = b_tree.Node()
            left_Node.set_keys(merging_keys[:pivot])
            left_Node.set_pointers(merging_pointers[:pivot+1])
            left_Node.set_parent(parent)
            for child in left_Node.pointers:
                child.set_parent(left_Node)

            right_Node = b_tree.Node()
            right_Node.set_keys(merging_keys[pivot:])
            right_Node.set_pointers(merging_pointers[pivot+1:])
            right_Node.set_parent(parent)
            for child in right_Node.pointers:
                child.set_parent(right_Node)

            parent.pointers.remove(left_sibling)
            parent.pointers.remove(current_Node)
            parent.pointers.remove(right_sibling)
            parent.add_child(left_Node)
            parent.add_child(right_Node)

            self.merge(left_Node)
            self.merge(right_Node)
            
        # 2->1 merge
        else:
            if left_sibling is not None:
                for key in left_sibling.keys:
                    current_Node.keys.append(key)
                parent_key = parent.keys.pop(index-1)
                current_Node.keys.append(parent_key)
                current_Node.keys.sort(key=lambda x: x[0])
                parent.pointers.remove(left_sibling)
                for child in left_sibling.pointers:
                    current_Node.add_child(child)
                if parent.key_count() >= self.d:
                    self.split(current_Node)
                if parent.key_count() == 0 and parent.parent is None:
                    self.root = current_Node
                    current_Node.parent = None

            elif right_sibling is not None:
                for key in right_sibling.keys:
                    current_Node.keys.append(key)
                parent_key = parent.keys.pop(index)
                current_Node.keys.append(parent_key)
                current_Node.keys.sort(key=lambda x: x[0])
                parent.pointers.remove(right_sibling)
                for child in right_sibling.pointers:
                    current_Node.add_child(child)
                if parent.key_count() >= self.d:
                    self.split(current_Node)
                if parent.key_count() == 0 and parent.parent is None:
                    self.root = current_Node
                    current_Node.parent = None
            
            if parent.key_count() == 0 and parent.parent is None:
                self.root = current_Node
                current_Node.parent = None
        
        self.merge(parent)