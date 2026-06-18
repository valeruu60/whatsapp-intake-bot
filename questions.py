 
QUESTIONS = [
    {
        "key": "applicant_type",
        "prompt": "Welcome to FinAgra intake. \n\nLet's get started. What is your aplicant type?\n 1. Individual\n 2. Legal Entity",
        "type": "choice",
        "options": ["Individual", "Legal Entity"],
    },
    {
        "key": "legal_name",
        "prompt": "What is your "
                  "*full legal name*, exactly as it appears on official documents?",
        "type": "text",
    },
    {
        "key": "date_of_birth",
        "prompt": "Thanks! What is your *date of birth*? (Format: DD/MM/YYYY)",
        "type": "text",
    },
    {
        "key": "gender",
        "prompt": "Thanks! What is your *gender*?",
        "type": "text",
    },
    {
        "key": "preferred_language",
        "prompt": " Thanks! What is your *preferred language*?",
        "type": "text",
    },
    {
        "key": "email",
        "prompt": "What is your *email address*?",
        "type": "text",
    },
    {
        "key": "country_of_residence",
        "prompt": "What is your *country of residence*?",
        "type": "text",
    },
    {
        "key": "have_land",
        "prompt": "Do you have any land or property?\n\n1. I own land \n2. I lease land \n3. I intend to lease land \n4. I need help fidning land",
        "type": "choice",
        "options": ["I own land", "I lease land", "I intend to lease land", "I need help finding land"],
    },
    {
        "key": "farming_connection",
        "prompt": "How are you connected to farming?\n\n1. I run or manage a farm now \n2. Agribusiness \n3. I grew up farming \n4. I used to farm \n5. I studied agronomy \n5. No farming experience but interested in starting",
        "type": "choice",
        "options": ["I run or manage a farm now", "Agribusiness", "I grew up farming", "I used to farm", "I studied agronomy", "No farming experience but interested in starting"],
    },
    {
        "key": "property_address",
        "prompt": "What is the *full address* of the land or property in question?",
        "type": "text",
    },
    {
        "key": "parcel_number",
        "prompt": "What is the *land parcel / plot number*? (If you don't know it, "
                  "type 'unknown'.)",
        "type": "text",
    },
    {
        "key": "rate_profeciency_wa",
        "prompt": "On a scale of 1-5, how would you rate your proficiency with WhatsApp? (1 = not at all comfortable, 5 = very comfortable)",
        "type": "choice",
        "options": ["1", "2", "3", "4", "5"],
    },
    {
        "key": "rate_profeciency_email",
        "prompt": "On a scale of 1-5, how would you rate your proficiency with email? (1 = not at all comfortable, 5 = very comfortable)",
        "type": "choice",
        "options": ["1", "2", "3", "4", "5"],
    },
    {
        "key": "rate_profeciency_facebook_youtube",
        "prompt": "On a scale of 1-5, how would you rate your proficiency with Facebook and YouTube? (1 = not at all comfortable, 5 = very comfortable)",
        "type": "choice",
        "options": ["1", "2", "3", "4", "5"],
    },
    {
        "key": "rate_profeciency_m_pesa",
        "prompt": "On a scale of 1-5, how would you rate your proficiency with M-Pesa? (1 = not at all comfortable, 5 = very comfortable)",
        "type": "choice",
        "options": ["1", "2", "3", "4", "5"],
    },
    {
        "key": "rate_profeciency_excel_google_sheets",
        "prompt": "On a scale of 1-5, how would you rate your proficiency with Excel and Google Sheets? (1 = not at all comfortable, 5 = very comfortable)",
        "type": "choice",
        "options": ["1", "2", "3", "4", "5"],
    },
    {
        "key": "id_number",
        "prompt": "What is your *national ID or passport number*?",
        "type": "text",
    },
    {
        "key": "id_document",
        "prompt": "Now please *upload a photo of your government-issued ID*.",
        "type": "file",
    },
    {
        "key": "time",
        "prompt": "How much time can you give to REP activities?\n\n1. Full-time \n2. Part-time moving to full-time\n3. Part-time long-term\n4. I'll decide later",
        "type": "choice",
        "options": ["Full-time", "Part-time moving to full-time", "Part-time long-term", "I'll decide later"],
    },
    {
        "key": "notes",
        "prompt": "Almost done. Anything else we should know? "
                  "(Type 'none' if there's nothing to add.)",
        "type": "text",
    },
]