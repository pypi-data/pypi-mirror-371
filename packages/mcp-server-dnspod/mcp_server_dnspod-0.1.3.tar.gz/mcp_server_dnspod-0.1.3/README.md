# Tencent Cloud DNS MCP Server
The Tencent Cloud DNS MCP server is implemented to manage authoritative DNS domains, records and obtain DNS resolution statistics.


## Features
- **DNS domains Management:**: Full lifecycle management, including creating, starting, stopping, and deleting DNS domains.
- **Record Management**: Obtain current records. 
- **DNS resolution statistics**: Obtain DNS resolution statistics for a domain or specified subdomains.



## API List
### 
#### DescribeDomainList
Get the list of domains.

**Input Parameters**:
- `Type` (string, optional): The domain group type.
- `Offset` (integer, optional): Offset, default 0.
- `Limit` (integer, optional): Number of results, default 20, max 100.
- `GroupId` (integer, optional): Group ID, which can be passed in to get all domains in the specified group.
- `Keyword` (integer, optional) Keyword for searching for a domain.
- `Tags` (array[string], optional): Filter by Tags.

#### CreateDomain
Create a domain.

**Input Parameters**:
- `Domain` (string): Domain.
- `GroupId` (integer, optional): Group ID, which can be passed in to get all domains in the specified group.
- `Tags` (array[string], optional): Bind tags for domain.

#### DeleteDomain
delete a domain.

**Input Parameters**:
- `Domain` (string): Domain.
- `DomainId` (integer, optional): The domain ID.

#### ModifyDomainStatus
Modify the status of a domain.

**Input Parameters**:
- `Domain` (string): Domain.
- `Status` (string): Domain status. Valid values: enable; disable.
- `DomainId` (integer, optional): The domain ID.

#### DescribeRecordList
Modify the status of a domain.

**Input Parameters**:
- `Domain` (string): Domain.
- `DomainId` (string, optional): The ID of the domain whose DNS records are requested.
- `SubDomain` (string, optional): The host header of a DNS record.
- `RecordType` (string, optional): The type of DNS record.
- `RecordLine` (string, optional): The name of the split zone for which DNS records are requested.
- `RecordLineId` (string, optional): The ID of the split zone for which DNS records are requested.
- `GroupId` (integer, optional): The group ID passed in to get DNS records in the group.
- `Keyword` (string, optional): The keyword for searching for DNS records.
- `SortField` (string, optional): The sorting field.
- `SortType` (string, optional): The sorting type.
- `Offset` (integer, optional): The offset.
- `Limit` (integer, optional): The limit.


#### DescribeRecordLineList
get record lines by domain and domain grade .

**Input Parameters**:
- `Domain` (string): Domain.
- `DomainGrade` (string): Domain grade.
- `DomainId` (integer, optional): Domain ID.

#### DescribeDomainAnalytics
get dns resolution statistics of domain.

**Input Parameters**:
- `Domain` (string): Domain.
- `StartDate` (string): Start Date, Format: YYYY-MM-DD.
- `EndDate` (string): End Date, Format: YYYY-MM-DD.
- `DnsFormat` (string): Format type, Date/Hour.
- `DomainId` (integer, optional): Domain ID.

#### DescribeSubdomainAnalytics
get dns resolution statistics of subdomain.

**Input Parameters**:
- `Domain` (string): Domain.
- `StartDate` (string): Start Date, Format: YYYY-MM-DD.
- `EndDate` (string): End Date, Format: YYYY-MM-DD.
- `Subdomain` (string): Host record such as www.
- `DnsFormat` (string): Format type, Date/Hour.
- `DomainId` (integer, optional): Domain ID.


## Configuration
### Set Tencent Cloud Credentials
1. Obtain SecretId and SecretKey from Tencent Cloud Console
2. Set default region (optional)

### Environment Variables
Configure the following environment variables:
- `TENCENTCLOUD_SECRET_ID`: Tencent Cloud SecretId
- `TENCENTCLOUD_SECRET_KEY`: Tencent Cloud SecretKey  
- `TENCENTCLOUD_REGION`: Default region (optional)

### Usage in Claude Desktop
Add the following configuration to claude_desktop_config.json:

```json
{
  "mcpServers": {
    "tencent-dnspod": {
      "command": "uv",
      "args": [
        "run",
        "mcp-server-dnspod"
      ],
      "env": {
        "TENCENTCLOUD_SECRET_ID": "YOUR_SECRET_ID_HERE",
        "TENCENTCLOUD_SECRET_KEY": "YOUR_SECRET_KEY_HERE",
        "TENCENTCLOUD_REGION": "YOUR_REGION_HERE"
      }
    }
  }
}
```

## Installation
```sh
pip install mcp-server-dnspod
```

## License
MIT License. See LICENSE file for details.
