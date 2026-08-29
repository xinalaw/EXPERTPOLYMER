"""Модульные тесты нечёткой экспертной подсистемы (fuzzy_expert.py)."""
import pytest

from expert_system.fuzzy_expert import FuzzyExpert


@pytest.fixture(scope="module")
def expert():
    return FuzzyExpert()


class TestFuzzyExpert:
    def test_ideal_powder_is_suitable(self, expert):
        result = expert.evaluate(sphericity=0.95, smoothness=0.95,
                                 uniformity=0.95)
        assert result["verdict"] == "suitable"
        assert result["score"] >= 70

    def test_bad_powder_is_unsuitable(self, expert):
        result = expert.evaluate(sphericity=0.1, smoothness=0.1,
                                 uniformity=0.1)
        assert result["verdict"] == "unsuitable"
        assert result["score"] < 40

    def test_medium_powder_is_conditional(self, expert):
        result = expert.evaluate(sphericity=0.5, smoothness=0.5,
                                 uniformity=0.5)
        assert result["verdict"] == "conditional"

    def test_low_sphericity_alone_degrades_verdict(self, expert):
        result = expert.evaluate(sphericity=0.05, smoothness=0.9,
                                 uniformity=0.9)
        assert result["verdict"] in ("unsuitable", "conditional")

    def test_score_in_valid_range(self, expert):
        for s in (0.0, 0.3, 0.6, 1.0):
            result = expert.evaluate(s, s, s)
            assert 0 <= result["score"] <= 100

    def test_inputs_echoed_back(self, expert):
        result = expert.evaluate(0.7, 0.8, 0.9)
        assert result["inputs"]["sphericity"] == 0.7
        assert result["inputs"]["smoothness"] == 0.8
        assert result["inputs"]["uniformity"] == 0.9

    def test_monotonicity(self, expert):
        """Лучшие входы не должны давать худшую оценку."""
        low = expert.evaluate(0.3, 0.3, 0.3)["score"]
        high = expert.evaluate(0.9, 0.9, 0.9)["score"]
        assert high > low
