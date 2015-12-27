import AST
import SymbolTable
from Memory import *
from Exceptions import  *
from visit import *
import sys, time

sys.setrecursionlimit(10000)

class Interpreter(object):

    def __init__(self):
        self.memoryStack = MemoryStack()
        self.declaredType = None
        self.isFunctionScope = False

    @on('node')
    def visit(self, node):
        pass


    @when(AST.Program)
    def visit(self, node):
        node.parts.accept(self)

    @when(AST.Parts)
    def visit(self, node):
        for part in node.parts:
            part.accept(self)

    @when(AST.Part)
    def visit(self, node):
        pass


    @when(AST.Declaration)
    def visit(self, node):
        self.declaredType = node.type
        for init in node.inits.inits:
            init.accept(self)

    # @when(AST.Declarations)
    # def visit(self, node):
    #     for declaration in node.declarations:
    #         declaration.accept(self)


    @when(AST.Init)
    def visit(self, node):
        expr_val = node.expression.accept(self)
        self.memoryStack.insert(node.id, expr_val)
        return expr_val

    # @when(AST.Inits)
    # def visit(self, node):
    #     for init in node.inits:
    #         init.accept(self)

    @when(AST.Instructions)
    def visit(self, node):
        for instruction in node.instructions:
            instruction.accept(self)


    @when(AST.BinExpr)
    def visit(self, node):

        # r1 = node.expr1.accept(self)
        # r2 = node.expr2.accept(self)
        # return eval(("{0}" + node.operator + "{1}").format(r1, r2))

        file_ = open('Failed.txt', 'a')
        file_.write("tu dziala\n")
        file_.close()

        left_node = node.expr1.accept(self)
        if type(left_node) == AST.Const:
            left = left_node.value
        else:
            left = left_node
        left_type = type(left).__name__

        right_node = node.expr2.accept(self)
        if type(right_node) == AST.Const:
            right = right_node.value
        else:
            right = right_node
        right_type = type(right).__name__

        operator = node.operator


############

        returned_type = {'Integer': {}, 'Float': {}, 'String': {}, 'Boolean': {}}
        for i in returned_type.keys():
            returned_type[i] = {}
            for j in returned_type.keys():
                returned_type[i][j] = {}
                for k in ['+', '-', '/', '*', '==', '>=', '<=', '!=']:
                    returned_type[i][j][k] = None

        returned_type['Integer']['Float']['+'] = 'Float'
        returned_type['Integer']['Integer']['+'] = 'Integer'
        returned_type['Float']['Float']['+'] = 'Float'
        returned_type['Float']['Integer']['+'] = 'Float'
        returned_type['String']['String']['+'] = 'String'
        returned_type['Integer']['Float']['-'] = 'Float'
        returned_type['Integer']['Integer']['-'] = 'Integer'
        returned_type['Float']['Float']['-'] = 'Float'
        returned_type['Float']['Integer']['-'] = 'Float'
        returned_type['Integer']['Float']['*'] = 'Float'
        returned_type['Integer']['Integer']['*'] = 'Integer'
        returned_type['Float']['Float']['*'] = 'Float'
        returned_type['Float']['Integer']['*'] = 'Float'
        returned_type['String']['Integer']['*'] = 'String'
        returned_type['Integer']['Float']['/'] = 'Float'
        returned_type['Integer']['Integer']['/'] = 'Integer'
        returned_type['Float']['Float']['/'] = 'Float'
        returned_type['Float']['Integer']['/'] = 'Float'
        returned_type['Float']['Float']['=='] = 'Boolean'
        returned_type['Integer']['Integer']['=='] = 'Boolean'
        returned_type['String']['String']['=='] = 'Boolean'
        returned_type['Float']['Float']['!='] = 'Boolean'
        returned_type['Integer']['Integer']['!='] = 'Boolean'
        returned_type['String']['String']['!='] = 'Boolean'
        returned_type['Float']['Float']['>='] = 'Boolean'
        returned_type['Integer']['Integer']['>='] = 'Boolean'
        returned_type['String']['String']['>='] = 'Boolean'
        returned_type['Float']['Float']['<='] = 'Boolean'
        returned_type['Integer']['Integer']['<='] = 'Boolean'
        returned_type['String']['String']['<='] = 'Boolean'
        returned_type['Float']['Integer']['=='] = 'Boolean'
        returned_type['Integer']['Float']['=='] = 'Boolean'
        returned_type['Float']['Integer']['!='] = 'Boolean'
        returned_type['Integer']['Float']['!='] = 'Boolean'
        returned_type['Float']['Integer']['>='] = 'Boolean'
        returned_type['Integer']['Float']['>='] = 'Boolean'
        returned_type['Float']['Integer']['<='] = 'Boolean'
        returned_type['Integer']['Float']['<='] = 'Boolean'
        returned_type['Integer']['Integer']['<<'] = 'Integer'
        returned_type['Integer']['Integer']['>>'] = 'Integer'
        returned_type['Integer']['Integer']['|'] = 'Integer'
        returned_type['Integer']['Integer']['&'] = 'Integer'
        returned_type['Integer']['Integer']['^'] = 'Integer'
        returned_type['Integer']['Integer']['<'] = 'Boolean'
        returned_type['Float']['Float']['<'] = 'Boolean'
        returned_type['Float']['Integer']['<'] = 'Boolean'
        returned_type['Integer']['Float']['<'] = 'Boolean'
        returned_type['Boolean']['Boolean']['<'] = 'Boolean'
        returned_type['Float']['Float']['>'] = 'Boolean'
        returned_type['Float']['Integer']['>'] = 'Boolean'
        returned_type['Integer']['Float']['>'] = 'Boolean'
        returned_type['Integer']['Integer']['>'] = 'Boolean'
        returned_type['Boolean']['Boolean']['>'] = 'Boolean'
        returned_type['Boolean']['Boolean']['&&'] = 'Boolean'
        returned_type['Boolean']['Boolean']['||'] = 'Boolean'
        returned_type['Integer']['Integer']['%'] = 'Integer'
        returned_type['Integer']['Float']['%'] = 'Integer'
        returned_type['Float']['Integer']['%'] = 'Integer'
        returned_type['Float']['Float']['%'] = 'Integer'

###########

        left = left_type[0].upper() + left_type[1:]
        right = right_type[0].upper() + right_type[1:]

        if left == 'Int':
            left += 'eger'
        if right == 'Int':
            right += 'eger'

        res_type = returned_type[left][right][node.operator]
        if res_type is None:
           return None

        # perform operation...
        result = None
        if operator == '+':
            if type(left) is str and type(right) is str:
                result = left + right
            else:
                result = left.value + right.value
        elif operator == '-':
            result = left.value - right.value
        elif operator == '*':
            result = left.value * right.value
        elif operator == '/':
            try:
                result = left.value / right.value
            except ZeroDivisionError:
                print "Line {0}: Division by 0.".format(node.line_no)
                return None
        elif operator == '%':
            try:
                result = left.value % right.value
            except ZeroDivisionError:
                print "Line {0}: Division by 0.".format(node.line_no)
                return None
        elif operator == '==':
            result = left.value == right.value
        elif operator == '!=':
            result = left.value != right.value
        elif operator == '>=':
            result = left.value >= right.value
        elif operator == '<=':
            result = left.value <= right.value
        elif operator == '>':
            if type(left) is str and type(right) is str:
                result = left > right
            else:
                result = left.value > right.value
        elif operator == '<':
            if type(left) is str and type(right) is str:
                result = left < right
            else:
                result = left.value < right.value
        elif operator == '|':
            result = left.value | right.value
        elif operator == '&':
            result = left.value & right.value
        elif operator == '^':
            result = left.value ^ right.value
        elif operator == '>>':
            result = left.value >> right.value
        elif operator == '<<':
            result = left.value << right.value
        elif operator == '&&':
            result = left.value and right.value
        elif operator == '||':
            result = left.value and right.value

        # create result node
        if type(result) is int:
            res_node = int(result)
        elif type(result) is float:
            res_node = float(result)
        elif type(result) is str:
            res_node = str(result)
        else:
            res_node = bool(result)

        return res_node

        # try sth smarter than:
        # if(node.op=='+') return r1+r2
        # elsif(node.op=='-') ...
        # but do not use python eval
        # dopisac evaluatora, ktory przyjmie argumeny, operator i zwroci wynik (search on GitHub)



    @when(AST.Assignment)
    def visit(self, node):
        expr_accept = node.expression.accept(self)
        self.memoryStack.set(node.id, expr_accept)
        return expr_accept

    @when(AST.Choice)
    def visit(self, node):
        if node._if.accept(self) is False:
            if node._else is not None:
                node._else.accept(self)

    @when(AST.If)
    def visit(self, node):
        if node.cond.accept(self):
            return node.statement.accept(self)
        else:
            return False

    @when(AST.Else)
    def visit(self, node):
        return node.statement.accept(self)


    @when(AST.Const)
    def visit(self, node):
        return node.value

    @when(AST.While)
    def visit(self, node):
        while node.cond.accept(self):
            try:
                node.statement.accept(self)
            except BreakException:
                break
            except ContinueException:
                pass


    @when(AST.RepeatUntil)
    def visit(self,node):
        while True:
            try:
                node.statement.accept(self)
                if node.cond.accept(self):
                    break
            except BreakException:
                break
            except ContinueException:
                if node.cond.accept(self):
                    break

    @when(AST.Compound)
    def visit(self, node):
        if not self.isFunctionScope:
            newMemory = Memory("scope")
            self.memoryStack.push(newMemory)
            node.parts.accept(self)
            self.memoryStack.pop()
        else:
            node.parts.accept(self)
            self.isFunctionScope = False

    @when(AST.Break)
    def visit(self, node):
        raise BreakException()

    @when(AST.Continue)
    def visit(self, node):
        raise ContinueException()

    @when(AST.Return)
    def visit(self, node):
        value = node.expression.accept(self)
        raise ReturnValueException(value)

    @when(AST.ArgumentList)
    def visit(self, node):
        for arg in node.arg_list:
            arg.accept(self)

    @when(AST.Argument)
    def visit(self, node):
        return node.id

    @when(AST.ExpressionList)
    def visit(self, node):
        for expression in node.expressions:
            expression.accept(self)

    @when(AST.Labeled)
    def visit(self, node):
        node.instruction.accept(self)

    @when(AST.Print)
    def visit(self, node):
        value = node.expression.accept(self)
        if isinstance(value, basestring):
            value = value.replace("\"", "")
        print value

    @when(AST.Id)
    def visit(self, node):
        return self.memoryStack.get(node.id)

    @when(AST.FunctionDefinitions) ###
    def visit(self, node):
        for fundef in node.fundefs:
            fundef.accept(self)

    @when(AST.FunctionDefinition)
    def visit(self, node):
        self.memoryStack.insert(node.id, node)

    @when(AST.FunctionCall)
    def visit(self, node):
        function = self.memoryStack.get(node.id)
        functionMemory = Memory(node.id)
        for argId, argExpr in zip(function.arglist.arg_list, node.expression_list.expressions):
            functionMemory.put(argId.accept(self), argExpr.accept(self))
        self.memoryStack.push(functionMemory)
        self.isFunctionScope = True
        try:
            function.compound_instr.accept(self)
        except ReturnValueException as e:
            return e.value
        finally:
            self.isFunctionScope = False
            self.memoryStack.pop()

    @when(AST.ExpressionInPar)
    def visit(self, node):
        return node.expression.accept(self)