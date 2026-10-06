#!/usr/bin/env python3
"""Build public/index.html for The Shelf.

All app data lives here. Run `python3 build.py` after editing and commit the
regenerated public/index.html. The output is plain static HTML (no JS needed to
see every app), so it stays crawlable and instant to paint.
"""
import html
import json
import os

SITE = "https://apps.suvadipchakraborty.workers.dev"
WORKERS = "suvadipchakraborty.workers.dev"
FEEDBACK_TO = "suvadipchakraborty@gmail.com"

# id, label, blurb, hue (oklch), fallback light hex, fallback deep hex
CATEGORIES = [
    ("around", "Around you", "Live data for Indian cities and everyday errands.", 258),
    ("safe", "Health & safety", "Checks worth doing before you tap, take or eat.", 150),
    ("learn", "Learn", "Quick reads and flashcards for curious minds.", 315),
    ("time", "Through time", "Old news, inventions and objects, one day at a time.", 70),
    ("world", "World & culture", "Places, food, faith, books and film from everywhere.", 205),
    ("games", "Games", "Daily puzzles and quick rounds. No sign-up.", 25),
]

# Apps flagged here get a "New" badge. Remove ids once they stop being new.
NEW = {"radio", "flightdle", "pulse", "reality", "altsurf", "address", "chuckle", "safebite", "daru", "debunk", "ghost",
       "sip", "pantry", "stargazer", "faceoff", "moodpoem", "dossier", "auratunes", "roast"}

# id: (name, category, short tagline, long description, url, search keywords)
def u(sub, q=""):
    return f"https://{sub}.{WORKERS}/{q}"

APPS = [
    # ---- Around you
    ("traffic", "Indian Traffic Premier League", "around",
     "Which city loses the most time to traffic",
     "Live rankings of how much time your city's traffic steals from you, hour by hour.",
     u("indian-traffic-premier-league"), "traffic city rankings commute delay congestion jam"),
    ("air", "Air Olympics", "around",
     "100 cities ranked by yesterday's air",
     "100 cities, one daily leaderboard — who breathed the cleanest air yesterday.",
     u("air-olympics"), "air quality aqi pollution cities rankings breathe"),
    ("mandi", "Mandi Nibs", "around",
     "Today's wholesale mandi prices",
     "Today's real wholesale mandi prices, before you leave the house. Know before you buy.",
     u("mandi"), "vegetables fruit prices market sabzi wholesale produce"),
    ("train", "TrainLive", "around",
     "Live running status of any train",
     "Enter any Indian Railways train number and see its live running status — current location, next station, platform and delay.",
     u("train-tracker"), "railway irctc train status delay platform station"),
    ("pin", "PIN Code Buddy", "around",
     "Post office and district for any PIN",
     "Type any 6-digit Indian PIN code and get the post office, district, state and delivery status, straight from India Post's own records.",
     u("pin-code-buddy"), "pincode postal post office address zip india post"),
    ("sarkar", "Sarkar Sahayak", "around",
     "Government schemes you may qualify for",
     "Answer three simple questions and see the government schemes you may actually qualify for — eligibility, benefits and steps, in plain language.",
     u("sarkar-sahayak"), "government schemes yojana eligibility benefits welfare"),
    ("reality", "Reality Check", "around",
     "What your salary becomes in a new city",
     "Compare two cities side by side on rent, utilities and everyday costs, then see what your current salary is really worth in the new place, in your own currency.",
     u("reality-check"), "relocation moving city salary cost of living rent calculator compare"),
    ("address", "AddressCraft India", "around",
     "Clean, split Indian addresses to paste",
     "Turn any area, city or PIN code into properly split fields (house number, street, locality, city, state and PIN), ready to paste into checkout forms.",
     u("addresscraft"), "address format checkout form delivery pincode locality india split fields"),
    ("daru", "Daru Desi", "around",
     "Same bottle, different city, different price",
     "Alcohol prices in India change at every state border. Browse what's available in each city, compare your home city with where you're headed, and spot the bottles that cost less when you travel.",
     u("daru-desi"), "alcohol liquor whisky beer wine rum vodka prices compare state travel bottle duty"),
    ("sip", "SIP Time Machine", "around",
     "What your monthly SIP would be worth today",
     "Pick any mutual fund, set your monthly amount and dial the years. See exactly what that disciplined SIP would be worth today, with no complicated charts.",
     u("sip-time-machine"), "sip mutual fund investment returns calculator money savings what if invest monthly nav"),
    ("pantry", "Pantry Rescue", "around",
     "Turn what's in your fridge into dinner",
     "Add the ingredients you already have and find recipes that need the fewest extras. No more staring into the fridge or ordering out.",
     u("pantry-rescue"), "recipes cooking ingredients fridge leftovers dinner meals kitchen food pantry"),

    # ---- Health & safety
    ("thaga", "ThagaShield", "safe",
     "Check a suspicious call, text or chat",
     "Paste a suspicious call, text or chat and get a straight answer in 60 seconds. Nothing leaves your phone.",
     u("thaga-shield"), "scam fraud phishing spam cyber safety whatsapp thaga"),
    ("side", "Side Effect Checker", "safe",
     "Official FDA warnings by medicine salt",
     "Type the salt name printed on the strip and get official FDA warnings and the most reported reactions in plain, scannable cards.",
     u("side-effect"), "medicine drug salt tablet pharmacy reactions warnings"),
    ("foodrx", "FoodRx", "safe",
     "What to eat and avoid, all in one list",
     "Select your health conditions and get one combined list of foods to eat and avoid — no conflicting advice, just where they overlap.",
     u("foodrx", "?v=2"), "diet nutrition food eat avoid health conditions"),
    ("safebite", "SafeBite", "safe",
     "Instant allergen check before you eat",
     "Set your allergy profile once (it stays on your device), then check any food for allergens before you take a bite. Powered by Open Food Facts.",
     u("safebite"), "allergy allergen food peanuts dairy gluten eggs soy shellfish barcode safe"),
    ("debunk", "Debunk Daily", "safe",
     "Today's fake news, fact-checked",
     "The latest false stories as clean cards, newest first, each with the claim and the verdict on why it doesn't hold up. No endless threads, no noise.",
     u("debunk-daily"), "fake news fact check misinformation hoax claims debunk verdict rumour whatsapp forward"),

    # ---- Learn
    ("bytebriefs", "ByteBriefs", "learn",
     "Data & AI news in 60 seconds",
     "Data & AI news in 60 seconds a day. No fluff, one clear takeaway.",
     u("byte-briefs"), "news data ai analytics daily digest briefing"),
    ("abstracted", "Abstracted", "learn",
     "Latest AI research as swipeable cards",
     "The latest AI research as clean, swipeable cards. No 40-page PDFs staring you down.",
     u("abstracted", "?v=2"), "ai research papers arxiv summaries cards"),
    ("tharoor", "Tharoor Words", "learn",
     "Rare-word flashcards that work offline",
     "Build a vocabulary like Shashi Tharoor. Flashcards of rare words with pronunciation, definitions and examples, and it works offline.",
     u("new-word"), "vocabulary words flashcards english dictionary offline learn"),
    ("synapse", "Synapse", "learn",
     "Human knowledge as a living constellation",
     "Human knowledge as a living constellation — tap a spark, watch a field of ideas light up.",
     u("synapse", "?v=2"), "knowledge ideas map constellation explore network"),
    ("pulse", "Curiosity Pulse", "learn",
     "What the world is reading right now",
     "What is the world reading right now? Live top Wikipedia articles by country, plus a real-time stream of edits happening this second.",
     u("curiosity-pulse"), "wikipedia trending reading live edits countries"),
    ("altsurf", "Alt-Surf", "learn",
     "Real alternatives to any website",
     "Type in the site you're stuck on and discover what else exists. No rankings, no sponsored results, just alternatives.",
     u("alt-surf"), "alternatives websites similar sites discover netflix reddit notion spotify"),
    ("stargazer", "Stargazer", "learn",
     "ISS, sky cover, moon and NASA's picture",
     "A pocket dashboard for the cosmos: live ISS position, local cloud cover and visibility, the moon phase and NASA's Astronomy Picture of the Day.",
     u("stargazer"), "stars night sky iss space station moon phase nasa apod astronomy clouds visibility telescope"),
    ("faceoff", "Country Face-Off", "learn",
     "Two countries, thirty years of data",
     "Put any two nations head to head on GDP per capita, life expectancy, internet usage and more. Watch the lines race across three decades and get the verdict. Powered by World Bank data.",
     u("country-face-off"), "countries compare gdp life expectancy internet world bank data india usa china germany versus"),

    # ---- Through time
    ("retro", "Retroactive", "time",
     "Tech and science history, any date",
     "A daily time machine through tech and science history — pick a date, meet the past.",
     u("retroactive"), "history tech science timeline on this day"),
    ("gazette", "The Time Machine Gazette", "time",
     "Read newspapers from 100 years ago today",
     "Open today's date, wind the clock back a century, and read the actual newspapers from that exact day. No summaries, no modern commentary.",
     u("news18"), "newspaper history archive century old chronicling"),
    ("prior", "Prior Art", "time",
     "A daily dive into odd, brilliant patents",
     "A daily dive into the brilliant, bizarre and genuinely patented. Real diagrams, real inventions.",
     u("prior-art"), "patents inventions diagrams history"),
    ("artifact", "The Daily Artifact", "time",
     "One museum object, every day",
     "One object from the world's museums, every day. Switch between Global and India Only, then tap Discover Next for another.",
     u("museum"), "museum objects art history india collection"),
    ("dossier", "Court Dossier", "time",
     "History's notable crimes, as clean case files",
     "Browse real cases across decades and countries and read a clean narrative of the investigation and trial, without the dense legalese or wiki-bloat.",
     u("court-dossier"), "crime court cases trials investigation true crime history law dossier detective"),

    # ---- World & culture
    ("compass", "Cultural Compass", "world",
     "Who's celebrating what, on any date",
     "Tap any date and see who's celebrating, remembering or observing something, anywhere in the world.",
     u("global-holidays", "?v=2"), "holidays festivals calendar observances world dates"),
    ("culinary", "Culinary Geography", "world",
     "A real dish for every country",
     "Tap a country, meet its people, taste its story — a real dish tied to a real place.",
     u("global-food", "?v=2"), "food dishes cuisine recipes countries"),
    ("wander", "Wanderlust Roulette", "world",
     "Shake your phone, land in a random country",
     "Shake your phone and land in a random country, with a photo, budget check, capital, languages, currency and a map link.",
     u("wanderlust"), "travel random country trip map shake destination"),
    ("radio", "Radio Golden Hour", "world",
     "Local radio where the sun is setting now",
     "Finds the city where the sun is setting right now and plays a real local radio station. Drift west with the dusk line.",
     u("golden-hour"), "radio music stations sunset live listen"),
    ("ghost", "Forgotten Coordinates", "world",
     "Find any city's ghost twin",
     "Type any city and meet its ghost twin: a place that once lived and was left behind, with the story history forgot. No tourist traps, just lost places.",
     u("forgotten-coordinates"), "ghost town abandoned lost places ruins history city twin travel forgotten"),
    ("ekayana", "Ekayana", "world",
     "A quiet room for the Gita, Quran and Bible",
     "A quiet, distraction-free room to sit with the Gita, the Quran and the Bible, one verse at a time.",
     u("spiritual-books", "?v=2"), "gita quran bible scripture verses spiritual religion"),
    ("blind", "Blind Date with a Book", "world",
     "Pick a mood, unwrap a mystery book",
     "No cover, no title — just pick a mood, cozy to dark & twisty, and meet the book waiting to be unwrapped.",
     u("blind-date-book"), "books reading mood random novel gift"),
    ("spoiler", "The Reverse Spoiler", "world",
     "A brutal second opinion on any movie",
     "The anti-watchlist. Type a movie, get a brutal second opinion on why to skip it, plus what else you could do with those two hours.",
     u("reverse-spoiler"), "movies film cinema skip watchlist review"),
    ("moodpoem", "Mood Poem", "world",
     "One classic poem for how you feel right now",
     "Tell it how you feel, or how the weather feels, and get one timeless classic poem to match. No scrolling, no modern noise.",
     u("mood-poem"), "poem poetry verse classic mood feeling romantic melancholy hopeful rain literature"),
    ("auratunes", "AuraTunes", "world",
     "Pick a mood, get five tracks",
     "Choose a mood, add a genre and an era, and get a short curated playlist of five tracks instantly. No endless scrolling, no algorithm rabbit holes.",
     u("mood-music"), "music songs playlist mood chill energetic focus romantic genre era tracks discover"),

    # ---- Games
    ("flightdle", "Flightdle", "games",
     "Daily puzzle: name the flight's destination",
     "The daily aviation puzzle. See where a real flight took off, the airline and the aircraft, then name the hidden destination in five guesses. Distance and compass hints, a streak, and a shareable emoji grid.",
     u("plane-above"), "wordle flights planes aviation daily puzzle airports"),
    ("chroma", "Chroma Guess", "games",
     "A daily colour game that humbles you",
     "The daily colour game that quietly destroys your confidence. Five rounds, four near-identical options, or go Endless until your first miss.",
     u("colours"), "colour color game daily puzzle eyes"),
    ("gauntlet", "The Gauntlet", "games",
     "Trivia survival with three lives",
     "A trivia survival roguelike. Three lives, shrinking timers, and a boss round with no lifelines.",
     u("trivia-fight"), "trivia quiz roguelike game lives boss"),
    ("tatkal", "Tatkal Tapasya", "games",
     "The 10am Tatkal panic, as a game",
     "The 10am IRCTC Tatkal booking panic, recreated as a game. No real tickets, all the trauma.",
     u("tatkal"), "irctc ticket booking game railway panic"),
    ("jargon", "Jargon Buster", "games",
     "Corporate nonsense, decoded",
     "Hit \"Synergize Paradigm\" for a fresh piece of corporate nonsense, then watch it get decoded into actual human language.",
     u("jargon-buster"), "corporate office buzzwords humour game decode"),
    ("chuckle", "The Chuckle Hub", "games",
     "One clean joke, whenever you need it",
     "Tap once, get a light joke, heart the ones you love and come back for another. No doomscrolling, no feeds.",
     u("chuckle-hub"), "jokes humour funny laugh smile daily fun"),
    ("roast", "Roast & Toast", "games",
     "One tap for a roast, one for a compliment",
     "Need the perfect compliment for a friend or the ultimate comeback for a troll? One tap for a savage roast, one for a pure compliment, with one-click copy.",
     u("roast-toast"), "roast compliment insult comeback toast friend funny copy banter humour troll"),
]

# ---------------------------------------------------------------- glyphs
# 24x24, stroke-based. Colour/stroke width come from CSS (.glyph).
DOT = 'fill="currentColor" stroke="none"'
GLYPHS = {
    "traffic": f'<rect x="8" y="2.5" width="8" height="19" rx="3"/><circle cx="12" cy="7.5" r="1.3" {DOT}/><circle cx="12" cy="12" r="1.3" {DOT}/><circle cx="12" cy="16.5" r="1.3" {DOT}/>',
    "air": '<path d="M17.7 7.7a2.5 2.5 0 1 1 1.8 4.3H2"/><path d="M9.6 4.6A2 2 0 1 1 11 8H2"/><path d="M12.6 19.4A2 2 0 1 0 14 16H2"/>',
    "mandi": '<path d="M12 7.5c-1.5-1-4-1.2-5.5.4-2 2.1-1.6 6 .4 8.5 1.2 1.5 2.8 2.6 5.1 2.6s3.9-1.1 5.1-2.6c2-2.5 2.4-6.4.4-8.5-1.5-1.6-4-1.4-5.5-.4Z"/><path d="M12 7.5V5"/><path d="M12 5c1-1.6 2.6-2 4-1.5"/>',
    "train": f'<path d="M7 3h10a2 2 0 0 1 2 2v10a4 4 0 0 1-4 4H9a4 4 0 0 1-4-4V5a2 2 0 0 1 2-2Z"/><path d="M5 11h14"/><circle cx="9" cy="15" r="1" {DOT}/><circle cx="15" cy="15" r="1" {DOT}/><path d="m8.5 19-2 2.5M15.5 19l2 2.5"/>',
    "pin": '<path d="M12 21.5s7-6 7-11.5a7 7 0 1 0-14 0c0 5.5 7 11.5 7 11.5Z"/><circle cx="12" cy="10" r="2.6"/>',
    "sarkar": '<path d="M3 9.5 12 4l9 5.5H3Z"/><path d="M5.5 12.5v5M9.8 12.5v5M14.2 12.5v5M18.5 12.5v5"/><path d="M3.5 20.5h17"/>',
    "reality": '<path d="M4 20V9l4-2.5V20"/><path d="M8 20V4.5l5 2V20"/><path d="M13 20v-7l4-1.5V20"/><path d="M3 20.5h18"/><path d="M10 8.5h1M10 11.5h1M10 14.5h1"/>',
    "address": '<path d="M12 21.5s6.5-5.4 6.5-10.8a6.5 6.5 0 1 0-13 0c0 5.4 6.5 10.8 6.5 10.8Z"/><path d="M9.5 9.5h5M9.5 12h3"/>',
    "safebite": '<path d="M12 3 4.5 6v5.5c0 4.4 3 7.8 7.5 9.5 4.5-1.7 7.5-5.1 7.5-9.5V6L12 3Z"/><path d="M9 15.5V9.2M7.4 9.2v2a1.6 1.6 0 0 0 3.2 0v-2M15.2 15.5V9c-1.3.7-1.9 1.9-1.9 3.5h1.9"/>',
    "daru": '<path d="M9.5 2.5h5M10 2.5v4.2c0 1.2-2 2.2-2 4.3v9a1.5 1.5 0 0 0 1.5 1.5h5a1.5 1.5 0 0 0 1.5-1.5v-9c0-2.1-2-3.1-2-4.3V2.5"/><path d="M8 13h8"/><path d="M11 16.5h2"/>',
    "debunk": '<path d="M4 4.5h16v11H12l-4.5 4v-4H4v-11Z"/><path d="m9.5 8.5 5 4M14.5 8.5l-5 4"/>',
    "thaga": '<path d="M12 3 4.5 6v5.5c0 4.4 3 7.8 7.5 9.5 4.5-1.7 7.5-5.1 7.5-9.5V6L12 3Z"/><path d="m9 12 2.2 2.2L15.5 10"/>',
    "side": '<path d="m10.5 20.5-7-7a4.95 4.95 0 0 1 7-7l7 7a4.95 4.95 0 0 1-7 7Z"/><path d="m8.5 8.5 7 7"/>',
    "foodrx": '<path d="M6.5 3v7.5M3.5 3v5a3 3 0 0 0 6 0V3"/><path d="M6.5 11v10"/><path d="M17.5 21V3c-2.4 1.4-3.5 4-3.5 7.5h3.5"/>',
    "bytebriefs": '<path d="M13 2.5 4.5 13.5H11l-1 8 8.5-11H12l1-8Z"/>',
    "abstracted": '<path d="M14 3H7.5A2.5 2.5 0 0 0 5 5.5v13A2.5 2.5 0 0 0 7.5 21h9a2.5 2.5 0 0 0 2.5-2.5V8l-5-5Z"/><path d="M14 3v5h5"/><path d="M9 13h6M9 17h4"/>',
    "tharoor": '<path d="m5 20 7-16 7 16"/><path d="M7.8 14h8.4"/>',
    "synapse": '<circle cx="6" cy="7" r="2"/><circle cx="18" cy="6" r="2"/><circle cx="12" cy="12.5" r="2.4"/><circle cx="6" cy="18" r="2"/><circle cx="18" cy="17.5" r="2"/><path d="m7.6 8.3 2.6 2.7M16.6 7.6l-3 3.3M7.6 16.8l2.6-2.4M16.5 16.2l-2.4-2.2"/>',
    "altsurf": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18"/><path d="M16 8l3 4-3 4"/><path d="M8 16l-3-4 3-4"/>',
    "pulse": '<path d="M2.5 12H6l3-8 5 16 3-8h4.5"/>',
    "retro": '<path d="M3.5 12a8.5 8.5 0 1 0 2.6-6.1L3.5 8.5"/><path d="M3.5 3.5v5h5"/><path d="M12 7.5V12l3 2"/>',
    "gazette": '<path d="M5 21h14a2 2 0 0 0 2-2V5a2 2 0 0 0-2-2H9a2 2 0 0 0-2 2v14a2 2 0 0 1-2 2Zm0 0a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h2"/><path d="M11 7.5h7v4h-7z"/><path d="M11 15h7M11 18h4.5"/>',
    "prior": '<path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 0 0-3.6 10.8c.7.5 1.1 1.3 1.1 2.1v.1h5v-.1c0-.8.4-1.6 1.1-2.1A6 6 0 0 0 12 3Z"/>',
    "artifact": '<path d="M9 3h6"/><path d="M10 3v3.2C10 8 7 8.6 7 13c0 3.5 2.2 6 3 8h4c.8-2 3-4.5 3-8 0-4.4-3-5-3-6.8V3"/><path d="M7.5 12c-2 0-3 1-3 2.5s1.2 2 2.8 2M16.5 12c2 0 3 1 3 2.5s-1.2 2-2.8 2"/>',
    "compass": '<circle cx="12" cy="12" r="9"/><path d="m15.8 8.2-2 5.6-5.6 2 2-5.6 5.6-2Z"/>',
    "culinary": '<path d="M3.5 11.5h17a8.5 8.5 0 0 1-17 0Z"/><path d="M8 20.5h8"/><path d="M8.5 3.5c-1 1.4 1 2.4 0 4M12 3.5c-1 1.4 1 2.4 0 4M15.5 3.5c-1 1.4 1 2.4 0 4"/>',
    "ghost": f'<path d="M5.5 21V10a6.5 6.5 0 0 1 13 0v11l-2.2-2-2.1 2-2.2-2-2.2 2-2.1-2-2.2 2Z"/><circle cx="9.6" cy="10.5" r="1" {DOT}/><circle cx="14.4" cy="10.5" r="1" {DOT}/>',
    "wander": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18"/><path d="M12 3c3 2.6 4.5 5.6 4.5 9S15 18.4 12 21c-3-2.6-4.5-5.6-4.5-9S9 5.6 12 3Z"/>',
    "radio": f'<path d="M4.9 19.1a10 10 0 0 1 0-14.2"/><path d="M8 16a5.6 5.6 0 0 1 0-8"/><circle cx="12" cy="12" r="1.7" {DOT}/><path d="M16 8a5.6 5.6 0 0 1 0 8"/><path d="M19.1 4.9a10 10 0 0 1 0 14.2"/>',
    "ekayana": '<path d="M2.5 5.2C5 3.8 8.8 4 12 6c3.2-2 7-2.2 9.5-.8V19c-2.5-1.4-6.3-1.2-9.5.8-3.2-2-7-2.2-9.5-.8V5.2Z"/><path d="M12 6v13.8"/>',
    "blind": '<rect x="3.5" y="8" width="17" height="4" rx="1"/><path d="M5 12v8a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-8"/><path d="M12 8v13"/><path d="M12 8c-1.2-3.2-5-3.8-5-1.6C7 8 9.4 8 12 8Zm0 0c1.2-3.2 5-3.8 5-1.6C17 8 14.6 8 12 8Z"/>',
    "spoiler": '<path d="M3 3l18 18"/><path d="M10.6 5.2A9.6 9.6 0 0 1 12 5c6 0 9.5 7 9.5 7a15 15 0 0 1-2.9 3.7M6.6 6.7A15 15 0 0 0 2.5 12S6 19 12 19a9.4 9.4 0 0 0 4.2-1"/><path d="M9.9 9.9a3 3 0 0 0 4.2 4.2"/>',
    "flightdle": '<path d="M12 2.5c.9 0 1.6.9 1.6 2v5l7.9 4.6v2.1l-7.9-2.2v4.2l2.1 1.6v1.8L12 20.7l-3.6.9v-1.8l2.1-1.6v-4.2l-7.9 2.2v-2.1l7.9-4.6v-5c0-1.1.7-2 1.5-2Z"/>',
    "chroma": '<circle cx="9" cy="9.5" r="5.2"/><circle cx="15" cy="9.5" r="5.2"/><circle cx="12" cy="15" r="5.2"/>',
    "gauntlet": '<path d="M14.5 17.5 3 6V3h3l11.5 11.5"/><path d="m13 19 6-6"/><path d="m16 16 4 4"/><path d="m19 21 2-2"/><path d="M14.5 6.5 18 3h3v3l-3.5 3.5"/><path d="m5 14 4 4"/><path d="m7 17-3 3"/><path d="m3 19 2 2"/>',
    "tatkal": '<path d="M3.5 8.5a2 2 0 0 1 2-2h13a2 2 0 0 1 2 2v2a2 2 0 0 0 0 3.8v2.2a2 2 0 0 1-2 2h-13a2 2 0 0 1-2-2v-2.2a2 2 0 0 0 0-3.8v-2Z"/><path d="M14.5 7v1.5M14.5 11.2v1.6M14.5 15.5V17"/>',
    "chuckle": '<circle cx="12" cy="12" r="9"/><path d="M8 13.5a4.5 4.5 0 0 0 8 0Z"/><path d="M8.5 9.5h.01M15.5 9.5h.01"/>',
    "jargon": '<path d="M20.5 11.5a8 8 0 0 1-11.4 7.2L4 20l1.2-4.4A8 8 0 1 1 20.5 11.5Z"/><path d="M8.5 10.5h7M8.5 13.5h4"/>',
    "sip": '<path d="M3.5 20.5h17"/><path d="M5.5 17v-3.5M10 17V10.5M14.5 17v-5M19 17V6.5"/><path d="m5 8.5 4.5-3 4 2.5 5-4"/>',
    "pantry": '<path d="M5 9h14l-1.2 10.2a1.5 1.5 0 0 1-1.5 1.3H7.7a1.5 1.5 0 0 1-1.5-1.3L5 9Z"/><path d="M3.5 9h17"/><path d="M9 9c0-2.5 1.3-4.5 3-4.5S15 6.5 15 9"/>',
    "stargazer": '<path d="M12 3.5 14 9l5.5.5-4.2 3.6 1.3 5.4L12 15.6 7.4 18.5l1.3-5.4L4.5 9.5 10 9l2-5.5Z"/><path d="M19.5 3.5v3M18 5h3"/>',
    "faceoff": '<path d="M4 20V10M10 20V4M14 20V8M20 20V13"/><path d="M2.5 20.5h19"/>',
    "dossier": '<path d="M3.5 7.5a1.5 1.5 0 0 1 1.5-1.5h4l2 2h8a1.5 1.5 0 0 1 1.5 1.5v8.5a1.5 1.5 0 0 1-1.5 1.5H5A1.5 1.5 0 0 1 3.5 18V7.5Z"/><path d="M8 13h8M8 16h5"/>',
    "moodpoem": '<path d="M19.5 4.5c-7 0-12 4-12 10v3"/><path d="M19.5 4.5c0 6-4 10-10 10"/><path d="M7.5 17.5 5 21"/><path d="M11 10.5h4"/>',
    "auratunes": '<path d="M9 18V6l10-2v12"/><circle cx="6.5" cy="18" r="2.5"/><circle cx="16.5" cy="16" r="2.5"/>',
    "roast": '<path d="M12 21c-3.9 0-7-2.9-7-6.6 0-2.7 1.6-4.4 3-6 .9-1 1.4-2.2 1.4-3.9 2.5 1.2 4 3 4.3 5.2.7-.7 1.1-1.6 1.2-2.7 2.1 1.8 3.1 4.2 3.1 6.9 0 3.7-2.1 7.1-6 7.1Z"/><path d="M9.5 15.5a2.5 2.5 0 0 0 5 0"/>',
}

UI_ICONS = {
    "search": '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
    "x": '<path d="M6 6l12 12M18 6 6 18"/>',
    "star": '<path d="m12 3.2 2.7 5.5 6 .9-4.4 4.3 1 6L12 17l-5.4 2.9 1-6-4.4-4.3 6-.9L12 3.2Z"/>',
    "share": '<circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="M8.6 10.5 15.4 6.5M8.6 13.5l6.8 4"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    "moon": '<path d="M21 12.8A9 9 0 1 1 11.2 3 7 7 0 0 0 21 12.8Z"/>',
    "grid": '<rect x="3.5" y="3.5" width="7" height="7" rx="2"/><rect x="13.5" y="3.5" width="7" height="7" rx="2"/><rect x="3.5" y="13.5" width="7" height="7" rx="2"/><rect x="13.5" y="13.5" width="7" height="7" rx="2"/>',
    "shelf": '<path d="M6.5 3.5h11a1 1 0 0 1 1 1V21l-6.5-4.2L5.5 21V4.5a1 1 0 0 1 1-1Z"/>',
    "sliders": '<path d="M4 7h9M17 7h3M4 17h3M11 17h9"/><circle cx="15" cy="7" r="2"/><circle cx="9" cy="17" r="2"/>',
    "download": '<path d="M12 3v12"/><path d="m7 10 5 5 5-5"/><path d="M5 21h14"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m4 7 8 6 8-6"/>',
    "linkedin": f'<rect x="3" y="3" width="18" height="18" rx="3"/><path d="M7.5 10.5v6"/><circle cx="7.5" cy="7.5" r=".7" {DOT}/><path d="M11.5 16.5v-3.5a2 2 0 0 1 4 0v3.5"/><path d="M11.5 13v3.5"/>',
    "refresh": '<path d="M20 11a8 8 0 0 0-14.6-4.5L4 8"/><path d="M4 4v4h4"/><path d="M4 13a8 8 0 0 0 14.6 4.5L20 16"/><path d="M20 20v-4h-4"/>',
    "check": '<path d="m5 12.5 4.5 4.5L19 7.5"/>',
    "chevron": '<path d="m9 5 7 7-7 7"/>',
    "trash": '<path d="M4 7h16M10 11v6M14 11v6M6 7l1 13h10l1-13M9 7V4h6v3"/>',
    "reset": '<path d="M4 12a8 8 0 1 1 2.5 5.8"/><path d="M4 6v6h6"/>',
    "alert": '<path d="M12 3 2.5 20h19L12 3Z"/><path d="M12 10v4M12 17.4v.1"/>',
    "plus": '<path d="M12 5v14M5 12h14"/>',
}


def esc(s):
    return html.escape(s, quote=True)


def sprite():
    out = ['<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs>']
    for k, v in GLYPHS.items():
        out.append(f'<symbol id="g-{k}" viewBox="0 0 24 24">{v}</symbol>')
    for k, v in UI_ICONS.items():
        out.append(f'<symbol id="i-{k}" viewBox="0 0 24 24">{v}</symbol>')
    out.append("</defs></svg>")
    return "\n".join(out)


def ui(name, cls="ico"):
    return f'<svg class="{cls}" aria-hidden="true"><use href="#i-{name}"/></svg>'


OFFSETS = [-14, -7, 0, 7, 14, -10, 4]


def app_markup():
    cat_by_id = {c[0]: c for c in CATEGORIES}
    out = []
    idx = 0
    for cid, label, blurb, hue in CATEGORIES:
        out.append(
            f'<li class="group-head" data-cat="{cid}" data-i="{idx}">'
            f'<h2>{esc(label)}</h2><p>{esc(blurb)}</p></li>'
        )
        idx += 1
        n = 0
        for a in APPS:
            aid, name, cat, tag, desc, url, keys = a
            if cat != cid:
                continue
            off = OFFSETS[n % len(OFFSETS)]
            n += 1
            badge = ' <span class="badge-new">New</span>' if aid in NEW else ""
            out.append(
                f'<li class="app" data-id="{aid}" data-cat="{cid}" data-i="{idx}" '
                f'data-name="{esc(name)}" data-keys="{esc(keys)}" style="--o:{off}">\n'
                f'  <a class="app-link" href="{esc(url)}" target="_blank" rel="noopener">\n'
                f'    <span class="app-icon" aria-hidden="true"><svg class="glyph"><use href="#g-{aid}"/></svg></span>\n'
                f'    <span class="app-text">\n'
                f'      <span class="app-name">{esc(name)}{badge}</span>\n'
                f'      <span class="app-tag">{esc(tag)}</span>\n'
                f'      <span class="app-desc">{esc(desc)}</span>\n'
                f'    </span>\n'
                f'  </a>\n'
                f'  <button class="pin" type="button" data-id="{aid}" aria-pressed="false" aria-label="Pin {esc(name)}">{ui("star")}</button>\n'
                f'</li>'
            )
            idx += 1
    return "\n".join(out)


def tabs_markup():
    out = ['<button class="tab" type="button" role="tab" id="tab-all" data-tab="all" data-h="275" aria-selected="true">All</button>']
    for cid, label, blurb, hue in CATEGORIES:
        out.append(
            f'<button class="tab" type="button" role="tab" id="tab-{cid}" data-tab="{cid}" data-cat="{cid}" data-h="{hue}" aria-selected="false">'
            f'<span class="dot" aria-hidden="true"></span>{esc(label)}</button>'
        )
    return "\n        ".join(out)


def jsonld():
    cat_label = {c[0]: c[1] for c in CATEGORIES}
    items = []
    for i, a in enumerate(APPS, 1):
        aid, name, cat, tag, desc, url, keys = a
        items.append({
            "@type": "SoftwareApplication",
            "position": i,
            "name": name,
            "description": desc,
            "url": url,
            "applicationCategory": cat_label[cat],
            "operatingSystem": "Web",
        })
    data = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "The Shelf — small apps built by Suva",
        "url": SITE + "/",
        "description": "A growing shelf of small, single-purpose apps built by Suva.",
        "author": {"@type": "Person", "name": "Suva", "sameAs": "https://www.linkedin.com/in/suva"},
        "mainEntity": {"@type": "ItemList", "itemListElement": items},
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


def mailto(subject, body):
    from urllib.parse import quote
    return f"mailto:{FEEDBACK_TO}?subject={quote(subject)}&body={quote(body)}"


FEEDBACK_BODY = "Hi Suva,\r\n\r\nWhat I was trying to do:\r\n\r\n\r\nWhat happened, or what I'd change:\r\n\r\n"
BROKEN_BODY = "Hi Suva,\r\n\r\nWhich app is broken:\r\n\r\nWhat went wrong:\r\n\r\nWhat I expected:\r\n\r\n"
IDEA_BODY = "Hi Suva,\r\n\r\nMy app idea, in one line:\r\n\r\nWho it would help:\r\n\r\nWhy it would be useful:\r\n\r\n"


def build():
    n = len(APPS)
    page = TEMPLATE
    repl = {
        "{{COUNT}}": str(n),
        "{{SPRITE}}": sprite(),
        "{{TABS}}": tabs_markup(),
        "{{APPS}}": app_markup(),
        "{{JSONLD}}": jsonld(),
        "{{MAIL_FEEDBACK}}": esc(mailto("Feedback on The Shelf", FEEDBACK_BODY)),
        "{{MAIL_BROKEN}}": esc(mailto("Broken app on The Shelf", BROKEN_BODY)),
        "{{MAIL_IDEA}}": esc(mailto("App idea for The Shelf", IDEA_BODY)),
        "{{SITE}}": SITE,
    }
    for k, v in repl.items():
        page = page.replace(k, v)
    # inline UI icon helper: {{i:name}}
    import re
    page = re.sub(r"\{\{i:([a-z]+)\}\}", lambda m: ui(m.group(1)), page)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public", "index.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"wrote {out} ({n} apps, {len(page)//1024} KB)")


TEMPLATE = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "template.html"), encoding="utf-8").read()

if __name__ == "__main__":
    build()
