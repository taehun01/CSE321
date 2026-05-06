import csv
import time
import random
import b_tree
import b_plus_tree
import b_star_tree

class EvalBtree(b_tree.Btree):
    def __init__(self, d=4):
        super().__init__(d)

class EvalBstartree(b_star_tree.Bstartree):
    def __init__(self, d=4):
        super().__init__(d)

class EvalBplustree(b_plus_tree.Bplustree):
    def __init__(self, d=4):
        super().__init__(d)


def load_data(filename):
    csv_data = []
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader) 
        for row in reader:
            csv_data.append({
                'id': int(row[0]),
                'name': row[1],
                'gender': row[2],
                'gpa': float(row[3]),
                'height': float(row[4])
            })
    return csv_data


def calculate_key_node_count(current_Node, d):
    if current_Node is None:
        return 0, 0
    keys_count = current_Node.key_count()
    nodes_count = 1
    for child in current_Node.pointers:
        i, j = calculate_key_node_count(child, d)
        keys_count += i
        nodes_count += j
    return keys_count, nodes_count


def btree_range_query(current_Node, start_key, end_key, result):
    if current_Node is None:
        return
    i = 0
    while i < current_Node.key_count() and current_Node.keys[i][0] < start_key:
        i += 1
    if current_Node.pointers:
        btree_range_query(current_Node.pointers[i], start_key, end_key, result)
    while i < current_Node.key_count() and current_Node.keys[i][0] <= end_key:
        result.append(current_Node.keys[i])
        if current_Node.pointers:
            btree_range_query(current_Node.pointers[i+1], start_key, end_key, result)
        i += 1


def evaluations():
    print("Loading data from student.csv...")
    csv_data = load_data("student.csv")
    dataset_size = len(csv_data)
    print(f"Loaded {dataset_size} records.\n")
    
    orders = [3, 5, 10]
    EvalBtrees = [
        ("B -Tree", EvalBtree),
        ("B*-Tree", EvalBstartree),
        ("B+-Tree", EvalBplustree)
    ]
    
    d_10_trees = {}
    
    print("--- Evaluation 1: Insertion & Parameter Tuning ---")
    for d in orders:
        print(f"\nEvaluating Order d={d}")
        for name, Tree in EvalBtrees:
            tree = Tree(d=d)
    
            start_time = time.time()
            for rid, record in enumerate(csv_data):
                tree.insert(record['id'], rid)
            exec_time = time.time() - start_time
            
            keys_count, nodes_count = calculate_key_node_count(tree.root, d)
            max_possible_keys = nodes_count * (d-1) 
            if max_possible_keys > 0:
                utilization = (keys_count / max_possible_keys) * 100
            else:
                utilization = 0
            print(f"  {name}: Time={exec_time:.4f}s | Splits={tree.split_count} | Node Util={utilization:.2f}%")
            
            if d == 10:
                d_10_trees[name] = tree

    print("\n--- Evaluation 2: Point Search (d=10) ---")
    search_sample_size = 10000
    search_keys = [record['id'] for record in random.sample(csv_data, search_sample_size)]
    
    for name, tree in d_10_trees.items():
        start_time = time.time()
        for key in search_keys:
            tree.search(key)
        exec_time = time.time() - start_time
        mean_time = exec_time / search_sample_size
        print(f"  {name}: Total Time={exec_time:.4f}s | Mean Retrieval Time={mean_time:.6f}s")

    print("\n--- Evaluation 3: Range Query (d=10) ---")
    start_range = 202000000
    end_range = 202100000
    print(f"Query: Avg GPA and Height of Male students between {start_range} and {end_range}")
    
    for name, tree in d_10_trees.items():
        start_time = time.time()
        result_keys = []
        
        if name == "B+-Tree":
            result_keys = tree.range_query(start_range, end_range)
        else:
            btree_range_query(tree.root, start_range, end_range, result_keys)
            
        gpa_sum = 0.0
        height_sum = 0.0
        count = 0
        for key, rid in result_keys:
            if rid is not None:
                record = csv_data[rid]
                if record['gender'] == 'Male':
                    gpa_sum += record['gpa']
                    height_sum += record['height']
                    count += 1
        if count == 0:
            avg_gpa, avg_height = 0.0, 0.0
        else:
            avg_gpa, avg_height = gpa_sum / count, height_sum / count

        exec_time = time.time() - start_time
        print(f"  {name}: Time={exec_time:.4f}s | Avg GPA={avg_gpa:.2f}, Avg Height={avg_height:.2f} | records Scanned={len(result_keys)}")

    print("\n--- Evaluation 4: Deletion & Structural Integrity (d=10) ---")
    delete_sample_size = 20000
    delete_keys = [record['id'] for record in random.sample(csv_data, delete_sample_size)]
    
    for name, tree in d_10_trees.items():
        start_time = time.time()
        for key in delete_keys:
            tree.remove(key)
        exec_time = time.time() - start_time
        
        keys_count, nodes_count = calculate_key_node_count(tree.root, tree.d)
        print(f"  {name}: Deletion Time for {delete_sample_size} records = {exec_time:.4f}s | Remaining Total Nodes = {nodes_count}")


evaluations()