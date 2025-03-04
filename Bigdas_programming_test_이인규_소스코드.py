import csv


class BTree_node:
    def __init__(self, is_leaf = False):
        self.key_value_list = []
        self.is_leaf = is_leaf
        self.children_node = []
        self.parent_node = None

class BTree:
    def __init__(self, max_children):
        self.max_children = max_children
        self.min_children = max_children // 2

        self.root = BTree_node(True) # root node는 초기엔 leaf node임

    def search(self, target_key, cur_node = None):
        if cur_node == None: #  root 노드부터 탐색
            cur_node = self.root

        search_index = binary_search(cur_node.key_value_list, target_key)

        if search_index < len(cur_node.key_value_list) and cur_node.key_value_list[search_index][0] == target_key: # 현재 node에서 찾은 경우
            return cur_node.key_value_list[search_index][1]

        else: # 자식 node 찾아봐야 함
            if cur_node.is_leaf == True: # 재귀적으로 자식을 탐색할때, 리프노드에도 없는 경우
                return None
            else:
                child_node = cur_node.children_node[search_index]

                return self.search(target_key, child_node)


    def insertion(self,key_value): # input = [key, value]
        cur_node = self.root # 현재 node
        overflow_node = self.insert_first(cur_node, key_value) # 삽입 먼저 진행하는 post order 방식식
        
        if overflow_node != None:
            handled_overflow_node = self.handle_overflow(overflow_node)

            if handled_overflow_node.parent_node == None: # root node인지 확인
                # root node라면 root node가 추가된 경우임

                # root node가 아니라면 root node까지지 split이 진행되지 않으면 
                # handle_overflow안에서 root node의 자식 node들만 변경(root node는 변경안됨)

                self.root = handled_overflow_node


    def insert_first(self, cur_node, key_value):
        if cur_node.is_leaf == True: # 해당 node에 바로 삽입하면 됨
            index_to_insert = binary_search(cur_node.key_value_list, key_value[0])
            cur_node.key_value_list.insert(index_to_insert, key_value)

            if len(cur_node.key_value_list) > self.max_children:
                return cur_node
            else:
                return None
            
        else: # 삽입할 node 찾아야 함
            child_index_to_insert = binary_search(cur_node.key_value_list, key_value[0])
            cur_node_child = cur_node.children_node[child_index_to_insert]
            return self.insert_first(cur_node_child, key_value)
        

    def handle_overflow(self, overflow_node):
        mid_index = len(overflow_node.key_value_list) // 2 
        parent_node = overflow_node.parent_node  # 부모 노드
        
        if parent_node is None:  # root node가 overflow
            new_root = BTree_node(False)  # 새로운 root node
            new_root.key_value_list.append(overflow_node.key_value_list[mid_index])

            left_child_node = BTree_node(overflow_node.is_leaf)
            right_child_node = BTree_node(overflow_node.is_leaf)

            left_child_node.key_value_list = overflow_node.key_value_list[:mid_index]
            right_child_node.key_value_list = overflow_node.key_value_list[mid_index+1:]

            if not overflow_node.is_leaf: # split할 node가 자식 존재 -> 자식 나눠가짐
                left_child_node.children_node = overflow_node.children_node[:mid_index+1]
                right_child_node.children_node = overflow_node.children_node[mid_index+1:]

                for child in left_child_node.children_node: # 원래 부모는 split할 node였음음
                    child.parent_node = left_child_node
                for child in right_child_node.children_node:
                    child.parent_node = right_child_node

            left_child_node.parent_node = new_root
            right_child_node.parent_node = new_root

            new_root.children_node.append(left_child_node)
            new_root.children_node.append(right_child_node)

            return new_root

        else:  # root node가 아닌 경우
            mid_key_value = overflow_node.key_value_list[mid_index] # 8
            parent_index_to_insert = binary_search(parent_node.key_value_list, mid_key_value[0]) # 1

            parent_node.key_value_list.insert(parent_index_to_insert, mid_key_value)

            left_child_node = BTree_node(overflow_node.is_leaf)
            right_child_node = BTree_node(overflow_node.is_leaf)

            parent_node.children_node.pop(parent_index_to_insert)
            parent_node.children_node.insert(parent_index_to_insert, left_child_node)
            parent_node.children_node.insert(parent_index_to_insert+1, right_child_node)
            

            left_child_node.key_value_list = overflow_node.key_value_list[:mid_index]
            right_child_node.key_value_list = overflow_node.key_value_list[mid_index+1:]
            

            if not overflow_node.is_leaf: # split할 node가 자식 존재 -> 자식 나눠가짐
                left_child_node.children_node = overflow_node.children_node[:mid_index+1]
                right_child_node.children_node = overflow_node.children_node[mid_index+1:]

                for child in left_child_node.children_node: # 원래 부모는 split할 node였음
                    child.parent_node = left_child_node
                for child in right_child_node.children_node:
                    child.parent_node = right_child_node


            left_child_node.parent_node = parent_node
            right_child_node.parent_node = parent_node

            if len(parent_node.key_value_list) > self.max_children:
                return self.handle_overflow(parent_node)

            return parent_node
            # 이 경우에는 handled_overflow_node의 부모가 존재w
            # self.root를 바꿀 필요없음
            # 위에서 self.root의 자식 node들이 바뀜
    

    def deletion(self, key_delete):
        underflow_node = self.delete_first(self.root, key_delete) # 삭제 먼저 진행

        if underflow_node != None: # root node가 아닌 node가 underflow 발생한 경우
            handled_underflow_node = self.handle_underflow(underflow_node)
        
            if handled_underflow_node.parent_node == None: # root node인지 확인
                # root node라면 root node가 추가된 경우임

                # root node가 아니라면 root node까지지 split이 진행되지 않으면 
                # handle_underflow안에서 root node의 자식 node들만 변경(root node는 변경안됨)

                self.root = handled_underflow_node


    def delete_first(self, cur_node, key_delete): # root node부터 탐색
        search_index = binary_search(cur_node.key_value_list, key_delete)

        if search_index < len(cur_node.key_value_list) and cur_node.key_value_list[search_index][0] == key_delete: # 현재 node에서 찾은 경우
            if cur_node.is_leaf == True: # leaf node는 바로 삭제 가능
                cur_node.key_value_list.pop(search_index) # 삭제 진행

                if len(cur_node.key_value_list) < self.min_children: # 삭제 진행 후에 underflow 발생한 경우 해당 node return
                    return cur_node
                else:
                    return None # underflow 발생하지 않아서 None return 

            else: 
                # successor를 찾고 삭제할 node로 대체하고 다시 삭제 재귀수행
                succesor_node = self.get_successor_node(cur_node, search_index)
                cur_node.key_value_list[search_index] = succesor_node.key_value_list[0] # succesor node의 가장 왼쪽 key와 value로 바꿈꿈
                return self.delete_first(succesor_node, succesor_node.key_value_list[0][0])
                

        else: # 자식 node 찾아봐야 함
            if cur_node.is_leaf == True: # 재귀적으로 자식을 탐색할때, 리프노드에도 없는 경우
                return None
            else:
                child_node = cur_node.children_node[search_index]
                return self.delete_first(child_node, key_delete) # succesor node로 다시 삭제 재귀 실행
             
            
    def get_successor_node(self, cur_node, search_index):
        # successor는 삭제할 key보다 크지만 가장 가까운 값임
        # succesor는 cur_node의 오른쪽 sub tree의 leaf node에서 가장 왼쪽의 key와 value임
        child_node = cur_node.children_node[search_index+1]
        while not child_node.is_leaf: # leaf node 탐색
            child_node = child_node.children_node[0] # 가장 왼쪽 노드
        
        return child_node


    def handle_underflow(self, underflow_node): 
        parent_node = underflow_node.parent_node # underflow node의 부모 node

        if parent_node == None: # root node인 경우
            return underflow_node # underflow node가 root node가 됨


        underflow_node_index = parent_node.children_node.index(underflow_node) # underflow node가 부모 node에서 몇번째 자식 node인지 나타내는 index

        if underflow_node_index == 0: # underflow node가 첫번째 자식인 경우
            right_sibling_node = parent_node.children_node[underflow_node_index+1]

            if len(right_sibling_node.key_value_list) > self.min_children: # 오른쪽 sibling node에서 하나 빌려올 수 있다면 빌려옴
                return self.borrow_from_right(underflow_node, right_sibling_node, parent_node, underflow_node_index) # borrow를 통해 underflow를 해결했다면 또 underflow가 일어나지 않음

            else: # 오른쪽 sibling node를 빌려왔을 때, 오른쪽 sibling node가 underflow 일어난다면, merge 진행
                return self.merge_with_right(underflow_node, right_sibling_node, parent_node, underflow_node_index)

        elif underflow_node_index == len(parent_node.children_node)-1: # underflow node가 마지막 자식인 경우
            left_sibling_node = parent_node.children_node[underflow_node_index-1]

            if len(left_sibling_node.key_value_list) > self.min_children: # 왼쪽 sibling node에서 하나 빌려올 수 있다면 빌려옴
                return self.borrow_from_left(underflow_node, left_sibling_node, parent_node, underflow_node_index) # borrow를 통해 underflow를 해결했다면 또 underflow가 일어나지 않음
            
            else: # 왼쪽 sibling node를 빌려왔을 때, 오른쪽 sibling node가 underflow 일어난다면, merge 진행
                return self.merge_with_left(underflow_node, left_sibling_node, parent_node, underflow_node_index)

        else: # underflow node가 가운데 자식임
            right_sibling_node = parent_node.children_node[underflow_node_index+1]
            left_sibling_node = parent_node.children_node[underflow_node_index-1]

            if len(right_sibling_node.key_value_list) > self.min_children: # 오른쪽 sibling node에서 하나 빌려올 수 있다면 빌려옴
                return self.borrow_from_right(underflow_node, right_sibling_node, parent_node, underflow_node_index) # borrow를 통해 underflow를 해결했다면 또 underflow가 일어나지 않음

            elif len(left_sibling_node.key_value_list) > self.min_children: # 왼쪽 sibling node에서 하나 빌려올 수 있다면 빌려옴
                return self.borrow_from_left(underflow_node, left_sibling_node, parent_node, underflow_node_index) # borrow를 통해 underflow를 해결했다면 또 underflow가 일어나지 않음
            
            else: # 양쪽 sibling에게 borrow할 수 없어서 merge해야 함
                # 오른쪽, 왼쪽 merge 중에 오른쪽 merge를 선택함
                # 왼쪽 merge를 선택해도 무관함
                return self.merge_with_right(underflow_node, right_sibling_node, parent_node, underflow_node_index)
            

    def merge_with_left(self, underflow_node, left_sibling_node, parent_node, underflow_node_index):
        parent_key_value_down = parent_node.key_value_list.pop(underflow_node_index-1) # underflow에게 내려갈 부모 node의 key와 value

        underflow_node.key_value_list.insert(0, parent_key_value_down) # underflow node가 부모node의 key와 value 받음

        underflow_node.key_value_list = left_sibling_node.key_value_list + underflow_node.key_value_list  # 왼쪽 sibling node의 key와 value 받음

        if not left_sibling_node.is_leaf: # 자식이 존재한다면 자식도 업데이트 해줘야 함
            underflow_node.children_node = left_sibling_node.children_node + underflow_node.children_node # 왼쪽 sibling node의 자식을 받음

            for child in left_sibling_node.children_node: # 왼쪽 sibling node의 자식도 underflow가 부모가 됨
                child.parent_node = underflow_node
        
        parent_node.children_node.pop(underflow_node_index - 1) # 왼쪽 sibling node 제거


        if len(parent_node.key_value_list) == 0: 
            # 만약 parent node의 key와 value를 가져왔더니, 빈 경우
            # 이 경우는 parent node가 root node일 경우밖에 없음
            # 이때는 merge된 underflow node가 root가 되어야 함
            underflow_node.parent_node = None # root node의 조건
            return underflow_node
        
        else: 
            if len(parent_node.key_value_list) < self.min_children: # parent node를 pop한 이후에 underflow가 발생했다면
                return self.handle_underflow(underflow_node=parent_node) # parent node를 재귀적으로 undeflow 처리함
            else:
                return parent_node
            

    def merge_with_right(self, underflow_node, right_sibling_node, parent_node, underflow_node_index):
        parent_key_value_down = parent_node.key_value_list.pop(underflow_node_index) # underflow에게 내려갈 부모 node의 key와 value

        underflow_node.key_value_list.append(parent_key_value_down) # underflow node가 부모node의 key와 value 받음

        underflow_node.key_value_list = underflow_node.key_value_list + right_sibling_node.key_value_list # 오른쪽 sibling node의 key와 value 받음

        if not right_sibling_node.is_leaf: # 자식이 존재한다면 자식도 업데이트 해줘야 함
            underflow_node.children_node = underflow_node.children_node + right_sibling_node.children_node # 오른쪽 sibling node의 자식을 받음

            for child in right_sibling_node.children_node: # 오른쪽 sibling node의 자식도 underflow가 부모가 됨
                child.parent_node = underflow_node
        
        parent_node.children_node.pop(underflow_node_index + 1) # 오른쪽 sibling node 제거


        if len(parent_node.key_value_list) == 0: 
            # 만약 parent node의 key와 value를 가져왔더니, 빈 경우
            # 이 경우는 parent node가 root node일 경우밖에 없음
            # 이때는 merge된 underflow node가 root가 되어야 함
            underflow_node.parent_node = None # root node의 조건
            return underflow_node
        
        else: 
            if len(parent_node.key_value_list) < self.min_children: # parent node를 pop한 이후에 underflow가 발생했다면
                return self.handle_underflow(underflow_node=parent_node) # parent node를 재귀적으로 undeflow 처리함
            else:
                return parent_node

    def borrow_from_right(self, underflow_node, right_sibling_node, parent_node, underflow_node_index):
        parent_key_value_down = parent_node.key_value_list[underflow_node_index] # underflow에게 내려갈 부모 node의 key와 value

        right_sibling_key_value_up = right_sibling_node.key_value_list.pop(0) # 부모 node에게 올라갈 오른쪽 sibling node의 key와 value

        parent_node.key_value_list[underflow_node_index] = right_sibling_key_value_up # 부모 node의 key와 value 업데이트

        underflow_node.key_value_list.append(parent_key_value_down) # underflow node의 key와 value 업데이트트


        if not right_sibling_node.is_leaf: # 자식이 존재한다면 자식도 업데이트 해줘야 함
            child_move = right_sibling_node.children_node.pop(0) # 오른쪽 sibling node의 가장 왼쪽 자식이 이동할 자식 node임

            underflow_node.children_node.append(child_move) # underflow node의 가장 오른쪽에 붙여줌

            child_move.parent_node = underflow_node # 부모 업데이트

        return parent_node 

    def borrow_from_left(self, underflow_node, left_sibling_node, parent_node, underflow_node_index):
        parent_key_value_down = parent_node.key_value_list[underflow_node_index-1] # underflow에게 내려갈 부모 node의 key와 value

        left_sibling_key_value_up = left_sibling_node.key_value_list.pop(-1) # 부모 node에게 올라갈 왼쪽 sibling node의 key와 value

        parent_node.key_value_list[underflow_node_index - 1] = left_sibling_key_value_up # 부모 node의 key와 value 업데이트

        underflow_node.key_value_list.insert(0, parent_key_value_down) # underflow node의 key와 value 업데이트트

        if not left_sibling_node.is_leaf: # 자식이 존재한다면 자식도 업데이트 해줘야 함
            child_to_move = left_sibling_node.children_node.pop(-1)  # 왼쪽 sibling node의 가장 오른쪽 자식이 이동할 자식 node임

            underflow_node.children_node.insert(0, child_to_move) # underflow node의 가장 왼쪽에 붙여줌

            child_to_move.parent_node = underflow_node # 부모 업데이트

        return parent_node

def binary_search(key_value_list, key):  
    # list의 key가 들어갈만한 왼쪽 index를 return
    # bisect left를 구현한 것
    key_list = [x[0] for x in key_value_list]

    left, right = 0, len(key_list)

    while left < right:
        mid = (left + right) // 2
        if key_list[mid] < key:
            left = mid + 1
        else:
            right = mid

    return left

def program_compare(file_read, file_write): # 입출력 파일 비교 함수
    print('comparing..')
    with open(file_read, 'r', encoding='utf-8') as f1, open(file_write, 'r', encoding='utf-8') as f2:
        content1 = f1.readlines()
        content2 = f2.readlines()
        if content1 == content2:
            print("comparing result: two files are totally same!")
        else:
            print("comparing result: two files are not totally same..")

def program_insert(BTree_class): # 프로그램에서 insert하는 함수
    file_read = input("file name to read: ")
    file_write = input("file name to write: ")


    with open(file_read, 'r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter='\t')
        print("inserting..")
        for row in reader:
            
            input_key = int(row[0])
            input_value = int(row[1])

            BTree_class.insertion([input_key, input_value])

    
    with open(file_write, 'w', newline='', encoding='utf-8') as file:
        print("writing..")
        writer = csv.writer(file, delimiter='\t')
        
        with open(file_read, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter='\t')
            for row in reader:
                key_search = int(row[0])

                value_search = BTree_class.search(target_key=key_search)

                writer.writerow([key_search, value_search])
                
    program_compare(file_read, file_write) # 비교하여 결과 출력

def program_delete(BTree_class): # 프로그램에서 delete하는 함수
    file_original = input("file name to delete: ") # delete할 파일 이름
    file_delete = input("file name of delete information: ") # 삭제 정보가 담긴 파일 이름
    file_write = input("file name to write: ")

    if file_delete == 'delete.csv':
        compare_file = 'delete_compare.csv'

    elif file_delete == 'delete2.csv':
        compare_file = 'delete_compare2.csv'

    with open(file_original, 'r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter='\t')
        print("inserting..")
        for row in reader:
            
            input_key = int(row[0])
            input_value = int(row[1])

            BTree_class.insertion([input_key, input_value])


    with open(file_delete, 'r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter='\t')
        print("deleting..")
        for row in reader:
            
            input_key = int(row[0])

            BTree_class.deletion(input_key)
    
    with open(file_write, 'w', newline='', encoding='utf-8') as file:
        print("writing..")
        writer = csv.writer(file, delimiter='\t')
        
        with open(file_original, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter='\t')
            for row in reader:
                key_search = int(row[0])

                value_search = BTree_class.search(target_key=key_search)

                if value_search == None:
                    value_write = 'N/A'
                else:
                    value_write = str(value_search)

                writer.writerow([key_search, value_write])
                
    program_compare(compare_file, file_write) # 비교하여 결과 출력

        
def program_run(): # 프로그램 실행함수 
    while True:
        BTree_class = BTree(100) 

        print("1. insertion \n2. deletion \n3. quit")

        order = int(input("Choose the operation you want: "))
        
        if order == 3:
            print("quit the program")
            break
        elif order == 1:
            program_insert(BTree_class)

        elif order == 2:
            program_delete(BTree_class)


if __name__ == '__main__':

    program_run()





