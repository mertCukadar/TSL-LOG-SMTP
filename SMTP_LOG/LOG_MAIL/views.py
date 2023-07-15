from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMessage
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
import time
import smtplib
from datetime import datetime
from email.mime.text import MIMEText




def send_mail(alarm_message):

    EMAIL = settings.EMAIL_HOST_USER
    PASSWORD = settings.EMAIL_HOST_PASSWORD

    with smtplib.SMTP(settings.EMAIL_HOST, 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login('<HOST  MAIL FROM', '<PASSWORD>')

        msg = MIMEText(alarm_message , 'plain' , 'utf-8')
        msg['Subject'] = "SICAKLIK TAKIP SISTEMI ALARM"
        msg['From'] = EMAIL
        msg['To'] =  "<TO MAIL>"
        
        smtp.sendmail(msg['From'], msg['To'], msg.as_string()) 






def alarm_log_name_collector():

    #postgres connction script

    conn = psycopg2.connect(
        database = settings.DATABASES['default']['NAME'],
        user = settings.DATABASES['default']['USER'],
        password = settings.DATABASES['default']['PASSWORD'],
        host = settings.DATABASES['default']['HOST'],
        port = settings.DATABASES['default']['PORT'],
    )

    cursor= conn.cursor(cursor_factory = RealDictCursor)

    try:
        cursor.execute("SELECT 1")
        conn.commit()
    except (psycopg2.OperationalError , psycopg2.InterfaceError):
        print("bağlantı kurulamadı") #send mail fonksiyonu ile değiştirilecek
    schema = "public"
    table = "alarms"       

    #aalm_table // bunu kullanıcaz

    query = sql.SQL("SELECT * FROM {}.{}").format(
        sql.Identifier(schema),
        sql.Identifier(table))

    cursor.execute(query)
    collected_log_vars = cursor.fetchall()
    
    #print(collected_log_vars)
    
    alarm_id_pair_dict = {}
    alarm_class_pair_dict = {}
    

    for var in collected_log_vars:
        alarm_id_pair_dict.update({var["alarm_id"]:var["alarm_name"]})
        alarm_class_pair_dict.update({var["alarm_id"]:var["alarm_class"]})
    
    # print(alarm_id_pair_dict)
    # print("===============================================")
    # print(alarm_class_pair_dict)
    return alarm_id_pair_dict , alarm_class_pair_dict

alarm_start = False
mail_send = False


def modify_number():
    global mail_send
    mail_send = not mail_send
    return  mail_send


def modify_alarm():
    global alarm_start
    alarm_start = not alarm_start

def alarm_detection():

    #postgres connction script

    conn = psycopg2.connect(
        database = settings.DATABASES['default']['NAME'],
        user = settings.DATABASES['default']['USER'],
        password = settings.DATABASES['default']['PASSWORD'],
        host = settings.DATABASES['default']['HOST'],
        port = settings.DATABASES['default']['PORT'],
    )

    cursor= conn.cursor(cursor_factory = RealDictCursor)

    try:
        cursor.execute("SELECT 1")
        conn.commit()
    except (psycopg2.OperationalError , psycopg2.InterfaceError):
        print("bağlantı kurulamadı") #send mail fonksiyonu ile değiştirilecek
    
    schema = "logs"
    table = "aalm_table"       
    

    query = sql.SQL("SELECT * FROM {}.{}").format(
        sql.Identifier(schema),
        sql.Identifier(table))

    cursor.execute(query)
    collected_log_vars = cursor.fetchall()
    
    
        
    
    if (len(collected_log_vars) != 0 and mail_send == False):
        modify_number()
        modify_alarm()

        alarm_name_dict , alarm_className_dict = alarm_log_name_collector()
        
        

        alarm_id = collected_log_vars[0]["alarm_id"]
        
        query_tag_id = sql.SQL(f"SELECT tag_id FROM  public.alarms where alarm_id = {alarm_id}")

        cursor.execute(query_tag_id)
        tag_id = cursor.fetchall()

        tag_id = tag_id[0]['tag_id']
        # print(alarm_id)
        # print(f"tag_id : {tag_id[0]['tag_id']}")

        query_val = sql.SQL(f"SELECT dataval FROM  logs.lct_table where tag_id = {tag_id}")
        cursor.execute(query_val)

        alarm_log_dataval = cursor.fetchall()
        alarm_log_dataval = str(alarm_log_dataval[0]["dataval"])

        alarms = []
        for log in collected_log_vars:
            currentDateTime = datetime.now()
            currentTime = currentDateTime.strftime("%H:%M:%S")
            alarm_id = log["alarm_id"]
            alarms.append("==================================="+
            "\n"+ "ALARM DURUMU:" + alarm_name_dict[alarm_id] + " --> " + alarm_log_dataval +
            "\n\n" +"ALARM KONUMU:" + alarm_className_dict[alarm_id] +
             "\n\n" + "ALARM SAATI:" + currentTime + "\n\n" +
              "===================================")

        message = ""
        for alarm in alarms:
            message += alarm 


        send_mail(message)
    



    elif (len(collected_log_vars) == 0):
        if(mail_send == True):
            modify_number()
    
   
     
  
    else:
        #print("unexpected condition...")
        pass

    alarms_end = []
    if (len(collected_log_vars) == 0 and alarm_start == True):
        modify_alarm()
        alarms_end.append("===================================" + "\n\n"
             + "TUM ALARMLAR TEMIZLENDI \n Sistem monitorunden kontol saglayın \n\n"
             + "===================================")
        alarm_end_msg = ""
        for alarm in alarms_end:
            alarm_end_msg += alarm
        
        send_mail(alarm_end_msg)
        
    #print(f"collected_log_vars : {len(collected_log_vars)} , mail send: {mail_send}")
    #print(f"alarm send : {alarm_start}")




def start_logger():
    while True:
        try:
            alarm_detection()
        except:
            pass




