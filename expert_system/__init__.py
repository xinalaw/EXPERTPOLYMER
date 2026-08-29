"""
Экспертная система анализа морфологии частиц полимерных порошков
для оценки пригодности к аддитивному производству.

Публичный интерфейс пакета:

    from expert_system import Analyzer
    analyzer = Analyzer()
    result = analyzer.analyze("path/to/sem_image.png")

Импорты ленивые (PEP 562): тяжёлые зависимости (ultralytics, opencv)
загружаются только при реальном обращении к Analyzer / YOLODetector,
поэтому, например, fuzzy_expert можно использовать и тестировать отдельно.
"""
from . import config

__all__ = ["Analyzer", "YOLODetector", "FuzzyExpert",
           "config", "metrics", "storage", "visualization"]

__version__ = "1.0.0"

_LAZY = {
    "Analyzer":     ("expert_system.analyzer", "Analyzer"),
    "YOLODetector": ("expert_system.detector", "YOLODetector"),
    "FuzzyExpert":  ("expert_system.fuzzy_expert", "FuzzyExpert"),
    "metrics":       ("expert_system.metrics", None),
    "storage":       ("expert_system.storage", None),
    "visualization": ("expert_system.visualization", None),
}


def __getattr__(name):
    if name in _LAZY:
        import importlib
        module_name, attr = _LAZY[name]
        module = importlib.import_module(module_name)
        value = module if attr is None else getattr(module, attr)
        globals()[name] = value
        return value
    raise AttributeError(f"module 'expert_system' has no attribute {name!r}")
