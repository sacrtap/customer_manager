"""
价格区间管理 API 测试
"""

import pytest
from sanic import Sanic
from app.blueprints.price_band import price_band_bp
from app.blueprints.price_config import price_config_bp
from app.middlewares.auth import attach_auth_middleware
import uuid


@pytest.fixture
def app():
    """创建测试应用"""
    app_name = f"test_app_{uuid.uuid4().hex[:8]}"
    app = Sanic(app_name)
    attach_auth_middleware(app)
    app.blueprint(price_band_bp)
    app.blueprint(price_config_bp)
    return app


# 使用数据库中存在的用户 ID
TEST_USER_ID = 122



def test_create_price_band(app):
    """测试创建价格区间"""
    from app.utils.jwt import create_access_token
    
    token = create_access_token(TEST_USER_ID, "admin", ["pricing.create"])
    
    # 先创建价格配置
    config_data = {
        "code": f"CONFIG-{uuid.uuid4().hex[:8]}",
        "name": "测试配置",
        "base_price": 100.00,
        "status": "active",
        "created_by": TEST_USER_ID,
    }
    
    request, config_response = app.test_client.post(
        "/api/v1/price-configs",
        json=config_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    
    config_id = config_response.json["data"]["id"]
    
    # 创建价格区间
    price_band_data = {
        "code": f"PB-{uuid.uuid4().hex[:8]}",
        "name": "测试价格区间",
        "price_config_id": config_id,
        "min_quantity": 1,
        "max_quantity": 100,
        "unit_price": 100.00,
        "discount_rate": 5.0,
        "final_price": 95.00,
        "priority": 1,
        "is_active": True,
    }
    
    request, response = app.test_client.post(
        "/api/v1/price-bands",
        json=price_band_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status == 200
    data = response.json["data"]
    assert data["code"] == price_band_data["code"]
    assert data["name"] == price_band_data["name"]
    assert data["unit_price"] == price_band_data["unit_price"]
    assert data["is_active"] == True



def test_get_price_bands_list(app):
    """测试获取价格区间列表"""
    from app.utils.jwt import create_access_token
    
    token = create_access_token(TEST_USER_ID, "admin", ["pricing.view", "pricing.create"])
    
    # 先创建价格配置和价格区间
    config_data = {
        "code": f"CONFIG-{uuid.uuid4().hex[:8]}",
        "name": "测试配置",
        "base_price": 100.00,
        "status": "active",
        "created_by": TEST_USER_ID,
    }
    
    request, config_response = app.test_client.post(
        "/api/v1/price-configs",
        json=config_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    
    config_id = config_response.json["data"]["id"]
    
    # 创建两个价格区间
    for i in range(2):
        price_band_data = {
            "code": f"PB-{uuid.uuid4().hex[:8]}",
            "name": f"测试价格区间{i}",
            "price_config_id": config_id,
            "min_quantity": 1,
            "max_quantity": 100,
            "unit_price": 100.00,
            "discount_rate": 5.0,
            "final_price": 95.00,
            "priority": 1,
            "is_active": True,
        }
        
        app.test_client.post(
            "/api/v1/price-bands",
            json=price_band_data,
            headers={"Authorization": f"Bearer {token}"},
        )
    
    # 获取列表
    request, response = app.test_client.get(
        "/api/v1/price-bands",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status == 200
    assert "data" in response.json
    assert "total" in response.json
    assert len(response.json["data"]) >= 2



def test_filter_price_bands_by_status(app):
    """测试按状态筛选价格区间"""
    from app.utils.jwt import create_access_token
    
    token = create_access_token(TEST_USER_ID, "admin", ["pricing.view", "pricing.create"])
    
    # 先创建价格配置
    config_data = {
        "code": f"CONFIG-{uuid.uuid4().hex[:8]}",
        "name": "测试配置",
        "base_price": 100.00,
        "status": "active",
        "created_by": TEST_USER_ID,
    }
    
    request, config_response = app.test_client.post(
        "/api/v1/price-configs",
        json=config_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    
    config_id = config_response.json["data"]["id"]
    
    # 创建活跃和禁用的价格区间
    for is_active in [True, False, True]:
        price_band_data = {
            "code": f"PB-{uuid.uuid4().hex[:8]}",
            "name": f"测试价格区间-{is_active}",
            "price_config_id": config_id,
            "min_quantity": 1,
            "max_quantity": 100,
            "unit_price": 100.00,
            "discount_rate": 5.0,
            "final_price": 95.00,
            "priority": 1,
            "is_active": is_active,
        }
        
        app.test_client.post(
            "/api/v1/price-bands",
            json=price_band_data,
            headers={"Authorization": f"Bearer {token}"},
        )
    
    # 筛选活跃的价格区间
    request, response = app.test_client.get(
        "/api/v1/price-bands?is_active=true",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status == 200
    assert len(response.json["data"]) >= 2



def test_search_price_bands(app):
    """测试搜索价格区间"""
    from app.utils.jwt import create_access_token
    
    token = create_access_token(TEST_USER_ID, "admin", ["pricing.view", "pricing.create"])
    
    # 先创建价格配置
    config_data = {
        "code": f"CONFIG-{uuid.uuid4().hex[:8]}",
        "name": "测试配置",
        "base_price": 100.00,
        "status": "active",
        "created_by": TEST_USER_ID,
    }
    
    request, config_response = app.test_client.post(
        "/api/v1/price-configs",
        json=config_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    
    config_id = config_response.json["data"]["id"]
    
    # 创建价格区间
    price_band_data = {
        "code": f"PB-{uuid.uuid4().hex[:8]}",
        "name": "搜索测试区间",
        "price_config_id": config_id,
        "min_quantity": 1,
        "max_quantity": 100,
        "unit_price": 100.00,
        "discount_rate": 5.0,
        "final_price": 95.00,
        "priority": 1,
        "is_active": True,
    }
    
    app.test_client.post(
        "/api/v1/price-bands",
        json=price_band_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    
    # 搜索
    request, response = app.test_client.get(
        "/api/v1/price-bands?keyword=搜索测试",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status == 200
    assert len(response.json["data"]) >= 1



def test_get_price_band_by_id(app):
    """测试通过 ID 获取价格区间"""
    from app.utils.jwt import create_access_token
    
    token = create_access_token(TEST_USER_ID, "admin", ["pricing.view", "pricing.create"])
    
    # 先创建价格配置
    config_data = {
        "code": f"CONFIG-{uuid.uuid4().hex[:8]}",
        "name": "测试配置",
        "base_price": 100.00,
        "status": "active",
        "created_by": TEST_USER_ID,
    }
    
    request, config_response = app.test_client.post(
        "/api/v1/price-configs",
        json=config_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    
    config_id = config_response.json["data"]["id"]
    
    # 创建价格区间
    price_band_data = {
        "code": f"PB-{uuid.uuid4().hex[:8]}",
        "name": "测试区间",
        "price_config_id": config_id,
        "min_quantity": 1,
        "max_quantity": 100,
        "unit_price": 100.00,
        "discount_rate": 5.0,
        "final_price": 95.00,
        "priority": 1,
        "is_active": True,
    }
    
    create_response, _ = app.test_client.post(
        "/api/v1/price-bands",
        json=price_band_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    
    band_id = create_response.json["data"]["id"]
    
    # 获取
    request, response = app.test_client.get(
        f"/api/v1/price-bands/{band_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status == 200
    data = response.json["data"]
    assert data["id"] == band_id
    assert data["name"] == "测试区间"



def test_update_price_band(app):
    """测试更新价格区间"""
    from app.utils.jwt import create_access_token
    
    token = create_access_token(TEST_USER_ID, "admin", ["pricing.update", "pricing.create"])
    
    # 先创建价格配置
    config_data = {
        "code": f"CONFIG-{uuid.uuid4().hex[:8]}",
        "name": "测试配置",
        "base_price": 100.00,
        "status": "active",
        "created_by": TEST_USER_ID,
    }
    
    request, config_response = app.test_client.post(
        "/api/v1/price-configs",
        json=config_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    
    config_id = config_response.json["data"]["id"]
    
    # 创建价格区间
    price_band_data = {
        "code": f"PB-{uuid.uuid4().hex[:8]}",
        "name": "原名称",
        "price_config_id": config_id,
        "min_quantity": 1,
        "max_quantity": 100,
        "unit_price": 100.00,
        "discount_rate": 5.0,
        "final_price": 95.00,
        "priority": 1,
        "is_active": True,
    }
    
    create_response, _ = app.test_client.post(
        "/api/v1/price-bands",
        json=price_band_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    
    band_id = create_response.json["data"]["id"]
    
    # 更新
    update_data = {
        "name": "新名称",
        "unit_price": 120.00,
        "discount_rate": 10.0,
    }
    
    request, response = app.test_client.put(
        f"/api/v1/price-bands/{band_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status == 200
    data = response.json["data"]
    assert data["name"] == "新名称"
    assert data["unit_price"] == 120.00
    assert data["discount_rate"] == 10.0



def test_delete_price_band(app):
    """测试删除价格区间"""
    from app.utils.jwt import create_access_token
    
    token = create_access_token(TEST_USER_ID, "admin", ["pricing.delete", "pricing.create"])
    
    # 先创建价格配置
    config_data = {
        "code": f"CONFIG-{uuid.uuid4().hex[:8]}",
        "name": "测试配置",
        "base_price": 100.00,
        "status": "active",
        "created_by": TEST_USER_ID,
    }
    
    request, config_response = app.test_client.post(
        "/api/v1/price-configs",
        json=config_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    
    config_id = config_response.json["data"]["id"]
    
    # 创建价格区间
    price_band_data = {
        "code": f"PB-{uuid.uuid4().hex[:8]}",
        "name": "删除测试",
        "price_config_id": config_id,
        "min_quantity": 1,
        "max_quantity": 100,
        "unit_price": 100.00,
        "discount_rate": 5.0,
        "final_price": 95.00,
        "priority": 1,
        "is_active": True,
    }
    
    create_response, _ = app.test_client.post(
        "/api/v1/price-bands",
        json=price_band_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    
    band_id = create_response.json["data"]["id"]
    
    # 删除
    request, response = app.test_client.delete(
        f"/api/v1/price-bands/{band_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status == 200
    
    # 验证已删除
    get_request, get_response = app.test_client.get(
        f"/api/v1/price-bands/{band_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert get_response.status == 404



def test_price_band_validation(app):
    """测试价格区间验证"""
    from app.utils.jwt import create_access_token
    
    token = create_access_token(TEST_USER_ID, "admin", ["pricing.create"])
    
    # 先创建价格配置
    config_data = {
        "code": f"CONFIG-{uuid.uuid4().hex[:8]}",
        "name": "测试配置",
        "base_price": 100.00,
        "status": "active",
        "created_by": TEST_USER_ID,
    }
    
    request, config_response = app.test_client.post(
        "/api/v1/price-configs",
        json=config_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    
    config_id = config_response.json["data"]["id"]
    
    # 测试缺少必填字段
    invalid_data = {
        "name": "测试区间",
        # 缺少 code
        "price_config_id": config_id,
    }
    
    request, response = app.test_client.post(
        "/api/v1/price-bands",
        json=invalid_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status == 422



def test_price_band_with_amount_bands(app):
    """测试使用金额区间的价格区间"""
    from app.utils.jwt import create_access_token
    
    token = create_access_token(TEST_USER_ID, "admin", ["pricing.view", "pricing.create"])
    
    # 先创建价格配置
    config_data = {
        "code": f"CONFIG-{uuid.uuid4().hex[:8]}",
        "name": "测试配置",
        "base_price": 100.00,
        "status": "active",
        "created_by": TEST_USER_ID,
    }
    
    request, config_response = app.test_client.post(
        "/api/v1/price-configs",
        json=config_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    
    config_id = config_response.json["data"]["id"]
    
    # 创建金额区间
    price_band_data = {
        "code": f"PB-{uuid.uuid4().hex[:8]}",
        "name": "金额区间测试",
        "price_config_id": config_id,
        "min_amount": 1000.00,
        "max_amount": 5000.00,
        "unit_price": 100.00,
        "discount_rate": 5.0,
        "final_price": 95.00,
        "priority": 1,
        "is_active": True,
    }
    
    request, response = app.test_client.post(
        "/api/v1/price-bands",
        json=price_band_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status == 200
    data = response.json["data"]
    assert data["min_amount"] == 1000.00
    assert data["max_amount"] == 5000.00



def test_price_band_pagination(app):
    """测试价格区间分页"""
    from app.utils.jwt import create_access_token
    
    token = create_access_token(TEST_USER_ID, "admin", ["pricing.view", "pricing.create"])
    
    # 先创建价格配置
    config_data = {
        "code": f"CONFIG-{uuid.uuid4().hex[:8]}",
        "name": "测试配置",
        "base_price": 100.00,
        "status": "active",
        "created_by": TEST_USER_ID,
    }
    
    request, config_response = app.test_client.post(
        "/api/v1/price-configs",
        json=config_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    
    config_id = config_response.json["data"]["id"]
    
    # 创建多个价格区间
    for i in range(5):
        price_band_data = {
            "code": f"PB-{uuid.uuid4().hex[:8]}",
            "name": f"分页测试{i}",
            "price_config_id": config_id,
            "min_quantity": 1,
            "max_quantity": 100,
            "unit_price": 100.00,
            "discount_rate": 5.0,
            "final_price": 95.00,
            "priority": 1,
            "is_active": True,
        }
        
        app.test_client.post(
            "/api/v1/price-bands",
            json=price_band_data,
            headers={"Authorization": f"Bearer {token}"},
        )
    
    # 测试分页
    request, response = app.test_client.get(
        "/api/v1/price-bands?page=1&per_page=2",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status == 200
    assert len(response.json["data"]) == 2
    assert response.json["total"] >= 5



def test_price_band_sorting(app):
    """测试价格区间排序"""
    from app.utils.jwt import create_access_token
    
    token = create_access_token(TEST_USER_ID, "admin", ["pricing.view", "pricing.create"])
    
    # 先创建价格配置
    config_data = {
        "code": f"CONFIG-{uuid.uuid4().hex[:8]}",
        "name": "测试配置",
        "base_price": 100.00,
        "status": "active",
        "created_by": TEST_USER_ID,
    }
    
    request, config_response = app.test_client.post(
        "/api/v1/price-configs",
        json=config_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    
    config_id = config_response.json["data"]["id"]
    
    # 创建不同优先级的价格区间
    for priority in [3, 1, 2]:
        price_band_data = {
            "code": f"PB-{uuid.uuid4().hex[:8]}",
            "name": f"优先级{priority}",
            "price_config_id": config_id,
            "min_quantity": 1,
            "max_quantity": 100,
            "unit_price": 100.00,
            "discount_rate": 5.0,
            "final_price": 95.00,
            "priority": priority,
            "is_active": True,
        }
        
        app.test_client.post(
            "/api/v1/price-bands",
            json=price_band_data,
            headers={"Authorization": f"Bearer {token}"},
        )
    
    # 按优先级排序
    request, response = app.test_client.get(
        "/api/v1/price-bands?sort_field=priority&sort_desc=true",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status == 200
    data = response.json["data"]
    assert len(data) >= 3
    # 验证第一个优先级最高
    assert data[0]["priority"] >= data[1]["priority"]



def test_duplicate_code_validation(app):
    """测试代码唯一性验证"""
    from app.utils.jwt import create_access_token
    
    token = create_access_token(TEST_USER_ID, "admin", ["pricing.create"])
    
    # 先创建价格配置
    config_data = {
        "code": f"CONFIG-{uuid.uuid4().hex[:8]}",
        "name": "测试配置",
        "base_price": 100.00,
        "status": "active",
        "created_by": TEST_USER_ID,
    }
    
    request, config_response = app.test_client.post(
        "/api/v1/price-configs",
        json=config_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    
    config_id = config_response.json["data"]["id"]
    
    # 创建第一个价格区间
    code = f"PB-{uuid.uuid4().hex[:8]}"
    price_band_data = {
        "code": code,
        "name": "测试区间 1",
        "price_config_id": config_id,
        "min_quantity": 1,
        "max_quantity": 100,
        "unit_price": 100.00,
        "discount_rate": 5.0,
        "final_price": 95.00,
        "priority": 1,
        "is_active": True,
    }
    
    response, _ = app.test_client.post(
        "/api/v1/price-bands",
        json=price_band_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status == 200
    
    # 尝试创建相同代码的价格区间
    duplicate_data = {
        **price_band_data,
        "name": "测试区间 2",
    }
    
    request, response = app.test_client.post(
        "/api/v1/price-bands",
        json=duplicate_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status in [400, 422, 500]
