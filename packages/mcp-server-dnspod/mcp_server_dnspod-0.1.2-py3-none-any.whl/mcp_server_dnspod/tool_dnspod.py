"""
腾讯云 DNSPod 相关操作工具模块
"""
import json
from tencentcloud.dnspod.v20210323 import dnspod_client, models as dnspod_models
from .capi_client import get_dnspod_client, get_common_client
from asyncio.log import logger
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
import random
import string
import re
from typing import Optional, Tuple

def DescribeDomainList(Type: str=None, Offset: int=None, Limit: int=None, GroupId: int=None, Keyword: str=None, Tags: list=None) -> str:
    """查询域名列表"""
    client = get_dnspod_client() # 使用默认地域
    req = dnspod_models.DescribeDomainListRequest()

    params = {}
    if Type is not None:
        params["Type"] = Type
    if Offset is not None:
        params["Offset"] = Offset
    if Limit is not None:
        params["Limit"] = Limit
    if GroupId is not None:
        params["GroupId"] = GroupId
    if Keyword is not None:
        params["Keyword"] = Keyword
    if Tags is not None:
        params["Tags"] = Tags
    
    req.from_json_string(json.dumps(params))
    resp = client.DescribeDomainList(req)

    return resp.to_json_string()

def CreateDomain(Domain: str, GroupId: int=None, Tags: list=None) -> str:
    """添加域名"""
    client = get_dnspod_client()
    req = dnspod_models.CreateDomainRequest()

    params = {
        "Domain": Domain
    }
    if GroupId is not None:
        params["GroupId"] = GroupId
    if Tags is not None:
        params["Tags"] = Tags
    
    req.from_json_string(json.dumps(params))
    resp = client.CreateDomain(req)

    return resp.to_json_string()

def DeleteDomain(Domain: str, DomainId: int=None) -> str:
    """删除域名"""
    client = get_dnspod_client()
    req = dnspod_models.DeleteDomainRequest()

    params = {
        "Domain": Domain
    }
    if DomainId is not None:
        params["DomainId"] = DomainId
    
    req.from_json_string(json.dumps(params))
    resp = client.DeleteDomain(req)

    return resp.to_json_string()
    
def ModifyDomainStatus(Domain: str, Status: str,  DomainId: int=None) -> str:
    """修改域名解析状态"""
    client = get_dnspod_client()
    req = dnspod_models.ModifyDomainStatusRequest()

    params = {
        "Domain": Domain,
        "Status": Status
    }
    if DomainId is not None:
        params["DomainId"] = DomainId
    
    req.from_json_string(json.dumps(params))
    resp = client.ModifyDomainStatus(req)

    return resp.to_json_string()

def DescribeRecordList(Domain: str, DomainId: int=None, Subdomain: str=None, RecordType: str=None, 
                RecordLine: str=None, RecordLineId: str=None,GroupId: int=None, Keyword: str=None,
                SortField: str=None, SortType: str=None, Offset: int=None, Limit: int=None) -> str:
    """添加记录"""
    client = get_dnspod_client()
    req = dnspod_models.DescribeRecordListRequest()

    params = {
        "Domain": Domain
    }
    if DomainId is not None:
        params["DomainId"] = DomainId
    if Subdomain is not None:
        params["Subdomain"] = Subdomain
    if RecordType is not None:
        params["RecordType"] = RecordType
    if RecordLine is not None:
        params["RecordLine"] = RecordLine
    if RecordLineId is not None:
        params["RecordLineId"] = RecordLineId
    if GroupId is not None:
        params["GroupId"] = GroupId
    if RecordLineId is not None:
        params["RecordLineId"] = RecordLineId
    if Keyword is not None:
        params["Keyword"] = Keyword
    if SortField is not None:
        params["SortField"] = SortField
    if SortType is not None:
        params["SortType"] = SortType
    if Offset is not None:
        params["Offset"] = Offset
    if Limit is not None:
        params["Limit"] = Limit
    
    req.from_json_string(json.dumps(params))
    resp = client.DescribeRecordList(req)

    return resp.to_json_string()

def DescribeRecord(Domain: str, RecordId: int, DomainId: int=None) -> str:
    """获取记录信息"""
    client = get_dnspod_client()
    req = dnspod_models.DescribeRecordRequest()

    params = {
        "Domain": Domain,
        "RecordId": RecordId
    }
    if DomainId is not None:
        params["DomainId"] = DomainId

    
    req.from_json_string(json.dumps(params))
    resp = client.DescribeRecord(req)

    return resp.to_json_string()


def CreateRecord(Domain: str, RecordType: str, RecordLine: str, Value: str, 
                DomainId: int=None, SubDomain: str=None, RecordLineId: str=None,
                MX: int=None,TTL: int=None, Weight: int=None, Status: str=None,
                Remark: str=None, DnssecConflictMode: str=None, GroupId: int=None) -> str:
    """添加记录"""
    client = get_dnspod_client()
    req = dnspod_models.CreateRecordRequest()

    params = {
        "Domain": Domain,
        "RecordType": RecordType,
        "RecordLine": RecordLine,
        "Value": Value,
    }
    if DomainId is not None:
        params["DomainId"] = DomainId
    if SubDomain is not None:
        params["SubDomain"] = SubDomain
    if RecordLineId is not None:
        params["RecordLineId"] = RecordLineId
    if MX is not None:
        params["MX"] = MX
    if TTL is not None:
        params["TTL"] = TTL
    if Weight is not None:
        params["Weight"] = Weight
    if Status is not None:
        params["Status"] = Status
    if Remark is not None:
        params["Remark"] = Remark
    if DnssecConflictMode is not None:
        params["DnssecConflictMode"] = DnssecConflictMode
    if GroupId is not None:
        params["GroupId"] = GroupId
    
    
    req.from_json_string(json.dumps(params))
    resp = client.CreateRecord(req)

    return resp.to_json_string()

def ModifyRecord(Domain: str, RecordType: str, RecordLine: str, Value: str, RecordId: int, 
                DomainId: int=None, SubDomain: str=None, RecordLineId: str=None,
                MX: int=None,TTL: int=None, Weight: int=None, Status: str=None,
                Remark: str=None, DnssecConflictMode: str=None) -> str:
    """修改记录"""
    client = get_dnspod_client()
    req = dnspod_models.ModifyRecordRequest()

    params = {
        "Domain": Domain,
        "RecordType": RecordType,
        "RecordLine": RecordLine,
        "Value": Value,
        "RecordId": RecordId,
    }
    if DomainId is not None:
        params["DomainId"] = DomainId
    if SubDomain is not None:
        params["SubDomain"] = SubDomain
    if RecordLineId is not None:
        params["RecordLineId"] = RecordLineId
    if MX is not None:
        params["MX"] = MX
    if TTL is not None:
        params["TTL"] = TTL
    if Weight is not None:
        params["Weight"] = Weight
    if Status is not None:
        params["Status"] = Status
    if Remark is not None:
        params["Remark"] = Remark
    if DnssecConflictMode is not None:
        params["DnssecConflictMode"] = DnssecConflictMode
    
    req.from_json_string(json.dumps(params))
    resp = client.ModifyRecord(req)

    return resp.to_json_string()

def DeleteRecord(Domain: str, RecordId: int, DomainId: int=None) -> str:
    """删除记录"""
    client = get_dnspod_client()
    req = dnspod_models.DeleteRecordRequest()
    params = {
        "Domain": Domain,
        "RecordId": RecordId,
    }
    if DomainId is not None:
        params["DomainId"] = DomainId

    req.from_json_string(json.dumps(params))
    resp = client.DeleteRecord(req)

    return resp.to_json_string()

def ModifyRecordStatus(Domain: str, RecordId: int, Status: str,  DomainId: int=None) -> str:
    """修改域名解析状态"""
    client = get_dnspod_client()
    req = dnspod_models.ModifyRecordStatusRequest()

    params = {
        "Domain": Domain,
        "RecordId": RecordId,
        "Status": Status
    }
    if DomainId is not None:
        params["DomainId"] = DomainId
    
    req.from_json_string(json.dumps(params))
    resp = client.ModifyRecordStatus(req)

    return resp.to_json_string()

def DescribeRecordLineCategoryList(Domain: str, DomainId: int=None) -> str:
    """按照分类获取线路列表"""
    client = get_dnspod_client()
    req = dnspod_models.DescribeRecordLineCategoryListRequest()
    params = {
        "Domain": Domain,
    }
    if DomainId is not None:
        params["DomainId"] = DomainId

    req.from_json_string(json.dumps(params))
    resp = client.DescribeRecordLineCategoryList(req)

    return resp.to_json_string()

def DescribeRecordLineList(Domain: str, DomainGrade: str, DomainId: int=None) -> str:
    """获取线路列表"""
    client = get_dnspod_client()
    req = dnspod_models.DescribeRecordLineListRequest()
    params = {
        "Domain": Domain,
        "DomainGrade": DomainGrade,
    }
    if DomainId is not None:
        params["DomainId"] = DomainId

    req.from_json_string(json.dumps(params))
    resp = client.DescribeRecordLineList(req)

    return resp.to_json_string()

def DescribeDomainAnalytics(Domain: str, StartDate: str, EndDate: str, DnsFormat: str=None, DomainId: int=None) -> str:
    """查看域名的解析量统计"""
    client = get_dnspod_client()
    req = dnspod_models.DescribeDomainAnalyticsRequest()
    params = {
        "Domain": Domain,
        "StartDate": StartDate,
        "EndDate": EndDate,
    }
    if DomainId is not None:
        params["DomainId"] = DomainId
    if DnsFormat is not None:
        params["DnsFormat"] = DnsFormat

    req.from_json_string(json.dumps(params))
    resp = client.DescribeDomainAnalytics(req)

    return resp.to_json_string()

def DescribeSubdomainAnalytics(Domain: str, StartDate: str, EndDate: str, Subdomain: str, 
                            DnsFormat: str=None, DomainId: int=None) -> str:
    """查看子域名的解析量统计"""
    client = get_dnspod_client()
    req = dnspod_models.DescribeSubdomainAnalyticsRequest()
    params = {
        "Domain": Domain,
        "StartDate": StartDate,
        "EndDate": EndDate,
        "Subdomain": Subdomain,
    }
    if DomainId is not None:
        params["DomainId"] = DomainId
    if DnsFormat is not None:
        params["DnsFormat"] = DnsFormat

    req.from_json_string(json.dumps(params))
    resp = client.DescribeSubdomainAnalytics(req)

    return resp.to_json_string()