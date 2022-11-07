import requests
import json

url = "https://safe-commercefr.atlassian.net/rest/api/2/issue"

headers={
    "Accept": "application/json",
    "Content-Type": "application/json"
}
payload=json.dumps(
    {
    "fields": {
        "project":
        {
            "key": "SAF"
        },
        "summary": "Uso de CPU acima de 95%",
        "description": "A CPU desta maquina atingiu niveis elevados de uso, recomendamos fazer verificar o que está causando está lentidão.",
        "issuetype": {
            "name": "Task"
        }
    }
}
)
response=requests.post(
    url,
    data=payload,
    headers=headers,
    auth=("pedrogustavofr000@gmail.com", "9Wi7zK0W9W4ZrUCZiN4QB4F6")
)

print(response.text)
