class OrgNameAndEndpointSet(Exception):
    def __init__(self):
        super().__init__(
            "'Organization Name' and 'endpoint' cannot both be set.")


class OrgNameAndEndpointNotSet(Exception):
    def __init__(self):
        super().__init__(
            "You must set either 'Organization Name' or 'endpoint'.")
