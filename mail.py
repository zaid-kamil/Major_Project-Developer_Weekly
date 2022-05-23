import smtplib, ssl

server = smtplib.SMTP_SSL('smtp.gmail.com',465)
server.login('dev.weekly2022@gmail.com', 'dev5404Weekly')
print("LOGIN SUC")