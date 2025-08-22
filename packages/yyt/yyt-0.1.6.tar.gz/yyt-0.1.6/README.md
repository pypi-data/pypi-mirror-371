# yyt

多分支 worktree 管理工具（支持 `krepo-ng` 与 `git`）。

## 安装

```bash
pip install yyt
```

## 使用

- 创建 worktree：

```bash
yyt add <path> <branch>
```

这会在 `~/<path>/wpsmain` 和 `~/<path>/wpsweb` 下分别创建或切换到 `<branch>`。

- 列出 worktree：

```bash
yyt list
```

- 移除 worktree：

```bash
yyt remove <path>
```

这会移除 `~/<path>/wpsmain` 和 `~/<path>/wpsweb` 的 worktree，并删除整个 `<path>` 目录。

- 配置管理：

```bash
yyt set work_dir=~/workspace  # 设置工作目录
yyt config                    # 显示当前配置
```

- 修改配置和生成构建脚本（仅限 Linux）：

```bash
yyt modify                    # 修改 wpsweb/server/Makefile 和生成 build_server.sh
yyt modify --force            # 强制在非 Linux 系统上运行（不推荐）
```

这会自动查找 wpsweb 目录，并执行以下操作：
1. **修改 `server/Makefile`**：
   - 去掉 `-Wl,-s` 参数
   - 将 `-O2` 修改为 `-g`
2. **生成 `build_server.sh`**：
   - 清空文件内容并写入构建脚本
   - 动态替换路径变量（基于当前执行路径）
   - 自动设置执行权限

> **注意**: `modify` 命令仅在 Linux 系统上支持，因为它需要修改 Makefile 和生成 shell 脚本。

## 依赖

- 需要本机已安装并在 PATH 中可用：`krepo-ng`、`git`。
- 配置文件位置：`~/.yyt.json`

## 许可

MIT