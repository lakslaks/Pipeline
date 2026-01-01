"""
04_api_interaction.py
Demonstrates calling an external API using requests (must be installed).
"""

from my_pipeline.executor import PipelineExecutor
import asyncio
import requests

def fetch_activity():
    return requests.get("https://www.boredapi.com/api/activity").json()["activity"]

class MyAPIs:
    @staticmethod
    def fetch_activity():
        return fetch_activity()

steps = [
    {"name": "call_api", "action": "self#fetch_activity", "publish": "activity"},
    {"name": "print_activity", "action": "builtins#print", "args": ["${activity}"]}
]

executor = PipelineExecutor(name="api-example", steps=steps, custom_objects={"self": MyAPIs()})
asyncio.run(executor.execute())
