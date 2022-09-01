import os
import time

from celery import Celery
from celery.utils.log import get_task_logger
import re

from .scrapers.amazon.scrape_reviews import scrape_reviews

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
# celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "db+sqlite:///celery.db")

logger = get_task_logger(__name__)

@celery.task(name="create_task")
def create_task(task_type):
    time.sleep(int(task_type) * 10)
    return True


@celery.task(name="scrape_amazon")
def scrape_amazon(links):
    task_id = scrape_amazon.request.id
    logger.info(f"task_id = {task_id}")
    rule_asin = r'dp/(?P<asin>\w{10})'

    logger.info(links)

    asins = [match.group('asin') for match in re.finditer(rule_asin, links)]
    
    # Scrape the pages and save them locally
    scrape_reviews(asins)
    
    # Parse them out and generates an output file
    # generate_file(asins, task_id)

    time.sleep(10)
    return True