from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_article_view_exposes_cross_page_journey_links():
    source = (REPO_ROOT / "ka_article_view.html").read_text()
    assert "params.get('paper')" in source
    assert "article-primary-topic-link" in source
    assert "article-theory-link" in source
    assert "journey-link-mechanism" in source
    assert "from_article" in source
    assert "journeyHref('ka_topic_facet_view.html'" in source
    assert "journeyHref('ka_home_theory.html'" in source
    assert 'id="journey"' in source


def test_theory_topic_and_mechanism_pages_preserve_journey_context():
    theory_source = (REPO_ROOT / "ka_home_theory.html").read_text()
    theory_journey_source = (REPO_ROOT / "ka_journey_theory.html").read_text()
    topic_source = (REPO_ROOT / "ka_topic_facet_view.html").read_text()
    mechanism_source = (REPO_ROOT / "ka_journey_mechanism.html").read_text()

    assert "theory-topic-link" in theory_source
    assert "live-mechanism-journey-link" in theory_source
    assert "live-theory-journey-link" in theory_source
    assert "from_topic" in theory_source
    assert "from_article" in theory_source
    assert 'id="live-theory-handoff"' in theory_source
    assert 'id="j-theory-handoff"' in theory_journey_source
    assert 'id="j-theory-mechanism-link"' in theory_journey_source
    assert "params.get('from_topic')" in theory_journey_source
    assert "params.get('from_article')" in theory_journey_source
    assert 'id="__ka_topic_focus"' in topic_source
    assert 'id="__ka_topic_handoff"' in topic_source
    assert "params.get('topic')" in topic_source
    assert "params.get('from_article')" in topic_source
    assert 'id="j-mechanism-focus"' in mechanism_source
    assert 'id="j-mechanism-theory-journey-link"' in mechanism_source
    assert "params.get('theory')" in mechanism_source
    assert "params.get('from_topic')" in mechanism_source
    assert "params.get('from_article')" in mechanism_source
