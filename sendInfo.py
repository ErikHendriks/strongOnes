import datetime
import gnupg
import smtplib

conf = [line.strip('\n') for line in open('/etc/breakout/conf.v20')]

def sendEmail(text,subject):
    '''
    '''
    try:
        fingerprint = conf[3]
        password = conf[4]
        sender = conf[6]
        reciever = conf[5]
        gpg = gnupg.GPG(gnupghome='/etc/breakout/.gnupg')
        text = str(gpg.encrypt(text,fingerprint))
        mail = '''From: %s\nTo: %s\nSubject: %s\n\n%s
                ''' % (sender,reciever,subject,text)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender,password)
#       server.set_debuglevel(1)
        server.sendmail(sender, reciever, mail)
        server.quit()
    except Exception as e:
#       print(e)
        with open('/var/log/strongOnes.log', 'a') as LOG:
                LOG.write(str(datetime.datetime.now()) + ' sendEmail: {}\n'.format(e))
        pass

