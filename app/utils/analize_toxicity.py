from curl_cffi import AsyncSession

from app.config import SETTINGS


async def analize_toxicity(text: str) -> float:
    async with AsyncSession(impersonate='chrome110') as s:
        analyze_request = {
            'comment': {'text': text},
            'requestedAttributes': {'TOXICITY': {}},
            'languages': ['ru', 'en']
        }
        link = f'{SETTINGS.TOXICITY_ANALYZER.API_URL}?key={SETTINGS.TOXICITY_ANALYZER.API_KEY.get_secret_value()}'
        resp = await s.post(link, json=analyze_request)
        return resp.json()['attributeScores']['TOXICITY']['summaryScore']['value']
