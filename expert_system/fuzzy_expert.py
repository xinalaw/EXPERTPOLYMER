"""
Нечёткая экспертная подсистема (Mamdani) для оценки пригодности порошка
к аддитивному производству.

Входные лингвистические переменные (универс [0, 1]):
    sphericity — доля сферических частиц в составе;
    smoothness — средняя округлость частиц;
    uniformity — однородность размеров (1 − дисперсность).

Выходная переменная suitability — пригодность, [0, 100].
Дефаззификация — методом центра тяжести (по умолчанию в scikit-fuzzy).
"""
from __future__ import annotations

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

from . import config


class FuzzyExpert:
    """Нечёткая система вывода для итоговой оценки порошка."""

    def __init__(self):
        self._build_system()

    def _build_system(self):
        # Входные переменные
        sphericity = ctrl.Antecedent(np.arange(0, 1.01, 0.01), "sphericity")
        smoothness = ctrl.Antecedent(np.arange(0, 1.01, 0.01), "smoothness")
        uniformity = ctrl.Antecedent(np.arange(0, 1.01, 0.01), "uniformity")

        # Выходная переменная
        suitability = ctrl.Consequent(np.arange(0, 101, 1), "suitability")

        # Функции принадлежности — входные (треугольные)
        for var in (sphericity, smoothness, uniformity):
            var["low"]    = fuzz.trimf(var.universe, [0,    0,   0.5])
            var["medium"] = fuzz.trimf(var.universe, [0.25, 0.5, 0.75])
            var["high"]   = fuzz.trimf(var.universe, [0.5,  1.0, 1.0])

        # Функции принадлежности — выходные
        suitability["poor"]       = fuzz.trimf(suitability.universe, [0,  0,   40])
        suitability["acceptable"] = fuzz.trimf(suitability.universe, [20, 50,  75])
        suitability["good"]       = fuzz.trimf(suitability.universe, [60, 100, 100])

        # База правил
        rules = [
            # Благоприятные сценарии
            ctrl.Rule(sphericity["high"] & smoothness["high"] & uniformity["high"],
                      suitability["good"]),
            ctrl.Rule(sphericity["high"] & smoothness["high"] & uniformity["medium"],
                      suitability["good"]),
            ctrl.Rule(sphericity["high"] & smoothness["medium"] & uniformity["high"],
                      suitability["acceptable"]),
            ctrl.Rule(sphericity["medium"] & smoothness["medium"] & uniformity["medium"],
                      suitability["acceptable"]),
            ctrl.Rule(sphericity["high"] & smoothness["medium"] & uniformity["medium"],
                      suitability["acceptable"]),
            # Неблагоприятные сценарии
            ctrl.Rule(sphericity["low"], suitability["poor"]),
            ctrl.Rule(smoothness["low"], suitability["poor"]),
            ctrl.Rule(uniformity["low"], suitability["poor"]),
            ctrl.Rule(sphericity["low"] & uniformity["low"], suitability["poor"]),
        ]

        system = ctrl.ControlSystem(rules)
        self.simulation = ctrl.ControlSystemSimulation(system)

    def evaluate(self, sphericity: float, smoothness: float,
                 uniformity: float) -> dict:
        """
        Нечёткий вывод по трём входным показателям (каждый в [0, 1]).

        Возвращает оценку score (0–100), вердикт и текстовое заключение.
        """
        self.simulation.input["sphericity"] = float(np.clip(sphericity, 0.01, 0.99))
        self.simulation.input["smoothness"] = float(np.clip(smoothness, 0.01, 0.99))
        self.simulation.input["uniformity"] = float(np.clip(uniformity, 0.01, 0.99))
        self.simulation.compute()

        score = float(self.simulation.output["suitability"])

        if score >= config.SCORE_SUITABLE:
            verdict, conclusion = "suitable", (
                "Материал пригоден для аддитивного производства")
        elif score >= config.SCORE_CONDITIONAL:
            verdict, conclusion = "conditional", (
                "Материал условно пригоден, требует дополнительной обработки")
        else:
            verdict, conclusion = "unsuitable", (
                "Материал не пригоден для аддитивного производства")

        return {
            "score": round(score, 2),
            "verdict": verdict,
            "conclusion": conclusion,
            "inputs": {
                "sphericity": round(sphericity, 3),
                "smoothness": round(smoothness, 3),
                "uniformity": round(uniformity, 3),
            },
        }
