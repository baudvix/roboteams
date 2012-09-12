def printer(arg1, arg2):
	print printer.func_code.co_varnames
	print a, b

if __name__ == '__main__':
	a = 5
	b = 6
	printer(a, b)