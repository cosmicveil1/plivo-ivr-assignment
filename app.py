from flask import Flask, request, Response
from plivo import RestClient, plivoxml
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

# =========================
# PLIVO CONFIG
# =========================

AUTH_ID = os.getenv("AUTH_ID")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")

PLIVO_NUMBER = os.getenv("PLIVO_NUMBER")

YOUR_NUMBER = os.getenv("YOUR_NUMBER")

BASE_URL = os.getenv("BASE_URL")

CORRECT_OTP = os.getenv("CORRECT_OTP")

client = RestClient(
    auth_id=AUTH_ID,
    auth_token=AUTH_TOKEN
)

# =========================
# HOME
# =========================

@app.route("/")
def home():
    return "IVR Running"

# =========================
# MAKE CALL
# =========================

@app.route("/make-call")
def make_call():

    response = client.calls.create(
        from_=PLIVO_NUMBER,
        to_=YOUR_NUMBER,
        answer_url=f"{BASE_URL}/answer",
        answer_method="GET"
    )

    return {
        "message": "Call initiated",
        "response": str(response)
    }

# =========================
# ANSWER
# =========================

@app.route("/answer", methods=["GET", "POST"])
def answer():

    response = plivoxml.ResponseElement()

    get_digits = plivoxml.GetDigitsElement(
        action=f"{BASE_URL}/check-otp",
        method="POST",
        num_digits=4,
        timeout=7
    )

    get_digits.add(
        plivoxml.SpeakElement(
            "Please enter your four digit OTP."
        )
    )

    response.add(get_digits)

    return Response(
        response.to_string(),
        mimetype="text/xml"
    )

# =========================
# CHECK OTP
# =========================

@app.route("/check-otp", methods=["POST"])
def check_otp():

    digits = request.form.get("Digits")

    response = plivoxml.ResponseElement()

    if digits == CORRECT_OTP:

        response.add(
            plivoxml.SpeakElement(
                "Authentication successful."
            )
        )

        get_digits = plivoxml.GetDigitsElement(
            action=f"{BASE_URL}/language",
            method="POST",
            num_digits=1
        )

        get_digits.add(
            plivoxml.SpeakElement(
                "Press 1 for English. Press 2 for Spanish."
            )
        )

        response.add(get_digits)

    else:

        response.add(
            plivoxml.SpeakElement(
                "Incorrect OTP. Please try again."
            )
        )

        response.add(
            plivoxml.RedirectElement(
                f"{BASE_URL}/answer"
            )
        )

    return Response(
        response.to_string(),
        mimetype="text/xml"
    )

# =========================
# LANGUAGE MENU
# =========================

@app.route("/language", methods=["POST"])
def language():

    digit = request.form.get("Digits")

    response = plivoxml.ResponseElement()

    if digit == "1":

        get_digits = plivoxml.GetDigitsElement(
            action=f"{BASE_URL}/action",
            method="POST",
            num_digits=1
        )

        get_digits.add(
            plivoxml.SpeakElement(
                "English selected. Press 1 to play audio. Press 2 to connect associate."
            )
        )

        response.add(get_digits)

    elif digit == "2":

        get_digits = plivoxml.GetDigitsElement(
            action=f"{BASE_URL}/action",
            method="POST",
            num_digits=1
        )

        get_digits.add(
        plivoxml.SpeakElement(
            "Español seleccionado. Presione uno para reproducir audio. Presione dos para conectar con un asociado."
        )
    )

        response.add(get_digits)

    else:

        response.add(
            plivoxml.SpeakElement(
                "Invalid input."
            )
        )

        response.add(
            plivoxml.RedirectElement(
                f"{BASE_URL}/language"
            )
        )

    return Response(
        response.to_string(),
        mimetype="text/xml"
    )

# =========================
# ACTION MENU
# =========================

@app.route("/action", methods=["POST"])
def action():

    digit = request.form.get("Digits")

    response = plivoxml.ResponseElement()

    if digit == "1":

        response.add(
            plivoxml.SpeakElement(
                "Playing audio now."
            )
        )

        response.add(
            plivoxml.PlayElement(
                "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
            )
        )

    elif digit == "2":

        response.add(
            plivoxml.SpeakElement(
                "Connecting your call."
            )
        )

        dial = plivoxml.DialElement()

        dial.add(
            plivoxml.NumberElement(
                "02264236412"
            )
        )

        response.add(dial)

    else:

        response.add(
            plivoxml.SpeakElement(
                "Invalid choice."
            )
        )

        response.add(
            plivoxml.RedirectElement(
                f"{BASE_URL}/action"
            )
        )

    return Response(
        response.to_string(),
        mimetype="text/xml"
    )

# =========================
# RUN SERVER
# =========================

if __name__ == "__main__":
    app.run(port=5000, debug=True)