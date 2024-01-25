cookies = "OptanonAlertBoxClosed=2024-01-25T08:51:43.845Z; OptanonConsent=isGpcEnabled=1&datestamp=Thu+Jan+25+2024+17%3A59%3A24+GMT%2B0800+(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&version=202306.2.0&browserGpcFlag=1&isIABGlobal=false&hosts=&consentId=a8bcbdfe-e331-4706-8a05-19820c35c528&interactionCount=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0003%3A1%2CSPD_BG%3A0%2CC0002%3A0%2CC0004%3A0&geolocation=US%3BCA&AwaitingReconsent=false"

d = list()

for nv in cookies.split(";"):
    n, v = nv.split("=", maxsplit=1)

    d.append({"name": n, "value": v})
print(d)
