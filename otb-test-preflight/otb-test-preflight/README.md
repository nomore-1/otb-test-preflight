# OpenTenBase test preflight

面向 OpenTenBase 测试框架的只读环境预检 CLI 与 Agent Skill。参考官方 [`precheck.py`](https://github.com/OpenTenBase/OpenTenBase/blob/master/src/test/opentenbase_test/precheck.py)：现有检查要求 OPENTENBASE_HOME 与 PATH 一致，并比较安装和源码构建的 postgres。本工具将这些检查独立为无需启动集群的 JSON CLI，同时检查 psql、可执行权限和真实路径，汇总全部结果而不是遇到首个错误立即退出。二进制差异仅作为警告，不设置等待。

## 使用

Python 3.8+，无第三方依赖。在 Linux/macOS 终端运行：

```sh
python3 scripts/preflight.py --home /opt/opentenbase
python3 scripts/preflight.py --source-postgres /path/to/OpenTenBase/src/backend/postgres
```

默认读取 OPENTENBASE_HOME 和 PATH；可选源码二进制对比使用 SHA-256。退出码 0 表示无失败（可能含警告），1 表示至少一项检查失败。`skip` 表示未提供源码二进制，不等于通过。报告包含本地路径，分享前注意脱敏。

Agent 可读取 `SKILL.md` 并调用上述 CLI。无需 API key、GPU、数据库连接。仅验证本地文件与 PATH，不检查远程节点、配置、端口或实际集群就绪状态。

## 测试

```sh
python3 -m unittest discover -s tests -v
```

测试使用临时目录及模拟可执行文件（不会执行文件内容），覆盖缺失环境变量、工具缺失、权限、PATH 遮蔽、符号链接、二进制比较及退出码。见 `examples/tests.log`。`examples/demo.json` 为模拟安装目录中运行工具得到的输出，路径已替换，非真实集群验证。
