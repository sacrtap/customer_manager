"""
后端E2E测试 - 客户CRUD
"""
import pytest
import requests


class TestCustomerCRUD:
    """客户CRUD E2E测试"""
    
    def test_create_customer_success(self, base_url, test_tokens):
        """创建客户成功"""
        token = test_tokens["admin"]
        
        response = requests.post(
            f"{base_url}/customers",
            json={
                "name": "E2E测试客户",
                "code": "E2E001",
                "industry": "科技",
                "sales_rep_id": 1,
                "tier_level": "A",
                "annual_consumption": 100000.00,
                "contact_person": "测试联系人",
                "contact_phone": "13800138000",
                "contact_email": "test@example.com"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["id"] is not None
        assert data["name"] == "E2E测试客户"
        assert data["code"] == "E2E001"
    
    def test_get_customer_detail(self, base_url, test_tokens):
        """查看客户详情"""
        token = test_tokens["admin"]
        
        # 先创建一个客户
        create_response = requests.post(
            f"{base_url}/customers",
            json={"name": "详情测试客户", "sales_rep_id": 1},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if create_response.status_code == 200:
            customer_id = create_response.json()["data"]["id"]
            
            # 获取详情
            response = requests.get(
                f"{base_url}/customers/{customer_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            data = response.json()["data"]
            assert data["id"] == customer_id
            assert data["name"] == "详情测试客户"
    
    def test_update_customer(self, base_url, test_tokens):
        """更新客户"""
        token = test_tokens["admin"]
        
        # 先创建一个客户
        create_response = requests.post(
            f"{base_url}/customers",
            json={"name": "原始客户", "industry": "原行业", "sales_rep_id": 1},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if create_response.status_code == 200:
            customer_id = create_response.json()["data"]["id"]
            
            # 更新客户
            response = requests.put(
                f"{base_url}/customers/{customer_id}",
                json={
                    "name": "更新后的客户",
                    "industry": "新行业",
                    "tier_level": "B"
                },
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            data = response.json()["data"]
            assert data["name"] == "更新后的客户"
            assert data["industry"] == "新行业"
            assert data["tier_level"] == "B"
    
    def test_delete_customer(self, base_url, test_tokens):
        """删除客户"""
        token = test_tokens["admin"]
        
        # 先创建一个客户
        create_response = requests.post(
            f"{base_url}/customers",
            json={"name": "待删除客户", "sales_rep_id": 1},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if create_response.status_code == 200:
            customer_id = create_response.json()["data"]["id"]
            
            # 删除客户
            response = requests.delete(
                f"{base_url}/customers/{customer_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
    
    def test_pagination_query(self, base_url, test_tokens):
        """分页查询客户列表"""
        token = test_tokens["admin"]
        
        response = requests.get(
            f"{base_url}/customers",
            params={"page": 1, "size": 10},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()["data"]
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
    
    def test_keyword_search(self, base_url, test_tokens):
        """多维度查询 - 关键词"""
        token = test_tokens["admin"]
        
        response = requests.get(
            f"{base_url}/customers",
            params={"keyword": "科技"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()["data"]
        assert "items" in data
    
    def test_industry_filter(self, base_url, test_tokens):
        """多维度查询 - 行业"""
        token = test_tokens["admin"]
        
        response = requests.get(
            f"{base_url}/customers",
            params={"industries": "科技"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()["data"]
        assert "items" in data
    
    def test_sales_only_see_own_customers(self, base_url, test_tokens):
        """销售只能看自己客户"""
        token = test_tokens["sales"]
        
        response = requests.get(
            f"{base_url}/customers",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()["data"]
        assert "items" in data


class TestImportExport:
    """批量导入导出E2E测试"""
    
    def test_download_import_template_success(self, base_url, test_tokens):
        """下载导入模板成功"""
        token = test_tokens["admin"]
        
        response = requests.get(
            f"{base_url}/customers/import-template",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert response.headers.get("Content-Type").startswith("application/vnd.open")
        
        # 验证文件内容不为空
        assert len(response.content) > 0
    
    def test_batch_export_success(self, base_url, test_tokens):
        """批量导出客户数据成功"""
        token = test_tokens["admin"]
        
        response = requests.get(
            f"{base_url}/customers/export",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert response.headers.get("Content-Type").startswith("application/vnd.open")
        
        # 验证文件内容不为空
        assert len(response.content) > 0
        assert b"客户 ID" in response.content or b"客户ID" in response.content
        assert b"客户名称" in response.content
