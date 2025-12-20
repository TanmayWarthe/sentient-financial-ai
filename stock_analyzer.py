import logging
import configparser

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
config = configparser.ConfigParser()
config.read('config.ini')
log_level = config.get('DEFAULT', 'log_level', fallback='INFO')
logger.setLevel(log_level)
logger = logging.getLogger(__name__)

logger.info("Mera stock analyzer")
def main() -> None:
	"""Simple CLI for stock analyzer demo."""
	try:
		name: str = input("Apna naam batao: ")
		logger.info(f"Hello {name}! Yeh mera pehla stock analyzer hai!")
	except Exception as e:
		logger.error(f"Input error: {e}")
		print("Input error. Please try again.")

if __name__ == "__main__":
	main()