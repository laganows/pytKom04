
class Memory:

    def __init__(self, name): # memory name
        self.memory_name = name
        self.memory_set = {}

    def has_key(self, name):  # variable name
        return self.memory_set.has_key(name)

    def get(self, name):         # gets from memory current value of variable <name>
        if not self.has_key(name):
            return None
        return self.memory_set[name]

    def put(self, name, value):  # puts into memory current value of variable <name>
        self.memory_set[name] = value

        
class MemoryStack:
                                                                             
    def __init__(self, memory=None): # initialize memory stack with memory <memory>
        self.memory_stack = []
        if memory is None:
            self.memory_stack.append(Memory("sth"))
        else:
            self.memory_stack.append(memory)

    def get(self, name):             # gets from memory stack current value of variable <name>
        for i in range(1, len(self.memory_stack) + 1):
            if self.memory_stack[-i].has_key(name):
                return self.memory_stack[-i].get(name)
        return None

    def insert(self, name, value): # inserts into memory stack variable <name> with value <value>
        self.memory_stack[-1].put(name, value)

    def set(self, name, value): # sets variable <name> to value <value>
        for i in range(1, len(self.memory_stack) + 1):
            if self.memory_stack[-i].has_key(name):
                self.memory_stack[-i].put(name, value)
                return None
        
    def push(self, memory): # pushes memory <memory> onto the stack
        self.memory_stack.append(memory)

    def pop(self):          # pops the top memory from the stack
        return self.memory_stack.pop()