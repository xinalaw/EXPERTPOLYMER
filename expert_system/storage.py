"""
Хранение результатов анализа в локальной базе данных SQLite.

Схема нормализована (3НФ) и состоит из трёх сущностей:

    particle_classes  — справочник морфологических классов частиц;
    analysis_results  — один проведённый анализ изображения;
    particles         — каждая обнаруженная частица.

Связи: analysis_results 1—N particles (один анализ содержит много частиц),
       particle_classes 1—N particles (один класс у многих частиц).
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (Column, DateTime, Float, ForeignKey, Integer,
                        String, Text, create_engine)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

from . import config

engine = create_engine(config.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Описания классов для справочника (заполняется при init_db)
CLASS_DESCRIPTIONS = {
    "dendritic":  "Дендритные частицы с разветвлённой структурой",
    "fragmented": "Осколочные частицы неправильной формы",
    "spongy":     "Губчатые частицы с пористой поверхностью",
    "spherical":  "Сферические частицы, оптимальные для печати",
    "teardrop":   "Каплевидные (вытянутые) частицы",
}


class ParticleClass(Base):
    """Справочник морфологических классов частиц."""
    __tablename__ = "particle_classes"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)

    particles = relationship("Particle", back_populates="particle_class")


class AnalysisResult(Base):
    """Один проведённый анализ одного изображения."""
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True)
    image_path = Column(String, nullable=False)
    total_particles = Column(Integer)

    # Сводные морфологические показатели выборки
    avg_circularity = Column(Float)
    dispersity      = Column(Float)

    # Заключение нечёткой экспертной подсистемы
    expert_score = Column(Float)
    verdict      = Column(String)
    conclusion   = Column(Text)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    particles = relationship("Particle", back_populates="analysis",
                             cascade="all, delete-orphan")


class Particle(Base):
    """Одна обнаруженная частица в рамках конкретного анализа."""
    __tablename__ = "particles"

    id = Column(Integer, primary_key=True)
    analysis_id = Column(Integer, ForeignKey("analysis_results.id"),
                         nullable=False)
    class_id = Column(Integer, ForeignKey("particle_classes.id"),
                      nullable=False)

    confidence  = Column(Float)   # уверенность YOLO, 0–1
    circularity = Column(Float)   # округлость, 0–1
    diameter_px = Column(Float)   # эквивалентный диаметр, px
    area_px     = Column(Float)   # площадь, px²
    bbox        = Column(String)  # "x,y,w,h"

    analysis = relationship("AnalysisResult", back_populates="particles")
    particle_class = relationship("ParticleClass", back_populates="particles")


def init_db():
    """Создаёт таблицы и заполняет справочник классов (если пуст)."""
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if db.query(ParticleClass).count() == 0:
            for name in config.CLASSES:
                db.add(ParticleClass(
                    name=name,
                    description=CLASS_DESCRIPTIONS.get(name, "")))
            db.commit()


def save_result(result: dict, image_path: str) -> int:
    """
    Сохраняет результат анализа вместе с каждой частицей.
    Возвращает id созданной записи analysis_results.
    """
    expert = result.get("expert", {})

    with SessionLocal() as db:
        class_ids = {c.name: c.id for c in db.query(ParticleClass).all()}

        record = AnalysisResult(
            image_path=str(image_path),
            total_particles=result.get("total_particles", 0),
            avg_circularity=result.get("avg_circularity", 0),
            dispersity=result.get("dispersity", 0),
            expert_score=expert.get("score", 0),
            verdict=expert.get("verdict", ""),
            conclusion=expert.get("conclusion", ""),
        )

        for p in result.get("particles", []):
            record.particles.append(Particle(
                class_id=class_ids[p["class"]],
                confidence=p["confidence"],
                circularity=p["circularity"],
                diameter_px=p["diameter"],
                area_px=p["area"],
                bbox=",".join(map(str, p["bbox"])),
            ))

        db.add(record)
        db.commit()
        return record.id


def get_all_results() -> list[AnalysisResult]:
    """Все сохранённые анализы (история), новые первыми."""
    with SessionLocal() as db:
        return db.query(AnalysisResult).order_by(
            AnalysisResult.created_at.desc()).all()


def get_composition(analysis_id: int) -> dict:
    """
    Состав порошка (%) для анализа — вычисляется из таблицы particles
    соединением со справочником классов (демонстрация работы со связями).
    """
    with SessionLocal() as db:
        rows = (db.query(ParticleClass.name, Particle.id)
                  .join(Particle, Particle.class_id == ParticleClass.id)
                  .filter(Particle.analysis_id == analysis_id).all())
        total = len(rows)
        if total == 0:
            return {}
        counts: dict[str, int] = {}
        for name, _ in rows:
            counts[name] = counts.get(name, 0) + 1
        return {k: round(v / total * 100, 1) for k, v in counts.items()}