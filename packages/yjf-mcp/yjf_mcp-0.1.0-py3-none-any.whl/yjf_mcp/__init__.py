from mcp.server.fastmcp import FastMCP
from .user_location import UserLocationQuery

mcp = FastMCP('Find the location of Yang Jianfei')

# 创建位置查询实例
location_query = UserLocationQuery()

@mcp.tool()
def get_user_latest_location(user_id: int=1, limit: int = 1) -> str:
    """
    获取“杨建飞(Yang Jianfei)”用户的最新位置记录
    
    Args:
        user_id: 用户ID，默认为1
        limit: 返回记录数量限制，默认为1
        
    Returns:
        JSON格式的位置信息
    """
    result = location_query.get_latest_locations(user_id=user_id, limit=limit)
    return str(result)


def main() -> None:
    mcp.run(transport='stdio')
