import tdxlib


def test_tdx_connection(cassette):
    tdx = tdxlib.tdx_ticket_integration.TDXTicketIntegration('tdxlib.ini')
    search = tdx.search_tickets("test")
