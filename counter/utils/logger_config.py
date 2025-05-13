import logging

# Create a logger
app_logger = logging.getLogger(__name__)
app_logger.setLevel(logging.DEBUG)

# Create a file handler
file_handler = logging.FileHandler('webapp.log')
file_handler.setLevel(logging.DEBUG)

# Create a formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add the file handler to the logger
app_logger.addHandler(file_handler)