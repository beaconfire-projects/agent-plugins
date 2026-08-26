---
name: mgt-order-search
description: Search and paginate Beaconfireinc MGT orders. Use when a user asks to find, filter, inspect, or list orders through the MGT MCP service.
---

# MGT 订单列表查询

使用 MGT MCP 服务查询订单列表时，按下面的接口契约构造请求。该契约根据管理后台前端仓库
`/Users/wangn/code/seethingx/beaconfire/fe-management-base/src/pages/Order/`
中的实现整理：

- `services/index.ts`：接口路径和 HTTP 方法
- `index.tsx`：分页参数和响应数据结构
- `FormFields.tsx`：前端实际提交的筛选字段
- `services/type.ts`：订单字段定义

## 接口

- 方法：`GET`
- 路径：`/mgt-api/api/v1/order/ccOrderList`
- 通过 MGT MCP 工具调用时，使用该工具要求的参数对象传递下面的查询参数；不要臆造工具名称或额外参数。

### 基础分页请求

```json
{
  "limit": 10,
  "offset": 1
}
```

**重要：这里的 `offset` 是页码，不是零基记录偏移量。第一页必须使用 `offset=1`。**

管理后台的默认配置是 `limit=10, offset=1`，切换页面时也会直接把页码写入 `offset`：

```text
第 1 页：offset=1
第 2 页：offset=2
第 3 页：offset=3
```

除非 MGT MCP 工具的最新接口说明明确要求不同语义，否则不要将 `offset` 换算成
`(page - 1) * limit`。

## 查询参数

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `limit` | number | 每页数量，默认使用 `10` |
| `offset` | number | 页码，从 `1` 开始；第一页为 `1` |
| `text` | string | 模糊搜索订单编号、注册用户 ID 或商品名称 |
| `sourceType` | number | 订单渠道：`1` 用户下单，`2` 代用户下单，`3` 会员权益用户下单，`4` 会员权益用户下订阅单 |
| `orderStatus` | number | 订单状态：`0` 待支付，`1` 支付成功，`2` 超时关闭，`3` 手动关闭 |
| `beginTime` | string | 查询开始时间，建议使用 ISO 8601 格式 |
| `endTime` | string | 查询结束时间，建议使用 ISO 8601 格式 |

只传递用户实际指定的筛选条件；空筛选项不要传空字符串，避免后端对空值产生歧义。

示例：查询支付成功的订单，第 1 页，每页 20 条：

```json
{
  "limit": 20,
  "offset": 1,
  "orderStatus": 1
}
```

示例：按关键词和时间范围查询：

```json
{
  "limit": 10,
  "offset": 1,
  "text": "123456",
  "beginTime": "2025-01-01T00:00:00Z",
  "endTime": "2025-01-31T23:59:59Z"
}
```

## 响应处理

前端从响应中读取：

```text
ent.items  -> 当前页订单数组
ent.total  -> 订单总数
```

如果 MCP 工具返回了外层响应包装，则先按工具的响应格式解包，再读取 `ent.items` 和
`ent.total`。向用户汇报结果时说明当前页、每页数量和总数；没有结果时明确说明没有匹配订单。

常用订单字段包括：

- `orderId`：订单号
- `skuName`：商品名称
- `userId`：注册用户 ID
- `unRegisterUser`：未注册用户名称
- `sourceType`：订单渠道
- `status`：订单状态
- `orderPayCurrency`：支付币种
- `originalPrice`、`payAmountUsd`、`payAmountCny`、`payAmountCad`：金额字段
- `orderTime`、`payTime`：下单和支付时间

## 查询流程

1. 先确认用户要查的对象、时间范围、状态和页码；信息不足时默认查询第 1 页。
2. 使用 `GET /mgt-api/api/v1/order/ccOrderList` 及最小必要参数查询。
3. 牢记第一页传 `offset=1`，不要发送 `offset=0`。
4. 根据 `ent.total` 判断是否需要继续翻页；翻页时只递增页码，保持 `limit` 和其他筛选条件不变。
5. 对订单状态、订单渠道和金额字段进行可读化展示，但保留 `orderId` 等原始值以便复核。
6. 不要在输出中暴露 OAuth Token、Authorization header 或其他凭据。

## 相关代码

- 前端页面：`src/pages/Order/index.tsx`
- 请求封装：`src/pages/Order/services/index.ts`
- 查询表单：`src/pages/Order/FormFields.tsx`
- 订单类型：`src/pages/Order/services/type.ts`
