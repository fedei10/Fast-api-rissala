from email.message import EmailMessage
import ssl
import smtplib

def send_mail(email_reciver,title,img,content,id):
    subject = 'Check out'
    email_sender = "aakrout25@gmail.com"
    email_password = "sxyp rtsy qmyd moiu"
    html_body = f"""
        <html>
        <head>
        <style>
        .btn {{
            display: inline-block;
            font-weight: 400;
            color: #212529;
            text-align: center;
            vertical-align: middle;
            -webkit-user-select: none;
            -moz-user-select: none;
            -ms-user-select: none;
            user-select: none;
            background-color: transparent;
            border: 1px solid transparent;
            padding: .375rem .75rem;
            font-size: 1rem;
            line-height: 1.5;
            border-radius: .25rem;
            transition: color .15s ease-in-out, background-color .15s ease-in-out, border-color .15s ease-in-out, box-shadow .15s ease-in-out;
            text-decoration: none;
        }}

        /* Primary button styles */
        .btn-primary {{
            color: #fff;
            background-color: #007bff;
            border-color: #007bff;
        }}

        .btn-primary:hover {{
            color: #fff;
            background-color: #0069d9;
            border-color: #0062cc;
        }}
        </style>
        </head>
        <body>
            <div class="container">
                <div class="row">
                    <div class="col">
                        <h1 style="color:red">{title}</h1>
                        <p>{content}</p>
                        <img src="{img}">
                        <a href="{id}" class="btn btn-primary">Read now</a>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_reciver
    em['Subject'] = subject
    em.add_alternative(html_body, subtype='html')

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_reciver, em.as_string())