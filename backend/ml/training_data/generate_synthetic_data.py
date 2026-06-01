import os
import random
import csv
from datetime import datetime, timedelta

# Define paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
TRAINING_DATA_PATH = os.path.join(CURRENT_DIR, 'training-data.csv')

# Users from the actual codebase/database context
USERS = [
    "Rahul Pardasani",
    "Siddharth Shukla",
    "Dingal",
    "saumya bansal",
    "Raina",
    "Aditi Singh",
    "Suhani Gupta",
    "Ronak Khemka",
    "Rohil Chaturvedi",
    "Prajwal sharma"
]

# Vocabulary lists for randomization in templates
RESTAURANTS = ["McD", "KFC", "Burger King", "Starbucks", "Haldirams", "Bercos", "Dominos", "Pizza Hut", "Chai Point", "Waffle House", "Subway"]
LOCATIONS = ["college", "campus", "airport", "railway station", "metro station", "CP", "mall", "market", "office", "home", "library"]
SUBJECTS = ["Semester 4", "DSA", "DBMS", "OS", "Machine Learning", "Web Dev", "Physics", "Maths", "Chemistry", "Lab Manual", "Minor Project"]

# Category templates for realistic synthetics
TEMPLATES = {
    "food": [
        "Swiggy order from {restaurant}",
        "Zomato delivery {restaurant}",
        "Dinner at {restaurant} with friends",
        "Lunch with group at {restaurant}",
        "McD burger and fries",
        "KFC chicken bucket",
        "Dominos pizza party",
        "Starbucks cold brew coffee",
        "Chai and samosa at canteen",
        "Breakfast at college canteen",
        "Lunch box shared with friends",
        "Haldirams chole bhature",
        "Waffles at CP",
        "Maggi and cold drink evening",
        "Ice cream scoop desert",
        "Chaat papdi street food",
        "Chicken biryani pack",
        "Burger King meal prep",
        "Tasty momos near college gate",
        "Dosa and filter coffee morning",
        "Snacks and chips for study session",
        "Tea stall chai sutta",
        "Groceries at Reliance Fresh",
        "Fruit juice and shakes",
        "Late night pizza delivery",
        "Shawarma roll evening",
        "Coffee and cookies starbucks",
        "Sandwich and fruit pack",
        "Coke and chips party",
        "Samosa chai party canteen"
    ],
    "transportation": [
        "Uber ride to {location}",
        "Ola cab from {location}",
        "Auto fare to {location}",
        "Cab commute to college campus",
        "Metro smartcard online recharge",
        "Petrol for scooty",
        "Bus ticket to city center",
        "Parking charges at Mall",
        "Train ticket reservation home",
        "Flight ticket booking holidays",
        "Morning auto fare college",
        "Evening cab surge price",
        "Rapido bike ride campus",
        "Toll plaza payment national highway",
        "Uber auto daily commute",
        "Ola auto to metro station",
        "Cab fare back home",
        "Ride share petrol cost split",
        "Cab 26 evening ride",
        "Auto 18 morning commute",
        "Uber discount ride",
        "Weekly cab expenses",
        "Airport taxi pickup",
        "Bus pass monthly",
        "Ola bike evening commute",
        "Tuk tuk fare station",
        "Metro ticket ride",
        "Cab to railway station"
    ],
    "education": [
        "Exam printouts for finals",
        "Photocopy notes from library",
        "Textbook for {subject} course",
        "Udemy course subscription for {subject}",
        "Lab manual prints and binding",
        "Stationery notebook and pens",
        "Xerox copy of assignment sheets",
        "Minor project report print",
        "Coursera specialization monthly fee",
        "Spiral binding lab report",
        "Research paper printout for seminar",
        "Notebooks and files for class",
        "Scientific calculator for exam",
        "Academic book purchase",
        "Drawing board and sheets lab",
        "Engineering graphics prints",
        "Coding bootcamp course fee",
        "Tutorial notes copy shop",
        "Exam fees university portal",
        "Reference book DBMS and OS",
        "Python programming print notes",
        "Maths textbook photocopy",
        "Assignment prints urgent",
        "Library membership fine payment"
    ],
    "entertainment": [
        "Movie ticket bookmyshow cinema",
        "Netflix subscription share monthly",
        "Spotify premium family plan",
        "Concert entry tickets live show",
        "Bowling alley games Smaash",
        "Arcade games tickets play zone",
        "Club entry fee weekend drinks",
        "Party contribution drinks and snacks",
        "Gaming zone entry ticket",
        "Theme park ticket amusement ride",
        "Museum exhibition entry ticket",
        "Pub night with group friends",
        "Drinks and food lounge bar",
        "Standup comedy show tickets",
        "Concert pass music festival",
        "Bowling game bowling lane",
        "Billiard table hourly rent",
        "Laser tag gaming session",
        "House party drinks beer",
        "IPL match tickets stadium",
        "PlayStation arcade gaming lounge",
        "Weekend getaway entry fee",
        "DJ night entry ticket",
        "Ice skating entry tickets"
    ],
    "payment": [
        "Settled balance on Splitwise app",
        "Paid back for food and dinner",
        "Transfer to account cleared",
        "Repay debt cleared friend",
        "Payment to roommate split",
        "Cleared dues Splitwise settlement",
        "Repayment for cab share",
        "Sent money via Paytm wallet",
        "Settle all remaining balances",
        "Paid back emergency cash borrow",
        "Splitwise settlement payment transfer",
        "Balance settlement cleared out",
        "Room rent payment settlement",
        "Paid back for grocery contribution",
        "Cleared all pending debts Splitwise",
        "Settle balance for movie ticket",
        "Sent back borrowed money cash",
        "UPI payment settlement to friend"
    ],
    "miscellaneous": [
        "Laundry washing and ironing bill",
        "Medicines from Apollo pharmacy",
        "Haircut salon charges barber shop",
        "Mobile phone prepaid recharge",
        "WiFi internet monthly broadband bill",
        "Room rent share utility bills",
        "Birthday gift for friend party",
        "Cough syrup and cold medicines",
        "Toiletries shampoo soap face wash",
        "Gym membership monthly fee",
        "Amazon delivery package online buy",
        "Supermarket home supplies groceries",
        "Dentist doctor consultation clinic",
        "Electricity bill share apartment",
        "Shoe repair and polish",
        "Water bottle set room",
        "Earphones replacement purchase",
        "Room keys duplication lock",
        "Room cleaning supplies sweep",
        "Gifts for parents family trip"
    ]
}

# Real-world noisy abbreviations & shorthands
SHORTHANDS = {
    "payment": ["pymt", "pd", "setl", "pmt"],
    "settled": ["setld", "stl", "cleared"],
    "balance": ["bal", "blnc"],
    "transportation": ["tpt", "commute", "ride", "cab"],
    "canteen": ["cntn", "mess", "stall"],
    "breakfast": ["bfast", "snack"],
    "dinner": ["dnr", "food"],
    "lunch": ["lnch"],
    "netflix": ["netflx", "ntflx"],
    "spotify": ["sptfy", "spot"],
    "movie": ["mov", "tkt"],
    "ticket": ["tkt", "pass"],
    "concert": ["gig", "show"],
    "stationery": ["stat", "book"],
    "notebook": ["ntbk", "copy"],
    "photocopy": ["xerox", "photo", "prnt"],
    "printouts": ["prints", "prnt"],
    "project": ["proj"],
    "medicine": ["meds", "med"],
    "pharmacy": ["apollo", "med"],
    "recharge": ["rchrg"],
    "internet": ["wifi", "net"],
    "laundry": ["wash", "ldry"],
    "friend": ["frnd", "dude"],
    "group": ["grp"]
}

# Ambiguous cross-category samples (intentionally confusing — these mix keywords from multiple categories)
AMBIGUOUS_SAMPLES = {
    "food": [
        "cab to restaurant dinner",
        "canteen lunch notes prints",
        "paid back for swiggy delivery",
        "movie night popcorn and nachos",
        "uber eats delivery charges",
        "party snacks and drinks contribution",
        "paid for dinner and cab back",
        "settlement for last night food",
        "grocery delivery amazon fresh",
        "recharge coupon for zomato pro",
        "gym protein shake canteen",
        "office lunch split with team",
        "birthday cake and party food",
        "drinks and snacks at pub",
        "netflix and chill pizza order",
        "cab fare included in dinner bill",
        "chai sutta break campus",
    ],
    "transportation": [
        "cab ride to movie hall",
        "Uber ride to zomato dinner",
        "paying for auto to college",
        "flight ticket to project presentation",
        "metro recharge card top up",
        "petrol bill and snacks on highway",
        "cab to pharmacy emergency",
        "auto to laundry and back",
        "uber to concert venue entry",
        "ola ride splitwise settlement",
        "parking charges restaurant visit",
        "bus ticket for exam center",
        "cab charge for birthday party",
        "rapido to print shop xerox",
        "fuel share road trip weekend",
        "flight booking for family gift trip",
    ],
    "education": [
        "canteen printout copy sheets",
        "stationary shop paytm bill",
        "metro card xerox notes",
        "bought project reference book",
        "amazon book delivery for course",
        "paid for lab manual binding",
        "uber to exam center fare",
        "netflix documentary subscription study",
        "canteen break study session snacks",
        "print shop near restaurant",
        "exam prep food and coffee",
        "coursera subscription payment monthly",
        "library fine and canteen tea",
        "coding bootcamp party celebration",
        "cab to bookshop for textbook",
    ],
    "entertainment": [
        "netflix payment settlement",
        "drinks and pub cab charge",
        "movie snacks booking show",
        "concert ticket print copy",
        "party food and drinks bill",
        "spotify paid subscription renew",
        "arcade gaming and pizza",
        "bowling and dinner combo deal",
        "club entry and cab back",
        "movie night food delivery",
        "IPL snacks and drinks",
        "pub night cab fare home",
        "gaming zone recharge card",
        "house party groceries and decorations",
        "dj night uber ride",
        "standup show dinner afterwards",
    ],
    "payment": [
        "laundry bill payment",
        "repayment of canteen dinner tab",
        "settled movie ticket balance",
        "transfer to room rent landlord",
        "paid back uber cab share",
        "cleared grocery delivery balance",
        "settle entertainment expenses splitwise",
        "upi transfer for printing bill",
        "paytm to friend for food",
        "repay borrowed cash for medicine",
        "settled all dues and balances",
        "payment for netflix subscription share",
        "transfer rent and electricity bill",
        "cash back for concert tickets",
        "splitwise balance food and cab",
    ],
    "miscellaneous": [
        "paid for laundry services",
        "swiggy delivery medicines order",
        "cab fare to dentist clinic",
        "gift for friend birthday party",
        "amazon order phone cover charger",
        "salon haircut and snacks after",
        "pharmacy medicine delivery uber",
        "wifi bill recharge paytm",
        "gym membership renewal payment",
        "doctor visit and cab fare",
        "electricity bill splitwise settlement",
        "shoe repair near restaurant",
        "room cleaning supplies amazon",
        "birthday gift delivery cab",
        "mobile recharge and food court",
    ]
}

# Lazy, ultra-short vague words (many overlap across categories intentionally)
VAGUE_WORDS = {
    "food": ["lunch", "dinner", "canteen", "snacks", "swiggy", "zomato", "cafe", "chai", "momos", "pizza",
             "burger", "mcd", "waffle", "grocery", "khana", "nashta", "thali", "biryani", "roll", "maggi",
             "coffee", "juice", "shake", "dosa", "paratha", "noodles", "sandwich"],
    "transportation": ["cab", "auto", "metro", "ride", "uber", "ola", "petrol", "fuel", "rapido", "bike",
                        "taxi", "bus", "train", "flight", "commute", "fare", "stn", "toll", "parking"],
    "education": ["print", "xerox", "notes", "copy", "book", "lab", "stationary", "udemy", "exam",
                  "assignment", "report", "spiral", "binding", "coursera", "textbook", "project", "seminar"],
    "entertainment": ["movie", "netflix", "spotify", "concert", "drinks", "party", "arcade", "bowling",
                      "club", "pub", "game", "tkt", "show", "ipl", "stadium", "comedy", "dj", "outing"],
    "payment": ["paid", "settle", "splitwise", "paytm", "upi", "transfer", "cash", "repay", "debt",
                "dues", "repayment", "cleared", "sent", "received", "balance", "settlement"],
    "miscellaneous": ["laundry", "medicine", "recharge", "rent", "gift", "wifi", "bill", "salon", "barber",
                      "haircut", "doctor", "amazon", "flipkart", "charger", "earphones", "gym", "cleaning"]
}

# Generic filler entries with almost no category signal (these are really hard to classify)
GENERIC_FILLERS = [
    "stuff", "things", "misc", "random", "idk", "yesterday", "last week",
    "today morning", "evening thing", "usual", "same as before", "regular",
    "monthly", "weekly", "daily", "shared", "split", "contrib", "personal",
    "urgent", "emergency", "forgot name", "check later", "ask rahul", "see msg",
    "from last time", "pending", "old one", "new one", "extra", "remaining"
]

def introduce_typos(text, probability=0.10):
    """Introduce realistic typing errors like character swaps, omissions, or duplications."""
    words = text.split()
    new_words = []
    for word in words:
        if len(word) > 3 and random.random() < probability:
            typo_type = random.choice(['swap', 'drop', 'duplicate'])
            idx = random.randint(1, len(word) - 2)
            if typo_type == 'swap':
                word_list = list(word)
                word_list[idx], word_list[idx+1] = word_list[idx+1], word_list[idx]
                word = "".join(word_list)
            elif typo_type == 'drop':
                word = word[:idx] + word[idx+1:]
            elif typo_type == 'duplicate':
                word = word[:idx] + word[idx] + word[idx:]
        new_words.append(word)
    return " ".join(new_words)

def apply_shorthand(text, probability=0.15):
    """Map standard words to chat/SMS abbreviations with a set probability."""
    words = text.split()
    new_words = []
    for word in words:
        low_word = word.lower()
        if low_word in SHORTHANDS and random.random() < probability:
            sh = random.choice(SHORTHANDS[low_word])
            if word[0].isupper():
                sh = sh.capitalize()
            word = sh
        new_words.append(word)
    return " ".join(new_words)

def apply_formatting(text):
    """Add irregular punctuation, case variance, and trailing symbols."""
    r = random.random()
    if r < 0.08:
        text = text.upper()
    elif r < 0.18:
        text = text.lower()
        
    # 15% chance of irregular trailing symbols
    if random.random() < 0.15:
        punc = random.choice(["...", "??", "!!", "!!?", ".", " - split", ",,,"])
        text += punc
        
    # 5% chance of double spacing
    if random.random() < 0.05:
        text = "  " + text
        
    return text

def generate_messy_description(category):
    """Generate a messy description using a mixture of templates, vagueness, cross-category noise, and formatting filters."""
    rand_val = random.random()
    
    if rand_val < 0.18:
        # 1. 18% chance of ambiguous cross-category overlap
        description = random.choice(AMBIGUOUS_SAMPLES[category])
    elif rand_val < 0.32:
        # 2. 14% chance of an ultra-short lazy entry
        description = random.choice(VAGUE_WORDS[category])
        if random.random() < 0.50:
            description += f" {random.choice(['eve', 'morn', 'tues', 'bill', 'share', '12', 'wed', 'fri', 'sat'])}"
    elif rand_val < 0.38:
        # 3. 6% chance of a completely generic filler with almost no signal
        description = random.choice(GENERIC_FILLERS)
    else:
        # 4. 62% chance of a standard template with random slots
        template = random.choice(TEMPLATES[category])
        description = template.format(
            restaurant=random.choice(RESTAURANTS),
            location=random.choice(LOCATIONS),
            subject=random.choice(SUBJECTS)
        )
        
    # Run through the noise pipeline
    description = apply_shorthand(description)
    description = introduce_typos(description)
    description = apply_formatting(description)
    
    # Strip double whitespaces just to keep CSV format friendly
    return " ".join(description.split())

def generate_random_date():
    """Generate a random ISO date between 2023 and 2025."""
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2025, 6, 1)
    time_diff = end_date - start_date
    random_days = random.randint(0, time_diff.days)
    random_hours = random.randint(0, 23)
    random_minutes = random.randint(0, 59)
    random_seconds = random.randint(0, 59)
    res_date = start_date + timedelta(days=random_days, hours=random_hours, minutes=random_minutes, seconds=random_seconds)
    return res_date.strftime("%Y-%m-%dT%H:%M:%SZ")

def generate_cost(category):
    """Generate a realistic price (in INR) based on category."""
    if category == "food":
        return round(random.uniform(20.0, 1500.0), 2)
    elif category == "transportation":
        return round(random.uniform(30.0, 450.0), 2)
    elif category == "education":
        return round(random.uniform(10.0, 550.0), 2)
    elif category == "entertainment":
        return round(random.uniform(100.0, 3000.0), 2)
    elif category == "payment":
        return round(random.uniform(50.0, 3500.0), 2)
    elif category == "miscellaneous":
        return round(random.uniform(25.0, 1800.0), 2)
    return round(random.uniform(40.0, 900.0), 2)

def main():
    # Load existing training data
    existing_records = []
    existing_ids = set()
    category_counts = {}
    
    if os.path.exists(TRAINING_DATA_PATH):
        with open(TRAINING_DATA_PATH, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_records.append(row)
                existing_ids.add(row['Expense ID'])
                cat = row['expense_type']
                category_counts[cat] = category_counts.get(cat, 0) + 1
    
    print(f"Loaded {len(existing_records)} existing records from training-data.csv")
    print(f"Current Category Counts: {category_counts}")
    
    # We want exactly 835 samples for each category (total 5010)
    TARGET_PER_CATEGORY = 835
    synthetic_records_added = 0
    
    # Clear out previous synthetic data to start fresh and avoid stacking
    # We only keep the original 124 records (their IDs are < 3180000000)
    original_records = [r for r in existing_records if int(r['Expense ID']) < 3180000000]
    original_ids = {r['Expense ID'] for r in original_records}
    
    # Recalculate base counts
    base_counts = {}
    for r in original_records:
        cat = r['expense_type']
        base_counts[cat] = base_counts.get(cat, 0) + 1
        
    print(f"Base Original records to preserve: {len(original_records)}")
    print(f"Original Category Counts: {base_counts}")
    
    final_dataset = list(original_records)
    
    for category in TEMPLATES.keys():
        current_count = base_counts.get(category, 0)
        needed = TARGET_PER_CATEGORY - current_count
        
        if needed <= 0:
            continue
            
        print(f"Generating {needed} messy, realistic synthetic samples for '{category}'...")
        
        for _ in range(needed):
            # Generate unique 10-digit Expense ID (starting with 328 to mark messy synthetic data)
            while True:
                expense_id = str(random.randint(3280000000, 3289999999))
                if expense_id not in original_ids:
                    original_ids.add(expense_id)
                    break
            
            description = generate_messy_description(category)
            cost = str(generate_cost(category))
            currency = "INR" if random.random() < 0.95 else "USD"
            date_str = generate_random_date()
            created_by = random.choice(USERS)
            
            new_row = {
                'Expense ID': expense_id,
                'Description': description,
                'Cost': cost,
                'Currency Code': currency,
                'Date': date_str,
                'Created By': created_by,
                'expense_type': category
            }
            final_dataset.append(new_row)
            synthetic_records_added += 1

    # Shuffle records so synthetic data is mixed naturally with original data
    random.shuffle(final_dataset)
    
    # Save the expanded dataset back to training-data.csv
    with open(TRAINING_DATA_PATH, mode='w', newline='', encoding='utf-8') as f:
        fieldnames = ['Expense ID', 'Description', 'Cost', 'Currency Code', 'Date', 'Created By', 'expense_type']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in final_dataset:
            writer.writerow(row)
            
    print(f"Successfully generated {synthetic_records_added} messy synthetic records.")
    print(f"Total records in augmented dataset: {len(final_dataset)}")
    
    # Print new category distributions
    new_counts = {}
    for row in final_dataset:
        cat = row['expense_type']
        new_counts[cat] = new_counts.get(cat, 0) + 1
    print(f"New Category Counts: {new_counts}")

if __name__ == '__main__':
    main()
