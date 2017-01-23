from lxml import etree
from ftplib import FTP
import StringIO
import boto3
import time


print('Loading function')


# aws sns publish --phone-number "+61413514357" --message-attributes '{"AWS.SNS.SMS.SenderID": {"DataType": "String", "StringValue": "weatherman"}}' --message "Test from cli"


def ftp_get(host, dir, file):
    print("Retrieving: ftp://" + host + dir + file)
    ftp = FTP(host)
    ftp.login()
    ftp.cwd(dir)
    outStr = StringIO.StringIO()
    ftp.retrlines('RETR ' + file, outStr.write)
    contents = outStr.getvalue()
    outStr.close()
    return contents


def get_precis_forecast():
    xml = ftp_get('ftp.bom.gov.au', '/anon/gen/fwo/', 'IDV10753.xml')
    tree = etree.fromstring(xml)
    
    xpath_expr = '//area[@aac="VIC_PT042"]/forecast-period[@index="0"]/element[@type="air_temperature_maximum"]'
    nodes = tree.xpath(xpath_expr)
    max_temp = nodes[0].text if nodes and len(nodes) > 0 else None
    
    xpath_expr = '//area[@aac="VIC_PT042"]/forecast-period[@index="0"]/text[@type="precis"]'
    nodes = tree.xpath(xpath_expr)
    short_forecast = nodes[0].text if nodes and len(nodes) > 0 else None
    
    return max_temp + " - " + short_forecast if max_temp else short_forecast


def get_city_forecast():
    xml = ftp_get('ftp.bom.gov.au', '/anon/gen/fwo/', 'IDV10751.xml')
    tree = etree.fromstring(xml)
    
    xpath_expr = '//area[@aac="VIC_ME001"]/forecast-period[@index="0"]/text[@type="forecast"]'
    nodes = tree.xpath(xpath_expr)
    detailed_forecast = nodes[0].text
    
    return detailed_forecast


def send_as_sms(message):
    client = boto3.client('sns')
    client.publish(
        PhoneNumber='+61413514357',
        Message=message,
        MessageAttributes={
            'AWS.SNS.SMS.SenderID': {
                'DataType': 'String',
                'StringValue': 'weatherman',
            }
        }
    )
    return


def lambda_handler(event, context):
    precis_forecast = get_precis_forecast()
    detailed_forecast = get_city_forecast()
    print precis_forecast
    print detailed_forecast
    send_as_sms(precis_forecast)
    time.sleep(1)
    send_as_sms(detailed_forecast)

    return


if __name__ == '__main__':
    lambda_handler(None, None)
