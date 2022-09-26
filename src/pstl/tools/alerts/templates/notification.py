import requests


requests.post('https://api.mynotifier.app', {
    "apiKey": '****-*****-*****',
    "message": "Our first notification!",
    "description": "This is cool",
    "type": "info", # info, error, warning or success
    })
