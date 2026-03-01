import json
from pathlib import Path

summaries_path = Path(__file__).parent.parent.parent / 'data' / 'summaries.json'
with summaries_path.open("r", encoding='utf-8') as f:
    summaries = json.load(f)

summaries['none'] = 'Usa esta clasificacion para las preguntas que no tengan que ver con el contenido del informe de mercado de jovenes'

__all__ = ['summaries']
