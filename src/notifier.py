import requests
import json

TIPO_SLA = ""

def enviar_mensagem_slack(mensagem):
    #Variável que define o tipo de dados que estamos enviando. E que envie a solicitação e poste está mensagem
    payload = '{"text":"%s"}' % mensagem
    
    # Variável que irá obter reposta que iremos receber da API. Logo depois do sinal de igual tem a chamada da bilioteca de solicitaçao. 
    # E também o link do bot criado para o envio de mensagens
    requests.post('https://hooks.slack.com/services/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', data=payload)

def create_issue():
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
            "summary": "Uso de {} acima de 95%".format(TIPO_SLA),
            "description": "Está máquina está atingindo elevados níveis de uso de {}. Por favor verifique o que está causando este alto consumo de hardware.".format(TIPO_SLA),
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
