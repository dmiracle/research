from zeep import Client

if __name__ == "__main__":
    client = Client("http://localhost:8000/?wsdl")
    print("2 + 5 =", client.service.add(2, 5))
