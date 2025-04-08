from huggingface_hub import HfApi
import os

# 设置令牌
token = "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"

# 创建 API 客户端
api = HfApi(token=token)

try:
    # 尝试获取用户信息
    user_info = api.whoami()
    print("令牌有效！")
    print(f"用户名: {user_info['name']}")
    print(f"邮箱: {user_info['email']}")
    print(f"权限: {user_info['auth']}")
except Exception as e:
    print(f"令牌无效或出现错误: {str(e)}")
