"""
腾讯云客户端创建模块
"""
import os
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.common_client import CommonClient
from tencentcloud.dnspod.v20210323 import dnspod_client

# 从环境变量中读取认证信息
secret_id = os.getenv("TENCENTCLOUD_SECRET_ID")
secret_key = os.getenv("TENCENTCLOUD_SECRET_KEY")
default_region = os.getenv("TENCENTCLOUD_REGION")

def get_common_client(region: str = None, product = "dnspod", version="2021-03-23") -> CommonClient:
    """
    创建并返回通用客户端实例

    Args:
        region: 地域信息
        product: 产品名称
        version: 产品版本

    Returns:
        CommonClient: 通用客户端实例
    """
    cred = credential.Credential(secret_id, secret_key)
    if not region:
        region = default_region or "ap-guangzhou"

    http_profile = HttpProfile()
    http_profile.endpoint = "dnspod.tencentcloudapi.com"

    client_profile = ClientProfile()
    client_profile.httpProfile = http_profile
    client_profile.request_client = "MCP-Server"

    return CommonClient(product, version, cred, region, profile=client_profile)

def get_dnspod_client(region: str = None) -> dnspod_client.DnspodClient:
    """
    创建并返回DNSPod客户端

    Args:
        region: 地域信息

    Returns:
        DnspodClient: DNSPod客户端实例
    """
    cred = credential.Credential(secret_id, secret_key)
    if not region:
        region = default_region or "ap-guangzhou"

    http_profile = HttpProfile()
    http_profile.endpoint = "dnspod.tencentcloudapi.com"

    client_profile = ClientProfile()
    client_profile.httpProfile = http_profile
    client_profile.request_client = "MCP-Server"

    return dnspod_client.DnspodClient(cred, region, client_profile)
