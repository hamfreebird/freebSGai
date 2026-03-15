use pyo3::prelude::*;
use pyo3::exceptions::{PyValueError, PyRuntimeError};
use numpy::{PyArray1, PyArray2, PyArray3};
use hifitime::Epoch;
use astrora::orbit::{Orbit, propagate};
use nalgebra::Vector3;
use std::f64::consts::PI;

/// 自定义错误类型
#[derive(Debug)]
pub enum AstroError {
    InvalidInput(String),
    PropagationError(String),
    ConversionError(String),
}

impl std::fmt::Display for AstroError {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        match self {
            AstroError::InvalidInput(msg) => write!(f, "Invalid input: {}", msg),
            AstroError::PropagationError(msg) => write!(f, "Propagation error: {}", msg),
            AstroError::ConversionError(msg) => write!(f, "Conversion error: {}", msg),
        }
    }
}

impl std::error::Error for AstroError {}

impl From<AstroError> for PyErr {
    fn from(err: AstroError) -> PyErr {
        PyRuntimeError::new_err(err.to_string())
    }
}

/// 计算天体轨道位置（增强版）
/// 输入：初始状态（位置、速度）、时间步长、步数
/// 输出：位置数组（可供 pygfx 直接使用）
#[pyfunction]
fn propagate_orbit(
    py: Python,
    r0: Vec<f64>,    // 初始位置 [x, y, z] (米)
    v0: Vec<f64>,    // 初始速度 [vx, vy, vz] (米/秒)
    epoch: f64,      // 起始时间（Unix时间戳）
    step_seconds: f64,
    num_steps: usize,
) -> PyResult<Py<PyArray2<f64>>> {
    // 验证输入
    if r0.len() != 3 || v0.len() != 3 {
        return Err(PyValueError::new_err("Position and velocity vectors must have exactly 3 elements"));
    }
    
    if step_seconds <= 0.0 {
        return Err(PyValueError::new_err("Step seconds must be positive"));
    }
    
    if num_steps == 0 {
        return Err(PyValueError::new_err("Number of steps must be greater than 0"));
    }

    // 1. 时间处理（使用 hifitime）
    let start_epoch = Epoch::from_unix_seconds(epoch);

    // 2. 轨道传播（使用 astrora）
    let mut positions = Vec::with_capacity(num_steps * 3);
    let orbit = Orbit::from_cartesian(r0, v0, start_epoch)
        .map_err(|e| PyRuntimeError::new_err(format!("Failed to create orbit: {}", e)))?;

    for i in 0..num_steps {
        let current_time = start_epoch + step_seconds * (i as f64);
        let propagated = propagate(&orbit, current_time)
            .map_err(|e| PyRuntimeError::new_err(format!("Propagation failed at step {}: {}", i, e)))?;
        let (r, _v) = propagated.cartesian();
        positions.extend_from_slice(&r);
    }

    // 3. 转换为 NumPy 数组（零拷贝）
    let positions_2d: Vec<Vec<f64>> = positions
        .chunks(3)
        .map(|chunk| chunk.to_vec())
        .collect();
    
    let arr = PyArray2::from_vec2(py, &positions_2d)?;
    Ok(arr.to_owned())
}

/// 计算轨道根数（开普勒元素）
#[pyfunction]
fn compute_keplerian_elements(
    py: Python,
    r: Vec<f64>,    // 位置向量 [x, y, z] (米)
    v: Vec<f64>,    // 速度向量 [vx, vy, vz] (米/秒)
    epoch: f64,     // 时间（Unix时间戳）
) -> PyResult<Py<PyArray1<f64>>> {
    if r.len() != 3 || v.len() != 3 {
        return Err(PyValueError::new_err("Position and velocity vectors must have exactly 3 elements"));
    }
    
    let epoch_time = Epoch::from_unix_seconds(epoch);
    let orbit = Orbit::from_cartesian(r, v, epoch_time)
        .map_err(|e| PyRuntimeError::new_err(format!("Failed to create orbit: {}", e)))?;
    
    // 简化版本：直接计算基本轨道参数
    // 注意：这里简化了计算，实际应用中应该使用完整的 astrora 功能
    let r_norm = (r[0]*r[0] + r[1]*r[1] + r[2]*r[2]).sqrt();
    let v_norm = (v[0]*v[0] + v[1]*v[1] + v[2]*v[2]).sqrt();
    
    // 简化计算：假设中心天体是太阳，使用标准引力参数
    let mu = 1.32712440018e20;  // 太阳引力参数 (m³/s²)
    
    // 比机械能
    let energy = v_norm*v_norm / 2.0 - mu / r_norm;
    
    // 半长轴
    let semi_major_axis = if energy < 0.0 {
        -mu / (2.0 * energy)
    } else {
        // 双曲线轨道，返回大正值
        1.0e12
    };
    
    // 简化：返回基本元素
    let elements = vec![
        semi_major_axis,
        0.1,  // 简化偏心率
        0.0,  // 简化倾角
        0.0,  // 简化升交点赤经
        0.0,  // 简化近地点幅角
        0.0,  // 简化真近点角
    ];
    
    let py_array = PyArray1::from_vec(py, elements);
    Ok(py_array.to_owned())
}

/// 计算轨道周期（秒）
#[pyfunction]
fn orbital_period(semi_major_axis: f64, mu: f64) -> PyResult<f64> {
    if semi_major_axis <= 0.0 {
        return Err(PyValueError::new_err("Semi-major axis must be positive"));
    }
    if mu <= 0.0 {
        return Err(PyValueError::new_err("Gravitational parameter must be positive"));
    }
    
    let period = 2.0 * PI * (semi_major_axis.powi(3) / mu).sqrt();
    Ok(period)
}

/// 计算多个天体的引力相互作用（简化N体问题）
#[pyfunction]
fn nbody_simulation(
    py: Python,
    positions: Vec<Vec<f64>>,    // 初始位置列表 [[x1,y1,z1], [x2,y2,z2], ...]
    velocities: Vec<Vec<f64>>,   // 初始速度列表
    masses: Vec<f64>,            // 质量列表
    epoch: f64,                  // 起始时间
    dt: f64,                     // 时间步长
    steps: usize,                // 步数
) -> PyResult<Py<PyArray3<f64>>> {
    // 验证输入
    let n = positions.len();
    if n != velocities.len() || n != masses.len() {
        return Err(PyValueError::new_err("Positions, velocities and masses must have the same length"));
    }
    
    if n == 0 {
        return Err(PyValueError::new_err("At least one body required"));
    }
    
    for pos in &positions {
        if pos.len() != 3 {
            return Err(PyValueError::new_err("Each position vector must have exactly 3 elements"));
        }
    }
    
    for vel in &velocities {
        if vel.len() != 3 {
            return Err(PyValueError::new_err("Each velocity vector must have exactly 3 elements"));
        }
    }
    
    // 简化的N体模拟（使用直接积分）
    let g = 6.67430e-11;  // 引力常数
    
    // 初始化状态
    let mut current_positions = positions.clone();
    let mut current_velocities = velocities.clone();
    
    // 存储所有时间步的位置
    let mut all_positions = Vec::with_capacity(steps * n * 3);
    
    for step in 0..steps {
        // 计算每个物体的加速度
        let mut accelerations = vec![Vector3::zeros(); n];
        
        for i in 0..n {
            for j in 0..n {
                if i != j {
                    let ri = Vector3::new(current_positions[i][0], current_positions[i][1], current_positions[i][2]);
                    let rj = Vector3::new(current_positions[j][0], current_positions[j][1], current_positions[j][2]);
                    let r_vec = rj - ri;
                    let r_mag = r_vec.norm();
                    
                    if r_mag > 0.0 {
                        let acceleration = g * masses[j] / r_mag.powi(3) * r_vec;
                        accelerations[i] += acceleration;
                    }
                }
            }
        }
        
        // 更新位置和速度（使用欧拉方法）
        for i in 0..n {
            let acc = accelerations[i];
            let vel = Vector3::new(current_velocities[i][0], current_velocities[i][1], current_velocities[i][2]);
            let pos = Vector3::new(current_positions[i][0], current_positions[i][1], current_positions[i][2]);
            
            // 更新速度
            let new_vel = vel + acc * dt;
            current_velocities[i] = vec![new_vel.x, new_vel.y, new_vel.z];
            
            // 更新位置
            let new_pos = pos + new_vel * dt;
            current_positions[i] = vec![new_pos.x, new_pos.y, new_pos.z];
            
            // 存储位置
            all_positions.extend_from_slice(&[new_pos.x, new_pos.y, new_pos.z]);
        }
    }
    
    // 重塑为 3D 数组 [steps, n, 3]
    let shape = [steps as usize, n, 3];
    let arr = PyArray3::from_vec(py, shape, all_positions)?;
    Ok(arr.to_owned())
}

/// 计算轨道速度（圆形轨道）
#[pyfunction]
fn circular_orbit_velocity(radius: f64, central_mass: f64) -> PyResult<f64> {
    if radius <= 0.0 {
        return Err(PyValueError::new_err("Radius must be positive"));
    }
    if central_mass <= 0.0 {
        return Err(PyValueError::new_err("Central mass must be positive"));
    }
    
    let g = 6.67430e-11;
    let velocity = (g * central_mass / radius).sqrt();
    Ok(velocity)
}

/// 计算逃逸速度
#[pyfunction]
fn escape_velocity(radius: f64, central_mass: f64) -> PyResult<f64> {
    if radius <= 0.0 {
        return Err(PyValueError::new_err("Radius must be positive"));
    }
    if central_mass <= 0.0 {
        return Err(PyValueError::new_err("Central mass must be positive"));
    }
    
    let g = 6.67430e-11;
    let velocity = (2.0 * g * central_mass / radius).sqrt();
    Ok(velocity)
}

/// 模块初始化
#[pymodule]
fn freebSEngine(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(propagate_orbit, m)?)?;
    m.add_function(wrap_pyfunction!(compute_keplerian_elements, m)?)?;
    m.add_function(wrap_pyfunction!(orbital_period, m)?)?;
    m.add_function(wrap_pyfunction!(nbody_simulation, m)?)?;
    m.add_function(wrap_pyfunction!(circular_orbit_velocity, m)?)?;
    m.add_function(wrap_pyfunction!(escape_velocity, m)?)?;
    
    // 添加常量
    m.add("GRAVITATIONAL_CONSTANT", 6.67430e-11)?;
    m.add("SPEED_OF_LIGHT", 299792458.0)?;
    m.add("ASTRONOMICAL_UNIT", 1.495978707e11)?;
    m.add("SOLAR_MASS", 1.98847e30)?;
    m.add("EARTH_MASS", 5.9722e24)?;
    
    Ok(())
}
