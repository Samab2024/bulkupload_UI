import string, csv

charwhitelist = dict()
# charwhitelist = dict(email_address=string.ascii_letters + string.digits + "'-_.@", custom_id = string.ascii_letters + string.digits + "'-_.@", app_id=string.digits, first_name=string.ascii_letters+string.digits+' -_,\'', last_name=string.ascii_letters+string.digits+' -_,\'', teams = string.ascii_letters + string.digits + "'-_.@")

class csvIn:
	def __init__(self, source):
		self.READER = csv.reader( source )
		self.header = next(self.READER)

	@classmethod
	def fromFile(cls, filename = None):
		if filename == None: filename = input('Location of CSV File: ')
		return cls( open(filename, "rt") )

	@classmethod
	def fromStream(cls, filename):
		return cls( filename )

	def __iter__(self):
		return self

	def next(self):
		try:
			lineinfo = self.pullRow(self.header, next(self.READER))
		except StopIteration:
			return False
		else:
			lineinfo['rownum'] = self.READER.line_num
			return lineinfo

	def pullRow(self, header, row):
		colnum = 0
		lineinfo = {}
		for col in row:
			if (header[colnum] != '') and (col != ''):
				filtered_col = self.inputFilter(header[colnum], col)
				if filtered_col != '': lineinfo[header[colnum]] = filtered_col.strip()
			colnum += 1
		return lineinfo

	def inputFilter(self, field, value):
		if field == 'file': value = '@' + value
		# elif field in charwhitelist: value = filter(lambda x: x in charwhitelist[field], value)
		return value