#"""RF Analysis Engine
#
#This application is the server for the RF-Metadata-Displayer application.
#It contains a simple search api endpoint that the displayer app uses to query the database and get the results.
#
#Subpackages:
#    rest_api (rfserver.rest_api): Rest API endpoints and utilities.
#    db (rfserver.db): Database modules and connections.
#
#Attributes:
#    __version__ (str): Current version of the application.
#"""

__version__ = "1.0.0"   

__all__ = (
    "__version__",
    "main",
)
