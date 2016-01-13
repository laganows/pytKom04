import re
import AST
from Memory import *
from Exceptions import *
from visit import *
import sys

sys.setrecursionlimit(10000)

class Interpreter(object):

    def __init__(self):
        self.isOutsideFunction = True
        self.stack = MemoryStack()
        self.nodeDeclarationType = None

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
        self.nodeDeclarationType = node.type
        for init in node.inits.inits:
            init.accept(self)

    @when(AST.Init)
    def visit(self, node):
        tmp = node.expression.accept(self)
        self.stack.insert(node.id, tmp)
        return tmp

    @when(AST.Instructions)
    def visit(self, node):
        for instruction in node.instructions:
            instruction.accept(self)

    @when(AST.BinExpr)
    def visit(self, node):
        r1 = node.expr1.accept(self)
        r2 = node.expr2.accept(self)

        if node.operator == '+':
            return r1 + r2
        elif node.operator == '-':
            return r1 - r2
        elif node.operator == '*':
            return r1 * r2
        elif node.operator == '/':
            return r1 / r2
        elif node.operator == '>':
            return 1 if r1 > r2 else 0
        elif node.operator == '<':
            return 1 if r1 < r2 else 0
        elif node.operator == '>=':
            return 1 if r1 >= r2 else 0
        elif node.operator == '<=':
            return 1 if r1 <= r2 else 0
        elif node.operator == '==':
            return 1 if r1 == r2 else 0
        elif node.operator == '!=':
            return 1 if r1 != r2 else 0
        elif node.operator == '%':
            return r1 % r2
        elif node.operator == '&':
            return r1 & r2
        elif node.operator == '^':
            return r1 ^ r2
        elif node.operator == '|':
            return r1 | r2
        elif node.operator == '<<':
            return r1 << r2
        elif node.operator == '>>':
            return r1 >> r2


    @when(AST.Assignment)
    def visit(self, node):
        tmp = node.expression.accept(self)
        self.stack.set(node.id, tmp)
        return tmp

    @when(AST.Choice)
    def visit(self, node):
        if node._if.accept(self) is False and node._else is not None:
            return node._else.accept(self)

    @when(AST.If)
    def visit(self, node):
        return node.statement.accept(self) if node.cond.accept(self) else False

    @when(AST.Else)
    def visit(self, node):
        return node.statement.accept(self)


    @when(AST.Const)
    def visit(self, node):
        if re.match(r"(\+|-){,1}(\.\d+|\d+\.\d+)", node.value):
            return float(node.value)
        elif re.match(r"(\+|-){,1}\d+", node.value):
            return int(node.value)
        elif type(node.value) is str:
            return node.value
        else:
            item = self.stack.get(node.value)
            if item is not None:
                return item.value
            else:
                return item

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
        if self.isOutsideFunction:
            new = Memory("new")
            self.stack.push(new)
            node.parts.accept(self)
            self.stack.pop()
        else:
            node.parts.accept(self)
            self.isOutsideFunction = True

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
        return self.stack.get(node.id)

    @when(AST.FunctionDefinitions)
    def visit(self, node):
        for fundef in node.fundefs:
            fundef.accept(self)

    @when(AST.FunctionDefinition)
    def visit(self, node):
        self.stack.insert(node.id, node)

    @when(AST.FunctionCall)
    def visit(self, node):
        fun = self.stack.get(node.id)
        funMemory = Memory(node.id)
        tmp = len(fun.arglist.arg_list)
        tmp2 = len(node.expression_list.expressions)

        for i in range(0, min(tmp, tmp2), 1):
            funMemory.put(fun.arglist.arg_list[i].accept(self), node.expression_list.expressions[i].accept(self))

        self.stack.push(funMemory)
        self.isOutsideFunction = False
        try:
            fun.compound_instr.accept(self)
        except ReturnValueException as er:
            return er.value
        finally:
            self.isOutsideFunction = True
            self.stack.pop()

    @when(AST.ExpressionInPar)
    def visit(self, node):
        return node.expression.accept(self)