import requests
import json

API_URL = "http://localhost:8000/notes"  # ändra om du kör på annan host

def test_notes_api():
    test_input = "möte igår med anna vi pratade om budget måste fixa rapport till fredag"

    print("🔹 Skickar testanteckningar till API...")
    response = requests.post(API_URL, json={"text": test_input})

    if response.status_code != 200:
        print(f"❌ Fel: Statuskod {response.status_code}")
        print(response.text)
        return

    try:
        data = response.json()
        print("✅ Response JSON:")
        print(json.dumps(data, indent=2, ensure_ascii=False))

        # Enkel validering av fält
        for key in ["title", "date", "summary", "action_items"]:
            if key not in data:
                print(f"❌ Fält saknas: {key}")
                return

        if not isinstance(data["action_items"], list):
            print("❌ action_items är inte en lista")
            return

        print("🎉 Testet lyckades! Alla fält finns och action_items är en lista.")

    except json.JSONDecodeError:
        print("❌ JSON kunde inte parsas")
        print(response.text)


if __name__ == "__main__":
    test_notes_api()
