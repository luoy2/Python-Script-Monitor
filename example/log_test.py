import logging
import time

module_logger = logging.getLogger(__name__) # What do I have to enter here?
module_logger.setLevel(0)

def main():
    FORMAT = '%(asctime)s | %(name)s | %(module)s |  %(levelname)s: %(message)s'
    logging.basicConfig(level=0, format=FORMAT)
    while 1:
        logging.debug("this is a debugging message")
        time.sleep(1)
        logging.info("this is an informational message")
        time.sleep(1)
        logging.error("this is an error message")
        time.sleep(1)
        logging.warning("this is a warning message")
        time.sleep(1)
        logging.critical("this is a critical message")
        time.sleep(1)


if __name__ == '__main__':
    main()
