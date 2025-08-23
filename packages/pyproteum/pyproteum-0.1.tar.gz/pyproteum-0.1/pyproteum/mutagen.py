import sys
from random import Random
import os
from pyproteum.models.models import *
import pickle
from peewee import IntegrityError
from pyproteum.moperators.myoperator import *
from pyproteum.moperators.oplist import operator_list

rd = Random()

def main():
	n = len(sys.argv)-2
	if n < 1:
		usage()
	
	if sys.argv[1] == '--create':
		__create()
		return
	else:
		usage()

def find_op(name):
	name = name.lower()
	l = []
	for r in operator_list:
		if r['name'].startswith(name):
			l.append(r['class'])
	if l == []:
		raise ValueError('Opertor not found.')
	return l

def __create():
	session_name = sys.argv[-1]
	directory = None
	i = 2
	ops = []
	percent = 100
	while i < len(sys.argv[:-2]):
		s = sys.argv[i]
		match s:
			case '--D':
				i += 1
				directory = sys.argv[i]
			case '--all':
				try:
					i += 1
					percent = int(sys.argv[i])
				except:
					usage()
					return			
			case '--seed':
				try:
					i += 1
					seed = int(sys.argv[i])
					rd.seed(seed)
				except:
					usage()
					return				
			case _:
				try:
					i += 1
					for r in  find_op(s[2:]):
						p = float(sys.argv[i]) 
						if p > 100: p = 100
						if p < 0 : p = 0
						ops.append((r,p))
				except:
					usage()
					return
		i += 1
	if ops == []:
		for r in operator_list:
			ops.append((r['class'],percent))

	muta_create(directory, session_name, ops)


def usage():
	print('Usage:')
	print('muta-gen --create [--D <directory> ] [(--<mutant op> |--all) <percentage>] [--seed <integer number>] <session name>')
	print('\t--<mutant operator> means the name of an operator or a preffix that matches one or many opertors ')
	print('\tFor instance "--s" matches all operators beginning with an "s", case insensitive.')
	print('\t--all means all operators')
	print('\t--seed stablishes the seed for mutant sampling. Using the same seed generates the same mutants.')
	sys.exit()
				
def muta_create(d, session_name, ops):
	try :
		if d:
			os.chdir(d)
		database = SqliteDatabase(session_name+'.db')
		db.initialize(database)  # aqui o proxy é vinculado ao banco real
		db.pragma('foreign_keys', 1, permanent=True)
	except Exception as ex:
		print('Error: test session not found')
		print(ex)
		sys.exit() 

	for reg_session in Session:
		mutants = apply_mutations(reg_session.filename, ops)
		print(f'Generated {len(mutants)} total mutants')
	   # print(mutants[-1])
		insert_db(mutants, reg_session)

def insert_db(muta, reg_session):
	ignore = None
	for m in muta:
		if m['operator'] == ignore:
			continue
		ignore = None
		try: 
			Mutant.create(
				source = reg_session,
				operator = m['operator'],
				function = m['function'],
				func_lineno = m['func_lineno'],
				func_end_lineno = m['func_end_lineno'],
				lineno = m['lineno'],
				col_offset = m['col_offset'],
				end_lineno = m['end_lineno'],
				end_col_offset = m['end_col_offset'],
				seq_number = m['seq_number'],
				ast = pickle.dumps(m['ast'])
			)
		except IntegrityError as ex:
			print(f'Can not insert mutants {m["operator"]}. They probably already are in the test session.')
			ignore = m['operator']
		except Exception as ex:
			print('Can not insert mutants.')
			print(type(ex), ex)
			return


def apply_mutations(filename, oper_list):

	try:
		with open(filename) as f:
			source = f.read()
	except Exception as ex:
		print('Error: Can´t read source file')
		print(ex)
		sys.exit()
	
	try:
		tree = ast.parse(source.replace('\t', '    '))
	except Exception as ex:
		print(f'Error in file {filename}. Check the errors')
		print(ex)
		sys.exit()

	mutants = []
	for op_class,percentage in oper_list:
		op = op_class(tree)
		print(f'Applying {str(op)}')
		op.go_visit()
		sampled = selecionar_percentual(op.mutants, percentage)
		print(f'Generated {len(sampled)} mutants for {str(op)}')
		mutants += sampled

	return mutants
		
def selecionar_percentual(lista, n):
	if n < 0: n = 0
	if n > 100: n = 100
	if lista == [] :
		return []
	quantidade = max(1, int(len(lista) * n / 100)) if n > 0 else 0
	return sorted(rd.sample(lista, quantidade))

if __name__ == '__main__' :
	main()




