import requests

from xpath_blindeye.config import PARAMETERS, INJECTION_FORMAT, URL, SUCCESS, INJECT_PARAMETER_NAME, HTTP_MODE


def request(query: str):
    inject_value = PARAMETERS.get(INJECT_PARAMETER_NAME)
    inject_value = inject_value.format(inject=INJECTION_FORMAT.format(query))
    params = PARAMETERS.copy()
    params[INJECT_PARAMETER_NAME] = inject_value

    # TODO - Retry on request failure 
    if HTTP_MODE == "POST":
        resp = requests.post(URL, data=params)
    else:
        resp = requests.get(URL, params=params)
    resp.raise_for_status()
    return SUCCESS in resp.text
