import ast
import copy
from pyproteum.print_visit import PrintVisit



class MyOperator(ast.NodeTransformer):
	
	def __init__(self, original):
		self.original = copy.deepcopy(original)
		self.mutants = []
		self.function = ''
		self.func_lineno = 0
		self.func_end_lineno = 0		
		self.docstrings = set()
		self.pre_visit(self.original)

	def pre_visit(self, tree):
		for node in ast.walk(tree):
			try:
				if ast.get_docstring(node):
					fn = node.body[0]
					self.docstrings.add(id(fn))
			except: 
				continue

	def salva_muta(self, node, func, ln, eln, seq=1):
		cop = copy.deepcopy(self.original)
		#self.ajustar_col_offsets(cop, node.lineno, node.col_offset, desloca)
		ast.fix_missing_locations(cop)

		if self.check_sintaxe(cop):
			muta = MutantDict({'function': func,
					'func_lineno': ln,
					'func_end_lineno': eln,
					'operator': str(self),
					'lineno':node.lineno,
					'col_offset':node.col_offset,
					'end_lineno':node.end_lineno,
					'end_col_offset':node.end_col_offset,
					'seq_number' : seq,
					'ast':cop
					})
			self.mutants.append(muta)
		else:
			print(f'Skiping mutant {str(self)}')
			pass
		


	# def ajustar_col_offsets(self, node_raiz, linha_alvo, col_alvo, deslocamento):
	# 	for no in ast.walk(node_raiz):
	# 		if hasattr(no, 'lineno') and hasattr(no, 'col_offset'):
	# 			if no.lineno == linha_alvo and no.col_offset > col_alvo:
	# 				no.col_offset += deslocamento
	# 				# print(no, linha_alvo, col_alvo, no.lineno, no.col_offset)

		
	def go_visit(self):
		self.visit(self.original)

	def visit_FunctionDef(self, node):
		old_f = self.function
		old_l = self.func_lineno
		old_el = self.func_end_lineno
		self.function = node.name
		self.func_lineno = node.lineno
		self.func_end_lineno = node.end_lineno
		r = self.generic_visit(node)
		self.function = old_f
		self.func_end_lineno = old_el
		self.func_lineno = old_l
		return r

	def visit_Expr(self, node):
		if id(node) in self.docstrings:
			return node		
		return self.generic_visit(node)

	def __str__(self):
		s = str(type(self))
		return s [-6:-2].lower()
		

	def check_sintaxe(self,tree):
		unv = PrintVisit(tree)
		try:
			unv.go_visit()
			ast.parse(str(unv))
			return True
		except Exception as ex:
			print(unv)
			print(ex)
			return False

	
	def show_node(self, node):
		print('\n', node)
		if hasattr(node, 'lineno'):
			print(f'lineno: {node.lineno}')			
			print(f'end_lineno: {node.end_lineno}')
			print(f'col_offset: {node.col_offset}')	
			print(f'end_col_offset: {node.end_col_offset}')					

class MutantDict(dict):


	def __lt__(self, other):
		if self['operator'] < other['operator']:
			return True
		if self['operator'] > other['operator']:
			return False
		if self['lineno'] < other['lineno']:
			return True
		if self['lineno'] > other['lineno']:
			return False
		if self['col_offset'] < other['col_offset']:
			return True
		if self['col_offset'] > other['col_offset']:
			return False
		if self['seq_number'] < other['seq_number']:
			return True
		if self['seq_number'] > other['seq_number']:
			return False
		return False


# This class is used to set the parent of each node.
# Not all operators use this
# CCsr 
class ParentSetter(ast.NodeVisitor):
    def visit(self, node):
        # garante que todo nó tenha attrs (pai/campo/índice podem já ter sido definidos)
        if not hasattr(node, "parent"):
            node.parent = None
            node.parent_field = None
            node.parent_index = None
        super().visit(node)

    def generic_visit(self, node):
        for field, value in ast.iter_fields(node):
            if isinstance(value, ast.AST):
                value.parent = node
                value.parent_field = field
                value.parent_index = None
                self.visit(value)
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, ast.AST):
                        item.parent = node
                        item.parent_field = field
                        item.parent_index = i
                        self.visit(item)


