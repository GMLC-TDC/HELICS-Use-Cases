import sys
import linecache
import six

def PrintException():
	exc_type, exc_obj, tb = sys.exc_info()
	f = tb.tb_frame
	lineno = tb.tb_lineno
	filename = f.f_code.co_filename
	linecache.checkcache(filename)
	line = linecache.getline(filename, lineno, f.f_globals)
	six.print_("Exception in Line {}".format(lineno))
	six.print_("Error in Code: {}".format(line.strip()))
	six.print_("Error Reason: {}".format(exc_obj))
