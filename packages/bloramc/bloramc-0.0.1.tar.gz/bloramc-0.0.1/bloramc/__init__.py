# bloramc/__init__.py

class _BloraMcPrinter:
    def __call__(self, message):
        print(f"BloraMc : {message}")

# Create an instance that can be called like a function
bloramc = _BloraMcPrinter()
