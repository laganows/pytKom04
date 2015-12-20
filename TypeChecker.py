import re
from SymbolTable import SymbolTable, VariableSymbol, Function
import AST

ttype = {}
operators = ['+', '-', '*', '/', '%','|', '&', '^', '<<', '>>','&&', '||','==', '!=', '>', '<', '<=', '>=','=']

for operator in operators:
    ttype[operator] = {}
    for type_ in ['int', 'float', 'string']:
        ttype[operator][type_] = {}

#arithmetic operations
ttype['+']['int']['int'] = 'int'
ttype['+']['int']['float'] = 'float'
ttype['+']['float']['int'] = 'float'
ttype['+']['float']['float'] = 'float'

ttype['-']['int']['int'] = 'int'
ttype['-']['int']['float'] = 'float'
ttype['-']['float']['int'] = 'float'
ttype['-']['float']['float'] = 'float'

ttype['*']['int']['int'] = 'int'
ttype['*']['int']['float'] = 'float'
ttype['*']['float']['int'] = 'float'
ttype['*']['float']['float'] = 'float'

ttype['/']['int']['int'] = 'int'
ttype['/']['int']['float'] = 'float'
ttype['/']['float']['int'] = 'float'
ttype['/']['float']['float'] = 'float'

ttype['%']['int']['int'] = 'int'
ttype['%']['int']['float'] = 'float'
ttype['%']['float']['int'] = 'float'
ttype['%']['float']['float'] = 'float'

ttype['+']['string']['string'] = 'string'
ttype['*']['string']['int'] = 'string'
ttype['=']['float']['int'] = 'float'
ttype['=']['float']['float'] = 'float'
ttype['=']['int']['int'] = 'int'
ttype['=']['string']['string'] = 'string'
ttype['=']['int']['float'] = ('int', 'warn')

#bitwise operations
ttype['|']['int']['int'] = 'int'
ttype['&']['int']['int'] = 'int'
ttype['^']['int']['int'] = 'int'
ttype['<<']['int']['int'] = 'int'
ttype['>>']['int']['int'] = 'int'

#logic operators
ttype['&&']['int']['int'] = 'int'
ttype['||']['int']['int'] = 'int'

#comparison operators
ttype['==']['int']['int'] = 'int'
ttype['==']['int']['float'] = 'int'
ttype['==']['float']['int'] = 'int'
ttype['==']['float']['float'] = 'int'
ttype['==']['string']['string'] = 'int'

ttype['!=']['int']['int'] = 'int'
ttype['!=']['int']['float'] = 'int'
ttype['!=']['float']['int'] = 'int'
ttype['!=']['float']['float'] = 'int'
ttype['!=']['string']['string'] = 'int'

ttype['>']['int']['int'] = 'int'
ttype['>']['int']['float'] = 'int'
ttype['>']['float']['int'] = 'int'
ttype['>']['float']['float'] = 'int'
ttype['>']['string']['string'] = 'int'

ttype['<']['int']['int'] = 'int'
ttype['<']['int']['float'] = 'int'
ttype['<']['float']['int'] = 'int'
ttype['<']['float']['float'] = 'int'
ttype['<']['string']['string'] = 'int'

ttype['<=']['int']['int'] = 'int'
ttype['<=']['int']['float'] = 'int'
ttype['<=']['float']['int'] = 'int'
ttype['<=']['float']['float'] = 'int'
ttype['<=']['string']['string'] = 'int'

ttype['>=']['int']['int'] = 'int'
ttype['>=']['int']['float'] = 'int'
ttype['>=']['float']['int'] = 'int'
ttype['>=']['float']['float'] = 'int'
ttype['>=']['string']['string'] = 'int'


class NodeVisitor(object):

    def visit(self, node, *args):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node, *args)

    def generic_visit(self, node, *args):        # Called if no explicit visitor function exists for a node.
        if isinstance(node, list):
            for elem in node:
                self.visit(elem, *args)
        else:
            if node is None:
                pass
            else:
                for child in node.children:
                    if isinstance(child, list):
                        for item in child:
                            if isinstance(item, AST.Node):
                                self.visit(item, *args)
                    elif isinstance(child, AST.Node):
                        self.visit(child, *args)


class TypeChecker(NodeVisitor):

    def findVariable(self, tab, variable):
        if variable in tab.symbols:
            return tab.get(variable)
        elif tab.symbol.name == variable:
            return tab.symbol
        elif tab.getParentScope() is not None:
            return self.findVariable(tab.getParentScope(), variable)

    def visit_Program(self, node):
        tab = SymbolTable(None, "program", None)
        self.scope = tab
        self.actFunc = None
        self.actComp = None
        self.actLoop = []
        self.noErrors = True
        self.visit(node.parts, tab)

    def visit_Parts(self, node, tab):
        for part in node.parts:
            self.visit(part, tab)

    def visit_Part(self, node, tab):
        pass

    def visit_Declaration(self, node, tab):
        self.visit(node.inits, tab, node.type)

    def visit_Inits(self, node, tab, type):
        for init in node.inits:
            self.visit(init, tab, type)

    def visit_Init(self, node, tab, type):
        if node.id in tab.symbols and self.actFunc != None:
            print "Error: Function identifier '{0}' used as a variable: line {1}".format(node.id, node.line)
            self.noErrors = False

        elif node.id in tab.symbols:
            print "Error: Variable '{0}' already declared: line {1}".format(node.id, node.line)
            self.noErrors = False


        value_type = self.visit(node.expression, tab)
        if not value_type in ttype['='][type]:
            print "Error: Assignment of {0} to {1}: line {2}" \
                .format(value_type, type, node.line)
            self.noErrors = False

        else:
            if "warn" in ttype['='][type][value_type]:
                print "Warning: Assignment of {0} to {1}: line {2}" \
                    .format(value_type, type, node.line)

            tab.put(node.id, VariableSymbol(node.id, type, node.expression))

    def visit_Instructions(self, node, tab):
        for instruction in node.instructions:
            self.visit(instruction, tab)

    def visit_Instruction(self, node, tab):
        pass

    def visit_Print(self, node, tab):
        self.visit(node.expression, tab)

    def visit_Labeled(self, node, tab):
        self.visit(node.instruction, tab)

    def visit_Assignment(self, node, tab):
        variable = self.findVariable(tab, node.id)
        if variable is None:
            print "Error: Variable '{0}' undefined in current scope: line {1}".format(node.id, node.line-1)
            self.noErrors = False
        else:
            value_type = self.visit(node.expression, tab)
            if value_type != None:
                if not value_type in ttype["="][variable.type]:
                    print "Error: Assignment of {0} to {1}: line {2}" \
                        .format(value_type, variable.type, node.line)
                    self.noErrors = False

                else:
                    if "warn" in ttype["="][variable.type][value_type]:
                        print "Warning: Value of type {0} assigned to symbol {1} of type {2}: line {3}" \
                                .format(value_type, node.id, variable.type, node.line)
                    return ttype["="][variable.type][value_type]

    def visit_Choice(self, node, tab):
        self.visit(node._if, tab)
        self.visit(node._else, tab)

    def visit_If(self, node, tab):
        self.visit(node.cond, tab)
        self.visit(node.statement, tab)

    def visit_Else(self, node, tab):
        self.visit(node.statement, tab)

    def visit_While(self, node, tab):
        self.visit(node.cond, tab)
        self.actLoop.append(node)
        self.visit(node.statement, tab)
        self.actLoop.pop()

    def visit_RepeatUntil(self, node, tab):
        self.visit(node.cond, tab)
        self.actLoop.append(node)
        self.visit(node.statement, tab)
        self.actLoop.pop()

    def visit_Return(self, node, tab):
        if not type(self.actFunc)==AST.FunctionDefinition:
            print "Error: Return instruction outside a function: line {0}".format(node.line-2)
            self.noErrors = False
        else:
            rettype = self.visit(node.expression, tab)
            if rettype != self.actFunc.type and rettype != None:
                print "Error: Improper returned type, expected {2}, got {0}: line {1}".format(rettype, node.line-1, self.actFunc.type)
                self.noErrors = False

            self.hasReturn = True

    def visit_Continue(self, node, tab):
        if not type(self.actLoop[-1])==AST.While and not type(self.actLoop[-1])==AST.RepeatUntil:
            print "Error: continue instruction outside a loop: line {0}".format(node.line-1)
            self.noErrors = False

    def visit_Break(self, node, tab): #node - wezel drzewa
        if not type(self.actLoop[-1])==AST.While and not type(self.actLoop[-1])==AST.RepeatUntil:
            print "Error: break instruction outside a loop: line {0}".format(node.line-1)
            self.noErrors = False

    def visit_Compound(self, node, tab, *args):
        if len(args) > 0 and args[0] is True:
            self.visit(node.parts, tab)
        else:
            tab = tab.pushScope(node)
            self.actComp = node
            self.visit(node.parts, tab)
            self.actComp = None
            tab = tab.popScope()

    def visit_Condition(self, node, tab):
        pass

    def visit_Expression(self, node, tab):
        pass

    def visit_Const(self, node):
        if re.match(r"(\+|-){0,1}(\d+\.\d+|\.\d+)", node.value):
            return self.visit_Float(node)
        elif re.match(r"(\+|-){0,1}\d+", node.value):
            return self.visit_Integer(node)
        elif re.match(r"\A('.*'|\".*\")\Z", node.value):
            return self.visit_String(node)
        else:
            variable = self.scope.get(node.value)
            if variable is None:
                print "Variable {} in line {} hasn't been declared".format(node.value, node.line)
            else:
                return variable.type

    def visit_Integer(self, node):
        return 'int'

    def visit_Float(self,node):
        return 'float'

    def visit_String(self,node):
        return 'string'

    def visit_Id(self, node, tab):
        variable = self.findVariable(tab, node.id)
        if variable is None:
            print "Error: Usage of undeclared variable '{0}': line {1}".format(node.id, node.line)
            self.noErrors = False

        else:
            return variable.type

    def visit_BinExpr(self, node, tab):
        type1 = self.visit(node.expr1, tab)
        type2 = self.visit(node.expr2, tab)
        op = node.operator;
        if type1 is None or not type2 in ttype[op][type1]:
            print "Error: Illegal operation, {0} {1} {2}: line {3}".format(type1, op, type2, node.line)
            self.noErrors = False

        else:
            return ttype[op][type1][type2]

    def visit_ExpressionInPar(self, node, tab):
        expression = node.expression
        return self.visit(expression, tab)

    def visit_FunctionCall(self, node, tab):
        function = self.findVariable(tab, node.id)
        if function is None:
            print "Error: Call of undefined fun: '{0}': line {1}".format(node.id, node.line)
            self.noErrors = False

        else:
            if len(function.arguments.arg_list) != len(node.expression_list.expressions):
                print "Error: Improper number of args in {0} call: line {1}".format(node.id, node.line)
                self.noErrors = False

            else:
                for i in range(len(function.arguments.arg_list)):
                    arg_type = function.arguments.arg_list[i].type
                    given_type = self.visit(node.expression_list.expressions[i], tab)
                    if not given_type in ttype['='][arg_type]:
                        print "Error: Improper type of args in {0} call: line {1}".format(node.id, node.line)
                        self.noErrors = False

                        break

            self.visit(node.expression_list, tab)
            return function.type

    def visit_ExpressionList(self, node, tab):
        for expression in node.expressions:
            self.visit(expression, tab)

    def visit_FunctionDefinitions(self, node, tab):
        for fundef in node.fundefs:
            self.visit(fundef, tab)

    def visit_FunctionDefinition(self, node, tab):
        fun_name = self.findVariable(tab, node.id)
        if not fun_name is None:
            print "Error: Redefinition of function '{0}': line {1}".format(node.id, node.arglist.line)
            self.noErrors = False

        else:
            tab.put(node.id, Function(node.id, node.type, node.arglist))
            tab = tab.pushScope(node.id)
            tab.put(node.id, Function(node.id, node.type, node.arglist))
            self.actFunc = node
            self.hasReturn = False
            self.visit(node.arglist, tab)
            self.visit(node.compound_instr, tab, True)
            if self.hasReturn == False:
                print "Error: Missing return statement in function '{0}' function returning {2}: line {1}".format(node.id, node.arglist.line, self.actFunc.type)
                self.noErrors = False

            self.hasReturn = False
            self.actFunc = None
            tab = tab.popScope()

    def visit_ArgumentList(self, node, tab):
        for arg in node.arg_list:
            self.visit(arg, tab)

    def visit_Argument(self, node, tab):
        if node.id in tab.symbols:
            print "Error: Redefinition of symbol {0}: line {1}".format(node.id, node.line)
            self.noErrors = False

        else:
            tab.put(node.id, VariableSymbol(node.id, node.type, None))
            return node.type