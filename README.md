# fcu-mcp
逢甲大學 iLearn 和 MyFCU 整合 MCP

## Tools
### 1. login
登入 iLearn 和 MyFCU。
```json
{
  "username": "your_username",
  "password": "your_password"
}
```

### 2. get_future_events
從 iLearn 取得未來事件
```json
{
  "username": "your_username",
}
```

### 3. get_course_list
從 MyFCU 取得課表清單
```json
{
  "username": "your_username",
  "year": "113",
  "semester": "1"
}
```