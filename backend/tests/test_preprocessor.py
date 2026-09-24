from backend.app.services.preprocessor import preprocess_news_text


def test_clean_text_normal():
    sample = "The Ministry of Health announced new vaccination guidelines on Monday."
    res = preprocess_news_text(sample)
    assert res["word_count"] == 10
    assert res["sensational_score"] == 0
    assert len(res["flags"]) == 0


def test_sensational_buzzwords_detected():
    sample = "SHOCKING SECRET TRUTH! SHARE BEFORE IT GETS DELETED! MIRACLE CURE REVEALED!!!"
    res = preprocess_news_text(sample)
    assert res["sensational_score"] > 40
    assert len(res["flags"]) >= 2
