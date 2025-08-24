import ast
from pyproteum.moperators.myoperator import *



class Ssdl(MyOperator):
	
	
	def __init__(self, original):
		super().__init__(original)


	def generic_visit(self, node):		
		for _, value in ast.iter_fields(node):
			if isinstance(value, list):
				for k, item in enumerate(value):
					if id(item) in self.docstrings:
						self.visit(item)							
					elif self._is_command(item):
						pass_node = ast.Pass()
						ast.copy_location(pass_node, item)
						value[k] = pass_node
						# self.show_node(pass_node)
						# self.show_node(item)
						self.salva_muta(pass_node, self.function, self.func_lineno, self.func_end_lineno)
						value[k] = item

					self.visit(item)


			elif isinstance(value, ast.AST):
				self.visit(value)
		return node

	def _is_command(self, node):
		return isinstance(node, (
			ast.If, ast.For, ast.AsyncFor, ast.While, ast.With, ast.Try,
			ast.Assign, ast.AugAssign, ast.Expr, ast.AsyncWith,
			ast.Return, ast.Raise, ast.Assert, ast.Delete, ast.Nonlocal,
			ast.Break, ast.Continue, ast.Match, ast.AnnAssign, ast.Global
		))