"""
腾讯云 DNSPod 服务主模块
"""
from asyncio.log import logger
from typing import Any
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
from . import tool_dnspod

server = Server("dnspod")

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict[str, Any] | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """处理工具调用请求"""
    try:
        if name == "DescribeDomainList":
            result = tool_dnspod.DescribeDomainList(
                Type=arguments.get("Type"),
                Offset=arguments.get("Offset", 0),
                Limit=arguments.get("Limit", 20),
                GroupId=arguments.get("GroupId"),
                Keyword=arguments.get("Keyword"),
                Tags=arguments.get("Tags")
            )
        elif name == "CreateDomain":
            result = tool_dnspod.CreateDomain(
                Domain=arguments.get("Domain"),
                GroupId=arguments.get("GroupId"),
                Tags=arguments.get("Tags")
            )
        elif name == "DeleteDomain":
            result = tool_dnspod.DeleteDomain(
                Domain=arguments.get("Domain"),
                DomainId=arguments.get("DomainId")
            )
        elif name == "ModifyDomainStatus":
            result = tool_dnspod.ModifyDomainStatus(
                Domain=arguments.get("Domain"),
                Status=arguments.get("Status"),
                DomainId=arguments.get("DomainId")
            )            
        elif name == "DescribeRecordList":
            result = tool_dnspod.DescribeRecordList(
                Domain=arguments.get("Domain"),
                DomainId=arguments.get("DomainId"),
                Subdomain=arguments.get("Subdomain"),
                RecordType=arguments.get("RecordType"),
                RecordLine=arguments.get("RecordLine"),
                RecordLineId=arguments.get("RecordLineId"),
                GroupId=arguments.get("GroupId"),
                Keyword=arguments.get("Keyword"),
                SortField=arguments.get("SortField"),
                SortType=arguments.get("SortType"),
                Offset=arguments.get("Offset"),
                Limit=arguments.get("Limit")
            )
        elif name == "DescribeRecord":
            result = tool_dnspod.DescribeRecord(
                Domain=arguments.get("Domain"),
                RecordId=arguments.get("RecordId"),
                DomainId=arguments.get("DomainId")
            )
        elif name == "DescribeRecordLineCategoryList":
            result = tool_dnspod.DescribeRecordLineCategoryList(
                Domain=arguments.get("Domain"),
                DomainId=arguments.get("DomainId")
            )
        elif name == "DescribeRecordLineList":
            result = tool_dnspod.DescribeRecordLineList(
                Domain=arguments.get("Domain"),
                DomainGrade=arguments.get("DomainGrade"),
                DomainId=arguments.get("DomainId")
            )
        elif name == "DescribeDomainAnalytics":
            result = tool_dnspod.DescribeDomainAnalytics(
                Domain=arguments.get("Domain"),
                StartDate=arguments.get("StartDate"),
                EndDate=arguments.get("EndDate"),
                DomainId=arguments.get("DomainId"),
                DnsFormat=arguments.get("DnsFormat")
            )
        elif name == "DescribeSubdomainAnalytics":
            result = tool_dnspod.DescribeSubdomainAnalytics(
                Domain=arguments.get("Domain"),
                StartDate=arguments.get("StartDate"),
                EndDate=arguments.get("EndDate"),
                Subdomain=arguments.get("Subdomain"),
                DomainId=arguments.get("DomainId"),
                DnsFormat=arguments.get("DnsFormat")
            )
        else:
            raise ValueError(f"未知的工具: {name}")

        return [types.TextContent(type="text", text=str(result))]
    except Exception as e:
        return [types.TextContent(type="text", text=f"错误: {str(e)}")]

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="DescribeDomainList",
            description="查询DNSPod的域名列表",
            inputSchema={
                "type": "object",
                "properties": {
                    "Type": {
                        "type": "string",
                        "description": "域名分组类型，默认为ALL。可取值为ALL，MINE，SHARE，ISMARK，PAUSE，VIP，RECENT，SHARE_OUT，FREE。示例值：ALL",
                    },
                    "Offset": {
                        "type": "integer",
                        "description": "记录开始的偏移, 第一条记录为 0, 依次类推。默认值为0。示例值：0",
                    },
                    "Limit": {
                        "type": "integer",
                        "description": "要获取的域名数量, 比如获取20个, 则为20。默认值为3000。示例值：20",
                    },
                    "GroupId": {
                        "type": "integer",
                        "description": "分组ID, 获取指定分组的域名。示例值：1",
                    },
                    "Keyword": {
                        "type": "string",
                        "description": "根据关键字搜索域名。示例值：qq",
                    },
                    "Tags": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "标签过滤",
                    },
                },
            },
        ),
        types.Tool(
            name="CreateDomain",
            description="添加DNSPod解析的域名",
            inputSchema={
                "type": "object",
                "properties": {
                    "Domain": {
                        "type": "string",
                        "description": "域名",
                    },
                    "GroupId": {
                        "type": "integer",
                        "description": "分组ID, 获取指定分组的域名。示例值：1",
                    },
                    "Tags": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "绑定标签",
                    },
                },
                "required": ["Domain"],
            },
        ),
        types.Tool(
            name="DeleteDomain",
            description="删除DNSPod解析的域名",
            inputSchema={
                "type": "object",
                "properties": {
                    "Domain": {
                        "type": "string",
                        "description": "域名",
                    },
                    "DomainId": {
                        "type": "integer",
                        "description": "域名 ID 。参数 DomainId 优先级比参数 Domain 高，如果传递参数 DomainId 将忽略参数 Domain 。可以通过接口DescribeDomainList查到所有的Domain以及DomainId",
                    },
                },
                "required": ["Domain"],
            },
        ),
        types.Tool(
            name="ModifyDomainStatus",
            description="修改域名解析状态",
            inputSchema={
                "type": "object",
                "properties": {
                    "Domain": {
                        "type": "string",
                        "description": "域名",
                    },
                    "Status": {
                        "type": "string",
                        "description": "域名状态，”enable” 、”disable” 分别代表启用和暂停示例值：enable",
                    },
                    "DomainId": {
                        "type": "integer",
                        "description": "域名 ID 。参数 DomainId 优先级比参数 Domain 高，如果传递参数 DomainId 将忽略参数 Domain 。可以通过接口DescribeDomainList查到所有的Domain以及DomainId",
                    },
                },
                "required": ["Domain", "Status"],
            },
        ),
        types.Tool(
            name="DescribeRecordList",
            description="查看记录列表",
            inputSchema={
                "type": "object",
                "properties": {
                    "Domain": {
                        "type": "string",
                        "description": "域名",
                    },
                    "DomainId": {
                        "type": "string",
                        "description": "域名 ID 。参数 DomainId 优先级比参数 Domain 高，如果传递参数 DomainId 将忽略参数 Domain 。可以通过接口DescribeDomainList查到所有的Domain以及DomainId。",
                    },
                    "SubDomain": {
                        "type": "string",
                        "description": "主机记录，如 www，如果不传，默认为 @。",
                    },
                    "RecordType": {
                        "type": "string",
                        "description": "获取某种类型的解析记录，如 A，CNAME，NS，AAAA，显性URL，隐性URL，CAA，SPF等。",
                    },
                    "RecordLine": {
                        "type": "string",
                        "description": "记录线路，可以通过接口DescribeRecordLineList查看当前域名允许的线路信息，中文，比如：默认。",
                    },
                    "RecordLineId": {
                        "type": "string",
                        "description": "线路的 ID，可以通过接口DescribeRecordLineList查看当前域名允许的线路信息，英文字符串，比如：10=1。参数RecordLineId优先级高于RecordLine，如果同时传递二者，优先使用RecordLineId参数。",
                    },
                    "GroupId": {
                        "type": "integer",
                        "description": "获取某个分组下的解析记录时，传这个分组Id。可通过DescribeRecordGroupList接口获取所有分组。",
                    },
                    "Keyword": {
                        "type": "string",
                        "description": "通过关键字搜索解析记录，当前支持搜索主机头和记录值。",
                    },
                    "SortField": {
                        "type": "string",
                        "description": "排序字段，支持 name,line,type,value,weight,mx,ttl,updated_on 几个字段。",
                    },
                    "SortType": {
                        "type": "string",
                        "description": "排序方式，正序：ASC，逆序：DESC。默认值为ASC。",
                    },
                    "Offset": {
                        "type": "integer",
                        "description": "偏移量，默认值为0。",
                    },
                    "Limit": {
                        "type": "integer",
                        "description": "限制数量，当前Limit最大支持3000。默认值为100。",
                    },
                },
                "required": ["Domain"],
            },
        ),
        types.Tool(
            name="DescribeRecordLineCategoryList",
            description="按照分类获取线路列表",
            inputSchema={
                "type": "object",
                "properties": {
                    "Domain": {
                        "type": "string",
                        "description": "要查询线路列表的域名。",
                    },
                    "DomainId": {
                        "type": "integer",
                        "description": "要查询线路列表的域名 ID 。参数 DomainId 优先级比参数 Domain 高，如果传递参数 DomainId 将忽略参数 Domain 。可以通过接口DescribeDomainList查到所有的Domain以及DomainId",
                    },
                },
                "required": ["Domain"],
            },
        ),
        types.Tool(
            name="DescribeRecordLineList",
            description="获取等级允许的线路",
            inputSchema={
                "type": "object",
                "properties": {
                    "Domain": {
                        "type": "string",
                        "description": "要查询线路列表的域名。",
                    },
                    "DomainGrade": {
                        "type": "string",
                        "description": "域名套餐等级。 旧套餐：D_FREE、D_PLUS、D_EXTRA、D_EXPERT、D_ULTRA 、DP_EXTRA 分别对应免费套餐、个人豪华、企业 I、企业 II、企业 III、企业基础版。 新套餐：DP_FREE、DP_PLUS、DP_EXPERT、DP_ULTRA 分别对应新免费、专业版、企业版、尊享版。",
                    },
                    "DomainId": {
                        "type": "integer",
                        "description": "要查询线路列表的域名 ID 。参数 DomainId 优先级比参数 Domain 高，如果传递参数 DomainId 将忽略参数 Domain 。可以通过接口DescribeDomainList查到所有的Domain以及DomainId",
                    },
                },
                "required": ["Domain", "DomainGrade"],
            },
        ),
        types.Tool(
            name="DescribeDomainAnalytics",
            description="域名解析量统计",
            inputSchema={
                "type": "object",
                "properties": {
                    "Domain": {
                        "type": "string",
                        "description": "要查询解析量的域名。",
                    },
                    "StartDate": {
                        "type": "string",
                        "description": "查询的开始时间，格式：YYYY-MM-DD。",
                    },
                    "EndDate": {
                        "type": "string",
                        "description": "查询的结束时间，格式：YYYY-MM-DD。",
                    },
                    "DnsFormat": {
                        "type": "string",
                        "description": "DATE:按天维度统计 HOUR:按小时维度统计。",
                    },
                    "DomainId": {
                        "type": "integer",
                        "description": "域名 ID 。参数 DomainId 优先级比参数 Domain 高，如果传递参数 DomainId 将忽略参数 Domain 。可以通过接口DescribeDomainList查到所有的Domain以及DomainId",
                    },
                },
                "required": ["Domain", "StartDate", "EndDate"],
            },
        ),
        types.Tool(
            name="DescribeSubdomainAnalytics",
            description="子域名解析量统计",
            inputSchema={
                "type": "object",
                "properties": {
                    "Domain": {
                        "type": "string",
                        "description": "要查询解析量的域名。",
                    },
                    "StartDate": {
                        "type": "string",
                        "description": "查询的开始时间，格式：YYYY-MM-DD。",
                    },
                    "EndDate": {
                        "type": "string",
                        "description": "查询的结束时间，格式：YYYY-MM-DD。",
                    },
                    "Subdomain": {
                        "type": "string",
                        "description": "要查询解析量的子域名。",
                    },
                    "DnsFormat": {
                        "type": "string",
                        "description": "DATE:按天维度统计 HOUR:按小时维度统计。",
                    },
                    "DomainId": {
                        "type": "integer",
                        "description": "域名 ID 。参数 DomainId 优先级比参数 Domain 高，如果传递参数 DomainId 将忽略参数 Domain 。可以通过接口DescribeDomainList查到所有的Domain以及DomainId",
                    },
                },
                "required": ["Domain", "StartDate", "EndDate", "Subdomain"],
            },
        ),
    ]

async def serve():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        logger.info("Server running with stdio transport")

        await server.run(
            read_stream, 
            write_stream, 
            InitializationOptions(
                server_name="dnspod",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

