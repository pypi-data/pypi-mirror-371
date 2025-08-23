from mcp.server.fastmcp import FastMCP
import sys

app = FastMCP("ai-competition")


@app.tool()
def get_current_time(time_type: str):
    """查询当前时间

    Args:
        time_type: 时间格式化类型

    Returns:
        当前时间格式化后的值
    """
    from datetime import datetime
    return {"time": datetime.now().isoformat()}


@app.tool()
def get_weather(city: str):
    """查询城市的气温和天气

        Args:
            city: 城市名称

        Returns:
            temperature：城市的气温
            weather：城市的天气

    """
    return {"city": city, "temperature": "25°C", "weather": "Sunny"}


def main():
    """主函数，启动MCP服务器"""
    try:
        # 运行FastMCP服务器
        app.run()
    except KeyboardInterrupt:
        print("\n服务器已停止")
        sys.exit(0)
    except Exception as e:
        print(f"服务器启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
