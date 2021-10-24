'''Inform wichtlers about their wichtelpartner.'''
import random
import os
import sys
import time
import typing

from dotenv import load_dotenv

load_dotenv()

MAIL_TEMPLATE = '''Hallo {name},

schön, dass Du auch dieses Jahr an der Wichtelaktion zu Weihnachten teilnimmst! In
dieser Mail bekommst du Deinen Wichtelpartner / Deine Wichtelpartnerin zugeteilt.
Wie immer ist diese Information streng geheim, also bitte zeige diese Mail niemandem.
Das Budget für das Wichtelgeschenk sollte nicht mehr als 40€ betragen. Der
Übergabezeitpunkt und -ort ist wie immer einer der Weihnachtsfeiertagen bei den Frigges.

Dein Wichtelpartner / Deine Wichtelpartnerin lautet: {partner}.

Grüße und einen schönen Sonntag,
Timon (der Wichtelbeauftragte)

P.S.: Nicht über den Absendernamen wundern, das ist nur ein Testaccount von mir.'''

def build_addressbook(participants_path: str='participants.csv'):
    addressbook = {}

    with open(participants_path, 'r') as infile:
        for line in infile:
            name, address = line.replace('\n', '').split(',')
            addressbook[name] = address

    return addressbook

def send_mail(to_address: str,
              content: str,
              subject: str = 'Wichteln 2021',
              from_name: str = 'Der Wichtelbeauftragte'):
    import smtplib, ssl
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    message = MIMEMultipart()
    message['Subject'] = subject
    message['From'] = from_name
    message['To'] = to_address

    plain_text = MIMEText(content, _subtype='plain', _charset='UTF-8')
    message.attach(plain_text)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(os.getenv('GMAIL_SMTP'),
                          os.getenv('GMAIL_PORT'),
                          context=context) as server:
        server.login(os.getenv('GMAIL_ADDRESS'),
                     os.getenv('GMAIL_PASSWORD'))
        server.sendmail(os.getenv('GMAIL_ADDRESS'),
                        to_address,
                        message.as_string())

def assign_partner(names: typing.List[str]) -> typing.Dict[str, str]:
    '''Assignes a partner for each name in input list.'''
    partner_dict = {}
    remaining_partner = names.copy()

    removed = False

    for name in names:
        if name in remaining_partner:
            remaining_partner.remove(name)
            removed = True
        partner = random.choice(remaining_partner)
        partner_dict[name] = partner

        if removed:
            remaining_partner.append(name)
        remaining_partner.remove(partner)
        removed = False

    return partner_dict

if __name__=='__main__':
    addressbook = build_addressbook()
    print(f'Welcome to wichtler! We have {len(addressbook)} participants: '
          f'{sorted(addressbook.keys())}')

    if len(sys.argv) == 2:
        seed = sys.argv[-1]
        random.seed(sys.argv[-1])
        print(f'Running partner assignment with seed: {seed}.')
    else:
        print(f'No seed set. Using random seed instead.')

    try:
        partner_dict = assign_partner(list(addressbook.keys()))
    except IndexError:
        print('Did not converge. Please try another seed!')
        sys.exit()

    debug = input('Do you want to send mails? If not, run in debug mode and'
                  ' and print results. [yes/no]\n') != 'yes'

    for name, partner in partner_dict.items():
        address = addressbook[name]
        content = MAIL_TEMPLATE.format(name=name,
                                       partner=partner)

        if debug:
            print(f'{name} ({address}) has the wichtelpartner {partner}.')
        else:
            send_mail(to_address=address,
                    content=content)
            print(f'Send mail to {address}.')
            time.sleep(1)
