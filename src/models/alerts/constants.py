__author__ = 'Geert Dobbels'



COLLECTION = "alerts"
URL = os.environ.get('MAILGUN_URL')
API_KEY = os.environ.get('MAILGUN_API_KEY')
FROM = os.environ.get('MAILGUN_FROM')

ALERT_TIMEOUT=10