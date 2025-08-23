from bi_sc_client.client import BISomConnexioClient
from bi_sc_client.resources.token import Token


class NotifyInvoiceNumber:
    def __init__(self, invoice_number):
        self.invoice_number = invoice_number
        self.path = "/apidata/invoices_oc_generate_pdf/"
        self.client = BISomConnexioClient()
        self.headers = {"Authorization": Token(self.client).token}
        self.params = {"invoice": self.invoice_number}

    def run(self):
        self.client.send_request("GET", self.path, self.params, self.headers)
