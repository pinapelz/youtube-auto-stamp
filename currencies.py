import requests
import json

class CurrencyConv:
    def __init__(self, currency_json_url: str="https://open.er-api.com/v6/latest/USD"):
        try:
            self._currency_data = json.loads(requests.get(currency_json_url).text)
        except:
            raise Exception("Unable to load currency data from " + currency_json_url)
        self._currency_rates = self._currency_data["rates"]
    
    def convert(self, amount: float, from_currency: str, to_currency: str) -> float:
        # handle some conversion errors
        from_currency = from_currency.replace("\xa0", "").strip().upper()
        from_currency= from_currency.replace("₱", "PHP")
        from_currency = from_currency.replace("¥", "JPY")
        try:
            if from_currency == to_currency:
                return amount
            return amount * self._currency_rates[to_currency] / self._currency_rates[from_currency]
        except:
            raise Exception("Unable to convert from " + from_currency + " to " + to_currency)

if __name__ == "__main__":
    converter = CurrencyConv()
    print(converter.convert(100.0, "SGD", "USD"))        
