import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
import smtplib
from email.message import EmailMessage
import schedule
import json

remetente = ''
destinatario = ''
email_password = ''

def enviar_email(remetente,destinatario,email_password,mensagem):
    print('Enviando email ...')
    # Configurações de login
    EMAIL_ADDRESS = remetente
    EMAIL_PASSWORD = email_password

    # Criar e enviar um email
    mail = EmailMessage()
    mail['Subject'] = 'Previsão do Tempo'
    mail['From'] = EMAIL_ADDRESS
    mail['To'] = destinatario
    mail.add_header('Content-Type','text/html')
    mail.set_payload(mensagem.encode('utf-8'))

    # Enviar o email
    with smtplib.SMTP_SSL('smtp.gmail.com',465) as email:
        email.login(EMAIL_ADDRESS,EMAIL_PASSWORD)
        email.send_message(mail)
    print('Email enviado !!')

def main():
    driver = uc.Chrome()
    driver.get("https://www.google.com/search?q=previsao+do+tempo")
    sleep(5)
    btns = driver.find_elements(By.TAG_NAME,'g-raised-button')
    sleep(3)
    btns[1].click()
    sleep(3)

    div_temp_semana = driver.find_element(By.ID,'wob_dp')
    div_dias_semana = div_temp_semana.find_elements(By.CLASS_NAME,'wob_df')[:4]
    lista_info_temp = []
    
    for div_dia in div_dias_semana:
        dia = div_dia.find_elements(By.TAG_NAME,'div')[0].text
        temperaturas = []
        spans = div_dia.find_elements(By.TAG_NAME,'span')
        for span in spans:
            if span.get_attribute('style') =='display: inline;':
                temperaturas.append(span.text)
        condicao_tempo = div_dia.find_element(By.TAG_NAME,'img').get_attribute('alt')
        lista_info_temp.append([dia,temperaturas,condicao_tempo])
        

    dados_dict = [{"dia": dia, "temperaturas": temperaturas, "condicao_tempo": condicao_tempo} for dia, temperaturas, condicao_tempo in lista_info_temp]
    dados_json = json.dumps(dados_dict, indent=4)
    with open('dados_meteorologicos.json', 'w') as arquivo_json:
        arquivo_json.write(dados_json)
        
    mensagem = '''
    <!DOCTYPE html>
    <html lang="pt-br">
          <head>
                <meta charset="utf-8">
          </head>
          <body>

    '''
    
    for pos,info in enumerate(lista_info_temp):
        
        if pos == 0:

            temperatura_atual = driver.find_element(By.ID,'wob_tm').text
            
            mensagem += f'''
                <h2>Tempo Hoje:</h2>
                <p>Dia: {info[0]}</p>
                <p>Temperatura Atual: {temperatura_atual} ºC</p>
                <p>Condição do tempo: {info[2]}</p>

                <h2>Previsão para os próximos 3 dias:</h2>
    '''
        else:

             mensagem +=f'''
                <hr>
                <p>Dia: {info[0]}</p>
                <p>Min: {info[1][1]} ºC - Máx: {info[1][0]} ºC</p>
                <p>Condição do tempo: {info[2]}</p>
                <hr>

    '''

    mensagem +='''
            </body>
    </html>

    '''

    enviar_email(remetente,destinatario,email_password,mensagem)

    driver.close()
    driver.quit()
    
schedule.every(1).days.at('08:00').do(main)

while True:
    schedule.run_pending()
    sleep(2)
