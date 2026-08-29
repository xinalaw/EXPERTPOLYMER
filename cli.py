"""
Точка входа: анализ СЭМ-изображений из командной строки.

Примеры запуска:
    python main.py data/images/spherical/img_001.png
    python main.py img.png --boxes --masks          # с визуализациями
    python main.py img.png --json result.json       # сохранить JSON
    python main.py data/images/spherical/           # вся папка
    python main.py img.png --no-db                  # без записи в БД
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from expert_system import Analyzer, config, storage, visualization


def print_report(image_path: Path, result: dict) -> None:
    """Печатает человекочитаемый отчёт по одному изображению."""
    print(f"\n{'=' * 60}")
    print(f"Изображение: {image_path}")
    print("=" * 60)

    if "error" in result:
        print(f"  {result['error']}")
        return

    print(f"Всего частиц: {result['total_particles']}")

    print("\nСостав порошка:")
    for cls, pct in sorted(result["composition"].items(),
                           key=lambda kv: -kv[1]):
        bar = "█" * int(pct / 2.5)
        print(f"  {cls:<12} {pct:5.1f}%  {bar}")

    print(f"\nСредняя округлость: {result['avg_circularity']}")
    print(f"Дисперсность:       {result['dispersity']}")

    s = result["size_stats"]
    print(f"Размеры, px:        min {s['min_px']}, max {s['max_px']}, "
          f"mean {s['mean_px']} ± {s['std_px']}")

    e = result["expert"]
    print(f"\n--- Заключение экспертной системы ---")
    print(f"Оценка пригодности: {e['score']} / 100")
    print(f"Вердикт:            {e['verdict']}")
    print(f"Заключение:         {e['conclusion']}")


def collect_images(path: Path) -> list[Path]:
    """Файл -> [файл]; папка -> все изображения в ней (рекурсивно)."""
    if path.is_file():
        return [path]
    if path.is_dir():
        return sorted(p for p in path.rglob("*")
                      if p.suffix.lower() in config.IMAGE_EXTENSIONS)
    return []


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Экспертная система анализа частиц полимерных порошков")
    parser.add_argument("path", type=Path,
                        help="Путь к изображению или папке с изображениями")
    parser.add_argument("--boxes", action="store_true",
                        help="Сохранить визуализацию с bounding boxes")
    parser.add_argument("--masks", action="store_true",
                        help="Сохранить визуализацию с масками сегментации")
    parser.add_argument("--json", type=Path, metavar="FILE",
                        help="Сохранить полный результат в JSON-файл")
    parser.add_argument("--no-db", action="store_true",
                        help="Не сохранять результат в базу данных")
    args = parser.parse_args()

    images = collect_images(args.path)
    if not images:
        print(f"Изображения не найдены: {args.path}", file=sys.stderr)
        return 1

    config.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    if not args.no_db:
        storage.init_db()

    analyzer = Analyzer()
    all_results = {}

    for image_path in images:
        result = analyzer.analyze(str(image_path))
        all_results[str(image_path)] = result
        print_report(image_path, result)

        if "error" in result:
            continue

        if not args.no_db:
            record_id = storage.save_result(result, str(image_path))
            print(f"Сохранено в БД, id = {record_id}")

        stem = image_path.stem
        if args.boxes:
            out = config.RESULTS_DIR / f"{stem}_boxes.jpg"
            visualization.draw_boxes(analyzer.detector, str(image_path), str(out))
            print(f"Boxes: {out}")
        if args.masks:
            out = config.RESULTS_DIR / f"{stem}_masks.jpg"
            visualization.draw_masks(analyzer.detector, str(image_path), str(out))
            print(f"Masks: {out}")

    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(
            json.dumps(all_results, ensure_ascii=False, indent=2),
            encoding="utf-8")
        print(f"\nJSON сохранён: {args.json}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
