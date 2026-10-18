"""classify_jump: одиночный скачок не то же самое, что общий."""

from transflux import FluxVar, classify_jump


def test_velocity_on_the_threshold_is_calm():
    sensor = FluxVar(value=0.0, trauma_threshold=10.0)
    sensor.flow(10.0)
    assert sensor.velocity == 10.0
    assert classify_jump(sensor, []) == "calm"


def test_jump_without_neighbors_is_alone():
    sensor = FluxVar(value=12.0, trauma_threshold=30.0)
    sensor.flow(300.0)
    assert classify_jump(sensor, []) == "alone"


def test_sensor_is_not_its_own_neighbor():
    sensor = FluxVar(value=12.0, trauma_threshold=30.0)
    sensor.flow(300.0)
    assert classify_jump(sensor, [sensor]) == "alone"


def test_quiet_neighbor_leaves_the_jump_alone():
    sensor = FluxVar(value=12.0, trauma_threshold=30.0)
    neighbor = FluxVar(value=14.0, trauma_threshold=30.0)
    sensor.flow(300.0)
    neighbor.flow(16.0)
    assert classify_jump(sensor, [neighbor]) == "alone"
    assert classify_jump(neighbor, [sensor]) == "calm"


def test_two_jumps_are_shared():
    left = FluxVar(value=12.0, trauma_threshold=30.0)
    right = FluxVar(value=14.0, trauma_threshold=30.0)
    left.flow(80.0)
    right.flow(90.0)
    assert classify_jump(left, [right]) == "shared"
    assert classify_jump(right, [left]) == "shared"


def test_classification_does_not_touch_the_flux():
    sensor = FluxVar(value=12.0, trauma_threshold=30.0, comfort=0.2)
    sensor.flow(300.0)
    before = (sensor.value, sensor.velocity, sensor.comfort)
    classify_jump(sensor, [])
    assert (sensor.value, sensor.velocity, sensor.comfort) == before
