import webbrowser

import urllib3
url = 'https://drivetest.ca/dtbookingngapp/viewBookings'

# Open URL in a new tab, if a browser window is already open.
webbrowser.open_new_tab(url)

# Open URL in new window, raising the window if possible.
#webbrowser.open_new(url)

# c0626-04308-60515
#https://drivetest.ca/dtbookingngapp/viewBookings
# https://drivetest.ca/booking/v1/driver/email

# {
# "email":"angelocarlotto@gmail.com",
# "emailConfirm":"angelocarlotto@gmail.com",
# "licenceNumber":"C0626-04308-60515",
# "licenceExpiry":"2029/05/01"
# }

# https://drivetest.ca/booking/v1/licenceClass


# https://drivetest.ca/booking/v1/booking/18298?year=2024&month=9

# https://drivetest.ca/booking/v1/booking?date=2024-09-11&is=18298

# https://drivetest.ca/booking/v1/location


import base64
import requests

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import asyncio
def decrypt_aes_192_ecb(key, ciphertext):
  """Decrypts AES-192 ECB encrypted data.

  Args:
    key: The 192-bit encryption key as a byte string.
    ciphertext: The base64 encoded ciphertext.

  Returns:
    The decrypted plaintext as a byte string.
  """

  # Convert key and ciphertext to bytes
  key = key.encode('utf-8')
  ciphertext = base64.b64decode(ciphertext)

  # Create the cipher object
  cipher = Cipher(algorithms.AES(key), modes.ECB())
  decryptor = cipher.decryptor()

  # Decrypt the data
  plaintext = decryptor.update(ciphertext) + decryptor.finalize()

  return plaintext

# Example usage
key = "qHw7xyfsG62JMmwQYmtSuYdH"
ciphertext = "zr9U1veR/0IpM1i4IUo4tewJN4/s2g78Orf+l+XHDwepmsBOA0pMjuVClC0TTV2InERskuY6cH3QOmenxCebp2cpOFNal0vtEelROkn+xqGMOIsTy8BE3nZI4E2lj5hjtowLNgOG539tVdWZ4bxV+hldRzAEs6/yUzMirjgG3g1sy0GsDgk6gdImCOkBXiyLpMz2/03x0zCHwAtPgxwQv23dYeoF6h1wT9Yw7JasSDsgvzEOdbNoBWCBB/W/ox0KZBP76XcFox9nvBj1nqEW7FtBcBzir1aL9yoVxLkBRkiB2fG1VjwaivLGqW/pXvGmcnVSiOb+rhIp6HokEoL8gKW3zw2baGTEyCdy7FldwESLPuIflEmABlObXfIpGHzHG+d1sPqGY5ZhLmdlqFtShtIc9FAyas9yLAckyn6/vL5aEhfsRwghzoX2S98hum84Q9lH2pkfN90L7oqupzzwVYw4ixPLwETedkjgTaWPmGO2jAs2A4bnf21V1ZnhvFX6EpKXaBCbgmcpFic5BB2py2zLQawOCTqB0iYI6QFeLIukzPb/TfHTMIfAC0+DHBC/bFAEMzOggWTkqd6Vtq6rviC/MQ51s2gFYIEH9b+jHQrcF4VBpBR5A1RLr6skszTZMW/pY/6cU4fvk3bekg40IXmoueNXPuMw5uQ48Z1jdveeBZh7Uh97dyjwXSa3f5D9kEm69YnAL/mcjop6q6vzGlnZvhl3Lkv9co1J7VdejL+4YQIElSTDD2zKdSpUyLCK0s10H6Kvp/GgF6328Ul9dybXbtfS+kl4/Uz0LpuhByxZ54wZaq33nCkCVrhom2VYXHeh2kY3imhakmuA+Do5XFVpEfL/eS4XNlTO7i9+kHAfoJO2rGJLuF4Q85Tu/ctH/AtTJqYEddhH16NlxYxhZfkPj+FLKQg5B019Ean3GCPRGxbBvpQGXtc7+9sF4RedA01pFqLpIM1kYZ0BM0uc75k/B2jsIQIaOmmANsmTAuKuMCm29W09XGBSZqkVboCGZ+1qlhpGYINw1g6OTdT2QEX4HMIqiWidgUvgXazaE6ALwdaipNBPZOvGcSiGmROebMtBrA4JOoHSJgjpAV4si6TM9v9N8dMwh8ALT4McEL+vi5zMvghPe+AtXUfIuvlqRJqeffGzlDqUfApHhzge6S9pS1nOLUjNyCdjf2mCgSZTXpewdml/p4sB6LtCkGKqRzpVI23JQ3bIjLGkMUPSmcWiX0Vhm4JkuHyIOFeD/17tEwf9tI3BAC+JU0RO9Gcn/r/4yMDRly9LRn0Q17zfAC8hKoARsFKFFjdjFlQ9u7OtDaX3ASh0sz3trmGtn3+e0ydwMjryP7yzlrH00zAiRX7LUaKq+IiqssWXHiNv019b68qeJpJG6033OgaojRYeuka/UEx3sYQx6Age77HqxbKPzPu1exu9ewArdr3fwRlbQXAc4q9Wi/cqFcS5AUZIgdnxtVY8Goryxqlv6V7xpvckaLJzzl+aVuobP/QLUix5ET14B3+8JJMUsqt3asY0oOM7efBwZQEYJLE51afl82eiyVafb4VTMrhBti1CQf3TJ3AyOvI/vLOWsfTTMCJFfstRoqr4iKqyxZceI2/TXxLfXhHdecoMa1wmEq9lrM/ND4zyodmBB0OomunPRAN5cz4EjarUdnxEcFxHkAB1xUdEUwcm4I+y+y35LQxNVoOFLgMa8b9gUtqenrqE9eXoAcvMJ09IXI5xQcIsdqmW/u1MOgg6SXvar3fW07tD8b9sy0GsDgk6gdImCOkBXiyLpMz2/03x0zCHwAtPgxwQv2DcsWV5lGKhOQdc+MT6YINEmp598bOUOpR8CkeHOB7peAR1yfKtzNz5M4vteHUMMANNaRai6SDNZGGdATNLnO+ZPwdo7CECGjppgDbJkwLiem/GOpvg/gc1tTwKBExhY2ftapYaRmCDcNYOjk3U9kBMtIAFQ9e7rs/WkaMvsEfpLCkgjzGGhwXZ/sYUqSMpbg=="  # Replace with actual base64 encoded data

def  teste():

# Define the API endpoint URL
  url = "https://drivetest.ca/booking/v1/driver/email"

  # Create the data dictionary
  data = {
    "email": "angelocarlotto@gmail.com",
    "emailConfirm": "angelocarlotto@gmail.com",
    "licenceNumber": "C0626-04308-60515",
    "licenceExpiry": "2029/05/01"
  }

  # Send the POST request
  response = requests.post(url, json=data)

  # Check for successful response
  if response.status_code == 200:
    print("Request successful!")
    # Access the response content (if needed)
    # response_data = response.json()
    # print(response_data)
  else:
    print(f"Error: {response.status_code}")
    print(response.text)  # Print the error message from the response

teste()
decrypted_data = decrypt_aes_192_ecb(key, ciphertext)
print(decrypted_data)
