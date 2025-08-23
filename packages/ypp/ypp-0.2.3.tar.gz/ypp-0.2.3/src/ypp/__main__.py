#!/usr/bin/env python3
import argparse
import json
import os
import platform
import shutil
import subprocess
import sys

try:
    from .makefile_modifier import command_modify_makefile
    from .auto_build import command_auto_build
except ImportError:
    from makefile_modifier import command_modify_makefile
    from auto_build import command_auto_build


def run_command(command_args, cwd_path=None) -> int:
    process = subprocess.Popen(
        command_args,
        cwd=cwd_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    assert process.stdout is not None
    for line in process.stdout:
        sys.stdout.write(line)
    process.wait()
    return process.returncode


def ensure_directory(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def path_exists_and_not_empty(path: str) -> bool:
    return os.path.exists(path) and any(True for _ in os.scandir(path))


def get_config_path() -> str:
    """获取配置文件路径"""
    return os.path.expanduser("~/.ypp.json")


def load_config() -> dict:
    """加载配置文件"""
    config_path = get_config_path()
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}


def save_config(config: dict) -> None:
    """保存配置文件"""
    config_path = get_config_path()
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except IOError as e:
        print(f"保存配置文件失败: {e}", file=sys.stderr)
        sys.exit(1)


def is_linux_system() -> bool:
    """检查是否为 Linux 系统"""
    return platform.system().lower() == "linux"


def get_workspace_dir() -> str:
    """获取配置的 workspace 路径，如果没有配置则使用默认路径"""
    config = load_config()
    workspace_path = config.get('work_dir')
    
    if workspace_path:
        return os.path.expanduser(workspace_path)
    
    # 默认逻辑：如果 ~/workspace 存在，使用它，否则使用 ~
    default_workspace = os.path.expanduser("~/workspace")
    return default_workspace if os.path.isdir(default_workspace) else os.path.expanduser("~")


def ng_sync(master_repo_path: str) -> None:
    if shutil.which("krepo-ng") is None:
        print("找不到 krepo-ng 命令，请先安装或配置 PATH。", file=sys.stderr)
        sys.exit(2)
    print(f"[krepo-ng] 同步仓库: {master_repo_path}")
    rc = run_command(["krepo-ng", "sync"], cwd_path=master_repo_path)
    if rc != 0:
        print("krepo-ng sync 失败", file=sys.stderr)
        sys.exit(rc)


def ng_worktree_add(master_repo_path: str, target_path: str, branch: str) -> None:
    if shutil.which("krepo-ng") is None:
        print("找不到 krepo-ng 命令，请先安装或配置 PATH。", file=sys.stderr)
        sys.exit(2)
    print(f"[krepo-ng] 创建 worktree -> {target_path} @ {branch}")
    rc = run_command(["krepo-ng", "worktree", "add", target_path, branch], cwd_path=master_repo_path)
    if rc != 0:
        sys.exit(rc)


def git_sync(master_repo_path: str) -> None:
    if shutil.which("git") is None:
        print("找不到 git 命令，请先安装或配置 PATH。", file=sys.stderr)
        sys.exit(2)
    print(f"[git] 同步仓库: {master_repo_path}")
    rc = run_command(["git", "pull"], cwd_path=master_repo_path)
    if rc != 0:
        print("git pull 失败", file=sys.stderr)
        sys.exit(rc)


def git_branch_exists(master_repo_path: str, branch: str) -> bool:
    has_local = run_command(["git", "show-ref", "--verify", f"refs/heads/{branch}"], cwd_path=master_repo_path) == 0
    return has_local


def git_worktree_add(master_repo_path: str, target_path: str, branch: str) -> None:
    if shutil.which("git") is None:
        print("找不到 git 命令，请先安装或配置 PATH。", file=sys.stderr)
        sys.exit(2)
    print(f"[git] 创建 worktree -> {target_path} @ {branch}")
    rc = run_command(["git", "worktree", "add", target_path, branch], cwd_path=master_repo_path)
    if rc != 0:
        sys.exit(rc)


def git_worktree_list(master_repo_path: str) -> None:
    if shutil.which("git") is None:
        print("找不到 git 命令，请先安装或配置 PATH。", file=sys.stderr)
        sys.exit(2)
    print(f"[git] worktree list @ {master_repo_path}")
    rc = run_command(["git", "worktree", "list"], cwd_path=master_repo_path)
    if rc != 0:
        sys.exit(rc)


def ng_worktree_remove(master_repo_path: str, target_path: str) -> None:
    if shutil.which("krepo-ng") is None:
        print("找不到 krepo-ng 命令，请先安装或配置 PATH。", file=sys.stderr)
        sys.exit(2)
    print(f"[krepo-ng] 移除 worktree -> {target_path}")
    rc = run_command(["krepo-ng", "worktree", "remove", target_path], cwd_path=master_repo_path)
    if rc != 0:
        sys.exit(rc)


def git_worktree_remove(master_repo_path: str, target_path: str) -> None:
    if shutil.which("git") is None:
        print("找不到 git 命令，请先安装或配置 PATH。", file=sys.stderr)
        sys.exit(2)
    print(f"[git] 移除 worktree -> {target_path}")
    rc = run_command(["git", "worktree", "remove", target_path], cwd_path=master_repo_path)
    if rc != 0:
        sys.exit(rc)


def command_add(path_value: str, branch_value: str) -> None:
    home_dir = get_workspace_dir()
    # wpsmain via krepo-ng
    master_wpsmain_path = os.path.join(home_dir, "master", "wpsmain")
    if not os.path.isdir(master_wpsmain_path):
        print(f"未找到主仓库目录: {master_wpsmain_path}", file=sys.stderr)
        sys.exit(1)

    target_root = os.path.join(home_dir, path_value)
    target_wpsmain_path = os.path.join(target_root, "wpsmain")
    if not path_exists_and_not_empty(target_wpsmain_path):
        ensure_directory(target_wpsmain_path)
        ng_sync(master_wpsmain_path)
        ng_worktree_add(master_wpsmain_path, target_wpsmain_path, branch_value)

    # wpsweb via git
    master_wpsweb_path = os.path.join(home_dir, "master", "wpsweb")
    if not os.path.isdir(master_wpsweb_path):
        print(f"未找到主仓库目录: {master_wpsweb_path}", file=sys.stderr)
        sys.exit(1)

    target_wpsweb_path = os.path.join(target_root, "wpsweb")
    if not path_exists_and_not_empty(target_wpsweb_path):
        ensure_directory(target_wpsweb_path)
        git_sync(master_wpsweb_path)
        git_worktree_add(master_wpsweb_path, target_wpsweb_path, branch_value)

    print("完成。")


def command_list() -> None:
    home_dir = get_workspace_dir()
    master_wpsmain_path = os.path.join(home_dir, "master", "wpsmain")
    master_wpsweb_path = os.path.join(home_dir, "master", "wpsweb")

    if not os.path.isdir(master_wpsmain_path):
        print(f"未找到主仓库目录: {master_wpsmain_path}", file=sys.stderr)
        sys.exit(1)
    if not os.path.isdir(master_wpsweb_path):
        print(f"未找到主仓库目录: {master_wpsweb_path}", file=sys.stderr)
        sys.exit(1)

    print("=== wpsmain worktrees ===")
    git_worktree_list(master_wpsmain_path)
    print("\n=== wpsweb worktrees ===")
    git_worktree_list(master_wpsweb_path)


def command_remove(path_value: str) -> None:
    home_dir = get_workspace_dir()
    
    # wpsmain via krepo-ng
    master_wpsmain_path = os.path.join(home_dir, "master", "wpsmain")
    if not os.path.isdir(master_wpsmain_path):
        print(f"未找到主仓库目录: {master_wpsmain_path}", file=sys.stderr)
        sys.exit(1)

    remove_wpsmain_path = os.path.join(path_value, "wpsmain")
    if os.path.exists(remove_wpsmain_path):
        ng_worktree_remove(master_wpsmain_path, remove_wpsmain_path)
    else:
        print(f"wpsmain worktree 不存在: {remove_wpsmain_path}")

    # wpsweb via git
    master_wpsweb_path = os.path.join(home_dir, "master", "wpsweb")
    if not os.path.isdir(master_wpsweb_path):
        print(f"未找到主仓库目录: {master_wpsweb_path}", file=sys.stderr)
        sys.exit(1)

    remove_wpsweb_path = os.path.join(path_value, "wpsweb")
    if os.path.exists(remove_wpsweb_path):
        git_worktree_remove(master_wpsweb_path, remove_wpsweb_path)
    else:
        print(f"wpsweb worktree 不存在: {remove_wpsweb_path}")

    # 删除整个路径目录
    if os.path.exists(path_value):
        try:
            shutil.rmtree(path_value)
            print(f"已删除目录: {path_value}")
        except OSError as e:
            print(f"删除目录失败: {path_value}, 错误: {e}", file=sys.stderr)
    else:
        print(f"目录不存在: {path_value}")
    
    print("完成。")


def command_set(key_value: str) -> None:
    """设置配置项。用法: set <key>=<value>"""
    # 解析 key=value 格式
    if '=' not in key_value:
        print("错误: 请使用 'key=value' 格式", file=sys.stderr)
        print("示例: ypp set work_dir=~/workspace", file=sys.stderr)
        sys.exit(1)
    
    parts = key_value.split('=', 1)
    if len(parts) != 2:
        print("错误: 请使用 'key=value' 格式", file=sys.stderr)
        sys.exit(1)
    
    key = parts[0].strip()
    value = parts[1].strip()
    
    if not key:
        print("错误: 配置项名称不能为空", file=sys.stderr)
        sys.exit(1)
    
    config = load_config()
    
    # 处理不同类型的配置项
    if key == 'work_dir':
        # 展开用户路径
        expanded_value = os.path.expanduser(value)
        if not os.path.isdir(expanded_value):
            print(f"错误: 指定的路径不存在: {expanded_value}", file=sys.stderr)
            sys.exit(1)
        
        config[key] = value  # 保存原始值（包含 ~）
        print(f"已设置 {key} 为: {value}")
    
    else:
        # 通用配置项
        config[key] = value
        print(f"已设置 {key} 为: {value}")
    
    save_config(config)
    print(f"配置文件位置: {get_config_path()}")


def command_show_config() -> None:
    """显示当前配置"""
    config = load_config()
    workspace_dir = get_workspace_dir()
    
    print("当前配置:")
    print(f"  Workspace 路径: {workspace_dir}")
    
    # 显示所有配置项
    if config:
        print("\n配置项详情:")
        for key, value in config.items():
            print(f"  {key}: {value}")
        print(f"\n配置文件: {get_config_path()}")
    else:
        print("  使用默认配置（未配置任何项）")
        print(f"  配置文件: {get_config_path()}")


def main() -> None:
    parser = argparse.ArgumentParser(description="多分支 worktree 管理工具（子命令版）")
    subparsers = parser.add_subparsers(dest="command", metavar="command")

    # add 子命令：添加 wpsmain 与 wpsweb 的 worktree
    add_parser = subparsers.add_parser("add", help="创建 worktree。用法: add <path> <branch>")
    add_parser.add_argument("path", help="目标路径名（对应 ~/<path>/...）")
    add_parser.add_argument("branch", help="要创建/切换的分支名")

    # list 子命令：列出 wpsmain 与 wpsweb 的 worktree
    subparsers.add_parser("list", help="列出 master 下 wpsmain 和 wpsweb 的 worktree")

    # remove 子命令：移除 wpsmain 与 wpsweb 的 worktree
    remove_parser = subparsers.add_parser("remove", help="移除 worktree。用法: remove <path>")
    remove_parser.add_argument("path", help="要移除的路径名（对应 ~/<path>/...）")

    # set 子命令：设置配置项
    set_parser = subparsers.add_parser("set", help="设置配置项。用法: set <key>=<value>")
    set_parser.add_argument("key_value", help="配置项，格式: key=value")

    # config 子命令：显示当前配置
    subparsers.add_parser("config", help="显示当前配置")

    # modify 子命令：修改 wpsweb/server/Makefile 修改 wpsweb/build_server.sh
    modify_parser = subparsers.add_parser("modify", help="修改 wpsweb/server/Makefile 和生成 build_server.sh（仅限 Linux）")
    modify_parser.add_argument("--force", action="store_true", help="强制在非 Linux 系统上运行（不推荐）")

    # build 子命令：自动编译 wpsmain
    subparsers.add_parser("build", help="自动编译 wpsmain（在 Docker 中执行）")

    args = parser.parse_args()

    if args.command == "add":
        command_add(args.path, args.branch)
        return
    if args.command == "list":
        command_list()
        return
    if args.command == "remove":
        command_remove(args.path)
        return
    if args.command == "set":
        command_set(args.key_value)
        return
    if args.command == "config":
        command_show_config()
        return
    if args.command == "modify":
        if not is_linux_system() and not getattr(args, 'force', False):
            print("错误: modify 命令仅在 Linux 系统上支持", file=sys.stderr)
            print(f"当前系统: {platform.system()}", file=sys.stderr)
            print("提示: 可以使用 --force 参数强制运行（不推荐）", file=sys.stderr)
            sys.exit(1)
        if not is_linux_system() and getattr(args, 'force', False):
            print(f"警告: 在 {platform.system()} 系统上强制运行 modify 命令", file=sys.stderr)
        command_modify_makefile()
        return
    if args.command == "build":
        command_auto_build()
        return

    parser.print_help()
    sys.exit(2)


if __name__ == "__main__":
    main()

