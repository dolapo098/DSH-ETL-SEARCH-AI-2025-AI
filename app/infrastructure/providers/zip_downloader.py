import urllib.request


class ZipDownloader:
    def download(self, url: str) -> bytes:

        with urllib.request.urlopen(url) as response:
            
            return response.read()

