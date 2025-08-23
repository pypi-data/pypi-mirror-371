from bi_sc_client.client import BISomConnexioClient
from bi_sc_client.resources.token import Token


class InvoicePDFRegenerator:
    def __init__(self, invoice_numbers):
        self.path = "/apidata/invoices_oc_regenerate_pdf/"
        self.client = BISomConnexioClient()
        self.headers = {"Authorization": Token(self.client).token}
        self.params = invoice_numbers

    def run(self):
        self.client.send_request("PUT", self.path, self.params, self.headers)
