#!/usr/bin/env python3
"""
测试ID修复：验证对象和实体ID不会无限增长
"""
import sys
sys.path.append('.')

from entities.entity import Entity, Object
import numpy as np
import uuid

def test_entity_copy():
    """测试实体复制功能"""
    print("测试实体复制...")
    entity = Entity(
        mass=1.0e30,
        density=1408.0,
        radius=6.96e8,
        position=np.array([0.0, 0.0]),
        velocity=np.array([0.0, 0.0]),
        name="Test Sun"
    )
    
    print(f"原始实体ID: {entity.id}")
    print(f"原始实体名称: {entity.name}")
    
    # 复制实体
    copy1 = entity.copy()
    print(f"副本1 ID: {copy1.id}")
    print(f"副本1名称: {copy1.name}")
    
    # 再次复制
    copy2 = copy1.copy()
    print(f"副本2 ID: {copy2.id}")
    print(f"副本2名称: {copy2.name}")
    
    # 验证ID不包含"_copy"后缀
    assert "_copy" not in copy1.id, f"副本ID包含'_copy': {copy1.id}"
    assert "_copy" not in copy2.id, f"副本ID包含'_copy': {copy2.id}"
    
    # 验证ID是有效的UUID
    try:
        uuid.UUID(copy1.id)
        uuid.UUID(copy2.id)
        print("[OK] 实体ID是有效的UUID")
    except ValueError:
        print("[ERROR] 实体ID不是有效的UUID")
        return False
    
    print("[PASS] 实体复制测试通过")
    return True

def test_object_copy():
    """测试对象复制功能"""
    print("\n测试对象复制...")
    obj = Object(
        position=np.array([1.5e11, 0.0]),
        velocity=np.array([0.0, 29780.0]),
        label="Test Object"
    )
    
    print(f"原始对象ID: {obj.id}")
    print(f"原始对象标签: {obj.label}")
    
    # 复制对象
    copy1 = obj.copy()
    print(f"副本1 ID: {copy1.id}")
    print(f"副本1标签: {copy1.label}")
    
    # 再次复制
    copy2 = copy1.copy()
    print(f"副本2 ID: {copy2.id}")
    print(f"副本2标签: {copy2.label}")
    
    # 验证ID不包含"_copy"后缀
    assert "_copy" not in copy1.id, f"副本ID包含'_copy': {copy1.id}"
    assert "_copy" not in copy2.id, f"副本ID包含'_copy': {copy2.id}"
    
    # 验证ID是有效的UUID
    try:
        uuid.UUID(copy1.id)
        uuid.UUID(copy2.id)
        print("[OK] 对象ID是有效的UUID")
    except ValueError:
        print("[ERROR] 对象ID不是有效的UUID")
        return False
    
    print("[PASS] 对象复制测试通过")
    return True

def test_physics_update():
    """测试物理更新不会改变ID"""
    print("\n测试物理更新...")
    from physics.motion import update_entities, update_objects
    
    # 创建测试实体
    entities = [
        Entity(
            mass=1.0e30,
            density=1408.0,
            radius=6.96e8,
            position=np.array([0.0, 0.0]),
            velocity=np.array([0.0, 0.0]),
            name="Sun"
        ),
        Entity(
            mass=5.97e24,
            density=5515.0,
            radius=6.371e6,
            position=np.array([1.5e11, 0.0]),
            velocity=np.array([0.0, 29780.0]),
            name="Earth"
        )
    ]
    
    original_ids = [e.id for e in entities]
    print(f"原始实体IDs: {original_ids}")
    
    # 更新实体
    updated_entities = update_entities(entities, dt=1.0)
    updated_ids = [e.id for e in updated_entities]
    print(f"更新后实体IDs: {updated_ids}")
    
    # 验证ID保持不变
    assert original_ids == updated_ids, "实体ID在更新后改变了"
    print("[OK] 实体更新保持ID不变")
    
    # 创建测试对象
    objects = [
        Object(
            position=np.array([1.5e11 + 4.0e7, 0.0]),
            velocity=np.array([0.0, 3070.0]),
            label="Satellite"
        )
    ]
    
    original_obj_ids = [obj.id for obj in objects]
    print(f"原始对象IDs: {original_obj_ids}")
    
    # 更新对象
    updated_objects, _ = update_objects(objects, entities, dt=1.0)
    updated_obj_ids = [obj.id for obj in updated_objects]
    print(f"更新后对象IDs: {updated_obj_ids}")
    
    # 验证ID保持不变
    assert original_obj_ids == updated_obj_ids, "对象ID在更新后改变了"
    print("[OK] 对象更新保持ID不变")
    
    return True

def main():
    """主测试函数"""
    print("=" * 60)
    print("测试ID修复")
    print("=" * 60)
    
    tests = [
        ("实体复制", test_entity_copy),
        ("对象复制", test_object_copy),
        ("物理更新", test_physics_update)
    ]
    
    all_passed = True
    for test_name, test_func in tests:
        try:
            if not test_func():
                all_passed = False
                print(f"[FAIL] {test_name} 失败")
        except Exception as e:
            print(f"[ERROR] {test_name} 异常: {e}")
            import traceback
            traceback.print_exc()
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("[SUCCESS] 所有测试通过！ID修复成功")
    else:
        print("[FAILURE] 部分测试失败")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)