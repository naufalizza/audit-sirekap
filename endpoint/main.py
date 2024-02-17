from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/invalid-endpoints")
def read_invalid_endpoints():
    return {
        "timestamp": 213213,
        "data": [
            {
                "endpoint_tps": "http://pemilu2024.kpu.go.id/pilpres/hitung-suara/34/3403/340309/3403092003/3403092003001",
                "assertion_error": [
                    "Assertion Error 1",
                    "Assertion Error 2",
                    "Assertion Error 3",
                ]
            },
            {
                "endpoint_tps": "https://pemilu2024.kpu.go.id/pilpres/hitung-suara/73/7371/737111/7371111005/7371111005001",
                "assertion_error": [
                    "Assertion Error 2",
                    "Assertion Error 4"
                ]
            }
        ]
    }
