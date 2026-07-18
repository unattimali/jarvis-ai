from flask import Flask, request, jsonify
from flask_cors import CORS
from ollama import chat
import requests
import random

import os
from werkzeug.utils import secure_filename

AI_MODEL = "gemma3:1b"

from fun_data import *
from study_data import *

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "uploads"
)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Enable CORS
CORS(app)

# OpenWeather API Key
WEATHER_API_KEY = "571e4eed27cbf118d268a4e7c107a652"
GNEWS_API_KEY = "f4b341463a55429bc34f174227690619"
CURRENCY_API = "https://open.er-api.com/v6/latest"
JOKE_API = "https://v2.jokeapi.dev/joke/Any?safe-mode"



# ---------------- CHAT ROUTE ---------------- #

@app.route("/chat", methods=["POST"])
def chat_with_ai():

    data = request.json
    user_message = data["message"]

    
    

    # ---------- WEATHER ----------

    if "weather" in user_message.lower():

        city = "Ahmedabad"   # Default city

        words = user_message.split()

        for i, word in enumerate(words):

            if word.lower() == "in" and i + 1 < len(words):
                city = words[i + 1]
                break

        url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?q={city}&appid={WEATHER_API_KEY}&units=metric"
        )

        response = requests.get(url)
        weather = response.json()

        if response.status_code != 200:

            return jsonify({
                "reply": "❌ City not found."
            })

        weather_text = f"""
🌤 <b>Weather Report</b>

📍 {weather['name']}, {weather['sys']['country']}

🌡 <b>Temperature:</b> {round(weather['main']['temp'])}°C

🥵 <b>Feels Like:</b> {round(weather['main']['feels_like'])}°C

💧 <b>Humidity:</b> {weather['main']['humidity']}%

🌬 <b>Wind:</b> {weather['wind']['speed']} m/s

☁ <b>Condition:</b> {weather['weather'][0]['description'].title()}
"""

        return jsonify({
            "reply": weather_text
        })

        # ---------- DICTIONARY ----------

    message = user_message.lower()

    if (
        message.startswith("meaning")
        or message.startswith("meaning of")
        or message.startswith("define")
        or message.startswith("what is")
    ):

        word = (
            message.replace("meaning of", "")
                   .replace("meaning", "")
                   .replace("define", "")
                   .replace("what is", "")
                   .strip()
        )

        if word == "":
            return jsonify({
                "reply": "❌ Please enter a word."
            })

        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"

        response = requests.get(url)

        if response.status_code != 200:
            return jsonify({
                "reply": f"❌ No definition found for '{word}'."
            })

        data = response.json()

        entry = data[0]

        meaning = "Meaning not available."
        example = "No example available."
        part = "Unknown"

        synonyms = []
        antonyms = []

        for m in entry["meanings"]:

            if part == "Unknown":
                part = m["partOfSpeech"]

            if "synonyms" in m:
                synonyms.extend(m["synonyms"])

            if "antonyms" in m:
                antonyms.extend(m["antonyms"])

            for d in m["definitions"]:

                if meaning == "Meaning not available.":
                    meaning = d["definition"]

                if (
                    example == "No example available."
                    and "example" in d
                ):
                    example = d["example"]

                if "synonyms" in d:
                    synonyms.extend(d["synonyms"])

                if "antonyms" in d:
                    antonyms.extend(d["antonyms"])

        synonyms = list(dict.fromkeys(synonyms))
        antonyms = list(dict.fromkeys(antonyms))

        synonym_text = ", ".join(synonyms[:5]) if synonyms else "Not available"

        antonym_text = ", ".join(antonyms[:5]) if antonyms else "Not available"

        dictionary_text = f"""
📖 <b>Dictionary</b>

🔤 <b>Word:</b> {entry['word'].title()}

🏷 <b>Part of Speech:</b> {part.title()}

📚 <b>Meaning:</b>
{meaning}

💡 <b>Example:</b>
{example}

✅ <b>Synonyms:</b>
{synonym_text}

❌ <b>Antonyms:</b>
{antonym_text}
"""

        return jsonify({
            "reply": dictionary_text
        })
    # ---------- NEWS ----------

    if "news" in user_message.lower():

        category = "general"

        message = user_message.lower()

        if "technology" in message or "tech" in message:
            category = "technology"

        elif "business" in message:
            category = "business"

        elif "sports" in message or "sport" in message:
            category = "sports"

        elif "health" in message:
            category = "health"

        elif "science" in message:
            category = "science"

        elif "entertainment" in message:
            category = "entertainment"

        url = (
            f"https://gnews.io/api/v4/top-headlines?"
            f"category={category}"
            f"&lang=en"
            f"&country=in"
            f"&max=5"
            f"&apikey={GNEWS_API_KEY}"
        )

        response = requests.get(url)

        data = response.json()

        if "articles" not in data:
            return jsonify({
                "reply": "❌ Unable to fetch news."
            })

        news_text = f"📰 <b>{category.title()} News</b><br><br>"

        for i, article in enumerate(data["articles"], start=1):

            news_text += (
                f"{i}. <b>{article['title']}</b><br>"
                f"🔗 {article['url']}<br><br>"
            )

        return jsonify({
            "reply": news_text
        })
    

    # ---------- CURRENCY CONVERTER ----------

    if " to " in user_message.lower() or "convert" in user_message.lower():

        import re

        try:

            message = user_message.upper()

            # Remove unnecessary words
            message = message.replace("CONVERT", "")

            # Currency name replacements
            replacements = {
                "INDIAN RUPEES": "INR",
                "INDIAN RUPEE": "INR",
                "RUPEES": "INR",
                "RUPEE": "INR",
                "RS.": "INR",
                "RS": "INR",

                "US DOLLARS": "USD",
                "US DOLLAR": "USD",
                "DOLLARS": "USD",
                "DOLLAR": "USD",

                "EUROS": "EUR",
                "EURO": "EUR",

                "POUNDS": "GBP",
                "POUND": "GBP",

                "YEN": "JPY",

                "DIRHAM": "AED",
                "DIRHAMS": "AED"
            }

            for key, value in replacements.items():
                message = message.replace(key, value)

            # Add space if user types 100USD
            message = re.sub(r'(\d)([A-Z])', r'\1 \2', message)

            parts = message.split()

            amount = float(parts[0])
            from_currency = parts[1]
            to_currency = parts[3]

            response = requests.get(
                f"{CURRENCY_API}/{from_currency}"
            )

            data = response.json()

            if data["result"] != "success":

                return jsonify({
                    "reply": "❌ Invalid currency code."
                })

            if to_currency not in data["rates"]:

                return jsonify({
                    "reply": "❌ Currency not found."
                })

            rate = data["rates"][to_currency]

            converted = round(amount * rate, 2)

            return jsonify({
                "reply": f"""
💱 <b>Currency Converter</b>

💵 {amount} {from_currency}

⬇

💰 <b>{converted} {to_currency}</b>
"""
            })

        except:

            return jsonify({
                "reply":
"""❌ Examples:

100 USD to INR
500 INR to USD
5 rupees to usd
250 rs to usd
convert 100 dollars to rupees
"""
            })
        
# ---------- STUDY HUB ----------

    if (
        "study" == user_message.lower()
        or "study hub" in user_message.lower()
        or "study assistant" in user_message.lower()
    ):

        return jsonify({
            "reply": study_menu
        })


# ---------- RANDOM FACT ----------

    if (
        "random fact" in user_message.lower()
        or user_message.lower().strip() == "fact"
        or "tell me a fact" in user_message.lower()
        or "give me a fact" in user_message.lower()
    ):

        try:

            response = requests.get(
                "https://uselessfacts.jsph.pl/api/v2/facts/random"
            )

            data = response.json()

            return jsonify({
                "reply": f"""
💡 <b>Random Fact</b>

📖 {data['text']}
"""
            })

        except:

            return jsonify({
                "reply": "❌ Unable to fetch a random fact."
            }) 

    # ---------- JOKE GENERATOR ----------

    if (
        "joke" in user_message.lower()
        or "tell me a joke" in user_message.lower()
        or "make me laugh" in user_message.lower()
    ):

        try:


            response = requests.get(
                "https://official-joke-api.appspot.com/random_joke"
            )

            data = response.json()

            intros = [
                "😂 Here's one for you!",
                "🤣 Get ready to laugh!",
                "😄 Jarvis found a funny one!",
                "🎭 Comedy mode activated!",
                "😁 Hope this makes you smile!"
            ]

            intro = random.choice(intros)

            return jsonify({
                "reply": f"""
{intro}

🎤 <b>Setup:</b>

{data['setup']}

🤣 <b>Punchline:</b>

{data['punchline']}

😆 Want another? Just type <b>joke</b> again!
"""
            })

        except:

            return jsonify({
                "reply": "❌ Sorry! I couldn't think of a joke right now."
            })  
        

 # ---------- PROGRAMMING JOKE ----------

    if (
         "programming joke" in user_message.lower()
        or "coding joke" in user_message.lower()
        ):

        joke = random.choice(programming_jokes)

        return jsonify({
        "reply": f"""
    😂 <b>Programming Joke</b>

    🤣 {joke['setup']}

    💬 {joke['punchline']}
    """
        })   
    
# ---------- DAD JOKE ----------

    if (
        "dad joke" in user_message.lower()
        or "funny joke" in user_message.lower()
    ):

            joke = random.choice(dad_jokes)

            return jsonify({
                "reply": f"""
😂 <b>Dad Joke</b>

🤣 {joke}
"""
        })

# ---------- RIDDLE ----------

    if (
        "riddle" in user_message.lower()
        or "brain teaser" in user_message.lower()
    ):

        riddle = random.choice(riddles)

        return jsonify({
            "reply": f"""
🧠 <b>Riddle</b>

❓ {riddle['question']}

💡 <b>Answer:</b>

{riddle['answer']}
"""
        })
# ---------- PICKUP LINE ----------

    if (
        "pickup line" in user_message.lower()
        or "pick up line" in user_message.lower()
        or "flirt" in user_message.lower()
    ):

        line = random.choice(pickup_lines)

        return jsonify({
            "reply": f"""
❤️ <b>Pickup Line</b>

😘 {line}
"""
        })
# ---------- ROAST ME ----------

    if (
        "roast me" in user_message.lower()
        or "roast" in user_message.lower()
    ):

        roast = random.choice(roasts)

        return jsonify({
            "reply": f"""
🔥 <b>Roast Me</b>

😂 {roast}

😎 Don't take it personally... you asked for it!
"""
        })
# ---------- TRUTH ----------

    if (
        user_message.lower() == "truth"
        or "truth question" in user_message.lower()
        or "give me a truth" in user_message.lower()
    ):

        truth = random.choice(truths)

        return jsonify({
            "reply": f"""
🎲 <b>Truth</b>

🤔 {truth}
"""
        })
# ---------- DARE ----------

    if (
        user_message.lower() == "dare"
        or "give me a dare" in user_message.lower()
        or "dare challenge" in user_message.lower()
    ):

        dare = random.choice(dares)

        return jsonify({
            "reply": f"""
🎯 <b>Dare Challenge</b>

😈 {dare}

🔥 Come on... you accepted the challenge!
"""
        })
# ---------- WOULD YOU RATHER ----------

    if (
        "would you rather" in user_message.lower()
        or user_message.lower() == "wyr"
        or user_message.lower() == "would"
    ):

        question = random.choice(would_you_rather)

        return jsonify({
            "reply": f"""
🎉 <b>Would You Rather</b>

🤔 {question}

👇 Reply with your choice!
"""
        })
# ---------- DAILY MOTIVATION ----------

    if (
        "motivation" in user_message.lower()
        or "motivate me" in user_message.lower()
        or "daily motivation" in user_message.lower()
    ):

        quote = random.choice(motivations)

        return jsonify({
            "reply": f"""
🌟 <b>Daily Motivation</b>

💪 {quote}

🚀 Keep moving forward!
"""
        })
    # ---------- INSPIRATIONAL QUOTES ----------

    if (
        "quote" in user_message.lower()
        or "inspirational quote" in user_message.lower()
        or "quote of the day" in user_message.lower()
    ):

        quote = random.choice(quotes)

        return jsonify({
            "reply": f"""
💬 <b>Inspirational Quote</b>

📜 {quote}

✨ Have an amazing day!
"""
        })
    # ---------- COMPLIMENT ----------

    if (
        "compliment" in user_message.lower()
        or "compliment me" in user_message.lower()
        or "say something nice" in user_message.lower()
        or "praise me" in user_message.lower()
    ):

        compliment = random.choice(compliments)

        return jsonify({
            "reply": f"""
🎁 <b>Compliment</b>

😊 {compliment}

🌟 Keep being awesome!
"""
        })
    # ---------- BRAIN TEASER ----------

    if (
        "brain teaser" in user_message.lower()
        or "brain game" in user_message.lower()
        or "brain puzzle" in user_message.lower()
        or "teaser" in user_message.lower()
    ):

        teaser = random.choice(brain_teasers)

        return jsonify({
            "reply": f"""
🤯 <b>Brain Teaser</b>

🧩 {teaser}
"""
        })
    # ---------- COIN TOSS ----------

    if (
        "coin toss" in user_message.lower()
        or "flip a coin" in user_message.lower()
        or "heads or tails" in user_message.lower()
        or user_message.lower() == "coin"
    ):

        result = random.choice(["🪙 Heads", "🪙 Tails"])

        return jsonify({
            "reply": f"""
🪙 <b>Coin Toss</b>

The coin is spinning...

🎉 <b>{result}</b>
"""
        })
    # ---------- DICE ROLLER ----------

    if (
        "roll dice" in user_message.lower()
        or "roll a dice" in user_message.lower()
        or user_message.lower() == "dice"
        or "dice roller" in user_message.lower()
    ):

        number = random.randint(1, 6)

        dice = {
            1: "⚀",
            2: "⚁",
            3: "⚂",
            4: "⚃",
            5: "⚄",
            6: "⚅"
        }

        return jsonify({
            "reply": f"""
🎲 <b>Dice Roller</b>

Rolling...

🎉 You rolled:

{dice[number]} <b>{number}</b>
"""
        })
# ---------- MAGIC 8 BALL ----------
    if (
    "magic 8 ball" in user_message.lower()
    or "8 ball" in user_message.lower()
    or user_message.strip().endswith("?")
    ):

        answer = random.choice(magic_8_ball)

        return jsonify({
            "reply": f"""
🎱 <b>Magic 8 Ball</b>

🔮 {answer}

✨ Ask me another yes/no question!
"""
        })
   # ---------- EXCUSE GENERATOR ----------

    if (
        "excuse" in user_message.lower()
        or "give me an excuse" in user_message.lower()
        or "i need an excuse" in user_message.lower()
    ):

        excuse = random.choice(excuses)
        ending = random.choice(excuse_endings)

        return jsonify({
            "reply": f"""
🙈 <b>Excuse Generator</b>

📝 {excuse}

{ending}
"""
        })
    # ---------- GAMER CHALLENGE ----------

    if (
        "challenge me" in user_message.lower()
        or "challenge" in user_message.lower()
        or "give me a challenge" in user_message.lower()
    ):

        challenge = random.choice(gamer_challenges)

        return jsonify({
            "reply": f"""
🎮 <b>Challenge Accepted!</b>

🏆 {challenge}

🔥 Complete it and come back for another one!
"""
        })
    # ---------- FOOD SUGGESTION ----------

    if (
        "what should i eat" in user_message.lower()
        or "food suggestion" in user_message.lower()
        or "suggest food" in user_message.lower()
        or "recommend food" in user_message.lower()
        or "hungry" in user_message.lower()
    ):

        food = random.choice(foods)
        ending = random.choice(food_endings)

        return jsonify({
            "reply": f"""
🍕 <b>Food Suggestion</b>

🍽 Today's recommendation:

<b>{food}</b>

{ending}
"""
        })

    # ---------- OLLAMA ----------

    response = chat(
        model=AI_MODEL,
        messages=[
            {
                "role": "user",
                "content": user_message
            }
        ]
    )

    return jsonify({
        "reply": response["message"]["content"]
    }) 

# ===============================
# PDF Upload
# ===============================

import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/upload_pdf", methods=["POST"])
def upload_pdf():

    if "pdf" not in request.files:

        return jsonify({
            "reply": "❌ No PDF Selected."
        })

    file = request.files["pdf"]

    if file.filename == "":

        return jsonify({
            "reply": "❌ Please choose a PDF."
        })

    filename = secure_filename(file.filename)

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    file.save(filepath)

    return jsonify({
        "reply": f"✅ PDF Uploaded Successfully!<br><br>📄 {filename}"
    })    

    
# ---------------- WEATHER API ---------------- #

@app.route("/weather", methods=["GET"])
def weather():

    city = request.args.get("city")

    if not city:
        return jsonify({
            "error": "City is required"
        }), 400

    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={WEATHER_API_KEY}&units=metric"
    )

    response = requests.get(url)
    data = response.json()

    if response.status_code != 200:
        return jsonify(data), response.status_code

    return jsonify({
        "city": data["name"],
        "country": data["sys"]["country"],
        "temp": data["main"]["temp"],
        "feels_like": data["main"]["feels_like"],
        "humidity": data["main"]["humidity"],
        "wind": data["wind"]["speed"],
        "description": data["weather"][0]["description"],
        "icon": data["weather"][0]["icon"]
    })


# ---------------- RUN SERVER ---------------- #

if __name__ == "__main__":
    app.run(debug=True)