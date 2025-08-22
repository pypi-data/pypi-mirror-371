from typing import List, Union


class ProbelyException(Exception):
    pass


class ProbelyRequestFailed(ProbelyException):
    """General exception for non successful api calls"""

    def __init__(self, reason, *args, **kwargs):
        super().__init__(reason, *args)
        self.reason = reason


class ProbelyObjectsNotFound(ProbelyException):
    def __init__(self, ids: Union[str, List[str]], *args, **kwargs):
        if isinstance(ids, str):
            ids = [ids]

        ids_str = "', '".join(ids)
        super().__init__("objects not found: '{}'".format(ids_str), *args)

        self.not_found_object_ids: List[str] = ids


class ProbelyBadRequest(ProbelyException):
    def __init__(self, response_payload, *args, **kwargs):
        super().__init__("probely API validation: {}".format(response_payload), *args)
        self.response_payload = response_payload


class ProbelyRequestNoResultsException(ProbelyException):
    pass


class ProbelyMissConfig(ProbelyException):
    pass


class ProbelyValidation(ProbelyException):
    pass


class ProbelyCLIValidation(ProbelyException):
    pass


class ProbelyCLIValidationFiltersAndIDsMutuallyExclusive(ProbelyException):
    def __init__(self, *args):
        super().__init__("filters and identifiers are mutually exclusive", *args)


class ProbelyCLIFiltersNoResultsException(ProbelyCLIValidation):
    def __init__(self, *args):
        super().__init__("selected Filters return no results", *args)


class ProbelyApiUnavailable(ProbelyException):
    def __init__(self, *args, **kwargs):
        super().__init__("API is unavailable. Contact support.", *args)
