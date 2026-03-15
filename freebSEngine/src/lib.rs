use pyo3::prelude::*;
use pyo3::exceptions::{PyValueError, PyRuntimeError};
use numpy::{PyArray1, PyArray2, PyArray3, IntoPyArray};
use nalgebra::{Vector3, Matrix3};
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

/// 物理常量
const G: f64 = 6.67430e-11;  // 引力常数 (m³/kg/s²)
const C: f64 = 299792458.0;  // 光速 (m/s)
const AU: f64 = 1.495978707e11;  // 天文单位 (m)
const SOLAR_MASS_KG: f64 = 1.98847e30;  // 太阳质量 (kg)
const EARTH_MASS_KG: f64 = 5.9722e24;  // 地球质量 (kg)

/// 计算天体轨道位置
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

    // 假设中心天体是太阳（简化）
    let mu = G * SOLAR_MASS_KG;

    // 转换为向量
    let r_vec = Vector3::new(r0[0], r0[1], r0[2]);
    let v_vec = Vector3::new(v0[0], v0[1], v0[2]);

    // 计算轨道根数
    let h = r_vec.cross(&v_vec);  // 比角动量
    let h_norm = h.norm();

    // 偏心率向量
    let e_vec = v_vec.cross(&h) / mu - r_vec / r_vec.norm();
    let e = e_vec.norm();

    // 比机械能
    let energy = v_vec.norm_squared() / 2.0 - mu / r_vec.norm();

    // 半长轴
    let a = if energy < 0.0 {
        -mu / (2.0 * energy)
    } else {
        // 双曲线轨道，使用大正值
        1.0e12
    };

    // 初始真近点角
    let nu0 = if e > 0.0 {
        let cos_nu = e_vec.dot(&r_vec) / (e * r_vec.norm());
        let nu = cos_nu.acos();
        if r_vec.dot(&v_vec) < 0.0 {
            2.0 * PI - nu
        } else {
            nu
        }
    } else {
        0.0
    };

    // 轨道周期
    let period = if a > 0.0 && !a.is_infinite() {
        2.0 * PI * (a.powi(3) / mu).sqrt()
    } else {
        f64::INFINITY
    };

    // 存储所有位置
    let mut positions = Vec::with_capacity(num_steps * 3);

    for i in 0..num_steps {
        let t = i as f64 * step_seconds;

        let nu = if period.is_finite() {
            // 椭圆轨道：使用平均近点角近似
            let M = 2.0 * PI * t / period;
            nu0 + M
        } else {
            // 双曲线或抛物线轨道：简化处理
            nu0 + 0.01 * t
        };

        // 计算位置（在轨道平面内）
        let p = if a.is_finite() {
            a * (1.0 - e.powi(2))
        } else {
            h_norm.powi(2) / mu
        };

        let r_current = p / (1.0 + e * nu.cos());

        // 轨道平面内的坐标
        let x_orb = r_current * nu.cos();
        let y_orb = r_current * nu.sin();

        // 简化：假设轨道在xy平面内
        positions.push(x_orb);
        positions.push(y_orb);
        positions.push(0.0);
    }

    // 转换为 NumPy 数组
    let positions_2d: Vec<Vec<f64>> = positions
        .chunks(3)
        .map(|chunk| chunk.to_vec())
        .collect();

    let arr = PyArray2::from_vec2(py, &positions_2d)?;
    Ok(arr.to_owned())
}

/// 计算开普勒轨道根数
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

    // 假设中心天体是太阳
    let mu = G * SOLAR_MASS_KG;

    let r_vec = Vector3::new(r[0], r[1], r[2]);
    let v_vec = Vector3::new(v[0], v[1], v[2]);

    // 计算比角动量
    let h = r_vec.cross(&v_vec);
    let h_norm = h.norm();

    // 计算偏心率向量
    let e_vec = v_vec.cross(&h) / mu - r_vec / r_vec.norm();
    let e = e_vec.norm();

    // 计算比机械能
    let energy = v_vec.norm_squared() / 2.0 - mu / r_vec.norm();

    // 计算半长轴
    let a = if energy < 0.0 {
        -mu / (2.0 * energy)
    } else {
        f64::INFINITY
    };

    // 计算倾角
    let i = if h_norm > 0.0 {
        (h[2] / h_norm).acos().to_degrees()
    } else {
        0.0
    };

    // 计算升交点赤经
    let n = Vector3::new(0.0, 0.0, 1.0).cross(&h);
    let n_norm = n.norm();
    let raan = if n_norm > 0.0 {
        let mut raan = (n[0] / n_norm).acos().to_degrees();
        if n[1] < 0.0 {
            raan = 360.0 - raan;
        }
        raan
    } else {
        0.0
    };

    // 计算近地点幅角
    let argp = if n_norm > 0.0 && e > 0.0 {
        let mut argp = (n.dot(&e_vec) / (n_norm * e)).acos().to_degrees();
        if e_vec[2] < 0.0 {
            argp = 360.0 - argp;
        }
        argp
    } else {
        0.0
    };

    // 计算真近点角
    let nu = if e > 0.0 {
        let cos_nu = e_vec.dot(&r_vec) / (e * r_vec.norm());
        let mut nu = cos_nu.acos().to_degrees();
        if r_vec.dot(&v_vec) < 0.0 {
            nu = 360.0 - nu;
        }
        nu
    } else {
        0.0
    };

    // 返回所有元素
    let elements = vec![a, e, i, raan, argp, nu];
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

/// 计算多个天体的引力相互作用（N体问题）
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

    // 转换为向量数组
    let mut pos_vecs: Vec<Vector3<f64>> = positions.iter()
        .map(|p| Vector3::new(p[0], p[1], p[2]))
        .collect();

    let mut vel_vecs: Vec<Vector3<f64>> = velocities.iter()
        .map(|v| Vector3::new(v[0], v[1], v[2]))
        .collect();

    // 存储所有时间步的位置
    let mut all_positions = Vec::with_capacity(steps * n * 3);

    // 使用 leapfrog 积分器（更稳定）
    for step in 0..steps {
        // 存储当前位置
        for i in 0..n {
            all_positions.push(pos_vecs[i][0]);
            all_positions.push(pos_vecs[i][1]);
            all_positions.push(pos_vecs[i][2]);
        }

        // 计算加速度
        let mut accelerations = vec![Vector3::zeros(); n];

        for i in 0..n {
            for j in 0..n {
                if i != j {
                    let r_vec = pos_vecs[j] - pos_vecs[i];
                    let r = r_vec.norm();

                    if r > 0.0 {
                        let acceleration = G * masses[j] / r.powi(3) * r_vec;
                        accelerations[i] += acceleration;
                    }
                }
            }
        }

        // 更新速度（半步）
        for i in 0..n {
            vel_vecs[i] += accelerations[i] * (dt / 2.0);
        }

        // 更新位置
        for i in 0..n {
            pos_vecs[i] += vel_vecs[i] * dt;
        }

        // 重新计算加速度
        let mut accelerations_new = vec![Vector3::zeros(); n];
        for i in 0..n {
            for j in 0..n {
                if i != j {
                    let r_vec = pos_vecs[j] - pos_vecs[i];
                    let r = r_vec.norm();

                    if r > 0.0 {
                        let acceleration = G * masses[j] / r.powi(3) * r_vec;
                        accelerations_new[i] += acceleration;
                    }
                }
            }
        }

        // 更新速度（另外半步）
        for i in 0..n {
            vel_vecs[i] += accelerations_new[i] * (dt / 2.0);
        }
    }

    // 重塑为 3D 数组 [steps, n, 3]
    let shape = [steps as usize, n, 3];
    let arr = PyArray3::from_vec(py, shape, all_positions)?;
    Ok(arr.to_owned())
}

/// 计算圆形轨道速度
#[pyfunction]
fn circular_orbit_velocity(radius: f64, central_mass: f64) -> PyResult<f64> {
    if radius <= 0.0 {
        return Err(PyValueError::new_err("Radius must be positive"));
    }
    if central_mass <= 0.0 {
        return Err(PyValueError::new_err("Central mass must be positive"));
    }

    let velocity = (G * central_mass / radius).sqrt();
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

    let velocity = (2.0 * G * central_mass / radius).sqrt();
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
    m.add("GRAVITATIONAL_CONSTANT", G)?;
    m.add("SPEED_OF_LIGHT", C)?;
    m.add("ASTRONOMICAL_UNIT", AU)?;
    m.add("SOLAR_MASS", SOLAR_MASS_KG)?;
    m.add("EARTH_MASS", EARTH_MASS_KG)?;

    Ok(())
}
