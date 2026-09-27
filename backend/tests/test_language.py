from app.services.language_detector import detect_language


def test_detect_english():
    text = "Global temperatures reach new record according to meteorological researchers."
    res = detect_language(text)
    assert res["language"] == "English"
    assert res["iso_code"] == "en"


def test_detect_tamil():
    text = "தமிழ்நாடு அரசு புதிய கல்வி கொள்கை குறித்த அறிவிப்பை வெளியிட்டுள்ளது."
    res = detect_language(text)
    assert res["language"] == "Tamil"
    assert res["iso_code"] == "ta"


def test_detect_hindi():
    text = "भारतीय अंतरिक्ष अनुसंधान संगठन ने एक नया उपग्रह सफलतापूर्वक प्रक्षेपित किया।"
    res = detect_language(text)
    assert res["language"] == "Hindi"
    assert res["iso_code"] == "hi"
