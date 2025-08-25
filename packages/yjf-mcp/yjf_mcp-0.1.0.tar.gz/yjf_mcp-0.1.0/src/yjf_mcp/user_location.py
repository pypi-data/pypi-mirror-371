#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户位置查询模块
基于PHP脚本进行位置查询并返回相关数据
参考 test_get_latest.html 的查询逻辑
"""

import requests
import json
from datetime import datetime
from typing import List, Dict, Optional, Union


class UserLocationQuery:
    """用户位置查询类"""
    
    def __init__(self, base_url: str = "http://39.98.54.173:40013/VocalBuddy/API"):
        """
        初始化位置查询器
        
        Args:
            base_url: API基础URL
        """
        self.base_url = base_url.rstrip('/')
        self.php_script = "get_latest_locations.php"
        self.full_url = f"{self.base_url}/{self.php_script}"
    
    def get_latest_locations(self, user_id: Optional[int] = None, limit: int = 3) -> Dict[str, Union[bool, str, int, List[Dict]]]:
        """
        获取最新位置记录
        
        Args:
            user_id: 用户ID，如果为None则查询所有用户
            limit: 返回记录数量限制
            
        Returns:
            包含查询结果的字典
        """
        try:
            # 构建查询参数
            params = {'limit': limit}
            if user_id is not None:
                params['user_id'] = user_id
            
            # 发送GET请求
            response = requests.get(self.full_url, params=params, timeout=10)
            response.raise_for_status()
            
            # 解析JSON响应
            result = response.json()
            
            # 格式化返回数据
            if result.get('success') and 'data' in result:
                formatted_data = []
                for item in result['data']:
                    formatted_item = {
                        'id': item.get('id'),
                        'user_id': item.get('user_id'),
                        'latitude': item.get('latitude'),
                        'longitude': item.get('longitude'),
                        'address': item.get('address', '未提供'),
                        'recorded_at': item.get('recorded_at'),
                        'formatted_time': self._format_datetime(item.get('recorded_at'))
                    }
                    formatted_data.append(formatted_item)
                
                result['data'] = formatted_data
                result['message'] = '查询成功'
            
            return result
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'message': f'网络错误: {str(e)}',
                'data': [],
                'count': 0
            }
        except json.JSONDecodeError as e:
            return {
                'success': False,
                'message': f'JSON解析错误: {str(e)}',
                'data': [],
                'count': 0
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'未知错误: {str(e)}',
                'data': [],
                'count': 0
            }
    
    def get_user_latest_location(self, user_id: int) -> Dict[str, Union[bool, str, Dict]]:
        """
        获取指定用户的最新位置记录
        
        Args:
            user_id: 用户ID
            
        Returns:
            包含用户最新位置信息的字典
        """
        result = self.get_latest_locations(user_id=user_id, limit=1)
        
        if result.get('success') and result.get('data'):
            return {
                'success': True,
                'message': '获取用户最新位置成功',
                'location': result['data'][0]
            }
        else:
            return {
                'success': False,
                'message': result.get('message', '未找到用户位置记录'),
                'location': None
            }
    
    def get_all_users_latest_locations(self, limit: int = 10) -> Dict[str, Union[bool, str, List[Dict]]]:
        """
        获取所有用户的最新位置记录
        
        Args:
            limit: 返回记录数量限制
            
        Returns:
            包含所有用户最新位置记录的字典
        """
        return self.get_latest_locations(user_id=None, limit=limit)
    
    def get_location_statistics(self, limit: int = 50) -> Dict[str, Union[bool, str, Dict]]:
        """
        获取位置统计信息
        
        Args:
            limit: 查询记录数量限制
            
        Returns:
            包含统计信息的字典
        """
        result = self.get_latest_locations(user_id=None, limit=limit)
        
        if result.get('success'):
            data = result.get('data', [])
            unique_users = list(set(item.get('user_id') for item in data if item.get('user_id')))
            latest_record = data[0] if data else None
            
            stats = {
                'total_records': len(data),
                'unique_users': len(unique_users),
                'latest_user': latest_record.get('user_id') if latest_record else None,
                'latest_time': latest_record.get('formatted_time') if latest_record else None,
                'users_list': unique_users
            }
            
            return {
                'success': True,
                'message': '统计信息获取成功',
                'statistics': stats
            }
        else:
            return {
                'success': False,
                'message': result.get('message', '获取统计信息失败'),
                'statistics': None
            }
    
    def _format_datetime(self, datetime_str: Optional[str]) -> str:
        """
        格式化日期时间字符串
        
        Args:
            datetime_str: 日期时间字符串
            
        Returns:
            格式化后的日期时间字符串
        """
        if not datetime_str:
            return '未知时间'
        
        try:
            # 尝试解析不同的日期时间格式
            formats = [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%dT%H:%M:%S.%f',
                '%Y-%m-%dT%H:%M:%SZ'
            ]
            
            for fmt in formats:
                try:
                    dt = datetime.strptime(datetime_str, fmt)
                    return dt.strftime('%Y-%m-%d %H:%M:%S')
                except ValueError:
                    continue
            
            # 如果所有格式都失败，返回原始字符串
            return datetime_str
            
        except Exception:
            return '时间格式错误'


# 便捷函数
def get_user_location(user_id: int, limit: int = 1) -> Dict[str, Union[bool, str, List[Dict]]]:
    """
    获取用户位置信息的便捷函数
    
    Args:
        user_id: 用户ID
        limit: 返回记录数量限制
        
    Returns:
        包含位置信息的字典
    """
    query = UserLocationQuery()
    return query.get_latest_locations(user_id=user_id, limit=limit)


def get_all_locations(limit: int = 10) -> Dict[str, Union[bool, str, List[Dict]]]:
    """
    获取所有位置记录的便捷函数
    
    Args:
        limit: 返回记录数量限制
        
    Returns:
        包含所有位置记录的字典
    """
    query = UserLocationQuery()
    return query.get_latest_locations(user_id=None, limit=limit)


def get_location_stats(limit: int = 50) -> Dict[str, Union[bool, str, Dict]]:
    """
    获取位置统计信息的便捷函数
    
    Args:
        limit: 查询记录数量限制
        
    Returns:
        包含统计信息的字典
    """
    query = UserLocationQuery()
    return query.get_location_statistics(limit=limit)


# 测试函数
def test_user_location_query():
    """
    测试用户位置查询功能
    """
    print("=== 测试用户位置查询功能 ===")
    
    # 创建查询实例
    query = UserLocationQuery()
    
    # 测试1: 获取所有用户最新位置
    print("\n1. 获取所有用户最新位置记录:")
    result = query.get_all_users_latest_locations(limit=3)
    print(f"结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    # 测试2: 获取特定用户位置
    print("\n2. 获取特定用户位置记录:")
    result = query.get_latest_locations(user_id=1, limit=2)
    print(f"结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    # 测试3: 获取统计信息
    print("\n3. 获取位置统计信息:")
    result = query.get_location_statistics(limit=10)
    print(f"结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    # 测试4: 使用便捷函数
    print("\n4. 使用便捷函数测试:")
    result = get_user_location(user_id=1)
    print(f"结果: {json.dumps(result, ensure_ascii=False, indent=2)}")

