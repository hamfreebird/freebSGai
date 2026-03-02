use pyo3::prelude::*;
use pyo3::types::PyDict;
use numpy::{PyArray1, PyArray2, IntoPyArray};
use hifitime::Epoch;
use astrora::orbit::{Orbit, propagate};

/// 计算天体轨道位置
/// 输入：初始状态（位置、速度）、时间步长、步数
/// 输出：位置数组（可供 pygfx 直接使用）
#[pyfunction]
fn propagate_orbit(
    py: Python,
    r0: Vec<f64>,    // 初始位置 [x, y, z]
    v0: Vec<f64>,    // 初始速度 [vx, vy, vz]
    epoch: f64,      // 起始时间（MJD格式或Unix时间戳）
    step_seconds: f64,
    num_steps: usize,
) -> PyResult<Py<PyArray2<f64>>> {
    // 1. 时间处理（使用 hifitime）
    let start_epoch = Epoch::from_unix_seconds(epoch);

    // 2. 轨道传播（使用 astrora）
    let mut positions = Vec::with_capacity(num_steps * 3);
    let mut orbit = Orbit::from_cartesian(r0, v0, start_epoch);

    for i in 0..num_steps {
        let current_time = start_epoch + step_seconds * (i as f64);
        let propagated = propagate(&orbit, current_time)?;
        let (r, _v) = propagated.cartesian();
        positions.extend_from_slice(&r);
    }

    // 3. 转换为 NumPy 数组（零拷贝）
    let arr = PyArray2::from_vec2(
        py,
        &positions.chunks(3).map(|chunk| chunk.to_vec()).collect::<Vec<_>>()
    )?;
    Ok(arr.to_owned())
}

/// 模块初始化
#[pymodule]
fn freebSEngine(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(propagate_orbit, m)?)?;
    Ok(())
}
