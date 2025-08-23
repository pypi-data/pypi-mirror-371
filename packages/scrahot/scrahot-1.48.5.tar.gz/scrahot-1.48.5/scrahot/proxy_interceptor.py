from mitmproxy import http


def request(flow: http.HTTPFlow) -> None:
    print("proxy:", flow.request.pretty_url)
    # List of headers to remove
    headers_to_remove = [
        'Selenium',
        'selenium',
        'Sec-Ch-Device-Memory',
        'Sec-Ch-Ua-Arch',
        'Sec-Ch-Ua-Model',
        'Sec-Ch-Ua-Full-Version-List'
    ]

    # Remove unwanted headers
    for header in headers_to_remove:
        flow.request.headers.pop(header.lower(), None)

    # Define custom headers to add
    custom_headers = {
        'Sec-Ch-Ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Linux"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        # Add other custom headers as needed
    }

    # Add custom headers to the request
    for header_name, header_value in custom_headers.items():
        flow.request.headers[header_name] = header_value
