import asyncio
import logging

from aiohttp import ClientSession

from app.config import SETTINGS


async def analyze_toxicity(text: str) -> float:
    analyze_request = {
        'comment': {'text': text},
        'requestedAttributes': {'TOXICITY': {}},
        'languages': ['ru', 'en']
    }
    link = f'{SETTINGS.TOXICITY_ANALYZER.API_URL}?key={SETTINGS.TOXICITY_ANALYZER.API_KEY.get_secret_value()}'
    for attempts in range(5):
        try:
            async with ClientSession() as session:
                resp = await session.post(link, json=analyze_request)
                json = await resp.json()
                return json['attributeScores']['TOXICITY']['summaryScore']['value']
        except Exception as e:
            logging.error(f'Error with perspective api request: {e}', exc_info=True)
            await asyncio.sleep(1)
    raise Exception('Toxicity analization failed')
