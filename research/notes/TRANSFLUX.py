from dataclasses import dataclass
from typing import Callable, Any, Optional
import random
import time

@dataclass
class Flow:
    """Переменная как русло: текущее значение, цель, скорость изменения, шум, комфорт"""
    current: float = 0.0
    target: float = 0.0
    velocity: float = 0.0          # скорость изменения (м/с)
    acceleration: float = 0.0      # ускорение
    noise_level: float = 0.05      # дисперсия шума
    comfort: float = 1.0           # 0..1, насколько состояние "эйфорично"
    history: list[tuple[float, float]] = None  # (время, значение)

    def __post_init__(self):
        self.history = [(time.time(), self.current)]

    def update(self, dt: float = 0.1):
        """Обновить состояние за dt секунд"""
        error = self.target - self.current
        self.acceleration = 0.5 * error  # простая "пружина"
        self.velocity += self.acceleration * dt
        self.current += self.velocity * dt
        
        # Добавляем шум как часть сигнала
        noise = random.gauss(0, self.noise_level)
        self.current += noise
        
        # Комфорт падает при резких изменениях
        if abs(self.velocity) > 2.0:
            self.comfort = max(0.0, self.comfort - 0.15)
        
        self.history.append((time.time(), self.current))

    def __repr__(self):
        return (f"Flow(current={self.current:.3f}, target={self.target:.1f}, "
                f"velocity={self.velocity:.2f}, comfort={self.comfort:.2f})")


class GradientLogic:
    """Градиент истинности вместо bool"""
    @staticmethod
    def flows_towards(value: Flow, condition: Callable[[float], float]) -> float:
        """Насколько сильно выполнено условие (0..1)"""
        score = condition(value.current)
        # Учитываем комфорт и шум
        return max(0.0, min(1.0, score * value.comfort))

# Пример использования
if __name__ == "__main__":
    gender = Flow(current=0.0, target=1.0, noise_level=0.08)  # от 0 (нейтрально) к 1 (female)
    
    def is_female_enough(x: float) -> float:
        return max(0.0, min(1.0, (x - 0.3) / 0.7))  # порог ~0.3, полная уверенность на 1.0
    
    print("Начало:", gender)
    
    for _ in range(15):
        gender.update(dt=0.3)
        grad = GradientLogic.flows_towards(gender, is_female_enough)
        print(f"  → {gender} | Градиент 'female': {grad:.2f}")
        if grad > 0.7:
            print("   → Эйфория! Код разблокирован для female-контекста 💖")
        time.sleep(0.3)