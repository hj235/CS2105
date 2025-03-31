import sys
import logging
logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)
logger.info('Starting test.py...')
logger.debug('Debugging test.py...')
logger.warning('Warning in test.py...')
logger.error('Error in test.py...')
print(f'Hello World! {sys.argv}')