import logging, os, sys

def Logger(filename = 'logs'):
	logging.root.handlers = []
	logging.getLogger("requests").setLevel(logging.WARNING)
	logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s] %(message)s")
	logger = logging.getLogger()
	logger.setLevel(logging.INFO)

	fileHandler = logging.FileHandler("{0}/{1}.log".format(os.getcwd(), filename))
	fileHandler.setFormatter(logFormatter)
	logger.addHandler(fileHandler)

	consoleHandler = logging.StreamHandler(sys.stdout)
	consoleHandler.setFormatter(logFormatter)
	logger.addHandler(consoleHandler)
	return logger