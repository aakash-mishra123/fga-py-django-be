from collections import OrderedDict
import requests
import xml.etree.ElementTree as ET
import os
import urllib3
import requests


urllib3.disable_warnings()
def send_over_post(url, xml):
    headers = {
        'Content-Type': 'application/xml',
    }

    ca_file = os.path.abspath('fidelity/SSL/ca.pem')
    cert_file = os.path.abspath('fidelity/SSL/cert.pem')
    key_file = os.path.abspath('fidelity/SSL/key.pem')
    try:
        response = requests.post(
            url,
            headers=headers,
            data=xml,
            cert=(cert_file, key_file),
            verify=ca_file,
        )

        # Check for HTTP request errors
        response.raise_for_status()

        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

# # Example usage
# url = 'https://example.com/api'
# xml_data = '<xml>...</xml>'
# result = send_over_post(url, xml_data)

# if result:
#     print(result)
# else:
#     print("Request failed.")



def get_order_status(operation, language, merchant, order_id, session_id):
    # Create an XML request
    root = ET.Element('TKKPG')
    request = ET.SubElement(root, 'Request')

    operation_element = ET.SubElement(request, 'Operation')
    operation_element.text = operation

    language_element = ET.SubElement(request, 'Language')
    language_element.text = language

    order = ET.SubElement(request, 'Order')

    merchant_element = ET.SubElement(order, 'Merchant')
    merchant_element.text = merchant

    order_id_element = ET.SubElement(order, 'OrderID')
    order_id_element.text = order_id

    session_id_element = ET.SubElement(request, 'SessionID')
    session_id_element.text = session_id

    xml_data = ET.tostring(root, encoding='UTF-8', method='xml')

    # Send the XML request
    # url_req = "https://acs2test.quipugmbh.com:6443/Exec"
    url_req = "https://mpi.quipugmbh.com:6443/Exec"  # Live URL

    order_status = send_over_post(url_req, xml_data)

    return order_status


def stop_auto_recur(operation, language, merchant, order_id, session_id):
    # Create an XML request
    root = ET.Element('TKKPG')
    request = ET.SubElement(root, 'Request')

    operation_element = ET.SubElement(request, 'Operation')
    operation_element.text = operation

    language_element = ET.SubElement(request, 'Language')
    language_element.text = language

    order = ET.SubElement(request, 'Order')

    merchant_element = ET.SubElement(order, 'Merchant')
    merchant_element.text = merchant

    order_id_element = ET.SubElement(order, 'OrderID')
    order_id_element.text = order_id

    session_id_element = ET.SubElement(request, 'SessionID')
    session_id_element.text = session_id

    xml_data = ET.tostring(root, encoding='UTF-8', method='xml')

    # Send the XML request
    # url_req = "https://acs2test.quipugmbh.com:6443/Exec"
    url_req = "https://mpi.quipugmbh.com:6443/Exec"  # Live URL

    auto_recur_status = send_over_post(url_req, xml_data)

    return auto_recur_status





def create_recur_payment(
    operation, language, merchant, amount, currency, description,
    approve_url, cancel_url, decline_url, recur_frequency, recur_end_recur,
    recur_period, recur_remove_on_decline, order_type
):
    # Create an XML request
    root = ET.Element('TKKPG')
    request = ET.SubElement(root, 'Request')

    operation_element = ET.SubElement(request, 'Operation')
    operation_element.text = operation

    language_element = ET.SubElement(request, 'Language')
    language_element.text = language

    order = ET.SubElement(request, 'Order')

    merchant_element = ET.SubElement(order, 'Merchant')
    merchant_element.text = merchant

    amount_element = ET.SubElement(order, 'Amount')
    amount_element.text = amount

    currency_element = ET.SubElement(order, 'Currency')
    currency_element.text = currency

    description_element = ET.SubElement(order, 'Description')
    description_element.text = description

    approve_url_element = ET.SubElement(order, 'ApproveURL')
    approve_url_element.text = approve_url

    cancel_url_element = ET.SubElement(order, 'CancelURL')
    cancel_url_element.text = cancel_url

    decline_url_element = ET.SubElement(order, 'DeclineURL')
    decline_url_element.text = decline_url

    order_type_element = ET.SubElement(order, 'OrderType')
    order_type_element.text = order_type

    add_params = ET.SubElement(order, 'AddParams')

    purchase_recur_frequency = ET.SubElement(add_params, 'Purchase.Recur.frequency')
    purchase_recur_frequency.text = recur_frequency

    purchase_recur_end_recur = ET.SubElement(add_params, 'Purchase.Recur.endRecur')
    purchase_recur_end_recur.text = recur_end_recur

    purchase_recur_period = ET.SubElement(add_params, 'Purchase.Recur.period')
    purchase_recur_period.text = recur_period

    purchase_recur_remove_on_decline = ET.SubElement(add_params, 'Purchase.Recur.removeOnDecline')
    purchase_recur_remove_on_decline.text = recur_remove_on_decline

    xml_data = ET.tostring(root, encoding='UTF-8', method='xml')

    # Send the XML request
    # url_req = "https://acs2test.quipugmbh.com:6443/Exec"
    url_req = "https://mpi.quipugmbh.com:6443/Exec"  # Live URL

    result = send_over_post(url_req, xml_data)

    # Parse XML response
    xml_res = ET.fromstring(result)
    order_id = xml_res.find('98989').text
    session_id = xml_res.find('.//SessionID').text
    url = xml_res.find('.//URL').text

    # Generate URL to redirect browser
    redirect = f"{url}?ORDERID={order_id}&SESSIONID={session_id}"

    return redirect


def create_order(operation, language, merchant, amount, currency, description, approve_url, cancel_url, decline_url,
                 order_type, email, phone, shipping_country, shipping_city, delivery_period, merchant_ext_id,
                 shipping_state, shipping_zip_code, shipping_address):
    # Create an XML request
    root = ET.Element('TKKPG')
    print(root,"**********root*********")
    request = ET.SubElement(root, 'Request')
    print(request,'**************request****************')

    operation_element = ET.SubElement(request, 'Operation')
    operation_element.text = operation
    print(operation_element,"**************Operation****************")

    language_element = ET.SubElement(request, 'Language')
    language_element.text = language
    print(language_element,"**************Language****************")

    order = ET.SubElement(request, 'Order')
    print(order,"************order******************")

    merchant_element = ET.SubElement(order, 'Merchant')
    merchant_element.text = merchant
    print(merchant_element,"********************Merchant******************")


    amount_element = ET.SubElement(order, 'Amount')
    amount_element.text = str(amount)
    print(amount_element,"********************Amount******************")


    currency_element = ET.SubElement(order, 'Currency')
    currency_element.text = currency
    print(currency_element,"********************Currency******************")


    description_element = ET.SubElement(order, 'Description')
    description_element.text = description
    print(description_element,"********************Description******************")


    approve_url_element = ET.SubElement(order, 'ApproveURL')
    approve_url_element.text = approve_url
    print(approve_url_element,"********************ApproveURL******************")


    cancel_url_element = ET.SubElement(order, 'CancelURL')
    cancel_url_element.text = cancel_url
    print(cancel_url_element,"********************CancelURL******************")


    decline_url_element = ET.SubElement(order, 'DeclineURL')
    decline_url_element.text = decline_url
    print(decline_url_element,"********************DeclineURL******************")

    order_type_element = ET.SubElement(order, 'OrderType')
    order_type_element.text = order_type
    print(order_type_element,"********************OrderType******************")


    add_params_element = ET.SubElement(order, 'AddParams')
    print(add_params_element,"********************AddParams******************")

    fa_data_element = ET.SubElement(add_params_element, 'FA-DATA')
    print(fa_data_element,"********************FA-DATA******************")

    fa_data_element.text = (
        f'Email={email}; Phone={phone}; ShippingCountry={shipping_country}; '
        f'ShippingCity={shipping_city}; DeliveryPeriod={delivery_period}; '
        f'MerchantOrderID={merchant_ext_id}; ShippingState={shipping_state}; '
        f'ShippingZipCode={shipping_zip_code}; ShippingAddress={shipping_address};'
    )
    print(fa_data_element.text,"********fa_data_element.text********")

    xml_data = ET.tostring(root, encoding='UTF-8', method='xml')

    # Send the XML request
    # url_req = "https://acs2test.quipugmbh.com:6443/Exec"
    url_req = "https://mpi.quipugmbh.com:6443/Exec"  # Live URL

    print(url_req,'rawat')


    response = send_over_post(url_req, xml_data)
    print(response,'monika123')
    # Parse the XML response
    xml_res = ET.fromstring(response)

    order_id = xml_res.find('.//OrderID').text
    print(order_id)
    session_id = xml_res.find('.//SessionID').text
    url = xml_res.find('.//URL').text

    # Generate a URL to redirect the browser
    redirect = f'{url}?ORDERID={order_id}&SESSIONID={session_id}'

    # Redirect the user to the generated URL
    return redirect