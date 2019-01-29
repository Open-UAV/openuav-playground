

class NoContainerExc(Exception):
    """If the container is not running"""

class ContainerInformationFetchExc(Exception):
	"""If the server is unable to fetch the data from the simulation container"""

class NoUserIDExc(Exception):
    """If the User id is not present in the request"""

class InvalidIPExc(Exception):
	"""The IP format is incorrect"""