import urllib.request
import urllib.parse
import urllib.error

# Install a custom handler to prevent following redirects automatically
class SmartRedirectHandler(urllib.request.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        return headers

opener = urllib.request.build_opener(SmartRedirectHandler())
urllib.request.install_opener(opener)

# Prepare the parameters for the POST request
parameters = {
    'seqdb': 'pdb',
    'seq': '>Seq\nKLRVLGYHNGEWCEAQTKNGQGWVPSNYITPVNSLENSIDKHSWYHGPVSRNAAEY'
}
enc_params = urllib.parse.urlencode(parameters).encode('utf-8')

# Send the search request to the server
request = urllib.request.Request('https://www.ebi.ac.uk/Tools/hmmer/search/phmmer', data=enc_params)
response = urllib.request.urlopen(request)

# Get the URL where the results can be fetched from
results_url = response.getheader('Location')

# Modify the range, format, and presence of alignments in your results here
res_params = {
    'output': 'json',
    'range': '1,10'
}

# Add the parameters to your request for the results
enc_res_params = urllib.parse.urlencode(res_params)
modified_res_url = results_url + '?' + enc_res_params

# Send a GET request to fetch the results
results_request = urllib.request.Request(modified_res_url)
with urllib.request.urlopen(results_request) as data:
    # Print out the results
    print(data.read().decode('utf-8'))
